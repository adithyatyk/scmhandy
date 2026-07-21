import jpype
import traceback
from .as400 import get_connection

def transfer_data(htnm):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        empno = 999992
        pc = "SCM-HT1"
        datetime = "20190212094339"

        xml_data = """
        <root>
            ...
        </root>
        """

        # --------------------------
        # Call Stored Procedure
        # --------------------------
        jconn = conn.jconn

        cs = jconn.prepareCall("{CALL TYKSFLIB.spAddHtTake(?,?,?,?,?)}")

        cs.setInt(1, empno)
        cs.setString(2, pc)
        cs.setString(3, datetime)
        cs.setString(4, xml_data)

        Types = jpype.JClass("java.sql.Types")
        cs.registerOutParameter(
            jpype.JInt(5),
            jpype.JInt(Types.CHAR)
        )

        cs.execute()

        out_cd = cs.getString(5)

        print("OUT_CD =", out_cd)

        conn.commit()

        # If procedure failed, return immediately
        if out_cd != "1201":
            return {
                "success": False,
                "messageCode": out_cd
            }

        # --------------------------
        # SQL10
        # --------------------------
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
                "messageCode": "1215"
            }

        # --------------------------
        # SQL11
        # --------------------------
        cursor.execute("""
            DELETE
            FROM TYKSFLIB.HTSTORAGE
            WHERE HTNM = ?
        """, (htnm,))

        conn.commit()

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

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()