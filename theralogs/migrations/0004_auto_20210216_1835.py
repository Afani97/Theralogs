# Generated by Django 3.1.6 on 2021-02-16 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theralogs", "0003_auto_20210216_1819"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tlsession",
            name="transcript_id",
            field=models.CharField(
                blank=True, editable=False, max_length=200, null=True
            ),
        ),
    ]
