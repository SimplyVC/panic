export default {
  channels: {
    title: 'Channels Settings',
    what_title: 'What are Channels?',
    why_title: 'Why are they needed?',
    how_title: 'How are they setup?',
    what: 'Channels are various means of communication that PANIC will utilize '
        + 'to communicate with it\'s users. There are different types of '
        + 'channels that cater for users needs such as calling them directly '
        + 'during critical situations or even allowing a user to check the '
        + 'status of PANIC through Telegram Commands.',
    why: 'Channels are needed as they provide a reliable way of alerting users'
        + ' of any issues that may be occurring with their blockchains. '
        + 'Ensuring the uptime of blockchains is crucial for operators '
        + 'as well as their investors as potential downtime could lead to loss '
        + 'of funds and therefore loss of trust.',
    how: 'Channels can be setup in the section below, you can configure as many'
        + ' channels as you want. It is best to have multiple channels setup '
        + 'to ensure an operator is reachable. Alerts will be sent to the '
        + 'channels according to their specific blockchain and alert severity '
        + 'level.',
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
    botNamePlaceholder: 'telegram_chat_1',
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
    name: 'This will be used to identify the saved PagerDuty configuration.',
    token: 'This is your API token that will be used to send alerts to PagerDuty.',
    integrationKey: 'This key can be found on your PagerDuty dashboard.',
    severties: 'Severties dictate which alerts will be sent to PagerDuty.',
  },
  opsGenie: {
    description: 'Opsgenie is a modern incident management platform for operating '
    + 'always-on services, empowering Dev and Ops teams to plan for service '
    + 'disruptions and stay in control during incidents.',
    name: 'This will be used to identify the saved OpsGenie configuration.',
    token: 'This is your API token that will be used to send alerts to OpsGenie.',
    severties: 'Severties dictate which alerts will be sent to OpsGenie.',
  },
};
