import traceback
from .connection import get_connection


# ============================================================
# SQL01 / SQL02 / SQL03
# 未転送データチェック
# ============================================================

def check_untransferred_data(htnm, partner_code):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if partner_code == "11":

            # SQL01 : ACC
            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE S
                INNER JOIN TYKSFLIB.HTSTORADTL D
                    ON S.SERNO = D.SERNO
                WHERE S.HTNM = ?
                  AND S.PARTNERCD = 11
                  AND D.TAKEQTY > 0
                  AND D.TRANSFEFLG = ' '
            """, (htnm,))

        elif partner_code == "12":

            # SQL02 : Uセラ
            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE S
                INNER JOIN TYKSFLIB.HTSTORADTL D
                    ON S.SERNO = D.SERNO
                WHERE S.HTNM = ?
                  AND S.PARTNERCD = 12
                  AND D.TAKEQTY > 0
                  AND D.TRANSFEFLG = ' '
            """, (htnm,))

        else:

            # SQL03 : その他
            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE S
                INNER JOIN TYKSFLIB.HTSTORADTL D
                    ON S.SERNO = D.SERNO
                WHERE S.HTNM = ?
                  AND S.PARTNERCD NOT IN (11, 12)
                  AND D.TAKEQTY > 0
                  AND D.TRANSFEFLG = ' '
            """, (htnm,))

        row = cursor.fetchone()
        count = int(row[0]) if row else 0

        print("-----------------------------------")
        print("HT0110 : UNTRANSFERRED CHECK")
        print("HTNM         =", htnm)
        print("PARTNER CODE =", partner_code)
        print("COUNT        =", count)
        print("-----------------------------------")

        if count > 0:
            return {
                "success": False,
                "messageCode": "E221",
                "param": "入庫"
            }

        return {
            "success": True,
            "count": count
        }

    except Exception:

        traceback.print_exc()

        return {
            "success": False,
            "messageCode": "E102"
        }

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# 伝票№ / 注文番号 重複チェック
# ============================================================

def check_slip_no_exists(slip_no, partner_code):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        slip_no_int = int(str(slip_no).strip())

        if partner_code == "11":

            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE
                WHERE PARTNERCD = 11
                  AND SLIPNO = ?
            """, (slip_no_int,))

        elif partner_code == "12":

            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE
                WHERE PARTNERCD = 12
                  AND SLIPNO = ?
            """, (slip_no_int,))

        else:

            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE
                WHERE PARTNERCD NOT IN (11, 12)
                  AND SLIPNO = ?
            """, (slip_no_int,))

        row = cursor.fetchone()
        count = int(row[0]) if row else 0

        print("-----------------------------------")
        print("HT0110 : SLIPNO CHECK")
        print("SLIPNO       =", slip_no_int)
        print("PARTNER CODE =", partner_code)
        print("EXISTS COUNT =", count)
        print("-----------------------------------")

        return {
            "success": True,
            "exists": count > 0
        }

    except ValueError:

        return {
            "success": False,
            "exists": False,
            "messageCode": "E211",
            "param": (
                "注文番号"
                if partner_code == "0"
                else "伝票№"
            )
        }

    except Exception:

        traceback.print_exc()

        return {
            "success": False,
            "exists": False,
            "messageCode": "E102"
        }

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# SERNO取得
# ============================================================

def get_next_serno(cursor):

    cursor.execute("""
        SELECT COALESCE(MAX(SERNO), 0) + 1
        FROM TYKSFLIB.HTSTORAGE
    """)

    row = cursor.fetchone()

    return int(row[0]) if row else 1


# ============================================================
# HTSTORAGEへ登録
#
# ★ F4 実行時だけ呼び出す
#
# NUMERIC  -> 0
# VARCHAR  -> ' '
# SLIPNO   -> 入力番号
# ============================================================

def insert_slip_no(
    htnm,
    delivery_date,
    slip_numbers,
    partner_code
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        partner_code_int = int(partner_code)

        # ----------------------------------------------------
        # DELIVERY
        # 2026/06/08 -> 20260608
        # ----------------------------------------------------

        delivery_value = 0

        if delivery_date:

            date_text = str(delivery_date).replace("/", "").strip()

            if len(date_text) == 8 and date_text.isdigit():
                delivery_value = int(date_text)
            else:
                return {
                    "success": False,
                    "messageCode": "E211",
                    "param": "正しい日付"
                }

        # ----------------------------------------------------
        # Each number -> one HTSTORAGE row
        # ----------------------------------------------------

        for slip_no in slip_numbers:

            slip_no_int = int(str(slip_no).replace(" ", "").strip())

            # -----------------------------------------------
            # Duplicate check
            # -----------------------------------------------

            if partner_code == "11":

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM TYKSFLIB.HTSTORAGE
                    WHERE PARTNERCD = 11
                      AND SLIPNO = ?
                """, (slip_no_int,))

            elif partner_code == "12":

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM TYKSFLIB.HTSTORAGE
                    WHERE PARTNERCD = 12
                      AND SLIPNO = ?
                """, (slip_no_int,))

            else:

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM TYKSFLIB.HTSTORAGE
                    WHERE PARTNERCD NOT IN (11, 12)
                      AND SLIPNO = ?
                """, (slip_no_int,))

            row = cursor.fetchone()
            count = int(row[0]) if row else 0

            if count > 0:

                return {
                    "success": False,
                    "exists": True,
                    "slipNo": str(slip_no_int)
                }

            # -----------------------------------------------
            # Get SERNO
            # -----------------------------------------------

            serno = get_next_serno(cursor)

            # -----------------------------------------------
            # INSERT HTSTORAGE
            # -----------------------------------------------

            cursor.execute("""
                INSERT INTO TYKSFLIB.HTSTORAGE (
                    SERNO,
                    HTNM,
                    DELIVERY,
                    ORDERFY,
                    ORDERMM,
                    ORDERSERNO,
                    SLIPNO,
                    SUPPLIERNM,
                    SUPPLIERCD,
                    PARTNERCD,
                    ROWNO,
                    ITEMCD,
                    MATERIAL,
                    SYMBOL,
                    QTY
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                serno,              # SERNO
                htnm,               # HTNM
                delivery_value,     # DELIVERY
                0,                  # ORDERFY
                0,                  # ORDERMM
                0,                  # ORDERSERNO
                slip_no_int,        # SLIPNO
                " ",                # SUPPLIERNM
                " ",                # SUPPLIERCD
                partner_code_int,   # PARTNERCD
                0,                  # ROWNO
                0,                  # ITEMCD
                " ",                # MATERIAL
                " ",                # SYMBOL
                0                   # QTY
            ))

            print("-----------------------------------")
            print("HT0110 : INSERT HTSTORAGE")
            print("SERNO        =", serno)
            print("HTNM         =", htnm)
            print("DELIVERY     =", delivery_value)
            print("SLIPNO       =", slip_no_int)
            print("PARTNER CODE =", partner_code)
            print("-----------------------------------")

        conn.commit()

        return {
            "success": True,
            "messageCode": "I201"
        }

    except Exception:

        if conn:
            conn.rollback()

        traceback.print_exc()

        return {
            "success": False,
            "messageCode": "E102"
        }

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()