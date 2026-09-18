import random
from pydantic import Field
from typing import Literal, Any
from abc import ABC, abstractmethod
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from pydantic import BaseModel


class BaseExtractor(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def extract(self) -> Any:
        pass

    @abstractmethod
    def validate(self, raw_dict: dict[str, Any]) -> Any:
        pass

CurrencyCode = Literal["USD", "EUR", "GBP", "INR"]

class TransactionPayload(BaseModel):
    transaction_id: uuid.UUID = Field(description="transaction id field")
    account_id: str = Field(description="field for accountid")
    amount: Decimal = Field(
        description="Field for amount", gt=Decimal(0), decimal_places=4
    )
    currency: CurrencyCode = Field(description="Transaction currency ISO code")

    merchant_category_code: str = Field(
        description="field is for merchant category code"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def generatepayload(cls) -> "TransactionPayload":
        txn = uuid.uuid4()
        account_id = str(random.randint(1, 1000))
        amount = Decimal(random.randint(100, 10000000)) / Decimal(100)
        currency_options: list[Literal["USD", "EUR", "GBP", "INR"]] = [
            "USD",
            "EUR",
            "GBP",
            "INR",
        ]
        currency = random.choice(currency_options)
        merchant_category_code = str(random.randint(1, 9999))
        created_at = datetime.now(timezone.utc)
        return TransactionPayload(
            transaction_id=txn,
            account_id=account_id,
            amount=amount,
            currency=currency,
            merchant_category_code=merchant_category_code,
            created_at=created_at,
        )


class TransactionExtractor(BaseExtractor):
    def extract(self) -> Any:
        pass

    def validate(self, raw_data: dict[str, Any]) -> TransactionPayload:
        return TransactionPayload.model_validate(raw_data)


if __name__ == "__main__":
    txnextractor = TransactionExtractor()

    raw_dict = {
        "transaction_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "account_id": "acc_1001",
        "amount": "250.75",
        "currency": "USD",
        "merchant_category_code": "5411",
        "created_at": "2026-09-18T22:00:00Z",
    }
    invalid_dict = {
        "transaction_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "account_id": "acc_1001",
        "amount": "250.75",
        "currency": "USD",
        "merchant_category_code": 5411,
        "created_at": "2026-09-18T22:00:00Z",
    }

    validated_tx = txnextractor.validate(raw_dict)
    print(f"Validated Transaction object:{validated_tx}")
    print(f"Amount type: {type(validated_tx.amount)}")

    invalidate_tx = txnextractor.validate(invalid_dict)
    print(f"inValidated Transaction object:{invalidate_tx}")
