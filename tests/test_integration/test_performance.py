"""Performance benchmark tests."""

import random
import string
import time
from urllib.parse import quote

import pytest

from corpuslab.ingest.engine import ingest_stream


def _generate_payloads(n: int, seed: int = 42) -> list:
    rng = random.Random(seed)
    payloads = []
    templates = [
        lambda: "simple cleartext " + "".join(rng.choices(string.ascii_lowercase, k=20)),
        lambda: quote("encoded " + "".join(rng.choices(string.ascii_lowercase, k=20))),
        lambda: "&lt;" + "".join(rng.choices(string.ascii_lowercase, k=15)) + "&gt;",
        lambda: "\\u0048\\u0065\\u006C\\u006C\\u006F" + str(rng.randint(0, 9999)),
        lambda: "".join(rng.choices(string.ascii_letters + string.digits + string.punctuation, k=60)),
    ]
    for _ in range(n):
        fn = rng.choice(templates)
        payloads.append(fn())
    return payloads


class TestPerformance:
    @pytest.mark.slow
    def test_10k_payloads_under_60_seconds(self, tmp_path):
        source = tmp_path / "big.txt"
        payloads = _generate_payloads(10000)
        source.write_text("\n".join(payloads))

        start = time.monotonic()
        records = list(ingest_stream(str(source), "text"))
        elapsed = time.monotonic() - start

        assert len(records) > 9000  # some dedup expected
        assert elapsed < 60.0, f"Took {elapsed:.1f}s (limit: 60s)"
