export default {
  channels: {
    title: 'Channel\'s Setup',
    subtitle_1: 'Everything you need to know about Channels.',
    subtitle_2: 'Setup the channels now.',
    what_title: 'What are Channels?',
    supported_title: 'Supported Channels',
    how_title: 'How are they setup?',
    what_1: 'Channels are used by PANIC to communicate with it\'s users.',
    what_2: 'Channels allow for different modes of communication such as '
          + 'directly calling your phone or sending messages on Telegram.',
    what_3: 'Channels such as Telegram allow for commands to interact with'
          + 'PANIC such as checking the state of PANIC.',
    channel_1: 'Telegram: a cross-platform cloud-based instant messaging, video'
             + ' calling, and VoIP service.',
    channel_2: 'Twilio: allows software developers to programmatically '
             + 'make and receive phone calls.',
    channel_3: 'PagerDuty: a SaaS incident response platform for IT '
             + 'departments.',
    channel_4: 'OpsGenie: an advanced incident response orchestration platform '
             + 'for DevOps and IT Teams.',
    channel_5: 'Email: this can either be a private email server or one '
             + 'provided by a company such as Google.',
    how_1: 'Channels can be setup in the section below, you can configure as '
         + 'many channels as you want.',
    how_2: 'Once a channel is created it can be assigned to any blockchain you '
         + 'want later on during the blockchain setup.',
    how_3: 'Channels can be assigned to multiple blockchains meaning multiple '
         + 'chains can send alerts to the same Telegram bot.',
    how_4: 'Each channel has an option to select different alert severity '
         + 'levels. These selections will indicate which alerts the channel is '
         + 'going to receive.'
  },
  alerts:{
    title: 'Types of Alerts',
    info: 'INFO: little to zero severity but consists of information which is '
        + 'still important to acknowledge.',
    warning: 'WARNING: a less severe alert but which still requires attention '
        + 'as it may be indicative of an incoming critical alert.',
    critical: 'CRITICAL: the most severe alert and the type of alert that '
        + 'should be dealt with as soon as possible.',
    error: 'ERROR: This is a severe alert which indicates that something is '
        + 'wrong with PANIC.',
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
