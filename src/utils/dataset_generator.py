from collections.abc import Generator
import random
from typing import Any
from csv import DictWriter, DictReader
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Dict
import tracemalloc


class DatesetGenerator:
    def __init__(self) -> None:
        pass

    @property
    def generaterecords(self) -> Any:
        transaction_id = uuid.uuid4()
        account_id = f"acct-{str(random.randint(1,1000))}"
        amount = Decimal(random.randint(100, 10000000)) / Decimal(100)
        currency = random.choice(["USD", "EUR", "GBP", "INR"])
        merchant_category_code = random.randint(1, 9999)
        created_at = datetime.now(timezone.utc)
        return {
            "transaction_id": transaction_id,
            "account_id": account_id,
            "amount": amount,
            "currency": currency,
            "merchant_category_code": merchant_category_code,
            "created_at": created_at,
        }

    def generate_csv(
        self, records: List[Dict[str, Any]], filename: str = "transactions.csv"
    ) -> None:
        if not records:
            return
        print(records)
        headers = list(records[0].keys())
        with open(filename, mode="w", encoding="utf-8", newline="") as f:
            writer = DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)

    def read_all_records_naive(self, filename: str = "transactions.csv") -> Any:
        with open(filename, mode="r", encoding="utf-8") as f:
            reader = DictReader(f)
            return list(reader)

    def stream_ledger_records(
        self, filename: str = "transactions.csv", chunk_size: int = 1000
    ) -> Generator[List[Dict[str, str]], None, None]:
        with open(filename, mode="r", encoding="utf-8") as f:
            reader = DictReader(f)
            chunk: List[Dict[str, str]] = []
            for row in reader:
                chunk.append(row)
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
            if chunk:
                yield chunk


if __name__ == "__main__":
    dataset = DatesetGenerator()
    filename = "transactions.csv"

    print("--- 1. Naive Reader (read_all_records_naive) ---")
    tracemalloc.start()

    all_records = dataset.read_all_records_naive(filename)
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()

    tracemalloc.stop()
    print(f"Loaded: {len(all_records):,} records.")
    print(f"Peak Memory: {peak_bytes / (1024 * 1024):.2f} MB")

    # Clean up RAM before starting Test 2!
    del all_records

    # ==========================================
    # TEST 2: Streaming Generator Reader (Low RAM O(1))
    # ==========================================
    print("\n--- 2. Streaming Generator (stream_ledger_records) ---")
    tracemalloc.start()

    total_streamed = 0
    # Must use a FOR LOOP to pull chunks from generator!
    for chunk in dataset.stream_ledger_records(filename, chunk_size=1000):
        total_streamed += len(chunk)

    current_bytes, peak_bytes = tracemalloc.get_traced_memory()

    tracemalloc.stop()
    print(f"Streamed: {total_streamed:,} records.")
    print(f"Peak Memory: {peak_bytes / (1024 * 1024):.2f} MB")
