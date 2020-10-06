import {
  CHAINS_PAGE, CHANNELS_STEP, NODES_STEP, REPOSITORIES_STEP, CHAINS_STEP,
} from '../constants/constants';

export default {
  cosmos: {
    title: 'Cosmos Chain Setup',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis eget nisi sed dolor ornare fermentum. Fusce massa augue, pulvinar ut consectetur a, auctor non lacus. Donec dui libero, luctus ut libero a, sodales molestie sapien. Sed ac orci molestie, dignissim sem egestas, vehicula urna. Cras odio nunc, viverra et iaculis ut, cursus vitae arcu. Sed eros massa, pretium a diam at, semper placerat tellus. Donec vestibulum tortor non tellus placerat tincidunt. Nullam imperdiet augue nulla, non imperdiet eros sodales nec. In hac habitasse platea dictumst. Vivamus vel rhoncus turpis. Proin in velit magna. Nullam volutpat venenatis placerat. Etiam ex eros, rhoncus nec diam vel, sollicitudin commodo dui. Sed suscipit quis neque vel blandit. Vivamus dui nisl, pellentesque porttitor vehicula sed, tempus sit amet orci. Vestibulum congue laoreet dui sed viverra. ',
  },
  chainForm: {
    description: 'We will now go through the setup of cosmos based chains.',
    placeholder: 'cosmos',
    tooltip: 'This will be used to identify the current chain that you are setting up.',
    backStep: CHAINS_PAGE,
    nextStep: NODES_STEP,
  },
  kmsForm: {
    description: 'Kms description needs to be provided here.',
    exporterUrlHolder: 'http://176.67.65.56:9100',
    nameHolder: 'Cosmos_KMS_Config_1',
    nameTip: 'This will be used to identify the current KMS configuration.',
    exporterUrlTip: 'This is your node exporter URL, if you visit the system '
      + 'running KMS at the {IP_Addrees}:9100/metrics you should be able to'
      + 'see a list of metrics in Prometheus format.',
    monitorKmsTip: 'Enable if you want this KMS configuration to be monitored.',
    backStep: REPOSITORIES_STEP,
    nextStep: CHANNELS_STEP,
  },
  nodeForm: {
    description: 'Cosmos node setup description goes here.',
    nameHolder: 'cosmos-node-1',
    nameTip: 'This unique identifier will be used to identify your node.',
    tendermintHolder: 'http://122.321.32.12:26657',
    tendermintTip: 'This IP address will be used to monitor tendermint based '
      + 'statistics, if ommitted they will not be monitored and alerted on.',
    sdkHolder: 'http://122.321.32.12:1317',
    sdkTip: 'This IP address will be used to monitor cosmos SDK based '
      + 'statistics, if ommitted they will not be monitored and alerted on.',
    prometheusHodler: 'http://122.321.32.12:26660',
    prometheusTip: 'This IP address will be used to monitor prometheus based '
      + 'statistics, if ommitted they will not be monitored and alerted on.',
    exporterUrlHolder: 'http://122,.321.32.12:9100',
    exporterUrlTip: 'This IP address will be used to monitor node exporter '
      + 'statistics, if ommitted they will not be monitored and alerted on.',
    isValidatorTip: 'Set True if the node you are setting up is a validator.',
    isArchiveTip: 'Set True if the node you are setting up is an archive node.',
    monitorNodeTip: 'Set True if you want to monitor this configured node.',
    useAsDataSourceTip: 'Set True if you want to retreive blockchain data from '
      + 'this node.',
    backStep: CHAINS_STEP,
    nextStep: REPOSITORIES_STEP,
  },
};
