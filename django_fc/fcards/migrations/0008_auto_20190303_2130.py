# Generated by Django 2.0.5 on 2019-03-03 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fcards', '0007_floatingwindowindex'),
    ]

    operations = [
        migrations.AddField(
            model_name='fcsettings',
            name='fw_lesson_size',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='fcsettings',
            name='fw_review_lesson_cnt',
            field=models.IntegerField(default=6),
        ),
    ]