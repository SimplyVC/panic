import React from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { AlertsCosmosTableContainer } from 'containers/chains/common/alertsContainer';
import { CosmosChainFormContainer } from 'containers/chains/common/chainContainer';
import { ChannelsCosmosTableContainer } from 'containers/chains/common/channelsContainer';
import {
  KmsCosmosFormContainer,
  KmsCosmosTableContainer,
} from 'containers/chains/common/kmsContainer';
import {
  RepositoriesCosmosFormContainer,
  RepositoriesCosmosTableContainer,
} from 'containers/chains/common/repositoriesContainer';
import {
  ALERTS_STEP,
  CHAINS_STEP,
  CHANNELS_STEP,
  KMS_STEP,
  NODES_STEP,
  REPOSITORIES_STEP,
} from 'constants/constants';
import { NodesFormContainer, NodesTableContainer } from './nodesContainer';

const mapStateToProps = (state) => ({
  step: state.ChangeStepReducer.step,
});

// Returns the specific page according to pre-set steps
function getStep(stepName) {
  switch (stepName) {
    case ALERTS_STEP:
      return <AlertsCosmosTableContainer />;
    case CHAINS_STEP:
      return <CosmosChainFormContainer />;
    case CHANNELS_STEP:
      return <ChannelsCosmosTableContainer />;
    case KMS_STEP:
      return (
        <div>
          <KmsCosmosFormContainer />
          <KmsCosmosTableContainer />
        </div>
      );
    case NODES_STEP:
      return (
        <div>
          <NodesFormContainer />
          <NodesTableContainer />
        </div>
      );
    case REPOSITORIES_STEP:
      return (
        <div>
          <RepositoriesCosmosFormContainer />
          <RepositoriesCosmosTableContainer />
        </div>
      );
    default:
      return <CosmosChainFormContainer />;
  }
}

// Step Selector changes according to the step set
function StepManager(props) {
  const { step } = props;
  return <div>{getStep(step)}</div>;
}

StepManager.propTypes = {
  step: PropTypes.string.isRequired,
};

export default connect(mapStateToProps)(StepManager);
