from django.urls import path
from .ht0011 import validate_password
from .ht_views import form_data, worker_info, delete_temp

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
        "ht0400/delete-temp/",
        delete_temp
    ),
    
]


