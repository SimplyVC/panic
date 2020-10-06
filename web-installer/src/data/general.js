import {
  CHANNELS_STEP, NODES_STEP, REPOSITORIES_STEP, ALERTS_STEP,
} from '../constants/constants';

export default {
  general: {
    title: 'General Settings',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis eget nisi sed dolor ornare fermentum. Fusce massa augue, pulvinar ut consectetur a, auctor non lacus. Donec dui libero, luctus ut libero a, sodales molestie sapien. Sed ac orci molestie, dignissim sem egestas, vehicula urna. Cras odio nunc, viverra et iaculis ut, cursus vitae arcu. Sed eros massa, pretium a diam at, semper placerat tellus. Donec vestibulum tortor non tellus placerat tincidunt. Nullam imperdiet augue nulla, non imperdiet eros sodales nec. In hac habitasse platea dictumst. Vivamus vel rhoncus turpis. Proin in velit magna. Nullam volutpat venenatis placerat. Etiam ex eros, rhoncus nec diam vel, sollicitudin commodo dui. Sed suscipit quis neque vel blandit. Vivamus dui nisl, pellentesque porttitor vehicula sed, tempus sit amet orci. Vestibulum congue laoreet dui sed viverra. ',
  },
  repoForm: {
    description: 'General repositories description goes here.',
    nameHolder: 'SimplyVC/panic',
    nameTip: 'This is the path of the repository that will be monitored. E.g: '
      + 'If the full URL is https://github.com/simplyVC/panic then you '
      + 'have to enter simplyVC/panic.',
    monitorTip: 'Set True if you want to monitor this repository.',
    backStep: NODES_STEP,
    nextStep: CHANNELS_STEP,
  },
  channelsTable: {
    backStep: REPOSITORIES_STEP,
    nextStep: ALERTS_STEP,
  },
};
