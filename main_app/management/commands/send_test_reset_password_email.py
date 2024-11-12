# main_app/management/commands/send_test_reset_password_email.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Send a test email to verify the password reset email template."

    def handle(self, *args, **kwargs):
        subject = "Reset Your Password - Test Email"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['frankie@rubbleapp.com']

        # Render the HTML password reset email template with example context
        context = {
            'user': {'get_username': 'Frankie'},  # Example username
            'site_name': 'Rubble',
            'protocol': 'https',
            'domain': 'rubbleapp.com',
            'uid': 'dummy-uid',  # Mock UID for testing
            'token': 'dummy-token'  # Mock token for testing
        }
        html_content = render_to_string('email_templates/reset_password.html', context)
        text_content = "To reset your password, please follow the link provided in the email."

        # Set up the email with both HTML and plain-text versions
        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")

        # Send the email
        try:
            email.send()
            self.stdout.write(self.style.SUCCESS("Test password reset email sent successfully to frankie@rubbleapp.com"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send email: {e}"))