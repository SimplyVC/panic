import React from 'react';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button,
} from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import CheckIcon from '@material-ui/icons/Check';
import ClearIcon from '@material-ui/icons/Clear';
import CancelIcon from '@material-ui/icons/Cancel';
import { GLOBAL } from '../../../../constants/constants';

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
});

const SystemTable = (props) => {
  const classes = useStyles();

  const {
    config,
    systemConfig,
    removeSystemDetails,
  } = props;

  const currentConfig = config.byId[GLOBAL];

  if (currentConfig.systems.length === 0) {
    return <div />;
  }
  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell align="center">Name</TableCell>
            <TableCell align="center">Node Exporter Url</TableCell>
            <TableCell align="center">Monitor</TableCell>
            <TableCell align="center">Delete</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {currentConfig.systems.map((id) => (
            <TableRow key={id}>
              <TableCell align="center">
                {systemConfig.byId[id].name}
              </TableCell>
              <TableCell align="center">
                {systemConfig.byId[id].exporterUrl}
              </TableCell>
              <TableCell align="center">
                {systemConfig.byId[id].monitorSystem
                  ? <CheckIcon /> : <ClearIcon />}
              </TableCell>
              <TableCell align="center">
                <Button onClick={() => {
                  removeSystemDetails(systemConfig.byId[id]);
                }}
                >
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

SystemTable.propTypes = {
  config: PropTypes.shape({
    byId: PropTypes.shape({
      systems: PropTypes.arrayOf(PropTypes.string),
    }).isRequired,
  }).isRequired,
  systemConfig: PropTypes.shape({
    byId: PropTypes.shape({
      id: PropTypes.string,
      parentId: PropTypes.string,
      name: PropTypes.string,
      exporterUrl: PropTypes.string,
      monitorSystem: PropTypes.bool,
    }).isRequired,
    allIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
  removeSystemDetails: PropTypes.func.isRequired,
};

export default SystemTable;
