from django.conf.urls import url

from . import views

app_name='text'

urlpatterns = [
    url(r"^generate_src_file/", views.generate_src_file, name="generate_src_file"),
    url(r"^download_source_file/(?P<file_name>[^\"*]*)", views.download_source_file, name="download_source_file"),
    url(r"^work_with_text/(?P<file_name>[^\"*]*)", views.work_with_text, name="work_with_text"),
    url(r"^delete_file/(?P<file_name>[^\"*]+)/", views.delete_file, name="delete_file"),
    url(r"^save_file/(?P<file_name>[^\"*]+)/", views.save_file, name="save_file"),
]
