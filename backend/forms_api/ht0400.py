from .as400 import get_connection


def get_temp_count(code: str, inventoryFlag: str):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        taciaiflg = "0" if inventoryFlag == "完成品" else "1"

        sql = """
            SELECT COUNT(*)
            FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
              AND TACIAIFLG = ?
        """

        cursor.execute(sql, [str(code), taciaiflg])

        row = cursor.fetchone()

        if row:
            return row[0]

        return 0

    except Exception as e:
        print("Error:", e)
        return 0

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


def delete_temp_data(code: str, inventoryFlag: str):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        taciaiflg = "0" if inventoryFlag == "完成品" else "1"

        sql = """
            DELETE FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
              AND TACIAIFLG = ?
        """

        cursor.execute(sql, [str(code), taciaiflg])

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