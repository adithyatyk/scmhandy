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
from .ht0100 import (
    transfer_data as ht0100_transfer,
    check_delete_data as ht0100_check_delete_data,
    delete_temp_data as ht0100_delete_temp_data
)
from .ht0410 import insert_stocktak
from .ht0410 import detail_list as get_detail_list
from .ht0410 import delete_stocktak
from .ht0410 import check_delete_stocktak
from .ht3100 import (
    transfer_data as ht3100_transfer,
    delete_ht3110_temp_data as ht3100_delete_temp_data
)
from .ht0110 import (
    check_untransferred_exists,
    check_slip_no_exists,
    insert_slip_no
)
from .ht0120 import (
    get_storage_count,
    check_qr_exists,
    get_first_storage_item,
    register_qr
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
                "param": "確認用紙"
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

        result = check_delete_stocktak(
            worker_code,
            warehouse_code,
            qr_code,
            taciaiflg
        )

        return JsonResponse(result)

    else:
        return JsonResponse({
            "success": False,
            "code": "E229",
            "message": f"Unknown mode: {mode}"
        })
@csrf_exempt
def delete_qr(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        worker_code = data.get("code", "").strip()
        warehouse_code = data.get("warehouseCode", "").strip()
        qr_code = data.get("qrCode", "").strip()
        inventory_flag = data.get("inventoryFlag", "").strip()

        taciaiflg = "0" if inventory_flag == "完成品" else "1"

        result = delete_stocktak(
            worker_code,
            warehouse_code,
            qr_code,
            taciaiflg,
            inventory_flag
        )

        return JsonResponse(result)

    except Exception as e:

        print("Delete QR Error:", e)

        return JsonResponse({
            "success": False,
            "code": "E229",
            "message": str(e)
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
def ht0100_check_delete(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        htnm = str(data.get("code", "")).strip()

        result = ht0100_check_delete_data(htnm)

        return JsonResponse(result)

    except Exception:

        traceback.print_exc()

        return JsonResponse({
            "success": False,
            "messageCode": "E229"
        })
@csrf_exempt
def ht0100_delete_temp(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        htnm = str(data.get("code", "")).strip()
        confirm = data.get("confirm", False)

        result = ht0100_delete_temp_data(
            htnm,
            confirm
        )

        return JsonResponse(result)

    except Exception:

        traceback.print_exc()

        return JsonResponse({
            "success": False,
            "messageCode": "E229"
        })
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
@csrf_exempt
def ht0110_check_untransferred(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        htnm = str(data.get("code", "")).strip()
        partner_code = str(data.get("partnerCode", "")).strip()

        result = check_untransferred_exists(
            htnm,
            partner_code
        )

        return JsonResponse(result)

    except Exception as e:

        print("HT0110 Check Error:", e)

        return JsonResponse({
            "success": False,
            "messageCode": "E102"
        })
@csrf_exempt
def ht0110_execute(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        htnm = data.get("code", "")
        partner_code = str(data.get("partnerCode", "")).strip()
        delivery_date = str(data.get("deliveryDate", "")).strip()
        slip_numbers = data.get("slipNumbers", [])

        # -----------------------------------------------
        # Number list check
        # -----------------------------------------------

        label = (
            "注文番号"
            if partner_code == "0"
            else "伝票№"
        )

        if not slip_numbers:

            return JsonResponse({
                "success": False,
                "messageCode": "E211",
                "param": label
            })

        # -----------------------------------------------
        # Delivery date check
        # -----------------------------------------------

        if partner_code == "11":

            if not delivery_date:

                return JsonResponse({
                    "success": False,
                    "messageCode": "E211",
                    "param": "納品日"
                })

            date_text = delivery_date.replace("/", "")

            if (
                len(date_text) != 8
                or not date_text.isdigit()
            ):

                return JsonResponse({
                    "success": False,
                    "messageCode": "E211",
                    "param": "正しい日付"
                })

        # -----------------------------------------------
        # SQL01 / SQL02 / SQL03
        # -----------------------------------------------

        result = check_untransferred_exists(
            htnm,
            partner_code
        )

        if not result["success"]:

            if result.get("messageCode") == "E221":
                return JsonResponse({
                    "success": False,
                    "messageCode": "E221",
                    "param": "入庫"
                })

            return JsonResponse(result)

        # -----------------------------------------------
        # Check each number already registered
        # -----------------------------------------------

        for slip_no in slip_numbers:

            result = check_slip_no_exists(
                slip_no,
                partner_code,
                htnm,
                delivery_date
            )

            if not result["success"]:
                return JsonResponse(result)

            if result.get("exists"):

                return JsonResponse({
                    "success": False,
                    "messageCode": "E211",
                    "param": label
                })

        # -----------------------------------------------
        # INSERT HTSTORAGE
        # -----------------------------------------------

        result = insert_slip_no(
            htnm,
            delivery_date,
            slip_numbers,
            partner_code
        )

        if not result["success"]:
            return JsonResponse(result)

        return JsonResponse({
            "success": True,
            "messageCode": "I201"
        })

    except Exception:

        traceback.print_exc()

        return JsonResponse({
            "success": False,
            "messageCode": "E102"
        })        
@csrf_exempt
def ht0120_count(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        htnm = str(
            data.get("code", "")
        ).strip()

        count = get_storage_count(htnm)

        return JsonResponse({
            "success": True,
            "count": count
        })

    except Exception as e:

        print("HT0120 Count Error:", e)

        return JsonResponse({
            "success": False,
            "messageCode": "E102"
        })
@csrf_exempt
def ht0120_scan(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        }, status=405)

    try:

        data = json.loads(request.body or "{}")

        htnm = str(
            data.get("code", "")
        ).strip()

        qr_code = str(
            data.get("qrCode", "")
        ).strip()

        # =====================================================
        # QR BLANK CHECK
        # =====================================================

        if not qr_code:

            return JsonResponse({
                "success": False,
                "messageCode": "E211",
                "param": "QR"
            })

        # =====================================================
        # FIRST CHARACTER CHECK
        # G OR F ONLY
        # =====================================================

        if qr_code[0] not in ["G", "F"]:

            return JsonResponse({
                "success": False,
                "messageCode": "E220",
                "param": "受入"
            })

        # =====================================================
        # SQL02
        # CHECK QR ALREADY REGISTERED
        # =====================================================

        count = check_qr_exists(qr_code)

        print("HT0120 SQL02 QR =", qr_code)
        print("HT0120 SQL02 COUNT =", count)

        if count > 0:

            return JsonResponse({
                "success": False,
                "messageCode": "E214"
            })

        # =====================================================
        # REGISTER QR
        # =====================================================

        result = register_qr(
            qr_code,
            htnm
        )

        return JsonResponse(result)

    except Exception as e:

        print("HT0120 Scan Error:", e)

        return JsonResponse({
            "success": False,
            "messageCode": "E102"
        })