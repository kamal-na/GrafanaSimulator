# Generated by Django 3.1.7 on 2021-05-03 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0011_db_datasource_port'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_datasource',
            name='Port',
            field=models.IntegerField(),
        ),
    ]
