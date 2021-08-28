# VMware VeloCloud SD-WAN: Detect and Alert of WAN Anomaly

This Python app is containerised with [Docker Compose](https://docs.docker.com/compose/) for rapid and modular deployment that fits in any microservice architecture.

It does the following:

1. Call the [VMware VeloCloud Orchestrator API](#reference) to retrieve the WAN quality metrics i.e. upload and download latency, jitter and packet loss, between the SD-WAN Edge and its associated SD-WAN Gateway, for all of the Edges in the enterprise network;
2. Detect WAN anomaly by comparing the WAN quality metrics of the last 5 minutes, to those of the 60 minutes before, with a sampling interval of 5 minutes; and
3. Send an email alert should the averages of the WAN quality metrics of the last 5 minutes be more than two standard deviations higher than the averages of the 60-minute historical baseline.

For details on the WAN path monitoring mechanism and sampling interval, please refer to the [VMware SD-WAN Dynamic Multipath Optimisation (DMPO)](#reference) article on the VMware SD-WAN Knowledge Base.

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
2. Create the [environment variables](#environment-variables) for the VeloCloud Orchestrator authentication, and modify the [sampling durations and interval](#sampling-durations-and-interval) and the [crontab](#crontab) if needed;
3. [Docker Compose](#docker-compose) or [build and run](#build-and-run) the image manually to start the app, or alternatively run the Python script as a standalone service.

### Git Clone

Download a copy of the app with `git clone`
```shell
$ git clone https://github.com/kurtcms/vco-wan-anomaly-alert /app/
```

### Environment Variables

The app expects the hostname, username and password for the VeloCloud Orchestrator as well as the SMTPS port number, SMTP server address, the alert receiver email address, the alert sender email address and password, as environment variables in a `.env` file in the same directory. Be sure to create the `.env` file.

```shell
$ nano /app/.env
```

And define the variables accordingly.

```
VCO_HOSTNAME = 'vco.managed-sdwan.com/'
VCO_USERNAME = 'kurtcms@gmail.com'
VCO_PASSWORD = '(redacted)'

EMAIL_SSL_PORT = 465
EMAIL_SMTP_SERVER = 'smtp.kurtcms.org'
EMAIL_SENDER = 'alert@kurtcms.org'
EMAIL_RECEIVER = 'kurtcms@gmail.com'
EMAIL_SENDER_PASSWORD = '(redacted)'
```

### Sampling Durations and Interval

The intervals for the WAN quality metrics are 300 seconds i.e. 5 minutes and 3,600 seconds i.e. 60 minutes, for the present and historical baseline respectively, with a sampling interval of 300 seconds i.e. 5 minutes. All of these are passed to the respective function as argument at runtime and may be adjusted if needed.

```shell
$ nano /app/vco-wan-anomaly-alert.py
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

By default the app is scheduled with [cron](https://crontab.guru/) to retrieve the WAN quality metrics every 5 minutes, with `stdout` and `stderr` redirected to the main process for `Docker logs`.  

Modify the `crontab` if a different schedule is required.

```shell
$ nano /app/crontab
```

### Docker Container

#### Docker Compose

With Docker Compose, the container may be provisioned with a single command. Be sure to have Docker Compose [installed](https://docs.docker.com/compose/install/).

```shell
$ docker-compose up
```

Stopping the container is as simple as  a single command.

```shell
$ docker-compose down
```

#### Build and Run

Otherwise the Docker image can also be built manually.

```shell
$ docker build -t vco-wan-anomaly-alert /app/
```

Run the image with Docker once it is ready.  

```shell
$ docker run -it --rm --name vco-wan-anomaly-alert vco-wan-anomaly-alert
```

### Standalone Python Script

#### Dependencies

Alternatively the `vco-wan-anomaly-alert.py` script may be deployed as a standalone service. In which case be sure to install the following required libraries:

1. [Requests](https://github.com/psf/requests)
2. [Python-dotenv](https://github.com/theskumar/python-dotenv)
3. [NumPy](https://github.com/numpy/numpy)
4. [pandas](https://github.com/pandas-dev/pandas)

```shell
$ pip3 install requests python-dotenv numpy pandas
```

The [VeloCloud Orchestrator JSON-RPC API Client](https://github.com/vmwarecode/VeloCloud-Orchestrator-JSON-RPC-API-Client---Python) library is also required. Download it with [wget](https://www.gnu.org/software/wget/).

```shell
$ wget -P /app/ https://raw.githubusercontent.com/vmwarecode/VeloCloud-Orchestrator-JSON-RPC-API-Client---Python/master/client.py
```

#### Cron

The script may then be executed with a task scheduler such as [cron](https://crontab.guru/) that runs it once every 5 minutes for example.

```shell
$ (crontab -l; echo "*/5 * * * * /usr/bin/python3 /app/vco-wan-anomaly-alert.py") | crontab -
```

## Email Alert

Email alert will be sent from `EMAIL_SENDER` to `EMAIL_RECEIVER` should an anomaly be found. The subject of the email will be `WAN Anomoly Alert` with the details of the anomaly in the email body.

```
Latency (download, ms) of WAN BT Business Broadband between Edge LDN-vVCE and its associated Gateway is found to be 100.0 and is 2 standard deviation(s) away from the mean of 75.0 and standard deviation of 10.0 of the 60.0 minute(s) before.
Jitter (download, ms) of WAN BT Business Broadband between Edge LDN-vVCE and its associated Gateway is found to be 5.0 and is 2 standard deviation(s) away from the mean of 2.0 and standard deviation of 1.0 of the 60.0 minute(s) before.
Packet Loss (download, %) of WAN BT Business Broadband between Edge LDN-vVCE and its associated Gateway is found to be 5.0 and is 2 standard deviation(s) away from the mean of 1.0 and standard deviation of 1.0 of the 60.0 minute(s) before.
```

## Reference

- [VMware SD-WAN Orchestrator API v1 Release 4.0.1](https://code.vmware.com/apis/1045/velocloud-sdwan-vco-api)
- [VMware SD-WAN Knowledge Base - VMware SD-WAN Dynamic Multipath Optimisation (DMPO)](https://kb.vmware.com/s/article/2733094)
