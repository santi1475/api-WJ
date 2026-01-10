from django.contrib import admin
from .models import Cliente, DatosTributarios, CredencialPlataforma, CuentaDetraccion

class DatosTributariosInline(admin.StackedInline):
    model = DatosTributarios
    can_delete = False

class CredencialInline(admin.TabularInline):
    model = CredencialPlataforma
    extra = 1

class CuentaDetraccionInline(admin.StackedInline):
    model = CuentaDetraccion
    can_delete = False

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'ruc', 'responsable', 'categoria', 'estado')
    search_fields = ('razon_social', 'ruc')
    list_filter = ('categoria', 'estado', 'datos_tributarios__regimen_tributario')
    inlines = [DatosTributariosInline, CuentaDetraccionInline, CredencialInline]

admin.site.register(CredencialPlataforma)