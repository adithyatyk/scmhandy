from django.urls import path
from .ht0011 import validate_password
from .ht_views import (
    form_data,
    worker_info,
    check_delete_temp,
    delete_temp,
    warehouse_list,
    read_count,
    serial_no
)
from .ht_views import scan_qr,transfer,detail_list
urlpatterns = [

    path(
        "form/",
        form_data
    ),

    path(
        "password/",
        validate_password
    ),
    path(
        "worker-info/", 
        worker_info
    ),

    path(
        "ht0400/check-delete/",
        check_delete_temp
    ),

    path(
        "ht0400/delete-temp/",
        delete_temp
    ),

    path(
        "ht0410/warehouse/",
        warehouse_list
    ),

    path(
        "ht0410/count/",
        read_count
    ),

    path(
        "ht0410/serial/", 
        serial_no
    ),

    path(
        "ht0410/scan/",
        scan_qr
    ),
 
    path(
        "ht0100/transfer/",
        transfer
    ),

    path(
        "ht0410/list/",
        detail_list
    )
    
]


