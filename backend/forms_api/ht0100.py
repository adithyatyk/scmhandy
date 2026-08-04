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

        # No data
        if count == 0:
            return {
                "success": False,
                "messageCode": "E215"
            }

        # Data exists -> ask confirmation
        if not confirm:
            return {
                "success": False,
                "messageCode": "Q204"
            }

        # ---------------------------------------
        # SQL01 : Get HT Information
        # ---------------------------------------
        cursor.execute("""
            SELECT SERNO,
                   HTNM,
                   SCANDATE
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
            FETCH FIRST 1 ROW ONLY
        """, (htnm,))

        row = cursor.fetchone()

        empno = int(row[0])
        pc = row[1].strip()

        scan_date = str(row[2]).strip()
        datetime = scan_date[:14]

        # ---------------------------------------
        # XML
        # ---------------------------------------
        xml_data = """
        <root>
        <data>
        <orderFy>0</orderFy>
        <orderMm>0</orderMm>
        <orderSerNo>0</orderSerNo>
        <rowNo>1</rowNo>
        <partnerCd>12</partnerCd>
        <itemCd>7260009</itemCd>
        <material>SH1</material>
        <symbol>YA-4B</symbol>
        <qty>252</qty>
        <slipNo>180344</slipNo>
        <shippingDate>20180622</shippingDate>
        <confirmSerNo>1</confirmSerNo>
        <lot>20190208</lot>
        <destinationCd>721885</destinationCd>
        <confirmRowNo>9</confirmRowNo>
        <scanDate>2019/02/08 15:10:33</scanDate>
        </data>
        <data>
        <orderFy>0</orderFy>
        <orderMm>0</orderMm>
        <orderSerNo>0</orderSerNo>
        <rowNo>2</rowNo>
        <partnerCd>12</partnerCd>
        <itemCd>7260010</itemCd>
        <material>SH1</material>
        <symbol>YA-4C</symbol>
        <qty>320</qty>
        <slipNo>180344</slipNo>
        <shippingDate>20180622</shippingDate>
        <confirmSerNo>1</confirmSerNo>
        <lot>20190208</lot>
        <destinationCd>721885</destinationCd>
        <confirmRowNo>9</confirmRowNo>
        <scanDate>2019/02/08 15:10:33</scanDate>
        </data>
        <data>
        <orderFy>0</orderFy>
        <orderMm>0</orderMm>
        <orderSerNo>0</orderSerNo>
        <rowNo>3</rowNo>
        <partnerCd>12</partnerCd>
        <itemCd>7260012</itemCd>
        <material>SH1</material>
        <symbol>YA-6</symbol>
        <qty>98</qty>
        <slipNo>180344</slipNo>
        <shippingDate>20180622</shippingDate>
        <confirmSerNo>1</confirmSerNo>
        <lot>20190208</lot>
        <destinationCd>721885</destinationCd>
        <confirmRowNo>9</confirmRowNo>
        <scanDate>2019/02/08 15:10:33</scanDate>
        </data>
        <data>
        <orderFy>0</orderFy>
        <orderMm>0</orderMm>
        <orderSerNo>0</orderSerNo>
        <rowNo>4</rowNo>
        <partnerCd>12</partnerCd>
        <itemCd>7260014</itemCd>
        <material>SH1</material>
        <symbol>YA-6C</symbol>
        <qty>120</qty>
        <slipNo>180344</slipNo>
        <shippingDate>20180622</shippingDate>
        <confirmSerNo>1</confirmSerNo>
        <lot>20190208</lot>
        <destinationCd>721885</destinationCd>
        <confirmRowNo>9</confirmRowNo>
        <scanDate>2019/02/08 15:10:33</scanDate>
        </data>
        <data>
        <orderFy>0</orderFy>
        <orderMm>0</orderMm>
        <orderSerNo>0</orderSerNo>
        <rowNo>5</rowNo>
        <partnerCd>12</partnerCd>
        <itemCd>7260015</itemCd>
        <material>SH1</material>
        <symbol>YA-6C-2</symbol>
        <qty>120</qty>
        <slipNo>180344</slipNo>
        <shippingDate>20180622</shippingDate>
        <confirmSerNo>1</confirmSerNo>
        <lot>20190208</lot>
        <destinationCd>721885</destinationCd>
        <confirmRowNo>9</confirmRowNo>
        <scanDate>2019/02/08 15:10:33</scanDate>
        </data>
        <data>
        <orderFy>0</orderFy>
        <orderMm>0</orderMm>
        <orderSerNo>0</orderSerNo>
        <rowNo>6</rowNo>
        <partnerCd>12</partnerCd>
        <itemCd>7260017</itemCd>
        <material>SH1</material>
        <symbol>YA-7Cｶｲ</symbol>
        <qty>210</qty>
        <slipNo>180344</slipNo>
        <shippingDate>20180622</shippingDate>
        <confirmSerNo>1</confirmSerNo>
        <lot>20190208</lot>
        <destinationCd>721885</destinationCd>
        <confirmRowNo>9</confirmRowNo>
        <scanDate>2019/02/08 15:10:33</scanDate>
        </data>
        </root>
        """

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

        cs.registerOutParameter(
            5,
            Types.CHAR
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
        # SQL11 : Delete
        # ---------------------------------------
        cursor.execute("""
            DELETE
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
        """, (htnm,))

        print("DELETE =", cursor.rowcount)

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