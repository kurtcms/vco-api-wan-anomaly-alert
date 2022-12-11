# VMware VeloCloud SD-WAN Orchestrator API: Detect and Alert of WAN Anomaly

This Python app is containerised with [Docker Compose](https://docs.docker.com/compose/) for a modular and cloud native deployment that fits in any microservice architecture.

It does the following:

1. Call the [VMware VeloCloud Orchestrator (VCO) API](#reference) to retrieve the WAN quality metrics i.e. upload and download latency, jitter and packet loss, between the SD-WAN Edge and its associated SD-WAN Gateway, for all of the Edges in the enterprise network;
2. Detect WAN anomaly by comparing the WAN quality metrics of the last 5 minutes, to those of the 60 minutes before, with a sampling interval of 5 minutes; and
3. Send an email alert should the averages of the WAN quality metrics of the last 5 minutes be more than two standard deviations higher than the averages of the 60-minute historical baseline.

For details on the WAN path monitoring mechanism and sampling interval, please refer to the [VMware SD-WAN Dynamic Multipath Optimisation (DMPO)](#reference) article on the VMware SD-WAN Knowledge Base.

A detailed walk-through is available [here](https://kurtcms.org/vmware-velocloud-sd-wan-orchestrator-api-detect-and-alert-of-wan-anomaly/).

## Table of Content

- [Getting Started](#getting-started)
  - [Git Clone](#git-clone)
  - [Environment Variable](#environment-variables)
  - [Sampling Durations and Interval](#sampling-durations-and-interval)
  - [Crontab](#crontab)
  - [Docker Container](#docker-container)
	  - [Docker Compose](#docker-compose)
	  - [Build and Run](#build-and-run)
  - [Standalone Python Script](#standalone-python-script)
    - [Dependencies](#dependencies)
    - [Cron](#cron)
- [Email Alert](#email-alert)
- [Reference](#reference)

## Getting Started

Get started in three simple steps:

1. [Download](#git-clone) a copy of the app;
2. Create the [environment variables](#environment-variables) for the VCO authentication and for email notification, and modify the [sampling durations and interval](#sampling-durations-and-interval) and the [crontab](#crontab) if needed;
3. [Docker Compose](#docker-compose) or [build and run](#build-and-run) the image manually to start the app, or alternatively run the Python script as a standalone service.

### Git Clone

Download a copy of the app with `git clone`
```shell
$ git clone https://github.com/kurtcms/vco-api-wan-anomaly-alert /app/
```

### Environment Variables

The app expects the hostname, the API token or the username and password for the VCO; as well as the SMTPS port number, SMTP server address, the alert receiver email address, the alert sender email address and password; as environment variables in a `.env` file in the same directory.

Should both the API token, and the username and password, for the VCO be present, the app will always use the API token.

Be sure to create the `.env` file.

```shell
$ nano /app/vco-api-wan-anomaly-alert/.env
```

And define the variables accordingly.

```
VCO_HOSTNAME = 'vco.managed-sdwan.com/'

# Either the API token
VCO_TOKEN = '(redacted)'

# Or the username and password
VCO_USERNAME = 'kurtcms@gmail.com'
VCO_PASSWORD = '(redacted)'

# For email notification
EMAIL_SSL_PORT = 465
EMAIL_SMTP_SERVER = 'smtp.kurtcms.org'
EMAIL_SENDER = 'alert@kurtcms.org'
EMAIL_RECEIVER = 'kurtcms@gmail.com'
EMAIL_SENDER_PASSWORD = '(redacted)'
```

### Sampling Durations and Interval

The intervals for the WAN quality metrics are 300 seconds i.e. 5 minutes and 3,600 seconds i.e. 60 minutes, for the present and historical baseline respectively, with a sampling interval of 300 seconds i.e. 5 minutes. All of these are passed to the respective function as argument at runtime and may be adjusted if needed.

```shell
$ nano /app/vco_api_wan_anomaly_alert.py
```
Modify the values as appropriate.

```python
conn.detect_wan_anomaly(5, 300, 3600)
'''
min_per_sample of 5 i.e. one sample every 5 minutes
interval_sec_present of 300 i.e. 5 minutes
interval_sec_hist of 3600 i.e. 60 minutes
'''
```

### Crontab

By default the app is scheduled with [cron](https://linux.die.net/man/8/cron) to retrieve the WAN quality metrics every 5 minutes, with `stdout` and `stderr` redirected to the main process for `Docker logs`.  

Modify the `crontab` if a different schedule is required.

```shell
$ nano /app/vco-api-wan-anomaly-alert/crontab
```

### Docker Container

Packaged as a container, the app is a standalone, executable package that may be run on Docker Engine. Be sure to have [Docker](https://docs.docker.com/engine/install/) installed.

#### Docker Compose

With Docker Compose, the app may be provisioned with a single command. Be sure to have [Docker Compose](https://docs.docker.com/compose/install/) installed.

```shell
$ docker-compose up -d
```

Stopping the container is as simple as a single command.

```shell
$ docker-compose down
```

#### Build and Run

Otherwise the Docker image can also be built manually.

```shell
$ docker build -t vco_api_wan_anomaly_alert /app/vco-api-wan-anomaly-alert/
```

Run the image with Docker once it is ready.  

```shell
$ docker run -it --rm --name vco_api_wan_anomaly_alert vco_api_wan_anomaly_alert
```

### Standalone Python Script

Alternatively the `vco_api_wan_anomaly_alert.py` script may be deployed as a standalone service.

#### Dependencies

In which case be sure to install the following required libraries for the `vco_api_main.py`:

1. [Requests](https://github.com/psf/requests)
2. [Python-dotenv](https://github.com/theskumar/python-dotenv)
3. [NumPy](https://github.com/numpy/numpy)
4. [pandas](https://github.com/pandas-dev/pandas)

```shell
$ pip3 install requests python-dotenv numpy pandas
```

#### Cron

The script may then be executed with a task scheduler such as [cron](https://linux.die.net/man/8/cron) that runs it once every 5 minutes for example.

```shell
$ (crontab -l; echo "*/5 * * * * /usr/bin/python3 /app/vco-api-wan-anomaly-alert/vco_api_wan_anomaly_alert.py") | crontab -
```

## Email Alert

Email alert will be sent from `EMAIL_SENDER` to `EMAIL_RECEIVER` should an anomaly be found. The subject of the email will be `WAN Anomaly Alert` with the details of the anomaly in the email body.

```
Latency (download, ms) of WAN BT Business Broadband between Edge LDN-vVCE and its associated Gateway is found to be 100.0 and is 2 standard deviation(s) away from the mean of 75.0 and standard deviation of 10.0 of the 60.0 minute(s) before.
Jitter (download, ms) of WAN BT Business Broadband between Edge LDN-vVCE and its associated Gateway is found to be 5.0 and is 2 standard deviation(s) away from the mean of 2.0 and standard deviation of 1.0 of the 60.0 minute(s) before.
Packet Loss (download, %) of WAN BT Business Broadband between Edge LDN-vVCE and its associated Gateway is found to be 5.0 and is 2 standard deviation(s) away from the mean of 1.0 and standard deviation of 1.0 of the 60.0 minute(s) before.
```

## Reference

- [VMware SD-WAN Orchestrator API v1 Release 4.0.1](https://code.vmware.com/apis/1045/velocloud-sdwan-vco-api)
- [VMware SD-WAN Knowledge Base - VMware SD-WAN Dynamic Multipath Optimisation (DMPO)](https://kb.vmware.com/s/article/2733094)
