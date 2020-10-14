import React from 'react';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import {
  TextField, Button, Box, Typography, FormControlLabel, Checkbox, Grid, Tooltip,
} from '@material-ui/core';
import Divider from '@material-ui/core/Divider';
import InfoIcon from '@material-ui/icons/Info';
import { MuiThemeProvider } from '@material-ui/core/styles';
import { Autocomplete } from '@material-ui/lab';
import { SendTestEmailButton } from '../../../utils/buttons';
import { defaultTheme, theme } from '../../theme/default';
import Data from '../../../data/channels';

const EmailForm = ({errors, values, handleSubmit, handleChange, setFieldValue
  }) => {

  const updateToEmails = (event, emailsTo) => {
    setFieldValue('emailsTo', emailsTo);
  };

  return (
    <MuiThemeProvider theme={defaultTheme}>
      <div>
        <Typography variant="subtitle1" gutterBottom className="greyBackground">
          <Box m={2} p={3}>
            <p>{Data.email.description}</p>
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
                  placeholder="main_email_channel"
                  helperText={errors.configName ? errors.configName : ''}
                  onChange={handleChange}
                  fullWidth
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.email.name} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <Typography> SMTP: </Typography>
              </Grid>
              <Grid item xs={9}>
                <TextField
                  error={errors.smtp}
                  value={values.smtp}
                  type="text"
                  name="smtp"
                  placeholder="my.smtp.com"
                  helperText={errors.smtp ? errors.smtp : ''}
                  onChange={handleChange}
                  fullWidth
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.email.smtp} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <Typography> Email From: </Typography>
              </Grid>
              <Grid item xs={9}>
                <TextField
                  error={errors.emailFrom}
                  value={values.emailFrom}
                  type="text"
                  name="emailFrom"
                  placeholder="alerter@email.com"
                  helperText={errors.emailFrom ? errors.emailFrom : ''}
                  onChange={handleChange}
                  fullWidth
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.email.from} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <Typography> Emails To: </Typography>
              </Grid>
              <Grid item xs={9}>
                <Autocomplete
                  multiple
                  freeSolo
                  options={[]}
                  onChange={updateToEmails}
                  value={values.emailsTo}
                  renderInput={(params) => (
                    <TextField
                      // eslint-disable-next-line react/jsx-props-no-spreading
                      {...params}
                      error={errors.emailsTo}
                      type="text"
                      name="emailsTo"
                      placeholder="Add a destination email."
                      variant="standard"
                      helperText={errors.emailsTo ? errors.emailsTo : ''}
                      fullWidth
                    />
                  )}
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.email.to} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <Typography> Username: </Typography>
              </Grid>
              <Grid item xs={9}>
                <TextField
                  value={values.username}
                  type="text"
                  name="username"
                  placeholder="my_username"
                  onChange={handleChange}
                  fullWidth
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.email.username} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <Typography> Password: </Typography>
              </Grid>
              <Grid item xs={9}>
                <TextField
                  value={values.password}
                  type="password"
                  name="password"
                  placeholder="*****************"
                  onChange={handleChange}
                  fullWidth
                />
              </Grid>
              <Grid item xs={1}>
                <Grid container justify="center">
                  <MuiThemeProvider theme={theme}>
                    <Tooltip title={Data.email.password} placement="left">
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
                    <Tooltip title={Data.email.severties} placement="left">
                      <InfoIcon />
                    </Tooltip>
                  </MuiThemeProvider>
                </Grid>
              </Grid>
              <Grid item xs={8} />
              <Grid item xs={4}>
                <Grid container direction="row" justify="flex-end" alignItems="center">
                  <Box px={2}>
                    <SendTestEmailButton
                      disabled={(Object.keys(errors).length !== 0)}
                      to={values.emailsTo}
                      from={values.emailFrom}
                      smtp={values.smtp}
                      user={values.username}
                      pass={values.password}
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

EmailForm.propTypes = forbidExtraProps({
  errors: PropTypes.shape({
    configName: PropTypes.string,
    smtp: PropTypes.string,
    emailFrom: PropTypes.string,
    emailsTo: PropTypes.string,
  }).isRequired,
  handleSubmit: PropTypes.func.isRequired,
  values: PropTypes.shape({
    configName: PropTypes.string.isRequired,
    smtp: PropTypes.string.isRequired,
    emailFrom: PropTypes.string.isRequired,
    emailsTo: PropTypes.arrayOf(
      PropTypes.string.isRequired,
    ).isRequired,
    username: PropTypes.string.isRequired,
    password: PropTypes.string.isRequired,
    info: PropTypes.bool.isRequired,
    warning: PropTypes.bool.isRequired,
    critical: PropTypes.bool.isRequired,
    error: PropTypes.bool.isRequired,
  }).isRequired,
  handleChange: PropTypes.func.isRequired,
  setFieldValue: PropTypes.func.isRequired,
});

export default EmailForm;