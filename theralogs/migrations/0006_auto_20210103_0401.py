# Generated by Django 3.1.4 on 2021-01-03 04:01
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theralogs', '0005_auto_20201222_1950'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='user',
        ),
        migrations.AddField(
            model_name='patient',
            name='email',
            field=models.EmailField(default='test@test.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='patient',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
