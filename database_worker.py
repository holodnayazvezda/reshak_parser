import sqlite3


async def write_information_to_database(db_name, table, name, id=None):
    while True:
        try:
            conn = sqlite3.connect(db_name)
            c = conn.cursor()

            if id is None:
                query_create_table = f"CREATE TABLE IF NOT EXISTS {table} (name TEXT)"
                query = f"INSERT INTO {table} (name) VALUES (?)"
                values = (name,)
            else:
                query_create_table = f"CREATE TABLE IF NOT EXISTS {table} (id TEXT, name TEXT)"
                query = f"INSERT INTO {table} (id, name) VALUES (?, ?)"
                values = (id, name)

            c.execute(query_create_table)
            c.execute(query, values)
            conn.commit()
            c.close()
            conn.close()
            break
        except Exception:
            continue


async def update_information_in_database(db_name, table, name, id):
    while True:
        try:
            conn = sqlite3.connect(db_name)
            c = conn.cursor()

            query_create_table = f"CREATE TABLE IF NOT EXISTS {table} (id TEXT, name TEXT)"
            c.execute(query_create_table)

            select_query = f"SELECT EXISTS(SELECT 1 FROM {table} WHERE id = ?)"
            c.execute(select_query, (id,))
            record_exists = c.fetchone()[0]
            if record_exists:
                query = f"UPDATE {table} SET name = ? WHERE id = ?"
                values = (name, id)
            else:
                query = f"INSERT INTO {table} (id, name) VALUES (?, ?)"
                values = (id, name)
            c.execute(query, values)
            conn.commit()
            c.close()
            conn.close()
            break
        except Exception:
            continue
