"""
Django Management Command:  Generate Course Structure
Generates and stores course structure information for one or more courses.
"""
import logging

from django.core.management.base import BaseCommand
from opaque_keys.edx.keys import CourseKey
from six import text_type

from openedx.core.djangoapps.content.course_structures.tasks import update_course_structure
from xmodule.modulestore.django import modulestore

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Generates and stores course structure information for one or more courses.
    """
    help = 'Generates and stores course structure for one or more courses.'

    def add_arguments(self, parser):
        parser.add_argument('course_id', nargs='*')
        parser.add_argument('--all',
                            action='store_true',
                            help='Generate structures for all courses.')

    def handle(self, *args, **options):
        """
        Perform the course structure generation workflow
        """
        if options['all']:
            course_keys = [course.id for course in modulestore().get_courses()]
        else:
            course_keys = [CourseKey.from_string(arg) for arg in options['course_id']]

        if not course_keys:
            log.fatal('No courses specified.')
            return

        log.info('Generating course structures for %d courses.', len(course_keys))
        log.debug('Generating course structure(s) for the following courses: %s', course_keys)

        for course_key in course_keys:
            try:
                # Run the update task synchronously so that we know when all course structures have been updated.
                # TODO Future improvement: Use .delay(), add return value to ResultSet, and wait for execution of
                # all tasks using ResultSet.join(). I (clintonb) am opting not to make this improvement right now
                # as I do not have time to test it fully.
                update_course_structure.apply(args=[text_type(course_key)])
            except Exception as ex:
                log.exception('An error occurred while generating course structure for %s: %s',
                              text_type(course_key), text_type(ex))

        log.info('Finished generating course structures.')
