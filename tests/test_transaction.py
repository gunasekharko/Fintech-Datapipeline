import uuid
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.transaction import TransactionExtractor, TransactionPayload



def test_valid_transaction_parsing_and_decimal_coercion() -> None:
    """Assert valid raw dictionary parses into TransactionPayload with Decimal precision."""
    extractor = TransactionExtractor()
    raw_data = {
        "transaction_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "account_id": "acc_1001",
        "amount": "250.7500",
        "currency": "USD",
        "merchant_category_code": "5411",
    }

    txn = extractor.validate(raw_data)

    assert isinstance(txn.transaction_id, uuid.UUID)
    assert txn.transaction_id == uuid.UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    assert txn.account_id == "acc_1001"
    assert isinstance(txn.amount, Decimal)
    assert txn.amount == Decimal("250.7500")
    assert txn.currency == "USD"
    assert txn.merchant_category_code == "5411"
    assert txn.created_at is not None


def test_generatepayload_factory() -> None:
    """Assert mock payload generator creates valid TransactionPayload instances."""
    txn = TransactionPayload.generatepayload()

    assert isinstance(txn, TransactionPayload)
    assert isinstance(txn.transaction_id, uuid.UUID)
    assert txn.amount > Decimal(0)
    assert txn.currency in {"USD", "EUR", "GBP", "INR"}


def test_negative_or_zero_amount_fails_validation() -> None:
    """Assert amounts <= 0 raise Pydantic ValidationError (Financial Invariant)."""
    extractor = TransactionExtractor()

    # Zero amount
    with pytest.raises(ValidationError):
        extractor.validate({
            "transaction_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            "account_id": "acc_1001",
            "amount": "0.00",
            "currency": "USD",
            "merchant_category_code": "5411",
        })

    # Negative amount
    with pytest.raises(ValidationError):
        extractor.validate({
            "transaction_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            "account_id": "acc_1001",
            "amount": "-150.00",
            "currency": "USD",
            "merchant_category_code": "5411",
        })


def test_invalid_currency_fails_validation() -> None:
    """Assert unapproved currency literal raises ValidationError."""
    extractor = TransactionExtractor()

    with pytest.raises(ValidationError):
        extractor.validate({
            "transaction_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            "account_id": "acc_1001",
            "amount": "100.00",
            "currency": "CAD",  # Not in Literal['USD', 'EUR', 'GBP', 'INR']
            "merchant_category_code": "5411",
        })


def test_invalid_uuid_fails_validation() -> None:
    """Assert non-UUID string raises ValidationError."""
    extractor = TransactionExtractor()

    with pytest.raises(ValidationError):
        extractor.validate({
            "transaction_id": "invalid-uuid-string-123",
            "account_id": "acc_1001",
            "amount": "100.00",
            "currency": "USD",
            "merchant_category_code": "5411",
        })


def test_decimal_places_exceeding_four_fails_validation() -> None:
    """Assert amounts with more than 4 decimal places fail validation."""
    extractor = TransactionExtractor()

    with pytest.raises(ValidationError):
        extractor.validate({
            "transaction_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            "account_id": "acc_1001",
            "amount": "100.12345",  # 5 decimal places > allowed 4
            "currency": "USD",
            "merchant_category_code": "5411",
        })
