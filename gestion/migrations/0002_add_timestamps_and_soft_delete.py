# Generated migration for adding timestamps and soft delete

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        # Agregar campos de auditoría a Cliente
        migrations.AddField(
            model_name='cliente',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cliente',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Agregar campos de auditoría a DatosTributarios
        migrations.AddField(
            model_name='datostributarios',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='datostributarios',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Agregar campos de auditoría a CuentaDetraccion
        migrations.AddField(
            model_name='cuentadetraccion',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cuentadetraccion',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Agregar soft delete y auditoría a CredencialPlataforma
        migrations.AddField(
            model_name='credencialplataforma',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='credencialplataforma',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='credencialplataforma',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
