import React from 'react';

import Title from '../components/global/title';
import MainText from '../components/global/mainText';
import NavigationButtonContainer from '../containers/global/navigationButtonContainer';
import Data from '../data/channels';
import { WELCOME_PAGE, CHAINS_PAGE } from "../constants/pages";

function Channels() {
    return (
        <div>
            <Title
                text={Data.channels.title}
            />
            <MainText
                text={Data.channels.description}
            />
            <NavigationButtonContainer
                text={'Next'}
                navigation={CHAINS_PAGE}
            />
            <NavigationButtonContainer 
                text={'Manage'}
                navigation={WELCOME_PAGE}
            />
            <NavigationButtonContainer 
                text={'Back'}
                navigation={WELCOME_PAGE}
            />
        </div>
    )
}

export default Channels;