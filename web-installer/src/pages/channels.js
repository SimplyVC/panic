import React from 'react';

import Title from '../components/global/title';
import MainText from '../components/global/mainText';
import NavigationButtonContainer from '../containers/global/navigationButtonContainer';
import ChannelsGrid from '../components/channels/channelsGrid';
import {
  WELCOME_PAGE, CHAINS_PAGE, NEXT, BACK,
} from '../constants/constants';
import Data from '../data/channels';

function Channels() {
  return (
    <div>
      <Title
        text={Data.channels.title}
      />
      <MainText
        text={Data.channels.description}
      />
      <ChannelsGrid />
      <NavigationButtonContainer
        text={NEXT}
        navigation={CHAINS_PAGE}
      />
      <NavigationButtonContainer
        text={BACK}
        navigation={WELCOME_PAGE}
      />
    </div>
  );
}

export default Channels;
