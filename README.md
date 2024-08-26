# alert-tester

This is a very simple script to modify a PrometheusRule to force it to fire.
This can be useful when validating if an alert is being forwarded to a 
remote receiver correctly.

Please note this script does not revert a PrometheusRule definition and 
relies instead on the owning operator to revert the change. If this 
script is used to modify an unmanaged PrometheusRule, please remember 
to revert the change when you are finished testing.

