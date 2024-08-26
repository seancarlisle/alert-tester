import json
import subprocess
import argparse

"""
This is a very simple script to modify a PrometheusRule to force it to fire.
This can be useful when validating if an alert is being forwarded to a 
remote receiver correctly.

Please note this script does not revert a PrometheusRule definition and 
relies instead on the owning operator to revert the change. If this 
script is used to modify an unmanaged PrometheusRule, please remember 
to revert the change when you are finished testing.

This script comes with no warranty and is provided as-is. 
"""

def run_command(command):
    try:
        return subprocess.run(command, shell=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error:\n{e.stderr.decode('ASCII')}")

parser = argparse.ArgumentParser(
        prog="fire-alert",
        description="Script to force a desired OpenShift alert to fire.")
parser.add_argument("kubeconfig", help="The absolute path to a valid Kubeconfig")
parser.add_argument("target_alert", help="The name of the alert rule to modify")
args = parser.parse_args()

# Verify KUBECONFIG is valid
export_kubeconfig=f"export KUBECONFIG={args.kubeconfig}"
test_cmd = f"{export_kubeconfig};oc get co"

result = run_command(test_cmd)
if result is None:
    exit()

# Retrieve the prometheusrules to search for desired alert
# TODO: Update the code to allow the user to provide a PrometheusRule 
# if they know which one defines the target alert.
alert_name = args.target_alert
command = export_kubeconfig + f";oc get prometheusrules -A -ojson"

result = run_command(command)
if result is not None:
    if result.stdout is not None:
        prometheusrules = json.loads(result.stdout)
else:
    exit()

# Find the desired alert
print(f"Searching for alert {alert_name}...")
for i in prometheusrules["items"]:
    for group in i["spec"]["groups"]:
            for rule in group["rules"]:
                if "alert" in rule.keys():
                    if rule["alert"] == str(alert_name):
                        promrule_name = i["metadata"]["name"]
                        promrule_ns = i["metadata"]["namespace"]

                        # Create a json patch object and apply it to the PrometheusRule
                        patch = {"spec": { "groups": [ { "name": group["name"], "rules": [ { "alert": rule["alert"], "expr": 1, "for": "1s" } ] } ] } }
                        print(f"Alert found. Patching {alert_name} to fire immediately...")
                        command = f"{export_kubeconfig};oc patch prometheusrule/{promrule_name} -n {promrule_ns} --type=merge -p='{json.dumps(patch)}'"
                        result = run_command(command)
                        if result is not None:
                            print(result.stdout.decode('ASCII'))
                        exit()
                        
# We hit the bottom of the list, the alertname does not exist
print(f"The alert name {alert_name} was not found. Please verify th
