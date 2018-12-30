""" Tests for rendering functions in the mako pipeline. """

from unittest import skipUnless

import ddt
import os
from django.conf import settings
from django.test import TestCase
from paver.easy import call_task

from pipeline_mako import compressed_css, compressed_js, render_require_js_path_overrides


class RequireJSPathOverridesTest(TestCase):
    """Test RequireJS path overrides. """
    shard = 7

    OVERRIDES = {
        'jquery': 'common/js/vendor/jquery.js',
        'backbone': 'common/js/vendor/backbone.js',
        'text': 'js/vendor/text.js'
    }

    OVERRIDES_JS = [
        "<script type=\"text/javascript\">",
        "(function (require) {",
        "require.config({",
        "paths: {",
        "'jquery': 'common/js/vendor/jquery',",
        "'text': 'js/vendor/text',",
        "'backbone': 'common/js/vendor/backbone'",
        "}",
        "});",
        "}).call(this, require || RequireJS.require);",
        "</script>"
    ]

    def test_requirejs_path_overrides(self):
        result = render_require_js_path_overrides(self.OVERRIDES)
        # To make the string comparision easy remove the whitespaces
        self.assertEqual(map(str.strip, result.splitlines()), self.OVERRIDES_JS)


@ddt.ddt
class PipelineRenderTest(TestCase):
    """Test individual pipeline rendering functions. """
    shard = 7

    @classmethod
    def setUpClass(cls):
        """
        Create static assets once for all pipeline render tests.
        """
        super(PipelineRenderTest, cls).setUpClass()
        # Ensure that the npm requirements are always installed before updating static assets.
        prereq_install_value_orig = os.environ.get('NO_PREREQ_INSTALL')
        os.environ['NO_PREREQ_INSTALL'] = 'False'
        try:
            call_task('pavelib.prereqs.install_node_prereqs')
        except:
            raise
        finally:
            if prereq_install_value_orig is None:
                del os.environ['NO_PREREQ_INSTALL']
            else:
                os.environ['NO_PREREQ_INSTALL'] = prereq_install_value_orig
        # Update all static assets.
        call_task('pavelib.assets.update_assets', args=('lms', '--settings=test', '--themes=no'))

    @skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in LMS')
    @ddt.data(
        (True,),
        (False,),
    )
    def test_compressed_css(self, pipeline_enabled):
        """
        Verify the behavior of compressed_css, with the pipeline
        both enabled and disabled.
        """
        with self.settings(PIPELINE_ENABLED=pipeline_enabled):
            # Verify the default behavior
            css_include = compressed_css('style-main-v1')
            self.assertIn(u'lms-main-v1.css', css_include)

            # Verify that raw keyword causes raw URLs to be emitted
            css_include = compressed_css('style-main-v1', raw=True)
            self.assertIn(u'lms-main-v1.css?raw', css_include)

    @skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in LMS')
    def test_compressed_js(self):
        """
        Verify the behavior of compressed_css, with the pipeline
        both enabled and disabled.
        """
        # Verify that a single JS file is rendered with the pipeline enabled
        with self.settings(PIPELINE_ENABLED=True):
            js_include = compressed_js('base_application')
            self.assertIn(u'lms-base-application.js', js_include)

        # Verify that multiple JS files are rendered with the pipeline disabled
        with self.settings(PIPELINE_ENABLED=False):
            js_include = compressed_js('base_application')
            self.assertIn(u'/static/js/src/logger.js', js_include)
