from pythonmodels.Kresus import Kresus
from pythonmodels.FireflyIIIAPI import FireflyIIIAPI
from pythonmodels.Ntfy import Ntfy
from pythonmodels.CustomLogging import setup_logging

import hashlib
import json
import logging
from dotenv import load_dotenv
import os
from kafka import KafkaProducer
from kafka.errors import KafkaError
from typing import Union
from datetime import date, datetime
from time import sleep

from utils import test_create_get_delete_fireflyapi, check_kersus_firefly_accout, check_kresus_missing_transactions
    
    
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



def main():
    setup_logging()

    logger = logging.getLogger(__name__)
    
 
    producer = KafkaProducer(bootstrap_servers=['kafka1:9092', "kafka2:9093"])

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
    
    KRESUS_URL = load_env_variable(
        'KRESUS_URL',
        'F3S_KRESUS_URL',
        "http://your-kresus-instance:9876/v1",
    )


    logger.info(f"base_api_url for firefly-iii : {FIREFLY_BASE_URL}")
    logger.info(f"Firefly API token : {FIREFLY_PAT}")

    # Initialize Firefly III API wrapper
    firefly_api = FireflyIIIAPI(FIREFLY_BASE_URL, FIREFLY_PAT, "")
    # full testing of the firefly api
    test_create_get_delete_fireflyapi(firefly_api)
    
    def loop():
        # Initialize Kresus instance
        kresus = Kresus(KRESUS_URL)
        kresus.get_all_kresus()
        kresus.parse_account()
        check_kersus_firefly_accout(firefly_api, kresus)

        # Sync data from Kresus to Firefly III
        kresus.parse_transactions(date="2024-01-01")
        
        firefly_transactions_list = firefly_api.list_transactions(
            start="2024-01-01", end=f"{date.today()}"
        )

        kresus._reconciliate_transaction()

        missing_transactions = check_kresus_missing_transactions(
            local_transactions=kresus.transaction_list,
            transactions_list=firefly_transactions_list,
        )

        firefly_transactions_list = firefly_api.list_transactions(
            start="2024-01-01", end=f"{date.today()}"
        )

        kresus._reconciliate_transaction()

        missing_transactions = check_kresus_missing_transactions(
            local_transactions=kresus.transaction_list,
            transactions_list=firefly_transactions_list,
        )
        
        logger.info(
            f"{len(missing_transactions)} missing transactions from Kresus({len(kresus.transaction_list)}) to Firefly({len(firefly_transactions_list)})"
        )

        timestamp = datetime.now().isoformat()
        if len(missing_transactions) > 0:
            for transaction in missing_transactions:
                raw_message = {
                    "type": "MISSING TRANSACTION",
                    "date": timestamp,
                    "transaction_sha256": hashlib.sha256(
                        json.dumps(transaction.__dict__, indent=4, sort_keys=True, default=str).encode()
                    ).hexdigest(), # SHA256 hash of the transaction, it's use as an id for the consumer
                    "transaction": transaction.__dict__,
                }
                logger.info(f"Sending message to kafka: {raw_message}")
                producer.send('firefly-missing', bytes(json.dumps(raw_message, indent=4, default=str) , "utf-8"))
        
        producer.flush()
    
    while True:
        loop()
        sleep(60*60*24)



if __name__ == "__main__":
        main()
