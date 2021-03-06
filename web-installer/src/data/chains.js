export default {
  chains: {
    title: "Chain's Setup",
    subtitle_1: 'Everything you need to know about Chains.',
    subtitle_2: 'Setup the chains now!',
    what_title: 'What are Chains?',
    supported_title: 'Supported Chains',
    how_title: 'How are they setup?',
    what_1:
      'Chains are the type of blockchain nodes you have running that you '
      + 'want to be monitored and alerted on.',
    what_2:
      'The chains you will choose from are the underlying technology '
      + 'the blockchain is built with.',
    chain_1:
      'Cosmos-SDK: framework released by ICF for building '
      + 'application-specific blockchains.',
    chain_2:
      'Substrate: framework released by Web3 for building '
      + 'application-specific blockchains.',
    chain_3:
      'Other: Here you can monitor systems which do not belong to any '
      + 'blockchain, these are monitored through Node Exporter.',
    how_1:
      'Chains can be setup in the section below, you can configure as '
      + 'many chains as you want.',
    how_2:
      'First you will choose the type of blockchain you will be setting up'
      + ' is it built using the Cosmos-SDK or Substrate?',
    how_3:
      'From then on you will setup the chain name, the nodes belonging to '
      + 'the chain, the channels you want alerts for that chain to go to '
      + 'and finally the specific alerts configured for that chain.',
  },
  chain_name: {
    description: 'We will now go through the setup of cosmos based chains.',
    name:
      'This will be used to identify the current chain that you are '
      + 'setting up.',
  },
  kms: {
    description: '',
    name: 'This will be used to identify the current KMS configuration.',
    exporter_url: '',
    monitor_kms: '',
  },
  systems: {
    description: '',
    name: 'This will be used to identify the current System configuration.',
    exporter_url: '',
    monitor_system: '',
  },
  nodeDetails: {
    description: '',
    name: '',
    tendermintRPC: '',
    cosmosSDKRPC: '',
    prometheus_url: '',
    nodeExporterURL: '',
    is_validator: '',
    isArchive: '',
    monitor_node: '',
    use_as_data_source: '',
  },
  repositoryDetails: {
    description: '',
    name: '',
    monitor_repo: '',
  },
};
