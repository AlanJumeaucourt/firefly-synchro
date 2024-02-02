from pythonmodels.models import Transaction
from pythonmodels.FireflyIIIAPI import FireflyIIIAPI
from dotenv import load_dotenv
import logging
import os

from kafka import KafkaProducer
from kafka import KafkaConsumer

import json

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_env_variable(env_key: str, fallback_env_key: str, default_value: str) -> str:
    """
    Loads an environment variable with a fallback and default value.
    Raises an exception if the default value is used.
    """
    value = os.getenv(env_key)
    if value is None:
        value = os.getenv(fallback_env_key, default_value)
        if value == default_value:
            raise Exception(f"Please set the {fallback_env_key} environment variable OR the {env_key} in the .env file"
)
    return value


load_dotenv()

# Accessing variables using the function
FIREFLY_BASE_URL = load_env_variable(
    'FIREFLY_BASE_URL', 
    'F3S_FIREFLY_BASE_URL', 
    "https://your-firefly-instance.com/api/v1", 
)

FIREFLY_PAT = load_env_variable(
    'FIREFLY_PAT',
    'F3S_FIREFLY_PAT', 
    "your_firefly_personal_access_token", 
)


logger.info(f"base_api_url for firefly-iii : {FIREFLY_BASE_URL}")
logger.info(f"Firefly API token : {FIREFLY_PAT}")

# Initialize Firefly III API wrapper
firefly_api = FireflyIIIAPI(FIREFLY_BASE_URL, FIREFLY_PAT, "")


def add_missing_transactions(
    firefly_api: FireflyIIIAPI, missing_transaction: Transaction
):
    """
    Adds missing transactions to an external dataset using the Firefly III API.

    Args:
        firefly_api (FireflyIIIAPI): An instance of the FireflyIIIAPI class.
        missing_transactions (List[Transaction]): A list of transactions to be added.
    """

    transaction_data = {
        "apply_rules": True,
        "fire_webhooks": True,
        "transactions": [
            {
                "type": missing_transaction.type,
                "date": missing_transaction.date.strftime("%Y-%m-%d"),
                "amount": str(missing_transaction.amount),
                "description": str(missing_transaction.description),
                "source_name": missing_transaction.source_name,
                "destination_name": missing_transaction.destination_name,
                "category_name": "",
                "interest_date": "",
                "book_date": "",
                "process_date": "",
                "due_date": "",
                "payment_date": "",
                "invoice_date": "",
                "internal_reference": "",
                "notes": "",
                "external_url": "",
            }
        ],
    }
    logger.info(transaction_data)
    firefly_api.store_transaction(transaction_data=transaction_data)


producer = KafkaProducer(bootstrap_servers=["kafka1:9092", "kafka2:9093"])



def find_transaction_by_sha(consumer, sha256):
    """Search for a transaction in Kafka messages by SHA256."""
    for message in consumer:
        try:
            msg = json.loads(message.value.decode('utf-8'))
            if msg.get('transaction_sha256') == sha256:
                return msg
        except Exception as e:
            logger.error(f"Error processing Kafka message: {e}")
    return None


def process_add_transaction_events():
    """Process 'add_transaction' events and add corresponding transactions."""
    add_transaction_consumer = KafkaConsumer(
        "add_transaction",
        bootstrap_servers=["kafka1:9092", "kafka2:9093"],
        auto_offset_reset='earliest'
    )
    missing_transaction_consumer = KafkaConsumer(
        "firefly-missing",
        bootstrap_servers=["kafka1:9092", "kafka2:9093"],
        auto_offset_reset='earliest'
    )

    for message in add_transaction_consumer:
        try:
            event_msg = json.loads(message.value.decode('utf-8'))
            if event_msg.get('event') == 'add_transaction':
                sha256 = event_msg.get('transaction_sha256')
                missing_transaction_msg = find_transaction_by_sha(missing_transaction_consumer, sha256)
                
                if missing_transaction_msg and len(missing_transaction_msg) > 0:
                    logger.info(f"Adding missing transaction: {missing_transaction_msg['transaction']}")
                    transaction = Transaction(**missing_transaction_msg["transaction"])
                    
                    
                    add_missing_transactions(firefly_api, transaction)
                    
                    producer.send("firefly-added", value=json.dumps(missing_transaction_msg).encode('utf-8'))
                    kafka_message = {
                    "event": "transaction_added",
                    "transaction_sha256": sha256
                    }

                    producer.send('firefly-added', json.dumps(kafka_message).encode('utf-8'))
                    producer.flush()
  


        except Exception as e:
            logger.error(f"Error processing 'add_transaction' event: {e}")



process_add_transaction_events()

