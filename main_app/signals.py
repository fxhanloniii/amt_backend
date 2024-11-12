
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = "Welcome to Rubble — DIY & construction marketplace"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]

        # Render HTML email template with context data
        context = {
            'username': instance.username,
            'year': datetime.now().year,
        }
        html_content = render_to_string('main_app/email_templates/welcome_email.html', context)
        text_content = "Check out our app for more."

        # Set up the email with both HTML and plain-text versions
        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
