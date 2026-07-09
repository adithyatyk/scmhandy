from .as400 import get_connection

def delete_temp_data(worker_code: str):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            DELETE FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
              AND TACIAIFLG = '0'
        """

        print(sql)
        print("Parameter:", worker_code)

        cursor.execute(sql, [str(worker_code)])

        rows = cursor.rowcount
        print("Rows deleted:", rows)

        conn.commit()

        return rows > 0

    except Exception as e:
        print("Error:", e)

        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        return False

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass

        if conn:
            try:
                conn.close()
            except Exception:
                pass