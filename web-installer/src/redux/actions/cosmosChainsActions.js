import {
  ADD_CHAIN_COSMOS, ADD_NODE_COSMOS, ADD_REPOSITORY_COSMOS, REMOVE_NODE_COSMOS,
  REMOVE_REPOSITORY_COSMOS, ADD_KMS_COSMOS, REMOVE_KMS_COSMOS, SET_ALERTS_COSMOS,
  ADD_CONFIG_COSMOS, REMOVE_CONFIG_COSMOS, RESET_CONFIG_COSMOS,
  LOAD_CONFIG_COSMOS, ADD_TELEGRAM_CHANNEL_COSMOS,
  REMOVE_TELEGRAM_CHANNEL_COSMOS, ADD_TWILIO_CHANNEL_COSMOS,
  REMOVE_TWILIO_CHANNEL_COSMOS, ADD_EMAIL_CHANNEL_COSMOS,
  REMOVE_EMAIL_CHANNEL_COSMOS, ADD_PAGERDUTY_CHANNEL_COSMOS,
  REMOVE_PAGERDUTY_CHANNEL_COSMOS, ADD_OPSGENIE_CHANNEL_COSMOS,
  REMOVE_OPSGENIE_CHANNEL_COSMOS, UPDATE_WARNING_DELAY_COSMOS,
  UPDATE_WARNING_REPEAT_COSMOS, UPDATE_WARNING_THRESHOLD_COSMOS,
  UPDATE_WARNING_TIMEWINDOW_COSMOS, UPDATE_WARNING_ENABLED_COSMOS,
  UPDATE_CRITICAL_DELAY_COSMOS, UPDATE_CRITICAL_REPEAT_COSMOS,
  UPDATE_CRITICAL_THRESHOLD_COSMOS, UPDATE_CRITICAL_TIMEWINDOW_COSMOS,
  UPDATE_CRITICAL_ENABLED_COSMOS, UPDATE_ALERT_ENABLED_COSMOS,
  UPDATE_ALERT_SEVERTY_LEVEL_COSMOS, UPDATE_ALERT_SEVERTY_ENABLED_COSMOS,
  RESET_CHAIN_COSMOS, UPDATE_CHAIN_NAME, REMOVE_CHAIN_COSMOS,
} from './types';

const { v4: uuidv4 } = require('uuid');

// Only on the creation of a new chain, do you need to assign it
// a new identifer, from then on you re-used the old one.
export function addChainCosmos(payload) {
  return {
    type: ADD_CHAIN_COSMOS,
    payload: {
      id: uuidv4(),
      chainName: payload.chainName,
    },
  };
}

// This is used to delete the entire configuration of a setup cosmos chain
// To be invoked AFTER clearing the actual objects that are referenced in this
// object.
export function removeChainCosmos(payload) {
  return {
    type: REMOVE_CHAIN_COSMOS,
    payload,
  };
}

// @REMOVE Currently edited out, potentially not needed

// This function is used to keep track of which cosmos chain we are currently
// editing in the multi-step form.
// export function setCurrentCosmosChain(payload) {
//   return {
//     type: SET_CHAIN_COSMOS,
//     payload,
//   };
// }

// This function is used to change the name of the current chain
export function updateChainCosmos(payload) {
  return {
    type: UPDATE_CHAIN_NAME,
    payload,
  };
}

// This action is used to reset the current chain name to nothing
// most likely this will happen when click back after setting chain name
// or finishing a configuration setup of a chain
export function resetCurrentChainId() {
  return {
    type: RESET_CHAIN_COSMOS,
  };
}

export function addNodeCosmos(payload) {
  return {
    type: ADD_NODE_COSMOS,
    payload,
  };
}

export function removeNodeCosmos(payload) {
  return {
    type: REMOVE_NODE_COSMOS,
    payload,
  };
}

export function addRepositoryCosmos(payload) {
  return {
    type: ADD_REPOSITORY_COSMOS,
    payload,
  };
}

export function removeRepositoryCosmos(payload) {
  return {
    type: REMOVE_REPOSITORY_COSMOS,
    payload,
  };
}

export function addKMSCosmos(payload) {
  return {
    type: ADD_KMS_COSMOS,
    payload,
  };
}

export function removeKMSCosmos(payload) {
  return {
    type: REMOVE_KMS_COSMOS,
    payload,
  };
}

export function setAlertsCosmos(payload) {
  return {
    type: SET_ALERTS_COSMOS,
    payload,
  };
}

export function addConfigCosmos() {
  return {
    type: ADD_CONFIG_COSMOS,
  };
}

export function removeConfigCosmos(payload) {
  return {
    type: REMOVE_CONFIG_COSMOS,
    payload,
  };
}

export function resetConfigCosmos() {
  return {
    type: RESET_CONFIG_COSMOS,
  };
}

export function loadConfigCosmos(payload) {
  return {
    type: LOAD_CONFIG_COSMOS,
    payload,
  };
}

export function addTelegramChannelCosmos(payload) {
  return {
    type: ADD_TELEGRAM_CHANNEL_COSMOS,
    payload,
  };
}

export function removeTelegramChannelCosmos(payload) {
  return {
    type: REMOVE_TELEGRAM_CHANNEL_COSMOS,
    payload,
  };
}

export function addTwilioChannelCosmos(payload) {
  return {
    type: ADD_TWILIO_CHANNEL_COSMOS,
    payload,
  };
}

export function removeTwilioChannelCosmos(payload) {
  return {
    type: REMOVE_TWILIO_CHANNEL_COSMOS,
    payload,
  };
}

export function addEmailChannelCosmos(payload) {
  return {
    type: ADD_EMAIL_CHANNEL_COSMOS,
    payload,
  };
}

export function removeEmailChannelCosmos(payload) {
  return {
    type: REMOVE_EMAIL_CHANNEL_COSMOS,
    payload,
  };
}

export function addPagerDutyChannelCosmos(payload) {
  return {
    type: ADD_PAGERDUTY_CHANNEL_COSMOS,
    payload,
  };
}

export function removePagerDutyChannelCosmos(payload) {
  return {
    type: REMOVE_PAGERDUTY_CHANNEL_COSMOS,
    payload,
  };
}

export function addOpsGenieChannelCosmos(payload) {
  return {
    type: ADD_OPSGENIE_CHANNEL_COSMOS,
    payload,
  };
}

export function removeOpsGenieChannelCosmos(payload) {
  return {
    type: REMOVE_OPSGENIE_CHANNEL_COSMOS,
    payload,
  };
}

export function updateWarningDelayCosmos(payload) {
  return {
    type: UPDATE_WARNING_DELAY_COSMOS,
    payload,
  };
}

export function updateWarningRepeatCosmos(payload) {
  return {
    type: UPDATE_WARNING_REPEAT_COSMOS,
    payload,
  };
}

export function updateWarningThresholdCosmos(payload) {
  return {
    type: UPDATE_WARNING_THRESHOLD_COSMOS,
    payload,
  };
}

export function updateWarningTimeWindowCosmos(payload) {
  return {
    type: UPDATE_WARNING_TIMEWINDOW_COSMOS,
    payload,
  };
}

export function updateWarningEnabledCosmos(payload) {
  return {
    type: UPDATE_WARNING_ENABLED_COSMOS,
    payload,
  };
}

export function updateCriticalDelayCosmos(payload) {
  return {
    type: UPDATE_CRITICAL_DELAY_COSMOS,
    payload,
  };
}

export function updateCriticalRepeatCosmos(payload) {
  return {
    type: UPDATE_CRITICAL_REPEAT_COSMOS,
    payload,
  };
}

export function updateCriticalThresholdCosmos(payload) {
  return {
    type: UPDATE_CRITICAL_THRESHOLD_COSMOS,
    payload,
  };
}

export function updateCriticalTimeWindowCosmos(payload) {
  return {
    type: UPDATE_CRITICAL_TIMEWINDOW_COSMOS,
    payload,
  };
}

export function updateCriticalEnabledCosmos(payload) {
  return {
    type: UPDATE_CRITICAL_ENABLED_COSMOS,
    payload,
  };
}

export function updateAlertEnabledCosmos(payload) {
  return {
    type: UPDATE_ALERT_ENABLED_COSMOS,
    payload,
  };
}

export function updateAlertSeverityLevelCosmos(payload) {
  return {
    type: UPDATE_ALERT_SEVERTY_LEVEL_COSMOS,
    payload,
  };
}

export function updateAlertSeverityEnabledCosmos(payload) {
  return {
    type: UPDATE_ALERT_SEVERTY_ENABLED_COSMOS,
    payload,
  };
}
