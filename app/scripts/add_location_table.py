"""
Migration script để thêm bảng locations đơn giản
"""

from sqlalchemy import text
from app.core.db.base import engine


def add_locations_table():
    """Tạo bảng locations đơn giản"""

    create_table_sql = """
    CREATE TABLE locations (
        id CHAR(36) PRIMARY KEY,
        location VARCHAR(255),
        status ENUM('active', 'inactive', 'deleted', 'pending', 'approved', 'rejected', 'cancelled', 'completed', 'in_progress', 'on_hold', 'expired', 'refunded', 'refund_requested', 'refund_approved') DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_location (location),
        INDEX idx_status (status)
    );
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Đã tạo bảng locations")

    except Exception as e:
        print(f"❌ Lỗi khi tạo bảng locations: {e}")
        raise


def drop_locations_table():
    """Xóa bảng locations"""
    drop_sql = "DROP TABLE IF EXISTS locations;"

    try:
        with engine.connect() as conn:
            conn.execute(text(drop_sql))
            conn.commit()
            print("✅ Đã xóa bảng locations")
    except Exception as e:
        print(f"❌ Lỗi khi xóa bảng locations: {e}")
        raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_locations_table()
    else:
        add_locations_table()
