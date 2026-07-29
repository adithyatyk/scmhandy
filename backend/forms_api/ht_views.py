from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .as400 import get_connection
from .ht0010 import fetch_staff_rows
from .ht0400 import delete_temp_data
from .ht0410 import get_warehouse_list
from .ht0410 import get_read_count
from .ht0410 import get_serial_no
from .ht0410 import check_duplicate_qr
from .ht0100 import transfer_data
from .ht0410 import insert_stocktak
from .ht0410 import detail_list as get_detail_list
from .ht0410 import delete_stocktak
import json

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
        FROM TYKSFLIB.MSTAFF
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

        worker_code = data.get("code")
        inventory_flg = data.get("inventoryFlag")

        success = delete_temp_data(worker_code, inventory_flg)

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
        inventory_flag = data.get("inventoryFlag")

        taciaiflg = "0" if inventory_flag == "完成品" else "1"

        count = get_read_count(worker_code, warehouse_code, taciaiflg)

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
        inventory_flag = data.get("inventoryFlag")

        taciaiflg = "0" if inventory_flag == "完成品" else "1"

        serial = get_serial_no(worker_code, warehouse_code, taciaiflg)

        return JsonResponse({
            "success": True,
            "serial": serial
        })

    return JsonResponse({
        "success": False
    })        
@csrf_exempt
def scan_qr(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    data = json.loads(request.body or "{}")

    worker_code = data.get("code", "").strip()
    warehouse_code = data.get("warehouseCode", "").strip()
    qr_code = data.get("qrCode", "").strip()
    mode = data.get("mode", "").strip()
    inventory_flag = data.get("inventoryFlag", "").strip()
    taciaiflg = "0" if inventory_flag == "完成品" else "1"

    print("Before get_serial_no")
    next_serno = get_serial_no(worker_code, warehouse_code, taciaiflg) + 1
    print("After get_serial_no")

    print("Before duplicate check")
    result = check_duplicate_qr(qr_code, taciaiflg)
    print("After duplicate check", result)
    print("Mode =", mode)
    if mode == "入力":

        next_serno = get_serial_no(worker_code, warehouse_code, taciaiflg) + 1

        # Duplicate check
        result = check_duplicate_qr(qr_code, taciaiflg)

        if result["duplicate"]:
            return JsonResponse({
                "success": False,
                "code": "E214",
                "message": f"{worker_code}_{warehouse_code}_{next_serno}"
            })

        # First character validation
        if len(qr_code) == 0 or qr_code[0] not in ["T", "G", "F"]:
            return JsonResponse({
                "success": False,
                "code": "E220"
            })

        # Insert into HTSTOCKTAK
        result = insert_stocktak(
            worker_code,
            warehouse_code,
            qr_code,
            taciaiflg,
            inventory_flag
        )
    elif mode == "削除":
        result = delete_stocktak(
            worker_code,
            warehouse_code,
            qr_code,
            taciaiflg,
            inventory_flag
        )

        if not result["success"]:
            return JsonResponse({
                "success": False,
                "code": result.get("code", "E229"),
                "message": result.get("message", "")
            })

    return JsonResponse({
        "success": True
    })
@csrf_exempt
def transfer(request):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    body = json.loads(request.body)
    code = body.get("code")

    result = transfer_data(code)

    return JsonResponse(result)        
@csrf_exempt
def detail_list(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    data = json.loads(request.body or "{}")

    worker_code = data.get("code")
    warehouse_code = data.get("warehouseCode")
    inventory_flag = data.get("inventoryFlag")

    rows = get_detail_list(
        worker_code,
        warehouse_code,
        inventory_flag
    )

    return JsonResponse({
        "success": True,
        "rows": rows
    })