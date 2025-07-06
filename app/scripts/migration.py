"""
Migration script để thêm opening_days column vào salons table
"""

from sqlalchemy import text
from app.core.db.base import engine


def add_column(table: str, column: str, column_type: str):
    """Thêm cột vào bảng salons"""

    migration_sql = f"""
    ALTER TABLE {table} 
    ADD COLUMN {column} {column_type};
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(migration_sql))
            conn.commit()
            print(f"✅ Đã thêm cột {column} vào bảng {table}")

    except Exception as e:
        print(f"❌ Lỗi migration: {e}")
        raise


def rollback_column(table: str, column: str):
    """Xóa cột vào bảng salons"""
    rollback_sql = f"ALTER TABLE {table} DROP COLUMN {column};"

    try:
        with engine.connect() as conn:
            conn.execute(text(rollback_sql))
            conn.commit()
            print(f"✅ Đã xóa cột {column} trong bảng {table}")
    except Exception as e:
        print(f"❌ Lỗi rollback: {e}")
        raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_column("artists", "languages")
    else:
        add_column(
            "artists",
            "strengths",
            "TEXT",
        )
