import json
import time
import random
import uuid
from google.cloud import pubsub_v1

PROJECT_ID = "project-2e0885aa-8f3e-4da5-86a"
TOPIC_ID = "cost-of-living-stream"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

cities = ["Calgary", "Toronto", "Vancouver", "Edmonton"]
categories = ["Housing", "Groceries", "Utilities", "Transportation"]

print(f" Starting mock cost-of-living stream to {topic_path}...")

try:
    while True:
        # Generate clean JSON metric packet
        payload = {
            "event_id": str(uuid.uuid4()),
            "timestamp": int(time.time()),
            "city": random.choice(cities),
            "category": random.choice(categories),
            "index_value": round(random.uniform(100.0, 180.0), 2)
        }
        
        # Binary encode packet payload
        data = json.dumps(payload).encode("utf-8")
        
        # Publish to Google Cloud Pub/Sub
        future = publisher.publish(topic_path, data)
        print(f"Published message ID: {future.result()} | Data: {payload}")
        
        # Wait 2 seconds between message ticks
        time.sleep(2)
except KeyboardInterrupt:
    print("\n Stream generator stopped cleanly.")
