from .as400 import get_connection

def get_warehouse_list():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT
                STOCCD,
                STOCNM
            FROM TYKSFLIB.MWAREHOUSE
            WHERE DELFLG = ' '
            ORDER BY STOCCD
        """

        print(sql)

        cursor.execute(sql)

        rows = []

        for row in cursor.fetchall():

            rows.append({
                "code": str(row[0]).strip(),
                "name": str(row[1]).strip()
            })

        return rows

    except Exception as e:

        print("Error:", e)
        return []

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

def get_read_count(worker_code: str, warehouse_code: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT COUNT(*)
            FROM TYKSFLIB.HTSTOCKTAK
            WHERE HTNM = ?
              AND WAREHOUSCD = ?
              AND DELFLG = ''           
        """
        print("code:", worker_code)
        print("Warehouse Code:", warehouse_code)
        print(sql)
        cursor.execute(sql, [worker_code, warehouse_code])

        row = cursor.fetchone()

        return int(row[0]) if row else 0

    except Exception as e:
        print("Error:", e)
        return 0

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()                

def get_serial_no(worker_code: str, warehouse_code: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT MAX(SERNO)
            FROM TYKSFLIB.HTSTOCKTAK
            WHERE HTNM = ?
              AND WAREHOUSCD = ?                  
        """

        print("Worker Code:", worker_code)
        print("Warehouse Code:", warehouse_code)
        print(sql)

        cursor.execute(sql, [worker_code, warehouse_code])

        row = cursor.fetchone()

        if row and row[0] is not None:
            return int(row[0])

        return 0

    except Exception as e:
        print("Error:", e)
        return 0

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()            

def check_duplicate_qr(qr_code: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT
                HTNM,
                WAREHOUSCD,
                SERNO
            FROM TYKSFLIB.HTSTOCKQR
            WHERE QR = ?
              AND TACIAIFLG = '0'
        """

        print("QR Code:", qr_code)
        print(sql)

        cursor.execute(sql, [qr_code])

        # ADD THESE LINES HERE
        row = cursor.fetchone()

        print("ROW =", row)

        if row:
            return True

        return False

    except Exception as e:
        print("Error:", e)
        return False

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()