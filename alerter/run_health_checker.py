import logging
import multiprocessing
import signal
import sys
import time
from types import FrameType

from src.health_checker.manager import HealthCheckerManager
from src.utils import env
from src.utils.logging import create_logger, log_and_print
from src.utils.starters import get_initialisation_error_message


def _initialise_logger(log_name: str, log_file_template: str) -> logging.Logger:
    # Try initializing the logger until successful. This had to be done
    # separately to avoid instances when the logger creation failed and we
    # attempt to use it.
    while True:
        try:
            new_logger = create_logger(
                log_file_template.format(log_name), log_name, env.LOGGING_LEVEL,
                rotating=True)
            break
        except Exception as e:
            msg = get_initialisation_error_message(log_name, e)
            # Use a dummy logger in this case because we cannot create the
            # manager's logger.
            log_and_print(msg, dummy_logger)
            log_and_print("Re-attempting initialization procedure of {}."
                          .format(log_name), dummy_logger)
            time.sleep(10)  # sleep 10 seconds before trying again

    return new_logger


def _initialise_health_checker_manager() -> HealthCheckerManager:
    manager_name = 'Health Checker Manager'

    health_checker_manager_logger = _initialise_logger(
        manager_name, env.MANAGERS_LOG_FILE_TEMPLATE)

    # Attempt to initialise the health checker manager
    while True:
        try:
            health_checker_manager = HealthCheckerManager(
                health_checker_manager_logger, manager_name)
            break
        except Exception as e:
            msg = get_initialisation_error_message(manager_name, e)
            log_and_print(msg, health_checker_manager_logger)
            log_and_print("Re-attempting initialization procedure of {}."
                          .format(manager_name), health_checker_manager_logger)
            time.sleep(10)  # sleep 10 seconds before trying again

    return health_checker_manager


def run_health_checker_manager() -> None:
    sleep_period = 10
    health_checker_manager = _initialise_health_checker_manager()

    while True:
        try:
            log_and_print("{} started.".format(health_checker_manager),
                          health_checker_manager.logger)
            health_checker_manager.manage()
        except Exception as e:
            health_checker_manager.logger.exception(e)
            log_and_print("{} stopped.".format(health_checker_manager),
                          health_checker_manager.logger)
            log_and_print("Restarting {} in {} seconds.".format(
                health_checker_manager, sleep_period),
                health_checker_manager.logger)
            time.sleep(sleep_period)


# If termination signals are received, terminate all child process and exit
def on_terminate(signum: int, stack: FrameType) -> None:
    log_and_print("The Health Checker is terminating. All components will be "
                  "stopped gracefully.", dummy_logger)

    log_and_print("Terminating the Health Checker Manager.", dummy_logger)
    health_checker_manager_process.terminate()
    health_checker_manager_process.join()

    log_and_print("The health checker process has ended.", dummy_logger)
    sys.exit()


if __name__ == '__main__':
    dummy_logger = logging.getLogger('Dummy')

    # Start the managers in a separate process
    health_checker_manager_process = multiprocessing.Process(
        target=run_health_checker_manager, args=())
    health_checker_manager_process.start()

    signal.signal(signal.SIGTERM, on_terminate)
    signal.signal(signal.SIGINT, on_terminate)
    signal.signal(signal.SIGHUP, on_terminate)

    # If we don't wait for the processes to terminate the root process will
    # exit
    health_checker_manager_process.join()

    log_and_print("The health checker process has ended.", dummy_logger)
    sys.stdout.flush()
