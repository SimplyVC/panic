import React from 'react';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
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

/*
 * Contains the data of all the nodes of the current chain process. Has the
 * functionality to delete node data from redux.
 */
const NodesTable = ({
  chainConfig,
  substrateNodesConfig,
  currentChain,
  removeNodeDetails,
}) => {
  if (chainConfig.byId[currentChain].nodes.length === 0) {
    return <div />;
  }
  return (
    <TableContainer component={Paper}>
      <Table className="table" aria-label="substrate nodes table">
        <TableHead>
          <TableRow>
            <TableCell align="center">Name</TableCell>
            <TableCell align="center">Websocket</TableCell>
            <TableCell align="center">Telemetry</TableCell>
            <TableCell align="center">Prometheus</TableCell>
            <TableCell align="center">Node Exporter</TableCell>
            <TableCell align="center">Stash Address</TableCell>
            <TableCell align="center">Validator</TableCell>
            <TableCell align="center">Monitor</TableCell>
            <TableCell align="center">Archive</TableCell>
            <TableCell align="center">Data Source</TableCell>
            <TableCell align="center">Delete</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {chainConfig.byId[currentChain].nodes.map((id) => (
            <TableRow key={id}>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].name}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].node_ws_url}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].telemetry_url}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].prometheus_url}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].exporter_url}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].stash_address}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].is_validator ? (
                  <CheckIcon />
                ) : (
                  <ClearIcon />
                )}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].monitor_node ? (
                  <CheckIcon />
                ) : (
                  <ClearIcon />
                )}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].is_archive_node ? (
                  <CheckIcon />
                ) : (
                  <ClearIcon />
                )}
              </TableCell>
              <TableCell align="center">
                {substrateNodesConfig.byId[id].use_as_data_source ? (
                  <CheckIcon />
                ) : (
                  <ClearIcon />
                )}
              </TableCell>
              <TableCell align="center">
                <Button
                  onClick={() => {
                    removeNodeDetails(substrateNodesConfig.byId[id]);
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

NodesTable.propTypes = forbidExtraProps({
  chainConfig: PropTypes.shape({
    byId: PropTypes.shape({
      id: PropTypes.string,
      nodes: PropTypes.arrayOf(PropTypes.string),
    }).isRequired,
  }).isRequired,
  substrateNodesConfig: PropTypes.shape({
    byId: PropTypes.shape({
      id: PropTypes.string,
      parent_id: PropTypes.string,
      name: PropTypes.string.isRequired,
      node_ws_url: PropTypes.string,
      telemetry_url: PropTypes.string,
      prometheus_url: PropTypes.string,
      exporter_url: PropTypes.string,
      stash_address: PropTypes.string,
      is_validator: PropTypes.bool,
      monitor_node: PropTypes.bool,
      is_archive_node: PropTypes.bool,
      use_as_data_source: PropTypes.bool,
    }).isRequired,
    allIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
  removeNodeDetails: PropTypes.func.isRequired,
  currentChain: PropTypes.string.isRequired,
});

export default NodesTable;
