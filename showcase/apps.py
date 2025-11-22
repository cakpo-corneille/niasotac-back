from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'showcase'
    verbose_name = 'Gestion des produits'

    def ready(self):
        import showcase.signals
