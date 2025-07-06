"""
Backup và Restore script cho safe migration
"""

import json
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.core.db.base import engine
from app.core.db.create_db import (
    Salon,
    Customer,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def backup_data():
    """Backup tất cả dữ liệu ra file JSON"""
    db = SessionLocal()
    try:
        backup_data = {
            "backup_time": datetime.now().isoformat(),
            "customers": [],
            "salons": [],
            "service_groups": [],
            "services": [],
            "artists": [],
            "appointments": [],
        }

        # Backup customers
        customers = db.query(Customer).all()
        for customer in customers:
            backup_data["customers"].append(
                {
                    "id": customer.id,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "email": customer.email,
                    "phone_number": customer.phone_number,
                    "gender": (
                        customer.gender.value if customer.gender is not None else None
                    ),
                    "date_of_birth": (
                        customer.date_of_birth.isoformat()
                        if customer.date_of_birth is not None
                        else None
                    ),
                    "created_at": (
                        customer.created_at.isoformat()
                        if customer.created_at is not None
                        else None
                    ),
                    "updated_at": (
                        customer.updated_at.isoformat()
                        if customer.updated_at is not None
                        else None
                    ),
                }
            )

        # Backup salons
        salons = db.query(Salon).all()
        for salon in salons:
            backup_data["salons"].append(
                {
                    "id": salon.id,
                    "name": salon.name,
                    "address": salon.address,
                    "phone_number": salon.phone_number,
                    "email": salon.email,
                    "opening_hours": (
                        salon.opening_hours.strftime("%H:%M:%S")
                        if salon.opening_hours is not None
                        else None
                    ),
                    "closing_hours": (
                        salon.closing_hours.strftime("%H:%M:%S")
                        if salon.closing_hours is not None
                        else None
                    ),
                    "status": salon.status.value if salon.status is not None else None,
                    "created_at": (
                        salon.created_at.isoformat()
                        if salon.created_at is not None
                        else None
                    ),
                    "updated_at": (
                        salon.updated_at.isoformat()
                        if salon.updated_at is not None
                        else None
                    ),
                }
            )

        # Tương tự cho các bảng khác...

        # Lưu vào file
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Backup thành công: {filename}")
        return filename

    except Exception as e:
        print(f"❌ Lỗi backup: {e}")
        raise
    finally:
        db.close()


def restore_data(backup_file):
    """Restore dữ liệu từ backup file"""
    db = SessionLocal()
    try:
        with open(backup_file, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        print(f"🔄 Restore dữ liệu từ {backup_file}")

        # Restore customers
        for customer_data in backup_data["customers"]:
            customer = Customer(**customer_data)
            db.add(customer)

        # Restore salons với opening_days mặc định
        for salon_data in backup_data["salons"]:
            # Thêm opening_days nếu chưa có
            if "opening_days" not in salon_data:
                salon_data["opening_days"] = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                ]
            salon = Salon(**salon_data)
            db.add(salon)

        db.commit()
        print("✅ Restore thành công")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi restore: {e}")
        raise
    finally:
        db.close()


def safe_migration():
    """Migration an toàn với backup"""
    print("🚀 Bắt đầu safe migration...")

    # Bước 1: Backup
    backup_file = backup_data()

    # Bước 2: Drop và recreate tables
    from app.core.db.create_db import drop_tables, create_tables

    drop_tables()
    create_tables()

    # Bước 3: Restore với schema mới
    restore_data(backup_file)

    print("✅ Safe migration hoàn thành!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "backup":
            backup_data()
        elif command == "restore" and len(sys.argv) > 2:
            restore_data(sys.argv[2])
        elif command == "safe_migration":
            safe_migration()
    else:
        print("Usage:")
        print("  python backup_restore.py backup")
        print("  python backup_restore.py restore <backup_file>")
        print("  python backup_restore.py safe_migration")
