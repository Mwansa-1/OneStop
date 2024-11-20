# Generated by Django 4.2.2 on 2024-11-20 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_policy_file_alter_policy_content'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='policy',
            options={'verbose_name_plural': 'Policies'},
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(blank=True, choices=[('staff', 'Staff'), ('student', 'Student')], default='student', max_length=10, null=True),
        ),
    ]
