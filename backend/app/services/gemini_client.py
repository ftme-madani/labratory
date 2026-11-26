import httpx
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from ..config import settings

logger = logging.getLogger("gemini_client")

@dataclass
class GeminiResult:
    """ساختار خروجی استاندارد ارتباط با سرویس هوش مصنوعی Gemini"""
    success: bool
    text: str
    model: str
    is_fallback: bool = False
    error_message: Optional[str] = None
    latency_ms: float = 0.0

class GeminiClient:
    """
    کلاینت امن، تاب‌آور و مستقل سرور برای ارتباط با Google Gemini REST API.
    ویژگی‌ها:
    - استفاده مستقیم از httpx بدون نیاز به وابستگی‌های سنگین خارجی.
    - مدیریت دقیق Timeout و محافظت در برابر قطعی شبکه یا خطاهای 4xx/5xx.
    - عدم بروز اختلال در برنامه در صورت نبودن کلید یا در دسترس نبودن اینترنت (Fail-Safe).
    - رعایت حریم خصوصی و عدم ارسال متغیرهای حساس.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        enabled: Optional[bool] = None
    ):
        self.api_key = api_key if api_key is not None else settings.effective_gemini_api_key
        self.model = (model or settings.AI_MODEL or "gemini-1.5-flash").strip()
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else settings.AI_TIMEOUT_SECONDS
        self.enabled = enabled if enabled is not None else settings.AI_ENABLED

        # کنترل نرخ درخواست (حداقل فاصله بین دو درخواست همزمان برای جلوگیری از Rate Limit)
        self._last_request_time: float = 0.0
        self._min_interval: float = 0.3  # ثانیه

    def is_configured(self) -> bool:
        """بررسی آیا کلید و سرویس فعال و آماده پاسخ‌گویی است"""
        return bool(self.enabled and self.api_key and len(self.api_key) > 5)

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ) -> Optional[GeminiResult]:
        """
        ارسال همگام پرامپت به Google Gemini API با بازگشت امن در صورت شکست.
        اگر کلید تنظیم نشده یا خطایی رخ دهد، مقدار None بازگردانده می‌شود تا سیستم فال‌بک فعال شود.
        """
        if not self.is_configured():
            return None

        # کنترل نرخ درخواست (Throttle)
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)

        start_time = time.time()
        endpoint = f"{self.BASE_URL}/{self.model}:generateContent"
        params = {"key": self.api_key}

        # ساختار استاندارد Google Generative Language API
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature if temperature is not None else settings.AI_TEMPERATURE,
                "maxOutputTokens": max_output_tokens if max_output_tokens is not None else settings.AI_MAX_OUTPUT_TOKENS
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    endpoint,
                    params=params,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                self._last_request_time = time.time()
                latency_ms = round((time.time() - start_time) * 1000, 1)

                if response.status_code == 200:
                    data = response.json()
                    extracted_text = self._parse_candidates(data)
                    if extracted_text:
                        return GeminiResult(
                            success=True,
                            text=extracted_text,
                            model=self.model,
                            is_fallback=False,
                            latency_ms=latency_ms
                        )
                    else:
                        logger.warning("Gemini API 200 OK اما پاسخی در candidates یافت نشد.")
                        return None

                elif response.status_code == 429:
                    logger.warning("Gemini API Rate Limit (429) رخ داد. انتقال فوری به سیستم آفلاین.")
                    return None
                elif response.status_code in [400, 401, 403]:
                    logger.warning(f"خطای احراز هویت یا مدل Gemini API ({response.status_code}): {response.text[:200]}")
                    return None
                else:
                    logger.warning(f"خطای سرور Gemini API ({response.status_code}): {response.text[:200]}")
                    return None

        except httpx.TimeoutException:
            logger.warning(f"مهلت پاسخ‌گویی Gemini API ({self.timeout_seconds} ثانیه) به پایان رسید. انتقال خودکار به فال‌بک.")
            return None
        except httpx.RequestError as exc:
            logger.warning(f"خطای شبکه در ارتباط با Gemini API: {exc}. انتقال خودکار به فال‌بک.")
            return None
        except Exception as exc:
            logger.error(f"خطای غیرمنتظره در کلاینت Gemini: {exc}")
            return None

    async def generate_content_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ) -> Optional[GeminiResult]:
        """
        نسخه ناهمگام (Async) فراخوانی Gemini API با حفظ کامل منطق تاب‌آوری
        """
        if not self.is_configured():
            return None

        start_time = time.time()
        endpoint = f"{self.BASE_URL}/{self.model}:generateContent"
        params = {"key": self.api_key}

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature if temperature is not None else settings.AI_TEMPERATURE,
                "maxOutputTokens": max_output_tokens if max_output_tokens is not None else settings.AI_MAX_OUTPUT_TOKENS
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    endpoint,
                    params=params,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                latency_ms = round((time.time() - start_time) * 1000, 1)

                if response.status_code == 200:
                    data = response.json()
                    extracted_text = self._parse_candidates(data)
                    if extracted_text:
                        return GeminiResult(
                            success=True,
                            text=extracted_text,
                            model=self.model,
                            is_fallback=False,
                            latency_ms=latency_ms
                        )
                return None
        except Exception as exc:
            logger.warning(f"خطا در Async Gemini API: {exc}")
            return None

    def _parse_candidates(self, data: Dict[str, Any]) -> Optional[str]:
        """استخراج تمیز متن خروجی از ساختار JSON مدل Gemini"""
        candidates = data.get("candidates", [])
        if not candidates:
            return None

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return None

        text_parts = [p.get("text", "") for p in parts if "text" in p]
        full_text = "".join(text_parts).strip()
        return full_text if full_text else None

# سینگلتون پیش‌فرض کلاینت برای استفاده در سرتاسر بک‌اند
_global_gemini_client: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    """دریافت نمونه سراسری کلاینت هوش مصنوعی Gemini"""
    global _global_gemini_client
    if _global_gemini_client is None:
        _global_gemini_client = GeminiClient()
    return _global_gemini_client
