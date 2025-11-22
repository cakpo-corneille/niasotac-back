from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from ..constants import SOCIAL_MEDIA_PLATFORMS


class SocialLink(models.Model):
    name = models.CharField(max_length=50, choices=SOCIAL_MEDIA_PLATFORMS)
    url = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.name}"


class SiteSettings(models.Model):
    whatsapp_number = models.CharField(
        max_length=20,
        default="229XXXXXXXXX",
        verbose_name="Numéro WhatsApp",
        help_text="Format: 229XXXXXXXXX (sans le +)"
    )
    contact_email = models.EmailField(
        default="contact@niasotac.com",
        verbose_name="Email de contact"
    )
    contact_phone = models.CharField(
        max_length=20,
        default="+229 00 00 00 00",
        verbose_name="Téléphone de contact"
    )
    contact_address = models.CharField(
        max_length=200,
        default="Cotonou, Bénin",
        verbose_name="Adresse"
    )
    company_name = models.CharField(
        max_length=100,
        default="NIASOTAC TECHNOLOGIE",
        verbose_name="Nom de l'entreprise"
    )
    company_description = models.TextField(
        default="Votre revendeur tech de confiance au Bénin. Produits de qualité à prix compétitifs.",
        verbose_name="Description de l'entreprise"
    )
    social_links = models.ManyToManyField(SocialLink, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modifié par"
    )

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return "Paramètres du site"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("La suppression des paramètres du site est interdite.")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
