# Generated by Django 3.1.6 on 2021-02-04 19:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [('theralogs', '0001_initial'), ('theralogs', '0002_auto_20201221_2055'), ('theralogs', '0003_auto_20201221_2056'), ('theralogs', '0004_auto_20201221_2059'), ('theralogs', '0005_auto_20201222_1950'), ('theralogs', '0006_auto_20210103_0401'), ('theralogs', '0007_auto_20210103_1823'), ('theralogs', '0008_auto_20210111_1859'), ('theralogs', '0009_therapist_stripe_customer_id'), ('theralogs', '0010_therapist_stripe_payment_method_id'), ('theralogs', '0011_auto_20210113_2137'), ('theralogs', '0012_auto_20210113_2146'), ('theralogs', '0013_delete_tlfile'), ('theralogs', '0014_auto_20210201_1253'), ('theralogs', '0015_auto_20210201_1355'), ('theralogs', '0016_auto_20210204_1805')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Therapist',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('license_id', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('stripe_customer_id', models.CharField(editable=False, max_length=200)),
                ('stripe_payment_method_id', models.CharField(blank=True, editable=False, max_length=200, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('therapist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='theralogs.therapist')),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TLSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='theralogs.patient')),
                ('recording_length', models.FloatField(default=0)),
                ('recording_json', models.TextField(blank=True, editable=False, null=True)),
            ],
        ),
    ]
