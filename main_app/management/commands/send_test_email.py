# main_app/management/commands/send_test_email.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Send a test email to verify the welcome email template."

    def handle(self, *args, **kwargs):
        subject = "Welcome to Rubble - Test Email"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['frankie@rubbleapp.com']

        # Render the HTML email template with any context needed
        context = {
            'username': 'Frankie',  # Example username
            'year': 2024,  # Example year
        }
        html_content = render_to_string('email_templates/welcome_email.html', context)
        text_content = "Welcome to Rubble! A new marketplace for construction and DIY project materials."

        # Create the email
        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")

        # Send the email
        try:
            email.send()
            self.stdout.write(self.style.SUCCESS("Test email sent successfully to frankie@rubbleapp.com"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send email: {e}"))
