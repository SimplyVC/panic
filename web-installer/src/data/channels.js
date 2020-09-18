export default {
  channels: {
    title: 'Channels Settings',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis eget nisi '
    + 'sed dolor ornare fermentum. Fusce massa augue, pulvinar ut consectetur a, auctor '
    + 'non lacus. Donec dui libero, luctus ut libero a, sodales molestie sapien. Sed ac '
    + 'orci molestie, dignissim sem egestas, vehicula urna. Cras odio nunc, viverra et '
    + 'iaculis ut, cursus vitae arcu. Sed eros massa, pretium a diam at, semper placerat '
    + 'tellus. Donec vestibulum tortor non tellus placerat tincidunt. Nullam imperdiet '
    + 'augue nulla, non imperdiet eros sodales nec. In hac habitasse platea dictumst. '
    + 'Vivamus vel rhoncus turpis. Proin in velit magna. Nullam volutpat venenatis '
    + 'placerat. Etiam ex eros, rhoncus nec diam vel, sollicitudin commodo dui. Sed '
    + 'suscipit quis neque vel blandit. Vivamus dui nisl, pellentesque porttitor vehicula '
    + 'sed, tempus sit amet orci. Vestibulum congue laoreet dui sed viverra.',
  },
  telegram: {
    description: 'Alerts sent via Telegram are a fast and reliable means of alerting '
    + 'that we highly recommend setting up. This requires you to have a '
    + 'Telegram bot set up, which is a free and quick procedure. Telegram is '
    + 'also used as a two-way interface with the alerter and '
    + 'as an assistant, allowing you to do things such as snooze phone '
    + 'call alerts and to get the alerter\'s current status from Telegram. ',
    name: 'This will be used to identify the saved telegram configuration.',
    token: 'This is the API token of your created bot.',
    chatID: 'This is the chat identifier of your newely created bot.',
    severties: 'Severties dictate which alerts will be sent to your chat.',
    commands: 'This will enable commands to be sent from telegram to PANIC.',
    alerts: 'This will enable alerts to be sent from PANIC to telegram.',
    botNamePlaceholder: 'telegra_chat_1',
    botTokenPlaceholder: '123456789:ABCDEF-1234abcd5678efgh12345_abc123',
    chatIdPlaceholder: '-1231213121',
  },
  twilio: {
    description: 'Twilio phone-call alerts are the most important alerts since they '
    + 'are the best at grabbing your attention, especially when you\'re '
    + 'asleep! To set these up, you have to have a Twilio account set up, '
    + 'with a registered Twilio phone number and a verified phone number.'
    + 'The timed trial version of Twilio is free.',
    name: 'This will be used to identify the saved twilio configuration.',
    account: 'This is the account SID which can be found on your twilio dashboard.',
    token: 'This is the authentication token which can be found on your twilio dashboard.',
    phoneNumber: 'This is your twilio phone number which will be alerting you.',
    dialNumbers: 'These are the numbers configured in twilio, which will be called on critical alerts.',
  },
  email: {
    description: 'Email alerts are more useful as a backup alerting channel rather '
    + 'than the main one, given that one is much more likely to notice a '
    + 'a message on Telegram or a phone call. Email alerts also require '
    + 'an SMTP server to be set up for the alerter to be able to send.',
    smtp: 'This is the SMTP server\'s address, which is used to send the emails.',
    name: 'This will be used to identify the saved email configuration.',
    from: 'This is the email address that will be sending you the alerts.',
    to: 'These are the email addresses which will be notified on set alerts.',
    username: 'The username used for SMTP authentication.',
    password: 'The password used for SMTP authentication.',
    severties: 'Severties dictate which alerts will be sent to your email.',
  },
  pagerDuty: {
    description: 'PagerDuty is an incident management platform that provides reliable '
    + 'notifications, automatic escalations, on-call scheduling, and other functionality '
    + 'to help teams detect and fix infrastructure problems quickly.',
    name: 'This will be used to identify the saved pagerduty configuration.',
    token: 'This is your API token that will be used to send alerts to PagerDuty.',
    severties: 'These dictate which alerts will be sent to PagerDuty.',
  },
  opsGenie: {
    name: 'Opsgenie is a modern incident management platform for operating '
    + 'always-on services, empowering Dev and Ops teams to plan for service '
    + 'disruptions and stay in control during incidents.',
    token: 'This is your API token that will be used to send alerts to OpsGenie.',
    severties: 'These dictate which alerts will be sent to OpsGenie.',
  },
};
