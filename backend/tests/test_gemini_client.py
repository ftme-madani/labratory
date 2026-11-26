import pytest
import httpx
from unittest.mock import patch, MagicMock
from backend.app.services.gemini_client import GeminiClient, GeminiResult
from backend.app.config import Settings

def test_client_unconfigured_returns_none():
    """اگر کلید تنظیم نشده باشد یا سرویس غیرفعال باشد، باید سریعاً None بازگرداند و کرش نکند"""
    client = GeminiClient(api_key=None, enabled=True)
    res = client.generate_content("سلام")
    assert res is None

    client_disabled = GeminiClient(api_key="valid-key-123456", enabled=False)
    res2 = client_disabled.generate_content("سلام")
    assert res2 is None

def test_client_success_response_parsing():
    """دریافت پاسخ معتبر از Gemini API و استخراج صحیح متن"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "کاغذ تورنسل آبی در محیط اسیدی به رنگ سرخ درمی‌آید."}
                    ],
                    "role": "model"
                },
                "finishReason": "STOP"
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_response):
        client = GeminiClient(api_key="AIzaSyDummyKeyForTesting12345", model="gemini-1.5-flash", enabled=True)
        result = client.generate_content(
            prompt="چرا تورنسل آبی تغییر رنگ داد؟",
            system_instruction="تو معلم راهنمای علوم تجربی هستی."
        )

        assert result is not None
        assert isinstance(result, GeminiResult)
        assert result.success is True
        assert "سرخ" in result.text
        assert result.model == "gemini-1.5-flash"
        assert result.latency_ms >= 0

def test_client_timeout_graceful_fallback():
    """هنگام رخداد تایم‌اوت شبکه، برنامه نباید کرش کند و باید None برگرداند"""
    with patch("httpx.Client.post", side_effect=httpx.TimeoutException("Network timeout")):
        client = GeminiClient(api_key="AIzaSyDummyKeyForTesting12345", timeout_seconds=2.0, enabled=True)
        result = client.generate_content("پرسش آزمایشی")
        assert result is None

def test_client_rate_limit_or_auth_error_fallback():
    """هنگام بروز خطای 429 یا 401، کلاینت با متانت None برمی‌گرداند"""
    mock_err_response = MagicMock()
    mock_err_response.status_code = 429
    mock_err_response.text = '{"error": {"code": 429, "message": "Resource exhausted"}}'

    with patch("httpx.Client.post", return_value=mock_err_response):
        client = GeminiClient(api_key="AIzaSyDummyKeyForTesting12345", enabled=True)
        result = client.generate_content("پرسش آزمایشی")
        assert result is None

def test_effective_api_key_logic():
    """بررسی اولویت کلید و رد مقادیر پیش‌فرض ساختگی"""
    s1 = Settings(GEMINI_API_KEY="your-google-gemini-api-key-here", LLM_API_KEY=None)
    assert s1.effective_gemini_api_key is None

    s2 = Settings(GEMINI_API_KEY="", LLM_API_KEY="valid-backup-llm-key")
    assert s2.effective_gemini_api_key == "valid-backup-llm-key"

    s3 = Settings(GEMINI_API_KEY="real-gemini-key-12345")
    assert s3.effective_gemini_api_key == "real-gemini-key-12345"
