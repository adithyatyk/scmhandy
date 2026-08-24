import traceback
from datetime import datetime
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
# ============================================================
# ACC : Get transfer item data
# SQL10 source data
# ============================================================

def get_acc_transfer_data(cursor, delivery_date, slip_numbers):

    # --------------------------------------------------------
    # Convert frontend date
    # YYYY/MM/DD -> YYYYMMDD
    # --------------------------------------------------------

    date_text = str(delivery_date).strip()

    date_obj = datetime.strptime(
        date_text,
        "%Y/%m/%d"
    )

    delivery_value = int(
        date_obj.strftime("%Y%m%d")
    )

    # --------------------------------------------------------
    # Number list
    # --------------------------------------------------------

    slip_values = [
        int(str(value).replace(" ", "").strip())
        for value in slip_numbers
    ]

    if not slip_values:
        return []

    # --------------------------------------------------------
    # Create ?, ?, ?, ? dynamically
    # --------------------------------------------------------

    placeholders = ",".join(["?"] * len(slip_values))

    sql = f"""
        SELECT
            A.HASOBI,
            A.DENPNO,
            C.SYHNCD,
            REPLACE(
                CONCAT(C.ZISIT1, C.ZISIT2),
                ',',
                ' '
            ) AS ZISIT,

            CONCAT(C.HINME1, C.HINME2) AS HINME,
            C.SYUKSU,
            G.GOMANA,
            G.GOMATK
        FROM ACCSFLIB.FHB0 AS A

        INNER JOIN ACCSFLIB.FHC0 AS C
            ON A.DENPNO = C.DENPNO
           AND A.HASOBI = C.HASOBI

        LEFT JOIN PRDLIBF.GOMAST AS G
            ON C.SYHNCD = G.GOMANO

        WHERE A.HASOBI = ?
          AND A.DENPNO IN ({placeholders})
          AND A.@@JKX = ''
          AND C.@@JKX = ''

        ORDER BY A.DENPNO
    """

    params = [delivery_value] + slip_values

    cursor.execute(sql, params)

    rows = cursor.fetchall()

    print("-----------------------------------")
    print("HT0110 : ACC TRANSFER DATA")
    print("DELIVERY     =", delivery_value)
    print("SLIP NUMBERS =", slip_values)
    print("ROW COUNT    =", len(rows))
    print("-----------------------------------")

    return rows

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

        # ====================================================
        # DELIVERY DATE
        # Frontend : 2026/08/20
        # DB       : 20260820
        # ====================================================

        if not delivery_date:

            return {
                "success": False,
                "messageCode": "E211",
                "param": "納品日"
            }

        date_text = str(delivery_date).strip()

        try:

            date_obj = datetime.strptime(
                date_text,
                "%Y/%m/%d"
            )

        except ValueError:

            return {
                "success": False,
                "messageCode": "E211",
                "param": "正しい日付"
            }

        delivery_value = int(
            date_obj.strftime("%Y%m%d")
        )

        print("-----------------------------------")
        print("HT0110 : DELIVERY")
        print("INPUT    =", date_text)
        print("DELIVERY =", delivery_value)
        print("-----------------------------------")

        # ====================================================
        # ACC
        # PARTNER CODE = 11
        # SQL10
        # ====================================================

        if partner_code == "11":

            for slip_no in slip_numbers:

                slip_no_int = int(
                    str(slip_no).replace(" ", "").strip()
                )

                # --------------------------------------------
                # Duplicate check
                # --------------------------------------------

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM TYKSFLIB.HTSTORAGE
                    WHERE PARTNERCD = 11
                      AND SLIPNO = ?
                """, (
                    slip_no_int,
                ))

                row = cursor.fetchone()

                count = int(row[0]) if row else 0

                if count > 0:

                    return {
                        "success": False,
                        "exists": True,
                        "slipNo": str(slip_no_int)
                    }

                # --------------------------------------------
                # Get ACC source data
                # --------------------------------------------

                cursor.execute("""
                    SELECT
                        A.HASOBI,
                        A.DENPNO,
                        C.SYHNCD,
                        REPLACE(
                            CONCAT(C.ZISIT1, C.ZISIT2),
                            ',',
                            ' '
                        ) AS ZISIT,

                        CONCAT(C.HINME1, C.HINME2) AS HINME,
                        C.SYUKSU,
                        G.GOMANA,
                        G.GOMATK
                    FROM ACCSFLIB.FHB0 AS A

                    INNER JOIN ACCSFLIB.FHC0 AS C
                        ON A.DENPNO = C.DENPNO
                       AND A.HASOBI = C.HASOBI

                    LEFT JOIN PRDLIBF.GOMAST AS G
                        ON C.SYHNCD = G.GOMANO

                    WHERE A.HASOBI = ?
                      AND A.DENPNO = ?
                      AND A.@@JKX = ''
                      AND C.@@JKX = ''

                    ORDER BY A.DENPNO
                """, (
                    delivery_value,
                    slip_no_int
                ))

                rows = cursor.fetchall()

                print("-----------------------------------")
                print("HT0110 : ACC SOURCE DATA")
                print("DELIVERY =", delivery_value)
                print("SLIPNO   =", slip_no_int)
                print("ROWS     =", len(rows))
                print("-----------------------------------")

                # --------------------------------------------
                # No source data
                # --------------------------------------------

                if not rows:

                    return {
                        "success": False,
                        "messageCode": "E211",
                        "param": "伝票№"
                    }

                # --------------------------------------------
                # Insert every detail row
                # --------------------------------------------

                for source_row in rows:

                    (
                        hasobi,
                        denpno,
                        syhncd,
                        zisit,
                        hinme,
                        syuksu,
                        gomana,
                        gomatk
                    ) = source_row
                    
                    # ----------------------------------------
                    # Material
                    #
                    # GOMANA != NULL -> ZISIT1 + ZISIT2
                    # GOMANA = NULL  -> blank
                    # ----------------------------------------

                    material = (
                        str(zisit or "").strip()
                        if gomana is not None
                        else ""
                    )

                    # ----------------------------------------
                    # Symbol
                    #
                    # GOMATK != NULL -> HINME1 + HINME2
                    # GOMATK = NULL  -> blank
                    # ----------------------------------------

                    symbol = (
                        str(hinme or "").strip()
                        if gomatk is not None
                        else ""
                    )

                    # ----------------------------------------
                    # Get next SERNO
                    # ----------------------------------------

                    serno = get_next_serno(cursor)

                    # ----------------------------------------
                    # INSERT HTSTORAGE
                    # ----------------------------------------

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
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?
                        )
                    """, (
                        serno,             # SERNO
                        htnm,              # HTNM
                        int(hasobi),       # DELIVERY
                        0,                 # ORDERFY
                        0,                 # ORDERMM
                        0,                 # ORDERSERNO
                        int(denpno),       # SLIPNO
                        "ACC",             # SUPPLIERNM
                        "0",               # SUPPLIERCD
                        11,                # PARTNERCD
                        0,                 # ROWNO
                        int(syhncd),       # ITEMCD
                        material,          # MATERIAL
                        symbol,            # SYMBOL
                        int(syuksu or 0)   # QTY
                    ))

                    print("-----------------------------------")
                    print("HT0110 : INSERT HTSTORAGE")
                    print("SERNO       =", serno)
                    print("HTNM        =", htnm)
                    print("DELIVERY    =", hasobi)
                    print("SLIPNO      =", denpno)
                    print("SUPPLIERNM  = ACC")
                    print("PARTNERCD   = 11")
                    print("ITEMCD      =", syhncd)
                    print("MATERIAL    =", material)
                    print("SYMBOL      =", symbol)
                    print("QTY         =", syuksu)
                    print("-----------------------------------")

        # ====================================================
        # U-Cera
        # PARTNER CODE = 12
        # SQL11
        # ====================================================

        elif partner_code == "12":

            for slip_no in slip_numbers:

                slip_no_int = int(
                    str(slip_no).replace(" ", "").strip()
                )

                # --------------------------------------------
                # Duplicate check
                # --------------------------------------------

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM TYKSFLIB.HTSTORAGE
                    WHERE PARTNERCD = 12
                    AND SLIPNO = ?
                """, (
                    slip_no_int,
                ))

                row = cursor.fetchone()

                count = int(row[0]) if row else 0

                if count > 0:

                    return {
                        "success": False,
                        "exists": True,
                        "slipNo": str(slip_no_int)
                    }

            # --------------------------------------------
            # SQL11 : Get U-Cera source data
            # --------------------------------------------

            cursor.execute("""
                SELECT
                    H.HMHMNO,
                    H.HMHMGY,
                    H.HMTYCD,
                    H.HMNHSU,
                    Z.ZSZSRY,
                    H.HMSHNM,
                    G.GOMANA,
                    G.GOMATK
                FROM UCFLIB.HSMSD AS H

                LEFT JOIN UCFLIB.ZAISM AS Z
                    ON H.HMZSCD = Z.ZSZSCD

                LEFT JOIN PRDLIBF.GOMAST AS G
                    ON H.HMTYCD = G.GOMANO

                WHERE H.HMHMNO = ?

                ORDER BY H.HMHMNO
            """, (
                slip_no_int,
            ))

            rows = cursor.fetchall()

            print("-----------------------------------")
            print("HT0110 : U-CERA SOURCE DATA")
            print("HMHMNO   =", slip_no_int)
            print("ROWS     =", len(rows))
            print("-----------------------------------")

            # --------------------------------------------
            # No source data
            # --------------------------------------------

            if not rows:

                return {
                    "success": False,
                    "messageCode": "E211",
                    "param": "伝票№"
                }

            # --------------------------------------------
            # Insert every detail row
            # --------------------------------------------

            for source_row in rows:

                (
                    hmhmno,
                    hmhmgy,
                    hmtycd,
                    hmnhsu,
                    zszsry,
                    hmshnm,
                    gomana,
                    gomatk
                ) = source_row

                # ====================================================
        # その他
        # PARTNER CODE = 0
        # SQL12
        # ====================================================

        else:

            for slip_no in slip_numbers:

                # ------------------------------------------------
                # Screen number
                #
                # Example:
                # 202601002
                #
                # FY + MM + SERNO
                # ------------------------------------------------

                slip_no_text = (
                    str(slip_no)
                    .replace(" ", "")
                    .strip()
                )

                try:
                    slip_no_int = int(slip_no_text)
                except ValueError:

                    return {
                        "success": False,
                        "messageCode": "E211",
                        "param": "注文番号"
                    }

                # ------------------------------------------------
                # SQL12 : Get OTHER source data
                # ------------------------------------------------

                cursor.execute("""
                    SELECT
                        O.DELIVERY,
                        O.FY,
                        O.MM,
                        O.SERNO,
                        O.SUPPLIER1,
                        O.SUPPLIERCD,
                        D.PARTNERCD,
                        D.DTLNO,
                        D.ITEMCD,
                        D.MATERIAL,
                        D.SYMBOL,
                        D.QTY - D.HTTAKEQTY AS QTY
                    FROM TYKSFLIB.ORDER AS O

                    INNER JOIN TYKSFLIB.ORDERDTL AS D
                        ON O.FY = D.FY
                       AND O.MM = D.MM
                       AND O.SERNO = D.SERNO

                    WHERE
                        (
                            DIGITS(O.FY)
                            CONCAT DIGITS(O.MM)
                            CONCAT DIGITS(O.SERNO)
                        ) = ?

                        AND D.ITEMCD <> 0
                        AND D.NOINSPFLG <> '1'
                        AND D.HTTAKEFLG = ' '

                    ORDER BY D.DTLNO
                """, (
                    slip_no_text,
                ))

                rows = cursor.fetchall()

                print("-----------------------------------")
                print("HT0110 : OTHER SOURCE DATA")
                print("ORDER NO =", slip_no_text)
                print("ROWS     =", len(rows))
                print("-----------------------------------")

                # ------------------------------------------------
                # No source data
                # ------------------------------------------------

                if not rows:

                    return {
                        "success": False,
                        "messageCode": "E211",
                        "param": "注文番号"
                    }

                # ------------------------------------------------
                # Insert every detail row
                # ------------------------------------------------

                for source_row in rows:

                    (
                        delivery,
                        order_fy,
                        order_mm,
                        order_serno,
                        supplier_nm,
                        supplier_cd,
                        detail_partner_cd,
                        dtl_no,
                        item_cd,
                        material,
                        symbol,
                        qty
                    ) = source_row

                    # --------------------------------------------
                    # Get next SERNO
                    # --------------------------------------------

                    serno = get_next_serno(cursor)

                    # --------------------------------------------
                    # INSERT HTSTORAGE
                    # --------------------------------------------

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
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?
                        )
                    """, (
                        serno,                    # SERNO
                        htnm,                     # HTNM
                        int(delivery or 0),      # DELIVERY
                        int(order_fy or 0),      # ORDERFY
                        int(order_mm or 0),      # ORDERMM
                        int(order_serno or 0),   # ORDERSERNO
                        0,                        # SLIPNO
                        str(supplier_nm or "").strip(),
                        str(supplier_cd or "").strip(),
                        0,                        # PARTNERCD
                        int(dtl_no or 0),         # ROWNO
                        int(item_cd or 0),        # ITEMCD
                        str(material or "").strip(),
                        str(symbol or "").strip(),
                        int(qty or 0)             # QTY - HTTAKEQTY
                    ))

                    print("-----------------------------------")
                    print("HT0110 : INSERT HTSTORAGE")
                    print("SERNO       =", serno)
                    print("HTNM        =", htnm)
                    print("DELIVERY    =", delivery)
                    print("ORDERFY     =", order_fy)
                    print("ORDERMM     =", order_mm)
                    print("ORDERSERNO  =", order_serno)
                    print("SLIPNO      = 0")
                    print("SUPPLIERNM  =", supplier_nm)
                    print("SUPPLIERCD  =", supplier_cd)
                    print("PARTNERCD   = 0")
                    print("ROWNO       =", dtl_no)
                    print("ITEMCD      =", item_cd)
                    print("MATERIAL    =", material)
                    print("SYMBOL      =", symbol)
                    print("QTY         =", qty)
                    print("-----------------------------------")

        # ====================================================
        # COMMIT
        # ====================================================

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