# Generated for role profile saving on 2026-06-05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicaluser",
            name="active_districts",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="medicaluser",
            name="active_doctors",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="medicaluser",
            name="admin_name",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="medicaluser",
            name="category",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="medicaluser",
            name="total_patients",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
