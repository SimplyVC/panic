import React from 'react';
import { Grid, Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import Title from '../global/title';
import MainText from '../global/mainText';
import NavigationButtonContainer from '../../containers/global/navigationButtonContainer';
import FormAccordion from '../global/formAccordion';
import {
  WELCOME_PAGE, CHAINS_PAGE, NEXT, BACK, PERIODIC, SYSTEM, GITHUB,
} from '../../constants/constants';
import TimeLogo from '../../assets/icons/time.svg';
import SystemLogo from '../../assets/icons/system.svg';
import GithubLogo from '../../assets/icons/github.svg';
import Data from '../../data/general';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.primary,
  },
  icon: {
    paddingRight: '1rem',
  },
  heading: {
    fontSize: theme.typography.pxToRem(15),
    fontWeight: theme.typography.fontWeightRegular,
  },
}));

function GeneralsPage() {
  const classes = useStyles();

  return (
    <div>
      <Title
        text={Data.general.title}
      />
      <MainText
        text={Data.general.description}
      />
      <Box p={2} className={classes.root}>
        <Box
          p={3}
          border={1}
          borderRadius="borderRadius"
          borderColor="grey.300"
        >
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormAccordion
                icon={TimeLogo}
                name={PERIODIC}
                form={(<TelegramFormContainer />)}
              />
              <FormAccordion
                icon={SystemLogo}
                name={SYSTEM}
                form={(<TelegramFormContainer />)}
              />
              <TwilioTableContainer />
              <FormAccordion
                icon={GithubLogo}
                name={GITHUB}
                form={(<TelegramFormContainer />)}
              />
              <EmailTableContainer />
            </Grid>
          </Grid>
        </Box>
      </Box>
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

export default GeneralsPage;
