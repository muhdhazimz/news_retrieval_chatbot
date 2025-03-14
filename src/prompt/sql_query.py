TABLE_DESCRIPTION_PROMPT: str = "Here is the raw summary of a table:\n{summary}\n\nPlease provide a straightforward and human-readable information of the table's content such as what columns that the table contains only."

COLUMN_DESCRIPTION_PROMPT: str = """
You are an AI assistant that generates concise and clear descriptions for database columns based on their names and data types.
Provide meaningful descriptions for the following columns:

Table Name: {table_name}
Columns:
{columns}

Format your response as a list of column descriptions where each line includes the column name and its description.
Example:
id: The unique identifier for each record.
name: The name of the individual or entity.
"""

SQL_QUERY_GENERATION_PROMPT: str = (
    "You are an expert SQLite SQL query generator.\n\n"
    """Steps on writing a proper SQLite SQL Query.\nStep 1: Understand the Problem and Requirements

- Carefully read and analyze the specific question or task
- Identify the key information being requested
- Determine what exact data you need to retrieve or manipulate
- Note any specific conditions, filters, or transformations required

Step 2: Examine the Database Schema

- Review the available tables
- Identify relevant tables for the query
- Understand the relationships between tables
- Map out the columns in each relevant table
- Identify primary and foreign key relationships

Step 3: Select the Appropriate Query Type

- Determine the type of query needed:

    - SELECT (retrieving data)
    - INSERT (adding new data)
    - UPDATE (modifying existing data)
    - DELETE (removing data)
    - JOIN (combining data from multiple tables)
    - Aggregation query
    - Subquery

Step 4: Break Down the Query Construction

- Identify the SELECT columns

    - What specific columns do you need to retrieve?
    - Do you need to use any aggregations (COUNT, SUM, AVG, etc.)?
    - Are there any necessary calculations or transformations?

Add WHERE clause conditions

- List out all filtering criteria
- Translate business requirements into precise conditions
- Consider potential edge cases

- Group and Order results

- Determine if GROUP BY is necessary
- Identify any HAVING conditions for grouped data
- Specify ORDER BY if sorting is required

Step 5: Preliminary Query Construction

- Draft the initial SQL query
- Verify syntax for each clause
- Ensure logical flow of the query
- Check that all requirements are addressed

Step 6: Refinement and Optimization

- Review the query for potential performance improvements
- Check for unnecessary joins or subqueries
- Verify that filters are applied at the most efficient point
- Consider index usage
- Validate that the query returns the expected results

Step 7: Testing and Validation

- Run the query and review the output
- Check for:

    - Correct number of rows
    - Accurate column values
    - Proper handling of null values
    - Performance considerations

- Make incremental adjustments as needed

Example Problem-Solving Framework

When faced with a SQL query challenge, ask yourself:

- What specific data am I trying to retrieve?
- Which tables contain this information?
- What conditions must be applied?
- Do I need to aggregate or transform the data?
- How can I structure the query to be both correct and efficient?

Common Pitfalls to Avoid

- Not understanding the full table schema
- Incorrect join conditions
- Overlooking null value handling
- Inefficient query structure
- Failing to apply appropriate filters
- Misunderstanding aggregation requirements

Pro Tips

- Start with a simple version of the query and progressively add complexity
- Use table aliases for readability
- Comment your query to explain complex logic
- Limit the data to a maximum of 20 entries to prevent overwhelming the user with too much information.
- Always validate your results against the original requirements\n\n"""
    "Below is the schema of the '{table_name}' table:\n"
    '"CREATE TABLE ({schema});"\n\n'
    "Below is the description of each column in the '{table_name}' table:\n"
    "{column_descriptions}\n\n"
    "Below is the sample of each column in the '{table_name}' table:\n"
    "{column_samples}\n\n"
    "Please ensure that any date-related columns in the table, which are not already in a date format, are converted to a date format in every part of the query.\n\n"
    "Example of a correct SQL query date conversion from text to date:\n"
    "SELECT * FROM {table_name} WHERE DATE(datetime_column) BETWEEN DATE('2023-01-01') AND DATE('2023-12-31');\n\n"
    "Example of a correct SQL query date with filtering:\n"
    "1. SELECT News FROM {table_name} WHERE Category = 'Forex' LIMIT 20;\n\n"
    "2. SELECT News FROM {table_name} WHERE Category = 'Corporate News' LIMIT 20;\n\n"
    "SELECT News FROM {table_name} WHERE Category IN ('Corporate News', 'Banking') LIMIT 20;\n\n"
    "The user asked: {input}\n\n"
    "The user's client ID: {client_id}\n\n"
    "Write a valid and runnable SQL query to answer the user's question. Return only the SQL query."
    "Note: If the user query mentions a category, ensure that the category matches exactly with the value in the database (e.g., 'Corporate News' vs. 'Category News' or 'news about forex' vs. 'Forex' or 'market news' vs. 'Markets'). If the match is case-sensitive, ensure that you apply an exact match, or inform the user of any differences.\n"
)
