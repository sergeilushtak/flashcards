from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from fcards.models import Project

# Create your models here.
class MyTextFilesModel (models.Model):
    user = models.ForeignKey(User, related_name="text_files", on_delete=models.CASCADE)
    project = models.ForeignKey (Project, related_name="text_files", on_delete=models.CASCADE, default=0)
    file_name = models.CharField (max_length=32)
    current = models.BooleanField (default = False)
