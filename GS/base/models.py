from django.db import models
from django.contrib.auth.models import AbstractUser



class Client(models.Model):
    nom = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True, unique=True)
    adresse = models.CharField(max_length=300, null=True, blank=True)
    telephone = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    is_subadmin = models.BooleanField(default=False)

    def __str__(self):
        return self.nom or self.email

class Categorie(models.Model):
    nom = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nom
    
class Fournisseur(models.Model):
    nom = models.CharField(max_length=200, null=True, blank=True)
    adresse = models.CharField(max_length=300, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    telephone = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    nom = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantite_en_stock = models.IntegerField(null=True, blank=True)
    seuil_minimum = models.IntegerField(null=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nom

class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    date_commande = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.client.nom if self.client else 'Client inconnu'}"


class DetailCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="details")
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    quantite = models.IntegerField(null=True, blank=True)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Détail #{self.id} - {self.produit.nom if self.produit else 'Produit inconnu'}"