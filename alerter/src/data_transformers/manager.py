import logging
import multiprocessing
import sys
from datetime import datetime
from types import FrameType
from typing import Dict

import pika
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel

from src.abstract.publisher_subscriber import PublisherSubscriberComponent
from src.data_transformers.starters import (start_system_data_transformer,
                                            start_github_data_transformer)
from src.message_broker.rabbitmq import RabbitMQApi
from src.utils.constants import (HEALTH_CHECK_EXCHANGE,
                                 SYSTEM_DATA_TRANSFORMER_NAME,
                                 GITHUB_DATA_TRANSFORMER_NAME)
from src.utils.exceptions import MessageWasNotDeliveredException
from src.utils.logging import log_and_print

DT_MAN_INPUT_QUEUE = 'data_transformers_manager_queue'
DT_MAN_INPUT_ROUTING_KEY = 'ping'


class DataTransformersManager(PublisherSubscriberComponent):
    def __init__(self, logger: logging.Logger, name: str,
                 rabbitmq: RabbitMQApi) -> None:
        self._name = name
        self._transformer_process_dict = {}

        super().__init__(logger, rabbitmq)

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def transformer_process_dict(self) -> Dict:
        return self._transformer_process_dict

    def _initialise_rabbitmq(self) -> None:
        self.rabbitmq.connect_till_successful()

        # Declare consuming intentions
        self.logger.info("Creating '%s' exchange", HEALTH_CHECK_EXCHANGE)
        self.rabbitmq.exchange_declare(HEALTH_CHECK_EXCHANGE, 'topic', False,
                                       True, False, False)
        self.logger.info("Creating queue '%s'", DT_MAN_INPUT_QUEUE)
        self.rabbitmq.queue_declare(DT_MAN_INPUT_QUEUE, False, True, False,
                                    False)
        self.logger.info("Binding queue '%s' to exchange '%s' with routing key "
                         "'%s'", DT_MAN_INPUT_QUEUE, HEALTH_CHECK_EXCHANGE,
                         DT_MAN_INPUT_ROUTING_KEY)
        self.rabbitmq.queue_bind(DT_MAN_INPUT_QUEUE, HEALTH_CHECK_EXCHANGE,
                                 DT_MAN_INPUT_ROUTING_KEY)
        self.logger.debug("Declaring consuming intentions on '%s'",
                          DT_MAN_INPUT_QUEUE)
        self.rabbitmq.basic_consume(DT_MAN_INPUT_QUEUE, self._process_ping,
                                    True, False, None)

        # Declare publishing intentions
        self.logger.info("Setting delivery confirmation on RabbitMQ channel")
        self.rabbitmq.confirm_delivery()

    def _listen_for_data(self) -> None:
        self.rabbitmq.start_consuming()

    def _send_heartbeat(self, data_to_send: Dict) -> None:
        self.rabbitmq.basic_publish_confirm(
            exchange=HEALTH_CHECK_EXCHANGE, routing_key='heartbeat.manager',
            body=data_to_send, is_body_dict=True,
            properties=pika.BasicProperties(delivery_mode=2), mandatory=True)
        self.logger.debug("Sent heartbeat to '%s' exchange",
                          HEALTH_CHECK_EXCHANGE)

    def _start_transformers_processes(self) -> None:
        # Start the system data transformer in a separate process if it is not
        # yet started or it is not alive. This must be done in case of a
        # restart of the manager.
        if SYSTEM_DATA_TRANSFORMER_NAME not in \
                self.transformer_process_dict or not \
                self.transformer_process_dict[
                    SYSTEM_DATA_TRANSFORMER_NAME].is_alive():
            log_and_print("Attempting to start the {}.".format(
                SYSTEM_DATA_TRANSFORMER_NAME), self.logger)
            system_data_transformer_process = multiprocessing.Process(
                target=start_system_data_transformer, args=())
            system_data_transformer_process.daemon = True
            system_data_transformer_process.start()
            self._transformer_process_dict[SYSTEM_DATA_TRANSFORMER_NAME] = \
                system_data_transformer_process

        # Start the github data transformer in a separate process if it is not
        # yet started or it is not alive. This must be done in case of a
        # restart of the manager.
        if GITHUB_DATA_TRANSFORMER_NAME not in \
                self.transformer_process_dict or not \
                self.transformer_process_dict[
                    GITHUB_DATA_TRANSFORMER_NAME].is_alive():
            log_and_print("Attempting to start the {}.".format(
                GITHUB_DATA_TRANSFORMER_NAME), self.logger)
            github_data_transformer_process = multiprocessing.Process(
                target=start_github_data_transformer, args=())
            github_data_transformer_process.daemon = True
            github_data_transformer_process.start()
            self._transformer_process_dict[GITHUB_DATA_TRANSFORMER_NAME] = \
                github_data_transformer_process

    def _process_ping(
            self, ch: BlockingChannel, method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties, body: bytes) -> None:
        data = body
        self.logger.debug("Received %s", data)

        heartbeat = {}
        try:
            heartbeat['component_name'] = self.name
            heartbeat['running_processes'] = []
            heartbeat['dead_processes'] = []
            for transformer_name, process in \
                    self.transformer_process_dict.items():
                if process.is_alive():
                    heartbeat['running_processes'].append(transformer_name)
                else:
                    heartbeat['dead_processes'].append(transformer_name)
                    process.join()  # Just in case, to release resources
            heartbeat['timestamp'] = datetime.now().timestamp()

            # Restart dead transformers
            if len(heartbeat['dead_processes']) != 0:
                self._start_transformers_processes()
        except Exception as e:
            # If we encounter an error during processing log the error and
            # return so that no heartbeat is sent
            self.logger.error("Error when processing %s", data)
            self.logger.exception(e)
            return

        # Send heartbeat if processing was successful
        try:
            self._send_heartbeat(heartbeat)
        except MessageWasNotDeliveredException as e:
            # Log the message and do not raise it as there is no use in
            # re-trying to send a heartbeat
            self.logger.exception(e)
        except Exception as e:
            # For any other exception raise it.
            raise e

    def start(self) -> None:
        log_and_print("{} started.".format(self), self.logger)
        self._initialise_rabbitmq()
        while True:
            try:
                self._start_transformers_processes()
                self._listen_for_data()
            except (pika.exceptions.AMQPConnectionError,
                    pika.exceptions.AMQPChannelError) as e:
                # If we have either a channel error or connection error, the
                # channel is reset, therefore we need to re-initialise the
                # connection or channel settings
                raise e
            except Exception as e:
                self.logger.exception(e)
                raise e

    # If termination signals are received, terminate all child process and exit
    def _on_terminate(self, signum: int, stack: FrameType) -> None:
        log_and_print("{} is terminating. Connections with RabbitMQ will be "
                      "closed, and any running data transformers will be "
                      "stopped gracefully. Afterwards the {} process will "
                      "exit.".format(self, self), self.logger)
        self.disconnect_from_rabbit()

        for transformer, process in self.transformer_process_dict.items():
            log_and_print("Terminating the process of {}".format(transformer),
                          self.logger)
            process.terminate()
            process.join()

        log_and_print("{} terminated.".format(self), self.logger)
        sys.exit()

    def _send_data(self, *args) -> None:
        """
        This function was not implemented because the manager does not need
        to send any data other than heartbeats. The component is still a
        publisher because we are publishing heartbeats.
        """
        pass
