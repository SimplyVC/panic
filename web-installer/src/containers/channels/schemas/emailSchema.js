import * as Yup from 'yup';

const EmailSchema = (props) => Yup.object().shape({
  configName: Yup.string()
    .test(
      'unique-config-name',
      'Email config name is not unique.',
      (value) => {
        const { emails } = props;
        if (emails.allIds.length === 0) {
          return true;
        }
        for (let i = 0; i < emails.allIds.length; i += 1) {
          if (emails.byId[emails.allIds[i]].configName === value) {
            return false;
          }
        }
        return true;
      },
    )
    .required('Config name is required.'),
  smtp: Yup.string()
    .required('SMTP is required.'),
  emailFrom: Yup.string()
    .email('Email is not valid.')
    .required('Email From is required.'),
  emailsTo: Yup.array()
    .transform(function(value, originalValue) {
      if (this.isType(value) && value !== null) {
        return value;
      }
      return originalValue ? originalValue.split(/[\s,]+/) : [];
    }).of(Yup.string().email(({ value }) => `${value} is not a valid email `))
    .required('Email To is required.'),
});

export default EmailSchema;