from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

from ..constants import ICON_FORMATS
from ..managers import CategoryManager


class Category(MPTTModel):
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_file = models.FileField(
        upload_to='icons/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(ICON_FORMATS)],
        verbose_name="Icône",
        help_text="Formats acceptés: .ico, .png, .jpg, .svg (max 5MB)"
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Catégorie parente"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryManager()

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['parent', 'name']),
        ]

    def __str__(self):
        return f"{'—' * self.level} {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from ..utils import generate_unique_slug
            self.slug = generate_unique_slug(Category, self.name, max_length=120)
        super().save(*args, **kwargs)

    @property
    def is_main_category(self):
        return self.is_root_node()

    @property
    def product_count(self):
        return self.get_all_products().count()

    @property
    def direct_product_count(self):
        return self.products.count()

    def get_all_products(self):
        descendant_ids = self.get_descendants(include_self=True).values_list('id', flat=True)
        from .product import Product
        return Product.objects.filter(category_id__in=descendant_ids)

    def get_breadcrumb(self):
        return self.get_ancestors(include_self=True)

    def get_siblings_and_self(self):
        return self.get_siblings(include_self=True)

    def get_full_path(self, separator=' > '):
        ancestors = self.get_ancestors(include_self=True)
        return separator.join([cat.name for cat in ancestors])
