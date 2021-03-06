"""Queries for SQLAlchamy STAC view."""
import logging

from .models import APIKey
from .models import Attribute
from .models import CatalogEntry
from .models import Job
from sqlalchemy import and_
from sqlalchemy import func

LOGGER = logging.getLogger('stac')


def find_catalog_by_id(catalog, asset_id):
    """Find the single catalong entry matching catalog:asset_id.

    Args:
        catalog (str): catalog id
        asset_id (str): asset id in that catalog.

    Returns:
        CatalogEntry that matches the catalog:asset_id pair or None.

    """
    return CatalogEntry.query.filter(
        CatalogEntry.catalog == catalog,
        CatalogEntry.asset_id == asset_id).one_or_none()


def get_allowed_permissions_map(api_key):
    """Get allowed permissions for the given api key.

    Args:
        api_key (str): arbitrary api key string or None

    Returns:
        dictionary with 'READ' and 'WRITE' keys mapping to a set of catalog
        names and/or '*' to indicate full permissions allowed or None if
        the api key is not found. Form is [READ|WRITE]:{catalog_id}

    """
    if api_key is None:
        return None

    result = APIKey.query.filter(
        APIKey.api_key == api_key).one_or_none()

    LOGGER.debug(f'got these permissions for {api_key} {result}')
    if result is None:
        return None

    allowed_permissions = {}
    for permission_type in ['READ', 'WRITE']:
        allowed_permissions[permission_type] = set([
            permission.split(':')[1]
            for permission in result.permissions.split(' ')
            if permission.startswith(f'{permission_type}:')])

    return allowed_permissions


def get_assets_query(
        catalog_set, bounding_box_list=None, datetime_str=None,
        asset_id=None, description=None):
    """Get a Query object based on assets that match the search terms.

    Args:
        catalog_set (set): Only assets in these catalogs are returned.
        bounding_box_list (list): bounding box coordinates in order of
            [xmin, ymin, xmax, ymax]. If not None, any assets that intersect
            this box are returned.
        datetime_str (str):  "exact time" | "low_time/high_time" |
            "../high time" | "low time/..". If not None, any assets are bounded
            against this time or time range.
        asset_id (str): If not None, search for partial or exact match to this
            asset id.
        description (str): If not None, search for this partial or exact match
            to this description.


    Returns:
        List of CatalogEntry for those entries that match the search
        parameters.

    """
    query_parameter_list = []
    if bounding_box_list is not None:
        LOGGER.debug(f'querying bounding: {bounding_box_list}')
        s_xmin, s_ymin, s_xmax, s_ymax = bounding_box_list

        query_parameter_list.extend(
            [s_xmin <= CatalogEntry.bb_xmax,
             s_xmax >= CatalogEntry.bb_xmin,
             s_ymin <= CatalogEntry.bb_ymax,
             s_ymax >= CatalogEntry.bb_ymin])

    if datetime_str:
        LOGGER.debug(f'querying datetime_str {datetime_str}')
        if '/' in datetime_str:
            min_time, max_time = datetime_str.split('/')
            if min_time != '..':
                query_parameter_list.append(
                    CatalogEntry.utc_datetime >= min_time)
            if max_time != '..':
                query_parameter_list.append(
                    CatalogEntry.utc_datetime <= max_time)
        else:
            query_parameter_list.append(
                CatalogEntry.utc_datetime == datetime_str)

    LOGGER.debug(f'queryign catalog set {catalog_set}')
    query_parameter_list.append(CatalogEntry.catalog.in_(catalog_set))

    if asset_id:
        LOGGER.debug(f'querying asset id{asset_id}')
        query_parameter_list.append(CatalogEntry.asset_id.ilike(asset_id))

    if description:
        LOGGER.debug(f'querying description {description}')
        query_parameter_list.append(CatalogEntry.description.ilike(
            description))

    LOGGER.debug(f'whole query list: {query_parameter_list}')
    return CatalogEntry.query.filter(and_(*query_parameter_list))


def get_asset_attributes(catalog, asset_id):
    """Get additional asset attributes associated with catalog:asset_id.

    Args:
        catalog (str): the catalog to search in
        asset_id (str): the asset id to search for.

    Returns:
        dict of key/value pairs attributes associated with this catalog:asset.

    """
    return {
        attribute.key: attribute.value
        for attribute in Attribute.query.filter(and_(
            Attribute.asset_id == asset_id,
            Attribute.catalog == catalog)).all()}


def get_job_status(job_id):
    """Get Job status table for the given job_id.

    Args:
        job_id (str): unique job id

    Returns:
        a Job object describing given job or None if not in table.

    """
    return Job.query.filter(Job.job_id == job_id).one_or_none()


def get_expired_catalog_entries(current_time):
    """Returns all catalog entries where expiration time <= `current_time`.

    Args:
        current_time (str): UTC formatted string of current time.

    Returns:
        List of CatalogEntry where
            CatalogEntry.expiration_utc_datetime <= current time if the
            CatalogEntry.expiration_utc_datetime is defined.

    """
    return CatalogEntry.query.filter(and_(
            CatalogEntry.expiration_utc_datetime <= current_time,
            CatalogEntry.expiration_utc_datetime != '',
            CatalogEntry.expiration_utc_datetime.isnot(None)))


def get_running_jobs():
    """Return the number of active (not error or complete) jobs."""
    return Job.query.filter(Job.job_status.ilike('ACTIVE%')).count()
