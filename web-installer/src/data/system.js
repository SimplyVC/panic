export default {
  title: 'Systems Setup',
  description:
    'Here we will setup the monitoring of systems which do not '
    + "belong to any chain. These systems wouldn't have any "
    + 'previously setup nodes running on them but you would still '
    + "want the system's metrics monitored. For example you can "
    + "monitor the system that is running PANIC! The System's metrics"
    + ' are monitored through Node Exporter, so that will need to be '
    + 'installed on each system you want to monitor. A suggestion is '
    + "to give your configuration a name that includes the system's "
    + 'IP address such as system_1_172.32.123.43 .',
  name: 'This will be used to identify the current System configuration.',
  name_holder: 'system_1_172.32.123.43',
  exporter_url_holder: 'http://176.67.65.56:9100',
  exporter_url: 'This is the node exporter url of your system.',
  monitor_system: 'Set to True if you want your system monitored.',
};
