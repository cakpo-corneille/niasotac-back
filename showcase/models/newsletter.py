import urllib.parse
import uuid
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils import timezone

from ..constants import NEWSLETTER_CAMPAIGN_STATUSES
from ..managers import NewsletterSubscriberManager


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")
    name = models.CharField(max_length=150, blank=True, verbose_name="Nom")
    subscribed = models.BooleanField(default=True, verbose_name="Abonné")
    confirmed = models.BooleanField(default=False, verbose_name="Confirmé")
    confirmation_token = models.CharField(max_length=64, blank=True, db_index=True)
    source = models.CharField(max_length=100, blank=True, verbose_name="Source")
    tags = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Tags (séparés par des virgules)"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    objects = NewsletterSubscriberManager()

    class Meta:
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['confirmation_token'])
        ]

    def __str__(self):
        return f"{self.email} {'(confirmed)' if self.confirmed else ''}"

    def save(self, *args, **kwargs):
        if not self.confirmation_token:
            self.confirmation_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def get_confirmation_url(self, request=None):
        try:
            rel = reverse('newsletter_confirm', kwargs={'token': self.confirmation_token})
        except Exception:
            rel = f"/newsletter/confirm/{self.confirmation_token}/"

        if request:
            return request.build_absolute_uri(rel)

        try:
            current_site = Site.objects.get_current()
            return f"https://{current_site.domain}{rel}"
        except Exception:
            frontend = getattr(settings, "FRONTEND_URL", None) or "https://localhost"
            return f"{frontend}{rel}"

    def get_unsubscribe_url(self, request=None):
        try:
            rel = reverse('newsletter_unsubscribe', kwargs={'email': urllib.parse.quote(self.email)})
        except Exception:
            rel = f"/newsletter/unsubscribe/{urllib.parse.quote(self.email)}/"

        if request:
            return request.build_absolute_uri(rel)

        try:
            current_site = Site.objects.get_current()
            return f"https://{current_site.domain}{rel}"
        except Exception:
            frontend = getattr(settings, "FRONTEND_URL", None) or "https://localhost"
            return f"{frontend}{rel}"

    def send_confirmation_email(self, request=None, from_email=None):
        from ..services.newsletter_service import NewsletterService
        NewsletterService.send_confirmation_email(self, request)

    def confirm(self):
        self.confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=['confirmed', 'confirmed_at'])

    def unsubscribe(self):
        self.subscribed = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['subscribed', 'unsubscribed_at'])


class NewsletterTemplate(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nom template")
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    plain_content = models.TextField(verbose_name="Contenu texte", blank=True)
    html_content = models.TextField(verbose_name="Contenu HTML", blank=True)
    is_active = models.BooleanField(default=True)
    default_from = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Template newsletter"
        verbose_name_plural = "Templates newsletter"
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from ..utils import generate_unique_slug
            self.slug = generate_unique_slug(NewsletterTemplate, self.name, max_length=180)
        super().save(*args, **kwargs)

    def render_for_subscriber(self, subscriber):
        context = {
            'name': subscriber.name or '',
            'email': subscriber.email,
            'unsubscribe_url': subscriber.get_unsubscribe_url(),
        }
        text = self.plain_content.format(**context) if self.plain_content else ''
        html = self.html_content.format(**context) if self.html_content else ''
        return text, html


class NewsletterCampaign(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_SENDING = 'sending'
    STATUS_SENT = 'sent'
    STATUS_CANCELLED = 'cancelled'

    name = models.CharField(max_length=200, verbose_name="Nom campagne")
    template = models.ForeignKey(
        NewsletterTemplate,
        on_delete=models.PROTECT,
        related_name='campaigns'
    )
    subscribers = models.ManyToManyField(
        NewsletterSubscriber,
        blank=True,
        related_name='campaigns'
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Planifiée pour"
    )
    status = models.CharField(
        max_length=20,
        choices=NEWSLETTER_CAMPAIGN_STATUSES,
        default=STATUS_DRAFT
    )
    sent_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Campagne newsletter"
        verbose_name_plural = "Campagnes newsletter"
        ordering = ['-scheduled_at', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"

    def queue_recipients(self):
        qs = self.subscribers.all()
        if not qs.exists():
            qs = NewsletterSubscriber.objects.filter(subscribed=True, confirmed=True)
        return qs

    def send(self, chunk_size=100, from_email=None):
        from ..services.newsletter_service import NewsletterService
        return NewsletterService.send_campaign(self, chunk_size, from_email)


class NewsletterLog(models.Model):
    campaign = models.ForeignKey(
        NewsletterCampaign,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    subscriber = models.ForeignKey(
        NewsletterSubscriber,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[('sent', 'Envoyé'), ('failed', 'Échec')],
        default='sent'
    )
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log newsletter"
        verbose_name_plural = "Logs newsletter"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign', 'subscriber']),
        ]

    def __str__(self):
        subscriber_email = self.subscriber.email if self.subscriber else 'N/A'
        return f"{self.campaign.name} → {subscriber_email}: {self.status}"
