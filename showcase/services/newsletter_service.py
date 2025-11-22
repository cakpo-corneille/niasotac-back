from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction


class NewsletterService:

    @staticmethod
    def send_confirmation_email(subscriber, request=None):
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@localhost")
        subject = "Confirmez votre inscription à la newsletter"
        confirm_url = subscriber.get_confirmation_url(request)

        text = (
            f"Bonjour {subscriber.name or ''},\n\n"
            "Merci de vous être inscrit(e) à notre newsletter.\n"
            f"Veuillez confirmer votre inscription en cliquant sur le lien suivant:\n\n{confirm_url}\n\n"
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.\n"
        )

        html = (
            f"<p>Bonjour {subscriber.name or ''},</p>"
            "<p>Merci de vous être inscrit(e) à notre newsletter.</p>"
            f"<p><a href='{confirm_url}'>Confirmer mon inscription</a></p>"
        )

        msg = EmailMultiAlternatives(subject, text, from_email, [subscriber.email])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=True)

    @staticmethod
    def send_campaign(campaign, chunk_size=100):
        from ..models import NewsletterLog

        if campaign.status in ['sent', 'cancelled']:
            return 0

        template = campaign.template
        if not template.is_active:
            return 0

        from_email = template.default_from or getattr(
            settings, "DEFAULT_FROM_EMAIL", "no-reply@localhost"
        )

        recipients_qs = campaign.queue_recipients()
        total_sent = 0

        campaign.status = 'sending'
        campaign.save(update_fields=['status'])

        try:
            pks = list(recipients_qs.values_list('pk', flat=True))
            for i in range(0, len(pks), chunk_size):
                chunk_pks = pks[i:i + chunk_size]
                subscribers = recipients_qs.model.objects.filter(pk__in=chunk_pks)

                with transaction.atomic():
                    for sub in subscribers:
                        try:
                            text, html = template.render_for_subscriber(sub)
                            subject = template.subject.format(
                                name=sub.name or "",
                                email=sub.email
                            )
                            msg = EmailMultiAlternatives(
                                subject, text or '', from_email, [sub.email]
                            )
                            if html:
                                msg.attach_alternative(html, "text/html")
                            msg.send(fail_silently=False)

                            NewsletterLog.objects.create(
                                campaign=campaign,
                                subscriber=sub,
                                status='sent'
                            )
                            total_sent += 1
                        except Exception as e:
                            NewsletterLog.objects.create(
                                campaign=campaign,
                                subscriber=sub,
                                status='failed',
                                error=str(e)
                            )

            campaign.sent_count = total_sent
            campaign.status = 'sent'
            campaign.save(update_fields=['sent_count', 'status'])
        except Exception:
            campaign.status = 'cancelled'
            campaign.save(update_fields=['status'])
            raise

        return total_sent
