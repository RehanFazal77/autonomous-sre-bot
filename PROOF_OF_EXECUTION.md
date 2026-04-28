# 🛡️ Proof of Execution: Autonomous SRE Bot Auto-Remediation

The following log snippet was captured directly from the `sre-bot` pod running inside the Kubernetes cluster. It provides verifiable proof that the self-healing infrastructure successfully detected a simulated outage (via chaos engineering) and automatically remediated it by communicating with the Kubernetes API.

## 📝 Incident Log: Target Application Outage

```text
Starting Autonomous SRE Bot...
Monitoring SQS Queue: https://sqs.ap-south-2.amazonaws.com/793826055984/sre-remediation-queue
Loaded in-cluster Kubernetes config.

Received message: 5372fde3-dbf5-4aa3-a60e-fd5eabca3f8c
Alert Details: scale_up The target-app deployment has less than 2 replicas available. Target App Deployment Failed

Alerts Firing:
Labels:
 - alertname = DeploymentFailed
 - container = kube-state-metrics
 - deployment = target-app
 - endpoint = http
 - instance = 10.0.2.247:8080
 - job = kube-state-metrics
 - namespace = default
 - pod = prometheus-kube-state-metrics-5fbb55dcc9-8htnm
 - prometheus = default/prometheus-kube-prometheus-prometheus
 - service = prometheus-kube-state-metrics
 - severity = critical
Annotations:
 - action_required = scale_up
 - description = The target-app deployment has less than 2 replicas available.
 - summary = Target App Deployment Failed
Source: http://prometheus-kube-prometheus-prometheus.default:9090/graph?g0.expr=kube_deployment_status_replicas_available%7Bdeployment%3D%22target-app%22%7D+%3C+2&g0.tab=1

🚨 ALERT TRIGGERED 🚨 - Initiating auto-remediation for target-app
Current replicas: 0. Desired: 2.
Scaling deployment target-app back to 2 replicas...
✅ Auto-remediation successful. Deployment scaled.
Message processed and deleted from SQS.
```

## 🔍 Incident Breakdown
1. **Detection**: Prometheus detected that `target-app` replicas dropped below the required threshold of 2 (in this case, it was scaled to 0 via a chaos script).
2. **Alert Routing**: The alert was fired to AWS SNS and successfully queued in AWS SQS.
3. **Interception**: The SRE Bot pulled the message `5372fde3-dbf5-4aa3-a60e-fd5eabca3f8c` from the SQS queue.
4. **Resolution**: The bot authenticated with the cluster and instantly scaled the deployment back up to 2 replicas.
5. **Cleanup**: The bot deleted the message from the queue to prevent duplicate processing.



## Cluster Resources
```
$ kubectl get nodes 
NAME                                        STATUS   ROLES    AGE     VERSION
ip-10-0-x-xxx.ap-south-2.compute.internal   Ready    <none>   3h25m   v1.30.14-eks-bbe087e
ip-10-0-x-xx.ap-south-2.compute.internal    Ready    <none>   3h25m   v1.30.14-eks-bbe087e
ip-10-0-x-xxx.ap-south-2.compute.internal   Ready    <none>   98m     v1.30.14-eks-bbe087e
ip-10-0-x-xxx.ap-south-2.compute.internal   Ready    <none>   98m     v1.30.14-eks-bbe087e
ip-10-0-x-x.ap-south-2.compute.internal     Ready    <none>   3h25m   v1.30.14-eks-bbe087e
```
```
$ kubectl get pods -A 
NAMESPACE     NAME                                                     READY   STATUS    RESTARTS   AGE
default       alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          73m
default       prometheus-kube-prometheus-operator-68cdcdc4f7-nc7fj     1/1     Running   0          83m
default       prometheus-kube-state-metrics-5fbb55dcc9-8htnm           1/1     Running   0          83m
default       prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          83m
default       sre-bot-7d775d9b5f-4j7s5                                 1/1     Running   0          151m
default       target-app-544cf7d484-42mfz                              1/1     Running   0          72m
default       target-app-544cf7d484-w9g9f                              1/1     Running   0          72m
kube-system   aws-node-8f5cs                                           2/2     Running   0          3h25m
kube-system   aws-node-k95zn                                           2/2     Running   0          98m
kube-system   aws-node-l2tr8                                           2/2     Running   0          98m
kube-system   aws-node-pkpbh                                           2/2     Running   0          3h25m
kube-system   aws-node-x6b9z                                           2/2     Running   0          3h25m
kube-system   coredns-567d64bd9b-k5z25                                 1/1     Running   0          3h24m
kube-system   coredns-567d64bd9b-nlccs                                 1/1     Running   0          3h23m
kube-system   kube-proxy-b642x                                         1/1     Running   0          98m
kube-system   kube-proxy-fmqz7                                         1/1     Running   0          3h25m
kube-system   kube-proxy-gz9mj                                         1/1     Running   0          98m
kube-system   kube-proxy-r7smn                                         1/1     Running   0          3h25m
kube-system   kube-proxy-xfb7s                                         1/1     Running   0          3h25m
rehan-fazal@rehan-fazal-IdeaPad-Gaming-3-15IHU6:~/Desktop/Techolution/GITHUB/autonomous-sre-bot/scripts$ 
```
