# Generated by Django 5.0.7 on 2024-09-04 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adhafera', '0002_rename_list_order_listuser_list_position_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listsharecode',
            name='username',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='listsharecode',
            unique_together={('list', 'username')},
        ),
    ]