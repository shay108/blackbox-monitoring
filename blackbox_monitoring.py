import json
import urllib3
import time

# Consts
CONFIG_FILE = 'monitoring_config.json'
BASE_CONNECTIVITY_TEST = {
    "testId": "000",
    "testType": "connectivity",
    "endpoint": "https://www.amazon.com"
}
SUPPORTED_TEST_TYPES = ["connectivity", "latency"]
SUPPORTED_METHODS = ["GET"]


def get_parsed_config_file(config_file) -> dict:
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as err:
        print(f"Failed to parse config file: {config_file}, with error message {str(err)}")
        exit(1)


def test_connectivity(test_case: dict) -> str:
    try:
        res = http.request('GET', test_case["endpoint"])
        if res.status == 200:
            return "OK"
        else:
            return str(res.status)
    except Exception as err:
        return str(err)


def test_latency(test_case: dict) -> str:
    # Validate params
    if ("alertThreshold" not in test_case) or ("method" not in test_case):
        print(f"Missing 'alertThreshold' and/or 'method' parameters in test number: {test_case['testId']}. Skipping test...")
        return "skip"
    if test_case["method"] not in SUPPORTED_METHODS:
        return f"Unsupported method ({test_case['method']}) in latency check"
    if test_case["alertThreshold"] <= 0:
        return f"Invalid threshold ({test_case['alertThreshold']}) in latency check"

    try:
        start = time.time()
        http.request('GET', test_case["endpoint"])
        end = time.time()
        latency = int((end-start) * 1000)
        if latency <= test_case["alertThreshold"]:
            return "OK"
        else:
            return f"Measured latency ({latency} ms) is higher than the threshold ({test_case['alertThreshold']} ms)"
    except Exception as err:
        return str(err)


def send_alert(alert_message: str) -> None:
    print(alert_message)
    print()


# Setup sanity checks
tests_dict = get_parsed_config_file(CONFIG_FILE)

http = urllib3.PoolManager()
if test_connectivity(BASE_CONNECTIVITY_TEST) != "OK":
    print("Failed to get basic connectivity. Error issues?")
    exit(1)

# Main
seen_test_ids = dict()
try:
    for test in tests_dict:
        # Verify mandatory fields
        if test["testId"] in seen_test_ids:
            print(f"Duplicate testId: {test['testId']}. Skipping test...")
            continue
        else:
            seen_test_ids[test["testId"]] = True
        if test["testType"] not in SUPPORTED_TEST_TYPES:
            print(f"Invalid testType ({test['testType']}). Skipping test...")
            continue
        if "endpoint" not in test:
            print(f"Missing 'endpoint' parameter in test number: {test['testId']}. Skipping test...")
            continue

        # Test dispatcher
        if test["testType"] == "connectivity":
            test_result = test_connectivity(test)
        elif test["testType"] == "latency":
            test_result = test_latency(test)

        if test_result not in ["OK", "skip"]:
            send_alert(f"Endpoint: {test['endpoint']} has failed a {test['testType']} test, with error message: {test_result}")

except Exception as error:
    print(f"Critical error in parsing testId: {test['testId']}, with error message: {str(error)}. Exiting!")
    exit(1)
