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
            FROM ADITHYA1.MWAREHOUSE
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

def get_read_count(worker_code: str, warehouse_code: str, taciaiflg: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if taciaiflg == "1":
            table_name = "ADITHYA1.HTSTOCKTAT"
        else:
            table_name = "ADITHYA1.HTSTOCKTAK"

        if table_name == "ADITHYA1.HTSTOCKTAK":
            sql = f"""
                SELECT COUNT(*)
                FROM {table_name}
                WHERE HTNM = ?
                AND WAREHOUSCD = ?
                AND DELFLG = ''
            """
        else:
            sql = f"""
                SELECT COUNT(*)
                FROM {table_name}
                WHERE HTNM = ?
                AND WAREHOUSCD = ?
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

def get_serial_no(worker_code: str, warehouse_code: str, taciaiflg: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if taciaiflg == "1":
            table_name = "ADITHYA1.HTSTOCKTAT"
        else:
            table_name = "ADITHYA1.HTSTOCKTAK"

        sql = f"""
            SELECT MAX(SERNO)
            FROM {table_name}
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

def check_duplicate_qr(qr_code: str, taciaiflg: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 1
            FROM ADITHYA1.HTSTOCKQR
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
def check_httake(conf_serno, lot, destinat_cd, conf_rowno, partner_cd):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT COUNT(*)
            FROM ADITHYA1.HTTAKE
            WHERE CONFSERNO = ?
              AND LOT = ?
              AND DESTINATCD = ?
              AND CONFROWNO = ?
              AND PARTNERCD = ?
              AND SHIPMENFLG <> ''
        """
        print("SQL Query:", sql)
        print(conf_serno, lot, destinat_cd, conf_rowno, partner_cd)
        cursor.execute(sql, [
            conf_serno,
            lot,
            destinat_cd,
            conf_rowno,
            partner_cd
        ])

        row = cursor.fetchone()

        return row[0] > 0

    except Exception as e:
        print("HTTAKE Error:", e)
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def check_gomast(material: str, symbol: str, partner_cd: int):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()        

        sql = """
            SELECT GOMANO
            FROM ADITHYA1.GOMAST
            WHERE GOMANA = ?
              AND GOMATK = ?
              AND GOMASY = ?
        """

        cursor.execute(sql, [material, symbol, partner_cd])

        row = cursor.fetchone()

        if row and str(row[0]).strip() != "":
            return True

        return False

    except Exception as e:
        print("GOMAST Error:", e)
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def insert_stocktak(worker_code: str, warehouse_code: str, qr_code: str, taciaiflg: str,inventory_flag: str):

    conn = None
    cursor = None

    try:
        fields = qr_code.strip().split(",")

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
        conf_serno  = int(fields[7])
        item_cd     = int(fields[8])
        material    = fields[9].strip()
        symbol      = fields[10].strip()
        qty         = int(fields[11])

        valid = check_httake(
            conf_serno,
            lot,
            destinat_cd,
            conf_rowno,
            partner_cd
        )

        print("HTTAKE Valid:", valid)

        if not valid:
            return {
                "success": False,
                "code": "E226"
            }

        exists = check_gomast(material, symbol, partner_cd)
        print("Material:", material)
        print("Symbol:", symbol)
        print("Exists:", exists)

        if exists:
            material_value = material
            symbol_value = symbol
            partner_cd_value = partner_cd
        else:
            material_value = ""
            symbol_value = ""
            partner_cd_value = 0

        

        serno = get_serial_no(worker_code, warehouse_code, taciaiflg) + 1       

        conn = get_connection()
        cursor = conn.cursor()

        if inventory_flag == "完成品":
            sql = """
            INSERT INTO ADITHYA1.HTSTOCKTAK
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

            params = [
                worker_code,
                int(warehouse_code),
                serno,
                item_cd,
                material_value,
                symbol_value,
                pallet_unit,
                1,
                qty,
                partner_cd_value,
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
        else:
            sql = """
            INSERT INTO ADITHYA1.HTSTOCKTAT
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
                CONFSERNO,
                LOT,
                DESTINATCD,
                CONFROWNO
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, CAST(CURRENT TIMESTAMP AS CHAR(26)),
                ?, ?, ?, ?
            )
            """

            params = [
                worker_code,
                int(warehouse_code),
                serno,
                item_cd,
                material_value,
                symbol_value,
                pallet_unit,
                1,
                qty,
                partner_cd_value,
                int(worker_code),
                conf_serno,
                lot,
                destinat_cd,
                conf_rowno
                
            ]

        print("Parameter count:", len(params))

        for i, p in enumerate(params, 1):
            print(f"P{i}: {p!r} ({type(p).__name__})")

        cursor.execute(sql, params)

        if inventory_flag == "立会い":
            cursor.execute("""
                INSERT INTO ADITHYA1.HTSTOCKQR
                (
                    HTNM,
                    WAREHOUSCD,
                    SERNO,
                    TACIAIFLG,
                    QR
                )
                VALUES (?, ?, ?, '1', ?)
            """, [
                worker_code,
                int(warehouse_code),
                serno,
                qr_code
            ])
        else:
            cursor.execute("""
                INSERT INTO ADITHYA1.HTSTOCKQR
                (
                    HTNM,
                    WAREHOUSCD,
                    SERNO,
                    TACIAIFLG,
                    QR
                )
                VALUES (?, ?, ?, '0', ?)
            """, [
                worker_code,
                int(warehouse_code),
                serno,
                qr_code
            ])
        
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
def delete_stocktak(worker_code: str, warehouse_code: str, qr_code: str, taciaiflg: str, inventory_flag: str):

    conn = None
    cursor = None

    try:
        fields = qr_code.strip().split(",")

        if len(fields) != 12:
            return {
                "success": False,
                "code": "E220"
            }

        conf_serno = int(fields[7])
        lot = int(fields[2])
        destinat_cd = int(fields[4])
        conf_rowno = int(fields[5])

        conn = get_connection()
        cursor = conn.cursor()

        if inventory_flag == "完成品":
            table_name = "ADITHYA1.HTSTOCKTAK"
        else:
            table_name = "ADITHYA1.HTSTOCKTAT"

        sql = f"""
            DELETE FROM {table_name}
            WHERE HTNM = ?
              AND WAREHOUSCD = ?
              AND CONFSERNO = ?
              AND LOT = ?
              AND DESTINATCD = ?
              AND CONFROWNO = ?
        """

        cursor.execute(sql, [
            worker_code,
            int(warehouse_code),
            conf_serno,
            lot,
            destinat_cd,
            conf_rowno
        ])
        taciaiflg = "0" if inventory_flag == "完成品" else "1"

        cursor.execute("""
            DELETE FROM ADITHYA1.HTSTOCKQR
            WHERE HTNM = ?
            AND WAREHOUSCD = ?
            AND SERNO = ?
            AND TACIAIFLG = ?
        """, [
            worker_code,
            int(warehouse_code),
            serno,
            taciaiflg
        ])

        conn.commit()

        return {"success": True}

        deleted = cursor.rowcount

        conn.commit()

        return {
            "success": deleted > 0
        }

    except Exception as e:
        print("Delete Error:", e)
        return {"success": False}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()        
def detail_list(worker_code: str, warehouse_code: str, inventory_flag: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if inventory_flag == "立会い":
            table_name = "ADITHYA1.HTSTOCKTAT"
        else:
            table_name = "ADITHYA1.HTSTOCKTAK"

        if table_name == "ADITHYA1.HTSTOCKTAK":
            sql = f"""
                SELECT
                    MATERIAL,
                    SYMBOL,
                    QTY
                FROM {table_name}
                WHERE HTNM = ?
                AND WAREHOUSCD = ?
                AND DELFLG = ''
                ORDER BY CREATEDT DESC
            """
        else:
            sql = f"""
                SELECT
                    MATERIAL,
                    SYMBOL,
                    QTY
                FROM {table_name}
                WHERE HTNM = ?
                AND WAREHOUSCD = ?
                ORDER BY CREATEDT DESC
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