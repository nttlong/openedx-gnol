"""
Views that dispatch processing of OAuth requests to django-oauth2-provider or
django-oauth-toolkit as appropriate.
"""

from __future__ import unicode_literals

import hashlib
import json

from Cryptodome.PublicKey import RSA
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import View
from edx_oauth2_provider import views as dop_views  # django-oauth2-provider views
from jwkest.jwk import RSAKey
from oauth2_provider import models as dot_models  # django-oauth-toolkit
from oauth2_provider import views as dot_views
from ratelimit import ALL
from ratelimit.mixins import RatelimitMixin

from openedx.core.djangoapps.auth_exchange import views as auth_exchange_views
from openedx.core.lib.token_utils import JwtBuilder

from . import adapters
from .dot_overrides import views as dot_overrides_views
from .toggles import ENFORCE_JWT_SCOPES


class _DispatchingView(View):
    """
    Base class that route views to the appropriate provider view.  The default
    behavior routes based on client_id, but this can be overridden by redefining
    `select_backend()` if particular views need different behavior.
    """
    # pylint: disable=no-member

    dot_adapter = adapters.DOTAdapter()
    dop_adapter = adapters.DOPAdapter()

    def get_adapter(self, request):
        """
        Returns the appropriate adapter based on the OAuth client linked to the request.
        """
        if dot_models.Application.objects.filter(client_id=self._get_client_id(request)).exists():
            return self.dot_adapter
        else:
            return self.dop_adapter

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request to the selected backend's view.
        """
        backend = self.select_backend(request)
        view = self.get_view_for_backend(backend)
        return view(request, *args, **kwargs)

    def select_backend(self, request):
        """
        Given a request that specifies an oauth `client_id`, return the adapter
        for the appropriate OAuth handling library.  If the client_id is found
        in a django-oauth-toolkit (DOT) Application, use the DOT adapter,
        otherwise use the django-oauth2-provider (DOP) adapter, and allow the
        calls to fail normally if the client does not exist.
        """
        return self.get_adapter(request).backend

    def get_view_for_backend(self, backend):
        """
        Return the appropriate view from the requested backend.
        """
        if backend == self.dot_adapter.backend:
            return self.dot_view.as_view()
        elif backend == self.dop_adapter.backend:
            return self.dop_view.as_view()
        else:
            raise KeyError('Failed to dispatch view. Invalid backend {}'.format(backend))

    def _get_client_id(self, request):
        """
        Return the client_id from the provided request
        """
        if request.method == u'GET':
            return request.GET.get('client_id')
        else:
            return request.POST.get('client_id')


class AccessTokenView(RatelimitMixin, _DispatchingView):
    """
    Handle access token requests.
    """
    dot_view = dot_views.TokenView
    dop_view = dop_views.AccessTokenView
    ratelimit_key = 'openedx.core.djangoapps.util.ratelimit.real_ip'
    ratelimit_rate = settings.RATELIMIT_RATE
    ratelimit_block = True
    ratelimit_method = ALL

    def dispatch(self, request, *args, **kwargs):
        response = super(AccessTokenView, self).dispatch(request, *args, **kwargs)

        if response.status_code == 200 and request.POST.get('token_type', '').lower() == 'jwt':
            client_id = self._get_client_id(request)
            adapter = self.get_adapter(request)
            expires_in, scopes, user = self._decompose_access_token_response(adapter, response)
            issuer, secret, audience, filters, is_client_restricted = self._get_client_specific_claims(
                client_id,
                adapter
            )

            content = {
                'access_token': JwtBuilder(
                    user,
                    secret=secret,
                    issuer=issuer,
                ).build_token(
                    scopes,
                    expires_in,
                    aud=audience,
                    additional_claims={
                        'filters': filters,
                        'is_restricted': is_client_restricted,
                    },
                ),
                'expires_in': expires_in,
                'token_type': 'JWT',
                'scope': ' '.join(scopes),
            }
            response.content = json.dumps(content)

        return response

    def _decompose_access_token_response(self, adapter, response):
        """ Decomposes the access token in the request to an expiration date, scopes, and User. """
        content = json.loads(response.content)
        access_token = content['access_token']
        scope = content['scope']
        scopes = scope.split(' ')
        user = adapter.get_access_token(access_token).user
        expires_in = content['expires_in']
        return expires_in, scopes, user

    def _get_client_specific_claims(self, client_id, adapter):
        """ Get claims that are specific to the client. """
        # If JWT scope enforcement is enabled, we need to sign tokens
        # given to restricted application with a separate secret which
        # other IDAs do not have access to. This prevents restricted
        # applications from getting access to API endpoints available
        # on other IDAs which have not yet been protected with the
        # scope-related DRF permission classes. Once all endpoints have
        # been protected we can remove this if/else and go back to using
        # a single secret.
        # TODO: ARCH-162
        is_client_restricted = adapter.is_client_restricted(client_id)
        if ENFORCE_JWT_SCOPES.is_enabled() and is_client_restricted:
            issuer_setting = 'RESTRICTED_APPLICATION_JWT_ISSUER'
        else:
            issuer_setting = 'DEFAULT_JWT_ISSUER'

        jwt_issuer = getattr(settings, issuer_setting)
        filters = adapter.get_authorization_filters(client_id)
        return jwt_issuer['ISSUER'], jwt_issuer['SECRET_KEY'], jwt_issuer['AUDIENCE'], filters, is_client_restricted


class AuthorizationView(_DispatchingView):
    """
    Part of the authorization flow.
    """
    dop_view = dop_views.Capture
    dot_view = dot_overrides_views.EdxOAuth2AuthorizationView


class AccessTokenExchangeView(_DispatchingView):
    """
    Exchange a third party auth token.
    """
    dop_view = auth_exchange_views.DOPAccessTokenExchangeView
    dot_view = auth_exchange_views.DOTAccessTokenExchangeView


class RevokeTokenView(_DispatchingView):
    """
    Dispatch to the RevokeTokenView of django-oauth-toolkit
    """
    dot_view = dot_views.RevokeTokenView


class ProviderInfoView(View):
    def get(self, request, *args, **kwargs):
        data = {
            'issuer': settings.JWT_AUTH['JWT_ISSUER'],
            'authorization_endpoint': request.build_absolute_uri(reverse('authorize')),
            'token_endpoint': request.build_absolute_uri(reverse('access_token')),
            'end_session_endpoint': request.build_absolute_uri(reverse('logout')),
            'token_endpoint_auth_methods_supported': ['client_secret_post'],
            # NOTE (CCB): This is not part of the OpenID Connect standard. It is added here since we
            # use JWS for our access tokens.
            'access_token_signing_alg_values_supported': ['RS512', 'HS256'],
            'scopes_supported': ['openid', 'profile', 'email'],
            'claims_supported': ['sub', 'iss', 'name', 'given_name', 'family_name', 'email'],
            'jwks_uri': request.build_absolute_uri(reverse('jwks')),
        }
        response = JsonResponse(data)
        return response


class JwksView(View):
    @staticmethod
    def serialize_rsa_key(key):
        kid = hashlib.md5(key.encode('utf-8')).hexdigest()
        key = RSAKey(kid=kid, key=RSA.importKey(key), use='sig', alg='RS512')
        return key.serialize(private=False)

    def get(self, request, *args, **kwargs):
        secret_keys = []

        if settings.JWT_PRIVATE_SIGNING_KEY:
            secret_keys.append(settings.JWT_PRIVATE_SIGNING_KEY)

        # NOTE: We provide the expired keys in case there are unexpired access tokens
        # that need to have their signatures verified.
        if settings.JWT_EXPIRED_PRIVATE_SIGNING_KEYS:
            secret_keys += settings.JWT_EXPIRED_PRIVATE_SIGNING_KEYS

        return JsonResponse({
            'keys': [self.serialize_rsa_key(key) for key in secret_keys if key],
        })
