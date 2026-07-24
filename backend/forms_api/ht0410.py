from .as400 import get_connection
from datetime import datetime

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
        cursor.execute(sql, [worker_code, int(warehouse_code)])

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

        cursor.execute(sql, [worker_code, int(warehouse_code)])

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
            SELECT 1
            FROM TYKSFLIB.HTSTOCKQR
            WHERE QR = ?
              AND TACIAIFLG = '0'
        """

        cursor.execute(sql, [qr_code])

        row = cursor.fetchone()

        if row:
            return {"duplicate": True}

        return {"duplicate": False}

    except Exception as e:
        print("Error:", e)
        return {"duplicate": False}

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
    
def insert_stocktak(worker_code: str, warehouse_code: str, qr_code: str):

    conn = None
    cursor = None

    try:
        fields = qr_code.strip().split(",")
        print("QR:", qr_code)
        print("Fields:", fields)
        print("Length:", len(fields))

        if len(fields) != 12:
            return {
                "success": False,
                "code": "E220"
            }

        conf_type   = fields[0]

        partner_cd  = int(fields[1])
        lot         = int(fields[2])
        pallet_unit = int(fields[3])
        destinat_cd = int(fields[4])
        conf_rowno  = int(fields[5])
        # month       = int(fields[6])      # Not used in HTSTOCKTAK
        conf_serno  = int(fields[7])
        item_cd     = int(fields[8])
        material    = fields[9].strip()
        symbol      = fields[10].strip()
        qty         = int(fields[11])

        

        print("worker_code =", repr(worker_code))
        print("warehouse_code =", repr(warehouse_code))

        print("partner_cd =", repr(fields[1]))
        partner_cd = int(fields[1])

        print("lot =", repr(fields[2]))
        lot = int(fields[2])

        print("pallet_unit =", repr(fields[3]))
        pallet_unit = int(fields[3])

        print("destinat_cd =", repr(fields[4]))
        destinat_cd = int(fields[4])

        print("conf_rowno =", repr(fields[5]))
        conf_rowno = int(fields[5])

        print("conf_serno =", repr(fields[7]))
        conf_serno = int(fields[7]) if fields[7].strip() else 0

        print("item_cd =", repr(fields[8]))
        item_cd = int(fields[8])

        print("qty =", repr(fields[11]))
        qty = int(fields[11])

        print("worker_code int =", repr(worker_code))
        createid = int(worker_code)

        print("warehouse_code int =", repr(warehouse_code))
        warehouse = int(warehouse_code)
        
        print(int(fields[11]))

        serno = get_serial_no(worker_code, warehouse_code) + 1

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO TYKSFLIB.HTSTOCKTAK
        (
            HTNM,
            WAREHOUSCD,
            SERNO,
            ITEMCD,
            MATERIAL,
            SYMBOL,
            PALLETUNIT,
            PALLETQTY,
            QTY,
            PARTNERCD,
            CREATEID,
            CREATEDT,
            INSPUPDFLG,
            LASTID,
            LASTDT,
            DELFLG,
            CONFSERNO,
            LOT,
            DESTINATCD,
            CONFROWNO
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, CAST(CURRENT TIMESTAMP AS CHAR(26)),
            ?, ?, ?, ?, ?, ?, ?, ?
        )
        """
        print("Insert SQL:", sql)
        params = [
            worker_code,
            int(warehouse_code),
            serno,
            item_cd,
            material,
            symbol,
            pallet_unit,
            1,
            qty,
            partner_cd,
            int(worker_code),
            "",
            0,
            "",
            "",
            conf_serno,
            lot,
            destinat_cd,
            conf_rowno
        ]

        for i, p in enumerate(params, 1):
            print(f"P{i}: {p!r} ({type(p).__name__})")

        cursor.execute(sql, params)
        
        conn.commit()

        return {
            "success": True
        }

    except Exception as e:
        print("Insert Error:", e)

        return {
            "success": False,
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
def detail_list(worker_code: str, warehouse_code: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT
                MATERIAL,
                SYMBOL,
                QTY
            FROM TYKSFLIB.HTSTOCKTAK
            WHERE HTNM = ?
              AND WAREHOUSCD = ?
              AND DELFLG = ''
            ORDER BY SERNO
        """

        cursor.execute(sql, [worker_code, int(warehouse_code)])

        rows = []

        for row in cursor.fetchall():
            rows.append({
                "material": str(row[0]).strip(),
                "symbol": str(row[1]).strip(),
                "qty": row[2]
            })

        return rows

    except Exception as e:
        print("Error:", e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()