import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models.user import User
from .models.experiment import Experiment
from .models.attempt import ExperimentAttempt, StepActionLog, HintUsage
from .security import get_password_hash

def seed_database():
    """
    راه‌اندازی ساختار دیتابیس و کاشت داده‌های اولیه منطبق بر کتب درسی رسمی ایران
    """
    print("[1/4] ایجاد جداول پایگاه داده در SQLite/PostgreSQL...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print("[2/4] ایجاد حساب‌های کاربری پیش‌فرض (معلم و دانش‌آموز)...")
        # کاربر معلم
        teacher = db.query(User).filter(User.email == "m.moradi@edu.ir").first()
        if not teacher:
            teacher = User(
                username="moradi_teacher",
                email="m.moradi@edu.ir",
                hashed_password=get_password_hash("Teacher123456"),
                full_name="استاد محمد مرادی",
                role="teacher",
                grade="متوسطه اول و دوم",
                school_name="دبیرستان نمونه دولتی البرز"
            )
            db.add(teacher)

        # کاربر دانش‌آموز
        student = db.query(User).filter(User.email == "alireza@school.ir").first()
        if not student:
            student = User(
                username="alireza_student",
                email="alireza@school.ir",
                hashed_password=get_password_hash("Student123456"),
                full_name="علیرضا محمدی",
                role="student",
                grade="هشتم",
                school_name="دبیرستان شهید بهشتی"
            )
            db.add(student)

        db.commit()
        db.refresh(teacher)
        db.refresh(student)

        print("[3/4] کاشت آزمایش‌های سه‌گانه معتبر برنامه درسی علوم تجربی...")
        experiments_data = [
            {
                "slug": "acid-base-indicators",
                "title": "شناسایی اسیدها و بازها با معرف‌های رنگی",
                "subject": "شیمی",
                "grade": "هشتم",
                "difficulty": "آسان",
                "duration_minutes": 15,
                "status": "PUBLISHED",
                "summary": "بررسی تغییر رنگ کاغذ لیتموس (تورنسل) آبی و قرمز در محیط‌های اسیدی و بازی و اندازه‌گیری pH",
                "thumbnail_type": "flask",
                "textbook_source": {
                    "book": "علوم تجربی پایه هشتم",
                    "grade": "هشتم",
                    "chapter": "مخلوط و جداسازی مواد",
                    "chapterNumber": 1,
                    "page": 6,
                    "curriculumCode": "SCI-8-CH1-P6"
                },
                "objectives": [
                    "آشنایی با شناساگرهای اسید و باز (کاغذ لیتموس آبی و قرمز)",
                    "تشخیص خاصیت اسیدی آبلیمو و خاصیت بازی جوش شیرین",
                    "درک مفهوم مقیاس pH و ارتباط آن با یون‌های H+ و OH-"
                ],
                "safety_notes": [
                    "از چشیدن یا لمس مستقیم مواد شیمیایی نامشخص خودداری کنید.",
                    "در صورت تماس اسید با دست، بلافاصله موضع را با آب فراوان بشویید.",
                    "معرف‌ها را پس از استفاده در جای خشک و دور از نور مستقیم نگهداری نمایید."
                ],
                "available_tools": [
                    {"id": "beaker-lemon", "name": "بشر آبلیمو (اسید)", "type": "chemical", "category": "اسید", "icon": "flask", "properties": {"pH": 2.5, "state": "liquid"}},
                    {"id": "beaker-soda", "name": "بشر محلول جوش شیرین (باز)", "type": "chemical", "category": "باز", "icon": "flask", "properties": {"pH": 9.0, "state": "liquid"}},
                    {"id": "beaker-water", "name": "بشر آب خالص (خنثی)", "type": "chemical", "category": "خنثی", "icon": "flask", "properties": {"pH": 7.0, "state": "liquid"}},
                    {"id": "litmus-blue", "name": "کاغذ لیتموس آبی", "type": "tool", "category": "معرف", "icon": "test-tube"},
                    {"id": "litmus-red", "name": "کاغذ لیتموس قرمز", "type": "tool", "category": "معرف", "icon": "test-tube"},
                    {"id": "ph-meter", "name": "دستگاه pH متر دیجیتال", "type": "measurement", "category": "ابزار اندازه‌گیری", "icon": "gauge"}
                ],
                "steps_config": [
                    {"index": 1, "title": "آزمون کاغذ لیتموس آبی در اسید", "description": "کاغذ لیتموس آبی را درون ظرف آبلیمو قرار داده و تغییر رنگ را مشاهده کنید.", "hint": "اسیدها لیتموس آبی را به رنگ قرمز تغییر می‌دهند."},
                    {"index": 2, "title": "آزمون کاغذ لیتموس قرمز در باز", "description": "کاغذ لیتموس قرمز را درون ظرف محلول جوش شیرین قرار دهید.", "hint": "بازها لیتموس قرمز را به رنگ آبی تغییر می‌دهند."},
                    {"index": 3, "title": "اندازه‌گیری دقیق pH با حسگر دیجیتال", "description": "پروب pH متر را درون هر یک از ظروف برده و مقدار عددی را ثبت کنید.", "hint": "مقادیر کمتر از ۷ اسیدی و بیشتر از ۷ بازی هستند."}
                ]
            },
            {
                "slug": "mixture-separation-sand-salt",
                "title": "جداسازی مخلوط ناهمگن ماسه، نمک و آب",
                "subject": "شیمی",
                "grade": "هشتم",
                "difficulty": "متوسط",
                "duration_minutes": 20,
                "status": "PUBLISHED",
                "summary": "جداسازی فیزیکی اجزای یک مخلوط ناهمگن با استفاده از روش‌های انحلال در آب، صاف کردن با قیف و تبخیر",
                "thumbnail_type": "filter",
                "textbook_source": {
                    "book": "علوم تجربی پایه هشتم",
                    "grade": "هشتم",
                    "chapter": "تغییرهای شیمیایی در خدمت زندگی",
                    "chapterNumber": 2,
                    "page": 16,
                    "curriculumCode": "SCI-8-CH2-P16"
                },
                "objectives": [
                    "تشخیص تفاوت انحلال‌پذیری نمک و ماسه در آب",
                    "کار با قیف و کاغذ صافی برای جداسازی رسوب نامحلول",
                    "استفاده از حرارت برای تبخیر حلال و بازیابی بلورهای نمک"
                ],
                "safety_notes": [
                    "هنگام کار با چراغ بونزن از عینک ایمنی استفاده کنید.",
                    "ظرف شیشه‌ای داغ را بلافاصله روی سطح سرد قرار ندهید تا نشکند.",
                    "پیش از خنک شدن کامل لوله یا بشر، به آن دست نزنید."
                ],
                "available_tools": [
                    {"id": "mixture-beaker", "name": "بشر حاوی مخلوط ماسه و نمک", "type": "chemical", "category": "مخلوط", "icon": "flask"},
                    {"id": "water-bottle", "name": "آب‌فشان (پیست) آب مقطر", "type": "chemical", "category": "حلال", "icon": "droplet"},
                    {"id": "stirrer", "name": "همزن شیشه‌ای", "type": "tool", "category": "ابزار", "icon": "sparkles"},
                    {"id": "filter-funnel", "name": "قیف همراه با کاغذ صافی", "type": "tool", "category": "جداسازی", "icon": "filter"},
                    {"id": "bunsen-burner", "name": "چراغ بونزن و سه‌پایه", "type": "tool", "category": "حرارتی", "icon": "flame"},
                    {"id": "evaporating-dish", "name": "کپسول چینی تبخیر", "type": "tool", "category": "ظروف", "icon": "box"}
                ],
                "steps_config": [
                    {"index": 1, "title": "انحلال نمک در آب", "description": "به بشر حاوی ماسه و نمک آب مقطر اضافه کرده و با همزن شیشه‌ای هم بزنید تا نمک کاملاً حل شود.", "hint": "نمک خوراکی در آب محلول است اما ماسه حل نمی‌شود."},
                    {"index": 2, "title": "صاف کردن مخلوط با قیف", "description": "محتویات بشر را از صافی عبور دهید تا ماسه روی کاغذ صافی باقی بماند و محلول آب‌نمک خارج شود.", "hint": "ماسه به دلیل اندازه ذرات بزرگتر از منافذ صافی عبور نمی‌کند."},
                    {"index": 3, "title": "تبخیر آب و بلورشدن نمک", "description": "محلول شفاف آب‌نمک را در کپسول چینی ریخته و با چراغ بونزن حرارت دهید تا بلورهای سفید نمک پدیدار شوند.", "hint": "آب در ۱۰۰ درجه سانتی‌گراد تبخیر شده و نمک با نقطه جوش بالا باقی می‌ماند."}
                ]
            },
            {
                "slug": "simple-electric-circuit-ohm",
                "title": "بررسی مدار الکتریکی ساده و قانون اهم",
                "subject": "فیزیک",
                "grade": "نهم",
                "difficulty": "متوسط",
                "duration_minutes": 20,
                "status": "PUBLISHED",
                "summary": "بستن مدار الکتریکی با منبع ولتاژ، کلید، لامپ و مقاومت متغیر و بررسی رابطه شدت جریان با ولتاژ",
                "thumbnail_type": "zap",
                "textbook_source": {
                    "book": "علوم تجربی پایه نهم",
                    "grade": "نهم",
                    "chapter": "الکتریسیته",
                    "chapterNumber": 9,
                    "page": 98,
                    "curriculumCode": "SCI-9-CH9-P98"
                },
                "objectives": [
                    "درک مفهوم مدار بسته و مدار باز",
                    "بررسی قانون اهم (V = I * R)",
                    "مشاهده اثر اتصال کوتاه و اقدامات ایمنی آن"
                ],
                "safety_notes": [
                    "هیچ‌گاه دو سر باتری را مستقیماً با سیم بدون مصرف‌کننده متصل نکنید (اتصال کوتاه).",
                    "پیش از هرگونه تغییر در اتصالات مدار، کلید را در وضعیت قطع قرار دهید."
                ],
                "available_tools": [
                    {"id": "battery-pack", "name": "باتری قلمی ۱.۵ ولت (قابل تنظیم تا ۶ ولت)", "type": "tool", "category": "منبع تغذیه", "icon": "zap"},
                    {"id": "light-bulb", "name": "لامپ کوچک رشته‌ای (مصرف‌کننده)", "type": "tool", "category": "بار الکتریکی", "icon": "lightbulb"},
                    {"id": "switch", "name": "کلید قطع و وصل تک‌پل", "type": "tool", "category": "کنترل مدار", "icon": "toggle-left"},
                    {"id": "connecting-wires", "name": "سیم‌های رابط آزمایشگاهی", "type": "tool", "category": "اتصالات", "icon": "git-commit"},
                    {"id": "voltmeter", "name": "ولس‌متر دیجیتال", "type": "measurement", "category": "اندازه‌گیری", "icon": "gauge"},
                    {"id": "ammeter", "name": "آمپرمتر دیجیتال", "type": "measurement", "category": "اندازه‌گیری", "icon": "gauge"}
                ],
                "steps_config": [
                    {"index": 1, "title": "قرار دادن قطعات روی برد مدار", "description": "باتری، کلید و لامپ را روی میز آزمایشگاه قرار دهید.", "hint": "یک مدار کامل به منبع تغذیه، سیم رابط، کلید و مصرف‌کننده نیاز دارد."},
                    {"index": 2, "title": "برقراری اتصالات سیم‌کشی", "description": "سیم‌ها را از باتری به کلید و سپس به لامپ متصل کرده و مدار را ببندید.", "hint": "جریان الکتریکی تنها در یک حلقه بسته و متصل برقرار می‌شود."},
                    {"index": 3, "title": "بستن کلید و اندازه‌گیری جریان و روشنایی", "description": "کلید را در حالت وصل قرار دهید و روشن شدن لامپ و شدت جریان را مشاهده نمایید.", "hint": "طبق قانون اهم با افزایش ولتاژ، شدت جریان مدار افزایش می‌یابد."}
                ]
            },
            {
                "slug": "vinegar-baking-soda-reaction",
                "title": "واکنش سرکه و جوش‌شیرین و تولید گاز",
                "subject": "شیمی",
                "grade": "هشتم",
                "difficulty": "آسان",
                "duration_minutes": 15,
                "status": "PUBLISHED",
                "summary": "بررسی واکنش شیمیایی اسید استیک با بی‌کربنات سدیم، مشاهده تولید گاز کربن دی‌اکسید، فوران کف و بررسی استوکیومتری",
                "thumbnail_type": "flask",
                "textbook_source": {
                    "book": "علوم تجربی پایه هشتم",
                    "grade": "هشتم",
                    "chapter": "تغییرهای شیمیایی در خدمت زندگی",
                    "chapterNumber": 2,
                    "page": 12,
                    "curriculumCode": "SCI-8-CH2-P12"
                },
                "objectives": [
                    "آشنایی با واکنش‌های شیمیایی گرماگیر",
                    "مشاهده تولید گاز CO2 و فوران کف",
                    "درک مفهوم واکنش‌دهنده محدودکننده و رابطه استوکیومتری"
                ],
                "safety_notes": [
                    "از پاشیدن سرکه به چشم خودداری کنید.",
                    "در صورت تماس با پوست دست را با آب بشویید."
                ],
                "available_tools": [
                    {"id": "beaker_glass", "name": "لیوان آزمایشگاهی (بشر ۲۵۰ml)", "type": "tool", "category": "ظروف", "icon": "beaker"},
                    {"id": "bottle_vinegar", "name": "بطری سرکه سفید (اسید استیک ۵٪)", "type": "chemical", "category": "اسید", "icon": "flask"},
                    {"id": "jar_baking_soda", "name": "ظرف پودر جوش‌شیرین (بی‌کربنات سدیم)", "type": "chemical", "category": "باز", "icon": "sparkles"},
                    {"id": "spatula", "name": "اسپاتول (قاشقک آزمایشگاهی)", "type": "tool", "category": "ابزار", "icon": "sparkles"}
                ],
                "steps_config": [
                    {"index": 1, "title": "استقرار لیوان آزمایشگاهی", "description": "لیوان آزمایشگاهی شفاف را از قفسه به میز کار اضافه کنید.", "hint": "واکنش درون لیوان انجام می‌گیرد."},
                    {"index": 2, "title": "ریختن سرکه در لیوان", "description": "سرکه حاوی اسید استیک را به مقدار دلخواه درون لیوان بریزید.", "hint": "سرکه فاز مایع اسیدی واکنش است."},
                    {"index": 3, "title": "افزودن جوش‌شیرین به سرکه", "description": "پودر جوش‌شیرین را با اسپاتول به سرکه اضافه کنید.", "hint": "ترکیب اسید استیک و بی‌کربنات سدیم گاز CO2 آزاد می‌کند."},
                    {"index": 4, "title": "مشاهده فوران کف و تحلیل علمی", "description": "پدیده جوشش سریع، خروج حباب‌های CO2 و افت اندک دما را بررسی کنید.", "hint": "معادله: CH3COOH + NaHCO3 -> CH3COONa + H2O + CO2"}
                ]
            },
            {
                "slug": "simple-pendulum-motion",
                "title": "بررسی حرکت آونگ ساده و قانون دوره تناوب",
                "subject": "فیزیک",
                "grade": "نهم",
                "difficulty": "متوسط",
                "duration_minutes": 20,
                "status": "PUBLISHED",
                "summary": "بررسی حرکت نوسانی هماهنگ ساده، آزمون رابطه طول نخ با زمان تناوب و اثبات استقلال دوره تناوب از جرم وزنه در زوایای کوچک",
                "thumbnail_type": "zap",
                "textbook_source": {
                    "book": "علوم تجربی پایه نهم",
                    "grade": "نهم",
                    "chapter": "حرکت چیست؟",
                    "chapterNumber": 4,
                    "page": 45,
                    "curriculumCode": "SCI-9-CH4-P45"
                },
                "objectives": [
                    "بررسی رابطه دوره تناوب T با رادیکال طول نخ L",
                    "مشاهده تقریب زاویه کوچک (زیر ۱۵ درجه)",
                    "اثبات تجربی استقلال زمان تناوب از جرم وزنه"
                ],
                "safety_notes": [
                    "از رها کردن وزنه در زوایای بزرگ خودداری کنید تا از ضربه به پایه جلوگیری شود."
                ],
                "available_tools": [
                    {"id": "pendulum_stand", "name": "پایه نگهدارنده فلزی و گیره", "type": "tool", "category": "نگهدارنده", "icon": "box"},
                    {"id": "pendulum_string", "name": "نخ آزمایشگاهی با طول قابل تنظیم", "type": "tool", "category": "اتصالات", "icon": "git-commit"},
                    {"id": "pendulum_bob", "name": "وزنه فلزی کروی با جرم قابل تنظیم", "type": "tool", "category": "بار مکانیکی", "icon": "circle"},
                    {"id": "stopwatch", "name": "زمان‌سنج دیجیتال (کرونومتر)", "type": "measurement", "category": "اندازه‌گیری", "icon": "gauge"}
                ],
                "steps_config": [
                    {"index": 1, "title": "تنظیم و اتصال نخ به پایه", "description": "نخ را به گیره پایه نگهدارنده محکم کنید.", "hint": "طول نخ متغیر اصلی در دوره تناوب است."},
                    {"index": 2, "title": "اتصال وزنه به نخ", "description": "وزنه کروی را به انتهای نخ ببندید.", "hint": "در زوایای کوچک جرم وزنه بر دوره تناوب بی‌اثر است."},
                    {"index": 3, "title": "انحراف با زاویه کوچک", "description": "وزنه را حداکثر تا ۱۰ الی ۱۵ درجه از وضعیت تعادل منحرف سازید.", "hint": "تقریب زاویه کوچک برای حفظ فرمول خطی الزامی است."},
                    {"index": 4, "title": "رهاسازی و زمان‌گیری نوسان", "description": "زمان ۱۰ نوسان کامل را با زمان‌سنج ثبت کرده و دوره تناوب T را محاسبه نمایید.", "hint": "فرمول: T = 2π√(L/g)"}
                ]
            },
            {
                "slug": "plant-water-transport-celery",
                "title": "انتقال آب در گیاه و هدایت در آوندهای چوبی",
                "subject": "زیست‌شناسی",
                "grade": "هفتم",
                "difficulty": "آسان",
                "duration_minutes": 15,
                "status": "PUBLISHED",
                "summary": "مشاهده ماکروسکوپی و میکروسکوپی صعود شیره خام در آوندهای چوبی ساقه کرفس با ردیاب رنگ خوراکی و کشش تعرقی",
                "thumbnail_type": "filter",
                "textbook_source": {
                    "book": "علوم تجربی پایه هفتم",
                    "grade": "هفتم",
                    "chapter": "سفره سلامت (انتقال مواد در گیاهان)",
                    "chapterNumber": 12,
                    "page": 104,
                    "curriculumCode": "SCI-7-CH12-P104"
                },
                "objectives": [
                    "شناسایی بافت آوند چوبی (Xylem) در ساقه",
                    "درک نقش مکش تعرقی روزنه‌های برگ در صعود آب",
                    "مشاهده تغییر رنگ در رگبرگ‌ها با گذر زمان فشرده"
                ],
                "safety_notes": [
                    "مراقب لکه شدن لباس یا پوست با رنگ خوراکی باشید."
                ],
                "available_tools": [
                    {"id": "glass_cup", "name": "لیوان شفاف آزمایشگاهی", "type": "tool", "category": "ظروف", "icon": "beaker"},
                    {"id": "water_pitcher", "name": "پارچ آب مقطر", "type": "chemical", "category": "حلال", "icon": "droplet"},
                    {"id": "food_coloring", "name": "قطره‌چکان رنگ خوراکی (سرخ/آبی)", "type": "chemical", "category": "معرف", "icon": "droplets"},
                    {"id": "celery_stalk", "name": "ساقه تازه کرفس همراه با برگ", "type": "tool", "category": "نمونه زیستی", "icon": "sprout"}
                ],
                "steps_config": [
                    {"index": 1, "title": "ریختن آب در لیوان شفاف", "description": "لیوان را با آب مقطر تا نیمه پر کنید.", "hint": "آب به عنوان مایع حامل و شیره خام عمل می‌کند."},
                    {"index": 2, "title": "افزودن قطرات رنگ خوراکی", "description": "چند قطره رنگ خوراکی درون آب بریزید تا محلول یکنواخت رنگی شود.", "hint": "رنگ خوراکی نقش ردیاب فیزیکی در آوندها را دارد."},
                    {"index": 3, "title": "قرار دادن ساقه کرفس در آب", "description": "ساقه تازه کرفس را با مقطع تازه درون آب رنگی بگذارید.", "hint": "انتهای آوندها باید در تماس مستقیم با آب باشد."},
                    {"index": 4, "title": "شبیه‌سازی گذر زمان فشرده", "description": "روند صعود آب در فواصل زمانی ۱ تا ۲۴ ساعت را رصد نمایید.", "hint": "این شبیه‌سازی گذر زمان واقعی را به صورت فشرده نمایش می‌دهد."},
                    {"index": 5, "title": "بررسی آوندها و رگبرگ‌ها", "description": "برش عرضی ساقه و رنگین شدن رگبرگ‌ها به دلیل تعرق را مشاهده کنید.", "hint": "کشش تعرقی ناشی از تبخیر آب از روزنه‌ها موتور محرک صعود است."}
                ]
            },
            {
                "slug": "liquid-density-column",
                "title": "بررسی چگالی و لایه‌بندی مایعات (ستون چگالی)",
                "subject": "شیمی",
                "grade": "هفتم",
                "difficulty": "متوسط",
                "duration_minutes": 20,
                "status": "PUBLISHED",
                "summary": "ایجاد ستون سه‌لایه از عسل، آب و روغن مایع بر اساس اختلاف چگالی و پدیده عدم امتزاج مایعات",
                "thumbnail_type": "flask",
                "textbook_source": {
                    "book": "علوم تجربی پایه هفتم",
                    "grade": "هفتم",
                    "chapter": "اندازه‌گیری در علوم و ابزارهای آن",
                    "chapterNumber": 2,
                    "page": 16,
                    "curriculumCode": "SCI-7-CH2-P16"
                },
                "objectives": [
                    "درک مفهوم فرمول چگالی ρ = m / V",
                    "بررسی شرط شناوری و ته‌نشینی مایعات بر پایه چگالی",
                    "تشخیص نقش امتزاج‌ناپذیری در ثبات فازهای مجزا"
                ],
                "safety_notes": [
                    "ظروف شیشه‌ای را با احتیاط جابه‌جا کنید تا نشکنند."
                ],
                "available_tools": [
                    {"id": "measuring_cylinder", "name": "استوانه مدرج شفاف ۱۰۰ میلی‌لیتر", "type": "tool", "category": "اندازه‌گیری", "icon": "gauge"},
                    {"id": "flask_honey", "name": "ظرف عسل طبیعی (چگالی ۱.۴۲)", "type": "chemical", "category": "مایع چگال", "icon": "flask"},
                    {"id": "flask_water", "name": "ظرف آب مقطر رنگی (چگالی ۱.۰۰)", "type": "chemical", "category": "مایع خنثی", "icon": "flask"},
                    {"id": "flask_oil", "name": "ظرف روغن مایع گیاهی (چگالی ۰.۹۱)", "type": "chemical", "category": "مایع سبک", "icon": "flask"}
                ],
                "steps_config": [
                    {"index": 1, "title": "استقرار استوانه مدرج", "description": "استوانه مدرج شفاف را روی میز کار قرار دهید.", "hint": "استوانه مدرج امکان اندازه‌گیری حجم هر لایه را فراهم می‌کند."},
                    {"index": 2, "title": "ریختن عسل طبیعی", "description": "عسل با بالاترین چگالی را در کف استوانه بریزید.", "hint": "عسل با چگالی ۱.۴۲ g/cm³ در پایین‌ترین لایه می‌نشیند."},
                    {"index": 3, "title": "افزودن آرام آب مقطر", "description": "آب را به آرامی از دیواره استوانه روی عسل اضافه کنید.", "hint": "چگالی آب ۱.۰۰ g/cm³ است و روی عسل قرار می‌گیرد."},
                    {"index": 4, "title": "افزودن روغن مایع", "description": "روغن گیاهی را به لایه رویی اضافه نمایید.", "hint": "روغن با چگالی ۰.۹۱ g/cm³ روی آب شناور می‌ماند."},
                    {"index": 5, "title": "مشاهده لایه‌ها و ثبت علمی", "description": "مرز ۳ فاز مجزا، منیسک و تعادل هیدرواستاتیک را مشاهده کنید.", "hint": "امتزاج‌ناپذیری روغن و آب مانع مخلوط شدن لایه‌ها می‌شود."}
                ]
            },
            {
                "slug": "water-filtration-column",
                "title": "ساخت صافی چندلایه آب و تصفیه فیزیکی",
                "subject": "شیمی",
                "grade": "هفتم",
                "difficulty": "متوسط",
                "duration_minutes": 20,
                "status": "PUBLISHED",
                "summary": "جداسازی فیزیکی ذرات معلق آب گل‌آلود با طراحی صافی مطبق از پنبه، ماسه ریز و شن درشت و مقایسه شفافیت آب",
                "thumbnail_type": "filter",
                "textbook_source": {
                    "book": "علوم تجربی پایه هفتم",
                    "grade": "هفتم",
                    "chapter": "اتم‌ها، الفبای مواد و مخلوط‌ها",
                    "chapterNumber": 3,
                    "page": 24,
                    "curriculumCode": "SCI-7-CH3-P24"
                },
                "objectives": [
                    "آشنایی با تصفیه مکانیکی و فیلتراسیون ذرات",
                    "درک اهمیت ترتیب لایه‌ها از درشت به ریز جهت ممانعت از انسداد",
                    "آگاهی از لزوم گندزدایی شیمیایی و غیرقابل شرب بودن آب فیلترشده"
                ],
                "safety_notes": [
                    "آب خروجی این صافی فیزیکی به هیچ وجه آشامیدنی نبوده و نباید نوشیده شود!"
                ],
                "available_tools": [
                    {"id": "filter_column_bottle", "name": "بطری قیفی شکل ستون صافی", "type": "tool", "category": "ظروف", "icon": "filter"},
                    {"id": "cotton_layer", "name": "پنبه بهداشتی (تله ذرات ریز)", "type": "tool", "category": "فیلتر", "icon": "box"},
                    {"id": "fine_sand_layer", "name": "ماسه بادی ریز شسته‌شده", "type": "tool", "category": "فیلتر", "icon": "box"},
                    {"id": "gravel_layer", "name": "شن نخودی درشت", "type": "tool", "category": "فیلتر", "icon": "box"},
                    {"id": "dirty_water_flask", "name": "بشر آب کدر و گل‌آلود", "type": "chemical", "category": "مخلوط", "icon": "flask"},
                    {"id": "collection_beaker", "name": "بشر جمع‌آوری آب تصفیه‌شده", "type": "tool", "category": "ظروف", "icon": "beaker"}
                ],
                "steps_config": [
                    {"index": 1, "title": "آماده‌سازی بدنه صافی", "description": "بطری وارونه را روی پایه آزمایشگاه محکم کنید.", "hint": "بدنه بطری قیفی شکل محفظه استقرار لایه‌هاست."},
                    {"index": 2, "title": "چیدن لایه‌های فیلتر", "description": "به ترتیب پنبه در دهانه، ماسه در میانه و شن در بالا قرار دهید.", "hint": "ترتیب از دانه‌درشت به دانه‌ریز مانع گرفتگی سریع روزنه‌ها می‌شود."},
                    {"index": 3, "title": "ریختن آب گل‌آلود در ستون", "description": "آب کدر را روی لایه بالایی شن بریزید و ظرف جمع‌آوری را زیر خروجی بگذارید.", "hint": "نیروی گرانش آب را از میان لایه‌ها هدایت می‌کند."},
                    {"index": 4, "title": "مشاهده به دام افتادن ذرات معلق", "description": "به دام افتادن خاشاک در شن و گل و لای در ماسه را بررسی نمایید.", "hint": "روزنه‌های ریزتر ذرات کوچکتر را متوقف می‌کنند."},
                    {"index": 5, "title": "مقایسه شفافیت و هشدار ایمنی", "description": "کاهش کدورت آب خروجی را بررسی کرده و به هشدار غیرقابل شرب بودن توجه فرمایید.", "hint": "تصفیه فیزیکی میکروب‌ها و نمک‌های محلول را از بین نمی‌برد."}
                ]
            }
        ]

        for item in experiments_data:
            exp = db.query(Experiment).filter(Experiment.slug == item["slug"]).first()
            if not exp:
                exp = Experiment(
                    slug=item["slug"],
                    title=item["title"],
                    subject=item["subject"],
                    grade=item["grade"],
                    difficulty=item["difficulty"],
                    duration_minutes=item["duration_minutes"],
                    status=item["status"],
                    version=1,
                    summary=item["summary"],
                    thumbnail_type=item["thumbnail_type"],
                    textbook_source=item["textbook_source"],
                    objectives=item["objectives"],
                    safety_notes=item["safety_notes"],
                    available_tools=item["available_tools"],
                    steps_config=item["steps_config"]
                )
                db.add(exp)

        db.commit()

        print("[4/4] ایجاد تلاش نمونه و داده‌های آماری پداگوژیک...")
        # نمونه تلاش موفق دانش‌آموز برای آزمایش اسید و باز
        acid_exp = db.query(Experiment).filter(Experiment.slug == "acid-base-indicators").first()
        if acid_exp:
            sample_att = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == "att-seed-001").first()
            if not sample_att:
                now = datetime.now(timezone.utc)
                sample_att = ExperimentAttempt(
                    id="att-seed-001",
                    user_id=student.id,
                    experiment_id=acid_exp.id,
                    status="COMPLETED",
                    score=95.0,
                    steps_completed=3,
                    total_steps=3,
                    final_observations=[
                        "کاغذ تورنسل آبی در آبلیمو بلافاصله قرمز شد.",
                        "کاغذ تورنسل قرمز در جوش شیرین به رنگ آبی درآمد.",
                        "اندازه‌گیری pH اسید مقدار ۲.۵ و باز مقدار ۹.۰ را نشان داد."
                    ],
                    final_measurements={"lemon_pH": 2.5, "soda_pH": 9.0},
                    started_at=now - timedelta(days=2, minutes=20),
                    completed_at=now - timedelta(days=2)
                )
                db.add(sample_att)
                db.commit()

                # ثبت لاگ کنش‌های نمونه
                logs = [
                    StepActionLog(
                        attempt_id="att-seed-001",
                        step_index=1,
                        action_type="DIP_INDICATOR",
                        item_ids=["litmus-blue", "beaker-lemon"],
                        is_valid=True,
                        observation_text="کاغذ لیتموس آبی به رنگ قرمز تغییر کرد (خاصیت اسیدی).",
                        feedback_text="گام اول با موفقیت انجام شد."
                    ),
                    StepActionLog(
                        attempt_id="att-seed-001",
                        step_index=2,
                        action_type="DIP_INDICATOR",
                        item_ids=["litmus-red", "beaker-soda"],
                        is_valid=True,
                        observation_text="کاغذ لیتموس قرمز به رنگ آبی تغییر کرد (خاصیت بازی).",
                        feedback_text="گام دوم با موفقیت انجام شد."
                    ),
                    StepActionLog(
                        attempt_id="att-seed-001",
                        step_index=3,
                        action_type="MEASURE_PH",
                        item_ids=["ph-meter", "beaker-lemon"],
                        is_valid=True,
                        observation_text="مقدار pH آبلیمو برابر ۲.۵ ثبت گردید.",
                        feedback_text="اندازه‌گیری با موفقیت تکمیل شد."
                    )
                ]
                db.add_all(logs)

                # یک لاگ خطای شایع جهت غنی‌سازی آمار تحلیلی معلم
                sample_att_err = ExperimentAttempt(
                    id="att-seed-002",
                    user_id=student.id,
                    experiment_id=acid_exp.id,
                    status="IN_PROGRESS",
                    score=85.0,
                    steps_completed=1,
                    total_steps=3,
                    started_at=now - timedelta(days=1),
                )
                db.add(sample_att_err)
                db.commit()

                err_log = StepActionLog(
                    attempt_id="att-seed-002",
                    step_index=1,
                    action_type="DIP_INDICATOR",
                    item_ids=["litmus-red", "beaker-lemon"],
                    is_valid=False,
                    error_code="ERR_ACID_LITMUS_RED_NO_CHANGE",
                    observation_text="کاغذ لیتموس قرمز در محیط اسیدی تغییری نکرد.",
                    feedback_text="برای تشخیص اسید از کاغذ لیتموس آبی استفاده کنید."
                )
                hint_log = HintUsage(
                    attempt_id="att-seed-002",
                    step_index=1,
                    error_code="ERR_ACID_LITMUS_RED_NO_CHANGE",
                    hint_level=1,
                    hint_content="به رنگ اولیه کاغذ معرف دقت کنید. اسیدها کدام رنگ لیتموس را تغییر می‌دهند؟"
                )
                db.add_all([err_log, hint_log])
                db.commit()

        print("[OK] بذرپاشی پایگاه داده با موفقیت و داده‌های واقعی به پایان رسید!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
