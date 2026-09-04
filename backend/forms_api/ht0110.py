import traceback
from datetime import datetime
from .connection import get_connection


# ============================================================
# SQL01 / SQL02 / SQL03
# 未転送データチェック
# ============================================================

def check_untransferred_exists(htnm, partner_code):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Partner code comes from HT0100 -> HT0110 frontend
        partner_code_int = int(partner_code)

        if partner_code_int == 11:

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

        elif partner_code_int == 12:

            # SQL02 : U-Cera
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

            # SQL03 : Other
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
        print("PARTNER CODE =", partner_code_int)
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

    except ValueError:
        return {
            "success": False,
            "messageCode": "E102"
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

# ============================================================
# 伝票№ / 注文番号 重複チェック
# SQL13 / SQL14 / SQL15
# ============================================================

def check_slip_no_exists(
    slip_no,
    partner_code,
    htnm,
    delivery_date=None
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        partner_code_int = int(partner_code)

        slip_no_text = (
            str(slip_no)
            .replace(" ", "")
            .strip()
        )

        # ====================================================
        # ACC
        # SQL13
        # ====================================================

        if partner_code_int == 11:

            date_obj = datetime.strptime(
                str(delivery_date).strip(),
                "%Y/%m/%d"
            )

            delivery_value = int(
                date_obj.strftime("%Y%m%d")
            )

            slip_no_int = int(slip_no_text)

            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE
                WHERE HTNM = ?
                  AND DELIVERY = ?
                  AND SLIPNO = ?
            """, (
                htnm,
                delivery_value,
                slip_no_int
            ))

        # ====================================================
        # U-Cera
        # SQL14
        # ====================================================

        elif partner_code_int == 12:

            slip_no_int = int(slip_no_text)

            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE
                WHERE HTNM = ?
                  AND SLIPNO = ?
            """, (
                htnm,
                slip_no_int
            ))

        # ====================================================
        # Other
        # SQL15
        # ====================================================

        else:

            # -----------------------------------------------
            # Order Number format:
            #
            # YYYY MM SSS
            # 2026 01 002
            #
            # ORDERFY    = LEFT 4
            # ORDERMM    = MID 2
            # ORDERSERNO = RIGHT 3
            # -----------------------------------------------

            if len(slip_no_text) != 8 or not slip_no_text.isdigit():

                return {
                    "success": False,
                    "exists": False,
                    "messageCode": "E211",
                    "param": "注文番号"
                }

            order_fy = int(slip_no_text[:3])
            order_mm = int(slip_no_text[3:5])
            order_serno = int(slip_no_text[5:8])

            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTSTORAGE
                WHERE HTNM = ?
                AND ORDERFY = ?
                AND ORDERMM = ?
                AND ORDERSERNO = ?
            """, (
                htnm,
                order_fy,
                order_mm,
                order_serno
            ))

        row = cursor.fetchone()

        count = int(row[0]) if row else 0

        print("-----------------------------------")
        print("HT0110 : SLIPNO CHECK")
        print("HTNM         =", htnm)
        print("SLIPNO       =", slip_no_text)
        print("PARTNER CODE =", partner_code_int)

        if partner_code_int == 11:
            print("DELIVERY     =", delivery_value)

        elif partner_code_int == 0:
            print("ORDERFY      =", order_fy)
            print("ORDERMM      =", order_mm)
            print("ORDERSERNO   =", order_serno)

        print("EXISTS COUNT =", count)
        print("-----------------------------------")

        if count > 0:
            return {
                "success": False,
                "exists": True,
                "messageCode": "E221",
                "param": "入庫"
            }

        return {
            "success": True,
            "exists": False
        }

    except ValueError:

        return {
            "success": False,
            "exists": False,
            "messageCode": "E211",
            "param": (
                "注文番号"
                if str(partner_code) == "0"
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

        delivery_value = None

        if partner_code_int == 11:

            date_text = str(delivery_date).strip()

            date_obj = datetime.strptime(
                date_text,
                "%Y/%m/%d"
            )

            delivery_value = int(
                date_obj.strftime("%Y%m%d")
            )

            print("-----------------------------------")
            print("HT0110 : ACC DELIVERY")
            print("TODAY =", delivery_value)
            print("-----------------------------------")

        # ====================================================
        # ACC
        # PARTNER CODE = 11
        # SQL10
        # ====================================================

        if partner_code_int == 11:

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
                        "messageCode": "E221",
                        "param": "入庫",
                        "slipNo": str(slip_no_int)
                    }

                # --------------------------------------------
                # Get ACC source data
                # --------------------------------------------

                sql_acc = """
                    SELECT
                        A.HASOBI,
                        A.DENPNO,
                        C.SYHNCD,

                        CASE
                            WHEN G.GOMANA IS NULL
                            THEN REPLACE(
                                CONCAT(C.ZISIT1, C.ZISIT2),
                                ',',
                                ' '
                            )
                            ELSE G.GOMANA
                        END AS MATERIAL,

                        CASE
                            WHEN G.GOMATK IS NULL
                            THEN CONCAT(C.HINME1, C.HINME2)
                            ELSE G.GOMATK
                        END AS SYMBOL,

                        C.SYUKSU

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
                """

                print("-----------------------------------")
                print("HT0110 : ACC SQL")
                print(sql_acc)
                print("PARAM 1 HASOBI =", delivery_value)
                print("PARAM 2 DENPNO =", slip_no_int)
                print("-----------------------------------")

                cursor.execute(
                    sql_acc,
                    (
                        delivery_value,
                        slip_no_int
                    )
                )

                rows = cursor.fetchall()

                print("-----------------------------------")
                print("HT0110 : ACC SOURCE RESULT")
                print("ROWS =", len(rows))

                for i, source_row in enumerate(rows, 1):
                    print("ROW", i)
                    print("  HASOBI   =", source_row[0])
                    print("  DENPNO   =", source_row[1])
                    print("  SYHNCD   =", source_row[2])
                    print("  MATERIAL =", source_row[3])
                    print("  SYMBOL   =", source_row[4])
                    print("  SYUKSU   =", source_row[5])

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
                        material,
                        symbol,
                        syuksu
                    ) = source_row
                    
                    # ----------------------------------------
                    # Material
                    #
                    # GOMANA != NULL -> ZISIT1 + ZISIT2
                    # GOMANA = NULL  -> blank
                    # ----------------------------------------

                    item_cd = int(syhncd or 0)

                    material = str(material or "").strip()
                    symbol = str(symbol or "").strip()

                    qty = int(syuksu or 0)

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
                        item_cd,           # ITEMCD
                        material,         # MATERIAL
                        symbol,           # SYMBOL
                        qty               # QTY
                    ))

                    print("-----------------------------------")
                    print("HT0110 : INSERT HTSTORAGE")
                    print("SERNO       =", serno)
                    print("HTNM        =", htnm)
                    print("DELIVERY    =", hasobi)
                    print("SLIPNO      =", denpno)
                    print("SUPPLIERNM  = ACC")
                    print("PARTNERCD   = 11")
                    print("ITEMCD      =", item_cd)
                    print("MATERIAL    =", material)
                    print("SYMBOL      =", symbol)
                    print("QTY         =", qty)
                    print("-----------------------------------")

        # ====================================================
        # U-Cera
        # PARTNER CODE = 12
        # SQL11
        # ====================================================

                # ====================================================
        # U-Cera
        # PARTNER CODE = 12
        # SQL11
        # ====================================================

        elif partner_code_int == 12:

            for slip_no in slip_numbers:

                slip_no_int = int(
                    str(slip_no).replace(" ", "").strip()
                )

                # --------------------------------------------
                # SQL14 : Duplicate check
                #
                # HTNM = Worker Code
                # SLIPNO = Number List
                # --------------------------------------------

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM TYKSFLIB.HTSTORAGE
                    WHERE HTNM = ?
                      AND SLIPNO = ?
                """, (
                    htnm,
                    slip_no_int
                ))

                row = cursor.fetchone()

                count = int(row[0]) if row else 0

                print("-----------------------------------")
                print("HT0110 : U-CERA DUPLICATE CHECK")
                print("HTNM         =", htnm)
                print("SLIPNO       =", slip_no_int)
                print("EXISTS COUNT =", count)
                print("-----------------------------------")

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
                # INSERT every detail row
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

                    # ----------------------------------------
                    # SERNO
                    # ----------------------------------------

                    serno = get_next_serno(cursor)

                    # ----------------------------------------
                    # MATERIAL
                    # GOMANA != NULL -> ZSZSRY
                    # ----------------------------------------

                    material = ""

                    if gomana is not None:
                        material = str(zszsry or "").strip()

                    # ----------------------------------------
                    # SYMBOL
                    # GOMATK != NULL -> GOMATK
                    # ----------------------------------------

                    symbol = ""

                    if gomatk is not None:
                        symbol = str(gomatk).strip()

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
                        serno,
                        htnm,
                        0,
                        0,
                        0,
                        0,
                        int(hmhmno or 0),
                        "UCC",
                        "0",
                        12,
                        int(hmhmgy or 0),
                        int(hmtycd or 0),
                        material,
                        symbol,
                        int(hmnhsu or 0)
                    ))

                    print("-----------------------------------")
                    print("HT0110 : INSERT HTSTORAGE")
                    print("SERNO       =", serno)
                    print("HTNM        =", htnm)
                    print("DELIVERY    = 0")
                    print("SLIPNO      =", hmhmno)
                    print("SUPPLIERNM  = UCC")
                    print("SUPPLIERCD  = 0")
                    print("PARTNERCD   = 12")
                    print("ROWNO       =", hmhmgy)
                    print("ITEMCD      =", hmtycd)
                    print("MATERIAL    =", material)
                    print("SYMBOL      =", symbol)
                    print("QTY         =", hmnhsu)
                    print("-----------------------------------")

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
                        O.DELIVERYD,
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
                        D.QTY AS QTY
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
                        int(detail_partner_cd or 0),       # PARTNERCD
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
                    print("SLIPNO      =0")
                    print("SUPPLIERNM  =", supplier_nm)
                    print("SUPPLIERCD  =", supplier_cd)
                    print("PARTNERCD   =", detail_partner_cd)
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