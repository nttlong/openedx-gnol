from xmodule.tabs import CourseTabList
from lms.djangoapps.courseware.views.views import CourseTabView
from lms.djangoapps.courseware.access import has_access
def get_course_key_from_string(str_course_id):
    """
    :param str_course_id:
    :return:
    """
    #'/opt/edx-hawthorn.2-3/apps/edx/venvs/edxapp/lib/python2.7/site-packages/opaque_keys/__init__.py'
    from opaque_keys.edx.keys import CourseKey, UsageKey

    return CourseKey.from_string(str_course_id)
def get_module_store():
    """

    :return:
    """
    #'/opt/edx-hawthorn.2-3/apps/edx/edx-platform/common/lib/xmodule/xmodule/modulestore/django.py'
    from xmodule.modulestore.django import modulestore
    return modulestore()
def create_page_context(request, course=None, tab=None, **kwargs):
        """
        Creates the context for the fragment's template.
        """
        from courseware.access import has_access
        from courseware.masquerade import setup_masquerade
        from lms.djangoapps.courseware.access_utils import check_course_open_for_learner
        from lms.djangoapps.experiments.utils import get_experiment_user_metadata_context
        staff_access = has_access(request.user, 'staff', course)
        supports_preview_menu = tab.get('supports_preview_menu', False)
        uses_bootstrap = True
        if supports_preview_menu:
            masquerade, masquerade_user = setup_masquerade(request, course.id, staff_access, reset_masquerade_data=True)
            request.user = masquerade_user
        else:
            masquerade = None

        if course and not check_course_open_for_learner(request.user, course):
            # Disable student view button if user is staff and
            # course is not yet visible to students.
            supports_preview_menu = False

        context = {
            'course': course,
            'tab': tab,
            'active_page': tab.get('type', None),
            'staff_access': staff_access,
            'masquerade': masquerade,
            'supports_preview_menu': supports_preview_menu,
            'uses_bootstrap': uses_bootstrap,
            'uses_pattern_library': not uses_bootstrap,
            'disable_courseware_js': True,
        }
        context.update(
            get_experiment_user_metadata_context(
                course,
                request.user,
            )
        )
        return context
def check_course_access(course, user, action, check_if_enrolled=False, check_survey_complete=True):
    """
    Check that the user has the access to perform the specified action
    on the course (CourseDescriptor|CourseOverview).

    check_if_enrolled: If true, additionally verifies that the user is enrolled.
    check_survey_complete: If true, additionally verifies that the user has completed the survey.
    """
    # Allow staff full access to the course even if not enrolled
    if has_access(user, 'staff', course.id):
        return

    access_response = has_access(user, action, course, course.id)
    if not access_response:
        # Redirect if StartDateError
        if isinstance(access_response, StartDateError):
            start_date = strftime_localized(course.start, 'SHORT_DATE')
            params = QueryDict(mutable=True)
            params['notlive'] = start_date
            raise CourseAccessRedirect('{dashboard_url}?{params}'.format(
                dashboard_url=reverse('dashboard'),
                params=params.urlencode()
            ), access_response)

        # Redirect if the user must answer a survey before entering the course.
        if isinstance(access_response, MilestoneAccessError):
            raise CourseAccessRedirect('{dashboard_url}'.format(
                dashboard_url=reverse('dashboard'),
            ), access_response)

        # Deliberately return a non-specific error message to avoid
        # leaking info about access control settings
        raise CoursewareAccessException(access_response)

    if check_if_enrolled:
        # If the user is not enrolled, redirect them to the about page
        if not CourseEnrollment.is_enrolled(user, course.id):
            raise CourseAccessRedirect(reverse('about_course', args=[unicode(course.id)]))

    # Redirect if the user must answer a survey before entering the course.
    if check_survey_complete and action == 'load':
        if is_survey_required_and_unanswered(user, course):
            raise CourseAccessRedirect(reverse('course_survey', args=[unicode(course.id)]))
def course_get_tab_course(request,course_id):
    tab_type = 'courseware'
    from courseware.courses import get_course_with_access
    course_key = get_course_key_from_string(course_id)
    with get_module_store().bulk_operations(course_key):
        course = get_course_with_access(request.user, 'load', course_key)
        try:
            # Render the page
            # tab = CourseTabList.get_tab_by_type(course.tabs, tab_type)
            # page_context = create_page_context(request, course=course, tab=tab)

            from openedx.features.course_experience.utils import get_course_outline_block_tree

            courseware_outline = get_course_outline_block_tree(request,course_id)
            """
            Get course out line
            """
            # Show warnings if the user has limited access
            # Must come after masquerading on creation of page context

            # set_custom_metrics_for_course_key(course_key)
            # return super(CourseTabView, self).get(request, course=course, page_context=page_context)
            # from openedx.features.course_experience.views.course_home import CourseHomeFragmentView
            import xdj
            ret= xdj.dobject(courseware_outline)


            return ret
        except Exception as exception:  # pylint: disable=broad-except
            return CourseTabView.handle_exceptions(request, course, exception)
    pass
