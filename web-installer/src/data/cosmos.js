import {
  CHAINS_PAGE, CHANNELS_STEP, NODES_STEP, REPOSITORIES_STEP, CHAINS_STEP,
  KMS_STEP, ALERTS_STEP,
} from '../constants/constants';

export default {
  cosmos: {
    title: 'Cosmos Chain Setup',
  },
  chainForm: {
    title: 'Chain Name Setup',
    description: 'We will now go through the setup process of a Cosmos based '
               + 'chain. Firstly you will enter the unique identifier of this '
               + 'chain. It should infer the types of nodes you will be '
               + 'monitoring. If you are going to be monitoring Cosmos nodes '
               + 'then the identifier should be Cosmos and you shouldn\'t '
               + 'add nodes which do not belong to the Cosmos blockchain. For '
               + 'example do not setup Oasis nodes under the Kava chain '
               + 'but setup a chain for Kava and a chain for Oasis and add  '
               + 'respective nodes underneath them.',
    placeholder: 'cosmos',
    tooltip: 'This will be used to identify the current chain that you are '
           + 'setting up.',
    backStep: CHAINS_PAGE,
    nextStep: NODES_STEP,
  },
  kmsForm: {
    title: 'KMS Setup',
    description: 'Here you will monitor you Key Management System(KMS), for now'
               + ' there is no direct Prometheus monitoring of the KMS system '
               + 'so for now you will monitor the System of the running'
               + 'KMS software through Node Exporter.',
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
    title: 'Nodes Setup',
    description: 'This is the node\'s setup step, here you will configure the '
               + 'nodes you want monitored and alerted on. For each node you '
               + 'will enter a unique identifier so as a user you will know '
               + 'which node is being alerted on. A suggestion would be to add '
               + 'the IP Address to the node name e.g '
               + 'cosmos_main_validator[172.32.431.32] so that you will know '
               + 'straight away where to look for the node. If you want the '
               + 'system which your node is running on to be monitored for '
               + 'system metrics such as RAM and CPU usage please install '
               + 'Node Exporter on it.',
    nameHolder: 'cosmos_node_1[172.32.431.32]',
    nameTip: 'This unique identifier will be used to identify your node.',
    tendermintHolder: 'http://122.321.32.12:26657',
    tendermintTip: 'This IP address will be used to monitor tendermint based '
      + 'statistics, if omitted they will not be monitored and alerted on.',
    sdkHolder: 'http://122.321.32.12:1317',
    sdkTip: 'This IP address will be used to monitor cosmos SDK based '
      + 'statistics, if omitted they will not be monitored and alerted on.',
    prometheusHolder: 'http://122.321.32.12:26660',
    prometheusTip: 'This IP address will be used to monitor prometheus based '
      + 'statistics, if omitted they will not be monitored and alerted on.',
    exporterUrlHolder: 'http://122,.321.32.12:9100',
    exporterUrlTip: 'This IP address will be used to monitor node exporter '
      + 'statistics, if omitted they will not be monitored and alerted on.',
    isValidatorTip: 'Set True if the node you are setting up is a validator.',
    isArchiveTip: 'Set True if the node you are setting up is an archive node.',
    monitorNodeTip: 'Set True if you want to monitor this configured node.',
    useAsDataSourceTip: 'Set True if you want to retrieve blockchain data from '
      + 'this node.',
    backStep: CHAINS_STEP,
    nextStep: REPOSITORIES_STEP,
  },
  repoForm: {
    title: 'Github Repositories Setup',
    description: 'You will now add a github repository that you want monitored '
               + 'and alerted on. You will receive informational alerts '
               + 'whenever there is a new release for the monitored repo. '
               + 'You must enter the path of the repository with a trailing '
               + 'forward slash, so if you want to monitor '
               + 'https://github.com/tendermint/tendermint/ you will need to '
               + 'enter tendermint/tendermint/ into the Field below.',
    nameHolder: 'tendermint/tendermint/',
    nameTip: 'This is the path of the repository that will be monitored. E.g: '
      + 'If the full URL is https://github.com/tendermint/tendermint/ then you '
      + 'have to enter tendermint/tendermint/.',
    monitorTip: 'Set True if you want to monitor this repository.',
    backStep: NODES_STEP,
    nextStep: KMS_STEP,
  },
  channelsTable: {
    title: 'Choose Channels',
    description: 'Choose to which channels you would like this chain to send '
               + 'alerts to. You can select as many configurations as you want '
               + 'from as many channels as you want.',
    empty: 'You haven\'t setup any channels! You will not be alerted on this '
         + 'chain!',
    backStep: REPOSITORIES_STEP,
    nextStep: ALERTS_STEP,
  }
};
