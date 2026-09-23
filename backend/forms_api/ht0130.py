from .connection import get_connection


# ============================================================
# SQL 0-1 : ACC
# ============================================================

def get_acc_list(htnm):
    conn = get_connection()

    sql = """
        SELECT
            HTSTORAGE.SLIPNO,
            SUM(HTSTORAGE.QTY),
            SUM(HTSTORADTL.TAKEQTY),
            HTSTORADTL.TRANSFEFLG,
            HTSTORAGE.DELIVERY,
            HTSTORAGE.PARTNERCD
        FROM TYKSFLIB.HTSTORAGE
        INNER JOIN TYKSFLIB.HTSTORADTL
            ON HTSTORAGE.SERNO = HTSTORADTL.SERNO
        WHERE
            HTSTORAGE.HTNM = ?
            AND HTSTORAGE.SLIPNO > 0
            AND HTSTORAGE.PARTNERCD = 11
        GROUP BY
            HTSTORAGE.SLIPNO,
            HTSTORADTL.TRANSFEFLG,
            HTSTORAGE.DELIVERY,
            HTSTORAGE.PARTNERCD
    """

    try:
        cur = conn.cursor()
        cur.execute(sql, (htnm,))

        rows = cur.fetchall()

        return [
            {
                "slipNo": row[0],
                "qty": row[1] or 0,
                "takeQty": row[2] or 0,
                "transfeFlg": row[3],
                "delivery": row[4],
                "partnerCd": row[5],
            }
            for row in rows
        ]

    finally:
        conn.close()


# ============================================================
# SQL 0-2 : U-Cera
# ============================================================

def get_ucera_list(htnm):
    conn = get_connection()

    sql = """
        SELECT
            HTSTORAGE.SLIPNO,
            SUM(HTSTORAGE.QTY),
            SUM(HTSTORADTL.TAKEQTY),
            HTSTORADTL.TRANSFEFLG,
            HTSTORAGE.DELIVERY,
            HTSTORAGE.PARTNERCD
        FROM TYKSFLIB.HTSTORAGE
        INNER JOIN TYKSFLIB.HTSTORADTL
            ON HTSTORAGE.SERNO = HTSTORADTL.SERNO
        WHERE
            HTSTORAGE.HTNM = ?
            AND HTSTORAGE.SLIPNO > 0
            AND HTSTORAGE.PARTNERCD = 12
        GROUP BY
            HTSTORAGE.SLIPNO,
            HTSTORADTL.TRANSFEFLG,
            HTSTORAGE.DELIVERY,
            HTSTORAGE.PARTNERCD
    """

    try:
        cur = conn.cursor()
        cur.execute(sql, (htnm,))

        rows = cur.fetchall()

        return [
            {
                "slipNo": row[0],
                "qty": row[1] or 0,
                "takeQty": row[2] or 0,
                "transfeFlg": row[3],
                "delivery": row[4],
                "partnerCd": row[5],
            }
            for row in rows
        ]

    finally:
        conn.close()


# ============================================================
# SQL 0-3 : Other outsourced
# ============================================================

def get_other_list(htnm):
    conn = get_connection()

    sql = """
        SELECT
            HTSTORAGE.ORDERFY,
            HTSTORAGE.ORDERMM,
            HTSTORAGE.ORDERSERNO,
            SUM(HTSTORAGE.QTY),
            SUM(HTSTORADTL.TAKEQTY),
            HTSTORADTL.TRANSFEFLG,
            HTSTORAGE.DELIVERY,
            0 AS PARTNERCD
        FROM TYKSFLIB.HTSTORAGE
        INNER JOIN TYKSFLIB.HTSTORADTL
            ON HTSTORAGE.SERNO = HTSTORADTL.SERNO
        WHERE
            HTSTORAGE.HTNM = ?
            AND HTSTORAGE.SLIPNO = 0
        GROUP BY
            HTSTORAGE.ORDERFY,
            HTSTORAGE.ORDERMM,
            HTSTORAGE.ORDERSERNO,
            HTSTORADTL.TRANSFEFLG,
            HTSTORAGE.DELIVERY
    """

    try:
        cur = conn.cursor()
        cur.execute(sql, (htnm,))

        rows = cur.fetchall()

        return [
            {
                "orderFy": row[0],
                "orderMm": row[1],
                "orderSerNo": row[2],
                "qty": row[3] or 0,
                "takeQty": row[4] or 0,
                "transfeFlg": row[5],
                "delivery": row[6],
                "partnerCd": row[7],
            }
            for row in rows
        ]

    finally:
        conn.close()


# ============================================================
# HT0130 LIST
# ============================================================

def get_ht0130_list(htnm):

    acc_rows = get_acc_list(htnm)
    ucera_rows = get_ucera_list(htnm)
    other_rows = get_other_list(htnm)

    rows = []

    all_rows = acc_rows + ucera_rows + other_rows

    for row in all_rows:

        qty = row.get("qty", 0) or 0
        take_qty = row.get("takeQty", 0) or 0

        # ----------------------------------------
        # Result
        # ----------------------------------------

        if qty == take_qty:
            result = "OK"

        elif take_qty == 0:
            result = "未"

        elif qty > take_qty:
            result = "不足"

        else:
            result = "超過"

        # ----------------------------------------
        # Transfer
        # ----------------------------------------

        if str(row.get("transfeFlg", "")).strip() == "1":
            transfer = "済"
        else:
            transfer = "未"

        rows.append({
            "slipNo": row.get("slipNo"),
            "orderFy": row.get("orderFy"),
            "orderMm": row.get("orderMm"),
            "orderSerNo": row.get("orderSerNo"),
            "qty": qty,
            "takeQty": take_qty,
            "transfeFlg": row.get("transfeFlg"),
            "result": result,
            "transfer": transfer,
            "delivery": row.get("delivery"),
            "partnerCd": row.get("partnerCd"),
        })

    return rows


# ============================================================
# Find SERNO : ACC / U-Cera
# ============================================================

def get_serno_acc_ucera(
    htnm,
    slip_no,
    delivery,
    partner_cd,
    transfe_flg
):
    conn = get_connection()

    sql = """
        SELECT DISTINCT
            HTSTORAGE.SERNO
        FROM TYKSFLIB.HTSTORAGE
        INNER JOIN TYKSFLIB.HTSTORADTL
            ON HTSTORAGE.SERNO = HTSTORADTL.SERNO
        WHERE
            HTSTORAGE.HTNM = ?
            AND HTSTORAGE.SLIPNO = ?
            AND HTSTORAGE.DELIVERY = ?
            AND HTSTORAGE.PARTNERCD = ?
            AND HTSTORADTL.TRANSFEFLG = ?
    """

    try:
        cur = conn.cursor()

        cur.execute(
            sql,
            (
                htnm,
                slip_no,
                delivery,
                partner_cd,
                transfe_flg,
            )
        )

        row = cur.fetchone()

        if row:
            return row[0]

        return None

    finally:
        conn.close()


# ============================================================
# Find SERNO : Other
# ============================================================

def get_serno_other(
    htnm,
    order_fy,
    order_mm,
    order_serno,
    delivery,
    transfe_flg
):
    conn = get_connection()

    sql = """
        SELECT DISTINCT
            HTSTORAGE.SERNO
        FROM TYKSFLIB.HTSTORAGE
        INNER JOIN TYKSFLIB.HTSTORADTL
            ON HTSTORAGE.SERNO = HTSTORADTL.SERNO
        WHERE
            HTSTORAGE.HTNM = ?
            AND HTSTORAGE.ORDERFY = ?
            AND HTSTORAGE.ORDERMM = ?
            AND HTSTORAGE.ORDERSERNO = ?
            AND HTSTORAGE.DELIVERY = ?
            AND HTSTORADTL.TRANSFEFLG = ?
    """

    try:
        cur = conn.cursor()

        cur.execute(
            sql,
            (
                htnm,
                order_fy,
                order_mm,
                order_serno,
                delivery,
                transfe_flg,
            )
        )

        row = cur.fetchone()

        if row:
            return row[0]

        return None

    finally:
        conn.close()


# ============================================================
# DELETE HT0130
# ============================================================

def delete_ht0130(htnm, partner_code, selected):

    conn = get_connection()

    try:
        # ====================================================
        # ACC / U-Cera
        # ====================================================

        if partner_code in (11, 12):

            slip_no = selected.get("slipNo")
            delivery = selected.get("delivery")
            transfe_flg = selected.get("transfeFlg")

            if slip_no is None:
                return {
                    "success": False
                }

            serno = get_serno_acc_ucera(
                htnm,
                slip_no,
                delivery,
                partner_code,
                transfe_flg
            )

        # ====================================================
        # Other
        # ====================================================

        else:

            order_fy = selected.get("orderFy")
            order_mm = selected.get("orderMm")
            order_serno = selected.get("orderSerNo")
            delivery = selected.get("delivery")
            transfe_flg = selected.get("transfeFlg")

            serno = get_serno_other(
                htnm,
                order_fy,
                order_mm,
                order_serno,
                delivery,
                transfe_flg
            )

        # ====================================================
        # SERNO not found
        # ====================================================

        if serno is None:
            return {
                "success": False
            }

        print("HT0130 DELETE SERNO =", serno)

        # ====================================================
        # Delete detail
        # ====================================================

        cur = conn.cursor()

        delete_sql = """
            DELETE FROM TYKSFLIB.HTSTORADTL
            WHERE SERNO = ?
        """

        cur.execute(
            delete_sql,
            (serno,)
        )

        conn.commit()

        return {
            "success": True
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()