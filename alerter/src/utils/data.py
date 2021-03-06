import json
import logging
from enum import Enum
from typing import Dict

import requests
from prometheus_client.parser import text_string_to_metric_families

from src.utils.exceptions import (NoMetricsGivenException,
                                  MetricNotFoundException)


class RequestStatus(Enum):
    SUCCESS = True
    FAILED = False


def get_json(endpoint: str, logger: logging.Logger, params=None):
    if params is None:
        params = {}
    get_ret = requests.get(url=endpoint, params=params, timeout=15)
    logger.debug("get_json: get_ret: %s", get_ret)
    return json.loads(get_ret.content.decode('UTF-8'))


def get_prometheus(endpoint: str, logger: logging.Logger):
    metrics = requests.get(endpoint, timeout=10).content
    logger.debug("Retrieved prometheus data from endpoint: " + endpoint)
    return metrics.decode('utf-8')


def get_prometheus_metrics_data(endpoint: str, requested_metrics: list,
                                logger: logging.Logger) -> Dict:
    response = {}
    if len(requested_metrics) == 0:
        raise NoMetricsGivenException("No metrics given when requesting"
                                      "prometheus data from " + endpoint)

    metrics = get_prometheus(endpoint, logger)
    for family in text_string_to_metric_families(metrics):
        for sample in family.samples:
            if sample.name in requested_metrics:
                if sample.name not in response:
                    if sample.labels != {}:
                        response[sample.name] = {}
                        response[sample.name][json.dumps(sample.labels)] = \
                            sample.value
                    else:
                        response[sample.name] = sample.value
                else:
                    if sample.labels != {}:
                        response[sample.name][json.dumps(sample.labels)] = \
                            sample.value
                    else:
                        response[sample.name] = sample.value + \
                                                response[sample.name]

    # Raises a meaningful exception if some requested metrics are not found at
    # the endpoint
    missing_metrics = set(requested_metrics) - set(response)
    for metric in missing_metrics:
        raise MetricNotFoundException(metric, endpoint)

    return response
