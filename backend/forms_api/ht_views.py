from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .as400 import get_connection
from .ht0010 import fetch_staff_rows
from .ht0400 import delete_temp_data
from .ht0410 import get_warehouse_list
from .ht0410 import get_read_count
from .ht0410 import validate_scan

@csrf_exempt
def form_data(request):

    if request.method == "OPTIONS":

        response = JsonResponse({}, status=204)

        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"

        return response


    if request.method == "GET":

        rows, source, error = fetch_staff_rows()

        # ERROR CASE
        if error:

            response = JsonResponse({

                "staff": [],
                "source": source,
                "error": error

            })


        # NO DATA CASE
        elif not rows:

            response = JsonResponse({

                "staff": [],
                "source": source,
                "message": "No data available"

            })


        # SUCCESS CASE
        else:

            response = JsonResponse({

                "staff": rows,
                "source": source

            })

        response["Access-Control-Allow-Origin"] = "*"

        return response


    if request.method == "POST":

        response = JsonResponse({

            "message": "F4-NEXT completed."

        })

        response["Access-Control-Allow-Origin"] = "*"

        return response


    response = JsonResponse({

        "error": "Method not allowed"

    }, status=405)

    response["Access-Control-Allow-Origin"] = "*"

    return response



@csrf_exempt
def submit_staff(request):

    if request.method == "OPTIONS":

        response = JsonResponse({}, status=204)

        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"

        return response


    if request.method == "POST":

        try:

            import json

            payload = json.loads(
                request.body or "{}"
            )

        except json.JSONDecodeError:

            response = JsonResponse({

                "error": "Invalid JSON body"

            }, status=400)

            response["Access-Control-Allow-Origin"] = "*"

            return response


        cd = payload.get(
            "cd", ""
        ).strip()

        nm = payload.get(
            "nm", ""
        ).strip()


        if not cd or not nm:

            response = JsonResponse({

                "error":
                "Please select a staff row."

            }, status=400)

            response["Access-Control-Allow-Origin"] = "*"

            return response


        response = JsonResponse({

            "message":
            f"Selected staff: {cd} - {nm}",

            "data": {

                "cd": cd,
                "nm": nm

            }

        })

        response["Access-Control-Allow-Origin"] = "*"

        return response


    response = JsonResponse({

        "error": "Method not allowed"

    }, status=405)

    response["Access-Control-Allow-Origin"] = "*"

    return response

@csrf_exempt
def worker_info(request):

    cd = request.GET.get("cd")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT NM, PW
        FROM ADITHYA1.MSTAFF
        WHERE SYSTEM3='1'
        AND DELFLG=''
        AND CD=?
    """, [cd])

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return JsonResponse({"success": False})

    return JsonResponse({
        "success": True,
        "nm": str(row[0]).strip(),
        "pw": str(row[1]).strip()
    })

import json

@csrf_exempt
def delete_temp(request):

    if request.method == "DELETE":

        data = json.loads(request.body or "{}")

        worker_code = data.get("workerCode")

        success = delete_temp_data(worker_code)

        return JsonResponse({
            "success": success
        })
        
@csrf_exempt
def warehouse_list(request):

    if request.method == "OPTIONS":

        response = JsonResponse({}, status=204)

        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"

        return response

    if request.method == "GET":

        rows = get_warehouse_list()

        response = JsonResponse({
            "success": len(rows) > 0,
            "rows": rows
        })

        response["Access-Control-Allow-Origin"] = "*"

        return response

    response = JsonResponse({
        "success": False,
        "message": "Method not allowed"
    }, status=405)

    response["Access-Control-Allow-Origin"] = "*"

    return response

@csrf_exempt
def read_count(request):

    if request.method == "POST":

        data = json.loads(request.body or "{}")

        worker_code = data.get("code")
        warehouse_code = data.get("warehouseCode")

        count = get_read_count(worker_code, warehouse_code)

        return JsonResponse({
            "success": True,
            "count": count
        })

    return JsonResponse({
        "success": False
    })    
@csrf_exempt
def serial_no(request):

    if request.method == "POST":

        data = json.loads(request.body or "{}")

        worker_code = data.get("code")
        warehouse_code = data.get("warehouseCode")

        serial = get_serial_no(worker_code, warehouse_code)

        return JsonResponse({
            "success": True,
            "serial": serial
        })

    return JsonResponse({
        "success": False
    })    
@csrf_exempt
def scan_qr(request):

    if request.method == "POST":

        data = json.loads(request.body or "{}")

        qr_code = data.get("qrCode", "").strip()
        mode = data.get("mode", "").strip()

        # Input mode only
        if mode == "入力":

            # 1. Duplicate check
            if check_duplicate_qr(qr_code):
                return JsonResponse({
                    "success": False,
                    "code": "E214"
                })

            # 2. First character check
            if len(qr_code) == 0 or qr_code[0] not in ["T", "G", "F"]:
                return JsonResponse({
                    "success": False,
                    "code": "E220"
                })

            # 3. Shipment check (later)
            # if not check_shipment(...):
            #     return JsonResponse({
            #         "success": False,
            #         "code": "E226"
            #     })

        return JsonResponse({
            "success": True
        })