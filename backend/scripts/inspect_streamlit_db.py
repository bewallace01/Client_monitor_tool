"""Inspect the Streamlit SQLite database to understand schema and data."""

import sys
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def inspect_database(db_path: str):
    """Inspect a SQLite database and show its structure and data."""
    print("=" * 60)
    print(f"Inspecting Database: {db_path}")
    print("=" * 60)
    print()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print(f"Tables Found: {len(tables)}")
        print("-" * 60)

        for (table_name,) in tables:
            print(f"\nTable: {table_name}")
            print("-" * 60)

            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            print("Schema:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_str = " [PRIMARY KEY]" if pk else ""
                null_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"  - {col_name}: {col_type}{pk_str}{null_str}{default_str}")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nRow Count: {count}")

            # Show sample data (first 3 rows)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                col_names = [desc[1] for desc in columns]

                print("\nSample Data (first 3 rows):")
                for i, row in enumerate(rows, 1):
                    print(f"\n  Row {i}:")
                    for col_name, value in zip(col_names, row):
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:47] + "..."
                        print(f"    {col_name}: {value}")

            print()

        conn.close()

        print("=" * 60)
        print("[OK] Database inspection complete")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"[ERROR] Failed to inspect database: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    # Look for Streamlit database in data/ directory first
    streamlit_db = Path(__file__).resolve().parents[2] / "data" / "client_intelligence.db"

    if not streamlit_db.exists():
        # Try root directory
        streamlit_db = Path(__file__).resolve().parents[2] / "client_intelligence.db"

    if not streamlit_db.exists():
        print(f"[ERROR] Streamlit database not found")
        print("\nSearching for database files...")

        # Search for .db files
        root_dir = Path(__file__).resolve().parents[2]
        db_files = list(root_dir.glob("**/*.db"))

        if db_files:
            print(f"\nFound {len(db_files)} database file(s):")
            for db_file in db_files:
                print(f"  - {db_file}")
            print("\nUsing first non-backend database found...")
            # Skip backend/data/ database
            for db_file in db_files:
                if "backend" not in str(db_file):
                    streamlit_db = db_file
                    break
            else:
                streamlit_db = db_files[0]
        else:
            print("[ERROR] No database files found!")
            return False

    print(f"Using database: {streamlit_db}\n")
    return inspect_database(str(streamlit_db))


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
