from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from .ai_tutor import PrivacyAnonymizer, PedagogicalPromptBuilder

logger = logging.getLogger("llm_adapter")

class BaseLLMAdapter(ABC):
    """
    رابط پایه آداپتور هوش مصنوعی برای توضیح آموزشی خطاهای آزمایشگاهی.
    مدل زبانی تحت هیچ شرایطی حق تعیین نتیجه آزمایش یا تولید داده غیرمستند را ندارد.
    """
    @abstractmethod
    def generate_explanation(self, hint_context: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def answer_question(self, question: str, experiment_context: Dict[str, Any]) -> str:
        pass

class OfflineRuleLLMAdapter(BaseLLMAdapter):
    """
    آداپتور آفلاین مبتنی بر قواعد و کتب درسی ملی.
    ۱۰۰٪ رایگان، بدون نیاز به اینترنت، با قطعیت کامل و بدون توهم (Zero-Hallucination).
    """
    def generate_explanation(self, hint_context: Dict[str, Any]) -> str:
        base_content = hint_context.get("raw_hint", "")
        level = hint_context.get("level", 1)
        source = hint_context.get("textbook_source", "")

        prefix = ""
        if level == 1:
            prefix = "🤔 پرسش برای تفکر: "
        elif level == 2:
            prefix = "💡 سرنخ آموزشی: "
        else:
            prefix = "📘 راهکار و توضیح علمی: "

        if source and level == 3:
            return f"{prefix}{base_content} (مرجع درسی: {source})"
        return f"{prefix}{base_content}"

    def answer_question(self, question: str, experiment_context: Dict[str, Any]) -> str:
        q = question.lower()
        exp_title = experiment_context.get("title", "آزمایش علوم")

        # پایگاه دانش آفلاین هوشمند بر اساس کلیدواژه‌های علمی کتب درسی
        if any(w in q for w in ["آبلیمو", "اسید", "سرخ", "قرمز", "لیتموس", "تورنسل"]):
            if "صابون" in q or "باز" in q:
                return "آب‌صابون ماده‌ای بازی است و شناساگر تورنسل را به رنگ آبی درمی‌آورد، در حالی که اسیدها آن را سرخ می‌کنند."
            return "آب‌لیمو خاصیت اسیدی دارد (pH < 7). اسیدها در مجاورت کاغذ تورنسل آبی، با تغییر ساختار شناساگر رنگ آن را سرخ می‌کنند."
        
        elif any(w in q for w in ["صابون", "باز", "قلیایی", "آبی"]):
            return "مواد بازی مانند آب‌صابون دارای pH بالای ۷ هستند، مزه تلخ و حالت لغزنده دارند و کاغذ تورنسل سرخ را به آبی تبدیل می‌کنند."

        elif any(w in q for w in ["اتصال کوتاه", "خطر"]):
            return "در اتصال کوتاه، سیم‌های مدار بدون وجود مصرف‌کننده (مانند لامپ) به هم وصل می‌شوند. طبق قانون اهم مقاومت صفر شده، جریان به شدت بالا می‌رود و به باتری آسیب می‌زند."

        elif any(w in q for w in ["اهم", "ولتاژ", "باتری", "جریان", "لامپ"]):
            return "طبق قانون اهم (V = I × R)، هر چه ولتاژ باتری بیشتر باشد، شدت جریان عبوری بیشتر شده و در نتیجه روشنایی لامپ افزایش می‌یابد."

        elif any(w in q for w in ["جوش‌شیرین", "جوش شیرین", "گاز", "حباب", "کف"]):
            return "در واکنش سرکه و جوش‌شیرین، گاز دی‌اکسید کربن (CO2) تولید می‌شود که باعث ایجاد کف و جوشش است. همچنین این واکنش گرماگیر بوده و ظرف سرد می‌شود."

        elif any(w in q for w in ["آونگ", "طول", "نخ", "جرم", "وزنه", "تناوب"]):
            return "دوره تناوب آونگ ساده فقط به طول نخ و شتاب گرانش بستگی دارد (T = 2π√(L/g))؛ بنابراین تغییر جرم وزنه تأثیری در زمان نوسان ندارد."

        elif any(w in q for w in ["کرفس", "گیاه", "آوند", "رنگی"]):
            return "آب رنگی از طریق آوندهای چوبی در ساقه به وسیله نیروی مویینگی و تبخیر سطحی از روزنه‌های برگ بالا می‌رود و فقط دسته‌های آوندی رنگی می‌شوند."

        elif any(w in q for w in ["چگالی", "روغن", "عسل", "شناور"]):
            return "مایعی که چگالی کمتری دارد (روغن با چگالی حدود ۰.۹۲) روی مایع متراکم‌تر (آب با چگالی ۱.۰ و عسل با چگالی ۱.۴) شناور می‌ماند."

        elif any(w in q for w in ["تصفیه", "صافی", "شن", "ماسه", "کربن"]):
            return "صافی شنی ذرات درشت و معلق را جدا می‌کند، اما میکروب‌ها و املاح محلول مانند نمک را از بین نمی‌برد؛ برای شرب باید ضدعفونی شود."

        return (
            f"در آزمایش «{exp_title}»، رفتار مواد بر پایه مفاهیم کتاب علوم تجربی هدایت می‌شود. "
            f"برای بررسی دقیق‌تر، می‌توانید ابزارها را روی میز آزمایشگاه ترکیب کنید و اثر آن را مشاهده فرمایید."
        )

class ExternalLLMAdapter(BaseLLMAdapter):
    """
    آداپتور اتصال به مدل‌های هوش مصنوعی (Google Gemini) در سمت سرور.
    ویژگی‌ها:
    - محافظت سخت‌گیرانه از حریم خصوصی (Privacy Anonymizer).
    - تفکیک قطعی سه سطح راهنمایی آموزشی (سقراطی، سرنخ، پاسخ کامل علمی).
    - بازگشت امن و خودکار به قوانین کتاب درسی در صورت بروز هرگونه قطعی یا محدودیت.
    """
    def __init__(self, api_key: Optional[str] = None, fallback_adapter: Optional[BaseLLMAdapter] = None):
        self.api_key = api_key
        self.fallback = fallback_adapter or OfflineRuleLLMAdapter()

    def _get_gemini_client(self):
        try:
            from backend.app.services.gemini_client import get_gemini_client, GeminiClient
            if self.api_key:
                return GeminiClient(api_key=self.api_key)
            return get_gemini_client()
        except Exception as exc:
            logger.warning(f"دسترسی به GeminiClient ممکن نشد: {exc}")
            return None

    def _call_external_service(self, sanitized_context: Dict[str, Any]) -> Optional[str]:
        client = self._get_gemini_client()
        if not client or not client.is_configured():
            return None

        prompt = PedagogicalPromptBuilder.build_hint_prompt(sanitized_context)
        system_instruction = PedagogicalPromptBuilder.SYSTEM_INSTRUCTION

        result = client.generate_content(
            prompt=prompt,
            system_instruction=system_instruction
        )
        if result and result.success and result.text.strip():
            return result.text.strip()
        return None

    def generate_explanation(self, hint_context: Dict[str, Any]) -> str:
        # ۱. ناشناس‌سازی کامل کانتکست جهت رعایت حریم خصوصی دانش‌آموز
        sanitized_context = PrivacyAnonymizer.sanitize_context(hint_context)

        try:
            # ۲. تلاش برای دریافت از سرویس خارجی با مدیریت کامل خطا
            external_text = self._call_external_service(sanitized_context)
            if external_text:
                return external_text

            # ۳. در صورت عدم وجود پاسخ معتبر یا عدم پیکربندی، فال‌بک فعال می‌شود
            return self.fallback.generate_explanation(hint_context)

        except Exception as exc:
            logger.warning(f"خطا در فراخوانی هوش مصنوعی: {exc}. فال‌بک به قوانین کتاب درسی.")
            return self.fallback.generate_explanation(hint_context)

    def answer_question(self, question: str, experiment_context: Dict[str, Any]) -> str:
        sanitized_context = PrivacyAnonymizer.sanitize_context(experiment_context)
        client = self._get_gemini_client()

        if not client or not client.is_configured():
            return self.fallback.answer_question(question, experiment_context)

        try:
            prompt = PedagogicalPromptBuilder.build_question_prompt(question, sanitized_context)
            system_instruction = PedagogicalPromptBuilder.QUESTION_SYSTEM_INSTRUCTION

            result = client.generate_content(
                prompt=prompt,
                system_instruction=system_instruction
            )

            if result and result.success and result.text.strip():
                return result.text.strip()

            return self.fallback.answer_question(question, experiment_context)
        except Exception as exc:
            logger.warning(f"خطا در پاسخ به سؤال هوش مصنوعی: {exc}")
            return self.fallback.answer_question(question, experiment_context)

    def generate_teacher_insights(self, frequent_errors: List[Dict[str, Any]]) -> str:
        """تفسیر هوشمند خطاهای پرتکرار کلاس برای ارائه تحلیل آموزشی به معلم"""
        client = self._get_gemini_client()
        if not client or not client.is_configured() or not frequent_errors:
            return (
                "بر اساس داده‌های کلاسی ثبت‌شده، توصیه می‌شود مفاهیم پیش‌نیاز هر آزمایش "
                "و تفاوت خصلت اسیدها، بازها و مواد خنثی پیش از شروع کار عملی با دانش‌آموزان مرور شود."
            )

        try:
            prompt = PedagogicalPromptBuilder.build_teacher_insights_prompt(frequent_errors)
            system_instruction = (
                "شما متخصص و مشاور ارشد برنامه‌ریزی درسی و آموزش علوم تجربی هستید. "
                "تحلیل شما باید کاربردی، دقیق و بر پایه روان‌شناسی یادگیری برای معلم باشد."
            )

            result = client.generate_content(
                prompt=prompt,
                system_instruction=system_instruction
            )
            if result and result.success and result.text.strip():
                return result.text.strip()
            return "مفاهیم اسیدی و بازی و نحوه استفاده از شناساگرها نیازمند بررسی مجدد در کلاس درس است."
        except Exception as exc:
            logger.warning(f"خطا در تولید بینش‌های معلم: {exc}")
            return "بررسی نتایج نشان می‌دهد مرور کارگاهی دستورالعمل‌ها به کاهش خطاها کمک شایانی خواهد کرد."
