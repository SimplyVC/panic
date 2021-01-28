import logging
import os
import time

import pika.exceptions

from src.alerter.alerters.alerter import Alerter
from src.alerter.alerters.github import GithubAlerter
from src.alerter.alerters.system import SystemAlerter
from src.configs.system_alerts import SystemAlertsConfig
from src.utils.logging import create_logger, log_and_print
from src.utils.starters import get_initialisation_error_message
from src.utils.env import ALERTERS_LOG_FILE_TEMPLATE, LOGGING_LEVEL


def _initialise_alerter_logger(alerter_name: str) -> logging.Logger:
    # Try initializing the logger until successful. This had to be done
    # separately to avoid instances when the logger creation failed and we
    # attempt to use it.
    while True:
        try:
            alerter_logger = create_logger(
                ALERTERS_LOG_FILE_TEMPLATE.format(alerter_name),
                alerter_name, LOGGING_LEVEL, rotating=True)
            break
        except Exception as e:
            msg = get_initialisation_error_message(alerter_name, e)
            # Use a dummy logger in this case because we cannot create the
            # alerter's logger.
            log_and_print(msg, logging.getLogger('DUMMY_LOGGER'))
            time.sleep(10)  # sleep 10 seconds before trying again

    return alerter_logger


def _initialise_system_alerter(system_alerts_config: SystemAlertsConfig,
                               chain: str) -> SystemAlerter:
    # Alerter name based on system
    alerter_name = "System alerter ({})".format(chain)

    system_alerter_logger = _initialise_alerter_logger(alerter_name)

    # Try initializing an alerter until successful
    while True:
        try:
            system_alerter = SystemAlerter(alerter_name, system_alerts_config,
                                           system_alerter_logger)
            log_and_print("Successfully initialised {}".format(alerter_name),
                          system_alerter_logger)
            break
        except Exception as e:
            msg = get_initialisation_error_message(alerter_name, e)
            log_and_print(msg, system_alerter_logger)
            time.sleep(10)  # sleep 10 seconds before trying again

    return system_alerter


def _initialise_github_alerter() -> GithubAlerter:
    alerter_name = "GitHub Alerter"

    github_alerter_logger = _initialise_alerter_logger(alerter_name)

    # Try initializing an alerter until successful
    while True:
        try:
            github_alerter = GithubAlerter(alerter_name, github_alerter_logger)
            log_and_print("Successfully initialised {}".format(alerter_name),
                          github_alerter_logger)
            break
        except Exception as e:
            msg = get_initialisation_error_message(alerter_name, e)
            log_and_print(msg, github_alerter_logger)
            time.sleep(10)  # sleep 10 seconds before trying again

    return github_alerter


def start_github_alerter() -> None:
    github_alerter = _initialise_github_alerter()
    start_alerter(github_alerter)


def start_system_alerter(system_alerts_config: SystemAlertsConfig,
                         chain: str) -> None:
    system_alerter = _initialise_system_alerter(system_alerts_config, chain)
    start_alerter(system_alerter)


def start_alerter(alerter: Alerter) -> None:
    sleep_period = 10

    while True:
        try:
            log_and_print("{} started.".format(alerter), alerter.logger)
            alerter.start()
        except (pika.exceptions.AMQPConnectionError,
                pika.exceptions.AMQPChannelError):
            # Error would have already been logged by RabbitMQ logger.
            # Since we have to re-connect just break the loop.
            log_and_print("{} stopped.".format(alerter), alerter.logger)
        except Exception:
            # Close the connection with RabbitMQ if we have an unexpected
            # exception, and start again
            alerter.disconnect_from_rabbit()
            log_and_print("{} stopped.".format(alerter), alerter.logger)
            log_and_print("Restarting {} in {} seconds.".format(
                alerter, sleep_period), alerter.logger)
            time.sleep(sleep_period)
