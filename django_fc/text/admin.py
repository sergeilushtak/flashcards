from django.contrib import admin

# Register your models here.
from text.models import MyTextFilesModel
from fcards.models import Project, Language

admin.site.register (MyTextFilesModel)
admin.site.register (Project)
admin.site.register (Language)
