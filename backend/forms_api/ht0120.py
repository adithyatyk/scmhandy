from .connection import get_connection


def get_storage_count(htnm):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT HTSTORAGE.SERNO
                FROM TYKSFLIB.HTSTORAGE
                INNER JOIN TYKSFLIB.HTSTORADTL
                    ON HTSTORAGE.SERNO = HTSTORADTL.SERNO
                WHERE HTSTORAGE.HTNM = ?
            ) AS T
        """ 

        params = [htnm]

        print("========================================")
        print("HT0120 SQL01")
        print("SQL =")
        print(sql)
        print("PARAMS =", params)
        print("HTNM =", htnm)
        print("========================================")

        cursor.execute(sql, params)

        row = cursor.fetchone()

        count = int(row[0]) if row else 0

        print("HT0120 SQL01 COUNT =", count)

        return count

    except Exception as e:
        print("HT0120 SQL01 ERROR:", e)
        raise

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
def check_qr_exists(qr_code):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM TYKSFLIB.HTSTORADTL
            WHERE QR = ?
        """, [qr_code])

        row = cursor.fetchone()

        count = int(row[0]) if row else 0
        
        print("HT0120 SQL03 QR =", qr_code)
        print("HT0120 SQL03 COUNT =", count)

        return count

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
def get_first_storage_item(
    htnm,
    partner_cd,
    product_cd,
    material,
    symbol,
    quantity
):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if int(partner_cd) == 11:
            partner_condition = "= 11"
        elif int(partner_cd) == 12:
            partner_condition = "= 12"
        else:
            partner_condition = "NOT IN (11, 12)"

        sql = f"""
            SELECT HTSTORAGE.SERNO
            FROM TYKSFLIB.HTSTORAGE
            INNER JOIN TYKSFLIB.HTSTORADTL
                ON HTSTORAGE.SERNO = HTSTORADTL.SERNO
            WHERE HTSTORAGE.HTNM = ?
            AND HTSTORAGE.PARTNERCD {partner_condition}
            AND (
                    HTSTORAGE.ITEMCD = ?
                    OR (
                        HTSTORAGE.MATERIAL = ?
                        AND HTSTORAGE.SYMBOL = ?
                    )
                )
            AND HTSTORADTL.QR = ''
            GROUP BY
                HTSTORAGE.SERNO,
                HTSTORAGE.QTY
            HAVING
                HTSTORAGE.QTY >= SUM(HTSTORADTL.TAKEQTY) + ?
            ORDER BY
                HTSTORAGE.QTY - SUM(HTSTORADTL.TAKEQTY) - ?,
                HTSTORAGE.SERNO
            FETCH FIRST 1 ROW ONLY
        """

        params = [
            htnm,
            int(product_cd),
            material,
            symbol,
            int(quantity),
            int(quantity)
        ]

        print("========================================")
        print(sql)
        print("SQL =")
        print("HT0120 SQL10 / SQL11 / SQL12")
        print("PARAMS =", params)
        print("========================================")

        cursor.execute(sql, params)

        row = cursor.fetchone()

        if not row:
            print("HT0120 SQL10 / SQL11 / SQL12: NO DATA")
            return None

        serno = int(row[0])

        print(
            "HT0120 SQL10 / SQL11 / SQL12 SERNO =",
            serno
        )

        return serno

    except Exception as e:

        print(
            "HT0120 SQL10 / SQL11 / SQL12 ERROR:",
            e
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
def insert_storage_detail(
    serno,
    qr_code,
    lot,
    take_qty,
    confirm_no,
    confirm_row
):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --------------------------------------------------
        # Get next DTLNO
        # --------------------------------------------------
        cursor.execute("""
            SELECT COALESCE(MAX(DTLNO), 0) + 1
            FROM TYKSFLIB.HTSTORADTL
            WHERE SERNO = ?
        """, [serno])

        row = cursor.fetchone()

        dtlno = int(row[0]) if row else 1

        # --------------------------------------------------
        # INSERT
        # --------------------------------------------------
        sql = """
            INSERT INTO TYKSFLIB.HTSTORADTL
            (
                SERNO,
                DTLNO,
                QR,
                SCANDATE,
                LOT,
                TAKEQTY,
                CONFIRMNO,
                CONFIRMROW,
                TRANSFEFLG
            )
            VALUES
            (
                ?,
                ?,
                ?,
                CAST(CURRENT_TIMESTAMP AS VARCHAR(26)),
                ?,
                ?,
                ?,
                ?,
                ''
            )
        """

        params = [
            serno,
            dtlno,
            qr_code,
            lot,
            take_qty,
            confirm_no,
            confirm_row
        ]

        print("========================================")
        print("HT0120 INSERT HTSTORADTL")
        print("SQL =")
        print(sql)
        print("PARAMS =", params)
        print("SERNO =", serno)
        print("DTLNO =", dtlno)
        print("QR =", qr_code)
        print("LOT =", lot)
        print("TAKEQTY =", take_qty)
        print("CONFIRMNO =", confirm_no)
        print("CONFIRMROW =", confirm_row)
        print("========================================")

        cursor.execute(sql, params)

        conn.commit()

        print("HT0120 INSERT SUCCESS")

        return {
            "success": True,
            "dtlno": dtlno
        }

    except Exception as e:

        if conn:
            conn.rollback()

        print("HT0120 INSERT ERROR:", e)

        return {
            "success": False,
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()            
def register_qr(qr_code, htnm, partner_code):
    conn = None
    cursor = None

    try:
        # =====================================================
        # QR BASIC VALIDATION
        # =====================================================

        qr_code = qr_code.strip()

        if not qr_code:
            return {
                "success": False,
                "messageCode": "E211",
                "param": "QR"
            }

        if qr_code[0] != "G" and qr_code[0] != "F":
            return {
                "success": False,
                "messageCode": "E220",
                "param": "受入"
            }


        # =====================================================
        # SQL03 - DUPLICATE CHECK
        # =====================================================

        try:
            duplicate_count = check_qr_exists(qr_code)

            if duplicate_count > 0:
                return {
                    "success": False,
                    "messageCode": "E214"
                }

        except Exception as e:
            print("HT0120 SQL03 ERROR:", e)

            return {
                "success": False,
                "messageCode": "E206",
                "param": "受入"
            }
        # =====================================================
        # QR PARSE
        # =====================================================

        fields = qr_code.strip().split(",")

        if len(fields) < 6:
            return {
                "success": False,
                "messageCode": "E220",
                "param": "受入"
            }

        conf_type = fields[0].strip()

        # =====================================================
        # HEADER
        # =====================================================

        try:
            partner_cd = int(fields[1])
            selected_partner_code = int(partner_code)

            print("========================================")
            print("HT0120 PARTNER VALIDATION")
            print("SELECTED PARTNER CODE =", selected_partner_code)
            print("QR PARTNER CODE =", partner_cd)
            print("========================================")

            # =================================================
            # CHECK SELECTED PARTNER VS QR PARTNER
            # =================================================

            if selected_partner_code == 0:

                # Other:
                # Do not restrict QR partner.
                print("HT0120 OTHER - QR PARTNER ACCEPTED")

            else:

                # ACC = 11
                # U-Cera = 12

                if partner_cd != selected_partner_code:

                    print("HT0120 PARTNER MISMATCH")

                    return {
                        "success": False,
                        "messageCode": "E220",
                        "param": "受入"
                    }

            print("HT0120 PARTNER VALIDATION PASSED")

            # =================================================
            # STORAGE PARTNER CONDITION
            # =================================================

            if partner_cd == 11:

                partner_condition = "HTSTORAGE.PARTNERCD = 11"

            elif partner_cd == 12:

                partner_condition = "HTSTORAGE.PARTNERCD = 12"

            else:

                partner_condition = "HTSTORAGE.PARTNERCD NOT IN (11, 12)"

            print(
                "HT0120 PARTNER CONDITION =",
                partner_condition
            )

            # =================================================
            # HEADER VALUES
            # =================================================

            lot = int(fields[2])
            confirm_no = int(fields[3])
            destinat_cd = int(fields[4])

            print("HT0120 HEADER PARSED")
            print("LOT =", lot)
            print("CONFIRMNO =", confirm_no)
            print("DESTINATCD =", destinat_cd)

        except (ValueError, TypeError, IndexError) as e:

            print("HT0120 HEADER PARSE ERROR =", e)

            return {
                "success": False,
                "messageCode": "E220",
                "param": "受入"
            }
        # =====================================================
        # DETAIL PARSE
        # =====================================================

        detail_fields = fields[5:]
        details = []

        if conf_type == "G":

            # =================================================
            # G TYPE
            #
            # Single item:
            # G,PARTNER,LOT,CONFIRMNO,ITEMCD,MATERIAL,SYMBOL,QTY
            #
            # Multiple items:
            # G,PARTNER,LOT,CONFIRMNO,DESTINATCD,
            # ITEMCD,MATERIAL,SYMBOL,QTY,
            # ITEMCD,MATERIAL,SYMBOL,QTY,...
            # =================================================

            # -------------------------------------------------
            # SINGLE ITEM G QR
            # Example:
            # G,11,20260821,78,4180001,NF7,LH123,10
            # -------------------------------------------------

            if len(fields) == 8:

                try:
                    item_cd = int(fields[4])
                    material = fields[5].strip()
                    symbol = fields[6].strip()
                    quantity = int(fields[7])

                except (ValueError, TypeError, IndexError) as e:

                    print("HT0120 SINGLE G PARSE ERROR =", e)

                    return {
                        "success": False,
                        "messageCode": "E220",
                        "param": "受入"
                    }

                details.append({
                    "item_cd": item_cd,
                    "material": material,
                    "symbol": symbol,
                    "quantity": quantity
                })

                print("========================================")
                print("HT0120 SINGLE G QR")
                print("ITEMCD =", item_cd)
                print("MATERIAL =", material)
                print("SYMBOL =", symbol)
                print("QTY =", quantity)
                print("========================================")

            # -------------------------------------------------
            # MULTIPLE ITEM G QR
            # Existing working format
            # -------------------------------------------------

            else:

                if len(detail_fields) == 0 or len(detail_fields) % 4 != 0:

                    return {
                        "success": False,
                        "messageCode": "E220",
                        "param": "受入"
                    }

                for i in range(0, len(detail_fields), 4):

                    try:
                        item_cd = int(detail_fields[i])
                        material = detail_fields[i + 1].strip()
                        symbol = detail_fields[i + 2].strip()
                        quantity = int(detail_fields[i + 3])

                    except (ValueError, TypeError, IndexError) as e:

                        print("HT0120 MULTI G PARSE ERROR =", e)

                        return {
                            "success": False,
                            "messageCode": "E220",
                            "param": "受入"
                        }

                    details.append({
                        "item_cd": item_cd,
                        "material": material,
                        "symbol": symbol,
                        "quantity": quantity
                    })

        elif conf_type == "F":

            if len(detail_fields) == 0 or len(detail_fields) % 7 != 0:
                return {
                    "success": False,
                    "messageCode": "E220",
                    "param": "受入"
                }

            for i in range(0, len(detail_fields), 7):

                try:
                    period = detail_fields[i].strip()
                    month = detail_fields[i + 1].strip()
                    serial8 = detail_fields[i + 2].strip()
                    item_cd = int(detail_fields[i + 3])
                    material = detail_fields[i + 4].strip()
                    symbol = detail_fields[i + 5].strip()
                    quantity = int(detail_fields[i + 6])
                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "messageCode": "E220",
                        "param": "受入"
                    }

                details.append({
                    "period": period,
                    "month": month,
                    "serial8": serial8,
                    "item_cd": item_cd,
                    "material": material,
                    "symbol": symbol,
                    "quantity": quantity
                })

        else:
            return {
                "success": False,
                "messageCode": "E220",
                "param": "受入"
            }

        # =====================================================
        # DATABASE CONNECTION
        # =====================================================

        conn = get_connection()
        cursor = conn.cursor()

        # =====================================================
        # PHASE 1
        # CHECK ALL DETAILS FIRST
        # DO NOT INSERT ANYTHING HERE
        # =====================================================

        matched_details = []

        for index, detail in enumerate(details, start=1):

            item_cd = detail["item_cd"]
            material = detail["material"]
            symbol = detail["symbol"]
            quantity = detail["quantity"]

            print("========================================")
            print("HT0120 CHECK DETAIL", index)
            print("ITEMCD =", item_cd)
            print("MATERIAL =", material)
            print("SYMBOL =", symbol)
            print("QTY =", quantity)
            print("========================================")

            # -------------------------------------------------
            # Find matching storage
            # -------------------------------------------------

            debug_sql = f"""
                SELECT
                    HTSTORAGE.SERNO,
                    HTSTORAGE.HTNM,
                    HTSTORAGE.PARTNERCD,
                    HTSTORAGE.ITEMCD,
                    HTSTORAGE.MATERIAL,
                    HTSTORAGE.SYMBOL,
                    HTSTORAGE.QTY
                FROM TYKSFLIB.HTSTORAGE
                WHERE HTSTORAGE.HTNM = ?
                AND {partner_condition}
                AND (
                        HTSTORAGE.ITEMCD = ?
                        OR (
                            HTSTORAGE.MATERIAL = ?
                            AND HTSTORAGE.SYMBOL = ?
                        )
                    )
            """

            debug_params = [
                htnm,
                int(item_cd),
                material,
                symbol
            ]

            print("========================================")
            print("HT0120 DEBUG HTSTORAGE")
            print("DEBUG PARAMS =", debug_params)
            print("========================================")

            cursor.execute(debug_sql, debug_params)

            debug_rows = cursor.fetchall()

            print("HT0120 DEBUG ROW COUNT =", len(debug_rows))

            for debug_row in debug_rows:
                print("HT0120 DEBUG ROW =", debug_row)

            print("========================================")

            # -------------------------------------------------
            # Find matching storage
            # -------------------------------------------------

            sql = f"""
                SELECT
                    HTSTORAGE.SERNO
                FROM TYKSFLIB.HTSTORAGE
                LEFT JOIN TYKSFLIB.HTSTORADTL
                    ON HTSTORAGE.SERNO = HTSTORADTL.SERNO
                WHERE HTSTORAGE.HTNM = ?
                AND {partner_condition}
                AND (
                        HTSTORAGE.ITEMCD = ?
                        OR (
                            HTSTORAGE.MATERIAL = ?
                            AND HTSTORAGE.SYMBOL = ?
                        )
                    )
                GROUP BY
                    HTSTORAGE.SERNO,
                    HTSTORAGE.QTY
                HAVING
                    HTSTORAGE.QTY >=
                    COALESCE(SUM(HTSTORADTL.TAKEQTY), 0) + ?
                ORDER BY
                    HTSTORAGE.QTY -
                    COALESCE(SUM(HTSTORADTL.TAKEQTY), 0) - ?,
                    HTSTORAGE.SERNO
                FETCH FIRST 1 ROW ONLY
            """

            params = [
                htnm,
                int(item_cd),
                material,
                symbol,
                int(quantity),
                int(quantity)
            ]

            print("HT0120 CHECK SQL")
            print(sql)
            print("PARAMS =", params)

            cursor.execute(sql, params)

            row = cursor.fetchone()

            # -------------------------------------------------
            # No matching storage
            # -------------------------------------------------

            if not row:

                print(
                    "HT0120 DETAIL",
                    index,
                    "NO STORAGE DATA"
                )

                # IMPORTANT:
                # Nothing has been inserted yet.
                # Therefore simply return E218.

                return {
                    "success": False,
                    "messageCode": "E218"
                }

            serno = int(row[0])

            print(
                "HT0120 DETAIL",
                index,
                "SERNO =",
                serno
            )

            # Save matched information
            matched_details.append({
                "index": index,
                "serno": serno,
                "quantity": quantity
            })

        # ============================================================
        # PHASE 2
        # ALL DETAILS ARE VALID
        # NOW INSERT
        # ============================================================

        print("========================================")
        print("HT0120 ALL DETAILS VALID")
        print("START INSERT")
        print("========================================")

        next_dtlno = {}

        for detail in matched_details:

            index = detail["index"]
            serno = detail["serno"]
            quantity = detail["quantity"]

            # --------------------------------------------------------
            # Get next DTLNO for this SERNO
            # --------------------------------------------------------

            if serno not in next_dtlno:

                cursor.execute("""
                    SELECT COALESCE(MAX(DTLNO), 0) + 1
                    FROM TYKSFLIB.HTSTORADTL
                    WHERE SERNO = ?
                """, [serno])

                row = cursor.fetchone()

                next_dtlno[serno] = int(row[0]) if row else 1

            dtlno = next_dtlno[serno]

            # Increment for next detail using same SERNO
            next_dtlno[serno] += 1

            # --------------------------------------------------------
            # INSERT
            # --------------------------------------------------------

            sql = """
                INSERT INTO TYKSFLIB.HTSTORADTL
                (
                    SERNO,
                    DTLNO,
                    QR,
                    SCANDATE,
                    LOT,
                    TAKEQTY,
                    CONFIRMNO,
                    CONFIRMROW,
                    TRANSFEFLG
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    CAST(CURRENT TIMESTAMP AS VARCHAR(26)),
                    ?,
                    ?,
                    ?,
                    ?,
                    ''
                )
            """

            params = [
                serno,
                dtlno,
                qr_code,
                lot,
                quantity,
                confirm_no,
                index
            ]

            print("========================================")
            print("HT0120 INSERT DETAIL", index)
            print("SERNO =", serno)
            print("DTLNO =", dtlno)
            print("QR =", qr_code)
            print("LOT =", lot)
            print("TAKEQTY =", quantity)
            print("CONFIRMNO =", confirm_no)
            print("CONFIRMROW =", index)
            print("========================================")

            cursor.execute(sql, params)

        # =====================================================
        # COMMIT ONLY AFTER ALL INSERTS SUCCEED
        # =====================================================

        conn.commit()

        print("========================================")
        print("HT0120 REGISTER SUCCESS")
        print("QR =", qr_code)
        print("DETAIL COUNT =", len(details))
        print("========================================")

        return {
            "success": True,
            "messageCode": "I201"
        }

    except Exception as e:

        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        print("HT0120 REGISTER ERROR =", e)

        return {
            "success": False,
            "messageCode": "E206",
            "param": "受入"
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