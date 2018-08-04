from django.conf.urls import url

from . import views

app_name='fcards'

urlpatterns = [

    url(r"^upload_txt_file/$", views.upload_file, name="upload_txt_file"),
]
