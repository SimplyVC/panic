import React from 'react';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import {
  TextField, Button, Box, Typography, FormControlLabel, Checkbox, Grid, Tooltip,
} from '@material-ui/core';
import Divider from '@material-ui/core/Divider';
import InfoIcon from '@material-ui/icons/Info';
import { MuiThemeProvider } from '@material-ui/core/styles';
import { SendTestOpsGenieButton } from '../../../utils/buttons';
import { defaultTheme, theme } from '../../theme/default';
import Data from '../../../data/channels';

const OpsGenieForm = ({errors, values, handleSubmit, handleChange}) => {
  return (
    <MuiThemeProvider theme={defaultTheme}>
      <div>
        <Typography variant="subtitle1" gutterBottom className="greyBackground">
          <Box m={2} p={3}>
            <p>{Data.opsGenie.description}</p>
          </Box>
        </Typography>
        <Divider />
        <form onSubmit={handleSubmit} className="root">
          <Box p={3}>
            <Grid container spacing={3} justify="center" alignItems="center">
              <Grid item xs={2}>
                <Typography> Configuration Name: </Typography>
              </Grid>
              <Grid item xs={9}>
                <TextField
                  error={errors.configName}
                  value={values.configName}
                  type="text"
                  name="configName"
                  placeholder="ops-genie-1"
                  helperText={errors.configName ? errors.configName : ''}
                  onChange={handleChange}
                  fullWidth
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.opsGenie.name} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <Typography> API Token: </Typography>
              </Grid>
              <Grid item xs={9}>
                <TextField
                  error={errors.apiToken}
                  value={values.apiToken}
                  type="text"
                  name="apiToken"
                  placeholder="0a9sjd09j1md00d10md19mda2a"
                  helperText={errors.apiToken ? errors.apiToken : ''}
                  onChange={handleChange}
                  fullWidth
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.opsGenie.token} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <Typography> EU: </Typography>
              </Grid>
              <Grid item xs={1}>
                <FormControlLabel
                  control={(
                    <Checkbox
                      checked={values.eu}
                      onChange={handleChange}
                      name="eu"
                      color="primary"
                    />
                  )}
                />
              </Grid>
              <Grid item xs={8} />
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.opsGenie.token} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <Typography> Severities: </Typography>
              </Grid>
              <Grid item xs={9}>
                <FormControlLabel
                  control={(
                    <Checkbox
                      checked={values.info}
                      onChange={handleChange}
                      name="info"
                      color="primary"
                    />
                  )}
                  label="Info"
                  labelPlacement="start"
                />
                <FormControlLabel
                  control={(
                    <Checkbox
                      checked={values.warning}
                      onChange={handleChange}
                      name="warning"
                      color="primary"
                    />
                  )}
                  label="Warning"
                  labelPlacement="start"
                />
                <FormControlLabel
                  control={(
                    <Checkbox
                      checked={values.critical}
                      onChange={handleChange}
                      name="critical"
                      color="primary"
                    />
                  )}
                  label="Critical"
                  labelPlacement="start"
                />
                <FormControlLabel
                  control={(
                    <Checkbox
                      checked={values.error}
                      onChange={handleChange}
                      name="error"
                      color="primary"
                    />
                  )}
                  label="Error"
                  labelPlacement="start"
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.opsGenie.severties} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={8} />
              <Grid item xs={4}>
                <Grid container direction="row" justify="flex-end" alignItems="center">
                  <Box px={2}>
                    <SendTestOpsGenieButton
                      disabled={(Object.keys(errors).length !== 0)}
                      apiKey={values.apiToken}
                      eu={values.eu}
                    />
                    <Button
                      variant="outlined"
                      size="large"
                      disabled={(Object.keys(errors).length !== 0)}
                      type="submit"
                    >
                      <Box px={2}>
                        Add
                      </Box>
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Grid>
          </Box>
        </form>
      </div>
    </MuiThemeProvider>
  );
};

OpsGenieForm.propTypes = forbidExtraProps({
  errors: PropTypes.shape({
    configName: PropTypes.string,
    apiToken: PropTypes.string,
  }).isRequired,
  handleSubmit: PropTypes.func.isRequired,
  values: PropTypes.shape({
    configName: PropTypes.string.isRequired,
    apiToken: PropTypes.string.isRequired,
    eu: PropTypes.bool.isRequired,
    info: PropTypes.bool.isRequired,
    warning: PropTypes.bool.isRequired,
    critical: PropTypes.bool.isRequired,
    error: PropTypes.bool.isRequired,
  }).isRequired,
  handleChange: PropTypes.func.isRequired,
});

export default OpsGenieForm;