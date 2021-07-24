# Generated by Django 3.1.7 on 2021-03-31 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('UserName', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('Password', models.CharField(max_length=30)),
                ('FullName', models.CharField(max_length=80)),
                ('Email', models.EmailField(max_length=50)),
                ('SDATE', models.DateTimeField()),
            ],
        ),
    ]
