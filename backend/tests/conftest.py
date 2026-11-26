import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.models.user import User
from backend.app.models.experiment import Experiment
from backend.app.security import get_password_hash, create_access_token

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture()
def sample_teacher(db_session) -> User:
    teacher = User(
        username="test_teacher",
        email="teacher@test.ir",
        hashed_password=get_password_hash("SecretPass123"),
        full_name="دکتر تست مرادی",
        role="teacher",
        grade="متوسطه دوم",
        school_name="دبیرستان البرز"
    )
    db_session.add(teacher)
    db_session.commit()
    db_session.refresh(teacher)
    return teacher

@pytest.fixture()
def sample_student(db_session) -> User:
    student = User(
        username="test_student",
        email="student@test.ir",
        hashed_password=get_password_hash("SecretPass123"),
        full_name="علیرضا دانش‌آموز",
        role="student",
        grade="هشتم",
        school_name="مدرسه رازی"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student

@pytest.fixture()
def second_student(db_session) -> User:
    student2 = User(
        username="second_student",
        email="student2@test.ir",
        hashed_password=get_password_hash("SecretPass123"),
        full_name="رضا رضایی",
        role="student",
        grade="هشتم",
        school_name="مدرسه رازی"
    )
    db_session.add(student2)
    db_session.commit()
    db_session.refresh(student2)
    return student2

@pytest.fixture()
def teacher_auth_headers(sample_teacher: User) -> dict:
    token = create_access_token(data={"sub": str(sample_teacher.id), "role": "teacher"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def student_auth_headers(sample_student: User) -> dict:
    token = create_access_token(data={"sub": str(sample_student.id), "role": "student"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def second_student_auth_headers(second_student: User) -> dict:
    token = create_access_token(data={"sub": str(second_student.id), "role": "student"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def acid_base_experiment(db_session) -> Experiment:
    exp = Experiment(
        slug="acid-base-indicators",
        title="شناسایی اسیدها و بازها با معرف‌های رنگی",
        subject="شیمی",
        grade="هشتم",
        difficulty="آسان",
        duration_minutes=15,
        status="PUBLISHED",
        version=1,
        summary="بررسی تغییر رنگ کاغذ لیتموس آبی و قرمز در محیط‌های اسیدی و بازی",
        thumbnail_type="flask",
        textbook_source={
            "book": "علوم هشتم",
            "grade": "هشتم",
            "chapter": "مخلوط و جداسازی مواد",
            "chapterNumber": 1,
            "page": 6,
            "curriculumCode": "SCI-8-CH1-P6"
        },
        objectives=["شناسایی اسید و باز با لیتموس", "اندازه‌گیری pH"],
        safety_notes=["از لمس مستقیم پرهیز کنید."],
        available_tools=[
            {"id": "beaker-lemon", "name": "بشر آبلیمو (اسید)", "type": "chemical"},
            {"id": "beaker-soda", "name": "بشر جوش شیرین (باز)", "type": "chemical"},
            {"id": "litmus-blue", "name": "کاغذ لیتموس آبی", "type": "tool"},
            {"id": "litmus-red", "name": "کاغذ لیتموس قرمز", "type": "tool"},
            {"id": "ph-meter", "name": "دستگاه pH متر", "type": "measurement"}
        ],
        steps_config=[
            {"index": 1, "title": "آزمون اسید با لیتموس آبی", "hint": "اسید لیتموس آبی را قرمز می‌کند."},
            {"index": 2, "title": "آزمون باز با لیتموس قرمز", "hint": "باز لیتموس قرمز را آبی می‌کند."},
            {"index": 3, "title": "اندازه‌گیری pH", "hint": "مقدار کمتر از ۷ اسیدی است."}
        ]
    )
    db_session.add(exp)
    db_session.commit()
    db_session.refresh(exp)
    return exp

@pytest.fixture()
def mixture_experiment(db_session) -> Experiment:
    exp = Experiment(
        slug="mixture-separation-sand-salt",
        title="جداسازی مخلوط ناهمگن ماسه، نمک و آب",
        subject="شیمی",
        grade="هشتم",
        difficulty="متوسط",
        duration_minutes=20,
        status="PUBLISHED",
        version=1,
        summary="جداسازی فیزیکی اجزای یک مخلوط ناهمگن با انحلال، صاف کردن و تبخیر",
        thumbnail_type="filter",
        textbook_source={
            "book": "علوم هشتم",
            "grade": "هشتم",
            "chapter": "تغییرهای شیمیایی در خدمت زندگی",
            "chapterNumber": 2,
            "page": 16,
            "curriculumCode": "SCI-8-CH2-P16"
        },
        objectives=["انحلال نمک", "فیلتراسیون ماسه", "تبخیر آب و تبلور نمک"],
        safety_notes=["استفاده از عینک ایمنی هنگام کار با چراغ بونزن"],
        available_tools=[
            {"id": "beaker_sand_salt", "name": "بشر ماسه و نمک", "type": "chemical"},
            {"id": "wash_bottle_water", "name": "پیست آب مقطر", "type": "chemical"},
            {"id": "funnel_filter_paper", "name": "قیف و کاغذ صافی", "type": "tool"},
            {"id": "bunsen_burner", "name": "چراغ بونزن", "type": "tool"},
            {"id": "evaporating_dish", "name": "کپسول چینی تبخیر", "type": "tool"}
        ],
        steps_config=[
            {"index": 1, "title": "انحلال نمک در آب", "hint": "نمک در آب حل می‌شود."},
            {"index": 2, "title": "صاف کردن مخلوط با قیف", "hint": "ماسه روی صافی می‌ماند."},
            {"index": 3, "title": "تبخیر آب و بلورشدن نمک", "hint": "با حرارت آب تبخیر و نمک متبلور می‌شود."}
        ]
    )
    db_session.add(exp)
    db_session.commit()
    db_session.refresh(exp)
    return exp

@pytest.fixture()
def circuit_experiment(db_session) -> Experiment:
    exp = Experiment(
        slug="simple-electric-circuit-ohm",
        title="بررسی مدار الکتریکی ساده و قانون اهم",
        subject="فیزیک",
        grade="نهم",
        difficulty="متوسط",
        duration_minutes=20,
        status="PUBLISHED",
        version=1,
        summary="بستن مدار با باتری، کلید و لامپ و بررسی قانون اهم",
        thumbnail_type="zap",
        textbook_source={
            "book": "علوم نهم",
            "grade": "نهم",
            "chapter": "الکتریسیته",
            "chapterNumber": 9,
            "page": 98,
            "curriculumCode": "SCI-9-CH9-P98"
        },
        objectives=["بستن مدار متوالی", "بررسی قانون اهم"],
        safety_notes=["پیشگیری از اتصال کوتاه"],
        available_tools=[
            {"id": "battery_cell", "name": "باتری ۱.۵ ولت", "type": "tool"},
            {"id": "light_bulb", "name": "لامپ رشته‌ای", "type": "tool"},
            {"id": "switch_key", "name": "کلید قطع و وصل", "type": "tool"},
            {"id": "connecting_wires", "name": "سیم‌های رابط", "type": "tool"},
            {"id": "ammeter", "name": "آمپرمتر دیجیتال", "type": "measurement"}
        ],
        steps_config=[
            {"index": 1, "title": "سیم‌کشی مدار", "hint": "حلقه مدار را کامل کنید."},
            {"index": 2, "title": "بستن کلید", "hint": "کلید را روشن کنید."},
            {"index": 3, "title": "اندازه‌گیری جریان", "hint": "آمپرمتر را متصل کنید."}
        ]
    )
    db_session.add(exp)
    db_session.commit()
    db_session.refresh(exp)
    return exp

