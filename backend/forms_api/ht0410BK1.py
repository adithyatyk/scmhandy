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
            table_name = "TYKSFLIB.HTSTOCKTAT"
        else:
            table_name = "TYKSFLIB.HTSTOCKTAK"

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
        print("MAXIMUM")
        row = cursor.fetchone()
        print("Fetched row:", row)

        if row and row[0] is not None:
            print("Returning:", int(row[0]))
            return int(row[0])

        print("Returning 0")
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
            FROM TYKSFLIB.HTSTOCKQR
            WHERE QR = ?
              AND TACIAIFLG = ?
        """

        cursor.execute(sql, [qr_code, taciaiflg])
        print("duplicateqr complete")
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
            FROM TYKSFLIB.HTTAKE
            WHERE CONFSERNO = ?
              AND LOT = ?
              AND DESTINATCD = ?
              AND CONFROWNO = ?
              AND PARTNERCD = ?
              AND SHIPMENFLG <> ''
        """
        print("check_httake Parameters:", conf_serno, lot, destinat_cd, conf_rowno, partner_cd)
        print("check_httake SQL:", sql)
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
def check_gomast(material: str, symbol: str, partner_cd: int):

    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()        

        sql = """
            SELECT GOMANO
            FROM PRDLIBF.GOMAST
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

        print("========================================")
        print("QR INPUT:")
        print(qr_code)
        print("========================================")
        print("Total fields:", len(fields))
        print("Fields:", fields)

        if len(fields) < 6:
            return {
                "success": False,
                "code": "E220",
                "param": "確認用紙"
            }

        conf_type = fields[0].strip()

        print("conf_type:", conf_type)

        # =====================================================
        # COMMON HEADER
        # =====================================================

        partner_cd = int(fields[1])
        lot = int(fields[2])
        conf_serno = int(fields[3])
        destinat_cd = int(fields[4])

        print("----------------------------------------")
        print("HEADER")
        print("partner_cd :", partner_cd)
        print("lot        :", lot)
        print("conf_serno :", conf_serno)
        print("destinat_cd:", destinat_cd)
        print("----------------------------------------")

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
                print("ERROR: G/T detail field count is not multiple of 4")

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

                print(f"DETAIL {len(details)}:")
                print("  item_cd :", item_cd)
                print("  material:", material)
                print("  symbol  :", symbol)
                print("  qty     :", qty)

        # =====================================================
        # F
        # Detail = 7 fields
        #
        # Period
        # month
        # serial8
        # item_cd
        # material
        # symbol
        # qty
        # =====================================================

        elif conf_type == "F":

            detail_fields = fields[5:]

            if len(detail_fields) % 7 != 0:
                print("ERROR: F detail field count is not multiple of 7")

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

                print(f"DETAIL {len(details)}:")
                print("  period  :", period)
                print("  month   :", month)
                print("  serial8 :", serial8)
                print("  item_cd :", item_cd)
                print("  material:", material)
                print("  symbol  :", symbol)
                print("  qty     :", qty)

        # =====================================================
        # INVALID CONF TYPE
        # =====================================================

        else:

            print("ERROR: Unknown conf_type:", conf_type)

            return {
                "success": False,
                "code": "E220",
                "param": "確認用紙"
            }

        print("----------------------------------------")
        print("Total details:", len(details))
        print("========================================")   

        # =====================================================
        # GET FIRST SERNO
        # =====================================================        

        conn = get_connection()
        cursor = conn.cursor()

        serno = 1
        qr_serno = 1

        # =====================================================
        # DELETE PREVIOUS DATA BEFORE NEW INSERT
        # =====================================================

        if inventory_flag == "完成品":
            table_name = "TYKSFLIB.HTSTOCKTAK"
        else:
            table_name = "TYKSFLIB.HTSTOCKTAT"

        print("========================================")
        print("DELETE PREVIOUS DATA")
        print("TABLE:", table_name)
        print("HTNM:", worker_code)
        print("WAREHOUSCD:", warehouse_code)
        print("TACIAIFLG:", taciaiflg)
        print("========================================")

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

        print("Previous stock rows deleted:", stock_deleted)

        # -----------------------------------------------------
        # Delete previous QR data
        # -----------------------------------------------------

        delete_qr_sql = """
            DELETE FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
            AND WAREHOUSCD = ?
            AND TACIAIFLG = ?
        """

        cursor.execute(
            delete_qr_sql,
            [
                worker_code,
                int(warehouse_code),
                taciaiflg
            ]
        )

        qr_deleted = cursor.rowcount

        print("Previous QR rows deleted:", qr_deleted)

        # =====================================================
        # PROCESS EACH DETAIL
        # =====================================================

        for index, detail in enumerate(details, start=1):

            conf_rowno = index

            item_cd = detail["item_cd"]
            material = detail["material"]
            symbol = detail["symbol"]
            qty = detail["qty"]

            print("----------------------------------------")
            print("PROCESSING DETAIL")
            print("CONFROWNO:", conf_rowno)
            print("item_cd :", item_cd)
            print("material:", material)
            print("symbol  :", symbol)
            print("qty     :", qty)
            print("----------------------------------------")

            count = check_httake(
                conf_serno,
                lot,
                destinat_cd,
                conf_rowno,
                partner_cd
            )

            print("HTTAKE Count:", count)

            if count > 0:
                return {
                    "success": False,
                    "code": "E226"
                }

            # =================================================
            # GOMAST CHECK
            # =================================================

            exists = check_gomast(
                material,
                symbol,
                partner_cd
            )

            if exists:
                material_value = material
                symbol_value = symbol
                partner_cd_value = partner_cd
            else:
                material_value = ""
                symbol_value = ""
                partner_cd_value = 0


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

            print("Parameter count:", len(params))

            for i, p in enumerate(params, 1):
                print(f"P{i}: {p!r} ({type(p).__name__})")
                print("INSERT QUERY:")
                print(sql)
            cursor.execute(sql, params)

            # Next detail gets next SERNO
            serno += 1

        if inventory_flag == "立会い":
            cursor.execute("""
                INSERT INTO TYKSFLIB.HTSTOCKQR
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
                qr_serno,
                qr_code
            ])
        else:
            cursor.execute("""
                INSERT INTO TYKSFLIB.HTSTOCKQR
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
                qr_serno,
                qr_code
            ])
        
        conn.commit()

        return {
            "success": True
        }

    except Exception as e:
        print("Insert Error:", e)

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

        print("========================================")
        print("DELETE QR INPUT:")
        print(qr_code)
        print("Total fields:", len(fields))
        print("Fields:", fields)
        print("========================================")

        # G / T QR
        # Header = 5 fields
        # Detail = 4 fields each
        #
        # F QR
        # Header = 5 fields
        # Detail = 7 fields each

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

        print("CONF TYPE:", conf_type)
        print("DETAIL COUNT:", detail_count)

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

        print("========================================")
        print("CHECK HTSTOCKQR")
        print(sql_qr)
        print(
            "HTNM:",
            worker_code,
            "WAREHOUSCD:",
            warehouse_code,
            "QR:",
            qr_code,
            "TACIAIFLG:",
            taciaiflg
        )
        print("========================================")

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
            print("QR NOT FOUND IN HTSTOCKQR")

            return {
                "success": False,
                "code": "E215"
            }

        qr_serno = int(qr_row[0])

        print("QR SERNO:", qr_serno)

        # =====================================================
        # QR HEADER
        # =====================================================

        partner_cd = int(fields[1])
        lot = int(fields[2])
        conf_serno = int(fields[3])
        destinat_cd = int(fields[4])

        print("----------------------------------------")
        print("DELETE HEADER")
        print("partner_cd :", partner_cd)
        print("lot        :", lot)
        print("conf_serno :", conf_serno)
        print("destinat_cd:", destinat_cd)
        print("----------------------------------------")

        # =====================================================
        # TABLE
        # =====================================================

        if inventory_flag == "完成品":
            table_name = "TYKSFLIB.HTSTOCKTAK"
        else:
            table_name = "TYKSFLIB.HTSTOCKTAT"

        print("DELETE TABLE:", table_name)

        # =====================================================
        # CHECK HTTAKE FOR EVERY DETAIL
        # =====================================================

        for index in range(1, detail_count + 1):

            conf_rowno = index

            print("----------------------------------------")
            print("CHECK DETAIL:", conf_rowno)
            print("----------------------------------------")

            count = check_httake(
                conf_serno,
                lot,
                destinat_cd,
                conf_rowno,
                partner_cd
            )

            print("HTTAKE Count:", count)

            if count > 0:

                print(
                    "HTTAKE EXISTS - DELETE NOT ALLOWED:",
                    conf_rowno
                )

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

        print("========================================")
        print("DELETE STOCK QUERY:")
        print(delete_sql)
        print("PARAMETERS:", delete_params)
        print("========================================")

        cursor.execute(
            delete_sql,
            delete_params
        )

        stock_deleted = cursor.rowcount

        print("STOCK ROWS DELETED:", stock_deleted)

        # =====================================================
        # DELETE QR
        # =====================================================

        delete_qr_sql = """
            DELETE FROM TYKSFLIB.HTSTOCKQR
            WHERE HTNM = ?
              AND WAREHOUSCD = ?
              AND QR = ?
              AND TACIAIFLG = ?
        """

        delete_qr_params = [
            worker_code,
            int(warehouse_code),
            qr_code,
            taciaiflg
        ]

        print("========================================")
        print("DELETE QR QUERY:")
        print(delete_qr_sql)
        print("PARAMETERS:", delete_qr_params)
        print("========================================")

        cursor.execute(
            delete_qr_sql,
            delete_qr_params
        )

        qr_deleted = cursor.rowcount

        print("QR ROWS DELETED:", qr_deleted)

        # =====================================================
        # COMMIT
        # =====================================================

        conn.commit()

        print("========================================")
        print("DELETE SUCCESS")
        print("STOCK ROWS:", stock_deleted)
        print("QR ROWS:", qr_deleted)
        print("========================================")

        return {
            "success": True
        }

    except Exception as e:

        print("Delete Error:", e)

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
        print("Error:", e)
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

        print(sql)
        print(
            worker_code,
            warehouse_code,
            qr_code,
            taciaiflg
        )

        cursor.execute(sql, [
            worker_code,
            int(warehouse_code),
            qr_code,
            taciaiflg
        ])

        row = cursor.fetchone()

        return int(row[0]) > 0 if row else False

    except Exception as e:
        print("check_stockqr Error:", e)
        return False

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()       