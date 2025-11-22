from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Service(models.Model):
    title = models.CharField(max_length=150, verbose_name="Titre")
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(
        upload_to='services/',
        null=True,
        blank=True,
        verbose_name="Image"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    external_link = models.URLField(blank=True, null=True, verbose_name="Lien externe")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from ..utils import generate_unique_slug
            self.slug = generate_unique_slug(Service, self.title, max_length=180)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return self.external_link or reverse('service_detail', kwargs={'slug': self.slug})
