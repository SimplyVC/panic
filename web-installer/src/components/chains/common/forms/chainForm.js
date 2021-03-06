import React from 'react';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import { MuiThemeProvider } from '@material-ui/core/styles';
import {
  TextField, Typography, Box, Grid, Tooltip, Divider,
} from '@material-ui/core';
import InfoIcon from '@material-ui/icons/Info';
import { NEXT, BACK } from 'constants/constants';
import NavigationButton from 'components/global/navigationButton';
import { defaultTheme, theme } from 'components/theme/default';
import useStyles from 'assets/jss/material-kit-react/views/landingPageSections/productStyle';
import GridContainer from 'components/material_ui/Grid/GridContainer';
import GridItem from 'components/material_ui/Grid/GridItem';

/*
 * This form allows for the input of a chain name.
 */
const ChainNameForm = ({
  errors,
  handleChange,
  values,
  data,
  stepChanger,
  saveChainDetails,
  currentChain,
  updateChainDetails,
  pageChanger,
  clearChainId,
}) => {
  const classes = useStyles();
  // NextStep function will save the chain name, step changer
  function nextStep(step) {
    // If there is a current chain assigned already, overwrite the value
    // Otherwise add a new chain name.
    if (currentChain) {
      const payload = {
        id: currentChain,
        chain_name: values.chain_name,
      };
      updateChainDetails(payload);
    } else {
      const payload = {
        chain_name: values.chain_name,
      };
      saveChainDetails(payload);
    }
    stepChanger({ step });
  }

  // Next page is in fact returning back to the Chains settings page
  // but keeping the name the same for consistency
  function nextPage(page) {
    // Clear the current chain, id we are working on.
    clearChainId();
    // Change page
    pageChanger({ page });
  }

  return (
    <MuiThemeProvider theme={defaultTheme}>
      <div>
        <div className={classes.subsection}>
          <GridContainer justify="center">
            <GridItem xs={12} sm={12} md={8}>
              <h1 className={classes.title}>{data.chainForm.title}</h1>
            </GridItem>
          </GridContainer>
        </div>
        <Typography variant="subtitle1" gutterBottom className="greyBackground">
          <Box m={2} p={3}>
            <p>{data.chainForm.description}</p>
          </Box>
        </Typography>
        <Divider />
        <Box py={4}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
            }}
            className="root"
          >
            <Grid container spacing={3} justify="center" alignItems="center">
              <Grid item xs={2}>
                <Typography> Chain Name </Typography>
              </Grid>
              <Grid item xs={9}>
                <TextField
                  error={errors.chain_name}
                  value={values.chain_name}
                  type="text"
                  name="chain_name"
                  placeholder={data.chainForm.placeholder}
                  helperText={errors.chain_name ? errors.chain_name : ''}
                  onChange={handleChange}
                  inputProps={{ min: 0, style: { textAlign: 'right' } }}
                  autoComplete="off"
                  fullWidth
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={data.chainForm.tooltip} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={12} />
              <br />
              <br />
              <Grid item xs={4} />
              <Grid item xs={2}>
                <Box px={2}>
                  <NavigationButton
                    disabled={false}
                    nextPage={nextPage}
                    buttonText={BACK}
                    navigation={data.chainForm.backStep}
                  />
                </Box>
              </Grid>
              <Grid item xs={2}>
                <Box px={2}>
                  <NavigationButton
                    disabled={Object.keys(errors).length !== 0 || values.chain_name.length === 0}
                    nextPage={nextStep}
                    buttonText={NEXT}
                    navigation={data.chainForm.nextStep}
                  />
                </Box>
              </Grid>
              <Grid item xs={4} />
              <Grid item xs={12} />
            </Grid>
          </form>
        </Box>
      </div>
    </MuiThemeProvider>
  );
};

ChainNameForm.propTypes = forbidExtraProps({
  errors: PropTypes.shape({
    chain_name: PropTypes.string,
  }).isRequired,
  values: PropTypes.shape({
    chain_name: PropTypes.string.isRequired,
  }).isRequired,
  currentChain: PropTypes.string.isRequired,
  saveChainDetails: PropTypes.func.isRequired,
  stepChanger: PropTypes.func.isRequired,
  updateChainDetails: PropTypes.func.isRequired,
  handleChange: PropTypes.func.isRequired,
  pageChanger: PropTypes.func.isRequired,
  clearChainId: PropTypes.func.isRequired,
  data: PropTypes.shape({
    chainForm: PropTypes.shape({
      title: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      placeholder: PropTypes.string.isRequired,
      tooltip: PropTypes.string.isRequired,
      backStep: PropTypes.string.isRequired,
      nextStep: PropTypes.string.isRequired,
    }).isRequired,
  }).isRequired,
});

export default ChainNameForm;
