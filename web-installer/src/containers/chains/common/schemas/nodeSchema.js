import * as Yup from 'yup';
import { BLACKLIST } from 'constants/constants';

const NodeSchema = (props) => Yup.object().shape({
  name: Yup.string()
    .test('unique-node-name', 'Node name is not unique.', (value) => {
      const {
        cosmosNodesConfig, substrateNodesConfig, systemConfig, reposConfig,
      } = props;

      for (let i = 0; i < cosmosNodesConfig.allIds.length; i += 1) {
        if (cosmosNodesConfig.byId[cosmosNodesConfig.allIds[i]].name === value) {
          return false;
        }
      }
      for (let i = 0; i < substrateNodesConfig.allIds.length; i += 1) {
        if (substrateNodesConfig.byId[substrateNodesConfig.allIds[i]].name === value) {
          return false;
        }
      }
      for (let i = 0; i < systemConfig.allIds.length; i += 1) {
        if (systemConfig.byId[systemConfig.allIds[i]].name === value) {
          return false;
        }
      }
      for (let i = 0; i < reposConfig.allIds.length; i += 1) {
        if (reposConfig.byId[reposConfig.allIds[i]].repo_name === value) {
          return false;
        }
      }
      return true;
    })
    .required('Node name is required.'),
  exporter_url: Yup.string()
    .test('localhost', '127.0.0.1 is not allowed for security reasons.',
      (value) => {
        if (BLACKLIST.find((a) => value.includes(a))) {
          return false;
        }
        return true;
      }),
});

export default NodeSchema;
