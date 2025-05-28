from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Produit, Client, Categorie, Fournisseur, Commande, DetailCommande
from django.contrib import messages
from .forms import ClientForm, LoginForm, CommandeForm, DetailCommandeForm
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q

def check_registration(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Veuillez vous inscrire pour accéder à cette page.')
            return redirect('register')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def registerPage(request):
    if request.session.get('user_id'):
        return redirect('home')
        
    form = ClientForm()
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            request.session['user_id'] = client.id
            messages.success(request, 'Compte créé avec succès!')
            return redirect('home')
    
    context = {'form': form}
    return render(request, 'register.html', context)

def loginPage(request):
    if request.session.get('user_id'):
        client = Client.objects.get(id=request.session['user_id'])
        if client.is_subadmin:
            return redirect('subadmin_dashboard')
        return redirect('home')
        
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            request.session['user_id'] = client.id
            if client.is_subadmin:
                messages.success(request, 'Connexion réussie! Bienvenue dans le tableau de bord administrateur.')
                return redirect('subadmin_dashboard')
            messages.success(request, 'Connexion réussie!')
            return redirect('home')
    
    context = {'form': form}
    return render(request, 'logIn.html', context)

def logoutUser(request):
    request.session.flush()
    messages.info(request, 'Vous avez été déconnecté')
    return redirect('login')

@check_registration
def home(request):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if client.is_subadmin:
        return redirect('subadmin_dashboard')
    # Get specific car models for both carousel and new products
    featured_products = Produit.objects.filter(nom__in=['BMW M5 Competition', 'Mercedes-AMG E63 S', 'Mercedes-AMG GT', 'Aston Martin Valkyrie'])
    context = {
        'client': client,
        'carousel_products': featured_products,
        'new_products': featured_products
    }
    return render(request, 'home.html', context)

@check_registration
def subadmin_dashboard(request):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')
        
    context = {
        'client': client,
        'total_products': Produit.objects.count(),
        'total_categories': Categorie.objects.count(),
        'total_suppliers': Fournisseur.objects.count(),
        'total_orders': Commande.objects.count(),
        'products': Produit.objects.all(),
        'categories': Categorie.objects.all(),
        'suppliers': Fournisseur.objects.all(),
        'orders': Commande.objects.all()
    }
    return render(request, 'subadmin_dashboard.html', context)

@check_registration
def produits(request):
    products = Produit.objects.all()
    context = {'products': products}
    return render(request, 'productsList.html', context)

@check_registration
def produit(request, idprod):
    produit = Produit.objects.get(id=idprod)
    context = {'produit': produit}
    return render(request, 'ProductDetails.html', context)

@check_registration
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Produit, id=product_id)
        
        
        if 'cart' not in request.session:
            request.session['cart'] = {}
        
        
        cart = request.session['cart']
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity
        
        request.session['cart'] = cart
        messages.success(request, f'{product.nom} ajouté au panier!')
        return redirect('panier')
    
    return redirect('Product_Details', idprod=product_id)

@check_registration
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
            messages.success(request, 'Produit retiré du panier!')
    return redirect('panier')

@check_registration
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] = quantity
            request.session['cart'] = cart
    return redirect('panier')

@check_registration
def panier(request):
    cart_items = []
    total = Decimal('0.00')
    cart = request.session.get('cart', {})
    
    for produit_id, quantity in cart.items():
        produit = Produit.objects.get(id=produit_id)
        item_total = produit.prix_unitaire * Decimal(quantity)
        cart_items.append({
            'produit': produit,
            'quantity': quantity,
            'total': item_total
        })
        total += item_total
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'panier.html', context)

@check_registration
def commander(request):
    if request.method == 'POST':
        
        client = Client.objects.get(id=request.session.get('user_id'))
        
       
        commande = Commande.objects.create(
            client=client,
            date_commande=timezone.now().date(),
            statut='En attente'
        )
        
      
        cart = request.session.get('cart', {})
        
       
        for produit_id, quantity in cart.items():
            produit = Produit.objects.get(id=produit_id)
            prix_total = produit.prix_unitaire * Decimal(quantity)
            
            DetailCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantity,
                prix_total=prix_total
            )
            
           
            produit.quantite_en_stock -= quantity
            produit.save()
        
        
        request.session['cart'] = {}
        
        messages.success(request, 'Votre commande a été enregistrée avec succès!')
        return redirect('confirmation', commande_id=commande.id)
    
    
    cart_items = []
    total = Decimal('0.00')
    cart = request.session.get('cart', {})
    
    for produit_id, quantity in cart.items():
        produit = Produit.objects.get(id=produit_id)
        item_total = produit.prix_unitaire * Decimal(quantity)
        cart_items.append({
            'produit': produit,
            'quantity': quantity,
            'total': item_total
        })
        total += item_total
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'commander.html', context)

@check_registration
def confirmation(request, commande_id):
    commande = Commande.objects.get(id=commande_id)
    details = commande.details.all()
    total = sum(detail.prix_total for detail in details)
    
    context = {
        'commande': commande,
        'details': details,
        'total': total
    }
    return render(request, 'confirmation.html', context)

@check_registration
def categories(request):
    categories = Categorie.objects.all()
    context = {'categories': categories}
    return render(request, 'categories.html', context)

@check_registration
def fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    context = {'fournisseurs': fournisseurs}
    return render(request, 'fournisseurs.html', context)


@check_registration
def add_product(request):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        prix_unitaire = request.POST.get('prix_unitaire')
        quantite_en_stock = request.POST.get('quantite_en_stock')
        seuil_minimum = request.POST.get('seuil_minimum')
        categorie_id = request.POST.get('categorie')
        fournisseur_id = request.POST.get('fournisseur')
        image = request.FILES.get('image')

        categorie = get_object_or_404(Categorie, id=categorie_id)
        fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)

        produit = Produit.objects.create(
            nom=nom,
            description=description,
            prix_unitaire=prix_unitaire,
            quantite_en_stock=quantite_en_stock,
            seuil_minimum=seuil_minimum,
            categorie=categorie,
            fournisseur=fournisseur,
            image=image
        )
        messages.success(request, 'Produit ajouté avec succès!')
        return redirect('subadmin_dashboard')

    context = {
        'categories': Categorie.objects.all(),
        'suppliers': Fournisseur.objects.all()
    }
    return render(request, 'subadmin/add_product.html', context)

@check_registration
def edit_product(request, product_id):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    product = get_object_or_404(Produit, id=product_id)
    if request.method == 'POST':
        product.nom = request.POST.get('nom')
        product.description = request.POST.get('description')
        product.prix_unitaire = request.POST.get('prix_unitaire')
        product.quantite_en_stock = request.POST.get('quantite_en_stock')
        product.seuil_minimum = request.POST.get('seuil_minimum')
        product.categorie = get_object_or_404(Categorie, id=request.POST.get('categorie'))
        product.fournisseur = get_object_or_404(Fournisseur, id=request.POST.get('fournisseur'))
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        messages.success(request, 'Produit modifié avec succès!')
        return redirect('subadmin_dashboard')

    context = {
        'product': product,
        'categories': Categorie.objects.all(),
        'suppliers': Fournisseur.objects.all()
    }
    return render(request, 'subadmin/edit_product.html', context)

@check_registration
def delete_product(request, product_id):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    product = get_object_or_404(Produit, id=product_id)
    product.delete()
    messages.success(request, 'Produit supprimé avec succès!')
    return redirect('subadmin_dashboard')


@check_registration
def add_category(request):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        Categorie.objects.create(nom=nom, description=description)
        messages.success(request, 'Catégorie ajoutée avec succès!')
        return redirect('subadmin_dashboard')
    return render(request, 'subadmin/add_category.html')

@check_registration
def edit_category(request, category_id):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    category = get_object_or_404(Categorie, id=category_id)
    if request.method == 'POST':
        category.nom = request.POST.get('nom')
        category.description = request.POST.get('description')
        category.save()
        messages.success(request, 'Catégorie modifiée avec succès!')
        return redirect('subadmin_dashboard')
    return render(request, 'subadmin/edit_category.html', {'category': category})

@check_registration
def delete_category(request, category_id):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    category = get_object_or_404(Categorie, id=category_id)
    category.delete()
    messages.success(request, 'Catégorie supprimée avec succès!')
    return redirect('subadmin_dashboard')


@check_registration
def add_supplier(request):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        Fournisseur.objects.create(nom=nom, email=email, telephone=telephone, adresse=adresse)
        messages.success(request, 'Fournisseur ajouté avec succès!')
        return redirect('subadmin_dashboard')
    return render(request, 'subadmin/add_supplier.html')

@check_registration
def edit_supplier(request, supplier_id):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    supplier = get_object_or_404(Fournisseur, id=supplier_id)
    if request.method == 'POST':
        supplier.nom = request.POST.get('nom')
        supplier.email = request.POST.get('email')
        supplier.telephone = request.POST.get('telephone')
        supplier.adresse = request.POST.get('adresse')
        supplier.save()
        messages.success(request, 'Fournisseur modifié avec succès!')
        return redirect('subadmin_dashboard')
    return render(request, 'subadmin/edit_supplier.html', {'supplier': supplier})

@check_registration
def delete_supplier(request, supplier_id):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    supplier = get_object_or_404(Fournisseur, id=supplier_id)
    supplier.delete()
    messages.success(request, 'Fournisseur supprimé avec succès!')
    return redirect('subadmin_dashboard')


@check_registration
def view_order(request, order_id):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    order = get_object_or_404(Commande, id=order_id)
    return render(request, 'subadmin/view_order.html', {'order': order})

@check_registration
def edit_order(request, order_id):
    user_id = request.session.get('user_id')
    client = Client.objects.get(id=user_id)
    if not client.is_subadmin:
        messages.warning(request, 'Accès refusé. Privilèges administrateur requis.')
        return redirect('home')

    order = get_object_or_404(Commande, id=order_id)
    if request.method == 'POST':
        order.statut = request.POST.get('statut')
        order.save()
        messages.success(request, 'Commande modifiée avec succès!')
        return redirect('subadmin_dashboard')
    return render(request, 'subadmin/edit_order.html', {'order': order})

@check_registration
def search_products(request):
    query = request.GET.get('q', '')
    if query:
        
        try:
            product = Produit.objects.get(nom__iexact=query)
            return redirect('Product_Details', idprod=product.id)
        except Produit.DoesNotExist:
           
            products = Produit.objects.filter(
                Q(nom__icontains=query) |
                Q(description__icontains=query) |
                Q(categorie__nom__icontains=query)
            ).distinct()
            
            if products.count() == 1:
                
                return redirect('Product_Details', idprod=products.first().id)
            elif products.exists():
                
                context = {
                    'products': products,
                    'query': query,
                    'search_performed': True
                }
                return render(request, 'search_results.html', context)
    
    
    messages.info(request, f'Aucun produit trouvé pour "{query}".')
    return redirect('produits')