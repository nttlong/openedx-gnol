"""
Module for Video annotations using annotator.
"""
import textwrap

from lxml import etree
from pkg_resources import resource_string
from web_fragments.fragment import Fragment
from xblock.core import Scope, String

from xmodule.annotator_mixin import get_extension, get_instructions
from xmodule.annotator_token import retrieve_token
from xmodule.raw_module import RawDescriptor
from xmodule.x_module import XModule

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.ugettext_noop` because Django cannot be imported in this file
_ = lambda text: text


class AnnotatableFields(object):
    """ Fields for `VideoModule` and `VideoDescriptor`. """
    data = String(
        help=_("XML data for the annotation"),
        scope=Scope.content,
        default=textwrap.dedent("""\
        <annotatable>
            <instructions>
                <p>
                    Add the instructions to the assignment here.
                </p>
            </instructions>
        </annotatable>
        """))
    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        scope=Scope.settings,
        default=_('Video Annotation'),
    )
    sourceurl = String(
        help=_("The external source URL for the video."),
        display_name=_("Source URL"),
        scope=Scope.settings, default="http://video-js.zencoder.com/oceans-clip.mp4"
    )
    poster_url = String(
        help=_("Poster Image URL"),
        display_name=_("Poster URL"),
        scope=Scope.settings,
        default=""
    )
    annotation_storage_url = String(
        help=_("Location of Annotation backend"),
        scope=Scope.settings,
        default="http://your_annotation_storage.com",
        display_name=_("Url for Annotation Storage")
    )
    annotation_token_secret = String(
        help=_("Secret string for annotation storage"),
        scope=Scope.settings,
        default="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        display_name=_("Secret Token String for Annotation")
    )
    default_tab = String(
        display_name=_("Default Annotations Tab"),
        help=_("Select which tab will be the default in the annotations table: myNotes, Instructor, or Public."),
        scope=Scope.settings,
        default="myNotes",
    )
    # currently only supports one instructor, will build functionality for multiple later
    instructor_email = String(
        display_name=_("Email for 'Instructor' Annotations"),
        help=_("Email of the user that will be attached to all annotations that will be found in 'Instructor' tab."),
        scope=Scope.settings,
        default="",
    )
    annotation_mode = String(
        display_name=_("Mode for Annotation Tool"),
        help=_("Type in number corresponding to following modes:  'instructor' or 'everyone'"),
        scope=Scope.settings,
        default="everyone",
    )


class VideoAnnotationModule(AnnotatableFields, XModule):
    '''Video Annotation Module'''
    js = {
        'js': [
            resource_string(__name__, 'js/src/html/display.js'),
            resource_string(__name__, 'js/src/annotatable/display.js'),
            resource_string(__name__, 'js/src/javascript_loader.js'),
            resource_string(__name__, 'js/src/collapsible.js'),
        ]
    }
    css = {'scss': [resource_string(__name__, 'css/annotatable/display.scss')]}
    icon_class = 'videoannotation'

    def __init__(self, *args, **kwargs):
        super(VideoAnnotationModule, self).__init__(*args, **kwargs)

        xmltree = etree.fromstring(self.data)

        self.instructions = self._extract_instructions(xmltree)
        self.content = etree.tostring(xmltree, encoding='unicode')
        self.user_email = ""
        self.is_course_staff = False
        if self.runtime.get_user_role() in ['instructor', 'staff']:
            self.is_course_staff = True
        if self.runtime.get_real_user is not None:
            try:
                self.user_email = self.runtime.get_real_user(self.runtime.anonymous_student_id).email
            except Exception:  # pylint: disable=broad-except
                self.user_email = _("No email address found.")

    def _extract_instructions(self, xmltree):
        """ Removes <instructions> from the xmltree and returns them as a string, otherwise None. """
        return get_instructions(xmltree)

    def _get_extension(self, src_url):
        ''' get the extension of a given url '''
        return get_extension(src_url)

    def student_view(self, context):
        """ Renders parameters to template. """
        extension = self._get_extension(self.sourceurl)

        context = {
            'course_key': self.runtime.course_id,
            'display_name': self.display_name_with_default_escaped,
            'instructions_html': self.instructions,
            'sourceUrl': self.sourceurl,
            'typeSource': extension,
            'poster': self.poster_url,
            'content_html': self.content,
            'token': retrieve_token(self.user_email, self.annotation_token_secret),
            'annotation_storage': self.annotation_storage_url,
            'default_tab': self.default_tab,
            'instructor_email': self.instructor_email,
            'annotation_mode': self.annotation_mode,
            'is_course_staff': self.is_course_staff,
        }
        fragment = Fragment(self.system.render_template('videoannotation.html', context))

        # TinyMCE already exists in Studio so we should not load the files again
        # get_real_user always returns "None" in Studio since its runtimes contains no anonymous ids
        if self.runtime.get_real_user is not None:
            fragment.add_javascript_url(self.runtime.STATIC_URL + "js/vendor/tinymce/js/tinymce/tinymce.full.min.js")
            fragment.add_javascript_url(self.runtime.STATIC_URL + "js/vendor/tinymce/js/tinymce/jquery.tinymce.min.js")
        return fragment


class VideoAnnotationDescriptor(AnnotatableFields, RawDescriptor):
    ''' Video annotation descriptor '''
    module_class = VideoAnnotationModule
    resources_dir = None
    mako_template = "widgets/raw-edit.html"

    @property
    def non_editable_metadata_fields(self):
        non_editable_fields = super(VideoAnnotationDescriptor, self).non_editable_metadata_fields
        non_editable_fields.extend([
            VideoAnnotationDescriptor.annotation_storage_url,
            VideoAnnotationDescriptor.annotation_token_secret,
        ])
        return non_editable_fields
