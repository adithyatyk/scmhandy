from .connection import get_connection
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

        cursor.execute(sql)

        rows = []

        for row in cursor.fetchall():

            rows.append({
                "code": str(row[0]).strip(),
                "name": str(row[1]).strip()
            })

        return rows

    except Exception as e:

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
            table_name = "TYKSFLIB.HTSTOCKTAT"
        else:
            table_name = "TYKSFLIB.HTSTOCKTAK"

        if table_name == "TYKSFLIB.HTSTOCKTAK":
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
        
        cursor.execute(sql, [worker_code, int(warehouse_code)])

        row = cursor.fetchone()

        return int(row[0]) if row else 0

    except Exception as e:

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
            table_name = "TYKSFLIB.HTSTOCKTAT"
        else:
            table_name = "TYKSFLIB.HTSTOCKTAK"

        sql = f"""
            SELECT MAX(SERNO)
            FROM {table_name}
            WHERE HTNM = ?
            AND WAREHOUSCD = ?
        """
        cursor.execute(sql, [worker_code, int(warehouse_code)])
       
        row = cursor.fetchone()
        

        if row and row[0] is not None:
            
            return int(row[0])

        
        return 0

    except Exception as e:
        
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
            FROM TYKSFLIB.HTSTOCKQR
            WHERE QR = ?
              AND TACIAIFLG = ?
        """

        cursor.execute(sql, [qr_code, taciaiflg])
        
        row = cursor.fetchone()

        if row:
            return {"duplicate": True}

        return {"duplicate": False}

    except Exception as e:
        
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
            FROM TYKSFLIB.HTTAKE
            WHERE CONFSERNO = ?
              AND LOT = ?
              AND DESTINATCD = ?
              AND CONFROWNO = ?
              AND PARTNERCD = ?
              AND SHIPMENFLG <> ''
        """        
        cursor.execute(sql, [
            conf_serno,
            lot,
            destinat_cd,
            conf_rowno,
            partner_cd
        ])

        row = cursor.fetchone()

        return int(row[0]) if row else 0

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

        if len(fields) < 6:
            return {
                "success": False,
                "code": "E220",
                "param": "確認用紙"
            }

        conf_type = fields[0].strip()

        # =====================================================
        # COMMON HEADER
        # =====================================================

        partner_cd = int(fields[1])
        lot = int(fields[2])
        conf_serno = int(fields[3])
        destinat_cd = int(fields[4])

        # =====================================================
        # G / T
        # Detail = 4 fields
        #
        # item_cd
        # material
        # symbol
        # qty
        # =====================================================

        if conf_type in ("G", "T"):

            detail_fields = fields[5:]

            if len(detail_fields) % 4 != 0:

                return {
                    "success": False,
                    "code": "E220",
                    "param": "確認用紙"
                }

            details = []

            for i in range(0, len(detail_fields), 4):

                item_cd = int(detail_fields[i])
                material = detail_fields[i + 1].strip()
                symbol = detail_fields[i + 2].strip()
                qty = int(detail_fields[i + 3])

                detail = {
                    "item_cd": item_cd,
                    "material": material,
                    "symbol": symbol,
                    "qty": qty
                }

                details.append(detail)

        elif conf_type == "F":

            detail_fields = fields[5:]

            if len(detail_fields) % 7 != 0:
                
                return {
                    "success": False,
                    "code": "E220",
                    "param": "確認用紙"
                }

            details = []

            for i in range(0, len(detail_fields), 7):

                period = detail_fields[i].strip()
                month = detail_fields[i + 1].strip()
                serial8 = detail_fields[i + 2].strip()
                item_cd = int(detail_fields[i + 3])
                material = detail_fields[i + 4].strip()
                symbol = detail_fields[i + 5].strip()
                qty = int(detail_fields[i + 6])

                detail = {
                    "period": period,
                    "month": month,
                    "serial8": serial8,
                    "item_cd": item_cd,
                    "material": material,
                    "symbol": symbol,
                    "qty": qty
                }

                details.append(detail)

        # =====================================================
        # INVALID CONF TYPE
        # =====================================================

        else:

            return {
                "success": False,
                "code": "E220",
                "param": "確認用紙"
            }


        # =====================================================
        # GET FIRST SERNO
        # =====================================================        

        conn = get_connection()
        cursor = conn.cursor()

        serno = 1
        # qr_serno = 1

        # =====================================================
        # DELETE PREVIOUS DATA BEFORE NEW INSERT
        # =====================================================

        if inventory_flag == "完成品":
            table_name = "TYKSFLIB.HTSTOCKTAK"
        else:
            table_name = "TYKSFLIB.HTSTOCKTAT"

        # -----------------------------------------------------
        # Delete previous stock/detail data
        # -----------------------------------------------------

        delete_stock_sql = f"""
            DELETE FROM {table_name}
            WHERE HTNM = ?
            AND WAREHOUSCD = ?
        """

        cursor.execute(
            delete_stock_sql,
            [
                worker_code,
                int(warehouse_code)
            ]
        )

        stock_deleted = cursor.rowcount

        # =====================================================
        # PROCESS EACH DETAIL
        # =====================================================

        for index, detail in enumerate(details, start=1):

            conf_rowno = index

            item_cd = detail["item_cd"]
            material = detail["material"]
            symbol = detail["symbol"]
            qty = detail["qty"]

            count = check_httake(
                conf_serno,
                lot,
                destinat_cd,
                conf_rowno,
                partner_cd
            )

            if count > 0:
                return {
                    "success": False,
                    "code": "E226"
                }

            count = check_httake(
                    conf_serno,
                    lot,
                    destinat_cd,
                    conf_rowno,
                    partner_cd
                )

            if count > 0:
                return {
                    "success": False,
                    "code": "E226"
                }

            material_value = material
            symbol_value = symbol
            partner_cd_value = partner_cd

            # =================================================
            # INSERT
            # =================================================            

            if inventory_flag == "完成品":

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

                params = [
                    worker_code,
                    int(warehouse_code),
                    serno,
                    item_cd,
                    material_value,
                    symbol_value,
                    qty,
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
                INSERT INTO TYKSFLIB.HTSTOCKTAT
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
                    qty,
                    1,
                    qty,
                    partner_cd_value,
                    int(worker_code),
                    conf_serno,
                    lot,
                    destinat_cd,
                    conf_rowno
                ]

            for i, p in enumerate(params, 1):
 
                cursor.execute(sql, params)

                # Next detail gets next SERNO
                serno += 1

        # =====================================================
        # GET NEXT SERNO FOR HTSTOCKQR
        # =====================================================

        cursor.execute("""
            SELECT MAX(SERNO)
            FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
            AND WAREHOUSCD = ?
            AND TACIAIFLG = ?
        """, [
            worker_code,
            int(warehouse_code),
            taciaiflg
        ])

        row = cursor.fetchone()

        if row and row[0] is not None:
            qr_serno = int(row[0]) + 1
        else:
            qr_serno = 1

        # =====================================================
        # INSERT HTSTOCKQR
        # =====================================================

        cursor.execute("""
            INSERT INTO TYKSFLIB.HTSTOCKQR
            (
                HTNM,
                WAREHOUSCD,
                SERNO,
                TACIAIFLG,
                QR
            )
            VALUES (?, ?, ?, ?, ?)
        """, [
            worker_code,
            int(warehouse_code),
            qr_serno,
            taciaiflg,
            qr_code
        ])
        
        conn.commit()

        return {
            "success": True
        }

    except Exception as e:

        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        return {
            "success": False,
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
def check_delete_stocktak(
    worker_code: str,
    warehouse_code: str,
    qr_code: str,
    taciaiflg: str
):

    conn = None
    cursor = None

    try:
        fields = qr_code.strip().split(",")

        if len(fields) < 6:
            return {
                "success": False,
                "code": "E220",
                "param": "確認用紙"
            }

        conf_type = fields[0].strip()

        # -----------------------------
        # Check detail count
        # -----------------------------

        if conf_type in ("G", "T"):

            detail_fields = fields[5:]

            if len(detail_fields) % 4 != 0:
                return {
                    "success": False,
                    "code": "E220",
                    "param": "確認用紙"
                }

            detail_count = len(detail_fields) // 4

        elif conf_type == "F":

            detail_fields = fields[5:]

            if len(detail_fields) % 7 != 0:
                return {
                    "success": False,
                    "code": "E220",
                    "param": "確認用紙"
                }

            detail_count = len(detail_fields) // 7

        else:

            return {
                "success": False,
                "code": "E220",
                "param": "確認用紙"
            }

        # -----------------------------
        # QR header
        # -----------------------------

        partner_cd = int(fields[1])
        lot = int(fields[2])
        conf_serno = int(fields[3])
        destinat_cd = int(fields[4])

        # -----------------------------
        # Check QR exists
        # -----------------------------

        conn = get_connection()
        cursor = conn.cursor()

        sql_qr = """
            SELECT SERNO
            FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
              AND WAREHOUSCD = ?
              AND QR = ?
              AND TACIAIFLG = ?
        """

        cursor.execute(
            sql_qr,
            [
                worker_code,
                int(warehouse_code),
                qr_code,
                taciaiflg
            ]
        )

        qr_row = cursor.fetchone()

        if not qr_row:
            return {
                "success": False,
                "code": "E215"
            }

        # -----------------------------
        # Check HTTAKE
        # -----------------------------

        for index in range(1, detail_count + 1):

            conf_rowno = index

            count = check_httake(
                conf_serno,
                lot,
                destinat_cd,
                conf_rowno,
                partner_cd
            )

           
            if count > 0:

                return {
                    "success": False,
                    "code": "E226"
                }

        # -----------------------------
        # All checks passed
        # -----------------------------

        return {
            "success": True,
            "code": "Q204"
        }

    except Exception as e:

        return {
            "success": False,
            "code": "E229",
            "message": str(e)
        }

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
def delete_stocktak(
    worker_code: str,
    warehouse_code: str,
    qr_code: str,
    taciaiflg: str,
    inventory_flag: str
):

    conn = None
    cursor = None

    try:
        # =====================================================
        # QR PARSE
        # =====================================================

        fields = qr_code.strip().split(",")

        if len(fields) < 6:
            return {
                "success": False,
                "code": "E220",
                "param": "確認用紙"
            }

        conf_type = fields[0].strip()

        if conf_type in ("G", "T"):

            detail_fields = fields[5:]

            if len(detail_fields) % 4 != 0:
                return {
                    "success": False,
                    "code": "E220",
                    "param": "確認用紙"
                }

            detail_count = len(detail_fields) // 4

        elif conf_type == "F":

            detail_fields = fields[5:]

            if len(detail_fields) % 7 != 0:
                return {
                    "success": False,
                    "code": "E220",
                    "param": "確認用紙"
                }

            detail_count = len(detail_fields) // 7

        else:

            return {
                "success": False,
                "code": "E220",
                "param": "確認用紙"
            }

        # =====================================================
        # CHECK QR EXISTS IN HTSTOCKQR
        # =====================================================

        conn = get_connection()
        cursor = conn.cursor()

        sql_qr = """
            SELECT SERNO
            FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
              AND WAREHOUSCD = ?
              AND QR = ?
              AND TACIAIFLG = ?
        """

        cursor.execute(
            sql_qr,
            [
                worker_code,
                int(warehouse_code),
                qr_code,
                taciaiflg
            ]
        )

        qr_row = cursor.fetchone()

        if not qr_row:

            return {
                "success": False,
                "code": "E215"
            }

        qr_serno = int(qr_row[0])

        # =====================================================
        # QR HEADER
        # =====================================================

        partner_cd = int(fields[1])
        lot = int(fields[2])
        conf_serno = int(fields[3])
        destinat_cd = int(fields[4])

        # =====================================================
        # TABLE
        # =====================================================

        if inventory_flag == "完成品":
            table_name = "TYKSFLIB.HTSTOCKTAK"
        else:
            table_name = "TYKSFLIB.HTSTOCKTAT"

        # =====================================================
        # CHECK HTTAKE FOR EVERY DETAIL
        # =====================================================

        for index in range(1, detail_count + 1):

            conf_rowno = index

            count = check_httake(
                conf_serno,
                lot,
                destinat_cd,
                conf_rowno,
                partner_cd
            )

            if count > 0:

                conn.rollback()

                return {
                    "success": False,
                    "code": "E226"
                }

        # =====================================================
        # DELETE ALL CORRESPONDING TAK / TAT ROWS
        # =====================================================

        delete_sql = f"""
            DELETE FROM {table_name}
            WHERE HTNM = ?
              AND WAREHOUSCD = ?
              AND CONFSERNO = ?
              AND LOT = ?
              AND DESTINATCD = ?
        """

        delete_params = [
            worker_code,
            int(warehouse_code),
            conf_serno,
            lot,
            destinat_cd
        ]

        cursor.execute(
            delete_sql,
            delete_params
        )

        stock_deleted = cursor.rowcount

        # =====================================================
        # DELETE QR
        # =====================================================

        delete_qr_sql = """
            DELETE FROM TYKSFLIB.HTSTOCKQR
            WHERE QR = ?
        """

        delete_qr_params = [
            qr_code,
        ]

        cursor.execute(
            delete_qr_sql,
            delete_qr_params
        )

        qr_deleted = cursor.rowcount

        # =====================================================
        # COMMIT
        # =====================================================

        conn.commit()

        return {
            "success": True
        }

    except Exception as e:

        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        return {
            "success": False,
            "code": "E229",
            "message": str(e)
        }

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
def detail_list(worker_code: str, warehouse_code: str, inventory_flag: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if inventory_flag == "立会い":
            table_name = "TYKSFLIB.HTSTOCKTAT"
        else:
            table_name = "TYKSFLIB.HTSTOCKTAK"

        if table_name == "TYKSFLIB.HTSTOCKTAK":
            sql = f"""
                SELECT
                    MATERIAL,
                    SYMBOL,
                    QTY
                FROM {table_name}
                WHERE HTNM = ?
                AND WAREHOUSCD = ?
                AND DELFLG = ''
                ORDER BY CREATEDT ASC
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
                ORDER BY CREATEDT ASC
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
        
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def check_stockqr(worker_code: str, warehouse_code: str, qr_code: str, taciaiflg: str):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT COUNT(*)
            FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
              AND WAREHOUSCD = ?
              AND QR = ?
              AND TACIAIFLG = ?
        """

        cursor.execute(sql, [
            worker_code,
            int(warehouse_code),
            qr_code,
            taciaiflg
        ])

        row = cursor.fetchone()

        return int(row[0]) > 0 if row else False

    except Exception as e:
        
        return False

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()       