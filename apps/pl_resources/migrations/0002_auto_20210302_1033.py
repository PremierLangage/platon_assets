# Generated by Django 3.1.6 on 2021-03-02 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pl_resources', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pl_resources.circle'),
        ),
    ]