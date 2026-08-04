import jpype
import traceback
from .as400 import get_connection


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
                "messageCode": "Q204"
            }

        # ---------------------------------------
        # SQL01 : Get Header Information
        # ---------------------------------------
        cursor.execute("""
            SELECT
                SERNO,
                HTNM,
                SCANDATE
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

        scan_date = str(row[2]).strip()
        datetime = scan_date[:14]

        print("SERNO    =", empno)
        print("PC       =", pc)
        print("DATETIME =", datetime)

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
                CONFIRMNO,
                LOT,
                SUPPLIERCD,
                CONFIRMROW,
                SCANDATE
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
    <confirmSerNo>{r[11]}</confirmSerNo>
    <lot>{r[12]}</lot>
    <destinationCd>{str(r[13]).strip()}</destinationCd>
    <confirmRowNo>{r[14]}</confirmRowNo>
    <scanDate>{str(r[15]).strip()}</scanDate>
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
        cs.setString(3, datetime)
        cs.setString(4, xml_data)

        Types = jpype.JClass("java.sql.Types")

        cs.registerOutParameter(5, Types.CHAR)

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