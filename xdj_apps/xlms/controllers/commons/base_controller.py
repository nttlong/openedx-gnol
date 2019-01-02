import xdj
from xmodule.tabs import CourseTabList
from lms.djangoapps.courseware.views.views import CourseTabView
from lms.djangoapps.courseware.access import has_access
from survey.utils import is_survey_required_and_unanswered

class courseware_privileges():
    @staticmethod
    def full_access():
        return "full"
    @staticmethod
    def access_deny():
        return "deny"

    @staticmethod
    def need_enroll():
        return "need_enroll"

    @staticmethod
    def need_survey():
        return "need_survey"
    @staticmethod
    def need_login():
        return "need_login"

class XlmsController(xdj.BaseController):
    def __init__(self):
        super(XlmsController, self).__init__()

    def get_course_locator(self,course_key):
        from opaque_keys.edx.locator import CourseLocator
        return CourseLocator.from_string(course_key)

    def get_course_key(self, course_key):
        """
        Get course_id from courrse_key: the course_key is a string like 'course-v1:T+A001+B002'
        :param course_key:
        :return:
        """
        from opaque_keys.edx.keys import CourseKey, UsageKey

        return CourseKey.from_string(course_key)

    def get_module_store(self):
        """

        :return:
        """
        # '/opt/edx-hawthorn.2-3/apps/edx/edx-platform/common/lib/xmodule/xmodule/modulestore/django.py'
        from xmodule.modulestore.django import modulestore
        return modulestore()

    def check_course_access(self, course, user, action, check_if_enrolled=False, check_survey_complete=True):
        """
        Check that the user has the access to perform the specified action
        on the course (CourseDescriptor|CourseOverview).

        check_if_enrolled: If true, additionally verifies that the user is enrolled.
        check_survey_complete: If true, additionally verifies that the user has completed the survey.
        """


        # Allow staff full access to the course even if not enrolled
        if has_access(user, 'staff', course.id):
            return course, courseware_privileges.full_access

        access_response = has_access(user, action, course, course.id)
        if not access_response:
            return None, courseware_privileges.access_deny
        if check_if_enrolled:
            # If the user is not enrolled, redirect them to the about page
            if not CourseEnrollment.is_enrolled(user, course.id):
                return None, courseware_privileges.need_enroll

        # Redirect if the user must answer a survey before entering the course.
        if check_survey_complete and action == 'load':
            if is_survey_required_and_unanswered(user, course):
                return None, courseware_privileges.need_survey
            elif user.is_anonymous:
                return None, courseware_privileges.need_login
            else:
                return course, courseware_privileges.full_access

    def get_course_with_access(self, user, action, course_key, depth=0, check_if_enrolled=False, check_survey_complete=True):
        """
        Given a course_key, look up the corresponding course descriptor,
        check that the user has the access to perform the specified action
        on the course, and return the descriptor.

        Raises a 404 if the course_key is invalid, or the user doesn't have access.

        depth: The number of levels of children for the modulestore to cache. None means infinite depth

        check_if_enrolled: If true, additionally verifies that the user is either enrolled in the course
          or has staff access.
        check_survey_complete: If true, additionally verifies that the user has either completed the course survey
          or has staff access.
          Note: We do not want to continually add these optional booleans.  Ideally,
          these special cases could not only be handled inside has_access, but could
          be plugged in as additional callback checks for different actions.
        """
        course = self.get_course_by_id(course_key, depth)
        course, privilege = self.check_course_access(course, user, action, check_if_enrolled, check_survey_complete)
        return course, privilege

    def get_course_outline(self, model, course_id):
        """
        Get course outline of course_id
        :param model:
        :param course_id:
        :return:
        """
        tab_type = 'courseware'
        # from courseware.courses import get_course_with_access
        course_key = self.get_course_key(course_id)
        with self.get_module_store().bulk_operations(course_key):
            course, privilege = self.get_course_with_access(model.request.user, 'load', course_key)
            if not course:
                return None, privilege
            # Render the page
            # tab = CourseTabList.get_tab_by_type(course.tabs, tab_type)
            # page_context = create_page_context(request, course=course, tab=tab)
            from openedx.features.course_experience.utils import get_course_outline_block_tree
            courseware_outline = get_course_outline_block_tree(model.request, course_id)
            return xdj.dobject(courseware_outline), privilege

    def get_course_by_id(self,course_key, depth=0):
        """
        Given a course id, return the corresponding course descriptor.

        If such a course does not exist, raises a 404.

        depth: The number of levels of children for the modulestore to cache. None means infinite depth
        """
        with self.get_module_store().bulk_operations(course_key):
            course = self.get_module_store().get_course(course_key, depth=depth)
        if course:
            return course
        else:
            return None
