import base64
import json
import time
from googleapiclient import discovery
from google.auth import compute_engine
from pprint import pprint

def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    x = json.loads(pubsub_message)
    vm_name = x["jsonPayload"]["resource"]["name"]
    vm_zone = x["jsonPayload"]["resource"]["zone"]
    project_id = x["resource"]["labels"]["project_id"]
    print("vm_name="+vm_name)
    print("vm_zone="+vm_zone)
    print("project_id="+project_id)
    
    compute = discovery.build('compute', 'v1')
    
    print("getting metadata fingerprint")
    request = compute.instances().get(project= project_id, zone= vm_zone, instance= vm_name)
    response = request.execute()
    pprint(response)
    metadata_fingerprint= response['metadata']['fingerprint']
    print("existing metadata fingerprint = " + metadata_fingerprint)

    vm_status=response['status']
    print("vm_status = " + vm_status)
    while vm_status != 'RUNNING' :
        print("going to sleep for 1 second...")
        time.sleep(1)
        request = compute.instances().get(project= project_id, zone= vm_zone, instance= vm_name)
        response = request.execute()
        vm_status=response['status']
        print("vm_status = " + vm_status)

    print("Setting VM metadata")
    metadata_body = {
      "fingerprint": metadata_fingerprint,
      "items": [
        {
         "key": "startup-script-url",
         "value": "gs://mybucket/my_script.sh"
        }
      ]
    }

    request = compute.instances().setMetadata(project=project_id, zone=vm_zone, instance=vm_name, body=metadata_body)
    response = request.execute()
    pprint(response)

    print("Restarting VM")
    request = compute.instances().reset(project=project_id, zone=vm_zone, instance=vm_name)
    response = request.execute()
    pprint(response)
    
