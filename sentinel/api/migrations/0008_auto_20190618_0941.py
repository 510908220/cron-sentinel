# Generated by Django 2.2.2 on 2019-06-18 09:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20190617_2356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddIndex(
            model_name='alert',
            index=models.Index(fields=['unique_id', 'created'], name='alert_unique__b7e540_idx'),
        ),
    ]
