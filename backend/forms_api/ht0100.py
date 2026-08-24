import jpype
import traceback
from datetime import datetime
from .connection import get_connection


def transfer_data(htnm, confirm=False):

    conn = None
    cursor = None
    cs = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # ---------------------------------------
        # SQL10 : Check Data
        # ---------------------------------------
        cursor.execute("""
            SELECT COUNT(*)
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
        """, (htnm,))

        count = cursor.fetchone()[0]

        print("COUNT =", count)

        if count == 0:
            return {
                "success": False,
                "messageCode": "E215"
            }

        # Ask confirmation
        if not confirm:
            return {
                "success": False,
                "messageCode": "Q201"
            }

        # ---------------------------------------
        # SQL01 : Get Header Information
        # ---------------------------------------
        cursor.execute("""
            SELECT
                SERNO,
                HTNM
            FROM TYKSFLIB.HTSTORAGE
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

        # Current scan datetime
        now = datetime.now()

        # Stored procedure IN_DATETIME : YYYYMMDDHHMMSS
        datetime_value = now.strftime("%Y%m%d%H%M%S")

        # XML scanDate : YYYY/MM/DD HH:MM:SS
        scan_date = now.strftime("%Y/%m/%d %H:%M:%S")

        # ---------------------------------------
        # Build XML from HTSTORAGE
        # ---------------------------------------

        cursor.execute("""
            SELECT
                ORDERFY,
                ORDERMM,
                ORDERSERNO,
                ROWNO,
                PARTNERCD,
                ITEMCD,
                MATERIAL,
                SYMBOL,
                QTY,
                SLIPNO,
                DELIVERY,
                SUPPLIERCD
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
            ORDER BY ROWNO
        """, (htnm,))

        rows = cursor.fetchall()

        xml_data = "<root>"

        for r in rows:

            xml_data += f"""
        <data>
            <orderFy>{r[0]}</orderFy>
            <orderMm>{r[1]}</orderMm>
            <orderSerNo>{r[2]}</orderSerNo>
            <rowNo>{r[3]}</rowNo>
            <partnerCd>{r[4]}</partnerCd>
            <itemCd>{r[5]}</itemCd>
            <material>{str(r[6]).strip()}</material>
            <symbol>{str(r[7]).strip()}</symbol>
            <qty>{r[8]}</qty>
            <slipNo>{r[9]}</slipNo>
            <shippingDate>{r[10]}</shippingDate>
            <confirmSerNo>0</confirmSerNo>
            <lot>0</lot>
            <destinationCd>0</destinationCd>
            <confirmRowNo>0</confirmRowNo>
            <scanDate>{scan_date}</scanDate>
        </data>
        """

        xml_data += "</root>"

        print("===================================")
        print(xml_data)
        # ---------------------------------------
        # Stored Procedure
        # ---------------------------------------
        jconn = conn.jconn

        cs = jconn.prepareCall(
            "{CALL TYKSFLIB.spAddHtTake(?,?,?,?,?)}"
        )

        cs.setInt(1, empno)
        cs.setString(2, pc)
        cs.setString(3, datetime_value)
        cs.setString(4, xml_data)

        Types = jpype.JClass("java.sql.Types")

        cs.registerOutParameter(
            jpype.JInt(5),
            jpype.JInt(Types.CHAR)
        )

        cs.execute()

        out_cd = (cs.getString(5) or "").strip()

        print("OUT_CD =", out_cd)

        if not out_cd.startswith("I"):
            conn.rollback()
            return {
                "success": False,
                "messageCode": out_cd
            }

        conn.commit()

        # ---------------------------------------
        # Delete HTSTORAGE
        # ---------------------------------------
        cursor.execute("""
            DELETE
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
        """, (htnm,))

        print("DELETE COUNT =", cursor.rowcount)

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
            "messageCode": "E103"
        }

    finally:
        if cs:
            cs.close()

        if cursor:
            cursor.close()

        if conn:
            conn.close() 
def check_delete_data(htnm):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # ---------------------------------------
        # SQL10 : Check Data
        # ---------------------------------------
        cursor.execute("""
            SELECT COUNT(*)
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
        """, (htnm,))

        count = cursor.fetchone()[0]

        print("===================================")
        print("HT0100 DELETE CHECK")
        print("SQL10 : SELECT COUNT(*)")
        print("HTNM =", htnm)
        print("COUNT =", count)
        print("===================================")

        # No data
        if count == 0:
            return {
                "success": False,
                "messageCode": "E215"
            }

        # Data exists -> ask Q204
        return {
            "success": True,
            "messageCode": "Q204"
        }

    except Exception:

        traceback.print_exc()

        return {
            "success": False,
            "messageCode": "E229"
        }

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
def delete_temp_data(htnm, confirm=False):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # ---------------------------------------
        # SQL10 : Check Data
        # ---------------------------------------
        cursor.execute("""
            SELECT COUNT(*)
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
        """, (htnm,))

        count = cursor.fetchone()[0]

        print("===================================")
        print("HT0100 DELETE")
        print("SQL10 : SELECT COUNT(*)")
        print("HTNM =", htnm)
        print("COUNT =", count)
        print("===================================")

        if count == 0:
            return {
                "success": False,
                "messageCode": "E215"
            }

        # ---------------------------------------
        # Q204 confirmation
        # ---------------------------------------
        if not confirm:
            return {
                "success": True,
                "messageCode": "Q204"
            }

        # ---------------------------------------
        # SQL11 : DELETE HTSTORAGE
        # ---------------------------------------
        print("===================================")
        print("HT0100 DELETE SQL11")
        print("""
DELETE FROM TYKSFLIB.HTSTORAGE
WHERE HTNM = ?
        """)
        print("HTNM =", htnm)

        cursor.execute("""
            DELETE
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
        """, (htnm,))

        delete_count = cursor.rowcount

        print("DELETE COUNT =", delete_count)

        conn.commit()

        return {
            "success": True,
            "messageCode": "I202"
        }

    except Exception:

        if conn:
            conn.rollback()

        traceback.print_exc()

        return {
            "success": False,
            "messageCode": "E229"
        }

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()