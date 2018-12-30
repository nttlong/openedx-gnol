"""
OAuth Dispatch test mixins
"""

from django.conf import settings

import jwt
from jwt.exceptions import ExpiredSignatureError

from student.models import UserProfile, anonymous_id_for_user


class AccessTokenMixin(object):
    """ Mixin for tests dealing with OAuth 2 access tokens. """

    def assert_valid_jwt_access_token(self, access_token, user, scopes=None, should_be_expired=False, filters=None,
                                      jwt_issuer=settings.DEFAULT_JWT_ISSUER, should_be_restricted=None):
        """
        Verify the specified JWT access token is valid, and belongs to the specified user.

        Args:
            access_token (str): JWT
            user (User): User whose information is contained in the JWT payload.
            (optional) should_be_expired: indicates if the passed in JWT token is expected to be expired

        Returns:
            dict: Decoded JWT payload
        """
        scopes = scopes or []
        audience = jwt_issuer['AUDIENCE']
        issuer = jwt_issuer['ISSUER']
        secret_key = jwt_issuer['SECRET_KEY']

        def _decode_jwt(verify_expiration):
            """
            Helper method to decode a JWT with the ability to
            verify the expiration of said token
            """
            return jwt.decode(
                access_token,
                secret_key,
                algorithms=[settings.JWT_AUTH['JWT_ALGORITHM']],
                audience=audience,
                issuer=issuer,
                verify_expiration=verify_expiration
            )

        # Note that if we expect the claims to have expired
        # then we ask the JWT library not to verify expiration
        # as that would throw a ExpiredSignatureError and
        # halt other verifications steps. We'll do a manual
        # expiry verification later on
        payload = _decode_jwt(verify_expiration=not should_be_expired)

        expected = {
            'aud': audience,
            'iss': issuer,
            'preferred_username': user.username,
            'scopes': scopes,
            'version': settings.JWT_AUTH['JWT_SUPPORTED_VERSION'],
            'sub': anonymous_id_for_user(user, None),
        }

        if 'email' in scopes:
            expected['email'] = user.email

        if 'profile' in scopes:
            try:
                name = UserProfile.objects.get(user=user).name
            except UserProfile.DoesNotExist:
                name = None

            expected.update({
                'name': name,
                'administrator': user.is_staff,
                'family_name': user.last_name,
                'given_name': user.first_name,
            })

        if filters:
            expected['filters'] = filters

        if should_be_restricted is not None:
            expected['is_restricted'] = should_be_restricted

        self.assertDictContainsSubset(expected, payload)

        # Since we suppressed checking of expiry
        # in the claim in the above check, because we want
        # to fully examine the claims outside of the expiry,
        # now we should assert that the claim is indeed
        # expired
        if should_be_expired:
            with self.assertRaises(ExpiredSignatureError):
                _decode_jwt(verify_expiration=True)

        return payload
