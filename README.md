# PANIC Monitoring and Alerting for Blockchains!

**NOTE**: PANIC currently only alerts on System metrics and GitHub repository releases. Blockchain monitoring and alerting is coming soon!

<img src="docs/images/PANIC_BANNER.png" alt="PANIC Banner"/>

PANIC is an open source monitoring and alerting solution for Cosmos-SDK and Substrate based nodes by [SimplyVC](https://simply-vc.com.mt/). The tool was built with user friendliness in mind, and comes with numerous features such as phone calls for critical alerts, a Web-UI installation process and Telegram commands for increased control over your alerter.

The alerter's focus on a modular design means that it is beginner friendly but also developer friendly. It allows the user to decide which components of the alerter to set up while making it easy for developers to add new features. PANIC also offers more experienced users to fine-tune the alerter to their preference.

We are sure that PANIC will be beneficial for node operators and we look forward for feedback. Feel free to read on if you are interested in the design of the alerter, if you wish to try it out, or if you would like to support and contribute to this open source project.

## Design and Features

PANIC is designed to retrieve data directly from nodes as well as metrics of the underlying system through the use of Node Exporter. It also has a feature to alert on new GitHub repository releases of any repository you wish to be monitored. If you want to dive into the design and feature set of PANIC [click here](./docs/DESIGN_AND_FEATURES.md).

## Installation Guide

We will guide you through the steps required to get PANIC up and running. We recommend that PANIC is installed on a Linux system. This installation guide will use Docker and Docker Compose. It is highly suggested that everything needed in the [Requirements](#requirements) section is done before the installation procedure is started. It is recommended to have at least one alerting channel.

### Requirements

**Optional**: Node Exporter, this will be used to monitor the systems on which nodes the are running. It should be installed on each machine that you want to monitor. [Click here](#node-exporter-setup) if you want to set it up.
**Optional**: Telegram account and bots, for Telegram alerts and commands. [Click here](#telegram-setup) if you want to set it up.
**Optional**: Twilio account, for phone call alerts. [Click here](#twilio-setup) if you want to set it up.
**Optional**: PagerDuty account, for notifications and phone call alerts. [Click here](#pagerduty-setup) if you want to set it up.
**Optional**: OpsGenie account, for notifications and phone call alerts. [Click here](#opsgenie-setup) if you want to set it up.
**Required**: Git command line tools.
**Required**: This installation guide uses Docker and Docker Compose to run PANIC, these will need to be installed.

## Installation

**TIP**: If you're terminal is telling you that you do not have permissions to run a command try adding `sudo` to your command e.g `sudo docker --version` this will run your command as root.

### Git Installation

Firstly we will install and verify your Git installation.

```
# Install Git
sudo apt install git

# Verify your git installation
git --version
```

This should give you the current version of the software that has been installed.

### Docker and Docker Compose Installation

First, install Docker and Docker Compose by running these commands on your terminal.

```
# Install docker and docker-compose
curl -sSL https://get.docker.com/ | sh
sudo apt install docker-compose -y

# Confirm that installation successful
docker --version
docker-compose --version
```

These should give you the current versions of the softwares that have been installed.

### Configuration Setup

```
# Clone the panic repository and navigate into it
git clone https://github.com/SimplyVC/panic
cd panic
```

Now that you're in inside the PANIC directory, open up the .env file and change the fields of `INSTALLER_USERNAME` and `INSTALLER_PASSWORD` to your preferred but secure choice. This is to ensure that when configuring PANIC through the web-installer no one else can access it.

```
# This will access the .env file on your terminal
nano .env
```

Once inside change `admin` and `password` to different values. Here is an example:

```
INSTALLER_USERNAME=panic_operator
INSTALLER_PASSWORD=wowthisisasecurepassword
```

Then to exit hit the following keys:
```
# This will exit your .env file
CTRL + x
# This will select yes to save your modified file
Y
# Confirm file name and exit
ENTER
```

**Running PANIC**

Once you have everything setup, you can start PANIC by running the below command:

```
docker-compose up -d --build
```

Now you will have to configure PANIC to monitor your nodes and systems as well as give it the channels to alert you through. To do this, you will have to navigate to the running web-installer, this can be found on 
`https://{IP_ADDRESS}:8000`, if you're running it locally then it can be found here `https://localhost:8000`. There you will have to enter your `INSTALLER_USERNAME` and `INSTALLER_PASSWORD` which was previously changed.

After you've entered all the details the Web-Installer will save them as configuration files for PANIC to use. PANIC will automatically read the configuration files and begin monitoring the data sources.

Congratulations you should have PANIC up and running!

## Optional Installations

### Node Exporter Setup

##### Installing Node Exporter on the nodes is done as follows:

**Note**: This needs to be done on every host machine that you want the system metrics monitored and alerted on.

[Github](https://github.com/prometheus/node_exporter) link to most recent version of Node Exporter.

##### Create a Node Exporter user for running the exporter:

```
    sudo useradd --no-create-home --shell /bin/false node_exporter
```

##### Download and extract the latest version of Node Exporter:

```
wget https://github.com/prometheus/node_exporter/releases/download/v0.18.1/node_exporter-0.18.1.linux-amd64.tar.gz
tar -xzvf node_exporter-0.18.1.linux-amd64.tar.gz
```

##### Send the executable to /usr/local/bin:

```
sudo cp node_exporter-0.18.1.linux-amd64/node_exporter /usr/local/bin/
```

##### Give the Node Exporter user ownership of the executable:

```
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

##### Perform some cleanup and create and save a Node Exporter service with the below contents:

```
sudo rm node_exporter-0.18.1.linux-amd64 -rf
sudo nano /etc/systemd/system/node_exporter.service
```
```
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter
 
[Install]
WantedBy=multi-user.target
```

##### Reload systemctl services list, start the service and enable it to have it start on system restart:

```
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
sudo systemctl status node_exporter
```

Check if the installation was successful by checking if {NODE_IP}:{PORT}/metrics is accessible from a web browser.

[Back to the Requirements](#requirements)

### Telegram Setup

1. To create a free **Telegram account**, download the [app for Android / iPhone](https://telegram.org) and sign up using your phone number. 
2. To create a **Telegram bot**, add [@BotFather](https://telegram.me/BotFather) on Telegram, press Start, and follow the below steps:
    1. Send a `/newbot` command and fill in the requested details, including a bot name and username.
    2. Take a note of the API token, which looks something like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`.
    3. Access the link `t.me/<username>` to your new bot given by BotFather and press Start.
    4. Access the link `api.telegram.org/bot<token>/getUpdates`, replacing `<token>` with the bot's API token. This gives a list of the bot's activity, including messages sent to the bot.
    5. The result section should contain at least one message, due to us pressing the Start button. If not, sending a `/start` command to the bot should do the trick. Take a note of the `"id"` number in the `"chat"` section of this message.
    6. One bot is enough for now, but you can repeat these steps to create more bots.

**At the end, you should have:**
1. A Telegram account
2. A Telegram bot *(at least one)*
3. The Telegram bot's API token *(at least one)*
4. The chat ID of your chat with the bot *(at least one)*

[Back to the Requirements](#requirements)

### Twilio Setup

- To create a free trial **Twilio account**, head to the [try-twilio page](https://www.twilio.com/try-twilio) and sign up using your details.
- Next, three important pieces of information have to be obtained:
    1. Navigate to the [account dashboard page](https://www.twilio.com/console).
    2. Click the 'Get a Trial Number' button in the dashboard to generate a unique number.
    3. Take a note of the (i) Twilio phone number.
    4. Take a note of the (ii) account SID and (iii) auth token.
- All that remains now is to add a number that Twilio is able to call:
    1. Navigate to the [Verified Caller IDs page](https://www.twilio.com/console/phone-numbers/verified).
    2. Press the red **+** to add a new personal number and follow the verification steps.
    3. One number is enough for now, but you can repeat these steps to verify more than one number.

**At the end, you should have:**
1. A Twilio phone number.
2. The account SID, available in the account dashboard.
3. The auth token, available in the account dashboard.
4. A verified personal phone number *(at least one)*

If you wish to explore more advanced features, PANIC also supports configurable [TwiML](https://www.twilio.com/docs/voice/twiml); instructions which can re-program Twilio to do more than just call numbers. By default, the TwiML is set to [reject calls](https://www.twilio.com/docs/voice/twiml/reject) as soon as the recipient picks up, without any charges. This can be re-configured from the twilio section of the internal config to either a URL or raw TwiML instructions.

[Back to Requirements](#requirements)

### PagerDuty Setup

- To create a free trial **PagerDuty account**, head to the [PagerDuty sign-up page](https://www.pagerduty.com/sign-up/) and sign up using your details.
- Let's first go through the sign-up procedure
    1. Enter your details.
    2. Create a subdomain (You can call this anything you like.)
    3. Enter your service (You can say anything you like.)
    4. Click `Continue Without Adding Integrations`
    5. Enter your mobile and email details (Slack is Optional)
    6. Click Create your first incident to test your details.
      6.1 This will take you to a dashboard with your triggered incident.
      6.2 You can acknowledge or resolve this triggered incident.
- Next, two important pieces of information have to be obtained, firstly the integration key:
    1. Navigate to the `+ Add new services` button on the right side of the page
      1.1 Name your service and give it a description
      1.2 In the `Integration Settings` select `Use our API directly` and choose `Events API v2`,
      1.3 The rest can be configured to your preferences.
      1.4 Click `Add Service`
    2. You will be taken to a new page, where you need to navigate to the `Integrations` tab and take note of the (i)`Integration Key`.
- Secondly the API Token
    1. Navigate to `https:/{YOUR_SUBDOMAIN}.pagerduty.com/api_keys`.
    2. Click `Create New API Key`
    3. Give it a description (This can be anything you want)
    4. Click `Create Key` and take note of (ii)`API Key` value.

**At the end, you should have:**
1. The Integration Key
2. The API token

These will be used later in the Web-Installer to be saved in the configuration files.

**Note** You can also install an app for Android / iPhone as well as setup your phone number to receive alerts.

[Back to Requirements](#requirements)

### Opsgenie Setup

- To create a free trial **Opsgenie account**, head to the [Opsgenie sign-up page](https://www.atlassian.com/software/opsgenie/try) and sign up using your details.
- Let's go through the sign-up process and API setup.
    1. Enter your details and verify your account
    2. Click `Configure your profile` on the main page
      2.1 Enter and save your phone number
      2.2 Tick the `Voice` and `SMS` check boxes
      2.3 Click `Send test notification` to verify your phone number
      2.4 **Optional** install the Opsgenie mobile app
    3. Next click on `Set up your team` and enter the required details
    4. Next click on `Integrate with Jira and your monitoring tools`
      4.1 Make sure the `API` integration is selected
      4.2 Click `Save integrations`
      4.3 Click `Now, go to the integrations page and explore`
    5. Navigate to the API you just set up and take note of `API Key`.

**At the end, you should have:**
1. The API token

These will be used later in the Web-Installer to be saved in the configuration files.

**Note** You can also install the Opsgenie app for Android / iPhone as well as setup your phone number to receive calls.

[Back to Requirements](#requirements)

## Support and Contribution

On top of the additional work that we will put in ourselves to improve and maintain the tool, any support from the community through development will be greatly appreciated. 

## Who We Are

Simply VC runs highly reliable and secure infrastructure in our own datacentre in Malta, built with the aim of supporting the growth of the blockchain ecosystem. Read more about us on our website and Twitter:

- Simply VC website: <https://simply-vc.com.mt/>
- Simply VC Twitter: <https://twitter.com/Simply_VC>

---
