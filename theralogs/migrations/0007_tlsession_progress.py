# Generated by Django 3.1.6 on 2021-03-03 18:24

from django.db import migrations, models
import theralogs.models


class Migration(migrations.Migration):

    dependencies = [
        ("theralogs", "0006_tlsession_refunded"),
    ]

    operations = [
        migrations.AddField(
            model_name="tlsession",
            name="progress",
            field=models.IntegerField(
                choices=[(1, "PENDING"), (2, "COMPLETED"), (3, "FAILED")],
                default=theralogs.models.TLSession.ProgressTypes["PENDING"],
            ),
        ),
    ]
