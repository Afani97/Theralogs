# Generated by Django 3.1.6 on 2021-02-10 20:26

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ("theralogs", "0001_squashed_0016_auto_20210204_1805"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="therapist",
            name="city",
        ),
        migrations.RemoveField(
            model_name="therapist",
            name="state",
        ),
        migrations.AlterField(
            model_name="patient",
            name="email",
            field=django_cryptography.fields.encrypt(models.EmailField(max_length=254)),
        ),
        migrations.AlterField(
            model_name="patient",
            name="name",
            field=django_cryptography.fields.encrypt(models.CharField(max_length=200)),
        ),
        migrations.AlterField(
            model_name="therapist",
            name="license_id",
            field=django_cryptography.fields.encrypt(models.CharField(max_length=200)),
        ),
        migrations.AlterField(
            model_name="therapist",
            name="name",
            field=django_cryptography.fields.encrypt(models.CharField(max_length=200)),
        ),
        migrations.AlterField(
            model_name="tlsession",
            name="recording_length",
            field=models.FloatField(),
        ),
    ]
