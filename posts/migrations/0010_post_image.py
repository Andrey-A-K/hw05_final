# Generated by Django 2.2.6 on 2021-04-06 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20210404_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/'),
        ),
    ]