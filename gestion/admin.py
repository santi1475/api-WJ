from django.contrib import admin
from .models import Cliente, Credenciales

class CredencialesInline(admin.StackedInline):
    model = Credenciales
    can_delete = False
    verbose_name_plural = 'Claves y Accesos'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    inlines = [CredencialesInline]
    list_display = ('ruc', 'razon_social', 'estado', 'responsable')
    search_fields = ('ruc', 'razon_social')
    list_filter = ('estado', 'regimen_tributario')