# Generated by Django 5.1.3 on 2024-12-14 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200)),
                ('reservation_date', models.DateField()),
                ('reservation_slot', models.SmallIntegerField(default=10)),
            ],
        ),
    ]
