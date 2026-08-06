from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .connection import get_connection
from .ht0010 import fetch_staff_rows
from .ht0400 import (
    delete_temp_data,
    get_temp_count
)
from .ht0410 import get_warehouse_list
from .ht0410 import get_read_count
from .ht0410 import get_serial_no
from .ht0410 import check_duplicate_qr
from .ht0100 import transfer_data as ht0100_transfer
from .ht0410 import insert_stocktak
from .ht0410 import detail_list as get_detail_list
from .ht0410 import delete_stocktak
from .ht3100 import (
    transfer_data as ht3100_transfer
)
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
def check_delete_temp(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    data = json.loads(request.body or "{}")

    worker_code = data.get("code")
    inventory_flg = data.get("inventoryFlag")

    count = get_temp_count(worker_code, inventory_flg)

    if count == 0:
        return JsonResponse({
            "success": True,
            "code": "I203"
        })

    return JsonResponse({
        "success": True,
        "code": "Q204"
    })

@csrf_exempt
def delete_temp(request):

    if request.method != "DELETE":
        return JsonResponse({"success": False}, status=405)

    data = json.loads(request.body or "{}")

    worker_code = data.get("code")
    inventory_flg = data.get("inventoryFlag")

    success = delete_temp_data(worker_code, inventory_flg)

    if success:
        return JsonResponse({
            "success": True,
            "code": "I202"
        })

    return JsonResponse({
        "success": False,
        "code": "E229"
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
    
    if mode == "入力":

        result = check_duplicate_qr(qr_code, taciaiflg)

        if result["duplicate"]:
            return JsonResponse({
                "success": False,
                "code": "E214"
            })

        if len(qr_code) == 0 or qr_code[0] not in ["T", "G", "F"]:
            return JsonResponse({
                "success": False,
                "code": "E220",
                "param": "確認用"
            })

        result = insert_stocktak(
            worker_code,
            warehouse_code,
            qr_code,
            taciaiflg,
            inventory_flag
        )

        if not result["success"]:
            return JsonResponse(result)

        return JsonResponse({
            "success": True
        })

    elif mode == "削除":

        result = delete_stocktak(
            worker_code,
            warehouse_code,
            qr_code,
            taciaiflg,
            inventory_flag
        )

        if not result["success"]:
            return JsonResponse(result)

        return JsonResponse({
            "success": True
        })

    else:
        return JsonResponse({
            "success": False,
            "code": "E229",
            "message": f"Unknown mode: {mode}"
        })
        
@csrf_exempt
def transfer(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    body = json.loads(request.body or "{}")

    code = body.get("code")
    confirm = body.get("confirm", False)

    result = ht0100_transfer(
        code,
        confirm
    )

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

@csrf_exempt
def ht3100_check_transfer(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        code = data.get("code")
        inventory_flag = data.get("inventoryFlag")
        confirm = data.get("confirm", False)

        result = ht3100_transfer(
            code,
            inventory_flag,
            confirm
        )

        return JsonResponse(result)

    except Exception as e:

        print("HT3100 Transfer Error:", e)

        return JsonResponse({
            "success": False,
            "messageCode": "E103"
        })
@csrf_exempt
def ht3100_delete(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        code = data.get("code")
        inventory_flag = data.get("inventoryFlag")
        confirm = data.get("confirm", False)

        result = ht3100_delete_temp_data(
            code,
            inventory_flag,
            confirm
        )

        return JsonResponse(result)

    except Exception as e:

        print("HT3100 Delete Error:", e)

        return JsonResponse({
            "success": False,
            "messageCode": "E206"
        })