# Generated by Django 5.1.2 on 2024-10-28 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0002_item_iscompleted_list_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='isCompleted',
            new_name='is_completed',
        ),
        migrations.RenameField(
            model_name='list',
            old_name='createdAt',
            new_name='created_at',
        ),
    ]