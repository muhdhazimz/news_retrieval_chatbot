import ast
import cohere
import pandas as pd
import sqlite3

from typing import Union
from langchain.tools import tool
from dotenv import load_dotenv
from ..prompt import (
    TABLE_DESCRIPTION_PROMPT,
    COLUMN_DESCRIPTION_PROMPT,
    SQL_QUERY_GENERATION_PROMPT,
)
from ..utils import load_env_variable, load_csv_to_sqlite, load_excel_to_sqlite

load_dotenv()

COHERE_MODEL: str = load_env_variable("COHERE_MODEL", required=True)
COHERE_API_KEY: str = load_env_variable("COHERE_API_KEY", required=True)

# CSV_TABLE_PATH_LIST: list = ast.literal_eval(
#     load_env_variable("CSV_TABLE_PATH_LIST", required=True)
# )

EXCEL_TABLE_PATH_LIST: list = ast.literal_eval(
    load_env_variable("EXCEL_TABLE_PATH_LIST", required=True)
)

cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY)

conn = sqlite3.connect(":memory:")  

loaded_dataframes: dict = {}

# for csv_table_path in CSV_TABLE_PATH_LIST:
#     load_csv_to_sqlite(csv_table_path, conn, loaded_dataframes)

for excel_table_path in EXCEL_TABLE_PATH_LIST:
    load_excel_to_sqlite(excel_table_path, conn, loaded_dataframes)

def get_table_schema(conn: sqlite3.Connection, table_name: str):
    """
    Get the schema (columns and their data types) of a table from the SQLite database.

    Args:
        conn (sqlite3.Connection): The SQLite connection object.
        table_name (str): The name of the table to retrieve the schema from.

    Returns:
        schema (str): The schema description in a human-readable format.
    """
    query = f"PRAGMA table_info('{table_name}');"

    try:
        cursor = conn.execute(query)
        columns = cursor.fetchall()

        schema = []
        for col in columns:
            column_name = col[1]
            column_type = col[2]
            schema.append(f"{column_name} ({column_type})")

        return ", ".join(schema)

    except sqlite3.Error as e:
        return f"Error getting schema: {e}"


def get_column_samples_as_string(conn: sqlite3.Connection, table_name: str) -> str:
    """
    Retrieve one sample value from each column in the specified SQLite table and format as a string.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        table_name (str): Name of the table to sample from.

    Returns:
        str: A formatted string containing "{column_name}: {column_sample}" for each column.
    """
    try:
        # Get the column names from the table
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = [
            row[1] for row in cursor.fetchall()
        ]  # Column names are in the second field of PRAGMA table_info output

        if not columns:
            raise ValueError(f"Table '{table_name}' does not exist or has no columns.")

        # Construct a query to retrieve one value from each column
        query = f"SELECT {', '.join([f'MIN({col}) AS {col}' for col in columns])} FROM {table_name};"

        cursor = conn.execute(query)
        row = cursor.fetchone()

        # Format output as "{column_name}: {column_sample}"
        formatted_output = " \n".join(
            f"- {columns[i]}: {row[i]}" for i in range(len(columns))
        )

        return formatted_output

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return ""
    except Exception as e:
        print(f"Error: {e}")
        return ""


def generate_table_descriptions(table_name: str) -> str:
    """
    Generate a summary description of the entire table's content using Cohere's language model.
    The function summarizes the table structure, row and column counts, and a small preview of the data.

    Args:
        table_name (str): The name of the table for which the description is being generated.

    Returns:
        str: A summarized description of the table's content.
    """
    try:
        # Load the table data (assuming it's loaded from a CSV file or similar source)
        df = loaded_dataframes.get(table_name)

        if df is None:
            return "Table not found or is empty."

        # Create a basic table structure summary
        summary = f"The table '{table_name}' contains {df.shape[0]} rows and {df.shape[1]} columns. "
        summary += (
            "It includes the following types of data: "
            + ", ".join(df.dtypes.astype(str))
            + ". "
        )

        # Get a preview of the data (first 3 rows) to help understand its context
        preview = df.head(3).to_string(index=False)
        summary += f"\nHere is a preview of the data:\n{preview}"

        # Use Cohere's language model to summarize the description
        response = cohere_client.generate(
            model=COHERE_MODEL,
            prompt=TABLE_DESCRIPTION_PROMPT.format(summary=summary),
            max_tokens=100,
            temperature=0.3,
        )

        # Return the summarized version
        return response.generations[0].text.strip()

    except Exception as e:
        return f"Error generating table description: {e}"


def generate_column_descriptions(conn: sqlite3.Connection, table_name: str) -> str:
    """
    Generates a description for each column in a specified table using Cohere LLM.

    Args:
        conn (sqlite3.Connection): SQLite database connection.
        table_name (str): The name of the table for which column descriptions are generated.

    Returns:
        str: A string with pair of column names and their descriptions.
    """
    # Fetch column names from the table
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    if not columns:
        return {"error": f"Table '{table_name}' does not exist or has no columns."}

    column_descriptions = {}

    # Create a list of column names and types
    column_list = [f"{col[1]} ({col[2]})" for col in columns]

    # Build the prompt
    prompt = COLUMN_DESCRIPTION_PROMPT.format(
        table_name=table_name, columns="\n".join(column_list)
    )

    try:
        # Call Cohere API to generate descriptions
        response = cohere_client.generate(
            model=COHERE_MODEL, prompt=prompt, max_tokens=500, temperature=0.5
        )
        generated_text = response.generations[0].text.strip()

        # Parse the generated descriptions
        for line in generated_text.split("\n"):
            if ": " in line:
                col_name, description = line.split(": ", 1)
                column_descriptions[col_name.strip()] = description.strip()

        column_descriptions_str = ""

        for key in column_descriptions.keys():
            column_descriptions_str += f"{key}: {column_descriptions[key]}\n"

        return column_descriptions_str

    except Exception:
        return ""


@tool(return_direct=False, parse_docstring=True, error_on_invalid_docstring=False)
def get_available_fields_tool(table_name: str) -> dict:
    """
    Fetch all available categorical or date-related fields (columns) from the specified table.

    This function is useful when an SQL query for specific data returns no results,
    or the requested data is unavailable.

    Args:
        table_name: The name of the table (e.g., 'transactions', 'merchants', 'categories').

    Returns:
        dict: A dictionary containing available categorical or date-related fields along with the data.
              If no data is found, includes a message suggesting the exploration of available fields.

    Usage:
        - Use this function when an SQL query for a specific category, date, or other data returns no data or empty results.
        - This function will help retrieve available fields and data, limited to categorical (TEXT, INTEGER) and date-related (DATE, DATETIME, TIMESTAMP) columns.
    """
    # Fetch column names and their types dynamically
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    # Filter out columns that are either categorical (TEXT, INTEGER) or date-related (DATE, DATETIME)
    allowed_types = ["TEXT", "INTEGER", "DATE", "DATETIME", "TIMESTAMP", "REAL"]
    filtered_columns = [column[1] for column in columns if column[2] in allowed_types]

    # Retrieve data for the table, limited to the allowed fields (categorical/date-related)
    result = {"fields": filtered_columns, "data": {}}

    for column in filtered_columns:
        # For date, time, integer, and float, fetch min and max values
        if column in filtered_columns:
            column_type = next(col[2] for col in columns if col[1] == column)
            if column_type in ["DATE", "DATETIME", "TIMESTAMP"]:
                query = f"SELECT MIN({column}), MAX({column}) FROM {table_name}"
                min_max_data = conn.execute(query).fetchone()
                result["data"][column] = {
                    "min": min_max_data[0],
                    "max": min_max_data[1],
                }
            elif column_type in ["INTEGER", "REAL"]:
                query = f"SELECT MIN({column}), MAX({column}) FROM {table_name}"
                min_max_data = conn.execute(query).fetchone()
                result["data"][column] = {
                    "min": min_max_data[0],
                    "max": min_max_data[1],
                }
            else:
                # For other types (TEXT), just return the distinct values
                query = f"SELECT DISTINCT {column} FROM {table_name} ORDER BY RANDOM() LIMIT 15"
                distinct_values = conn.execute(query).fetchall()
                result["data"][column] = [value[0] for value in distinct_values]

    # If no data is found, suggest using this function to explore available fields.
    if not result["data"]:
        return {
            "fields": filtered_columns,
            "data": [],
            "message": "No data found for the query. You can use this function to explore available fields in the table.",
        }

    return result


@tool(return_direct=False, parse_docstring=True, error_on_invalid_docstring=False)
def search_table_for_query_tool(input: str) -> Union[str, None]:
    """
    Search through available tables and select the one that best matches the user query.

    This function uses Cohere LLM to determine relevance and return the best matching table
    based on the user's query. It also generates descriptions for each table to assist in
    selecting the most appropriate one.

    Args:
        input: The user's query in natural language.

    Returns:
        str: The name of the table that best matches the query, or None if no table is relevant.
    """
    # List all loaded CSV files (tables)
    available_tables = list(loaded_dataframes.keys())

    # Generate table descriptions for each available table
    table_descriptions = {}
    for table in available_tables:
        description = generate_table_descriptions(table)
        table_descriptions[table] = description

    # Prepare input for LLM analysis
    query_prompt = (
        "You are an intelligent assistant tasked with finding the most relevant table for a given query. "
        "Here is the user's query:\n\n"
        f"Query: {input}\n\n"
        "Available tables with descriptions:\n"
    )

    for table, description in table_descriptions.items():
        query_prompt += f"\nTable: {table}\nDescription: {description}"

    query_prompt += (
        "\n\nIdentify the single most relevant table based on the query context and the descriptions provided. "
        "Return only the relevant table name or 'None' if no table matches the query context."
    )

    # Use Cohere's language model to determine the relevance
    try:
        response = cohere_client.generate(
            model=COHERE_MODEL,
            prompt=query_prompt,
            max_tokens=200,
            temperature=0.3,
        )
        result = response.generations[0].text.strip()

        # If the result explicitly says 'None', return None
        if result.lower() == "none":
            return None

        # Ensure the result is one of the available tables
        matching_table = next(
            (table for table in available_tables if result in table), None
        )
        return matching_table or None

    except Exception as e:
        # Handle errors and provide fallback behavior
        print(f"Error during Cohere LLM query: {e}")
        return None


def generate_sql_query_with_cohere(input: str, table_name: str, client_id: str) -> str:
    """
    Generate a SQLite SQL query from natural language using Cohere based on the table schema.
    The schema is dynamically constructed based on the actual table columns and data types.

    Args:
        input (str): The user's query in natural language.
        table_name (str): The name of the table to generate the query for.
        client_id (str): The user's client ID.

    Returns:
        str: The SQL query generated by Cohere.
    """
    # Get the table schema from the SQLite database
    schema = get_table_schema(conn, table_name)

    # Get the column samples from the SQLite database
    column_samples = get_column_samples_as_string(conn, table_name)

    # Get the column descriptions from the SQLite database
    column_descriptions = generate_column_descriptions(conn, table_name)

    response = cohere_client.generate(
        model=COHERE_MODEL,
        prompt=SQL_QUERY_GENERATION_PROMPT.format(
            table_name=table_name,
            schema=schema,
            column_descriptions=column_descriptions,
            column_samples=column_samples,
            input=input,
            client_id=client_id,
        ),
        max_tokens=200,
        temperature=0,
    )

    cleaned_response = (
        response.generations[0].text.strip().replace("```sql", "").replace("```", "")
    )

    print(cleaned_response)

    return cleaned_response


@tool(return_direct=False, parse_docstring=True, error_on_invalid_docstring=False)
def sql_query_generator_and_executor_tool(
    query: str, selected_table: str, client_id: str
) -> str:
    """
    Generates and executes an SQL query based on the user's natural language query,
    the selected database table, and the provided client ID. This function integrates
    query generation, table selection, and result retrieval into a single streamlined process.
    Always run `search_table_for_query` tool before running this tool.

    Functionality:
        - Automatically generates an SQL query tailored to the user's request and filters results by client ID.
        - Executes the generated SQL query on the specified database table.
        - Retrieves query results and formats them as plain text for user readability.

    Args:
        query: The user's query in natural language.
        selected_table: The name of the database table to query.
        client_id: The client's unique identifier for filtering results.

    Returns:
        str: The query results formatted as plain text or a message indicating no results were found.
            If an error occurs, returns an error message.
    """
    try:
        # Generate SQL query using Cohere
        sql_query = generate_sql_query_with_cohere(query, selected_table, client_id)

        # Execute SQL query on SQLite database
        result = pd.read_sql_query(sql_query, conn)

        # Format the result as plain text
        if result.empty:
            return "No results found for your query."
        return result.to_string(index=False)
    except Exception as e:
        return f"Error executing query: {e}"
