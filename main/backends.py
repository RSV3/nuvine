from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import sanitize_address
from support.models import Email
from django.conf import settings


class EmailSinkBackend(EmailBackend):

    def _send(self, email_message):
        # set recipients to be the test account email
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]

        if email_message.alternatives:
            html_msg = email_message.alternatives[0]
        else:
            html_msg = ['']

        # email_log = Email(subject=email_message.subject, sender=from_email, recipients=str(recipients), text=email_message.body, html=html_msg)
        # email_log.save()

        email_message.to = [settings.EMAIL_TEST_ACCOUNT]
        email_message.bcc, email_message.cc = ([], [])
        return super(EmailSinkBackend, self)._send(email_message)
