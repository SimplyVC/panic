import React from 'react';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import { makeStyles } from '@material-ui/core/styles';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
} from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import CheckIcon from '@material-ui/icons/Check';
import ClearIcon from '@material-ui/icons/Clear';
import CancelIcon from '@material-ui/icons/Cancel';

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
});

const TelegramTable = (props) => {
  const classes = useStyles();

  const {
    telegrams,
    removeTelegramDetails,
  } = props;

  if (telegrams.length === 0) {
    return <div />;
  }
  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell align="center">Token</TableCell>
            <TableCell align="center">Chat ID</TableCell>
            <TableCell align="center">Info</TableCell>
            <TableCell align="center">Warning</TableCell>
            <TableCell align="center">Critical</TableCell>
            <TableCell align="center">Error</TableCell>
            <TableCell align="center">Alerts</TableCell>
            <TableCell align="center">Commands</TableCell>
            <TableCell align="center">Delete</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {telegrams.map((telegram) => (
            <TableRow key={telegram.botName}>
              <TableCell component="th" scope="row">
                {telegram.botName}
              </TableCell>
              <TableCell align="center">{telegram.botToken}</TableCell>
              <TableCell align="center">{telegram.chatID}</TableCell>
              <TableCell align="center">
                {telegram.info ? <CheckIcon /> : <ClearIcon />}
              </TableCell>
              <TableCell align="center">
                {telegram.warning ? <CheckIcon /> : <ClearIcon />}
              </TableCell>
              <TableCell align="center">
                {telegram.critical ? <CheckIcon /> : <ClearIcon />}
              </TableCell>
              <TableCell align="center">
                {telegram.error ? <CheckIcon /> : <ClearIcon />}
              </TableCell>
              <TableCell align="center">
                {telegram.alerts ? <CheckIcon /> : <ClearIcon />}
              </TableCell>
              <TableCell align="center">
                {telegram.commands ? <CheckIcon /> : <ClearIcon />}
              </TableCell>
              <TableCell align="center">
                <Button onClick={() => { removeTelegramDetails(telegram); }}>
                  <CancelIcon />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

TelegramTable.propTypes = forbidExtraProps({
  telegrams: PropTypes.arrayOf(PropTypes.shape({
    botName: PropTypes.string.isRequired,
    botToken: PropTypes.string.isRequired,
    chatID: PropTypes.string.isRequired,
    info: PropTypes.bool.isRequired,
    warning: PropTypes.bool.isRequired,
    critical: PropTypes.bool.isRequired,
    error: PropTypes.bool.isRequired,
    alerts: PropTypes.bool.isRequired,
    commands: PropTypes.bool.isRequired,
  })).isRequired,
  removeTelegramDetails: PropTypes.func.isRequired,
});

export default TelegramTable;
