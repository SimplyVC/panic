import {
  CHANNELS_STEP,
  NODES_STEP,
  REPOSITORIES_STEP,
  ALERTS_STEP,
} from 'constants/constants';

export default {
  general: {
    title: 'General Settings',
  },
  periodic: {
    title: 'Periodic Alive Reminder',
    description:
      'The periodic alive reminder is used to notify you that PANIC '
      + "and all of it's components are fully operational. If enabled"
      + ' and configured you will receive INFO alerts every (n) '
      + 'seconds notifying you that PANIC is operational. If the '
      + 'interval is very small this will result in you getting '
      + 'spammed with alerts, a suggestion is to keep it at a couple '
      + 'of hours.',
  },
  repoForm: {
    title: 'Github Repositories Setup',
    description:
      'You will now add a github repository that you want monitored '
      + 'and alerted on. You will receive informational alerts '
      + 'whenever there is a new release for the monitored repo. '
      + 'You must enter the path of the repository with a trailing '
      + 'forward slash, so if you want to monitor '
      + 'https://github.com/SimplyVC/panic/ you will need to '
      + 'enter SimplyVC/panic/ into the Field below.',
    nameHolder: 'SimplyVC/panic/',
    nameTip:
      'This is the path of the repository that will be monitored. E.g: '
      + 'If the full URL is https://github.com/SimplyVC/panic/ then you '
      + 'have to enter SimplyVC/panic/.',
    monitorTip: 'Set True if you want to monitor this repository.',
    backStep: NODES_STEP,
    nextStep: CHANNELS_STEP,
  },
  channelsTable: {
    title: 'Choose Channels',
    description:
      'Choose the channels which should receive alerts related to general repositories '
      + 'and systems, and the periodic alive reminder You can select as many configurations '
      + 'as you want from as many channels as you want.',
    empty:
      "You haven't setup any channels! You will not be alerted on this "
      + 'chain!',
    backStep: REPOSITORIES_STEP,
    nextStep: ALERTS_STEP,
  },
};
