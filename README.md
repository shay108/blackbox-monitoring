# Blackbox Monitoring Project

## General
This monitoring system is set test and alert on two test use cases:
1. Basic boolean connectivity test
2. Basic latency test (**whether the request succeeded or not**)

## Installation
1. Download the files to a folder or clone the repo
2. In the root folder, create a virtualenv: `virtualenv -p python3.7 venv`
3. Activate the virtualenv: `. /venv/bin/activate`
4. Install the requirements: `pip install -r requirements.txt`
5. Run the program: `python blackbox_monitoring.py`
* Notice the default config file has 4 tests cases (2 successful and 2 failures)

## Inputs
The system assumes a JSON configuration file in the root folder.
Each record in the JSON has to contain at least 3 mandatory fields:
1. `testId` [Unique int] 
2. `testType` ["connectivity" | "latency"]
3. `endpoint` [URL string]

In case `testType` = "latency", two additional fields are mandatory:
1a. `method` ["GET"]
2a. `alertThreshold` [int (milliseconds)]

## Process
The program loops over the test cases in the config file and performs the required test. If an error is found, a `send_alert` function is called with the alert/error message.
At the moment, the alert sending process is simply writing the to stdout.

## Architecture
The system is designed to run in a Serverless function (e.g. Lambda), triggered via a cronjob.
According to instructions, I've neglected the individual frequency requirement.
Some architecture changes are suggested below.  

## Potential Improvements
1. At the moment - the method to check latency is very basic and can be improved
2. The latency test assumes that a failed `GET` request is **not an issue**
3. Run tests in parallel
4. Change the alert process to deliver messages to a pub-sub system (e.g. SNS) which can relay them to PagerDuty / Slack / etc.
5. Pull config file from a central location (e.g. S3) 
6. Add unittests for the different scenarios
7. Logs currently go to stdout (i.e. to CloudWatch) but can be relayed to a centralized logs location (e.g. Elasticsearch, Splunk, Logz.io)
8. Add package and deployment process for the service (e.g. via ServerlessFramework)
