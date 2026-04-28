# 🤖 Autonomous SRE Infrastructure & Self-Healing EKS Cluster

## 📖 Overview
This project demonstrates a production-grade, self-healing cloud infrastructure. It features a fully automated CI/CD pipeline, an AWS EKS Kubernetes cluster provisioned via Terraform, open-source observability via Prometheus, and a custom Python Site Reliability Engineering (SRE) Bot that automatically detects outages and heals the infrastructure without human intervention.

This project was built to showcase deep expertise in modern DevOps, Cloud Engineering, and Site Reliability practices.

---

## 🏗️ Architecture & Workflow

The core functionality of this project is its **Self-Healing Loop**:

1. **Infrastructure**: An Amazon EKS cluster and AWS SQS/SNS topics are provisioned entirely via **Terraform**.
2. **CI/CD Pipeline**: Code pushed to GitHub automatically triggers a **GitHub Actions** workflow that builds Docker images, pushes them to DockerHub, and deploys them to the EKS cluster.
3. **Observability**: **Prometheus** continuously monitors the cluster state (specifically the replicas of the `target-app`).
4. **Alerting**: If the `target-app` crashes or is maliciously scaled down (Chaos Engineering), Prometheus sends an alert to **Alertmanager**.
5. **Event Routing**: Alertmanager natively publishes the alert payload to an **AWS SNS** topic, which forwards it to an **AWS SQS** queue.
6. **Auto-Remediation**: The **Python SRE Bot**, running constantly inside the cluster, polls the SQS queue. Upon receiving the alert, it authenticates with the Kubernetes API, patches the broken Deployment, and restores the application to health instantly.

---

## 🛠️ Technology Stack
- **Cloud Provider**: AWS (EKS, EC2, SNS, SQS, IAM)
- **Infrastructure as Code (IaC)**: Terraform
- **Containerization & Orchestration**: Docker, Kubernetes
- **CI/CD**: GitHub Actions
- **Observability**: Prometheus, Alertmanager, Kube-State-Metrics
- **Scripting / Bot**: Python, Boto3, Kubernetes Python Client
- **Testing**: Bash (Chaos Engineering scripts)

---

## 📂 Repository Structure

```text
├── .github/workflows/   # CI/CD Pipeline definitions
├── app/                 # The Target Application (Python/Flask)
├── sre-bot/             # The Autonomous Python SRE Bot
├── k8s/                 # Kubernetes Deployment Manifests
├── prometheus/          # Helm values and Prometheus Alert Rules
├── scripts/             # Chaos Engineering testing scripts
└── terraform/           # IaC to build VPC, EKS, SNS, and SQS
```

---

## 🚀 How to Run the Project

### 1. Provision Infrastructure
Configure your AWS credentials locally, then use Terraform to build the cluster and queues:
```bash
cd terraform
terraform init
terraform apply -auto-approve
```

### 2. Configure AWS Permissions
Ensure that your GitHub Repository contains the following Secrets for the CI/CD pipeline:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

### 3. Deploy the Applications
Push your code to the `main` branch. GitHub Actions will automatically build the `target-app` and `sre-bot` Docker images, push them to DockerHub, and apply the Kubernetes manifests in the `k8s/` folder.

### 4. Install Prometheus Observability
Install the Prometheus stack using Helm, passing in the custom configuration to link it to AWS SNS:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -f prometheus/values.yaml --namespace default
kubectl apply -f prometheus/alert-rule.yaml
```

---

## 💥 Chaos Engineering (Testing the Bot)

To verify the self-healing infrastructure, we introduce intentional chaos into the system:

1. **Start the SRE Bot Logs:**
   ```bash
   kubectl logs -f deployment/sre-bot
   ```
2. **Execute the Chaos Script:**
   In a new terminal window, run the chaos script to simulate a total application outage:
   ```bash
   ./scripts/chaos.sh
   ```
3. **Observe the Healing:**
   Watch the SRE Bot's logs. Within 60 seconds, Prometheus will detect the outage, fire the alert through the AWS pipeline, and the Bot will automatically intercept it and scale the `target-app` back to its desired healthy state.

---

## 🧹 Cleanup
To avoid AWS charges, ensure you destroy the infrastructure when finished:
```bash
cd terraform
terraform destroy -auto-approve
```