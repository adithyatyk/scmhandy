import jpype
import traceback
from .as400 import get_connection

def transfer_data(htnm):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        print(type(conn))
        print(hasattr(conn, "jconn"))
        cursor = conn.cursor()

        print("HTNM =", htnm)

        empno = 999992
        pc = "SCM-HT1"
        datetime = "20190212094339"

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
        <scanDate>2019/02/08 15:10:33</scanDate>
        </data>
        </root>
        """
        jconn = conn.jconn

        cs = jconn.prepareCall("{CALL TYKSFLIB.spAddHtTake(?,?,?,?,?)}")

        cs.setInt(1, empno)
        cs.setString(2, pc)
        cs.setString(3, datetime)

        cs.setString(4, xml_data)

        Types = jpype.JClass("java.sql.Types")
        JInt = jpype.JInt

        cs.registerOutParameter(JInt(5), JInt(Types.CHAR))

        cs.execute()

        out_cd = cs.getString(5)
        print("OUT_CD =", out_cd)

        conn.commit()
        
        print("Procedure executed successfully")

        # SQL10
        cursor.execute("""
            SELECT COUNT(*)
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
        """, (htnm,))

        count = cursor.fetchone()[0]

        print("HTSTORAGE count =", count)

        if count == 0:
            return {
                "success": False,
                "messageCode": "1215"
            }

        # SQL11
        try:
            cursor.execute("""
                DELETE FROM TYKSFLIB.HTSTORAGE
                WHERE HTNM = ?
            """, (htnm,))

            conn.commit()

        except Exception as e:
            print("Delete error:", e)

            return {
                "success": False,
                "messageCode": "E104"
            }

        return {
            "success": True,
            "messageCode": "1201"
        }

    except Exception:
        if conn:
            conn.rollback()

        traceback.print_exc()

        return {
            "success": False,
            "messageCode": "E103"
        }

        return {
            "success": False,
            "messageCode": "E103"
        }

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()