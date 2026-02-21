"""Tests for redaction patterns."""

from corpuslab.redaction.patterns import BUILTIN_PATTERNS


class TestBuiltinPatterns:
    def test_email(self):
        assert BUILTIN_PATTERNS["email"].search("user@example.com")
        assert not BUILTIN_PATTERNS["email"].search("no email here")

    def test_jwt(self):
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        assert BUILTIN_PATTERNS["jwt"].search(jwt)
        assert not BUILTIN_PATTERNS["jwt"].search("not a jwt")

    def test_bearer(self):
        assert BUILTIN_PATTERNS["bearer_token"].search("Bearer abcdefghijklmnopqrstuvwxyz")
        assert not BUILTIN_PATTERNS["bearer_token"].search("no bearer here")

    def test_api_key(self):
        assert BUILTIN_PATTERNS["api_key_assignment"].search("api_key=sk_test_1234567890abcdef")

    def test_ipv4(self):
        assert BUILTIN_PATTERNS["ipv4"].search("192.168.1.100")
        assert not BUILTIN_PATTERNS["ipv4"].search("no ip here")
