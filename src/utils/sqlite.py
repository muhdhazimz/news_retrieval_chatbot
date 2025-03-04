import os
import pandas as pd
import sqlite3


def preview_table_data(conn: sqlite3.Connection, table_name: str, limit: int = 5):
    try:
        query = """SELECT  txn_date
FROM transactions WHERE clnt_id = 28"""

        cursor = conn.execute(query)
        rows = cursor.fetchall()
        if rows:
            print(f"Preview of data from table '{table_name}':")
            for row in rows:
                print(row)
        else:
            print(f"Table '{table_name}' exists but contains no data.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}. This likely means the table '{table_name}' does not exist.")


def load_csv_to_sqlite(
    csv_file_path: str, conn: sqlite3.Connection, loaded_dataframes: dict
):
    """
    Load a CSV file into an SQLite database dynamically.
    The table name is set based on the CSV file name (without the file extension).
    Also, preprocesses the data by converting date columns to string format (YYYY-MM-DD).

    Args:
        csv_file_path (str): The path to the CSV file.
        conn (sqlite3.Connection): The SQLite connection object.
        loaded_dataframes (dict): Dictionary to store loaded dataframes.
    """
    df = pd.read_csv(csv_file_path)

    table_name = os.path.splitext(os.path.basename(csv_file_path))[0]

    date_columns = [col for col in df.columns if "date" in col.lower()]

    for col in date_columns:
        if (
            pd.to_datetime(df[col], format="%d/%m/%Y %H:%M", errors="coerce")
            .notna()
            .all()
        ):  
            df[col] = pd.to_datetime(
                df[col], format="%d/%m/%Y %H:%M", errors="coerce"
            ).dt.strftime("%Y-%m-%d")

    loaded_dataframes[table_name] = df

    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False,
    )

    print(f"Table '{table_name}' created and data loaded from {csv_file_path}.")


def load_excel_to_sqlite(
    excel_file_path: str, conn: sqlite3.Connection, loaded_dataframes: dict
):
    """
    Load an Excel file into an SQLite database dynamically.
    The table name is set based on the Excel file name (without the file extension).
    Also, preprocesses the data by converting date columns to string format (YYYY-MM-DD).

    Args:
        excel_file_path (str): The path to the Excel file.
        conn (sqlite3.Connection): The SQLite connection object.
        loaded_dataframes (dict): Dictionary to store loaded dataframes.
    """
    df = pd.read_excel(excel_file_path)

    table_name = os.path.splitext(os.path.basename(excel_file_path))[0]

    date_columns = [col for col in df.columns if "date" in col.lower()]

    for col in date_columns:
        if (
            pd.to_datetime(df[col], errors="coerce")
            .notna()
            .all()
        ):  
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    loaded_dataframes[table_name] = df

    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False,
    )

    print(f"Table '{table_name}' created and data loaded from {excel_file_path}.")

