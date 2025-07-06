from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Date,
    Time,
    Enum,
    ForeignKey,
    Table,
    CHAR,
    JSON,
)
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum as EnumType
import uuid

Base = declarative_base()

# Bảng trung gian cho mối quan hệ Many-to-Many giữa Artist và Service
artist_service_association = Table(
    "artist_services",
    Base.metadata,
    Column("artist_id", CHAR(36), ForeignKey("artists.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.now),
)


class Gender(str, EnumType):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class DayOfWeek(str, EnumType):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Status(str, EnumType):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    REFUND_REQUESTED = "refund_requested"
    REFUND_APPROVED = "refund_approved"


class Customer(Base):
    __tablename__ = "customers"
    id = Column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    first_name = Column(String(255), index=True, nullable=False)
    last_name = Column(String(255), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), index=True, nullable=False)
    gender = Column(Enum(Gender), index=True, nullable=False)
    date_of_birth = Column(Date, index=True, nullable=False)

    status = Column(Enum(Status), index=True, default=Status.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    appointments = relationship("Appointment", back_populates="customer")


class Salon(Base):
    __tablename__ = "salons"
    id = Column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    name = Column(String(255), index=True, nullable=False)
    address = Column(String(255), index=True, nullable=False)
    phone_number = Column(String(20), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    opening_hours = Column(Time, index=True, nullable=False)
    closing_hours = Column(Time, index=True, nullable=False)
    opening_days = Column(
        JSON,
        default=lambda: [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ],
        nullable=False,
    )
    status = Column(Enum(Status), index=True, default=Status.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    location = relationship("Location", back_populates="salons")
    artists = relationship("Artist", back_populates="salon")


class Location(Base):
    __tablename__ = "locations"
    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    location = Column(String(255), index=True)

    # Metadata
    status = Column(Enum(Status), index=True, default=Status.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    salons = relationship("Salon", back_populates="location")


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sub_category_id = Column(
        Integer, ForeignKey("service_sub_categories.id"), index=True
    )
    category_id = Column(Integer, ForeignKey("service_categories.id"), index=True)
    name = Column(String(255), index=True, nullable=False)

    status = Column(Enum(Status), index=True, default=Status.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    service_details = relationship("ServiceDetail", back_populates="service")
    appointments = relationship("Appointment", back_populates="service")
    artists = relationship(
        "Artist", secondary=artist_service_association, back_populates="services"
    )
    service_sub_category = relationship("ServiceSubCategory", back_populates="services")
    service_category = relationship("ServiceCategory", back_populates="services")


class ServiceCategory(Base):
    __tablename__ = "service_categories"
    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    name = Column(String(255), index=True, nullable=False)

    status = Column(Enum(Status), index=True, default=Status.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    services = relationship("Service", back_populates="service_category")
    service_sub_categories = relationship(
        "ServiceSubCategory", back_populates="service_category"
    )


class ServiceSubCategory(Base):
    __tablename__ = "service_sub_categories"
    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    name = Column(String(255), index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("service_categories.id"), index=True)

    status = Column(Enum(Status), index=True, default=Status.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    service_category = relationship(
        "ServiceCategory", back_populates="service_sub_categories"
    )
    services = relationship("Service", back_populates="service_sub_category")


class ServiceDetail(Base):
    __tablename__ = "service_details"
    id = Column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    service_id = Column(Integer, ForeignKey("services.id"), index=True)

    description = Column(String(1000))
    duration = Column(Integer, index=True)
    listed_price = Column(Float, index=True)
    listed_price_2_sessions = Column(Float, index=True)
    currency = Column(String(10), index=True, default="AUD")

    status = Column(Enum(Status), index=True, default=Status.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    service = relationship("Service", back_populates="service_details")


class Artist(Base):
    __tablename__ = "artists"
    id = Column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    name = Column(String(255), index=True)
    description = Column(String(1000))
    salon_id = Column(CHAR(36), ForeignKey("salons.id"), index=True)
    languages = Column(String(255), index=True, nullable=False)
    experience_years = Column(Integer, index=True, nullable=False)
    strengths = Column(String(1000))
    status = Column(Enum(Status), index=True, default=Status.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Many-to-Many relationship với Service
    services = relationship(
        "Service", secondary=artist_service_association, back_populates="artists"
    )
    salon = relationship("Salon", back_populates="artists")
    appointments = relationship("Appointment", back_populates="artist")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    customer_id = Column(CHAR(36), ForeignKey("customers.id"), index=True)
    artist_id = Column(CHAR(36), ForeignKey("artists.id"), index=True)
    service_id = Column(Integer, ForeignKey("services.id"), index=True)
    appointment_time = Column(DateTime, index=True)
    note = Column(String(1000))

    status = Column(Enum(Status), index=True, default=Status.PENDING)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    customer = relationship("Customer", back_populates="appointments")
    artist = relationship("Artist", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")


def create_tables():
    """Tạo tất cả các bảng trong database"""
    from app.core.db.base import engine

    print("Đang tạo các bảng trong database...")
    try:
        # Tạo tất cả bảng
        Base.metadata.create_all(bind=engine)
        print("✅ Tất cả bảng đã được tạo thành công!")

        # In danh sách các bảng đã tạo
        print("\n📋 Các bảng đã tạo:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

    except Exception as e:
        print(f"❌ Lỗi khi tạo bảng: {e}")
        raise


def drop_tables():
    """Xóa tất cả các bảng (cẩn thận!)"""
    from app.core.db.base import engine

    print("⚠️  CẢNH BÁO: Đang xóa tất cả bảng...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Tất cả bảng đã được xóa!")
    except Exception as e:
        print(f"❌ Lỗi khi xóa bảng: {e}")
        raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "drop_n_create":
        # Chạy: python create_db.py drop_n_create
        drop_tables()
        create_tables()
    else:
        # Chạy: python create_db.py
        create_tables()
