import csv
import os

from datetime import datetime


def fields_remove(alert: dict[str], remove_empty=True) -> dict[str]:
    """Delete fields that are unnecessary for analysis

    Args:
        alert (dict[str]): alert dict
        remove_empty (bool, optional): is it neccessary to remove empty fields. Defaults to True.

    Returns:
        dict[str]: cleaned alert
    """
    RM_FIELDS = [
        'alert_hash', 'alert_id', 'context.new_status', \
        # siem
        'info_max_time', 'info_min_time', 'info_search_time', 'info_sid', 'search_now', \
        # alerts
        'EDR_timeline_link', 'user_department_ancestors', 'net_user_department_ancestors', \
    ]
    SV_FIELDS = ['context.resolution', 'context.klassifikaciaTp']

    return {k: v for k, v in alert.items() if (v != '' or k in SV_FIELDS) and k not in RM_FIELDS}


def fields_rename(alert: dict[str]) -> dict[str]:
    mapping = {'context.resolution': 'alert_verdict', 'context.klassifikaciaTp': 'alert_classification'}
    return {mapping.get(key, key): value for key, value in alert.items()}


def fields_cut_long(alert: dict[str], lenght: int = 200) -> dict[str]:
    return {k: v[:lenght] if isinstance(v, str) and len(v) > lenght else v for k, v in alert.items()}


def fields_norm_values(alert: dict[str]) -> dict[str]:
    """Normalise values of fields for analysis

    Args:
        alert (dict[str]): alert body

    Returns:
        dict[str]: prepared alert
    """
    # normalise value of resolution
    mapping_resolution = {'fixed': 'TruePositive', 'invalid': 'FalsePositive', 'won\'tFix': 'WillNotBeFixed'}
    alert['context.resolution'] = mapping_resolution.get(alert.get('context.resolution', None), 'UnknownResolution')

    # parse time
    if isinstance(alert['_time'], str):
        alert['_time'] = datetime.strptime(alert['_time'], '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()

    # remove stash from sourcetype
    alert['sourcetype'] = str(alert.get('sourcetype', '')).replace('stash\n', '')

    return alert


def fields_process(alert: dict[str]) -> dict[str]:
    _alert = alert.copy()
    _alert = fields_norm_values(_alert)
    _alert = fields_remove(_alert)
    _alert = fields_rename(_alert)
    _alert = fields_cut_long(_alert)
    return _alert


def get_past_alerts(alert_name: str, exclude: list = []) -> dict:
    """get alerts previosly processed

    Args:
        alert_name (str): alert name
        exclude (list, optional): exclude alerts key. Defaults to [].

    Returns:
        dict: _description_
    """
    with open(os.getenv('DIR_CACHE', '/data/alerts.csv')) as csvfile:
        reader = csv.DictReader(csvfile)
        result = list()
        for row in reader:
            if alert_name == row.get('search_name', '') and row['context.ticket_key'] not in exclude:
                row = fields_process(row)
                result.append(row)

    result = sorted(result, key=lambda d: d['_time'], reverse=True)

    return result
