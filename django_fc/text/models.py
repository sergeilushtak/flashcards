from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class MyTextFilesModel (models.Model):
    user = models.ForeignKey(User, related_name="text_files", on_delete=models.CASCADE)
    file_name = models.CharField (max_length=32)
