from django.core.management.base import BaseCommand
from showcase.models import Category, Product
from django.core.files import File
from pathlib import Path
import random


class Command(BaseCommand):
    help = 'Peuple la base de données avec des catégories et produits de test'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('📦 Début du peuplement des données...'))

        media_root = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'products'

        categories_data = {
            'Ordinateurs': ['Ordinateurs portables', 'Ordinateurs de bureau', 'Mini PC'],
            'Composants': ['Processeurs', 'Cartes mères', 'Mémoire RAM'],
            'Imprimantes': ['Imprimantes laser', 'Imprimantes jet d\'encre', 'Imprimantes multifonctions'],
            'Accessoires': ['Claviers et souris', 'Webcams et microphones', 'Casques audio']
        }

        products_data = {
            # Exemple réduit pour clarté
            'Ordinateurs portables': [
                {'name': 'HP Pavilion 15', 'brand': 'HP', 'price': 450000, 'desc': 'Intel Core i5, 8Go RAM, 512Go SSD.', 'image': 'hp_pavilion_15_lapto_82f27639.jpg'},
                {'name': 'Dell Latitude 5420', 'brand': 'Dell', 'price': 520000, 'desc': 'Intel Core i7, 16Go RAM, 1To SSD.', 'image': 'dell_latitude_busine_0709ca7a.jpg'},
            ],
            'Casques audio': [
                {'name': 'Sony WH-1000XM4', 'brand': 'Sony', 'price': 185000, 'desc': 'Réduction de bruit active, autonomie 30h.', 'image': 'sony_wh-1000xm4_wire_082c1f72.jpg'},
            ],
            # Ajoute les autres sous-catégories ici…
        }

        # 🔄 Réinitialiser la base
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write('🧹 Anciennes données supprimées.')

        # 🏗 Créer les catégories
        category_map = {}
        for parent_name, subcats in categories_data.items():
            parent = Category.objects.create(name=parent_name, icon='fa fa-folder')
            category_map[parent_name] = parent
            self.stdout.write(self.style.SUCCESS(f'✓ Catégorie principale: {parent_name}'))

            for sub_name in subcats:
                sub = Category.objects.create(name=sub_name, parent=parent, icon='fa fa-tag')
                category_map[sub_name] = sub
                self.stdout.write(f'  ✓ Sous-catégorie: {sub_name}')

        # 🛒 Créer les produits
        for subcat_name, items in products_data.items():
            category = category_map.get(subcat_name)
            if not category:
                self.stdout.write(self.style.WARNING(f'⚠ Sous-catégorie introuvable: {subcat_name}'))
                continue

            for item in items:
                product = Product(
                    name=item['name'],
                    brand=item['brand'],
                    price=item['price'],
                    description=item['desc'],
                    category=category,
                    in_stock=random.choice([True, True, False]),
                    featured=random.choice([True, False])
                )

                image_path = media_root / item['image']
                if image_path.exists():
                    with open(image_path, 'rb') as f:
                        product.image.save(item['image'], File(f), save=False)
                else:
                    self.stdout.write(self.style.WARNING(f'    ⚠ Image non trouvée: {item["image"]}'))

                product.save()
                self.stdout.write(f'    ✓ Produit: {product.name} ({product.price} FCFA)')

        # 📊 Statistiques
        total_main = Category.objects.filter(parent__isnull=True).count()
        total_sub = Category.objects.filter(parent__isnull=False).count()
        total_products = Product.objects.count()

        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS(f'✓ {total_main} catégories principales'))
        self.stdout.write(self.style.SUCCESS(f'✓ {total_sub} sous-catégories'))
        self.stdout.write(self.style.SUCCESS(f'✓ {total_products} produits créés'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('✅ Données de test créées avec succès !'))
