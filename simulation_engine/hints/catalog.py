from typing import Dict
from ..schema import ErrorCategory
from .models import TieredHint

# نگاشت شناسه‌های آزمایش به عناوین رسمی کتاب درسی
EXPERIMENT_TITLES: Dict[str, str] = {
    "acid-base-indicators": "شناسایی اسیدها و بازها با معرف‌های رنگی",
    "exp-acid-base": "شناسایی اسیدها و بازها با معرف‌های رنگی",
    "mixture-separation-sand-salt": "جداسازی مخلوط ناهمگن ماسه، نمک و آب",
    "exp-mixture-separation": "جداسازی مخلوط ناهمگن ماسه، نمک و آب",
    "simple-electric-circuit-ohm": "بررسی مدار الکتریکی ساده و قانون اهم",
    "exp-simple-circuit": "بررسی مدار الکتریکی ساده و قانون اهم",
    "vinegar-baking-soda-reaction": "واکنش سرکه و جوش‌شیرین و تولید گاز",
    "exp-vinegar-baking-soda": "واکنش سرکه و جوش‌شیرین و تولید گاز",
    "simple-pendulum-motion": "بررسی حرکت آونگ ساده و قانون دوره تناوب",
    "exp-simple-pendulum": "بررسی حرکت آونگ ساده و قانون دوره تناوب",
    "plant-water-transport-celery": "انتقال آب در گیاه و هدایت در آوندهای چوبی",
    "exp-plant-transport": "انتقال آب در گیاه و هدایت در آوندهای چوبی",
    "liquid-density-column": "بررسی چگالی و لایه‌بندی مایعات (ستون چگالی)",
    "exp-density-column": "بررسی چگالی و لایه‌بندی مایعات (ستون چگالی)",
    "water-filtration-column": "ساخت صافی چندلایه آب و تصفیه فیزیکی",
    "exp-water-filtration": "ساخت صافی چندلایه آب و تصفیه فیزیکی"
}

# پایگاه دانش راهنماهای آموزشی سه‌سطحی معتبر کتب درسی برای تمام ۸ آزمایش
HINT_CATALOG: Dict[str, TieredHint] = {
    # =========================================================================
    # ۱. خطاهای آزمایش اسید و باز (علوم هشتم، ص ۱۶)
    # =========================================================================
    "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID": TieredHint(
        error_code="ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID",
        category=ErrorCategory.WRONG_TOOL,
        experiment_id="acid-base-indicators",
        step_index=1,
        level1_question="به نظر شما وقتی یک شناساگر از قبل به رنگ سرخ است، آیا می‌تواند حضور مادهٔ اسیدی را به شما نشان دهد؟",
        level2_clue="کاغذ تورنسل سرخ فقط در مواجهه با بازها تغییر رنگ می‌دهد. برای نشان دادن اسید، به شناساگری نیاز دارید که با اسید تغییر رنگ دهد.",
        level3_explanation="کاغذ تورنسل سرخ از قبل پروتون‌دار است و در اسید سرخ باقی می‌ماند. برای اثبات اسیدی بودن آب‌لیمو، باید کاغذ تورنسل آبی را انتخاب کنید تا به رنگ سرخ تبدیل شود."
    ),
    "ERR_INEFFECTIVE_INDICATOR_BLUE_ON_BASE": TieredHint(
        error_code="ERR_INEFFECTIVE_INDICATOR_BLUE_ON_BASE",
        category=ErrorCategory.WRONG_TOOL,
        experiment_id="acid-base-indicators",
        step_index=2,
        level1_question="آیا کاغذ تورنسل آبی می‌تواند در یک محیط قلیایی (بازی) تغییری از خود نشان دهد؟",
        level2_clue="صابون یک ماده بازی است و شناساگرهای بازی باید از رنگ اولیه سرخ به آبی تغییر کنند.",
        level3_explanation="کاغذ تورنسل آبی در محیط‌های بازی (pH > 7) تغییر رنگ نمی‌دهد. برای اثبات خاصیت بازی آب‌صابون، کاغذ تورنسل سرخ را در بشر قرار دهید تا آبی شود."
    ),
    "ERR_ORDER_VIOLATION_STEP1": TieredHint(
        error_code="ERR_ORDER_VIOLATION_STEP1",
        category=ErrorCategory.ORDER_VIOLATION,
        experiment_id="acid-base-indicators",
        step_index=1,
        level1_question="در دستورالعمل کتاب درسی، مقایسه با کدام نمونهٔ مجهول آغاز شده است؟ ترش‌مزه یا لیزکننده؟",
        level2_clue="در گام اول باید خصلت اسیدی نمونه خوراکی (آب‌لیمو) ارزیابی شود.",
        level3_explanation="ترتیب استاندارد آزمایش را رعایت کنید: ابتدا بشر آب‌لیمو را با تورنسل آبی امتحان کنید، سپس به سراغ آب‌صابون و آب‌مقطر بروید."
    ),
    "ERR_PRECONDITION_INDICATOR_NOT_ON_BENCH": TieredHint(
        error_code="ERR_PRECONDITION_INDICATOR_NOT_ON_BENCH",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="acid-base-indicators",
        step_index=1,
        level1_question="آیا تمام وسایل لازم برای انجام آزمایش را از قفسه به میز کار آورده‌اید؟",
        level2_clue="شناساگر هنوز در قفسه وسایل قرار دارد و روی سطح آزمایشگاه چیده نشده است.",
        level3_explanation="شناساگر مورد نظر (مثلاً کاغذ تورنسل) را با کلیک از قفسه به روی میز منتقل کنید تا بتوانید آن را درون محلول غوطه‌ور سازید."
    ),
    "ERR_PHENOLPHTHALEIN_ACID_MISINTERPRETATION": TieredHint(
        error_code="ERR_PHENOLPHTHALEIN_ACID_MISINTERPRETATION",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="acid-base-indicators",
        step_index=1,
        level1_question="آیا بی‌رنگ ماندن شناساگر فنل‌فتالئین در یک محلول به این معناست که آن محلول هیچ خاصیتی ندارد یا معرف خراب است؟",
        level2_clue="فنل‌فتالئین یک شناساگر اختصاصی است که در محیط اسیدی و خنثی بی‌رنگ می‌ماند و فقط در بازها تغییر رنگ ارغوانی می‌دهد.",
        level3_explanation="فنل‌فتالئین در محیط‌های اسیدی (pH < 7) کاملاً بی‌رنگ است و در محیط‌های بازی (pH > 8.2) به رنگ ارغوانی/صورتی پررنگ درمی‌آید. بنابراین بی‌رنگ ماندن آن در آب‌لیمو طبیعی است."
    ),
    "ERR_WATER_PH_MISCONCEPTION": TieredHint(
        error_code="ERR_WATER_PH_MISCONCEPTION",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="acid-base-indicators",
        step_index=3,
        level1_question="آیا آب مقطر خالص دارای خاصیت اسیدی یا بازی است و می‌تواند رنگ تورنسل را تغییر دهد؟",
        level2_clue="در آب خالص غلظت یون‌های هیدرونیوم و هیدروکسید دقیقاً برابر است.",
        level3_explanation="آب مقطر کاملاً خنثی بوده و pH آن برابر ۷ است. آب خالص هیچ تغییری در رنگ کاغذ لیتموس سرخ یا آبی ایجاد نمی‌کند."
    ),
    "ERR_MISSING_BEAKER-LEMON": TieredHint(
        error_code="ERR_MISSING_BEAKER-LEMON",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="acid-base-indicators",
        step_index=1,
        level1_question="برای بررسی خاصیت اسیدی، کدام ظرف را باید از قفسه روی میز کار قرار دهید؟",
        level2_clue="بشر حاوی آب‌لیمو ماده ترش‌مزه اسیدی آزمایش است.",
        level3_explanation="بشر آب‌لیمو را از قفسه به میز کار اضافه کنید تا بتوانید شناساگر لیتموس را درون آن امتحان نمایید."
    ),
    "ERR_MISSING_BEAKER-SODA": TieredHint(
        error_code="ERR_MISSING_BEAKER-SODA",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="acid-base-indicators",
        step_index=2,
        level1_question="برای بررسی خاصیت بازی، محلول جوش‌شیرین را کجای آزمایشگاه قرار داده‌اید؟",
        level2_clue="بشر حاوی محلول جوش‌شیرین باز قلیایی استاندارد این مرحله است.",
        level3_explanation="بشر محلول جوش‌شیرین را روی میز کار بگذارید تا آزمایش با تورنسل سرخ انجام شود."
    ),

    # =========================================================================
    # ۲. خطاهای آزمایش جداسازی مخلوط (علوم هشتم، ص ۶ و ۱۶)
    # =========================================================================
    "ERR_FILTER_WITHOUT_DISSOLUTION": TieredHint(
        error_code="ERR_FILTER_WITHOUT_DISSOLUTION",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="mixture-separation-sand-salt",
        step_index=2,
        level1_question="آیا می‌توان دو جامد خشک را با کاغذ صافی بدون حضور یک مایع حل‌کننده جدا کرد؟",
        level2_clue="کاغذ صافی ذرات جامد معلق در فاز مایع را نگه می‌دارد. برای تفکیک، ابتدا باید یکی از اجزا را حل کنید.",
        level3_explanation="نمک در آب حل می‌شود اما ماسه نامحلول است. ابتدا با پیست به مخلوط آب اضافه کرده و هم بزنید، سپس سوسپانسیون را روی کاغذ صافی بریزید."
    ),
    "ERR_HEAT_BEFORE_FILTER": TieredHint(
        error_code="ERR_HEAT_BEFORE_FILTER",
        category=ErrorCategory.ORDER_VIOLATION,
        experiment_id="mixture-separation-sand-salt",
        step_index=3,
        level1_question="اگر مخلوط حاوی ماسه را حرارت دهید، آیا ماسه در کپسول باقی می‌ماند یا از بین می‌رود؟",
        level2_clue="حرارت دادن برای تبخیر آب و به جا ماندن نمک است؛ اما ماسه هنوز در ظرف وجود دارد و جدا نشده است.",
        level3_explanation="حرارت دادن پیش از فیلتراسیون باعث سوختن رسوب ماسه و پرتاب آن می‌شود. ابتدا ماسه را با قیف و کاغذ صافی جدا کنید و سپس مایع زلال آب‌نمک را بجوشانید."
    ),
    "ERR_BOIL_DRY_EXPLOSION": TieredHint(
        error_code="ERR_BOIL_DRY_EXPLOSION",
        category=ErrorCategory.HAZARDOUS_ACTION,
        experiment_id="mixture-separation-sand-salt",
        step_index=3,
        level1_question="آیا پس از تبخیر کامل آب، کپسول چینی باید همچنان روی شعله مستقیم بماند؟",
        level2_clue="حرارت مستقیم به بلورهای خشک نمک سبب شکستن ظرف و پرتاب ذرات داغ می‌شود.",
        level3_explanation="به محض ظاهر شدن اولین بلورهای نمک و به اتمام رسیدن فاز مایع، شعله چراغ بونزن را خاموش کنید تا از پرتاب دانه‌های داغ نمک جلوگیری گردد."
    ),

    # =========================================================================
    # ۳. خطاهای آزمایش مدار الکتریکی (علوم نهم، ص ۹۸)
    # =========================================================================
    "ERR_CIRCUIT_WITHOUT_LOAD": TieredHint(
        error_code="ERR_CIRCUIT_WITHOUT_LOAD",
        category=ErrorCategory.HAZARDOUS_ACTION,
        experiment_id="simple-electric-circuit-ohm",
        step_index=1,
        level1_question="اگر دو قطب یک باتری بدون هیچ وسیله مصرف‌کننده‌ای مستقیماً به هم وصل شوند چه پدیده‌ای رخ می‌دهد؟",
        level2_clue="این حالت اتصال کوتاه نام دارد. مقاومت مدار نزدیک صفر می‌شود و جریان شدیدی از سیم‌ها می‌گذرد.",
        level3_explanation="اتصال مستقیم سیم‌ها به باتری بدون لامپ باعث اتصال کوتاه و داغ شدن شدید سیم می‌شود. حتماً لامپ ۳ ولتی را در مسیر مدار به عنوان مصرف‌کننده قرار دهید."
    ),
    "ERR_SWITCH_BEFORE_WIRING": TieredHint(
        error_code="ERR_SWITCH_BEFORE_WIRING",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="simple-electric-circuit-ohm",
        step_index=2,
        level1_question="آیا کلیدی که در مدار متصل نیست می‌تواند نقشی در هدایت الکتریکی داشته باشد؟",
        level2_clue="حلقه سیم‌کشی هنوز کامل نشده است. کلید باید درون یک مدار پیوسته قرار گیرد.",
        level3_explanation="ابتدا سیم‌های رابط را بین باتری، کلید و پایه‌های لامپ وصل کنید تا یک حلقه متوالی بسته تشکیل شود، سپس کلید را ببندید."
    ),
    "ERR_MEASURE_ON_OPEN_CIRCUIT": TieredHint(
        error_code="ERR_MEASURE_ON_OPEN_CIRCUIT",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="simple-electric-circuit-ohm",
        step_index=3,
        level1_question="آیا در یک مدار قطع، جریانی از سیم‌ها عبور می‌کند که آمپرمتر آن را ثبت کند؟",
        level2_clue="آمپرمتر برای نشان دادن شدت جریان نیاز به عبور بار الکتریکی دارد؛ کلید در وضعیت باز است.",
        level3_explanation="برای اندازه‌گیری جریان طبق قانون اهم، کلید مدار را ببندید تا بارها حرکت کرده و آمپرمتر عدد جریان عبوری را نشان دهد."
    ),
    "ERR_VOLTAGE_CURRENT_MISCONCEPTION": TieredHint(
        error_code="ERR_VOLTAGE_CURRENT_MISCONCEPTION",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="simple-electric-circuit-ohm",
        step_index=3,
        level1_question="آیا افزایش ولتاژ باتری باعث کاهش شدت جریان در یک مقاومت ثابت می‌شود یا افزایش آن؟",
        level2_clue="طبق قانون اهم، ولتاژ نیروی محرکه بارهاست: فرمول V = I * R را به یاد آورید.",
        level3_explanation="بر اساس قانون اهم (I = V / R)، در یک مقاومت ثابت با دو برابر شدن ولتاژ، شدت جریان عبوری از مدار نیز دقیقاً دو برابر شده و نور لامپ افزایش می‌یابد."
    ),

    # =========================================================================
    # ۴. خطاهای آزمایش واکنش سرکه و جوش‌شیرین (علوم هشتم، ص ۱۰-۱۴)
    # =========================================================================
    "ERR_SODA_BEFORE_VINEGAR": TieredHint(
        error_code="ERR_SODA_BEFORE_VINEGAR",
        category=ErrorCategory.ORDER_VIOLATION,
        experiment_id="vinegar-baking-soda-reaction",
        step_index=2,
        level1_question="آیا پودر جوش‌شیرین بدون تماس با یک اسید مایع می‌تواند واکنش دهد؟",
        level2_clue="واکنش اسید و باز نیازمند حضور محیط مایع و یون‌های اسید استیک است.",
        level3_explanation="ابتدا سرکه را به عنوان فاز مایع اسیدی درون لیوان بریزید و سپس پودر جوش‌شیرین را به آن بیفزایید."
    ),
    "ERR_REACTION_PRECONDITIONS_INCOMPLETE": TieredHint(
        error_code="ERR_REACTION_PRECONDITIONS_INCOMPLETE",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="vinegar-baking-soda-reaction",
        step_index=4,
        level1_question="آیا تمام واکنش‌دهنده‌های لازم درون لیوان آزمایشگاهی ترکیب شده‌اند؟",
        level2_clue="واکنش تولید گاز نیازمند اختلاط مستقیم هر دو جزء سرکه و بی‌کربنات است.",
        level3_explanation="مطمئن شوید که هر دو ماده سرکه و جوش‌شیرین را به لیوان اضافه کرده‌اید تا واکنش تشکیل کف و گاز CO2 آغاز گردد."
    ),
    "ERR_MISCONCEPTION_GAS_TYPE": TieredHint(
        error_code="ERR_MISCONCEPTION_GAS_TYPE",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="vinegar-baking-soda-reaction",
        step_index=4,
        level1_question="آیا گازی که شعله شمع را فوراً خاموش می‌کند می‌تواند اکسیژن (که آتش را مشتعل می‌کند) یا هیدروژن باشد؟",
        level2_clue="این گاز حاوی عنصر کربن است و از یون بی‌کربنات (HCO3) آزاد می‌شود و در کپسول‌های آتش‌نشانی کاربرد دارد.",
        level3_explanation="گاز حاصل از واکنش اسید استیک و بی‌کربنات سدیم، کربن دی‌اکسید (CO2) است نه اکسیژن یا هیدروژن. این گاز چگال‌تر از هوا بوده و مانع رسیدن اکسیژن به شعله می‌شود."
    ),
    "ERR_LIMITING_REACTANT_OVEREATING": TieredHint(
        error_code="ERR_LIMITING_REACTANT_OVEREATING",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="vinegar-baking-soda-reaction",
        step_index=4,
        level1_question="اگر تمام اسید سرکه موجود در ظرف مصرف شده باشد، آیا ریختن قاشق‌های بعدی جوش‌شیرین باز هم جوشش ایجاد می‌کند؟",
        level2_clue="مفهوم واکنش‌دهنده محدودکننده در شیمی می‌گوید با اتمام یکی از اجزا، واکنش کاملاً متوقف می‌شود.",
        level3_explanation="پدیده واکنش‌دهنده محدودکننده: پس از مصرف کامل سرکه، افزودن جوش‌شیرین بیشتر هیچ گازی تولید نمی‌کند و پودر دست‌نخورده در کف ظرف باقی می‌ماند. برای ادامه واکنش باید سرکه اضافه شود."
    ),
    "ERR_MISCONCEPTION_BOILING_VS_REACTION": TieredHint(
        error_code="ERR_MISCONCEPTION_BOILING_VS_REACTION",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="vinegar-baking-soda-reaction",
        step_index=4,
        level1_question="آیا تشکیل حباب همیشه به معنای رسیدن مایع به نقطه جوش حرارتی است؟",
        level2_clue="در این آزمایش هیچ حرارتی داده نشده است، حتی دمای ظرف اندکی سردتر می‌شود.",
        level3_explanation="حباب‌های مشاهده‌شده ناشی از جوشیدن فیزیکی نیستند، بلکه خروج سریع گاز کربن دی‌اکسید تولیدشده در اثر واکنش شیمیایی هستند. این واکنش گرماگیر موضعی بوده و دمای محلول اندکی افت می‌کند."
    ),
    "ERR_MISSING_BEAKER_GLASS": TieredHint(
        error_code="ERR_MISSING_BEAKER_GLASS",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="vinegar-baking-soda-reaction",
        step_index=1,
        level1_question="واکنش را در چه ظرف شفافی می‌خواهید انجام دهید؟",
        level2_clue="لیوان آزمایشگاهی شفاف را از قفسه انتخاب نمایید.",
        level3_explanation="لیوان آزمایشگاهی (بشر) را روی میز کار بگذارید تا سرکه و جوش‌شیرین درون آن ترکیب شوند."
    ),
    "ERR_MISSING_BOTTLE_VINEGAR": TieredHint(
        error_code="ERR_MISSING_BOTTLE_VINEGAR",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="vinegar-baking-soda-reaction",
        step_index=2,
        level1_question="مایع اسیدی واکنش در کدام ظرف قرار دارد؟",
        level2_clue="بطری سرکه حاوی اسید استیک ۵٪ است.",
        level3_explanation="بطری سرکه را به میز کار بیاورید و مقدار معینی از آن را داخل لیوان بریزید."
    ),
    "ERR_MISSING_JAR_BAKING_SODA": TieredHint(
        error_code="ERR_MISSING_JAR_BAKING_SODA",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="vinegar-baking-soda-reaction",
        step_index=3,
        level1_question="پودر بی‌کربنات سدیم را از کجا برمی‌دارید؟",
        level2_clue="ظرف جوش‌شیرین ماده جامد واکنش است.",
        level3_explanation="ظرف پودر جوش‌شیرین را به میز کار بیاورید و با اسپاتول به سرکه بیفزایید."
    ),

    # =========================================================================
    # ۵. خطاهای آزمایش حرکت آونگ ساده (علوم نهم، ص ۴۵)
    # =========================================================================
    "ERR_BOB_BEFORE_STRING": TieredHint(
        error_code="ERR_BOB_BEFORE_STRING",
        category=ErrorCategory.ORDER_VIOLATION,
        experiment_id="simple-pendulum-motion",
        step_index=2,
        level1_question="آیا وزنه می‌تواند بدون وجود نخ رابط از پایه آویزان شود؟",
        level2_clue="یک آونگ ساده از نخ متصل به پایه و وزنه متصل به نخ تشکیل می‌شود.",
        level3_explanation="ابتدا نخ را با طول مناسب به گیره پایه ببندید و سپس وزنه را به انتهای آن متصل کنید."
    ),
    "ERR_DEFLECT_WITHOUT_BOB": TieredHint(
        error_code="ERR_DEFLECT_WITHOUT_BOB",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="simple-pendulum-motion",
        step_index=3,
        level1_question="آیا نخی بدون وزنه می‌تواند نوسان آونگی منظمی ایجاد کند؟",
        level2_clue="برای ایجاد نوسان نیازمند جرم معلق و اینرسی وزنه هستید.",
        level3_explanation="وزنه را به انتهای نخ وصل کنید تا نیروی بازگرداننده گرانش برقرار شود."
    ),
    "ERR_LARGE_ANGLE_DEVIATION": TieredHint(
        error_code="ERR_LARGE_ANGLE_DEVIATION",
        category=ErrorCategory.HAZARDOUS_ACTION,
        experiment_id="simple-pendulum-motion",
        step_index=3,
        level1_question="آیا فرمول زمان تناوب آونگ برای هر زاویه‌ای حتی زوایای خیلی بزرگ برقرار است؟",
        level2_clue="در فیزیک، مدل آونگ ساده بر پایه تقریب زاویه کوچک (sin θ ≈ θ) بنا شده است.",
        level3_explanation="زاویه انحراف را زیر ۱۵ درجه تنظیم کنید؛ در زوایای بزرگتر حرکت غیرخطی شده و دوره تناوب از فرمول T = 2π√(L/g) پیروی نخواهد کرد."
    ),
    "ERR_OSCILLATION_INCOMPLETE": TieredHint(
        error_code="ERR_OSCILLATION_INCOMPLETE",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="simple-pendulum-motion",
        step_index=4,
        level1_question="آیا آونگ قبل از شروع زمان‌گیری، به وضعیت نوسان درآمده است؟",
        level2_clue="برای زمان‌سنجی باید آونگ را با زاویه کوچک منحرف و رها کرده باشید.",
        level3_explanation="ابتدا آونگ را تا زاویه ۱۰ درجه منحرف کرده و سپس با رهاسازی، دکمه کرونومتر را بزنید."
    ),
    "ERR_PENDULUM_MASS_DEPENDENCE": TieredHint(
        error_code="ERR_PENDULUM_MASS_DEPENDENCE",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="simple-pendulum-motion",
        step_index=4,
        level1_question="آیا در فرمول زمان تناوب آونگ ساده (T = 2π√(L/g)) متغیر جرم (m) دیده می‌شود؟",
        level2_clue="افزایش جرم نیروی گرانش را زیاد می‌کند، اما لَختی (مقاومت در برابر حرکت) را هم دقیقاً به همان نسبت زیاد می‌کند.",
        level3_explanation="زمان تناوب آونگ ساده در زوایای کوچک کاملاً مستقل از جرم وزنه است. وزنه ۵۰ گرمی و ۵۰۰ گرمی با طول نخ یکسان، دقیقاً در زمان مساوی یک نوسان کامل را طی می‌کنند."
    ),
    "ERR_PENDULUM_LENGTH_INVERSE": TieredHint(
        error_code="ERR_PENDULUM_LENGTH_INVERSE",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="simple-pendulum-motion",
        step_index=1,
        level1_question="نوسان یک تاب بلند در پارک کندتر است یا نوسان یک آونگ کوتاه چند سانتی‌متری؟",
        level2_clue="رابطه طول با زمان تناوب مستقیم است: هر چه L بیشتر باشد، T بزرگتر خواهد بود.",
        level3_explanation="با افزایش طول نخ، زمان تناوب (T) افزایش می‌یابد و آونگ کندتر رفت و برگشت می‌کند؛ بنابراین برای تندتر شدن نوسان باید طول نخ را کوتاه کنید."
    ),
    "ERR_MISSING_PENDULUM_STAND": TieredHint(
        error_code="ERR_MISSING_PENDULUM_STAND",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="simple-pendulum-motion",
        step_index=1,
        level1_question="نخ آونگ را به چه پایه‌ای می‌خواهید آویزان کنید؟",
        level2_clue="پایه نگهدارنده فلزی و گیره را از قفسه وسایل انتخاب نمایید.",
        level3_explanation="پایه نگهدارنده آزمایشگاهی را روی میز قرار دهید تا تکیه‌گاه آونگ فراهم شود."
    ),
    "ERR_MISSING_PENDULUM_STRING": TieredHint(
        error_code="ERR_MISSING_PENDULUM_STRING",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="simple-pendulum-motion",
        step_index=1,
        level1_question="رابط انعطاف‌پذیر آونگ برای تنظیم طول کجاست؟",
        level2_clue="نخ آزمایشگاهی با طول مشخص را از قفسه انتخاب کنید.",
        level3_explanation="نخ آزمایشگاهی را انتخاب کرده و به گیره پایه متصل نمایید."
    ),
    "ERR_MISSING_PENDULUM_BOB": TieredHint(
        error_code="ERR_MISSING_PENDULUM_BOB",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="simple-pendulum-motion",
        step_index=2,
        level1_question="جرم معلق آونگ را انتخاب کرده‌اید؟",
        level2_clue="وزنه فلزی کروی گلوله آونگ است.",
        level3_explanation="وزنه کروی فلزی را از قفسه انتخاب کرده و به انتهای نخ متصل نمایید."
    ),

    # =========================================================================
    # ۶. خطاهای آزمایش انتقال آب در گیاه (علوم هفتم، ص ۱۰۴)
    # =========================================================================
    "ERR_COLOR_BEFORE_WATER": TieredHint(
        error_code="ERR_COLOR_BEFORE_WATER",
        category=ErrorCategory.ORDER_VIOLATION,
        experiment_id="plant-water-transport-celery",
        step_index=2,
        level1_question="آیا قطره رنگ غلیظ در لیوان خالی می‌تواند پخش شود و بالا برود؟",
        level2_clue="رنگ خوراکی باید به عنوان نشانگر در یک حلال مایع حل و رقیق شود.",
        level3_explanation="ابتدا آب را داخل لیوان بریزید و سپس رنگ خوراکی را به آن اضافه کنید تا محلول رنگی یکنواخت حاصل شود."
    ),
    "ERR_CELERY_IN_CLEAR_WATER": TieredHint(
        error_code="ERR_CELERY_IN_CLEAR_WATER",
        category=ErrorCategory.WRONG_TOOL,
        experiment_id="plant-water-transport-celery",
        step_index=3,
        level1_question="آیا حرکت آب شفاف درون بافت ساقه با چشم قابل ردیابی و مشاهده است؟",
        level2_clue="برای آشکار شدن آوندهای چوبی، آب باید حاوی ماده رنگی شناساگر باشد.",
        level3_explanation="رنگ خوراکی را به آب اضافه کنید تا مسیر صعود شیره خام در آوندهای چوبی به وضوح نمایان شود."
    ),
    "ERR_CELERY_NOT_IN_WATER": TieredHint(
        error_code="ERR_CELERY_NOT_IN_WATER",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="plant-water-transport-celery",
        step_index=4,
        level1_question="آیا ساقه‌ای که درون آب قرار ندارد می‌تواند آب را به برگ‌ها منتقل کند؟",
        level2_clue="مقطع بریده‌شده ساقه کرفس باید در تماس مستقیم با محلول آب رنگی باشد.",
        level3_explanation="ساقه کرفس را درون لیوان آب رنگی بگذارید و سپس پیشروی آب با گذشت زمان را رصد نمایید."
    ),
    "ERR_CELERY_NOT_READY": TieredHint(
        error_code="ERR_CELERY_NOT_READY",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="plant-water-transport-celery",
        step_index=5,
        level1_question="آیا قبل از گذشت زمان کافی برای صعود آب، آوندها رنگین می‌شوند؟",
        level2_clue="صعود شیره خام نیازمند سپری شدن زمان و تبخیر آب از برگ‌هاست.",
        level3_explanation="شبیه‌سازی گذر زمان را اجرا کنید تا آب رنگی به ارتفاع ساقه و رگبرگ‌ها برسد."
    ),
    "ERR_MISCONCEPTION_XYLEM_PATH": TieredHint(
        error_code="ERR_MISCONCEPTION_XYLEM_PATH",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="plant-water-transport-celery",
        step_index=5,
        level1_question="در برش عرضی ساقه کرفس، آیا کل ساقه مثل اسفنج رنگی شده یا فقط لوله‌های دایره‌ای مشخصی رنگ گرفته‌اند؟",
        level2_clue="گیاهان برای جابه‌جایی آب و مواد معدنی دارای لوله‌های باریک تخصص‌یافته‌ای به نام آوند چوبی هستند.",
        level3_explanation="آب و مواد معدنی (شیره خام) منحصراً از مجاری آوند چوبی (Xylem) بالا می‌روند نه بافت گوشتی یا پوست ساقه. این لوله‌ها با رنگ خوراکی به شکل نقطه‌های تفکیک‌شده نمایان می‌شوند."
    ),
    "ERR_MISCONCEPTION_NO_LEAVES_NEEDED": TieredHint(
        error_code="ERR_MISCONCEPTION_NO_LEAVES_NEEDED",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="plant-water-transport-celery",
        step_index=4,
        level1_question="آیا نیروی محرک اصلی صعود آب در گیاه از ساقه است یا از تبخیر آب در برگ‌ها؟",
        level2_clue="پدیده تعرق در روزنه‌های برگ مثل یک مکنده قوی ستون آب را بالا می‌کشد.",
        level3_explanation="تبخیر سطحی آب از روزنه‌های برگ (تعرق) کششی به نام مکش تعرقی ایجاد می‌کند که ستون پیوسته آب را در آوندهای چوبی به سمت برگ‌ها بالا می‌کشد؛ بدون برگ این فرآیند بسیار کُند می‌شود."
    ),
    "ERR_MISSING_GLASS_CUP": TieredHint(
        error_code="ERR_MISSING_GLASS_CUP",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="plant-water-transport-celery",
        step_index=1,
        level1_question="محلول رنگی را درون چه ظرفی می‌خواهید آماده کنید؟",
        level2_clue="لیوان شفاف آزمایشگاهی ظرف استقرار ساقه است.",
        level3_explanation="لیوان شفاف شیشه‌ای را از قفسه انتخاب کرده و روی میز کار قرار دهید."
    ),
    "ERR_MISSING_FOOD_COLORING": TieredHint(
        error_code="ERR_MISSING_FOOD_COLORING",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="plant-water-transport-celery",
        step_index=2,
        level1_question="ماده نشانگر رنگی برای ردیابی مسیر آب کجاست؟",
        level2_clue="قطره‌چکان حاوی رنگ خوراکی را از قفسه بردارید.",
        level3_explanation="قطره‌چکان رنگ خوراکی را به میز کار بیاورید و چند قطره در آب بچکانید."
    ),
    "ERR_MISSING_CELERY_STALK": TieredHint(
        error_code="ERR_MISSING_CELERY_STALK",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="plant-water-transport-celery",
        step_index=3,
        level1_question="نمونه گیاهی آزمایش کجاست؟",
        level2_clue="ساقه تازه کرفس دارای برگ را از قفسه انتخاب کنید.",
        level3_explanation="ساقه کرفس را از قفسه انتخاب کرده و درون آب رنگی بگذارید."
    ),

    # =========================================================================
    # ۷. خطاهای آزمایش ستون چگالی مایعات (علوم هفتم، ص ۱۴-۱۸)
    # =========================================================================
    "ERR_POUR_WITHOUT_CYLINDER": TieredHint(
        error_code="ERR_POUR_WITHOUT_CYLINDER",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="liquid-density-column",
        step_index=2,
        level1_question="مایعات آزمایش را در چه ظرفی می‌خواهید لایه‌بندی و مقایسه کنید؟",
        level2_clue="یک استوانه مدرج شفاف برای مشاهده مرز لایه‌ها و منیسک مایعات ضروری است.",
        level3_explanation="ابتدا استوانه مدرج شفاف را روی میز کار قرار دهید و سپس مایعات را درون آن بریزید."
    ),
    "ERR_INSUFFICIENT_LIQUIDS_FOR_LAYERS": TieredHint(
        error_code="ERR_INSUFFICIENT_LIQUIDS_FOR_LAYERS",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="liquid-density-column",
        step_index=5,
        level1_question="آیا با یک مایع می‌توان ستون چگالی و مقایسه فازها را ایجاد کرد؟",
        level2_clue="ستون چگالی نیازمند مقایسه حداقل دو یا سه مایع با چگالی متفاوت است.",
        level3_explanation="عسل، آب و روغن مایع را به استوانه اضافه کنید تا تفکیک فازها و شناوری بر حسب چگالی شکل گیرد."
    ),
    "ERR_DENSITY_VOLUME_CONFUSION": TieredHint(
        error_code="ERR_DENSITY_VOLUME_CONFUSION",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="liquid-density-column",
        step_index=5,
        level1_question="آیا اگر مقدار بیشتری روغن (مثلاً ۱ لیتر) بریزیم، سنگین‌تر شده و به زیر ۱ قطره عسل می‌رود؟",
        level2_clue="چگالی نسبت جرم به حجم است (ρ = m / V) و با تغییر حجم مایع تغییر نمی‌کند.",
        level3_explanation="جایگاه قرارگیری مایعات در ستون منحصراً به چگالی (جرم واحد حجم) بستگی دارد نه حجم کل. عسل به دلیل چگالی بالاتر (۱.۴۲ گرم بر سانتی‌متر مکعب) همیشه در زیر آب و روغن قرار می‌گیرد."
    ),
    "ERR_MISCONCEPTION_VISCOSITY_DENSITY": TieredHint(
        error_code="ERR_MISCONCEPTION_VISCOSITY_DENSITY",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="liquid-density-column",
        step_index=4,
        level1_question="آیا هر مایعی که چسبنده‌تر یا غلیظ‌تر است (گرانروی بالاتری دارد)، حتماً چگال‌تر هم هست؟",
        level2_clue="روغن خوراکی کندتر از آب جاری می‌شود، اما چرا روی آب شناور می‌ماند؟",
        level3_explanation="گرانروی (لزجت) با چگالی تفاوت دارد. روغن گیاهی با اینکه غلیظ‌تر به نظر می‌رسد، چگالی کمتری نسبت به آب دارد (۰.۹۱ در برابر ۱.۰۰) و بنابراین روی آب شناور می‌ماند."
    ),
    "ERR_MISCONCEPTION_MISCIBILITY_IGNORED": TieredHint(
        error_code="ERR_MISCONCEPTION_MISCIBILITY_IGNORED",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="liquid-density-column",
        step_index=5,
        level1_question="اگر به جای روغن، الکل یا آب‌نمک با چگالی متفاوت می‌ریختیم، آیا لایه‌های جداگانه تشکیل می‌شد؟",
        level2_clue="برای تشکیل ستون چگالی پایدار، مایعات علاوه بر تفاوت چگالی، نباید در هم حل شوند.",
        level3_explanation="امتزاج‌ناپذیری (حل نشدن در یکدیگر) شرط اساسی پایداری لایه‌هاست. روغن و آب به دلیل تفاوت در قطبیت مخلوط نمی‌شوند؛ اما مایعات امتزاج‌پذیر (مانند آب و الکل) مخلوط شده و یک فاز همگن تشکیل می‌دهند."
    ),
    "ERR_MISSING_MEASURING_CYLINDER": TieredHint(
        error_code="ERR_MISSING_MEASURING_CYLINDER",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="liquid-density-column",
        step_index=1,
        level1_question="ستون چگالی در چه ظرف مدرجی ساخته می‌شود؟",
        level2_clue="استوانه مدرج شفاف ظرف اصلی آزمایش است.",
        level3_explanation="استوانه مدرج شفاف را از قفسه انتخاب کرده و روی میز کار قرار دهید."
    ),
    "ERR_MISSING_FLASK_HONEY": TieredHint(
        error_code="ERR_MISSING_FLASK_HONEY",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="liquid-density-column",
        step_index=2,
        level1_question="چگال‌ترین مایع آزمایش کجاست؟",
        level2_clue="ظرف عسل طبیعی را از قفسه بردارید.",
        level3_explanation="ظرف عسل طبیعی را روی میز کار بیاورید و در کف استوانه بریزید."
    ),
    "ERR_MISSING_FLASK_OIL": TieredHint(
        error_code="ERR_MISSING_FLASK_OIL",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="liquid-density-column",
        step_index=4,
        level1_question="سبک‌ترین مایع ستون چگالی کجاست؟",
        level2_clue="ظرف روغن مایع گیاهی در قفسه قرار دارد.",
        level3_explanation="روغن گیاهی را به آرامی به لایه رویی آب در استوانه اضافه کنید."
    ),

    # =========================================================================
    # ۸. خطاهای آزمایش ساخت صافی آب (علوم هفتم، ص ۲۴)
    # =========================================================================
    "ERR_LAYERS_BEFORE_BOTTLE": TieredHint(
        error_code="ERR_LAYERS_BEFORE_BOTTLE",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="water-filtration-column",
        step_index=2,
        level1_question="لایه‌های صافی (پنبه، ماسه، شن) را درون چه محفظه‌ای می‌خواهید قرار دهید؟",
        level2_clue="بدنه بطری قیفی شکل باید به عنوان نگهدارنده ستون فیلتر روی پایه باشد.",
        level3_explanation="ابتدا بطری صافی را آماده کرده و روی پایه قرار دهید، سپس لایه‌های تصفیه را در آن بچینید."
    ),
    "ERR_WATER_BEFORE_LAYERS": TieredHint(
        error_code="ERR_WATER_BEFORE_LAYERS",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="water-filtration-column",
        step_index=3,
        level1_question="اگر آب گل‌آلود را در بطری خالی بدون لایه‌های فیلتر بریزید چه اتفاقی می‌افتد؟",
        level2_clue="بدون لایه‌های پنبه، ماسه و شن، ذرات معلق فیلتر نشده و مستقیماً خارج می‌شوند.",
        level3_explanation="ابتدا لایه‌های صافی را با ترتیب پنبه در پایین، ماسه در میانه و شن در بالا بچینید، سپس آب گل‌آلود را بیفزایید."
    ),
    "ERR_OBSERVE_BEFORE_POURING": TieredHint(
        error_code="ERR_OBSERVE_BEFORE_POURING",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="water-filtration-column",
        step_index=4,
        level1_question="آیا بدون ورود آب به ستون، فرآیند تصفیه‌ای برای مشاهده وجود دارد؟",
        level2_clue="تصفیه فیزیکی زمانی رخ می‌دهد که آب از خلل و فرج لایه‌های دانه‌ای عبور کند.",
        level3_explanation="آب گل‌آلود را روی لایه بالایی بریزید تا جریان و ته‌نشینی ذرات معلق آغاز شود."
    ),
    "ERR_COMPARE_WITHOUT_FILTRATION": TieredHint(
        error_code="ERR_COMPARE_WITHOUT_FILTRATION",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="water-filtration-column",
        step_index=5,
        level1_question="آیا فرآیند فیلتراسیون آب کامل شده تا بتوانید شفافیت را مقایسه کنید؟",
        level2_clue="برای ارزیابی، باید آب از ستون عبور کرده و در بشر جمع‌آوری ریخته شده باشد.",
        level3_explanation="مراحل تصفیه و خروج آب زلال را کامل کنید تا بتوانید تغییر کدورت را بررسی نمایید."
    ),
    "ERR_MISCONCEPTION_POTABLE_WATER": TieredHint(
        error_code="ERR_MISCONCEPTION_POTABLE_WATER",
        category=ErrorCategory.HAZARDOUS_ACTION,
        experiment_id="water-filtration-column",
        step_index=5,
        level1_question="آیا آب زلال حاصل از فیلتراسیون ماسه و شن را می‌توان بلافاصله نوشید؟",
        level2_clue="صافی فیزیکی فقط ذرات معلق را می‌گیرد، اما با میکروب‌ها و نمک‌های محلول چه می‌کند؟",
        level3_explanation="هشدار مهم بهداشتی: آب خروجی این صافی به هیچ وجه آشامیدنی نیست! فیلتراسیون فیزیکی گل‌ولای را جدا می‌کند، اما باکتری‌ها و مواد شیمیایی محلول همچنان در آب باقی می‌مانند و حتماً به گندزدایی نیاز دارند."
    ),
    "ERR_INVERTED_FILTER_LAYERS": TieredHint(
        error_code="ERR_INVERTED_FILTER_LAYERS",
        category=ErrorCategory.ORDER_VIOLATION,
        experiment_id="water-filtration-column",
        step_index=2,
        level1_question="اگر ماسه بسیار ریز در بالاترین لایه قرار گیرد، چه بر سر عبور آب خواهد آمد؟",
        level2_clue="ترتیب لایه‌ها باید از دانه‌درشت به دانه‌ریز باشد تا منافذ سریع مسدود نشوند.",
        level3_explanation="ترتیب صحیح لایه‌ها: شن درشت در بالا (برای گرفتن خاشاک)، ماسه ریز در وسط (برای به دام انداختن ذرات ریزتر)، و پنبه در دهانه خروجی. اگر ماسه در بالا باشد سریعاً مسدود و سرریز می‌شود."
    ),
    "ERR_FILTER_SOLUBLE_SUBSTANCES": TieredHint(
        error_code="ERR_FILTER_SOLUBLE_SUBSTANCES",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="water-filtration-column",
        step_index=5,
        level1_question="آیا این صافی شنی می‌تواند نمک حل‌شده یا رنگ موجود در آب را هم تصفیه و جدا کند؟",
        level2_clue="فیلتراسیون فیزیکی فقط ذرات نامحلول را جدا می‌کند نه یون‌ها و مولکول‌های حل‌شده را.",
        level3_explanation="یون‌های نمک حل‌شده و رنگ‌های محلول بسیار کوچکتر از منافذ ماسه هستند و به راحتی از صافی عبور می‌کنند. برای جداسازی مواد محلول به روش‌های تقطیر یا اسمز معکوس نیاز است."
    ),
    "ERR_MISSING_FILTER_COLUMN_BOTTLE": TieredHint(
        error_code="ERR_MISSING_FILTER_COLUMN_BOTTLE",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="water-filtration-column",
        step_index=1,
        level1_question="محفظه ستون صافی کجاست؟",
        level2_clue="بطری قیفی شکل را از قفسه روی پایه بگذارید.",
        level3_explanation="بطری پلاستیکی وارونه را به عنوان بدنه ستون روی پایه مستقر کنید."
    ),
    "ERR_MISSING_DIRTY_WATER_FLASK": TieredHint(
        error_code="ERR_MISSING_DIRTY_WATER_FLASK",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="water-filtration-column",
        step_index=3,
        level1_question="آب کدر و گل‌آلود برای تصفیه را برداشته‌اید؟",
        level2_clue="بشر حاوی آب گل‌آلود نمونه آزمایش است.",
        level3_explanation="بشر آب گل‌آلود را از قفسه بردارید و روی ستون صافی بریزید."
    )
}

# راهنماهای عمومی پیش‌فرض برای دسته‌های مختلف خطا در صورت مواجهه با خطای پیش‌بینی‌نشده
DEFAULT_CATEGORY_HINTS: Dict[ErrorCategory, TieredHint] = {
    ErrorCategory.WRONG_TOOL: TieredHint(
        error_code="GENERIC_WRONG_TOOL",
        category=ErrorCategory.WRONG_TOOL,
        experiment_id="general",
        step_index=0,
        level1_question="آیا وسیله‌ای که انتخاب کرده‌اید برای این نوع اندازه‌گیری یا واکنش طراحی شده است؟",
        level2_clue="به کارکرد فیزیکی ابزار انتخابی و هشدارهای کتاب درسی دقت فرمایید.",
        level3_explanation="ابزار نامناسبی انتخاب شده است. وسیله استاندارد مربوط به این گام را از قفسه انتخاب و جایگزین نمایید."
    ),
    ErrorCategory.WRONG_REAGENT: TieredHint(
        error_code="GENERIC_WRONG_REAGENT",
        category=ErrorCategory.WRONG_REAGENT,
        experiment_id="general",
        step_index=0,
        level1_question="آیا ماده شیمیایی یا معرف درستی را برای این مرحله انتخاب کرده‌اید؟",
        level2_clue="به برچسب ماده و خواص اسیدی، بازی یا انحلال‌پذیری آن توجه نمایید.",
        level3_explanation="ماده نادرستی افزوده شده است. ماده مشخص‌شده در دستور کار آزمایش را انتخاب نمایید."
    ),
    ErrorCategory.MISSING_PRECONDITION: TieredHint(
        error_code="GENERIC_MISSING_PRECONDITION",
        category=ErrorCategory.MISSING_PRECONDITION,
        experiment_id="general",
        step_index=0,
        level1_question="آیا پیش از اجرای این کنش، تمام پیش‌نیازها و وسایل مرحله آماده شده‌اند؟",
        level2_clue="یکی از ابزارها یا شرایط اولیه هنوز روی میز کار فراهم نشده است.",
        level3_explanation="پیش‌شرط مرحله تامین نشده است. ابتدا وسایل مورد نیاز را به میز منتقل کرده و گام قبلی را تکمیل کنید."
    ),
    ErrorCategory.ORDER_VIOLATION: TieredHint(
        error_code="GENERIC_ORDER_VIOLATION",
        category=ErrorCategory.ORDER_VIOLATION,
        experiment_id="general",
        step_index=0,
        level1_question="آیا مراحل آزمایش را به ترتیبی که در پروتکل درسی آمده دنبال می‌کنید؟",
        level2_clue="این گام به یک نتیجه از گام‌های قبلی وابسته است که هنوز انجام نشده است.",
        level3_explanation="ترتیب گام‌ها نادرست است. لطفاً مطابق دستورالعمل گام‌به‌گام کتاب پیش بروید."
    ),
    ErrorCategory.HAZARDOUS_ACTION: TieredHint(
        error_code="GENERIC_HAZARDOUS_ACTION",
        category=ErrorCategory.HAZARDOUS_ACTION,
        experiment_id="general",
        step_index=0,
        level1_question="آیا این اقدام مطابق با نکات ایمنی آزمایشگاه علوم تجربی است؟",
        level2_clue="انجام این عمل ممکن است به شکستن ظرف یا آسیب حرارتی/شیمیایی منجر شود.",
        level3_explanation="هشدار ایمنی: این اقدام خطرناک است. پیش از ادامه به راهنمای ایمنی کتاب درسی توجه نمایید."
    ),
    ErrorCategory.SCIENTIFIC_MISCONCEPTION: TieredHint(
        error_code="GENERIC_MISCONCEPTION",
        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
        experiment_id="general",
        step_index=0,
        level1_question="آیا پیش‌بینی شما با نتایج علمی و قوانین فیزیک و شیمی تطابق دارد؟",
        level2_clue="مفاهیم متغیر مستقل و وابسته و تعاریف کتاب درسی را بازخوانی کنید.",
        level3_explanation="برداشت مفهومی نادرست است. نتیجه واقعی آزمایش را با قوانین علمی کتاب درسی تطبیق دهید."
    ),
    ErrorCategory.UNSUPPORTED_COMBINATION: TieredHint(
        error_code="GENERIC_UNSUPPORTED_COMBINATION",
        category=ErrorCategory.UNSUPPORTED_COMBINATION,
        experiment_id="general",
        step_index=0,
        level1_question="آیا این دو جزء یا ابزار می‌توانند در این مرحله با یکدیگر ترکیب شوند؟",
        level2_clue="ترکیب انتخابی در برنامه آزمایشگاهی این درس تعریف نشده است.",
        level3_explanation="این ترکیب تعریف نشده است. لطفاً وسایل مجاز را مطابق پروتکل به کار بگیرید."
    )
}
