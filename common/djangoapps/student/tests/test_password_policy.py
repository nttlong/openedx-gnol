# -*- coding: utf-8 -*-
"""
This test file will verify proper password policy enforcement, which is an option feature
"""
import json
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from mock import patch

from openedx.core.djangoapps.external_auth.models import ExternalAuthMap
from openedx.core.djangoapps.site_configuration.tests.factories import SiteFactory
from student.views import create_account


@patch.dict("django.conf.settings.FEATURES", {'ENFORCE_PASSWORD_POLICY': True})
class TestPasswordPolicy(TestCase):
    """
    Go through some password policy tests to make sure things are properly working
    """
    def setUp(self):
        super(TestPasswordPolicy, self).setUp()
        self.url = reverse('create_account')
        self.request_factory = RequestFactory()
        self.url_params = {
            'username': 'username',
            'email': 'foo_bar@bar.com',
            'name': 'username',
            'terms_of_service': 'true',
            'honor_code': 'true',
        }

    @override_settings(PASSWORD_MIN_LENGTH=6)
    def test_password_length_too_short(self):
        self.url_params['password'] = 'aaa'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at least 6 characters.",
        )

    @override_settings(PASSWORD_MIN_LENGTH=6)
    def test_password_length_long_enough(self):
        self.url_params['password'] = 'ThisIsALongerPassword'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @override_settings(PASSWORD_MAX_LENGTH=12)
    def test_password_length_too_long(self):
        self.url_params['password'] = 'ThisPasswordIsWayTooLong'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at most 12 characters.",
        )

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'UPPER': 3})
    def test_password_not_enough_uppercase(self):
        self.url_params['password'] = 'thisshouldfail'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at least 3 uppercase letters.",
        )

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'UPPER': 3})
    def test_password_enough_uppercase(self):
        self.url_params['password'] = 'ThisShouldPass'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'LOWER': 3})
    def test_password_not_enough_lowercase(self):
        self.url_params['password'] = 'THISSHOULDFAIL'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at least 3 lowercase letters.",
        )

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'LOWER': 3})
    def test_password_enough_lowercase(self):
        self.url_params['password'] = 'ThisShouldPass'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'DIGITS': 3})
    def test_not_enough_digits(self):
        self.url_params['password'] = 'thishasnodigits'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at least 3 digits.",
        )

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'DIGITS': 3})
    def test_enough_digits(self):
        self.url_params['password'] = 'Th1sSh0uldPa88'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'PUNCTUATION': 3})
    def test_not_enough_punctuations(self):
        self.url_params['password'] = 'thisshouldfail'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at least 3 punctuation marks.",
        )

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'PUNCTUATION': 3})
    def test_enough_punctuations(self):
        self.url_params['password'] = 'Th!sSh.uldPa$*'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'WORDS': 3})
    def test_not_enough_words(self):
        self.url_params['password'] = 'thisshouldfail'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at least 3 words.",
        )

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'WORDS': 3})
    def test_enough_wordss(self):
        self.url_params['password'] = u'this should pass'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'NUMERIC': 3})
    def test_not_enough_numeric_characters(self):
        self.url_params['password'] = u'thishouldfail½2'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at least 3 numbers.",
        )

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'NUMERIC': 3})
    def test_enough_numeric_characters(self):
        self.url_params['password'] = u'thisShouldPass½33'  # This unicode 1/2 should count as a numeric value here
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'ALPHABETIC': 3})
    def test_not_enough_alphabetic_characters(self):
        self.url_params['password'] = '123456ab'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Enter a password with at least 3 letters.",
        )

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {'ALPHABETIC': 3})
    def test_enough_alphabetic_characters(self):
        self.url_params['password'] = u'𝒯𝓗Ï𝓼𝒫å𝓼𝓼𝔼𝓼'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {
        'PUNCTUATION': 3,
        'WORDS': 3,
        'DIGITS': 3,
        'LOWER': 3,
        'UPPER': 3,
    })
    def test_multiple_errors_fail(self):
        self.url_params['password'] = 'thisshouldfail'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        errstring = (
            "Enter a password with at least "
            "3 uppercase letters & "
            "3 digits & "
            "3 punctuation marks & "
            "3 words."
        )
        self.assertEqual(obj['value'], errstring)

    @patch.dict("django.conf.settings.PASSWORD_COMPLEXITY", {
        'PUNCTUATION': 3,
        'WORDS': 3,
        'DIGITS': 3,
        'LOWER': 3,
        'UPPER': 3,
    })
    def test_multiple_errors_pass(self):
        self.url_params['password'] = u'tH1s Sh0u!d P3#$'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @override_settings(PASSWORD_DICTIONARY=['foo', 'bar'])
    @override_settings(PASSWORD_DICTIONARY_EDIT_DISTANCE_THRESHOLD=1)
    def test_dictionary_similarity_fail1(self):
        self.url_params['password'] = 'foo'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Password is too similar to a dictionary word.",
        )

    @override_settings(PASSWORD_DICTIONARY=['foo', 'bar'])
    @override_settings(PASSWORD_DICTIONARY_EDIT_DISTANCE_THRESHOLD=1)
    def test_dictionary_similarity_fail2(self):
        self.url_params['password'] = 'bar'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Password is too similar to a dictionary word.",
        )

    @override_settings(PASSWORD_DICTIONARY=['foo', 'bar'])
    @override_settings(PASSWORD_DICTIONARY_EDIT_DISTANCE_THRESHOLD=1)
    def test_dictionary_similarity_fail3(self):
        self.url_params['password'] = 'fo0'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Password is too similar to a dictionary word.",
        )

    @override_settings(PASSWORD_DICTIONARY=['foo', 'bar'])
    @override_settings(PASSWORD_DICTIONARY_EDIT_DISTANCE_THRESHOLD=1)
    def test_dictionary_similarity_pass(self):
        self.url_params['password'] = 'this_is_ok'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    def test_with_unicode(self):
        self.url_params['password'] = u'四節比分和七年前'
        response = self.client.post(self.url, self.url_params)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])

    @override_settings(PASSWORD_MIN_LENGTH=6, SESSION_ENGINE='django.contrib.sessions.backends.cache')
    def test_ext_auth_password_length_too_short(self):
        """
        Tests that even if password policy is enforced, ext_auth registrations aren't subject to it
        """
        self.url_params['password'] = 'aaa'  # shouldn't pass validation
        request = self.request_factory.post(self.url, self.url_params)
        request.site = SiteFactory.create()
        # now indicate we are doing ext_auth by setting 'ExternalAuthMap' in the session.
        request.session = import_module(settings.SESSION_ENGINE).SessionStore()  # empty session
        extauth = ExternalAuthMap(external_id='withmap@stanford.edu',
                                  external_email='withmap@stanford.edu',
                                  internal_password=self.url_params['password'],
                                  external_domain='shib:https://idp.stanford.edu/')
        request.session['ExternalAuthMap'] = extauth
        request.user = AnonymousUser()

        with patch('edxmako.request_context.get_current_request', return_value=request):
            response = create_account(request)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])


class TestUsernamePasswordNonmatch(TestCase):
    """
    Test that registration username and password fields differ
    """
    def setUp(self):
        super(TestUsernamePasswordNonmatch, self).setUp()
        self.url = reverse('create_account')

        self.url_params = {
            'username': 'username',
            'email': 'foo_bar@bar.com',
            'name': 'username',
            'terms_of_service': 'true',
            'honor_code': 'true',
        }

    def test_with_username_password_match(self):
        self.url_params['username'] = "foobar"
        self.url_params['password'] = "foobar"
        response = self.client.post(self.url, self.url_params)
        self.assertEquals(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertEqual(
            obj['value'],
            "Password cannot be the same as the username.",
        )

    def test_with_username_password_nonmatch(self):
        self.url_params['username'] = "foobar"
        self.url_params['password'] = "nonmatch"
        response = self.client.post(self.url, self.url_params)
        self.assertEquals(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(obj['success'])
