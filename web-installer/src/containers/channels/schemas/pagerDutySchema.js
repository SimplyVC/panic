import * as Yup from 'yup';

const PagerDutySchema = (props) => Yup.object().shape({
  channel_name: Yup.string()
    .test(
      'unique-config-name',
      'PagerDuty config name is not unique.',
      (value) => {
        const { pagerDuties } = props;
        if (pagerDuties.allIds.length === 0) {
          return true;
        }
        for (let i = 0; i < pagerDuties.allIds.length; i += 1) {
          if (pagerDuties.byId[pagerDuties.allIds[i]].channel_name === value) {
            return false;
          }
        }
        return true;
      },
    )
    .required('Config name is required.'),
  api_token: Yup.string()
    .required('API token is required.'),
  integration_key: Yup.string()
    .required('Integration key is required.'),
});

export default PagerDutySchema;
