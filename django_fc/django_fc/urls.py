"""django_fc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django_fc import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url (r"^toggle_mode/", views.toggle_stt_session_mode, name = 'toggle_mode'),
    url (r"^edit_settings/", views.edit_settings, name = 'edit_settings'),
    url(r"^select_project/(?P<name>[^\"*]*)", views.select_project, name="select_project"),
    url(r"^new_project/", views.new_project, name="new_project"),
    url(r"^accounts/", include("accounts.urls", namespace="accounts")),
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(r"^test/$", views.TestPage.as_view(), name="test"),
    url(r"^thanks/$", views.ThanksPage.as_view(), name="thanks"),
    url(r"^$", views.HomePage.as_view(), name="home"),

    url(r"^fcards/", include ('fcards.urls', namespace='fcards')),
    url(r"^upload/", include ('upload.urls', namespace='upload')),
    url(r"^text/"  , include ('text.urls'  , namespace='text')),


]
