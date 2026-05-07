import boto3
import json
import os
import time
from kubernetes import client, config

# Configuration
REGION = os.environ.get("AWS_REGION", "ap-south-2")
QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
TARGET_DEPLOYMENT = os.environ.get("TARGET_DEPLOYMENT", "target-app")
TARGET_NAMESPACE = os.environ.get("TARGET_NAMESPACE", "default")
DESIRED_REPLICAS = int(os.environ.get("DESIRED_REPLICAS", 2))

print(f"Starting Autonomous SRE Bot...")
print(f"Monitoring SQS Queue: {QUEUE_URL}")

# Initialize AWS SQS Client
sqs = boto3.client('sqs', region_name=REGION)

# Initialize Kubernetes Client
try:
    # Try incluster config first (when running as a pod)
    config.load_incluster_config()
    print("Loaded in-cluster Kubernetes config.")
except config.ConfigException:
    # Fallback to kubeconfig (when running locally for testing)
    config.load_kube_config()
    print("Loaded local kubeconfig.")

k8s_apps_v1 = client.AppsV1Api()

def auto_remediate():
    print(f"🚨 ALERT TRIGGERED 🚨 - Initiating auto-remediation for {TARGET_DEPLOYMENT}")
    try:
        # Fetch the current deployment
        deployment = k8s_apps_v1.read_namespaced_deployment(
            name=TARGET_DEPLOYMENT,
            namespace=TARGET_NAMESPACE
        )
        
        current_replicas = deployment.spec.replicas
        print(f"Current replicas: {current_replicas}. Desired: {DESIRED_REPLICAS}.")
        
        if current_replicas < DESIRED_REPLICAS:
            print(f"Scaling deployment {TARGET_DEPLOYMENT} back to {DESIRED_REPLICAS} replicas...")
            deployment.spec.replicas = DESIRED_REPLICAS
            
            # Apply the fix
            k8s_apps_v1.patch_namespaced_deployment(
                name=TARGET_DEPLOYMENT,
                namespace=TARGET_NAMESPACE,
                body=deployment
            )
            print("✅ Auto-remediation successful. Deployment scaled.")
        else:
            print("Deployment already at desired capacity. Investigating other potential issues... (Placeholder)")
            
    except Exception as e:
        print(f"❌ Failed to remediate: {e}")

def poll_sqs():
    while True:
        try:
            # Poll SQS for new alerts
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20 # Long polling
            )
            
            if 'Messages' in response:
                for message in response['Messages']:
                    print(f"Received message: {message['MessageId']}")
                    
                    # Assuming Datadog payload format
                    body = json.loads(message['Body'])
                    # If the message came through SNS, the actual alert is in the 'Message' field
                    if 'Message' in body:
                        # Attempt to parse inner message (might be a string)
                        try:
                            alert_details = json.loads(body['Message'])
                        except json.JSONDecodeError:
                            alert_details = body['Message']
                    else:
                        alert_details = body
                        
                    print(f"Alert Details: {alert_details}")
                    
                    # Trigger the fix
                    auto_remediate()
                    
                    # Delete the message from the queue after successful processing
                    sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    print("Message processed and deleted from SQS.")
            else:
                # No messages, continue polling
                pass
                
        except Exception as e:
            print(f"Error polling SQS: {e}")
            time.sleep(5) # Wait before retrying on error

if __name__ == "__main__":
    if not QUEUE_URL:
        print("CRITICAL ERROR: SQS_QUEUE_URL environment variable is not set.")
        exit(1)
        
    poll_sqs()
