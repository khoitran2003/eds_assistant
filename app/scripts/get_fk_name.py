from sqlalchemy.orm import Session
from app.core.db.base import SessionLocal, engine
from app.core.db.create_db import Service
from sqlalchemy import text

def get_fk_names_for_service_id(tables):
    """
    Lấy tên các foreign key constraints trên cột service_id của các bảng trong MySQL.
    
    Args:
        tables (list): Danh sách tên bảng cần kiểm tra.
    Returns:
        dict: key là tên bảng, value là list tên FK trên cột service_id.
    """
    fk_dict = {}
    with engine.connect() as conn:
        for table in tables:
            query = text("""
                SELECT
                    constraint_name
                FROM
                    information_schema.key_column_usage
                WHERE
                    table_schema = DATABASE()
                    AND table_name = :table_name
                    AND column_name = 'service_id'
                    AND referenced_table_name = 'services';
            """)
            result = conn.execute(query, {"table_name": table}).fetchall()
            fk_names = [row[0] for row in result]
            fk_dict[table] = fk_names
    return fk_dict


if __name__ == "__main__":
    tables = ["appointments", "service_details", "artist_services"]
    fk_names = get_fk_names_for_service_id(tables)
    for table, fks in fk_names.items():
        print(f"Bảng '{table}' có các foreign key trên cột service_id:")
        if not fks:
            print("  - Không có")
        else:
            for fk in fks:
                print(f"  - {fk}")
