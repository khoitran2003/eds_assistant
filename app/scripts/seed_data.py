from datetime import datetime, date, time
from uuid import uuid4
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, insert
import numpy as np
from base import SessionLocal
from create_db import (
    Gender,
    Customer,
    Salon,
    Service,
    ServiceCategory,
    Artist,
    Appointment,
    Location,
    Status,
    ServiceSubCategory,
    ServiceDetail,
    artist_service_association,
)

import random


def seed_customers():
    """Thêm dữ liệu salon mẫu với location_id thực tế"""
    db = SessionLocal()
    try:
        # Lấy locations đã tạo từ database

        customers_data = [
            {
                "first_name": "Khoi",
                "last_name": "Tran",
                "email": "khoi.tran@example.com",
                "phone_number": "+61 412345678",
                "gender": Gender.MALE,
                "date_of_birth": date(1990, 1, 1),
                "status": Status.ACTIVE,
            }
        ]
        for customer_data in customers_data:
            customer = Customer(**customer_data)
            db.add(customer)

        db.commit()
        print("✅ Đã thêm dữ liệu salon với location_id")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi thêm salon: {e}")
    finally:
        db.close()


# def seed_all_data():
#     """Thêm tất cả dữ liệu mẫu"""
#     print("🚀 Bắt đầu thêm dữ liệu mẫu vào database...")

#     seed_customers()

#     print("\n🎉 Hoàn thành thêm tất cả dữ liệu mẫu!")


def clear_all_data():
    """Xóa tất cả dữ liệu (cẩn thận!)"""
    db = SessionLocal()
    try:
        print("⚠️ CẢNH BÁO: Đang xóa tất cả dữ liệu...")

        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        tables = [
            "appointments",
            "artist_services",
            "artists",
            "services",
            "service_details",
            "service_sub_categories",
            "service_categories",
            "salons",
            "locations",
            "customers",
        ]

        for table in tables:
            db.execute(text(f"TRUNCATE TABLE {table}"))

        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.commit()
        print("✅ Đã xóa tất cả dữ liệu!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi xóa dữ liệu: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_customers()
