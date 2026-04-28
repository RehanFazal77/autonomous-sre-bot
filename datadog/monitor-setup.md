# Datadog Observability & Alerting Setup

## 1. Install Datadog Agent on EKS
Once your EKS cluster is running, install the Datadog agent using Helm:

```bash
helm repo add datadog https://helm.datadoghq.com
helm repo update

# Replace the API keys in values.yaml before running this:
helm install datadog-agent datadog/datadog -f datadog/values.yaml --namespace datadog --create-namespace
```

## 2. Configure AWS Integration
1. Go to your Datadog Dashboard -> Integrations.
2. Search for **AWS** and configure it.
3. Provide your AWS Account ID and allow Datadog to publish to your SNS topic (`datadog-alerts-topic`). 

## 3. Create the Trigger Monitor
This monitor watches the `target-app` and triggers an alert if pods drop below the desired count.

1. Go to **Monitors** -> **New Monitor** -> **Kubernetes**.
2. **Define the metric**: 
   - Watch `kubernetes_state.deployment.replicas_available`
   - Filter by `kube_deployment:target-app`
3. **Set alert conditions**:
   - Alert when the value is `< 2` at least once during the last 5 minutes.
4. **Notify your team (The SRE Bot)**:
   - In the "Notify" section, search for the AWS SNS integration webhook you set up.
   - Example: `@sns-datadog-alerts-topic`
5. **Message Body**:
   - Set the message to JSON format so the SRE Bot can easily parse it.
   ```json
   {
     "alert_type": "Deployment Failed",
     "deployment": "target-app",
     "action_required": "scale_up"
   }
   ```
6. Save the monitor.

Now, whenever you run `./scripts/chaos.sh`, this monitor will trigger, Datadog will send the JSON payload to AWS SNS, SNS forwards it to AWS SQS, and the Python SRE Bot will intercept and remediate it.
