from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.db.base import SessionLocal, engine


def get_data(table_model, order_by_column=None):
    db: Session = SessionLocal()
    try:
        query = db.query(table_model)
        if order_by_column is not None:
            query = query.order_by(order_by_column.asc())
        services = query.all()

        for s in services:
            print(
                f"{s.id} | {s.name} | {s.service_sub_category.name} | {s.service_category.name}"
            )
    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu: {e}")
    finally:
        db.close()


FK_INFOS = {
    "appointments": "appointments_ibfk_3",
    "service_details": "service_details_ibfk_1",
    "artist_services": "artist_services_ibfk_2",
}


def drop_foreign_keys(conn):
    print("🚧 Đang gỡ foreign keys cũ...")
    for table, fk_name in FK_INFOS.items():
        print(f"  - Gỡ FK '{fk_name}' trên bảng '{table}'")
        conn.execute(text(f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}"))
    print("✅ Đã gỡ xong các foreign keys.")


def alter_columns(conn):
    print("🚧 Đang đổi kiểu cột service_id sang INT...")

    # Bước 1: Gỡ khóa chính cũ
    conn.execute(text("ALTER TABLE services DROP PRIMARY KEY;"))

    # Bước 2: Đổi kiểu cột id sang INT AUTO_INCREMENT
    conn.execute(
        text(
            """
        ALTER TABLE services
        MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT;
    """
        )
    )

    # Bước 3: Đặt lại PRIMARY KEY (trên cột id)
    conn.execute(text("ALTER TABLE services ADD PRIMARY KEY (id);"))

    # Đổi kiểu cột service_id trong bảng con thành INT
    for table in FK_INFOS.keys():
        print(f"  - Đổi kiểu cột service_id trong bảng '{table}'")
        conn.execute(
            text(
                f"""
            ALTER TABLE {table}
            MODIFY COLUMN service_id INT NOT NULL;
        """
            )
        )
    print("✅ Đã đổi kiểu cột service_id sang INT.")


def update_service_ids(conn):
    print("🚧 Đang cập nhật lại id cho bảng services và các FK con...")

    # Lấy danh sách services theo thứ tự nào đó (ví dụ order by name)
    services = conn.execute(text("SELECT id FROM services ORDER BY id")).fetchall()

    # Tạo map cũ sang mới: giả sử đặt lại id bắt đầu từ 1 tăng dần
    old_to_new_id = {}
    new_id = 1
    for (old_id,) in services:
        old_to_new_id[old_id] = new_id
        new_id += 1

    # Cập nhật bảng services
    for old_id, new_id in old_to_new_id.items():
        conn.execute(
            text(f"UPDATE services SET id = :new_id WHERE id = :old_id"),
            {"new_id": new_id, "old_id": old_id},
        )

    # Cập nhật các bảng con FK service_id
    for table in FK_INFOS.keys():
        for old_id, new_id in old_to_new_id.items():
            conn.execute(
                text(
                    f"UPDATE {table} SET service_id = :new_id WHERE service_id = :old_id"
                ),
                {"new_id": new_id, "old_id": old_id},
            )

    print("✅ Đã cập nhật xong id và FK service_id.")


def recreate_foreign_keys(conn):
    print("🚧 Đang tạo lại foreign keys...")

    conn.execute(
        text(
            """
        ALTER TABLE appointments
        ADD CONSTRAINT appointments_ibfk_3 FOREIGN KEY (service_id) REFERENCES services(id);
    """
        )
    )

    conn.execute(
        text(
            """
        ALTER TABLE service_details
        ADD CONSTRAINT service_details_ibfk_1 FOREIGN KEY (service_id) REFERENCES services(id);
    """
        )
    )

    conn.execute(
        text(
            """
        ALTER TABLE artist_services
        ADD CONSTRAINT artist_services_ibfk_2 FOREIGN KEY (service_id) REFERENCES services(id);
    """
        )
    )

    print("✅ Đã tạo lại các foreign keys.")


def insert_row(conn):
    try:
        # Bước 1: Dời tất cả id >= 24 lên 1 đơn vị, bắt đầu từ id lớn nhất
        conn.execute(
            text(
                """
            UPDATE services 
            SET id = id + 1 
            WHERE id >= 24
            ORDER BY id DESC
        """
            )
        )

        # Bước 2: Thêm service mới vào id=24
        conn.execute(
            text(
                """
            INSERT INTO services (id, name, category_id, sub_category_id, status, created_at, updated_at)
            VALUES (24, 'New Inserted Service', 3, 1, 'ACTIVE', NOW(), NOW())
        """
            )
        )

        conn.commit()
        print("✅ Đã chèn hàng vào id=24 và cập nhật các id còn lại.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Lỗi: {e}")


def main():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # drop_foreign_keys(conn)
            # alter_columns(conn)
            # update_service_ids(conn)
            # recreate_foreign_keys(conn)
            insert_row(conn)

            trans.commit()
            print(
                "\n🎉 Hoàn thành chuyển đổi cột service_id từ VARCHAR sang INT và cập nhật FK."
            )
        except Exception as e:
            trans.rollback()
            print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
