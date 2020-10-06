import {
  CHAINS_PAGE, CHANNELS_STEP, NODES_STEP, CHAINS_STEP, REPOSITORIES_STEP,
} from '../constants/constants';

export default {
  substrate: {
    title: 'Substrate Chain Setup',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis eget nisi sed dolor ornare fermentum. Fusce massa augue, pulvinar ut consectetur a, auctor non lacus. Donec dui libero, luctus ut libero a, sodales molestie sapien. Sed ac orci molestie, dignissim sem egestas, vehicula urna. Cras odio nunc, viverra et iaculis ut, cursus vitae arcu. Sed eros massa, pretium a diam at, semper placerat tellus. Donec vestibulum tortor non tellus placerat tincidunt. Nullam imperdiet augue nulla, non imperdiet eros sodales nec. In hac habitasse platea dictumst. Vivamus vel rhoncus turpis. Proin in velit magna. Nullam volutpat venenatis placerat. Etiam ex eros, rhoncus nec diam vel, sollicitudin commodo dui. Sed suscipit quis neque vel blandit. Vivamus dui nisl, pellentesque porttitor vehicula sed, tempus sit amet orci. Vestibulum congue laoreet dui sed viverra. ',
  },
  chainForm: {
    description: 'We will now go through the setup of substrate based chains.',
    placeholder: 'polkadot',
    tooltip: 'This will be used to identify the current chain that you are setting up.',
    backStep: CHAINS_PAGE,
    nextStep: NODES_STEP,
  },
  nodeForm: {
    description: 'Substrate node setup description goes here.',
    nameHolder: 'polkadot-node-1',
    nameTip: 'This unique identifier will be used to identify your node.',
    websocketHolder: 'ws://122.321.32.12:9944',
    websocketTip: 'This IP address will be used to monitor the polkadot node  '
      + 'statistics, if ommitted they will not be monitored and alerted on.',
    telemetryHolder: 'http://122.321.32.12:8000',
    telemetryTip: 'This IP address will be used to monitor telemetry based '
      + 'statistics, if ommitted they will not be monitored and alerted on.',
    prometheusHodler: 'http://122.321.32.12:26660',
    prometheusTip: 'This IP address will be used to monitor prometheus based '
      + 'statistics, if ommitted they will not be monitored and alerted on.',
    exporterUrlHolder: 'http://122,.321.32.12:9100',
    exporterUrlTip: 'This IP address will be used to monitor node exporter '
      + 'statistics, if ommitted they will not be monitored and alerted on.',
    stashAddressHolder: 'EDDJBTFGdsg0gh8sd0sdsda2asd12dasdafs',
    stashAddressTip: 'This will be used to monitor the stash address account.',
    isValidatorTip: 'Set True if the node you are setting up is a validator.',
    isArchiveTip: 'Set True if the node you are setting up is an archive node.',
    monitorNodeTip: 'Set True if you want to monitor this configured node.',
    useAsDataSourceTip: 'Set True if you want to retreive blockchain data from '
      + 'this node.',
    backStep: CHAINS_STEP,
    nextStep: REPOSITORIES_STEP,
  },
  repoForm: {
    description: 'Substrate based repositories description goes here.',
    nameHolder: 'paritytech/substrate',
    nameTip: 'This is the path of the repository that will be monitored. E.g: '
      + 'If the full URL is https://github.com/paritytech/substrate then you '
      + 'have to enter paritytech/substrate.',
    monitorTip: 'Set True if you want to monitor this repository.',
    backStep: NODES_STEP,
    nextStep: CHANNELS_STEP,
  },
};
