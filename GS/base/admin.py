from django.contrib import admin
from .models import *

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'is_subadmin')
    list_filter = ('is_subadmin',)
    search_fields = ('nom', 'email', 'telephone')
    fieldsets = (
        ('Personal Information', {
            'fields': ('nom', 'email', 'telephone', 'adresse')
        }),
        ('Account Settings', {
            'fields': ('password', 'is_subadmin')
        }),
    )

admin.site.register(Categorie)
admin.site.register(Fournisseur)
admin.site.register(Produit)
admin.site.register(Commande)
admin.site.register(DetailCommande)