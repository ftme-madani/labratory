import hashlib
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("ai_tutor")

class PrivacyAnonymizer:
    """
    لایه محافظت از حریم خصوصی دانش‌آموزان و معلمان.
    تضمین عدم ارسال هرگونه مشخصات هویتی (PII) به سرویس‌های هوش مصنوعی خارجی.
    """

    FORBIDDEN_KEYS = {
        "name", "full_name", "first_name", "last_name",
        "email", "phone", "mobile", "school", "school_name",
        "password", "hashed_password", "national_id"
    }

    @classmethod
    def anonymize_id(cls, user_id: Any) -> str:
        """تبدیل شناسه به هش ناشناس و برگشت‌ناپذیر"""
        if not user_id:
            return "std-anon-0000"
        digest = hashlib.sha256(f"salt_privacy_{user_id}".encode()).hexdigest()[:8]
        return f"std-anon-{digest}"

    @classmethod
    def sanitize_context(cls, raw_context: Dict[str, Any]) -> Dict[str, Any]:
        """پالایش کامل دیکشنری ورودی از هرگونه اطلاعات هویتی و فردی"""
        clean_ctx: Dict[str, Any] = {}
        for key, value in raw_context.items():
            if key.lower() in cls.FORBIDDEN_KEYS:
                continue
            if isinstance(value, dict):
                clean_ctx[key] = cls.sanitize_context(value)
            elif isinstance(value, list):
                clean_ctx[key] = [
                    cls.sanitize_context(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                clean_ctx[key] = value

        if "user_id" in raw_context:
            clean_ctx["anonymous_student_id"] = cls.anonymize_id(raw_context["user_id"])
            clean_ctx.pop("user_id", None)

        return clean_ctx

class PedagogicalPromptBuilder:
    """
    سازنده پرامپت‌های مهندسی‌شده آموزشی منطبق بر اصول روان‌شناسی یادگیری و کتب درسی دوره متوسطه.
    """

    SYSTEM_INSTRUCTION = (
        "شما «دستیار هوشمند آموزشی آزمایشگاه مجازی علوم تجربی» برای دانش‌آموزان دوره متوسطه ایران هستید.\n"
        "رسالت‌های اصلی شما:\n"
        "۱. لحن: صمیمانه، تشویق‌کننده، محترمانه، به زبان فارسی ساده و روان متناسب با سن نوجوان.\n"
        "۲. صحت علمی قطعی: پاسخ شما صرفاً بر پایه پایگاه دانش علمی تأییدشده کتاب درسی استوار است. هرگز نتیجه آزمایش را حدس نزنید، جعل نکنید و تغییر ندهید.\n"
        "۳. پایبندی به سطوح سه‌گانه راهنمایی پداگوژیک (Scaffolding):\n"
        "   - سطح ۱ (سقراطی/تفکری): فقط یک پرسش هدایت‌کننده مطرح کنید تا دانش‌آموز خودش فکر کند. ابزار درست یا جواب نهایی را لو ندهید.\n"
        "   - سطح ۲ (سرنخ مفهومی): مفهوم علمی و خصلت مواد را یادآوری کنید، بدون ارائه پاسخ مستقیم.\n"
        "   - سطح ۳ (تشریح کامل و علمی): پاسخ صحیح، دلیل علمی دقیق، نام ماده/ابزار مناسب و راهکار اصلاحی را به طور کامل توضیح دهید.\n"
        "۴. صداقت در ندانستن: اگر اطلاعات موجود کافی نیست، صریحاً بگویید اطلاعات کافی برای نتیجه‌گیری قطعی وجود ندارد و فرضیه‌سازی نکنید."
    )

    QUESTION_SYSTEM_INSTRUCTION = (
        "شما «دستیار علمی و صوتی آزمایشگاه مجازی علوم تجربی» هستید.\n"
        "رسالت شما برای پاسخ به پرسش‌های علمی دانش‌آموز:\n"
        "۱. به پرسش دانش‌آموز پاسخ علمی مستقیم، دقیق، کامل و شیوا بدهید. هرگز پاسخ را با یک سؤال دیگر عوض نکنید، طفره نروید و از گفتن اینکه «ناخوانا است» پرهیز کنید.\n"
        "۲. علت علمی پدیده (مانند اسیدی بودن، یون هیدرونیوم، قانون اهم، رابطه ولتاژ و جریان، چگالی و...) را به زبان فارسی ساده، جذاب و روشن در ۲ الی ۴ جمله تشریح کنید.\n"
        "۳. لحن شما صمیمی، تشویق‌کننده، پرانرژی و متناسب با آموزش علوم دوره متوسطه باشد."
    )

    @classmethod
    def build_hint_prompt(cls, context: Dict[str, Any]) -> str:
        level = context.get("level", 1)
        raw_hint = context.get("raw_hint", "")
        error_code = context.get("error_code", "")
        experiment_title = context.get("experiment_title", "آزمایش علوم تجربی")
        step_index = context.get("step_index", 1)
        action_summary = context.get("action_summary", "کنش آزمایشگاهی")
        scientific_rationale = context.get("scientific_rationale", "")

        level_titles = {
            1: "سطح ۱: سؤال هدایت‌کننده (سقراطی) - بدون ارائه پاسخ مستقیم",
            2: "سطح ۲: سرنخ آموزشی و مفهومی - یادآوری خصلت ماده بدون لو دادن مستقیم جواب",
            3: "سطح ۳: توضیح کامل علمی به همراه پاسخ صحیح و دلیل آن"
        }

        prompt = (
            f"عنوان آزمایش: {experiment_title}\n"
            f"مرحله فعلی آزمایش: گام {step_index}\n"
            f"کنش انجام‌شده توسط دانش‌آموز: {action_summary}\n"
            f"کد خطای تشخیص‌داده‌شده توسط موتور علمی: {error_code}\n"
            f"حقیقت علمی کتاب درسی: {scientific_rationale}\n"
            f"هسته پیام درسی مصوب: {raw_hint}\n\n"
            f"وظیفه شما:\n"
            f"راهنمایی را دقیقاً برای «{level_titles.get(level, 'سطح ' + str(level))}» بازآفرینی کنید.\n"
            f"پاسخ باید فارسی، شیوا، پرانرژی و متناسب با سن دانش‌آموز باشد و از ۱ الی ۳ جمله تجاوز نکند."
        )
        return prompt

    @classmethod
    def build_question_prompt(cls, question: str, experiment_context: Dict[str, Any]) -> str:
        exp_title = experiment_context.get("title", "آزمایشگاه علوم تجربی")
        current_step = experiment_context.get("current_step", 1)
        observations = experiment_context.get("observations", [])
        obs_text = " | ".join(observations) if observations else "هنوز مشاهده‌ای ثبت نشده است."

        prompt = (
            f"آزمایش در حال انجام: {exp_title} (گام {current_step})\n"
            f"مشاهدات معتبر ثبت‌شده تا این لحظه: {obs_text}\n\n"
            f"پرسش دانش‌آموز:\n«{question}»\n\n"
            f"نکات مهم برای پاسخ:\n"
            f"۱. ممکن است پرسش از طریق تبدیل گفتار به متن (Voice) ثبت شده و به زبان گفتاری یا کوتاه باشد. منظور او را متناسب با آزمایش جاری درک کنید و هرگز نگویید ناخوانا است یا متوجه نشدید.\n"
            f"۲. پاسخ شما باید کاملاً منطبق بر مفاهیم علوم تجربی دوره متوسطه، بدون اصطلاحات پیچیده دانشگاهی، آموزنده، مهربان و صمیمانه باشد."
        )
        return prompt

    @classmethod
    def build_teacher_insights_prompt(cls, frequent_errors: List[Dict[str, Any]]) -> str:
        items_text = []
        for err in frequent_errors:
            items_text.append(
                f"- خطای «{err.get('error_title', err.get('error_code'))}» در آزمایش «{err.get('experiment_title')}»: {err.get('occurrence_count')} بار تکرار شده است. (مفهوم: {err.get('scientific_concept', 'نامشخص')})"
            )
        summary = "\n".join(items_text)

        prompt = (
            f"آمار خطاهای پرتکرار کلاس در پایگاه داده سامانه:\n{summary}\n\n"
            f"به عنوان مشاور ارشد پداگوژی و آموزش علوم:\n"
            f"۱. ریشه بدفهمی مشترک دانش‌آموزان در این مباحث را در ۲ الی ۳ بند تحلیلی تشریح کنید.\n"
            f"۲. برای دبیر کلاس، ۳ فعالیت یا مثال ملموس کلاسی برای رفع قطعی این بدفهمی‌ها پیشنهاد دهید."
        )
        return prompt
