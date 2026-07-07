import duckdb
import pandas as pd


def profile_file(file_path: str, sample_limit: int = 20):
    con = duckdb.connect()

    row_count = con.sql(f"""
        SELECT COUNT(*) AS row_count
        FROM '{file_path}'
    """).df()

    schema = con.sql(f"""
        DESCRIBE SELECT *
        FROM '{file_path}'
    """).df()

    sample = con.sql(f"""
        SELECT *
        FROM '{file_path}'
        LIMIT {sample_limit}
    """).df()

    return {
        "row_count": row_count,
        "schema": schema,
        "sample": sample,
    }