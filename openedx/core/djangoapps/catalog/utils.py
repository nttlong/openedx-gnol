"""Helper functions for working with the catalog service."""
import copy
import datetime
import logging
import uuid

import pycountry
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from edx_rest_api_client.client import EdxRestApiClient
from opaque_keys.edx.keys import CourseKey
from pytz import UTC

from entitlements.utils import is_course_run_entitlement_fulfillable
from openedx.core.constants import COURSE_PUBLISHED
from openedx.core.djangoapps.catalog.cache import (PROGRAM_CACHE_KEY_TPL,
                                                   SITE_PROGRAM_UUIDS_CACHE_KEY_TPL)
from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.lib.edx_api_utils import get_edx_api_data
from openedx.core.lib.token_utils import JwtBuilder
from student.models import CourseEnrollment

logger = logging.getLogger(__name__)


def create_catalog_api_client(user, site=None):
    """Returns an API client which can be used to make Catalog API requests."""
    scopes = ['email', 'profile']
    expires_in = settings.OAUTH_ID_TOKEN_EXPIRATION
    jwt = JwtBuilder(user).build_token(scopes, expires_in)

    if site:
        url = site.configuration.get_value('COURSE_CATALOG_API_URL')
    else:
        url = CatalogIntegration.current().get_internal_api_url()

    return EdxRestApiClient(url, jwt=jwt)


def get_programs(site, uuid=None):
    """Read programs from the cache.

    The cache is populated by a management command, cache_programs.

    Arguments:
        site (Site): django.contrib.sites.models object

    Keyword Arguments:
        uuid (string): UUID identifying a specific program to read from the cache.

    Returns:
        list of dict, representing programs.
        dict, if a specific program is requested.
    """
    missing_details_msg_tpl = 'Failed to get details for program {uuid} from the cache.'

    if uuid:
        program = cache.get(PROGRAM_CACHE_KEY_TPL.format(uuid=uuid))
        if not program:
            logger.warning(missing_details_msg_tpl.format(uuid=uuid))

        return program
    uuids = cache.get(SITE_PROGRAM_UUIDS_CACHE_KEY_TPL.format(domain=site.domain), [])
    if not uuids:
        logger.warning('Failed to get program UUIDs from the cache.')

    programs = cache.get_many([PROGRAM_CACHE_KEY_TPL.format(uuid=uuid) for uuid in uuids])
    programs = list(programs.values())

    # The get_many above sometimes fails to bring back details cached on one or
    # more Memcached nodes. It doesn't look like these keys are being evicted.
    # 99% of the time all keys come back, but 1% of the time all the keys stored
    # on one or more nodes are missing from the result of the get_many. One
    # get_many may fail to bring these keys back, but a get_many occurring
    # immediately afterwards will succeed in bringing back all the keys. This
    # behavior can be mitigated by trying again for the missing keys, which is
    # what we do here. Splitting the get_many into smaller chunks may also help.
    missing_uuids = set(uuids) - set(program['uuid'] for program in programs)
    if missing_uuids:
        logger.info(
            'Failed to get details for {count} programs. Retrying.'.format(count=len(missing_uuids))
        )

        retried_programs = cache.get_many([PROGRAM_CACHE_KEY_TPL.format(uuid=uuid) for uuid in missing_uuids])
        programs += list(retried_programs.values())

        still_missing_uuids = set(uuids) - set(program['uuid'] for program in programs)
        for uuid in still_missing_uuids:
            logger.warning(missing_details_msg_tpl.format(uuid=uuid))

    return programs


def get_program_types(name=None):
    """Retrieve program types from the catalog service.

    Keyword Arguments:
        name (string): Name identifying a specific program.

    Returns:
        list of dict, representing program types.
        dict, if a specific program type is requested.
    """
    catalog_integration = CatalogIntegration.current()
    if catalog_integration.enabled:
        try:
            user = catalog_integration.get_service_user()
        except ObjectDoesNotExist:
            return []

        api = create_catalog_api_client(user)
        cache_key = '{base}.program_types'.format(base=catalog_integration.CACHE_KEY)

        data = get_edx_api_data(catalog_integration, 'program_types', api=api,
                                cache_key=cache_key if catalog_integration.is_cache_enabled else None)

        # Filter by name if a name was provided
        if name:
            data = next(program_type for program_type in data if program_type['name'] == name)

        return data
    else:
        return []


def get_currency_data():
    """Retrieve currency data from the catalog service.

    Returns:
        list of dict, representing program types.
        dict, if a specific program type is requested.
    """
    catalog_integration = CatalogIntegration.current()
    if catalog_integration.enabled:
        try:
            user = catalog_integration.get_service_user()
        except ObjectDoesNotExist:
            return []

        api = create_catalog_api_client(user)
        cache_key = '{base}.currency'.format(base=catalog_integration.CACHE_KEY)

        return get_edx_api_data(catalog_integration, 'currency', api=api, traverse_pagination=False,
                                cache_key=cache_key if catalog_integration.is_cache_enabled else None)
    else:
        return []


def format_price(price, symbol='$', code='USD'):
    """
    Format the price to have the appropriate currency and digits..

    :param price: The price amount.
    :param symbol: The symbol for the price (default: $)
    :param code: The currency code to be appended to the price (default: USD)
    :return: A formatted price string, i.e. '$10 USD', '$10.52 USD'.
    """
    if int(price) == price:
        return '{}{} {}'.format(symbol, int(price), code)
    return '{}{:0.2f} {}'.format(symbol, price, code)


def get_localized_price_text(price, request):
    """
    Returns the localized converted price as string (ex. '$150 USD')

    If the users location has been added to the request, this will return the given price based on conversion rate
    from the Catalog service and return a localized string otherwise will return the default price in USD
    """
    user_currency = {
        'symbol': '$',
        'rate': 1,
        'code': 'USD'
    }

    # session.country_code is added via CountryMiddleware in the LMS
    user_location = getattr(request, 'session', {}).get('country_code')

    # Override default user_currency if location is available
    if user_location and get_currency_data:
        currency_data = get_currency_data()
        user_country = pycountry.countries.get(alpha2=user_location)
        user_currency = currency_data.get(user_country.alpha3, user_currency)

    return format_price(
        price=(price * user_currency['rate']),
        symbol=user_currency['symbol'],
        code=user_currency['code']
    )


def get_programs_with_type(site, include_hidden=True):
    """
    Return the list of programs. You can filter the types of programs returned by using the optional
    include_hidden parameter. By default hidden programs will be included.

    The program dict is updated with the fully serialized program type.

    Arguments:
        site (Site): django.contrib.sites.models object

    Keyword Arguments:
        include_hidden (bool): whether to include hidden programs

    Return:
        list of dict, representing the active programs.
    """
    programs_with_type = []
    programs = get_programs(site)

    if programs:
        program_types = {program_type['name']: program_type for program_type in get_program_types()}
        for program in programs:
            if program['type'] not in program_types:
                continue

            if program['hidden'] and not include_hidden:
                continue

            # deepcopy the program dict here so we are not adding
            # the type to the cached object
            program_with_type = copy.deepcopy(program)
            program_with_type['type'] = program_types[program['type']]
            programs_with_type.append(program_with_type)

    return programs_with_type


def get_course_runs():
    """
    Retrieve all the course runs from the catalog service.

    Returns:
        list of dict with each record representing a course run.
    """
    catalog_integration = CatalogIntegration.current()
    course_runs = []
    if catalog_integration.enabled:
        try:
            user = catalog_integration.get_service_user()
        except ObjectDoesNotExist:
            logger.error(
                'Catalog service user with username [%s] does not exist. Course runs will not be retrieved.',
                catalog_integration.service_username,
            )
            return course_runs

        api = create_catalog_api_client(user)

        querystring = {
            'page_size': catalog_integration.page_size,
            'exclude_utm': 1,
        }

        course_runs = get_edx_api_data(catalog_integration, 'course_runs', api=api, querystring=querystring)

    return course_runs


def get_course_runs_for_course(course_uuid):
    catalog_integration = CatalogIntegration.current()

    if catalog_integration.is_enabled():
        try:
            user = catalog_integration.get_service_user()
        except ObjectDoesNotExist:
            logger.error(
                'Catalog service user with username [%s] does not exist. Course runs will not be retrieved.',
                catalog_integration.service_username,
            )
            return []

        api = create_catalog_api_client(user)
        cache_key = '{base}.course.{uuid}.course_runs'.format(
            base=catalog_integration.CACHE_KEY,
            uuid=course_uuid
        )
        data = get_edx_api_data(
            catalog_integration,
            'courses',
            resource_id=course_uuid,
            api=api,
            cache_key=cache_key if catalog_integration.is_cache_enabled else None,
            long_term_cache=True,
            many=False
        )
        return data.get('course_runs', [])
    else:
        return []


def get_course_uuid_for_course(course_run_key):
    """
    Retrieve the Course UUID for a given course key

    Arguments:
        course_run_key (CourseKey): A Key for a Course run that will be pulled apart to get just the information
        required for a Course (e.g. org+course)

    Returns:
        UUID: Course UUID and None if it was not retrieved.
    """
    catalog_integration = CatalogIntegration.current()

    if catalog_integration.is_enabled():
        try:
            user = catalog_integration.get_service_user()
        except ObjectDoesNotExist:
            logger.error(
                'Catalog service user with username [%s] does not exist. Course UUID will not be retrieved.',
                catalog_integration.service_username,
            )
            return []

        api = create_catalog_api_client(user)

        run_cache_key = '{base}.course_run.{course_run_key}'.format(
            base=catalog_integration.CACHE_KEY,
            course_run_key=course_run_key
        )

        course_run_data = get_edx_api_data(
            catalog_integration,
            'course_runs',
            resource_id=unicode(course_run_key),
            api=api,
            cache_key=run_cache_key if catalog_integration.is_cache_enabled else None,
            long_term_cache=True,
            many=False,
        )

        course_key_str = course_run_data.get('course', None)

        if course_key_str:
            run_cache_key = '{base}.course.{course_key}'.format(
                base=catalog_integration.CACHE_KEY,
                course_key=course_key_str
            )

            data = get_edx_api_data(
                catalog_integration,
                'courses',
                resource_id=course_key_str,
                api=api,
                cache_key=run_cache_key if catalog_integration.is_cache_enabled else None,
                long_term_cache=True,
                many=False,
            )
            uuid_str = data.get('uuid', None)
            if uuid_str:
                return uuid.UUID(uuid_str)
    return None


def get_pseudo_session_for_entitlement(entitlement):
    """
    This function is used to pass pseudo-data to the front end, returning a single session, regardless of whether that
    session is currently available.

    First tries to return the first available session, followed by the first session regardless of availability.
    Returns None if there are no sessions for that course.
    """
    sessions_for_course = get_course_runs_for_course(entitlement.course_uuid)
    available_sessions = get_fulfillable_course_runs_for_entitlement(entitlement, sessions_for_course)
    if available_sessions:
        return available_sessions[0]
    if sessions_for_course:
        return sessions_for_course[0]
    return None


def get_visible_sessions_for_entitlement(entitlement):
    """
    Takes an entitlement object and returns the course runs that a user can currently enroll in.
    """
    sessions_for_course = get_course_runs_for_course(entitlement.course_uuid)
    return get_fulfillable_course_runs_for_entitlement(entitlement, sessions_for_course)


def get_fulfillable_course_runs_for_entitlement(entitlement, course_runs):
    """
    Looks through the list of course runs and returns the course runs that can
    be applied to the entitlement.

    Args:
        entitlement (CourseEntitlement): The CourseEntitlement to which a
        course run is to be applied.
        course_runs (list): List of course run that we would like to apply
        to the entitlement.

    Return:
        list: A list of sessions that a user can apply to the provided entitlement.
    """
    enrollable_sessions = []

    # Only retrieve list of published course runs that can still be enrolled and upgraded
    search_time = datetime.datetime.now(UTC)
    for course_run in course_runs:
        course_id = CourseKey.from_string(course_run.get('key'))
        (user_enrollment_mode, is_active) = CourseEnrollment.enrollment_mode_for_user(
            user=entitlement.user,
            course_id=course_id
        )
        is_enrolled_in_mode = is_active and (user_enrollment_mode == entitlement.mode)
        if (course_run.get('status') == COURSE_PUBLISHED and
                is_course_run_entitlement_fulfillable(course_id, entitlement, search_time)):
            if (is_enrolled_in_mode and
                    entitlement.enrollment_course_run and
                    course_id == entitlement.enrollment_course_run.course_id):
                enrollable_sessions.append(course_run)
            elif not is_enrolled_in_mode:
                enrollable_sessions.append(course_run)

    enrollable_sessions.sort(key=lambda session: session.get('start'))
    return enrollable_sessions


def get_course_run_details(course_run_key, fields):
    """
    Retrieve information about the course run with the given id

    Arguments:
        course_run_key: key for the course_run about which we are retrieving information

    Returns:
        dict with language, start date, end date, and max_effort details about specified course run
    """
    catalog_integration = CatalogIntegration.current()
    course_run_details = dict()
    if catalog_integration.enabled:
        try:
            user = catalog_integration.get_service_user()
        except ObjectDoesNotExist:
            msg = 'Catalog service user {} does not exist. Data for course_run {} will not be retrieved'.format(
                catalog_integration.service_username,
                course_run_key
            )
            logger.error(msg)
            return course_run_details
        api = create_catalog_api_client(user)

        cache_key = '{base}.course_runs'.format(base=catalog_integration.CACHE_KEY)

        course_run_details = get_edx_api_data(catalog_integration, 'course_runs', api, resource_id=course_run_key,
                                              cache_key=cache_key, many=False, traverse_pagination=False, fields=fields)
    else:
        msg = 'Unable to retrieve details about course_run {} because Catalog Integration is not enabled'.format(
            course_run_key
        )
        logger.error(msg)
    return course_run_details
