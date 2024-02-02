from kafka import KafkaProducer
import json
from time import sleep
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()

logging.basicConfig(level=logging.INFO, handlers=[handler])

producer = KafkaProducer(bootstrap_servers=['kafka1:9092', "kafka2:9093"])

transaction_sha256 = "87b39170689fcaab7296382e1deb57d333ddab8c95ddad2822c402212ba38756"
kafka_message = {
    "event": "transaction_added",
    "transaction_sha256": transaction_sha256
}

producer.send('firefly-added', json.dumps(kafka_message).encode('utf-8'))
producer.flush()
print(f"Sent message: {kafka_message}")
