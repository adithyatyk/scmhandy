from .as400 import get_connection


def _default_worker_query():
    return """
        SELECT CD, NM
        FROM TYKSFLIB.MSTAFF
        WHERE SYSTEM3='1'   
        AND DELFLG = '' 
        ORDER BY CD
    """.strip()

    
def fetch_staff_rows():

    
    try:
        return _fetch_staff()

    except Exception as exc:
        return [], "system", str(exc)


def _fetch_staff():

    conn = None

    try:
        
        conn = get_connection()

        cursor = conn.cursor()
        
        cursor.execute(_default_worker_query())

        rows = cursor.fetchall()
        
        if not rows:
            return [], "as400-jdbc", "No data available"

        staff = [
            {
                "cd": str(row[0]).strip(),
                "nm": str(row[1]).strip()
            }
            for row in rows
        ]

        return staff, "as400-jdbc", None

    except Exception as exc:
        return [], "as400-jdbc", str(exc)

    finally:
        if conn:
            conn.close()
               