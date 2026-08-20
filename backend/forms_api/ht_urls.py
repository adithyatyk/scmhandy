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
from .ht_views import (
    scan_qr,
    delete_qr,
    transfer,
    detail_list
)
from .ht_views import (ht3100_check_transfer,ht3100_delete)
from .ht_views import (ht3100_check_transfer,ht3100_delete,ht0110_check_untransferred)
urlpatterns = [

    path("form/",form_data),

    path("password/",validate_password),

    path("worker-info/",worker_info),

    path("ht0400/check-delete/",check_delete_temp),

    path("ht0400/delete-temp/",delete_temp),

    path("ht0410/warehouse/",warehouse_list),

    path("ht0410/count/",read_count),

    path("ht0410/serial/",serial_no),

    path("ht0410/scan/",scan_qr),

    path("ht0410/delete/",delete_qr),
 
    path("ht0100/transfer/",transfer),

    path("ht0410/list/",detail_list),

    path("ht3100/check-transfer/",ht3100_check_transfer),
    
    path("ht3100/delete/", ht3100_delete),

    path("ht0110/check-untransferred/", ht0110_check_untransferred),
    
]


