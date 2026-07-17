from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .as400 import get_connection
import json

@csrf_exempt
def validate_password(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)

        emp_id = data.get("cd")
        password = data.get("password")

        conn = get_connection()
        cur = conn.cursor()

        sql = """
        SELECT NM, PW
        FROM TYKSFLIB.MSTAFF
        WHERE SYSTEM3='1'
        AND DELFLG=''
        AND CD=?
        AND PW=?
        """

        cur.execute(sql, [emp_id, password])
        row = cur.fetchone()

        cur.close()
        conn.close()

        if row:
            return JsonResponse({
                "success": True,
                "fullname": str(row[0]).strip()
            })

        return JsonResponse({
            "success": False,
            "message": "Invalid credentials"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })