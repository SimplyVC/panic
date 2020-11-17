import copy
import json
import logging
import sys
from types import FrameType
from typing import Dict

import pika
import pika.exceptions
from src.alerter.alerters.alerter import Alerter
from src.alerter.alerts.system_alerts import (
    InvalidUrlAlert, OpenFileDescriptorsDecreasedBelowThresholdAlert,
    OpenFileDescriptorsIncreasedAboveThresholdAlert,
    ReceivedUnexpectedDataAlert, SystemBackUpAgainAlert,
    SystemCPUUsageDecreasedBelowThresholdAlert,
    SystemCPUUsageIncreasedAboveThresholdAlert,
    SystemRAMUsageDecreasedBelowThresholdAlert,
    SystemRAMUsageIncreasedAboveThresholdAlert, SystemStillDownAlert,
    SystemStorageUsageDecreasedBelowThresholdAlert,
    SystemStorageUsageIncreasedAboveThresholdAlert, SystemWentDownAtAlert)
from src.configs.system_alerts import SystemAlertsConfig
from src.utils.alert import floaty
from src.utils.exceptions import (MessageWasNotDeliveredException,
                                  ReceivedUnexpectedDataException)
from src.utils.logging import log_and_print
from src.utils.timing import TimedTaskLimiter


class SystemAlerter(Alerter):
    def __init__(self, alerts_config_name: str,
                 system_alerts_config: SystemAlertsConfig,
                 logger: logging.Logger) -> None:
        super().__init__(alerts_config_name, logger)
        self._system_alerts_config = system_alerts_config
        self._down_time_counter = 0
        self._queue_used = ''

    @property
    def alerts_configs(self) -> SystemAlertsConfig:
        return self._system_alerts_config

    def _initialize_alerter(self) -> None:
        self.rabbitmq.connect_till_successful()
        self.logger.info('Creating \'alert\' exchange')
        self.rabbitmq.exchange_declare(exchange='alert',
                                       exchange_type='topic', passive=False,
                                       durable=True, auto_delete=False,
                                       internal=False)
        self._queue_used = 'system_alerter_queue_' + \
                           self.alerts_configs.parent_id
        self.logger.info('Creating queue \'{}\''.format(self._queue_used))
        self.rabbitmq.queue_declare(self._queue_used, passive=False,
                                    durable=True, exclusive=False,
                                    auto_delete=False)
        routing_key = 'alerter.system.' + self.alerts_configs.parent_id
        self.logger.info('Binding queue \'{}\' to exchange '
                         '\'alert\' with routing key \'{}\''
                         ''.format(self._queue_used, routing_key))
        self.rabbitmq.queue_bind(queue=self._queue_used,
                                 exchange='alert',
                                 routing_key=routing_key)

        # Pre-fetch count is 10 times less the maximum queue size
        prefetch_count = round(self.publishing_queue.maxsize / 5)
        self.rabbitmq.basic_qos(prefetch_count=prefetch_count)
        self.logger.info('Declaring consuming intentions')

        # Set producing configuration
        self.logger.info('Setting delivery confirmation on RabbitMQ channel')
        self.rabbitmq.confirm_delivery()
        # TODO remove queue_purge for production
        self.rabbitmq.queue_purge(self._queue_used)
        self.rabbitmq.basic_consume(queue=self._queue_used,
                                    on_message_callback=self._process_data,
                                    auto_ack=False,
                                    exclusive=False,
                                    consumer_tag=None)

    def _process_data(self,
                      ch: pika.adapters.blocking_connection.BlockingChannel,
                      method: pika.spec.Basic.Deliver,
                      properties: pika.spec.BasicProperties,
                      body: bytes) -> None:
        data_received = json.loads(body.decode())
        parsed_routing_key = method.routing_key.split('.')
        processing_error = False
        try:
            if self.alerts_configs.parent_id in parsed_routing_key:
                if 'result' in data_received:
                    metrics = data_received['result']['data']
                    self._process_results(data_received['result']['data'],
                                          data_received['result']['meta_data'])
                elif 'error' in data_received:
                    self._process_errors(data_received['error'])
                else:
                    raise ReceivedUnexpectedDataException(
                        '{}: _process_data'.format(self))
        except Exception as e:
            self.logger.error("Error when processing {}".format(data_received))
            self.logger.exception(e)
            processing_error = True

        # If the data is processed, it can be acknowledged.
        self.rabbitmq.basic_ack(method.delivery_tag, False)

        # Place the data on the publishing queue if there were no processing
        # errors. This is done after acknowledging the data, so that if
        # acknowledgement fails, the data is processed again and we do not have
        # duplication of data in the queue.
        if not processing_error:
            self._place_latest_data_on_queue()

        # Send any data waiting in the publisher queue, if any
        try:
            self._send_data()
        except (pika.exceptions.AMQPChannelError,
                pika.exceptions.AMQPConnectionError) as e:
            # No need to acknowledge in this case as channel is closed. Logging
            # would have also been done by RabbitMQ.
            raise e
        except MessageWasNotDeliveredException as e:
            # Log the message and do not raise the exception so that the
            # message can be acknowledged and removed from the rabbit queue.
            # Note this message will still reside in the publisher queue.
            self.logger.exception(e)
        except Exception as e:
            # For any other exception acknowledge and raise it, so the
            # message is removed from the rabbit queue as this message will now
            # reside in the publisher queue
            raise e

    def _process_errors(self, error_data: Dict) -> None:
        is_down = self.alerts_configs.system_is_down
        meta_data = error_data['meta_data']
        if int(error_data['code']) == 5008:
            alert = ReceivedUnexpectedDataAlert(
                error_data['message'], 'ERROR', meta_data['time'],
                meta_data['system_parent_id'], meta_data['system_id']
            )
            self._data_for_alerting = alert.alert_data
            self.logger.debug('Successfully classified alert {}'
                              ''.format(alert.alert_data))
            self._place_latest_data_on_queue()
        elif int(error_data['code']) == 5009:
            alert = InvalidUrlAlert(
                error_data['message'], 'ERROR', meta_data['time'],
                meta_data['system_parent_id'], meta_data['system_id']
            )
            self._data_for_alerting = alert.alert_data
            self.logger.debug('Successfully classified alert {}'
                              ''.format(alert.alert_data))
            self._place_latest_data_on_queue()
        elif int(error_data['code']) == 5004:
            if is_down['enabled']:
                current = float(error_data['went_down_at']['current'])
                previous = error_data['went_down_at']['previous']
                difference = float(meta_data['time']) - current
                if previous is None:
                    if (int(is_down['critical_repeat']) <= difference and
                            is_down['critical_enabled']):
                        alert = SystemWentDownAtAlert(
                            meta_data['system_name'], 'CRITICAL',
                            meta_data['time'], meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                        self._data_for_alerting = alert.alert_data
                        self.logger.debug('Successfully classified alert {}'
                                          ''.format(alert.alert_data))
                        self._place_latest_data_on_queue()
                    else:
                        alert = SystemWentDownAtAlert(
                            meta_data['system_name'], 'WARNING',
                            meta_data['time'], meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                        self._data_for_alerting = alert.alert_data
                        self.logger.debug('Successfully classified alert {}'
                                          ''.format(alert.alert_data))
                        self._place_latest_data_on_queue()
                else:
                    if (int(is_down['critical_repeat']) > difference >=
                        int(is_down['warning_repeat']) and
                        is_down['warning_enabled'] and
                            is_down['warning_limiter'].can_do_task()):
                        alert = SystemStillDownAlert(
                            meta_data['system_name'], difference, 'WARNING',
                            meta_data['time'], meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                        self._data_for_alerting = alert.alert_data
                        self.logger.debug('Successfully classified alert {}'
                                          ''.format(alert.alert_data))
                        self._place_latest_data_on_queue()
                        is_down['warning_limiter'].did_task()
                    elif (int(is_down['critical_repeat']) <= difference and
                          is_down['critical_enabled'] and
                          is_down['critical_limiter'].can_do_task()):
                        alert = SystemStillDownAlert(
                            meta_data['system_name'], difference, 'CRITICAL',
                            meta_data['time'], meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                        self._data_for_alerting = alert.alert_data
                        self.logger.debug('Successfully classified alert {}'
                                          ''.format(alert.alert_data))
                        self._place_latest_data_on_queue()
                        is_down['critical_limiter'].did_task()
        else:
            raise ReceivedUnexpectedDataException(
                        '{}: _process_errors'.format(self))

    def _process_results(self, metrics: Dict, meta_data: Dict) -> None:
        open_fd = self.alerts_configs.open_file_descriptors
        cpu_use = self.alerts_configs.system_cpu_usage
        storage = self.alerts_configs.system_storage_usage
        ram_use = self.alerts_configs.system_ram_usage
        is_down = self.alerts_configs.system_is_down

        if is_down['enabled']:
            previous = metrics['went_down_at']['previous']
            if previous is not None:
                alert = SystemBackUpAgainAlert(
                    meta_data['system_name'], 'INFO',
                    meta_data['last_monitored'], meta_data['system_parent_id'],
                    meta_data['system_id']
                )
                self._data_for_alerting = alert.alert_data
                self.logger.debug('Successfully classified alert {}'
                                  ''.format(alert.alert_data))
                self._place_latest_data_on_queue()

        if open_fd['enabled']:
            current = metrics['open_file_descriptors']['current']
            previous = metrics['open_file_descriptors']['previous']
            if current not in [previous, None]:
                if (int(open_fd['warning_threshold']) <= float(current) <
                    int(open_fd['critical_threshold']) and
                    open_fd['warning_enabled'] and not
                    int(open_fd['warning_threshold']) <= floaty(previous) <
                    int(open_fd['critical_threshold']) and not
                    floaty(previous) >=
                        int(open_fd['critical_threshold'])):
                    alert = \
                        OpenFileDescriptorsIncreasedAboveThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'WARNING',
                            meta_data['last_monitored'], 'WARNING',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                elif (float(current) >= int(open_fd['critical_threshold']) and
                      open_fd['critical_enabled'] and
                      open_fd['limiter'].can_do_task()):
                    alert = \
                        OpenFileDescriptorsIncreasedAboveThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'CRITICAL',
                            meta_data['last_monitored'], 'CRITICAL',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                    open_fd['limiter'].did_task()
                elif (float(current) < floaty(previous) and
                      floaty(previous) >= int(open_fd['warning_threshold']) and
                      float(current) < int(open_fd['warning_threshold']) and
                      open_fd['warning_enabled']):
                    alert = \
                        OpenFileDescriptorsDecreasedBelowThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'INFO',
                            meta_data['last_monitored'], 'WARNING',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                elif (float(current) < floaty(previous) and
                      floaty(previous) >= int(open_fd['critical_threshold'])
                      and float(current) < int(open_fd['critical_threshold'])
                      and open_fd['critical_enabled']):
                    alert = \
                        OpenFileDescriptorsDecreasedBelowThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'INFO',
                            meta_data['last_monitored'], 'CRITICAL',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()

        if storage['enabled']:
            current = metrics['system_storage_usage']['current']
            previous = metrics['system_storage_usage']['previous']
            if current not in [previous, None]:
                if (int(storage['warning_threshold']) <= float(current) <
                    int(storage['critical_threshold']) and
                    storage['warning_enabled'] and not
                    int(storage['warning_threshold']) <= floaty(previous) <
                    int(storage['critical_threshold']) and not
                    floaty(previous) >=
                        int(storage['critical_threshold'])):
                    alert = \
                        SystemStorageUsageIncreasedAboveThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'WARNING',
                            meta_data['last_monitored'], 'WARNING',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                elif (float(current) >= int(storage['critical_threshold']) and
                      storage['critical_enabled'] and
                      storage['limiter'].can_do_task()):
                    alert = \
                        SystemStorageUsageIncreasedAboveThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'CRITICAL',
                            meta_data['last_monitored'], 'CRITICAL',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                    storage['limiter'].did_task()
                elif (float(current) < floaty(previous) and
                      floaty(previous) >= int(storage['warning_threshold']) and
                      float(current) < int(storage['warning_threshold']) and
                      storage['warning_enabled']):
                    alert = \
                        SystemStorageUsageDecreasedBelowThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'INFO',
                            meta_data['last_monitored'], 'WARNING',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                elif (float(current) < floaty(previous) and
                      floaty(previous) >= int(storage['critical_threshold'])
                      and float(current) < int(storage['critical_threshold'])
                      and storage['critical_enabled']):
                    alert = \
                        SystemStorageUsageDecreasedBelowThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'INFO',
                            meta_data['last_monitored'], 'CRITICAL',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()

        if cpu_use['enabled']:
            current = metrics['system_cpu_usage']['current']
            previous = metrics['system_cpu_usage']['previous']
            if current not in [previous, None]:
                if (int(cpu_use['warning_threshold']) <= float(current) <
                    int(cpu_use['critical_threshold']) and
                    cpu_use['warning_enabled'] and not
                    int(cpu_use['warning_threshold']) <= floaty(previous) <
                    int(cpu_use['critical_threshold']) and not
                    floaty(previous) >=
                        int(cpu_use['critical_threshold'])):
                    alert = \
                        SystemCPUUsageIncreasedAboveThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'WARNING',
                            meta_data['last_monitored'], 'WARNING',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                elif (float(current) >= int(cpu_use['critical_threshold']) and
                      cpu_use['critical_enabled'] and
                      cpu_use['limiter'].can_do_task()):
                    alert = \
                        SystemCPUUsageIncreasedAboveThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'CRITICAL',
                            meta_data['last_monitored'], 'CRITICAL',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                    cpu_use['limiter'].did_task()
                elif (float(current) < floaty(previous) and
                      floaty(previous) >= int(cpu_use['warning_threshold']) and
                      float(current) < int(cpu_use['warning_threshold']) and
                      cpu_use['warning_enabled']):
                    alert = \
                        SystemCPUUsageDecreasedBelowThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'INFO',
                            meta_data['last_monitored'], 'WARNING',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                elif (float(current) < floaty(previous) and
                      floaty(previous) >= int(cpu_use['critical_threshold'])
                      and float(current) < int(cpu_use['critical_threshold'])
                      and cpu_use['critical_enabled']):
                    alert = \
                        SystemCPUUsageDecreasedBelowThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'INFO',
                            meta_data['last_monitored'], 'CRITICAL',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()

        if ram_use['enabled']:
            current = metrics['system_ram_usage']['current']
            previous = metrics['system_ram_usage']['previous']
            if current not in [previous, None]:
                if (int(ram_use['warning_threshold']) <= float(current) <
                    int(ram_use['critical_threshold']) and
                    ram_use['warning_enabled'] and not
                    int(ram_use['warning_threshold']) <= floaty(previous) <
                    int(ram_use['critical_threshold']) and not
                    floaty(previous) >=
                        int(ram_use['critical_threshold'])):
                    alert = \
                        SystemRAMUsageIncreasedAboveThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'WARNING',
                            meta_data['last_monitored'], 'WARNING',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                elif (float(current) >= int(ram_use['critical_threshold']) and
                      ram_use['critical_enabled'] and
                      ram_use['limiter'].can_do_task()):
                    alert = \
                        SystemRAMUsageIncreasedAboveThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'CRITICAL',
                            meta_data['last_monitored'], 'CRITICAL',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                    ram_use['limiter'].did_task()
                elif (float(current) < floaty(previous) and
                      floaty(previous) >= int(ram_use['warning_threshold']) and
                      float(current) < int(ram_use['warning_threshold']) and
                      ram_use['warning_enabled']):
                    alert = \
                        SystemRAMUsageDecreasedBelowThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'INFO',
                            meta_data['last_monitored'], 'WARNING',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()
                elif (float(current) < floaty(previous) and
                      floaty(previous) >= int(ram_use['critical_threshold'])
                      and float(current) < int(ram_use['critical_threshold'])
                      and ram_use['critical_enabled']):
                    alert = \
                        SystemRAMUsageDecreasedBelowThresholdAlert(
                            meta_data['system_name'], floaty(previous),
                            float(current), 'INFO',
                            meta_data['last_monitored'], 'CRITICAL',
                            meta_data['system_parent_id'],
                            meta_data['system_id']
                        )
                    self._data_for_alerting = alert.alert_data
                    self.logger.debug('Successfully classified alert {}'
                                      ''.format(alert.alert_data))
                    self._place_latest_data_on_queue()

    def _place_latest_data_on_queue(self) -> None:
        self.logger.debug("Adding alert data to the publishing queue ...")

        # Place the latest alert data on the publishing queue. If the
        # queue is full, remove old data.
        if self.publishing_queue.full():
            self.publishing_queue.get()
        self.publishing_queue.put({
            'exchange': 'alert',
            'routing_key': 'alert_router.system',
            'data': copy.deepcopy(self.data_for_alerting)})

        self.logger.debug("Alert data added to the publishing queue "
                          "successfully.")

    def _alert_classifier_process(self) -> None:
        self._initialize_alerter()
        log_and_print('{} started.'.format(self), self.logger)
        while True:
            try:
                self.rabbitmq.start_consuming()
            except pika.exceptions.AMQPChannelError:
                # Error would have already been logged by RabbitMQ logger. If
                # there is a channel error, the RabbitMQ interface creates a
                # new channel, therefore perform another managing round without
                # sleeping
                continue
            except pika.exceptions.AMQPConnectionError as e:
                # Error would have already been logged by RabbitMQ logger.
                # Since we have to re-connect just break the loop.
                raise e
            except Exception as e:
                self.logger.exception(e)
                raise e

    def on_terminate(self, signum: int, stack: FrameType) -> None:
        log_and_print('{} is terminating. Connections with RabbitMQ will be '
                      'closed, and afterwards the process will exit.'
                      .format(self), self.logger)

        self.rabbitmq.queue_delete(self._queue_used)
        self.rabbitmq.disconnect_till_successful()
        log_and_print('{} terminated.'.format(self), self.logger)
        sys.exit()
