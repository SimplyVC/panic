import multiprocessing

import pika.exceptions

from alerter.src.monitors.managers.system import SystemMonitorsManager
from alerter.src.utils.logging import create_logger, log_and_print


def run_system_monitors_manager() -> None:
    # Create the loggers
    # TODO: Change like .env file accoridng to manager
    GENERAL_LOG_FILE = 'logs/managers/{}.log'
    LOGGING_LEVEL = 'INFO'
    logger_general = create_logger(
        GENERAL_LOG_FILE.format('System Monitors Manager'),
        'System Monitors Manager', LOGGING_LEVEL, rotating=True)

    system_monitors_manager = SystemMonitorsManager(logger_general)

    while True:
        try:
            system_monitors_manager.manage()
        except pika.exceptions.AMQPConnectionError:
            # Error would have already been logged by RabbitMQ logger.
            # Since we have to re-connect just break the loop.
            log_and_print('{} stopped.'.format(system_monitors_manager),
                          logger_general)
        except Exception:
            # Close the connection with RabbitMQ if we have an unexpected
            # exception, and start again
            system_monitors_manager.rabbitmq.disconnect_till_successful()
            log_and_print('{} stopped.'.format(system_monitors_manager),
                          logger_general)


if __name__ == '__main__':
    # Start the managers in a separate process
    system_monitors_manager_process = multiprocessing.Process(
        target=run_system_monitors_manager, args=[])
    system_monitors_manager_process.start()

    # If we don't wait for the processes to terminate the root process will exit
    system_monitors_manager_process.join()

# TODO: Put environment variables again, run alerter, monitors and managers
# TODO: Continue testing, for example connection errors, throw exceptions custom
#     : etc to see what happens
# TODO: Check IF logging is enough, possibly improve it
