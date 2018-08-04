# Generated by Django 2.0.5 on 2018-07-18 16:07

from django.db import migrations, models
import fc_engine.voc_db_entry


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VocEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=20)),
                ('lemma_ID', models.CharField(max_length=50)),
                ('lft_lemma', models.CharField(max_length=50)),
                ('correct_answer', models.CharField(max_length=50)),
                ('rgt_lemma', models.CharField(max_length=50)),
                ('cits', models.CharField(max_length=1000)),
                ('ctxs', models.CharField(max_length=1000)),
                ('times_asked', models.CharField(max_length=20)),
            ],
            bases=(models.Model, fc_engine.voc_db_entry.VocDBEntry),
        ),
    ]
