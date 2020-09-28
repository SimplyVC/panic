import { connect } from 'react-redux';
import {
  updateRepeatAlert, updateTimeWindowAlert, updateThresholdAlert,
  updateSeverityAlert, resetCurrentChainId,
} from '../../../redux/actions/substrateChainsActions';
import { changePage, changeStep } from '../../../redux/actions/pageActions';
import AlertsTable from '../../../components/chains/substrate/tables/alertsTable';

const mapStateToProps = (state) => ({
  currentChain: state.CurrentSubstrateChain,
  chainConfig: state.SubstrateChainsReducer,
});

function mapDispatchToProps(dispatch) {
  return {
    stepChanger: (step) => dispatch(changeStep(step)),
    pageChanger: (page) => dispatch(changePage(page)),
    clearChainId: () => dispatch(resetCurrentChainId()),
    updateRepeatAlertDetails: (details) => dispatch(updateRepeatAlert(details)),
    updateTimeWindowAlertDetails: (details) => dispatch(updateTimeWindowAlert(details)),
    updateThresholdAlertDetails: (details) => dispatch(updateThresholdAlert(details)),
    updateSeverityAlertDetails: (details) => dispatch(updateSeverityAlert(details)),
  };
}

const AlertsTableContainer = connect(
  mapStateToProps,
  mapDispatchToProps,
)(AlertsTable);

export default AlertsTableContainer;
