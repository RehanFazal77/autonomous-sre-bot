#!/bin/bash

# This script simulates a catastrophic failure in our target application

echo "⚠️  INITIATING CHAOS ENGINEERING PROTOCOL ⚠️"
echo "Target: target-app deployment"
echo "Action: Scaling replicas to 0 to simulate total outage"
echo ""

# Wait 2 seconds for dramatic effect
sleep 2

kubectl scale deployment target-app --replicas=0

echo ""
echo "💥 CHAOS DEPLOYED 💥"
echo "The target application has been scaled down to 0 replicas."
echo "Prometheus should detect this anomaly within 1-2 minutes and trigger an alert."
echo "Watch the SRE Bot logs to see the automated remediation in action."
