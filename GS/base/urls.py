from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginPage, name='login'),
    path('home/', views.home, name='home'),
    path('subadmin/dashboard/', views.subadmin_dashboard, name='subadmin_dashboard'),
    path('produits/', views.produits, name='produits'),
    path('produits/<int:idprod>', views.produit, name='Product_Details'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),
    path('panier/', views.panier, name='panier'),
    path('panier/ajouter/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('panier/supprimer/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('panier/modifier/<int:product_id>/', views.update_cart, name='update_cart'),
    path('commander/', views.commander, name='commander'),
    path('confirmation/<int:commande_id>/', views.confirmation, name='confirmation'),
    path('categories/', views.categories, name='categories'),
    path('fournisseurs/', views.fournisseurs, name='fournisseurs'),
    path('search/', views.search_products, name='search_products'),


    path('subadmin/products/add/', views.add_product, name='add_product'),
    path('subadmin/products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('subadmin/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),


    path('subadmin/categories/add/', views.add_category, name='add_category'),
    path('subadmin/categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('subadmin/categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),


    path('subadmin/suppliers/add/', views.add_supplier, name='add_supplier'),
    path('subadmin/suppliers/<int:supplier_id>/edit/', views.edit_supplier, name='edit_supplier'),
    path('subadmin/suppliers/<int:supplier_id>/delete/', views.delete_supplier, name='delete_supplier'),

    path('subadmin/orders/<int:order_id>/', views.view_order, name='view_order'),
    path('subadmin/orders/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    
]
