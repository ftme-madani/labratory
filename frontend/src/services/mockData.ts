import type { Experiment } from '../types/experiment'
import type { User, UserProgressStats } from '../types/user'
import type { ExperimentAttempt } from '../types/attempt'
import type { TeacherAnalyticsData } from '../types/analytics'

/**
 * داده‌های نمونه برای شبیه‌سازی لایه سرویس (Mock Data Layer)
 * تمام آزمایش‌ها منطبق با منابع کتب درسی مصوب آموزش و پرورش هستند.
 */

export const MOCK_EXPERIMENTS: Experiment[] = [
  {
    id: 'exp-acid-base',
    slug: 'acid-base-indicators',
    title: 'شناسایی و تفکیک اسیدها و بازها با شناساگرهای رنگی',
    subject: 'شیمی',
    grade: 'هشتم',
    difficulty: 'آسان',
    durationMinutes: 15,
    status: 'PUBLISHED',
    version: 1,
    featured: true,
    thumbnailSvgType: 'flask',
    textbook: {
      book: 'علوم تجربی پایه هشتم',
      grade: 'هشتم',
      chapter: 'تغییرهای شیمیایی در خدمت زندگی',
      chapterNumber: 2,
      page: 16,
      curriculumCode: 'SCI-08-CH02-EXP01'
    },
    summary:
      'در این آزمایش با استفاده از کاغذ تورنسل (لیتموس) سرخ و آبی و معرف‌های رنگی، خصلت اسیدی، خنثی یا بازی نمونه‌های مجهول آب‌لیمو، آب‌صابون و آب‌مقطر بررسی و ثبت می‌شود.',
    objectives: [
      'آشنایی با مفهوم شناساگر شیمیایی و تغییر رنگ در محیط‌های اسیدی و بازی',
      'تشخیص اسیدها به کمک تغییر رنگ کاغذ تورنسل آبی به سرخ',
      'تشخیص بازها به کمک تغییر رنگ کاغذ تورنسل سرخ به آبی',
      'بررسی رفتار آب خالص (مقطر) به عنوان ماده خنثی (بدون تغییر رنگ)'
    ],
    safetyNotes: [
      'از چشیدن یا لمس مستقیم محلول‌های شیمیایی خودداری کنید.',
      'هنگام کار با قطره‌چکان از عینک ایمنی آزمایشگاه استفاده نمایید.'
    ],
    availableTools: [
      {
        id: 'beaker_lemon',
        name: 'بشر آب‌لیمو (اسید ضعیف)',
        category: 'reagent',
        iconName: 'Beaker',
        description: 'حاوی اسید سیتریک با pH تقریبی ۲.۵',
        state: 'liquid',
        ph: 2.5
      },
      {
        id: 'beaker_soap',
        name: 'بشر آب‌صابون (محلول بازی)',
        category: 'reagent',
        iconName: 'Beaker',
        description: 'حاوی یون‌های هیدروکسید با pH تقریبی ۹.۵',
        state: 'liquid',
        ph: 9.5
      },
      {
        id: 'beaker_water',
        name: 'بشر آب‌مقطر (خنثی)',
        category: 'reagent',
        iconName: 'Beaker',
        description: 'آب خالص بدون املاح با pH خنثی ۷.۰',
        state: 'liquid',
        ph: 7.0
      },
      {
        id: 'litmus_blue',
        name: 'کاغذ تورنسل آبی',
        category: 'tool',
        iconName: 'TestTube',
        description: 'شناساگر اسید؛ در محیط اسیدی سرخ می‌شود'
      },
      {
        id: 'litmus_red',
        name: 'کاغذ تورنسل سرخ',
        category: 'tool',
        iconName: 'TestTube',
        description: 'شناساگر باز؛ در محیط بازی آبی می‌شود'
      },
      {
        id: 'pipette',
        name: 'قطره‌چکان آزمایشگاهی',
        category: 'tool',
        iconName: 'Pipette',
        description: 'جهت برداشتن و چکاندن کنترل‌شده قطرات معرف'
      }
    ],
    steps: [
      {
        index: 1,
        title: 'بررسی خصلت اسیدی آب‌لیمو',
        instruction: 'کاغذ تورنسل آبی را به محلول آب‌لیمو آغشته کنید و پدیده را مشاهده نمایید.',
        expectedAction: 'DIP_LITMUS_BLUE_INTO_LEMON',
        targetItems: ['litmus_blue', 'beaker_lemon'],
        scientificConcept: 'در حضور یون‌های H+، شناساگر تورنسل ساختار بازی خود را از دست داده و به فرم اسیدی سرخ رنگ تبدیل می‌شود.',
        hintLevels: {
          level1: 'آب‌لیمو مزه ترش دارد. مواد ترش‌مزه در کدام دسته از ترکیبات قرار می‌گیرند؟',
          level2: 'آب‌لیمو اسیدی است. کدام کاغذ تورنسل برای اثبات خاصیت اسیدی استفاده می‌شود؟',
          level3: 'کاغذ تورنسل آبی را انتخاب کرده و در بشر آب‌لیمو فرو ببرید؛ سرخ شدن آن نشانه اسید است.'
        },
        prediction: {
          question: 'به نظر شما پس از تماس کاغذ تورنسل آبی با آب‌لیمو (اسید)، رنگ آن چه تغییری می‌کند؟',
          options: ['سرخ می‌شود (خصلت اسیدی)', 'آبی باقی می‌ماند', 'زرد لیمویی می‌شود'],
          correctOptionIndex: 0,
          explanation: 'محلول‌های اسیدی شناساگر تورنسل آبی را به رنگ سرخ درمی‌آورند.'
        }
      },
      {
        index: 2,
        title: 'بررسی خصلت بازی آب‌صابون',
        instruction: 'کاغذ تورنسل سرخ را به محلول آب‌صابون آغشته کنید و تغییر رنگ را یادداشت نمایید.',
        expectedAction: 'DIP_LITMUS_RED_INTO_SOAP',
        targetItems: ['litmus_red', 'beaker_soap'],
        scientificConcept: 'صابون یک نمک اسید چرب با خاصیت قلیایی (بازی) است و یون OH- آزاد می‌کند که تورنسل سرخ را آبی می‌کند.',
        hintLevels: {
          level1: 'صابون خاصیت لیزکنندگی دارد. این صفت شناسه اسید است یا باز؟',
          level2: 'بازها کاغذ تورنسل سرخ را به چه رنگی تغییر می‌دهند؟',
          level3: 'کاغذ تورنسل سرخ را بردارید و درون بشر آب‌صابون قرار دهید تا رنگ آن به آبی تبدیل شود.'
        },
        prediction: {
          question: 'کاغذ تورنسل سرخ در تماس با محلول بازی آب‌صابون چه تغییری خواهد کرد؟',
          options: ['سرخ باقی می‌ماند', 'به رنگ آبی درمی‌آید (خصلت بازی)', 'بی‌رنگ و شفاف می‌شود'],
          correctOptionIndex: 1,
          explanation: 'مواد قلیایی یا بازها یون‌های OH- آزاد کرده و تورنسل سرخ را به رنگ آبی تغییر می‌دهند.'
        }
      },
      {
        index: 3,
        title: 'بررسی آب خالص به عنوان نمونه خنثی',
        instruction: 'یک قطعه تورنسل آبی و یک قطعه تورنسل سرخ را به آب‌مقطر آغشته نمایید.',
        expectedAction: 'TEST_NEUTRAL_WATER',
        targetItems: ['beaker_water', 'litmus_blue', 'litmus_red'],
        scientificConcept: 'آب مقطر دارای pH برابر ۷ بوده و غلظت یون‌های H+ و OH- در آن برابر است؛ بنابراین هیچ‌کدام از شناساگرها تغییر رنگ نمی‌دهند.',
        hintLevels: {
          level1: 'آیا آب خالص دارای خاصیت اسیدی یا بازی غالب است؟',
          level2: 'در محلول خنثی (pH=7) آیا انتظار تغییر رنگ شناساگر را دارید؟',
          level3: 'هر دو کاغذ تورنسل را در آب مقطر امتحان کنید؛ رنگ هیچ‌یک تغییر نمی‌کند که نشان‌دهنده خنثی بودن است.'
        },
        prediction: {
          question: 'رفتار شناساگرهای تورنسل آبی و سرخ را در آب مقطر خالص (خنثی) پیش‌بینی کنید:',
          options: ['رنگ هیچ‌کدام تغییر نمی‌کند (محیط خنثی)', 'هر دو به رنگ بنفش تیره درمی‌آیند', 'هر دو سرخ‌رنگ می‌شوند'],
          correctOptionIndex: 0,
          explanation: 'آب خالص با pH=۷ خنثی است و غلظت یون‌های هیدرونیوم و هیدروکسید در آن برابر است، لذا رنگ شناساگرها ثابت می‌ماند.'
        }
      }
    ]
  },
  {
    id: 'exp-mixture-separation',
    slug: 'mixture-separation-sand-salt',
    title: 'جداسازی مخلوط ناهمگن و همگن (ماسه، نمک و آب)',
    subject: 'شیمی',
    grade: 'هشتم',
    difficulty: 'متوسط',
    durationMinutes: 20,
    status: 'PUBLISHED',
    version: 1,
    featured: true,
    thumbnailSvgType: 'filter',
    textbook: {
      book: 'علوم تجربی پایه هشتم',
      grade: 'هشتم',
      chapter: 'مخلوط و جداسازی مواد',
      chapterNumber: 1,
      page: 6,
      curriculumCode: 'SCI-08-CH01-EXP02'
    },
    summary:
      'در این آزمایش با تکیه بر تفاوت انحلال‌پذیری و نقطه جوش، مخلوط جامد نمک و ماسه به روش انحلال در آب، صاف‌کردن (فیلتراسیون) و تبخیر حلال از یکدیگر تفکیک می‌شوند.',
    objectives: [
      'به‌کارگیری تفاوت در انحلال‌پذیری مواد به عنوان مبنای جداسازی فیزیکی',
      'یادگیری روش کار با قیف و کاغذ صافی جهت جداسازی رسوب‌های نامحلول',
      'جداسازی ماده حل‌شونده از محلول همگن به روش تبخیر حلال روی حرارت'
    ],
    safetyNotes: [
      'هنگام حرارت دادن کپسول چینی از دستکش نسوز یا انبرک مخصوص بوته استفاده کنید.',
      'به مایع در حال جوش نزدیک نشوید تا از پرتاب قطرات داغ جلوگیری شود.'
    ],
    availableTools: [
      {
        id: 'beaker_sand_salt',
        name: 'بشر مخلوط نمک و ماسه',
        category: 'reagent',
        iconName: 'Beaker',
        description: 'مخلوطی از نمک طعام (NaCl) و ماسه نامحلول (SiO2)'
      },
      {
        id: 'wash_bottle_water',
        name: 'پیست آب‌مقطر',
        category: 'reagent',
        iconName: 'FlaskConical',
        description: 'آب مقطر برای انحلال فاز محلول'
      },
      {
        id: 'glass_stirrer',
        name: 'همزن شیشه‌ای',
        category: 'tool',
        iconName: 'Sparkles',
        description: 'برای تسریع انحلال نمک در آب'
      },
      {
        id: 'funnel_filter_paper',
        name: 'قیف و کاغذ صافی بر روی پایه',
        category: 'tool',
        iconName: 'Filter',
        description: 'جداسازی ذرات نامحلول ماسه از فاز مایع'
      },
      {
        id: 'bunsen_burner',
        name: 'چراغ بونزن و سه‌پایه',
        category: 'tool',
        iconName: 'Flame',
        description: 'منبع گرما برای تبخیر آب'
      },
      {
        id: 'evaporating_dish',
        name: 'کپسول چینی تبخیر',
        category: 'glassware',
        iconName: 'CircleDot',
        description: 'ظرف مقاوم به حرارت برای تبخیر آب‌نمک'
      }
    ],
    steps: [
      {
        index: 1,
        title: 'حل کردن نمک در آب',
        instruction: 'به بشر محتوی ماسه و نمک آب اضافه کنید و با همزن شیشه‌ای به مدت ۳۰ ثانیه هم بزنید.',
        expectedAction: 'ADD_WATER_AND_STIR',
        targetItems: ['beaker_sand_salt', 'wash_bottle_water', 'glass_stirrer'],
        scientificConcept: 'نمک به دلیل قطبی بودن مولکول‌های آب در آن حل می‌شود، اما ماسه پیوند کووالانسی شبکه‌ای داشته و نامحلول می‌ماند.',
        hintLevels: {
          level1: 'کدام جزء مخلوط قابلیت حل شدن در آب را دارد؟',
          level2: 'برای جداسازی، ابتدا باید جزء محلول (نمک) را وارد فاز مایع کنید.',
          level3: 'آب مقطر را درون بشر بریزید و با همزن شیشه‌ای هم بزنید تا نمک کاملاً حل شود.'
        }
      },
      {
        index: 2,
        title: 'فیلتراسیون ماسه با قیف و کاغذ صافی',
        instruction: 'محتویات بشر را از روی قیف و کاغذ صافی عبور دهید تا ماسه جدا شود.',
        expectedAction: 'FILTER_MIXTURE',
        targetItems: ['funnel_filter_paper', 'beaker_sand_salt'],
        scientificConcept: 'روزنه‌های کاغذ صافی به آب و یون‌های محلول اجازه عبور می‌دهند، اما دانه‌های بزرگ ماسه پشت فیلتر باقی می‌مانند.',
        hintLevels: {
          level1: 'چگونه می‌توان یک جامد نامحلول را از یک مایع جدا کرد؟',
          level2: 'از قیف و کاغذ صافی برای به دام انداختن ذرات ماسه استفاده کنید.',
          level3: 'مایع را به آرامی روی قیف حاوی کاغذ صافی بریزید تا ماسه جدا شده و آب‌نمک شفاف در ارلن جمع شود.'
        }
      },
      {
        index: 3,
        title: 'تبخیر آب و بازیابی بلورهای نمک',
        instruction: 'مایع زلال حاصل را درون کپسول چینی ریخته و روی چراغ بونزن حرارت دهید تا آب تبخیر شود.',
        expectedAction: 'EVAPORATE_AND_CRYSTALLIZE',
        targetItems: ['evaporating_dish', 'bunsen_burner'],
        scientificConcept: 'نقطه جوش آب ۱۰۰ درجه سانتی‌گراد است در حالی که نقطه ذوب نمک طعام بیش از ۸۰۰ درجه است؛ بنابراین آب تبخیر شده و نمک متبلور بر جا می‌ماند.',
        hintLevels: {
          level1: 'چگونه نمک حل‌شده در آب را بدون نیاز به دستگاه پیچیده بازیابی کنیم؟',
          level2: 'آب فرار است و در اثر گرما بخار می‌شود، اما نمک غیرفرار است.',
          level3: 'محلول آب‌نمک را در کپسول چینی ریخته و زیر آن شعله بونزن را روشن کنید تا با تبخیر آب، بلورهای سفید نمک ظاهر شوند.'
        }
      }
    ]
  },
  {
    id: 'exp-simple-circuit',
    slug: 'simple-electric-circuit-ohm',
    title: 'بررسی مدار الکتریکی ساده و قانون اهم',
    subject: 'فیزیک',
    grade: 'نهم',
    difficulty: 'متوسط',
    durationMinutes: 15,
    status: 'PUBLISHED',
    version: 1,
    featured: true,
    thumbnailSvgType: 'circuit',
    textbook: {
      book: 'علوم تجربی پایه نهم',
      grade: 'نهم',
      chapter: 'الکتریسیته',
      chapterNumber: 9,
      page: 98,
      curriculumCode: 'SCI-09-CH09-EXP03'
    },
    summary:
      'در این آزمایش مدار الکتریکی متشکل از باتری، کلید و لامپ بسته شده و با اعمال ولتاژهای مختلف، رابطه مستقیم بین اختلاف پتانسیل، شدت جریان و مقاومت بررسی می‌شود.',
    objectives: [
      'فهم مدار بسته و مسیر عبور جریان الکتریکی',
      'بررسی قانون اهم (V = I * R) در اجزای مدار',
      'مشاهده رابطه ولتاژ باتری با میزان روشنایی لامپ'
    ],
    safetyNotes: [
      'از اتصال مستقیم دو قطب باتری بدون مصرف‌کننده (اتصال کوتاه) اکیداً خودداری نمایید.',
      'برای جلوگیری از سوختن لامپ، از منبع تغذیه بیش از ولتاژ نامی لامپ استفاده نکنید.'
    ],
    availableTools: [
      {
        id: 'battery_cell',
        name: 'باتری ۱.۵ ولت قلمی',
        category: 'electric',
        iconName: 'Battery',
        description: 'منبع اختلاف پتانسیل الکتریکی ۱.۵ ولت'
      },
      {
        id: 'switch_key',
        name: 'کلید قطع و وصل تیغه‌ای',
        category: 'electric',
        iconName: 'ToggleLeft',
        description: 'برای باز و بسته کردن مدار'
      },
      {
        id: 'light_bulb',
        name: 'لامپ کوچک ۳ ولتی',
        category: 'electric',
        iconName: 'Lightbulb',
        description: 'مصرف‌کننده الکتریکی با مقاومت درونی مشخص'
      },
      {
        id: 'ammeter',
        name: 'آمپرمتر دیجیتال',
        category: 'sensor',
        iconName: 'Gauge',
        description: 'اندازه‌گیری شدت جریان عبوری به صورت متوالی'
      },
      {
        id: 'connecting_wires',
        name: 'سیم‌های رابط گیره‌سوسماری',
        category: 'electric',
        iconName: 'Zap',
        description: 'اتصال‌دهنده رسانای اجزای مدار'
      }
    ],
    steps: [
      {
        index: 1,
        title: 'بستن اجزای مدار الکتریکی',
        instruction: 'باتری، کلید در حالت باز و لامپ را با سیم‌های رابط در یک حلقه به هم متصل کنید.',
        expectedAction: 'CONNECT_COMPONENTS',
        targetItems: ['battery_cell', 'switch_key', 'light_bulb', 'connecting_wires'],
        scientificConcept: 'برای برقراری جریان باید یک حلقه رسانای بسته بدون انقطاع میان دو قطب مثبت و منفی باتری تشکیل شود.',
        hintLevels: {
          level1: 'الکترون‌ها برای حرکت به چه مسیری نیاز دارند؟',
          level2: 'قطب مثبت باتری باید از طریق کلید به یک پایه لامپ و پایه دیگر لامپ به قطب منفی باتری متصل شود.',
          level3: 'سیم‌های رابط را بین باتری، کلید و لامپ بکشید تا یک حلقه متوالی بسته تشکیل گردد.'
        }
      },
      {
        index: 2,
        title: 'بستن کلید و مشاهده روشنایی لامپ',
        instruction: 'کلید مدار را ببندید تا جریان برقرار شده و لامپ روشن شود.',
        expectedAction: 'CLOSE_SWITCH',
        targetItems: ['switch_key'],
        scientificConcept: 'با بسته شدن کلید، میدان الکتریکی در مدار برقرار شده و عبور جریان از رشته تنگستن لامپ باعث داغ شدن و تابش نور می‌شود.',
        hintLevels: {
          level1: 'آیا در مدار باز جریان الکتریکی برقرار می‌شود؟',
          level2: 'کلید وظیفه کامل کردن مسیر رسانا را بر عهده دارد.',
          level3: 'روی کلید کلیک کنید تا در وضعیت بسته قرار گیرد؛ لامپ بلافاصله روشن خواهد شد.'
        }
      },
      {
        index: 3,
        title: 'اندازه‌گیری شدت جریان و تایید قانون اهم',
        instruction: 'آمپرمتر را به صورت متوالی در مدار قرار دهید و شدت جریان را ثبت کنید.',
        expectedAction: 'MEASURE_CURRENT',
        targetItems: ['ammeter'],
        scientificConcept: 'طبق قانون اهم، نسبت ولتاژ به جریان برابر مقاومت الکتریکی لامپ است: R = V / I.',
        hintLevels: {
          level1: 'آمپرمتر چگونه در مدار قرار می‌گیرد؟ متوالی یا موازی؟',
          level2: 'آمپرمتر دارای مقاومت درونی بسیار کم است و باید به شکل متوالی در مسیر سیم قرار گیرد.',
          level3: 'آمپرمتر را وارد مدار کنید؛ جریان ۰.۱۵ آمپر در ولتاژ ۱.۵ ولت مقاومت ۱۰ اهم را تایید می‌کند.'
        }
      }
    ]
  },
  {
    id: 'exp-vinegar-baking-soda',
    slug: 'vinegar-baking-soda-reaction',
    title: 'واکنش شیمیایی سرکه و جوش‌شیرین (تولید گاز کربن‌دی‌اکسید)',
    subject: 'شیمی',
    grade: 'هشتم',
    difficulty: 'آسان',
    durationMinutes: 15,
    status: 'PUBLISHED',
    version: 1,
    featured: true,
    thumbnailSvgType: 'flask',
    textbook: {
      book: 'علوم تجربی پایه هشتم',
      grade: 'هشتم',
      chapter: 'تغییرهای شیمیایی در خدمت زندگی',
      chapterNumber: 2,
      page: 18,
      curriculumCode: 'SCI-08-CH02-EXP02'
    },
    summary:
      'در این آزمایش با افزودن جوش‌شیرین به سرکه خوراکی، واکنش شیمیایی گرماگیر تولید گاز کربن‌دی‌اکسید، جوشش و ایجاد کف بررسی می‌شود.',
    objectives: [
      'آشنایی با نشانه‌های وقوع واکنش شیمیایی (تولید گاز و تغییر دما)',
      'شناسایی گاز کربن‌دی‌اکسید متصاعدشده در واکنش اسید و کربنات',
      'بررسی مفهوم واکنش‌دهنده محدودکننده در واکنش شیمیایی'
    ],
    safetyNotes: [
      'از بوئیدن مستقیم گازهای متصاعدشده خودداری کنید.',
      'هنگام واکنش و جوشش از عینک آزمایشگاهی استفاده کنید.'
    ],
    availableTools: [
      {
        id: 'beaker_1',
        name: 'بشر آزمایشگاهی ۲۵۰ میلی‌لیتری',
        category: 'glassware',
        iconName: 'Beaker',
        description: 'ظرف شفاف برای مشاهده واکنش و جوشش کف'
      },
      {
        id: 'vinegar_bottle',
        name: 'بطری سرکه خوراکی (اسید استیک ۵٪)',
        category: 'reagent',
        iconName: 'Droplet',
        description: 'محلول اسیدی ضعیف با غلظت مشخص'
      },
      {
        id: 'baking_soda_jar',
        name: 'ظرف جوش‌شیرین (سدیم هیدروژن‌کربنات)',
        category: 'reagent',
        iconName: 'Sparkles',
        description: 'پودر سفید نمک کربناته برای واکنش با اسید'
      }
    ],
    steps: [
      {
        index: 1,
        title: 'انتخاب و آماده‌سازی ظرف آزمایش',
        instruction: 'بشر آزمایشگاهی را انتخاب کرده و روی میز کار قرار دهید.',
        expectedAction: 'SELECT_BEAKER',
        targetItems: ['beaker_1'],
        scientificConcept: 'انجام واکنش در ظرف شفاف آزمایشگاهی امکان مشاهده تشکیل حباب و کف را فراهم می‌سازد.',
        hintLevels: {
          level1: 'آیا ظرف مناسب برای انجام واکنش را انتخاب کرده‌اید؟',
          level2: 'بشر آزمایشگاهی شفاف را از قفسه بردارید.',
          level3: 'روی بشر کلیک کنید تا روی میز کار قرار گیرد.'
        }
      },
      {
        index: 2,
        title: 'افزودن سرکه خوراکی به بشر',
        instruction: 'سرکه را داخل بشر بریزید و مقدار آن را با اسلایدر تنظیم نمایید.',
        expectedAction: 'POUR_VINEGAR',
        targetItems: ['vinegar_bottle', 'beaker_1'],
        scientificConcept: 'اسید استیک با غلظت حدود ۰.۸۳ مولار به عنوان واکنش‌دهنده اسیدی عمل می‌کند.',
        hintLevels: {
          level1: 'کدام مایع اسیدی باید پایه واکنش باشد؟',
          level2: 'سرکه خوراکی را به عنوان منبع اسید به بشر بیفزایید.',
          level3: 'بطری سرکه را برداشته و در بشر بریزید.'
        }
      },
      {
        index: 3,
        title: 'افزودن جوش‌شیرین و مشاهده فوران گاز',
        instruction: 'جوش‌شیرین را به سرکه اضافه کنید و فوران گاز و ایجاد کف را مشاهده کنید.',
        expectedAction: 'ADD_BAKING_SODA',
        targetItems: ['baking_soda_jar', 'beaker_1'],
        scientificConcept: 'واکنش گرماگیر اسید-کربنات منجر به تولید گاز کربن‌دی‌اکسید و کف فوم غلیظ می‌شود.',
        hintLevels: {
          level1: 'واکنش با اضافه شدن کدام ماده آغاز می‌شود؟',
          level2: 'پودر جوش‌شیرین را به بشر حاوی سرکه اضافه کنید.',
          level3: 'جوش‌شیرین را به بشر بیفزایید تا گاز CO2 آزاد شود.'
        },
        prediction: {
          question: 'با افزودن پودر جوش‌شیرین به سرکه، کدام گاز با ایجاد حباب و کف فراوان آزاد می‌شود؟',
          options: ['گاز کربن دی‌اکسید (CO₂)', 'گاز اکسیژن (O₂)', 'گاز هیدروژن اشتعال‌پذیر (H₂)'],
          correctOptionIndex: 0,
          explanation: 'واکنش اسید استیک با بی‌کربنات سدیم گاز CO₂ تولید کرده و ایجاد کف صابونی/گازی می‌کند.'
        }
      },
      {
        index: 4,
        title: 'تحلیل علمی و ثبت معادله واکنش',
        instruction: 'تولید گاز و افت دما را ثبت کرده و معادله موازنه شده را بررسی کنید.',
        expectedAction: 'OBSERVE_REACTION',
        targetItems: ['beaker_1'],
        scientificConcept: 'معادله CH3COOH + NaHCO3 -> CH3COONa + H2O + CO2 نشان‌دهنده موازنه جرم و تولید گاز است.',
        hintLevels: {
          level1: 'گاز خارج‌شده چه گازی است و واکنش چه نوعی است؟',
          level2: 'گاز تولیدشده CO2 است و واکنش گرماگیر می‌باشد.',
          level3: 'نتایج را ثبت و معادله موازنه واکنش را در گزارش تایید کنید.'
        },
        prediction: {
          question: 'تغییرات دمای ظرف را پس از این واکنش شیمیایی پیش‌بینی کنید:',
          options: ['دما اندکی کاهش می‌یابد (واکنش گرماگیر است)', 'دما به شدت بالا می‌رود و بشر داغ می‌شود', 'دما هیچ تغییری نمی‌کند'],
          correctOptionIndex: 0,
          explanation: 'واکنش اسید استیک و بی‌کربنات سدیم گرماگیر است و با جذب انرژی، دمای مخلوط کاهش می‌یابد.'
        }
      }
    ]
  },
  {
    id: 'exp-simple-pendulum',
    slug: 'simple-pendulum-motion',
    title: 'بررسی حرکت نوسانی آونگ ساده و عوامل مؤثر بر دوره تناوب',
    subject: 'فیزیک',
    grade: 'نهم',
    difficulty: 'متوسط',
    durationMinutes: 20,
    status: 'PUBLISHED',
    version: 1,
    featured: true,
    thumbnailSvgType: 'gauge',
    textbook: {
      book: 'علوم تجربی پایه نهم',
      grade: 'نهم',
      chapter: 'حرکت چیست؟',
      chapterNumber: 4,
      page: 44,
      curriculumCode: 'SCI-09-CH04-EXP01'
    },
    summary:
      'بررسی تجربی رابطه دوره تناوب آونگ با طول نخ و جرم وزنه و اثبات رابطه T = 2π√(L/g) در زوایای کوچک.',
    objectives: [
      'بررسی حرکت نوسانی هماهنگ ساده',
      'اندازه‌گیری زمان نوسان و محاسبه دوره تناوب',
      'اثبات عدم وابستگی دوره تناوب به جرم وزنه',
      'تحلیل رابطه خطی مجذور زمان تناوب با طول نخ'
    ],
    safetyNotes: [
      'از کشیدن بیش از حد نخ خودداری کنید.',
      'زاویه انحراف اولیه را کمتر از ۱۵ درجه نگه دارید.'
    ],
    availableTools: [
      {
        id: 'pendulum_stand',
        name: 'پایه و گیره نگهدارنده آونگ',
        category: 'tool',
        iconName: 'Tool',
        description: 'پایه فلزی سنگین جهت تثبیت نقطه آویز'
      },
      {
        id: 'pendulum_string',
        name: 'نخ سبک با طول متغیر',
        category: 'tool',
        iconName: 'GitBranch',
        description: 'نخ آونگ با طول قابل تنظیم از ۰.۲ تا ۱.۵ متر'
      },
      {
        id: 'pendulum_bob',
        name: 'وزنه فلزی آونگ',
        category: 'tool',
        iconName: 'Circle',
        description: 'وزنه استاندارد با جرم ۵۰ تا ۵۰۰ گرم'
      },
      {
        id: 'pendulum_stopwatch',
        name: 'زمان‌سنج دیجیتال دقیق',
        category: 'sensor',
        iconName: 'Clock',
        description: 'تایمر صدم ثانیه برای ثبت زمان نوسان‌ها'
      }
    ],
    steps: [
      {
        index: 1,
        title: 'انتخاب طول نخ و تنظیم پارامترها',
        instruction: 'طول نخ را با اسلایدر انتخاب کرده و پایه را آماده کنید.',
        expectedAction: 'SET_PARAMETERS',
        targetItems: ['pendulum_stand', 'pendulum_string'],
        scientificConcept: 'طول نخ فاصله بین نقطه آویز تا مرکز جرم وزنه است و عامل اصلی تعیین دوره تناوب است.',
        hintLevels: {
          level1: 'کدام کمیت فیزیکی بیشترین تاثیر را در زمان نوسان دارد؟',
          level2: 'طول نخ آونگ را تنظیم کنید.',
          level3: 'اسلایدر طول نخ را روی مقدار دلخواه قرار دهید.'
        }
      },
      {
        index: 2,
        title: 'اتصال وزنه به نخ آونگ',
        instruction: 'وزنه فلزی را به انتهای نخ متصل کنید.',
        expectedAction: 'ATTACH_BOB',
        targetItems: ['pendulum_bob', 'pendulum_string'],
        scientificConcept: 'وزنه نقش جرم نوسان‌گر را ایفا می‌کند و نیروی بازگرداننده آن مولفه مماس وزن است.',
        hintLevels: {
          level1: 'آونگ برای نوسان به چه جزئی نیاز دارد؟',
          level2: 'وزنه را به انتهای نخ وصل کنید.',
          level3: 'وزنه فلزی را از قفسه به نخ متصل نمایید.'
        },
        prediction: {
          question: 'اگر طول نخ ثابت باشد و وزنه سنگین‌تری وصل کنیم، زمان یک نوسان کامل چه تغییری می‌کند؟',
          options: ['زمان نوسان هیچ تغییری نمی‌کند (مستقل از جرم)', 'زمان نوسان کوتاه‌تر می‌شود', 'زمان نوسان طولانی‌تر می‌شود'],
          correctOptionIndex: 0,
          explanation: 'طبق رابطه T = 2π√(L/g)، زمان تناوب آونگ ساده کاملاً مستقل از جرم وزنه معلق است.'
        }
      },
      {
        index: 3,
        title: 'منحرف کردن آونگ از حالت تعادل',
        instruction: 'وزنه را با زاویه کوچک (کمتر از ۱۵ درجه) از وضعیت تعادل منحرف کنید.',
        expectedAction: 'DISPLACE_BOB',
        targetItems: ['pendulum_bob'],
        scientificConcept: 'در زوایای کوچک تر از ۱۵ درجه، تقریب sin(θ) ≈ θ برقرار است و حرکت هماهنگ ساده می‌شود.',
        hintLevels: {
          level1: 'چرا زاویه نوسان باید کوچک باشد؟',
          level2: 'زاویه را روی ۱۰ تا ۱۵ درجه تنظیم کنید.',
          level3: 'وزنه را کمی از خط قائم بکشید تا آماده رهاسازی شود.'
        }
      },
      {
        index: 4,
        title: 'رهاسازی وزنه و ثبت زمان نوسان',
        instruction: 'وزنه را رها کرده و با زمان‌سنج زمان ۱۰ نوسان کامل را اندازه بگیرید.',
        expectedAction: 'RELEASE_AND_MEASURE',
        targetItems: ['pendulum_stopwatch', 'pendulum_bob'],
        scientificConcept: 'دوره تناوب T برابر زمان تقسیم بر تعداد نوسان‌ها است و مستقیماً با رادیکال L متناسب است.',
        hintLevels: {
          level1: 'چگونه دوره تناوب یک نوسان را به دقت حساب کنیم؟',
          level2: 'زمان ۱۰ نوسان را تقسیم بر ۱۰ کنید.',
          level3: 'دکمه رهاسازی را بزنید و پس از ثبت نوسان‌ها نتایج را مشاهده کنید.'
        },
        prediction: {
          question: 'اگر طول نخ آونگ را افزایش دهیم، زمان یک نوسان کامل (دوره تناوب T) چه تغییری می‌کند؟',
          options: ['زمان تناوب افزایش می‌یابد (نوسان کندتر می‌شود)', 'زمان تناوب کاهش می‌یابد', 'طول نخ اثری بر دوره تناوب ندارد'],
          correctOptionIndex: 0,
          explanation: 'با افزایش طول نخ L، شتاب زاویه‌ای کاهش یافته و دوره تناوب طبق رابطه با رادیکال L افزایش می‌یابد.'
        }
      }
    ]
  },
  {
    id: 'exp-plant-transport',
    slug: 'plant-water-transport-celery',
    title: 'بررسی انتقال آب و مواد در آوندهای چوبی ساقه کرفس',
    subject: 'زیست‌شناسی',
    grade: 'هفتم',
    difficulty: 'آسان',
    durationMinutes: 15,
    status: 'PUBLISHED',
    version: 1,
    featured: true,
    thumbnailSvgType: 'leaf',
    textbook: {
      book: 'علوم تجربی پایه هفتم',
      grade: 'هفتم',
      chapter: 'سفر آب درون گیاه (آوندها)',
      chapterNumber: 13,
      page: 112,
      curriculumCode: 'SCI-07-CH13-EXP01'
    },
    summary:
      'مشاهده چگونگی صعود آب و املاح رنگی در آوندهای چوبی ساقه کرفس بر اثر مکش ناشی از تعرق در گذر زمان.',
    objectives: [
      'شناخت آوندهای چوبی و نقش آن‌ها در انتقال شیره خام',
      'بررسی اثر کشش تعرق در صعود آب در گیاه',
      'مشاهده آرایش دسته‌های آوندی در مقطع ساقه کرفس'
    ],
    safetyNotes: [
      'هنگام برش ساقه با تیغ از دستکش ایمنی استفاده کنید.',
      'از مالیدن رنگ خوراکی به چشم یا لباس پرهیز کنید.'
    ],
    availableTools: [
      {
        id: 'transparent_cup',
        name: 'لیوان شیشه‌ای شفاف',
        category: 'glassware',
        iconName: 'Beaker',
        description: 'ظرف نگهدارنده آب و ساقه کرفس'
      },
      {
        id: 'water_pitcher',
        name: 'ظرف آب مقطر',
        category: 'reagent',
        iconName: 'Droplet',
        description: 'آب مورد نیاز برای جذب توسط آوندها'
      },
      {
        id: 'food_coloring_bottle',
        name: 'قطره‌چکان رنگ خوراکی',
        category: 'reagent',
        iconName: 'Pipette',
        description: 'رنگ قرمز یا آبی برای ردگیری مسیر آب'
      },
      {
        id: 'celery_stalk',
        name: 'ساقه تازه کرفس به همراه برگ',
        category: 'tool',
        iconName: 'Leaf',
        description: 'ساقه گیاهی با آوندهای چوبی مشخص'
      }
    ],
    steps: [
      {
        index: 1,
        title: 'ریختن آب در لیوان شفاف',
        instruction: 'لیوان را برداشته و مقداری آب داخل آن بریزید.',
        expectedAction: 'POUR_WATER',
        targetItems: ['water_pitcher', 'transparent_cup'],
        scientificConcept: 'آب به عنوان حلال شیره خام و حامل رنگ در آوندها صعود می‌کند.',
        hintLevels: {
          level1: 'گیاه برای جذب چه ماده‌ای نیاز دارد؟',
          level2: 'آب را داخل لیوان بریزید.',
          level3: 'پارچ آب را در لیوان خالی کنید.'
        }
      },
      {
        index: 2,
        title: 'افزودن قطرات رنگ خوراکی',
        instruction: 'چند قطره رنگ خوراکی سرخ یا آبی به آب اضافه کرده و حل کنید.',
        expectedAction: 'ADD_FOOD_COLORING',
        targetItems: ['food_coloring_bottle', 'transparent_cup'],
        scientificConcept: 'رنگ خوراکی به عنوان ردیاب مسیر حرکت آب در آوندها بدون آسیب به گیاه عمل می‌کند.',
        hintLevels: {
          level1: 'چگونه می‌توان مسیر حرکت آب بی‌رنگ را دید؟',
          level2: 'قطرات رنگ خوراکی را به آب اضافه کنید.',
          level3: 'رنگ خوراکی را به لیوان اضافه نمایید.'
        }
      },
      {
        index: 3,
        title: 'قرار دادن ساقه کرفس در آب رنگی',
        instruction: 'ساقه تازه کرفس را از انتهای بریده شده داخل لیوان قرار دهید.',
        expectedAction: 'INSERT_CELERY',
        targetItems: ['celery_stalk', 'transparent_cup'],
        scientificConcept: 'سطح مقطع بریده شده ساقه ارتباط مستقیم آوندهای چوبی با محلول رنگی را برقرار می‌کند.',
        hintLevels: {
          level1: 'کدام اندام گیاهی باید درون آب قرار گیرد؟',
          level2: 'ساقه کرفس را داخل لیوان بگذارید.',
          level3: 'ساقه کرفس را به لیوان اضافه کنید.'
        }
      },
      {
        index: 4,
        title: 'مشاهده گذر زمان و صعود آب در آوندها',
        instruction: 'زمان شبیه‌سازی را جلو ببرید و صعود رنگ در ساقه و رگبرگ‌ها را بررسی کنید.',
        expectedAction: 'SIMULATE_TIME',
        targetItems: ['celery_stalk'],
        scientificConcept: 'کشش ناشی از تعرق در برگ‌ها ستون پیوسته آب را به تدریج بالا می‌کشد.',
        hintLevels: {
          level1: 'آیا صعود آب فوراً رخ می‌دهد؟',
          level2: 'اسلایدر زمان را روی ساعت‌های مختلف قرار دهید.',
          level3: 'زمان را روی ۱۲ یا ۲۴ ساعت قرار دهید تا اثر تعرق را ببینید.'
        }
      },
      {
        index: 5,
        title: 'بررسی مقطع عرضی ساقه و مشاهده آوندها',
        instruction: 'نمای برش عرضی را فعال کرده و نقاط رنگی آوندهای چوبی را ببینید.',
        expectedAction: 'OBSERVE_CROSS_SECTION',
        targetItems: ['celery_stalk'],
        scientificConcept: 'نقاط رنگی نمایانگر دسته‌های آوندی چوبی در حاشیه ساقه هستند.',
        hintLevels: {
          level1: 'آوندها در کجای ساقه واقع شده‌اند؟',
          level2: 'دکمه نمای برش عرضی را انتخاب کنید.',
          level3: 'برش میکروسکوپی را تماشا و یادداشت نمایید.'
        }
      }
    ]
  },
  {
    id: 'exp-density-column',
    slug: 'liquid-density-column',
    title: 'بررسی چگالی و امتزاج‌ناپذیری در تشکیل برج مایعات',
    subject: 'شیمی و فیزیک',
    grade: 'هفتم',
    difficulty: 'آسان',
    durationMinutes: 15,
    status: 'PUBLISHED',
    version: 1,
    featured: true,
    thumbnailSvgType: 'test-tube',
    textbook: {
      book: 'علوم تجربی پایه هفتم',
      grade: 'هفتم',
      chapter: 'اندازه‌گیری در علوم و ابزارهای آن',
      chapterNumber: 2,
      page: 14,
      curriculumCode: 'SCI-07-CH02-EXP02'
    },
    summary:
      'بررسی قرارگیری لایه‌ای عسل، آب و روغن بر اساس تفاوت چگالی (d = m/V) و امتزاج‌ناپذیری.',
    objectives: [
      'آشنایی با مفهوم چگالی و نحوه محاسبه آن (d = m/V)',
      'مقایسه چگالی مایعات مختلف (عسل > آب > روغن)',
      'درک نقش امتزاج‌ناپذیری مایعات در پایداری مرز لایه‌ها'
    ],
    safetyNotes: [
      'از ریختن سریع مایعات برای جلوگیری از تلاطم خودداری کنید.',
      'مایعات آزمایشگاهی را نچشید.'
    ],
    availableTools: [
      {
        id: 'graduated_cylinder',
        name: 'استوانه مدرج شیشه‌ای ۲۵۰ میلی‌لیتری',
        category: 'glassware',
        iconName: 'Beaker',
        description: 'ظرف باریک و دقیق برای تشکیل ستون مایعات'
      },
      {
        id: 'honey_jar',
        name: 'ظرف عسل غلیظ (چگالی ۱.۴۲)',
        category: 'reagent',
        iconName: 'Droplet',
        description: 'مایع با چگالی بالا و گرانروی زیاد'
      },
      {
        id: 'water_beaker',
        name: 'بشر آب معمولی (چگالی ۱.۰۰)',
        category: 'reagent',
        iconName: 'Droplets',
        description: 'مایع میانی قطبی استاندارد'
      },
      {
        id: 'oil_bottle',
        name: 'بطری روغن مایع خوراکی (چگالی ۰.۹۱)',
        category: 'reagent',
        iconName: 'Droplet',
        description: 'مایع سبک ناقطبی شناور'
      }
    ],
    steps: [
      {
        index: 1,
        title: 'آماده‌سازی استوانه مدرج',
        instruction: 'استوانه مدرج شفاف را انتخاب و روی میز کار بگذارید.',
        expectedAction: 'PREPARE_CONTAINER',
        targetItems: ['graduated_cylinder'],
        scientificConcept: 'استوانه مدرج باریک مناسب‌ترین ظرف برای بررسی مرز لایه‌های مایعات است.',
        hintLevels: {
          level1: 'ظرف شفاف مدرج را انتخاب کنید.',
          level2: 'استوانه مدرج را از قفسه بردارید.',
          level3: 'روی استوانه مدرج کلیک کنید.'
        }
      },
      {
        index: 2,
        title: 'ریختن عسل به عنوان چگال‌ترین مایع',
        instruction: 'عسل را به آرامی در کف استوانه بریزید.',
        expectedAction: 'POUR_HONEY',
        targetItems: ['honey_jar', 'graduated_cylinder'],
        scientificConcept: 'عسل با چگالی ۱.۴۲ گرم بر سانتی‌متر مکعب در پایین‌ترین سطح قرار می‌گیرد.',
        hintLevels: {
          level1: 'کدام مایع چگال‌تر از بقیه است؟',
          level2: 'عسل بیشترین چگالی را دارد؛ آن را در کف بریزید.',
          level3: 'دکمه ریختن عسل را بزنید.'
        }
      },
      {
        index: 3,
        title: 'افزودن آب به عنوان لایه میانی',
        instruction: 'آب را به آرامی روی لایه عسل بریزید.',
        expectedAction: 'POUR_WATER',
        targetItems: ['water_beaker', 'graduated_cylinder'],
        scientificConcept: 'آب با چگالی ۱.۰۰ روی عسل شناور می‌ماند و لایه میانی را تشکیل می‌دهد.',
        hintLevels: {
          level1: 'مایع با چگالی متوسط کدام است؟',
          level2: 'آب را به آرامی اضافه کنید.',
          level3: 'دکمه افزودن آب را فشار دهید.'
        },
        prediction: {
          question: 'وقتی آب را به آرامی روی لایه عسل می‌ریزیم چه اتفاقی می‌افتد؟',
          options: ['آب روی عسل شناور می‌ماند (چگالی آب کمتر از عسل است)', 'آب زیر عسل فرو می‌رود', 'آب و عسل بلافاصله کاملاً با هم مخلوط می‌شوند'],
          correctOptionIndex: 0,
          explanation: 'چگالی عسل ۱.۴۲ و چگالی آب ۱.۰۰ g/cm³ است، بنابراین آب روی عسل شناور می‌ماند.'
        }
      },
      {
        index: 4,
        title: 'افزودن روغن به عنوان سبک‌ترین مایع',
        instruction: 'روغن را روی لایه آب بریزید و شناور ماندن آن را ببینید.',
        expectedAction: 'POUR_OIL',
        targetItems: ['oil_bottle', 'graduated_cylinder'],
        scientificConcept: 'روغن با چگالی ۰.۹۱ به دلیل کمترین چگالی و ناقطبی بودن روی آب می‌ایستد.',
        hintLevels: {
          level1: 'کمترین چگالی متعلق به کدام مایع است؟',
          level2: 'روغن مایع را به استوانه اضافه کنید.',
          level3: 'دکمه افزودن روغن را بزنید.'
        }
      },
      {
        index: 5,
        title: 'مشاهده و تحلیل پایداری لایه‌ها',
        instruction: 'مرز سه لایه را مشاهده کرده و ارتباط آن با چگالی و امتزاج‌ناپذیری را یادداشت کنید.',
        expectedAction: 'OBSERVE_LAYERS',
        targetItems: ['graduated_cylinder'],
        scientificConcept: 'لایه‌ها پایدار می‌مانند زیرا علاوه بر اختلاف چگالی، آب و روغن در یکدیگر حل نمی‌شوند.',
        hintLevels: {
          level1: 'چرا آب و روغن مخلوط نمی‌شوند؟',
          level2: 'عدم امتزاج‌پذیری ناشی از تفاوت قطبیت است.',
          level3: 'نتایج آزمایش را در گزارش ثبت نمایید.'
        },
        prediction: {
          question: 'علاوه بر اختلاف چگالی، چه عامل مهم دیگری باعث پایداری مرز بین آب و روغن می‌شود؟',
          options: ['امتزاج‌ناپذیری (آب قطبی و روغن ناقطبی است و در هم حل نمی‌شوند)', 'رنگ متفاوت مایعات', 'دمای متفاوت مایعات'],
          correctOptionIndex: 0,
          explanation: 'چگالی تعیین‌کننده موقعیت لایه‌هاست، اما امتزاج‌ناپذیری مانع از انحلال مولکول‌های روغن در آب می‌شود.'
        }
      }
    ]
  },
  {
    id: 'exp-water-filtration',
    slug: 'water-filtration-column',
    title: 'ساخت صافی چندلایه آب و جداسازی فیزیکی ذرات معلق',
    subject: 'شیمی',
    grade: 'هشتم',
    difficulty: 'متوسط',
    durationMinutes: 20,
    status: 'PUBLISHED',
    version: 1,
    featured: true,
    thumbnailSvgType: 'filter',
    textbook: {
      book: 'علوم تجربی پایه هشتم',
      grade: 'هشتم',
      chapter: 'مخلوط و جداسازی مواد',
      chapterNumber: 1,
      page: 8,
      curriculumCode: 'SCI-08-CH01-EXP02'
    },
    summary:
      'بررسی تصفیه مکانیکی آب گل‌آلود با چینش علمی لایه‌های پنبه، ماسه ریز و شن درشت در ستون صافی.',
    objectives: [
      'آشنایی با اصول جداسازی فیزیکی مخلوط‌های معلق (سوسپانسیون)',
      'درک نقش چینش اندازه ذرات در لایه‌های صافی (از درشت به ریز)',
      'فهم تفاوت زلال‌سازی فیزیکی با ضدعفونی میکروبی آب'
    ],
    safetyNotes: [
      'هشدار مهم: آب خروجی این صافی به هیچ وجه قابل شرب نیست!',
      'از نوشیدن یا چشیدن آب تصفیه شده پرهیز نمایید.'
    ],
    availableTools: [
      {
        id: 'plastic_bottle',
        name: 'بطری پلاستیکی وارونه با پایه',
        category: 'tool',
        iconName: 'Filter',
        description: 'ستون شفاف برای قرار دادن لایه‌های فیلتر'
      },
      {
        id: 'cotton_layer',
        name: 'پنبه متراکم (لایه اول)',
        category: 'tool',
        iconName: 'Layers',
        description: 'لایه زیرین برای فیلتر نهایی و ممانعت از خروج ماسه'
      },
      {
        id: 'sand_layer',
        name: 'ماسه ریز شسته‌شده (لایه میانی)',
        category: 'tool',
        iconName: 'Layers',
        description: 'لایه میانی برای به دام انداختن ذرات ریز خاک'
      },
      {
        id: 'gravel_layer',
        name: 'شن درشت (لایه بالایی)',
        category: 'tool',
        iconName: 'Layers',
        description: 'لایه آغازین برای به دام انداختن آشغال‌ها و ذرات درشت'
      },
      {
        id: 'turbid_water_beaker',
        name: 'بشر آب گل‌آلود و کدر',
        category: 'reagent',
        iconName: 'Droplets',
        description: 'مخلوط سوسپانسیون آب و خاک با کدورت بالا'
      },
      {
        id: 'collection_cup',
        name: 'ظرف جمع‌آوری آب تصفیه‌شده',
        category: 'glassware',
        iconName: 'Beaker',
        description: 'ظرف شفاف زیر صافی جهت مقایسه زلالی آب'
      }
    ],
    steps: [
      {
        index: 1,
        title: 'آماده‌سازی بطری وارونه',
        instruction: 'بطری پلاستیکی را وارونه کرده و روی پایه قرار دهید.',
        expectedAction: 'PREPARE_BOTTLE',
        targetItems: ['plastic_bottle'],
        scientificConcept: 'دهانه باریک در پایین و دهانه گشاد در بالا ساختاری ایده‌آل برای ستون صافی ایجاد می‌کند.',
        hintLevels: {
          level1: 'ظرف اصلی فیلتر را آماده کنید.',
          level2: 'بطری وارونه را روی پایه قرار دهید.',
          level3: 'روی بطری کلیک کنید تا در جایگاه قرار گیرد.'
        }
      },
      {
        index: 2,
        title: 'چیدمان صحیح لایه‌های صافی',
        instruction: 'لایه‌ها را به ترتیب: پنبه در کف، ماسه در میانه و شن در بالا بچینید.',
        expectedAction: 'ARRANGE_FILTER_LAYERS',
        targetItems: ['cotton_layer', 'sand_layer', 'gravel_layer'],
        scientificConcept: 'عبور آب از لایه‌های با تخلخل درشت به ریز مانع از گرفتگی سریع فیلتر می‌شود.',
        hintLevels: {
          level1: 'ترتیب اندازه منافذ از بالا به پایین چگونه باید باشد؟',
          level2: 'شن درشت بالا، ماسه در وسط و پنبه در پایین قرار می‌گیرد.',
          level3: 'لایه‌ها را به ترتیب صحیح در بطری بچینید.'
        }
      },
      {
        index: 3,
        title: 'ریختن آب گل‌آلود در صافی',
        instruction: 'آب کدر را به آرامی روی لایه شن بریزید.',
        expectedAction: 'POUR_DIRTY_WATER',
        targetItems: ['turbid_water_beaker', 'plastic_bottle'],
        scientificConcept: 'آب گل‌آلود تحت اثر گرانش از میان منافذ عبور می‌کند.',
        hintLevels: {
          level1: 'آب ناخالص را به صافی بیفزایید.',
          level2: 'آب گل‌آلود را روی لایه بالایی بریزید.',
          level3: 'دکمه ریختن آب گل‌آلود را بزنید.'
        }
      },
      {
        index: 4,
        title: 'مشاهده فرآیند فیلتراسیون',
        instruction: 'گذر آب از لایه‌ها و به‌دام‌افتادن ذرات معلق را تماشا کنید.',
        expectedAction: 'OBSERVE_FILTRATION',
        targetItems: ['plastic_bottle'],
        scientificConcept: 'تخلخل دانه‌ها باعث جداسازی فیزیکی ذرات معلق خاکی از آب می‌شود.',
        hintLevels: {
          level1: 'ذرات گل در کدام لایه‌ها گیر می‌افتند؟',
          level2: 'به‌دام‌افتادن ذرات در ماسه و شن را ببینید.',
          level3: 'فرآیند تراوش آب را دنبال کنید.'
        }
      },
      {
        index: 5,
        title: 'مقایسه آب خروجی و ثبت هشدارهای بهداشتی',
        instruction: 'آب زلال خروجی را بررسی کرده و هشدار عدم آشامیدن را تایید کنید.',
        expectedAction: 'COMPARE_AND_EVALUATE',
        targetItems: ['collection_cup'],
        scientificConcept: 'کدورت آب از ۲۵۰ به ۱۲ NTU کاهش می‌یابد اما عاری از میکروب و نمک محلول نیست.',
        hintLevels: {
          level1: 'آیا آب زلال این صافی قابل نوشیدن است؟',
          level2: 'خیر! این آب هنوز حاوی میکروب‌ها و باکتری‌هاست.',
          level3: 'هشدار ایمنی را مطالعه کرده و آزمایش را به اتمام برسانید.'
        },
        prediction: {
          question: 'به نظر شما آیا آب زلال خارج‌شده از این صافی مکانیکی، قابل نوشیدن و گواراست؟',
          options: ['خیر! صافی فیزیکی میکروب‌ها و املاح را حذف نمی‌کند و نباید نوشیده شود', 'بله، آب کاملاً شفاف و عاری از هرگونه آلودگی است'],
          correctOptionIndex: 0,
          explanation: 'تصفیه فیزیکی فقط ذرات معلق خاکی را جدا می‌کند؛ باکتری‌ها، ویروس‌ها و سموم محلول در آب باقی می‌مانند و نوشیدن آن خطرساز است.'
        }
      }
    ]
  }
]

export const MOCK_USER: User = {
  id: 'usr-student-01',
  username: 'alireza_ahmadi',
  fullName: 'علیرضا احمدی',
  email: 'alireza@school.ir',
  role: 'student',
  grade: 'هشتم',
  schoolName: 'دبیرستان دوره اول شهید بهشتی',
  avatarUrl: '',
  createdAt: '2026-09-23T08:00:00Z'
}

export const MOCK_TEACHER: User = {
  id: 'usr-teacher-01',
  username: 'dr_moradi',
  fullName: 'دکتر مریم مرادی',
  email: 'm.moradi@edu.ir',
  role: 'teacher',
  schoolName: 'مجتمع آموزشی فرزانگان',
  createdAt: '2026-08-15T10:00:00Z'
}

export const MOCK_STUDENT_STATS: UserProgressStats = {
  completedExperiments: 2,
  totalAttempts: 4,
  averageScore: 92,
  hintsRequestedTotal: 3,
  badges: [
    {
      id: 'badge-chemist',
      title: 'شیمیدان کنجکاو',
      description: 'تکمیل موفقیت‌آمیز آزمایش اسید و باز با دقت بالای ۹۰٪',
      icon: 'FlaskConical',
      earnedAt: '2026-10-20'
    },
    {
      id: 'badge-safe-lab',
      title: 'رعایت‌کننده ایمنی',
      description: 'انجام بدون نقص مراحل و بدون وقوع خطای انتخاب وسیله',
      icon: 'ShieldCheck',
      earnedAt: '2026-10-22'
    },
    {
      id: 'badge-explorer',
      title: 'پژوهشگر جوان',
      description: 'استفاده هوشمندانه از راهنمایی‌های مفهومی سطح ۱',
      icon: 'Sparkles',
      earnedAt: '2026-10-25'
    }
  ]
}

export const MOCK_ATTEMPTS: ExperimentAttempt[] = [
  {
    id: 'att-101',
    userId: 'usr-student-01',
    experimentId: 'exp-acid-base',
    experimentSlug: 'acid-base-indicators',
    experimentTitle: 'شناسایی و تفکیک اسیدها و بازها با شناساگرهای رنگی',
    grade: 'هشتم',
    subject: 'شیمی',
    startedAt: '2026-10-25T10:14:00Z',
    completedAt: '2026-10-25T10:26:00Z',
    status: 'COMPLETED',
    score: 95,
    stepsCompleted: 3,
    totalSteps: 3,
    actionsLog: [
      {
        stepIndex: 1,
        timestamp: '2026-10-25T10:16:00Z',
        actionType: 'MIX',
        itemIds: ['litmus_blue', 'beaker_lemon'],
        isValid: true,
        observationText: 'کاغذ تورنسل آبی به رنگ سرخ درآمد ($pH \approx 2.5$).',
        feedbackText: 'آفرین! شناساگر با موفقیت ویژگی اسیدی آب‌لیمو را نشان داد.'
      },
      {
        stepIndex: 2,
        timestamp: '2026-10-25T10:20:00Z',
        actionType: 'MIX',
        itemIds: ['litmus_red', 'beaker_soap'],
        isValid: true,
        observationText: 'کاغذ تورنسل سرخ به رنگ آبی متمایل شد ($pH \approx 9.5$).',
        feedbackText: 'درست است! خاصیت بازی آب‌صابون اثبات شد.'
      },
      {
        stepIndex: 3,
        timestamp: '2026-10-25T10:24:00Z',
        actionType: 'MIX',
        itemIds: ['litmus_blue', 'beaker_water'],
        isValid: true,
        observationText: 'کاغذ تورنسل در آب مقطر تغییری نکرد ($pH = 7.0$).',
        feedbackText: 'عالی! آب مقطر نمونه خنثی است.'
      }
    ],
    observations: [
      'آب‌لیمو اسیدی است و تورنسل آبی را سرخ می‌کند.',
      'آب‌صابون بازی است و تورنسل سرخ را آبی می‌کند.',
      'آب مقطر خنثی است و روی شناساگرها بی‌اثر است.'
    ],
    hintsUsed: [
      {
        stepIndex: 1,
        level: 1,
        content: 'آب‌لیمو مزه ترش دارد. مواد ترش‌مزه در کدام دسته ترکیبات هستند؟',
        requestedAt: '2026-10-25T10:15:00Z'
      }
    ]
  },
  {
    id: 'att-102',
    userId: 'usr-student-01',
    experimentId: 'exp-mixture-separation',
    experimentSlug: 'mixture-separation-sand-salt',
    experimentTitle: 'جداسازی مخلوط ناهمگن و همگن (ماسه، نمک و آب)',
    grade: 'هشتم',
    subject: 'شیمی',
    startedAt: '2026-10-26T14:00:00Z',
    completedAt: '2026-10-26T14:18:00Z',
    status: 'COMPLETED',
    score: 88,
    stepsCompleted: 3,
    totalSteps: 3,
    actionsLog: [
      {
        stepIndex: 1,
        timestamp: '2026-10-26T14:04:00Z',
        actionType: 'MIX',
        itemIds: ['beaker_sand_salt', 'wash_bottle_water'],
        isValid: true,
        observationText: 'نمک در آب حل شد اما ماسه ته‌نشین شد.',
        feedbackText: 'انحلال‌پذیری تفکیکی به درستی اعمال شد.'
      },
      {
        stepIndex: 2,
        timestamp: '2026-10-26T14:10:00Z',
        actionType: 'HEAT',
        itemIds: ['funnel_filter_paper'],
        isValid: true,
        observationText: 'ماسه روی کاغذ صافی ماند و آب‌نمک شفاف عبور کرد.',
        feedbackText: 'فیلتراسیون با موفقیت انجام شد.'
      },
      {
        stepIndex: 3,
        timestamp: '2026-10-26T14:16:00Z',
        actionType: 'HEAT',
        itemIds: ['evaporating_dish', 'bunsen_burner'],
        isValid: true,
        observationText: 'آب تبخیر شد و بلورهای سفید نمک در کپسول چینی باقی ماندند.',
        feedbackText: 'تبخیر کامل شد و نمک طعام بازیابی گشت.'
      }
    ],
    observations: [
      'ماسه در آب نامحلول است و با صاف کردن جدا شد.',
      'نمک با تبخیر آب متبلور شد.'
    ],
    hintsUsed: [
      {
        stepIndex: 2,
        level: 1,
        content: 'چگونه می‌توان جامد نامحلول را از مایع جدا کرد؟',
        requestedAt: '2026-10-26T14:08:00Z'
      },
      {
        stepIndex: 2,
        level: 2,
        content: 'از قیف و کاغذ صافی استفاده نمایید.',
        requestedAt: '2026-10-26T14:09:00Z'
      }
    ]
  }
]

export const MOCK_TEACHER_ANALYTICS: TeacherAnalyticsData = {
  totalStudents: 34,
  activeExperimentsCount: 3,
  averageCompletionRate: 86.4,
  frequentErrors: [
    {
      errorCode: 'ERR_ORDER_VIOLATION_HEATING',
      errorTitle: 'حرارت دادن پیش از فیلتراسیون',
      experimentTitle: 'جداسازی مخلوط ماسه، نمک و آب',
      occurrenceCount: 18,
      scientificConcept: 'حرارت دادن مخلوط همراه با ماسه باعث سوختن یا پاشش رسوب شده و تفکیک را مخدوش می‌کند.',
      recommendedRemediation: 'تاکید بر ترتیب گام‌ها: ابتدا فیلتر کردن ماسه، سپس حرارت دادن مایع زلال.'
    },
    {
      errorCode: 'ERR_WRONG_INDICATOR_SELECTION',
      errorTitle: 'استفاده از تورنسل سرخ برای محیط اسیدی',
      experimentTitle: 'شناسایی و تفکیک اسیدها و بازها',
      occurrenceCount: 12,
      scientificConcept: 'تورنسل سرخ در محیط اسیدی تغییر رنگ نمی‌دهد و نمی‌تواند مستقیماً اسیدی بودن را اثبات نماید.',
      recommendedRemediation: 'مرور جدول رنگ‌های معرف‌های اسید-باز در پایه هشتم.'
    },
    {
      errorCode: 'ERR_SHORT_CIRCUIT_RISK',
      errorTitle: 'تلاش برای بستن مدار بدون مقاومت مصرف‌کننده',
      experimentTitle: 'بررسی مدار الکتریکی ساده و قانون اهم',
      occurrenceCount: 9,
      scientificConcept: 'اتصال سیم‌های باتری به یکدیگر بدون لامپ موجب داغ شدن سیم و تخلیه ناگهانی (اتصال کوتاه) می‌گردد.',
      recommendedRemediation: 'آموزش هشدارهای ایمنی در مبحث الکتریسیته پایه نهم.'
    }
  ],
  experimentStats: [
    {
      experimentId: 'exp-acid-base',
      experimentTitle: 'شناسایی اسیدها و بازها با شناساگر',
      totalAttempts: 32,
      completionRatePercent: 94,
      averageScorePercent: 91.5,
      averageHintsUsed: 1.2
    },
    {
      experimentId: 'exp-mixture-separation',
      experimentTitle: 'جداسازی مخلوط ماسه، نمک و آب',
      totalAttempts: 29,
      completionRatePercent: 82,
      averageScorePercent: 84.0,
      averageHintsUsed: 2.1
    },
    {
      experimentId: 'exp-simple-circuit',
      experimentTitle: 'مدار الکتریکی ساده و قانون اهم',
      totalAttempts: 25,
      completionRatePercent: 80,
      averageScorePercent: 82.5,
      averageHintsUsed: 1.8
    }
  ]
}
