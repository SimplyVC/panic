import {
  CHAINS_PAGE, CHANNELS_STEP, NODES_STEP, REPOSITORIES_STEP,
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
    exporterUrlPlaceHolder: 'http://176.67.65.56:9100',
    namePlaceHolder: 'Cosmos_KMS_Config_1',
    nameTip: 'This will be used to identify the current KMS configuration.',
    exporterUrlTip: 'This is your node exporter URL, if you visit the system '
      + 'running KMS at the {IP_Addrees}:9100/metrics you should be able to'
      + 'see a list of metrics in Prometheus format.',
    monitorKmsTip: 'Enable if you want this KMS configuration to be monitored.',
    backStep: REPOSITORIES_STEP,
    nextStep: CHANNELS_STEP,
  },
};
