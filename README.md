# gcp-vm-creation-action
This is an example showing how to add a startup script to a newly created VM. After the script is added the VM is restarted so that the script can run.
We create a logging sink that sends new VM creation notification to Pub/Sub. A Google Cloud Function is triggered whenever new messages are pulled to Pub/Sub and adds the startup-script-url metadata to the VM, pointing to a custom script that should do some initialization action.


# Important
```diff
- NO GUARANTEES, NO LIABILITY, THIS IS JUST EXAMPLE CODE
- NOT PRODUCTION CODE
- TESTED ONLY IN MY TEST ORG
```

# Create PubSub topic
```
export PROJECT_ID=<YOUR_PROJECT_ID>
gcloud config set project $PROJECT_ID

gcloud pubsub topics create new-vm-created-sink
```

# Choose one of the Steps 1 OR 2
## 1) PROJECT LEVEL SINK
```
gcloud logging sinks create new-vm-sink pubsub.googleapis.com/projects/$PROJECT_ID/topics/new-vm-created-sink --project=$PROJECT_ID --log-filter='resource.type="gce_instance" AND jsonPayload.event_subtype="compute.instances.insert" AND jsonPayload.event_type="GCE_API_CALL"'
```

## 2) ORG LEVEL SINK
```
export ORG_ID=<YOUR_ORG_ID>
gcloud logging sinks create new-vm-sink pubsub.googleapis.com/projects/$PROJECT_ID/topics/new-vm-created-sink --organization=$ORG_ID --include-children --log-filter='resource.type="gce_instance" AND jsonPayload.event_subtype="compute.instances.insert" AND jsonPayload.event_type="GCE_API_CALL"'
```

# Pub/Sub setup
```
gcloud pubsub topics add-iam-policy-binding new-vm-created-sink  --member='serviceAccount:<SERVICE_ACC_FROM_SINK_CREATE>@gcp-sa-logging.iam.gserviceaccount.com' --role='roles/pubsub.publisher'
```

# Trigger notification
```
gcloud compute instances create test-vm-pubsub-instance-3 --machine-type=f1-micro --zone=us-central1-b --preemptible --no-restart-on-failure --maintenance-policy=terminate --no-address

gcloud pubsub subscriptions create new-vm-sink-sub --topic=new-vm-created-sink

gcloud pubsub subscriptions pull new-vm-sink-sub

gcloud compute instances delete test-vm-pubsub-instance-1 --zone=us-central1-b --quiet
```
# Google Cloud function
create a GCF, PubSub. Run this from the gcf folder.
```
gcloud functions deploy vm-creation-test --runtime python37 --trigger-topic projects/$PROJECT_ID/topics/new-vm-created-sink
```

![log1](https://raw.githubusercontent.com/kojnp/gcp-vm-creation-action/main/images/log.png)

![log2](https://raw.githubusercontent.com/kojnp/gcp-vm-creation-action/main/images/log2.png)

![log3](https://raw.githubusercontent.com/kojnp/gcp-vm-creation-action/main/images/log3.png)