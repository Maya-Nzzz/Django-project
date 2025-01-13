import pandas as pd
import sqlite3


def process(database_name, csv_file, table_name):
    df = pd.read_csv(csv_file)
    conn = sqlite3.connect(database_name)

    create_table_query = f"""
        CREATE TABLE {table_name} (
            date TEXT PRIMARY KEY,
            BYR REAL NOT NULL,
            USD REAL NOT NULL,
            EUR REAL NOT NULL,
            KZT REAL NOT NULL,
            UAH REAL NOT NULL,
            AZN REAL NOT NULL,
            KGS REAL NOT NULL,
            UZS REAL NOT NULL
        );
        """

    conn.execute(create_table_query)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()


if __name__ == "__main__":
    database_name = "db.sqlite3"
    csv_file = input()
    table_name = input()
    process(database_name, csv_file, table_name)
