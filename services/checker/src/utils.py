from pythonmodels.FireflyIIIAPI import FireflyIIIAPI
from pythonmodels.Kresus import Kresus
from pythonmodels.Ntfy import Ntfy
from pythonmodels.models import Transaction

from dateutil.relativedelta import relativedelta
from datetime import date
import logging
from typing import List
import math

logger = logging.getLogger(__name__)

def test_create_get_delete_fireflyapi(firefly_api: FireflyIIIAPI):
    """
    Tests the creation, retrieval, and deletion of transactions in Firefly III.

    Args:
        firefly_api (FireflyIIIAPI): An instance of the FireflyIIIAPI class.
    """
    transaction_data = {
        "apply_rules": True,
        "fire_webhooks": True,
        "transactions": [
            {
                "type": "transfer",
                "date": f"{date.today()}",
                "amount": "200",
                "description": "test_create_get_delete_fireflyapi from python",
                "source_name": "Crédit Agricole Courant",
                "destination_name": "Boursorama CTO",
                "category_name": "",
                "interest_date": "",
                "book_date": "",
                "process_date": "",
                "due_date": "",
                "payment_date": "",
                "invoice_date": "",
                "internal_reference": "",
                "notes": "Created from python",
                "external_url": "",
            }
        ],
    }

    new_transaction = firefly_api.store_transaction(transaction_data)

    if new_transaction:
        logger.info(f"Nouvelle transaction : {new_transaction}")
        transaction_in_db = firefly_api.get_transaction(new_transaction.transaction_id)
        logger.info(f"{(new_transaction == transaction_in_db)=}")

    updated_new_transaction_data = {
        "apply_rules": True,
        "fire_webhooks": True,
        "transactions": [
            {
                "type": "transfer",
                "date": f"{date.today()}",
                "amount": "500",
                "description": "test_create_get_delete_fireflyapi from python",
                "source_name": "Crédit Agricole Courant",
                "destination_name": "Boursorama CTO",
                "category_name": "",
                "interest_date": "",
                "book_date": "",
                "process_date": "",
                "due_date": "",
                "payment_date": "",
                "invoice_date": "",
                "internal_reference": "",
                "notes": "Updated from python",
                "external_url": "",
            }
        ],
    }

    update_transaction = firefly_api.update_transaction(new_transaction.transaction_id, updated_new_transaction_data)
    updated_new_transaction = Transaction(**updated_new_transaction_data["transactions"][0])

    logger.info(f"{(update_transaction == updated_new_transaction)=}")

    transactions_list = firefly_api.list_transactions(
        start=f"{date.today() - relativedelta(months=1)}", end=f"{date.today()}"
    )

    if update_transaction in transactions_list:
        logger.info("Nouvelle transaction dans la liste des transactions")
        logger.info("Deletion de la transaction")
        deleted_transaction = firefly_api.delete_transaction(
            update_transaction.transaction_id
        )
        logger.info(f"transaction {update_transaction} deleted")
    else:
        logger.error("Nouvelle transaction n'est pas dans la liste des transactions")
        raise Exception("Nouvelle transaction n'est pas dans la liste des transactions")
    transactions_list = firefly_api.list_transactions(
        start=f"{date.today() - relativedelta(months=1)}", end=f"{date.today()}"
    )

    if update_transaction not in transactions_list:
        logger.info("Nouvelle transaction n'est plus dans la liste des transactions")
        
        
        
def check_kersus_firefly_accout(firefly_api: FireflyIIIAPI, kresus: Kresus):
    """
    Compares account balances in Kresus with those in Firefly III.

    Args:
        firefly_api (FireflyIIIAPI): An instance of the FireflyIIIAPI class.
        kresus (Kresus): An instance of the Kresus class.
    """
    fault_account : list[str] = []
    for kresus_account in kresus.list_accounts_to_sync:
        for firefly_account in firefly_api.list_accounts():
            if kresus_account.name == firefly_account.name:
                # Dont lookup CTO or PEA beacause it contain stock and value can change without transaction
                if kresus_account.current_balance != firefly_account.current_balance and "CTO" not in kresus_account.name and not "PEA" in kresus_account.name:
                    logger.info(
                        f"Account '{kresus_account.name}' balance is not up to date : {kresus_account.current_balance=} == {firefly_account.current_balance=} : {kresus_account.current_balance == firefly_account.current_balance} "
                    )
    if len(fault_account) > 0:
        logger.info(f"{len(fault_account)} accounts are not up to date")
        logger.info(f"list of faulty account : {fault_account}")
    else:
        logger.info(f"All account are up to date, great !")

def check_kresus_missing_transactions(
    local_transactions: List[Transaction], transactions_list: List[Transaction]
) -> List[Transaction]:
    """
    Compares Kresus transactions with those in an external dataset to identify missing transactions.

    Args:
        local_transactions (List[Transaction]): Transactions obtained from Kresus.
        transactions_list (List[Transaction]): Transactions from the external dataset.

    Returns:
        List[Transaction]: Transactions that are present in Kresus but missing in the external dataset.
    """
    missing_transactions: List[Transaction] = []

    for local_transaction in local_transactions:
        match_found = False
        for transaction in transactions_list:
            if (
                local_transaction.date == transaction.date
                and math.isclose(
                    local_transaction.amount, transaction.amount, abs_tol=0.001
                )
                and (
                    (local_transaction.source_name == transaction.source_name)
                    or (
                        local_transaction.destination_name
                        == transaction.destination_name
                    )
                )
            ):
                logger.debug(
                    f"{local_transaction.type=} && {transaction.type=} : {local_transaction.type == transaction.type}"
                )
                logger.debug(
                    f"{local_transaction.amount=} && {transaction.amount=} : {math.isclose(local_transaction.amount, transaction.amount, abs_tol=0.001)}"
                )
                logger.debug(
                    f"{local_transaction.date=} && {transaction.date=} : {local_transaction.date == transaction.date}"
                )
                logger.debug(
                    f"{local_transaction.source_name=} && {transaction.source_name=} : {local_transaction.source_name == transaction.source_name}"
                )
                logger.debug(
                    f"{local_transaction.destination_name=} && {transaction.destination_name=} : {local_transaction.destination_name == transaction.destination_name}"
                )
                logger.debug(
                    f"{local_transaction.description=} && {transaction.description=} : {Transaction._compare_descriptions(local_transaction, transaction, 50) if local_transaction.type != 'transfer' else True}\n"
                )
                match_found = True
                break
        if not match_found:
            missing_transactions.append(local_transaction)
            logger.info(f"{local_transaction.date=}")
            logger.info(f"{local_transaction.amount=}")
            logger.info(f"{local_transaction.source_name=}")
            logger.info(f"{local_transaction.destination_name=}")
            logger.info(f"{local_transaction.description=}\n")

    return missing_transactions

