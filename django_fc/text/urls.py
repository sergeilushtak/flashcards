from django.conf.urls import url

from . import views

app_name='text'

urlpatterns = [
    url(r"^work_with_text/(?P<file_name>[a-zA-Z_\.]*)/", views.work_with_text, name="work_with_text"),
]
