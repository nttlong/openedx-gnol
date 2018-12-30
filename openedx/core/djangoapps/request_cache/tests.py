# -*- coding: utf-8 -*-
"""
Tests for the request cache.
"""
from celery.task import task
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from mock import Mock

from openedx.core.djangoapps.request_cache import get_request_or_stub
from openedx.core.djangoapps.request_cache.middleware import RequestCache, request_cached
from xmodule.modulestore.django import modulestore


class TestRequestCache(TestCase):
    """
    Tests for the request cache.
    """

    def test_get_request_or_stub(self):
        """
        Outside the context of the request, we should still get a request
        that allows us to build an absolute URI.
        """
        stub = get_request_or_stub()
        expected_url = "http://{site_name}/foobar".format(site_name=settings.SITE_NAME)
        self.assertEqual(stub.build_absolute_uri("foobar"), expected_url)

    @task
    def _dummy_task(self):
        """ Create a task that adds stuff to the request cache. """
        cache = {"course_cache": "blah blah blah"}
        modulestore().request_cache.data.update(cache)

    @override_settings(CLEAR_REQUEST_CACHE_ON_TASK_COMPLETION=True)
    def test_clear_cache_celery(self):
        """ Test that the request cache is cleared after a task is run. """
        self._dummy_task.apply(args=(self,)).get()
        self.assertEqual(modulestore().request_cache.data, {})

    def test_request_cached_miss_and_then_hit(self):
        """
        Ensure that after a cache miss, we fill the cache and can hit it.
        """
        RequestCache.clear_request_cache()

        to_be_wrapped = Mock()
        to_be_wrapped.return_value = 42
        self.assertEqual(to_be_wrapped.call_count, 0)

        def mock_wrapper(*args, **kwargs):
            """Simple wrapper to let us decorate our mock."""
            return to_be_wrapped(*args, **kwargs)

        wrapped = request_cached(mock_wrapper)
        result = wrapped()
        self.assertEqual(result, 42)
        self.assertEqual(to_be_wrapped.call_count, 1)

        result = wrapped()
        self.assertEqual(result, 42)
        self.assertEqual(to_be_wrapped.call_count, 1)

    def test_request_cached_with_caches_despite_changing_wrapped_result(self):
        """
        Ensure that after caching a result, we always send it back, even if the underlying result changes.
        """
        RequestCache.clear_request_cache()

        to_be_wrapped = Mock()
        to_be_wrapped.side_effect = [1, 2, 3]
        self.assertEqual(to_be_wrapped.call_count, 0)

        def mock_wrapper(*args, **kwargs):
            """Simple wrapper to let us decorate our mock."""
            return to_be_wrapped(*args, **kwargs)

        wrapped = request_cached(mock_wrapper)
        result = wrapped()
        self.assertEqual(result, 1)
        self.assertEqual(to_be_wrapped.call_count, 1)

        result = wrapped()
        self.assertEqual(result, 1)
        self.assertEqual(to_be_wrapped.call_count, 1)

        direct_result = mock_wrapper()
        self.assertEqual(direct_result, 2)
        self.assertEqual(to_be_wrapped.call_count, 2)

        result = wrapped()
        self.assertEqual(result, 1)
        self.assertEqual(to_be_wrapped.call_count, 2)

        direct_result = mock_wrapper()
        self.assertEqual(direct_result, 3)
        self.assertEqual(to_be_wrapped.call_count, 3)

    def test_request_cached_with_changing_args(self):
        """
        Ensure that calling a decorated function with different positional arguments
        will not use a cached value invoked by a previous call with different arguments.
        """
        RequestCache.clear_request_cache()

        to_be_wrapped = Mock()
        to_be_wrapped.side_effect = [1, 2, 3, 4, 5, 6]
        self.assertEqual(to_be_wrapped.call_count, 0)

        def mock_wrapper(*args, **kwargs):
            """Simple wrapper to let us decorate our mock."""
            return to_be_wrapped(*args, **kwargs)

        wrapped = request_cached(mock_wrapper)

        # This will be a miss, and make an underlying call.
        result = wrapped(1)
        self.assertEqual(result, 1)
        self.assertEqual(to_be_wrapped.call_count, 1)

        # This will be a miss, and make an underlying call.
        result = wrapped(2)
        self.assertEqual(result, 2)
        self.assertEqual(to_be_wrapped.call_count, 2)

        # This is bypass of the decorator.
        direct_result = mock_wrapper(3)
        self.assertEqual(direct_result, 3)
        self.assertEqual(to_be_wrapped.call_count, 3)

        # These will be hits, and not make an underlying call.
        result = wrapped(1)
        self.assertEqual(result, 1)
        self.assertEqual(to_be_wrapped.call_count, 3)

        result = wrapped(2)
        self.assertEqual(result, 2)
        self.assertEqual(to_be_wrapped.call_count, 3)

    def test_request_cached_with_changing_kwargs(self):
        """
        Ensure that calling a decorated function with different keyword arguments
        will not use a cached value invoked by a previous call with different arguments.
        """
        RequestCache.clear_request_cache()

        to_be_wrapped = Mock()
        to_be_wrapped.side_effect = [1, 2, 3, 4, 5, 6]
        self.assertEqual(to_be_wrapped.call_count, 0)

        def mock_wrapper(*args, **kwargs):
            """Simple wrapper to let us decorate our mock."""
            return to_be_wrapped(*args, **kwargs)

        wrapped = request_cached(mock_wrapper)

        # This will be a miss, and make an underlying call.
        result = wrapped(1, foo=1)
        self.assertEqual(result, 1)
        self.assertEqual(to_be_wrapped.call_count, 1)

        # This will be a miss, and make an underlying call.
        result = wrapped(2, foo=2)
        self.assertEqual(result, 2)
        self.assertEqual(to_be_wrapped.call_count, 2)

        # This is bypass of the decorator.
        direct_result = mock_wrapper(3, foo=3)
        self.assertEqual(direct_result, 3)
        self.assertEqual(to_be_wrapped.call_count, 3)

        # These will be hits, and not make an underlying call.
        result = wrapped(1, foo=1)
        self.assertEqual(result, 1)
        self.assertEqual(to_be_wrapped.call_count, 3)

        result = wrapped(2, foo=2)
        self.assertEqual(result, 2)
        self.assertEqual(to_be_wrapped.call_count, 3)

        # Since we're changing foo, this will be a miss.
        result = wrapped(2, foo=5)
        self.assertEqual(result, 4)
        self.assertEqual(to_be_wrapped.call_count, 4)

    def test_request_cached_mixed_unicode_str_args(self):
        """
        Ensure that request_cached can work with mixed str and Unicode parameters.
        """
        RequestCache.clear_request_cache()

        def dummy_function(arg1, arg2):
            """
            A dummy function that expects an str and unicode arguments.
            """
            assert isinstance(arg1, str), 'First parameter has to be of type `str`'
            assert isinstance(arg2, unicode), 'Second parameter has to be of type `unicode`'
            return True

        self.assertTrue(dummy_function('Hello', u'World'), 'Should be callable with ASCII chars')
        self.assertTrue(dummy_function('H∂llå', u'Wørld'), 'Should be callable with non-ASCII chars')

        wrapped = request_cached(dummy_function)

        self.assertTrue(wrapped('Hello', u'World'), 'Wrapper should handle ASCII only chars')
        self.assertTrue(wrapped('H∂llå', u'Wørld'), 'Wrapper should handle non-ASCII chars')

    def test_request_cached_with_none_result(self):
        """
        Ensure that calling a decorated function that returns None
        properly caches the result and doesn't recall the underlying
        function.
        """
        RequestCache.clear_request_cache()

        to_be_wrapped = Mock()
        to_be_wrapped.side_effect = [None, None, None, 1, 1]
        self.assertEqual(to_be_wrapped.call_count, 0)

        def mock_wrapper(*args, **kwargs):
            """Simple wrapper to let us decorate our mock."""
            return to_be_wrapped(*args, **kwargs)

        wrapped = request_cached(mock_wrapper)

        # This will be a miss, and make an underlying call.
        result = wrapped(1)
        self.assertEqual(result, None)
        self.assertEqual(to_be_wrapped.call_count, 1)

        # This will be a miss, and make an underlying call.
        result = wrapped(2)
        self.assertEqual(result, None)
        self.assertEqual(to_be_wrapped.call_count, 2)

        # This is bypass of the decorator.
        direct_result = mock_wrapper(3)
        self.assertEqual(direct_result, None)
        self.assertEqual(to_be_wrapped.call_count, 3)

        # These will be hits, and not make an underlying call.
        result = wrapped(1)
        self.assertEqual(result, None)
        self.assertEqual(to_be_wrapped.call_count, 3)

        result = wrapped(2)
        self.assertEqual(result, None)
        self.assertEqual(to_be_wrapped.call_count, 3)
