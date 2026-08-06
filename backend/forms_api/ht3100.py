import jpype
import traceback
from .connection import get_connection


def transfer_data(htnm, inventory_flag, confirm=False):

    conn = None
    cursor = None
    cs = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # ---------------------------------------
        # SQL12 / SQL13 : Check Data
        # ---------------------------------------

        if inventory_flag == "外注品その他処理":

            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTREJECT
                WHERE HTNM = ?
                  AND PROCESSFLG <> 5
                  AND TRANSFEFLG = ''
            """, (htnm,))

        else:

            cursor.execute("""
                SELECT COUNT(*)
                FROM TYKSFLIB.HTREJECT
                WHERE HTNM = ?
                  AND PROCESSFLG = 5
                  AND TRANSFEFLG = ''
            """, (htnm,))

        count = cursor.fetchone()[0]

        print("COUNT =", count)

        if count == 0:
            return {
                "success": False,
                "messageCode": "E215"
            }

        # ---------------------------------------
        # Confirmation
        # ---------------------------------------

        if not confirm:

            param = "外注品その他" if inventory_flag == "外注品その他処理" else "出荷取消"

            return {
                "success": False,
                "messageCode": "Q201",
                "param": param
            }

        # ---------------------------------------
        # Header Information
        # ---------------------------------------

        cursor.execute("""
            SELECT
                SERNO,
                HTNM,
                SCANDATE
            FROM TYKSFLIB.HTREJECT
            WHERE HTNM = ?
            FETCH FIRST 1 ROW ONLY
        """, (htnm,))

        row = cursor.fetchone()

        if row is None:
            return {
                "success": False,
                "messageCode": "E215"
            }

        empno = int(row[0])
        pc = str(row[1]).strip()
        scan_date = str(row[2]).strip()
        datetime = scan_date[:14]

        print("SERNO    =", empno)
        print("PC       =", pc)
        print("DATETIME =", datetime)

        # ---------------------------------------
        # Detail Information
        # ---------------------------------------

        if inventory_flag == "外注品その他処理":

            cursor.execute("""
                SELECT
                    PROCESSFLG,
                    PARTNERCD,
                    CONFIRMNO,
                    SUPPLIERCD,
                    ROWNO,
                    ITEMCD,
                    MATERIAL,
                    SYMBOL,
                    QTY,
                    SCANDATE
                FROM TYKSFLIB.HTREJECT
                WHERE HTNM = ?
                  AND PROCESSFLG <> 5
                  AND TRANSFEFLG = ''
                ORDER BY ROWNO
            """, (htnm,))

        else:

            cursor.execute("""
                SELECT
                    PROCESSFLG,
                    PARTNERCD,
                    CONFIRMNO,
                    SUPPLIERCD,
                    ROWNO,
                    ITEMCD,
                    MATERIAL,
                    SYMBOL,
                    QTY,
                    SCANDATE
                FROM TYKSFLIB.HTREJECT
                WHERE HTNM = ?
                  AND PROCESSFLG = 5
                  AND TRANSFEFLG = ''
                ORDER BY ROWNO
            """, (htnm,))

        rows = cursor.fetchall()

        # ---------------------------------------
        # Build XML
        # ---------------------------------------

        # ---------------------------------------
# Build XML
# ---------------------------------------

        xml_data = "<root>"

        for r in rows:

            lot = "" if r[3] is None else str(r[3]).strip()

            xml_data += f"""
            <data>
                <flg>{r[0]}</flg>
                <partnerCd>{r[1]}</partnerCd>
                <confirmSerNo>{r[2]}</confirmSerNo>
                <lot>{lot}</lot>
                <rowNo>{r[4]}</rowNo>
                <itemCd>{r[5]}</itemCd>
                <material>{str(r[6]).strip()}</material>
                <symbol>{str(r[7]).strip()}</symbol>
                <qty>{r[8]}</qty>
                <scanDate>{str(r[9]).strip()[:14]}</scanDate>
            </data>
            """

        xml_data += "</root>"

        print("================ XML ================")
        print(xml_data)

        jconn = conn.jconn

        # ---------------------------------------
        # Stored Procedure
        # ---------------------------------------
        print("inventory_flag =", inventory_flag)
        if inventory_flag == "外注品その他処理":

            cs = jconn.prepareCall(
                "{CALL TYKSFLIB.spAddHtReject(?,?,?,?,?)}"
            )

        else:

            cs = jconn.prepareCall(
                "{CALL TYKSFLIB.spDelHtLeave(?,?,?,?,?)}"
            )

        cs.setInt(1, empno)
        cs.setString(2, pc)
        cs.setString(3, datetime)
        cs.setString(4, xml_data)

        Types = jpype.JClass("java.sql.Types")
        JInt = jpype.JInt

        cs.registerOutParameter(
            JInt(5),
            JInt(Types.CHAR)
        )
        print("===== STORED PROCEDURE PARAM =====")
        print("EMP =", empno)
        print("PC =", pc)
        print("DATE =", datetime)
        print("XML =", xml_data)
        cs.execute()

        out_cd = (cs.getString(5) or "").strip()

        print("OUT_CD =", out_cd)

        # ---------------------------------------
        # Stored Procedure Error
        # ---------------------------------------

        if out_cd == "E002":

            conn.rollback()

            return {
                "success": False,
                "messageCode": "E103"
            }

        if out_cd != "I001":

            conn.rollback()

            if inventory_flag == "外注品その他処理":
                param = "外注品その他削除中に"
            else:
                param = "出荷取消削除中に"

            return {
                "success": False,
                "messageCode": "E206",
                "param": param
            }

        # ---------------------------------------
        # SQL14 / SQL15
        # Update Transfer Flag
        # ---------------------------------------

        if inventory_flag == "外注品その他処理":

            cursor.execute("""
                UPDATE TYKSFLIB.HTREJECT
                   SET TRANSFEFLG = '1'
                 WHERE HTNM = ?
                   AND PROCESSFLG <> 5
                   AND TRANSFEFLG = ''
            """, (htnm,))

        else:

            cursor.execute("""
                UPDATE TYKSFLIB.HTREJECT
                   SET TRANSFEFLG = '1'
                 WHERE HTNM = ?
                   AND PROCESSFLG = 5
                   AND TRANSFEFLG = ''
            """, (htnm,))

        print("UPDATE COUNT =", cursor.rowcount)

        conn.commit()

        if inventory_flag == "外注品その他処理":
            message = "I201"
        else:
            message = "I202"

        return {
            "success": True,
            "messageCode": message
        }

    except Exception:

        if conn:
            conn.rollback()

        traceback.print_exc()

        return {
            "success": False,
            "messageCode": "E103"
        }

    finally:

        if cs:
            cs.close()

        if cursor:
            cursor.close()

        if conn:
            conn.close()