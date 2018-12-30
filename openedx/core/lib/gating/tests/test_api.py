"""
Tests for the gating API
"""
import unittest

from mock import patch, Mock
from nose.plugins.attrib import attr
from ddt import ddt, data, unpack
from django.conf import settings
from lms.djangoapps.gating import api as lms_gating_api
from milestones.tests.utils import MilestonesTestCaseMixin
from milestones import api as milestones_api
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase, TEST_DATA_SPLIT_MODULESTORE
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from openedx.core.lib.gating import api as gating_api
from openedx.core.lib.gating.exceptions import GatingValidationError
from student.tests.factories import UserFactory


@attr(shard=2)
@ddt
class TestGatingApi(ModuleStoreTestCase, MilestonesTestCaseMixin):
    """
    Tests for the gating API
    """

    MODULESTORE = TEST_DATA_SPLIT_MODULESTORE

    def setUp(self):
        """
        Initial data setup
        """
        super(TestGatingApi, self).setUp()

        # create course
        self.course = CourseFactory.create(
            org='edX',
            number='EDX101',
            run='EDX101_RUN1',
            display_name='edX 101'
        )
        self.course.enable_subsection_gating = True
        self.course.save()

        # create chapter
        self.chapter1 = ItemFactory.create(
            parent_location=self.course.location,
            category='chapter',
            display_name='untitled chapter 1'
        )

        # create sequentials
        self.seq1 = ItemFactory.create(
            parent_location=self.chapter1.location,
            category='sequential',
            display_name='untitled sequential 1'
        )
        self.seq2 = ItemFactory.create(
            parent_location=self.chapter1.location,
            category='sequential',
            display_name='untitled sequential 2'
        )

        self.generic_milestone = {
            'name': 'Test generic milestone',
            'namespace': unicode(self.seq1.location),
        }

    @patch('openedx.core.lib.gating.api.log.warning')
    def test_get_prerequisite_milestone_returns_none(self, mock_log):
        """ Test test_get_prerequisite_milestone_returns_none """

        prereq = gating_api._get_prerequisite_milestone(self.seq1.location)  # pylint: disable=protected-access
        self.assertIsNone(prereq)
        self.assertTrue(mock_log.called)

    def test_get_prerequisite_milestone_returns_milestone(self):
        """ Test test_get_prerequisite_milestone_returns_milestone """

        gating_api.add_prerequisite(self.course.id, self.seq1.location)
        prereq = gating_api._get_prerequisite_milestone(self.seq1.location)  # pylint: disable=protected-access
        self.assertIsNotNone(prereq)

    @data('', '0', '50', '100')
    def test_validate_min_score_is_valid(self, min_score):
        """ Test test_validate_min_score_is_valid """

        self.assertIsNone(gating_api._validate_min_score(min_score))  # pylint: disable=protected-access

    @data('abc', '-10', '110')
    def test_validate_min_score_raises(self, min_score):
        """ Test test_validate_min_score_non_integer """

        with self.assertRaises(GatingValidationError):
            gating_api._validate_min_score(min_score)  # pylint: disable=protected-access

    def test_find_gating_milestones(self):
        """ Test test_find_gating_milestones """

        gating_api.add_prerequisite(self.course.id, self.seq1.location)
        gating_api.set_required_content(self.course.id, self.seq2.location, self.seq1.location, 100)
        milestone = milestones_api.add_milestone(self.generic_milestone)
        milestones_api.add_course_content_milestone(self.course.id, self.seq1.location, 'fulfills', milestone)

        self.assertEqual(len(gating_api.find_gating_milestones(self.course.id, self.seq1.location, 'fulfills')), 1)
        self.assertEqual(len(gating_api.find_gating_milestones(self.course.id, self.seq1.location, 'requires')), 0)
        self.assertEqual(len(gating_api.find_gating_milestones(self.course.id, self.seq2.location, 'fulfills')), 0)
        self.assertEqual(len(gating_api.find_gating_milestones(self.course.id, self.seq2.location, 'requires')), 1)

    def test_get_gating_milestone_not_none(self):
        """ Test test_get_gating_milestone_not_none """

        gating_api.add_prerequisite(self.course.id, self.seq1.location)
        gating_api.set_required_content(self.course.id, self.seq2.location, self.seq1.location, 100)

        self.assertIsNotNone(gating_api.get_gating_milestone(self.course.id, self.seq1.location, 'fulfills'))
        self.assertIsNotNone(gating_api.get_gating_milestone(self.course.id, self.seq2.location, 'requires'))

    def test_get_gating_milestone_is_none(self):
        """ Test test_get_gating_milestone_is_none """

        gating_api.add_prerequisite(self.course.id, self.seq1.location)
        gating_api.set_required_content(self.course.id, self.seq2.location, self.seq1.location, 100)

        self.assertIsNone(gating_api.get_gating_milestone(self.course.id, self.seq1.location, 'requires'))
        self.assertIsNone(gating_api.get_gating_milestone(self.course.id, self.seq2.location, 'fulfills'))

    def test_prerequisites(self):
        """ Test test_prerequisites """

        gating_api.add_prerequisite(self.course.id, self.seq1.location)

        prereqs = gating_api.get_prerequisites(self.course.id)
        self.assertEqual(len(prereqs), 1)
        self.assertEqual(prereqs[0]['block_display_name'], self.seq1.display_name)
        self.assertEqual(prereqs[0]['block_usage_key'], unicode(self.seq1.location))
        self.assertTrue(gating_api.is_prerequisite(self.course.id, self.seq1.location))

        gating_api.remove_prerequisite(self.seq1.location)

        self.assertEqual(len(gating_api.get_prerequisites(self.course.id)), 0)
        self.assertFalse(gating_api.is_prerequisite(self.course.id, self.seq1.location))

    def test_required_content(self):
        """ Test test_required_content """

        gating_api.add_prerequisite(self.course.id, self.seq1.location)
        gating_api.set_required_content(self.course.id, self.seq2.location, self.seq1.location, 100, 100)

        prereq_content_key, min_score, min_completion = gating_api.get_required_content(
            self.course.id, self.seq2.location
        )
        self.assertEqual(prereq_content_key, unicode(self.seq1.location))
        self.assertEqual(min_score, 100)
        self.assertEqual(min_completion, 100)

        gating_api.set_required_content(self.course.id, self.seq2.location, None, None, None)

        prereq_content_key, min_score, min_completion = gating_api.get_required_content(
            self.course.id, self.seq2.location
        )
        self.assertIsNone(prereq_content_key)
        self.assertIsNone(min_score)
        self.assertIsNone(min_completion)

    def test_get_gated_content(self):
        """
        Verify staff bypasses gated content and student gets list of unfulfilled prerequisites.
        """

        staff = UserFactory(is_staff=True)
        student = UserFactory(is_staff=False)

        self.assertEqual(gating_api.get_gated_content(self.course, staff), [])
        self.assertEqual(gating_api.get_gated_content(self.course, student), [])

        gating_api.add_prerequisite(self.course.id, self.seq1.location)
        gating_api.set_required_content(self.course.id, self.seq2.location, self.seq1.location, 100)
        milestone = milestones_api.get_course_content_milestones(self.course.id, self.seq2.location, 'requires')[0]

        self.assertEqual(gating_api.get_gated_content(self.course, staff), [])
        self.assertEqual(gating_api.get_gated_content(self.course, student), [unicode(self.seq2.location)])

        milestones_api.add_user_milestone({'id': student.id}, milestone)  # pylint: disable=no-member

        self.assertEqual(gating_api.get_gated_content(self.course, student), [])

    @data(
        (100, 0, 50, 0, False),
        (100, 0, 100, 0, True),
        (0, 100, 0, 50, False),
        (0, 100, 0, 100, True),
        (100, 100, 50, 100, False),
        (100, 100, 100, 50, False),
        (100, 100, 100, 100, True),
    )
    @unpack
    def test_is_gate_fulfilled(self, min_score, min_completion, learner_score, learner_completion, is_gate_fulfilled):
        """
        Test if prereq section has any unfulfilled milestones
        """
        student = UserFactory(is_staff=False)
        gating_api.add_prerequisite(self.course.id, self.seq1.location)
        gating_api.set_required_content(
            self.course.id, self.seq2.location, self.seq1.location, min_score, min_completion
        )
        milestone = milestones_api.add_milestone(self.generic_milestone)
        milestones_api.add_course_content_milestone(self.course.id, self.seq1.location, 'fulfills', milestone)

        self.assertFalse(gating_api.is_gate_fulfilled(self.course.id, self.seq1.location, student.id))

        # complete the prerequisite to unlock the gated content
        # this call triggers reevaluation of prerequisites fulfilled by the gating block.
        with patch.object(gating_api, 'get_subsection_completion_percentage') as mock_grade:
            mock_grade.return_value = learner_completion
            lms_gating_api.evaluate_prerequisite(
                self.course,
                Mock(location=self.seq1.location, percent_graded=learner_score / 100.0),
                student,
            )
            self.assertEqual(
                gating_api.is_gate_fulfilled(self.course.id, self.seq1.location, student.id), is_gate_fulfilled
            )

    @unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
    def test_compute_is_prereq_met(self):
        """
        Test if prereq has been met and force recompute
        """
        student = UserFactory(is_staff=False)
        gating_api.add_prerequisite(self.course.id, self.seq1.location)
        gating_api.set_required_content(self.course.id, self.seq2.location, self.seq1.location, 100, 0)

        # complete the prerequisite to unlock the gated content
        # this call triggers reevaluation of prerequisites fulfilled by the gating block.
        with patch.object(gating_api, 'get_subsection_grade_percentage') as mock_grade:
            mock_grade.return_value = 75
            # don't force recompute
            prereq_met, prereq_meta_info = gating_api.compute_is_prereq_met(self.seq2.location, student.id, False)
            self.assertFalse(prereq_met)
            self.assertIsNone(prereq_meta_info['url'])
            self.assertIsNone(prereq_meta_info['display_name'])

            # force recompute
            prereq_met, prereq_meta_info = gating_api.compute_is_prereq_met(self.seq2.location, student.id, True)
            self.assertFalse(prereq_met)
            self.assertIsNotNone(prereq_meta_info['url'])
            self.assertIsNotNone(prereq_meta_info['display_name'])

            # change to passing grade
            mock_grade.return_value = 100

            # don't force recompute
            prereq_met, prereq_meta_info = gating_api.compute_is_prereq_met(self.seq2.location, student.id, False)
            self.assertFalse(prereq_met)
            self.assertIsNone(prereq_meta_info['url'])
            self.assertIsNone(prereq_meta_info['display_name'])

            # force recompute
            prereq_met, prereq_meta_info = gating_api.compute_is_prereq_met(self.seq2.location, student.id, True)
            self.assertTrue(prereq_met)
            self.assertIsNotNone(prereq_meta_info['url'])
            self.assertIsNotNone(prereq_meta_info['display_name'])
