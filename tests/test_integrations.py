"""Tests for Integration connectivity diagnostics and secret protection."""
import pytest
from utils.config import config, mask_secret
from database.database import test_db_connection as check_db_conn
from memory.hindsight_manager import memory_manager
from llm.llm_client import llm_client


def test_secret_masking():
    secret = "gsk_abcd1234efgh5678"
    masked = mask_secret(secret)
    assert secret not in masked
    assert "••••••••" in masked
    assert masked.startswith("gsk_")

    assert mask_secret(None) == "(not set)"
    assert mask_secret("") == "(not set)"


def test_database_connection_test_does_not_leak_secrets():
    # Test with invalid url
    config.database_url = "postgresql://user:super_secret_password@invalid.host:5432/db"
    ok, msg = check_db_conn()
    assert ok is False
    assert "super_secret_password" not in msg


def test_hindsight_connection_test_safe():
    ok, msg = memory_manager.test_connection()
    assert isinstance(ok, bool)
    assert isinstance(msg, str)


def test_llm_connection_test_safe():
    ok, msg = llm_client.test_connection()
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
