import json
import logging

from django.conf import settings
from django.template.loader import render_to_string
from rest_framework.renderers import JSONRenderer

from argus.incident.serializers import IncidentSerializer
from .base import NotificationMedium


LOG = logging.getLogger(__name__)

__all__ = ['EmailNotification']


def send_email_safely(function, additional_error=None, *args, **kwargs):
    try:
        result = function(*args, **kwargs)
        return result
    except ConnectionRefusedError as e:
        EMAIL_HOST = getattr(settings, "EMAIL_HOST", None)
        if not EMAIL_HOST:
            LOG.error("Notification: Email: EMAIL_HOST not set, cannot send")
        EMAIL_PORT = getattr(settings, "EMAIL_PORT", None)
        if not EMAIL_PORT:
            LOG.error("Notification: Email: EMAIL_PORT not set, cannot send")
        if EMAIL_HOST and EMAIL_PORT:
            LOG.error('Notification: Email: Connection refused to "%s", port "%s"', EMAIL_HOST, EMAIL_PORT)
        if additional_error:
            LOG.error(*additional_error)
        # TODO: Store error as incident


class EmailNotification(NotificationMedium):
    @staticmethod
    def send(incident, user, **_):
        if not user.email:
            logging.getLogger("django.request").warning(
                f"Cannot send email notification to user '{user}', as they have not set an email address."
            )

        title = f"Incident at {incident}"
        incident_dict = IncidentSerializer(incident, context={IncidentSerializer.NO_PKS_KEY: True}).data
        # Convert OrderedDicts to dicts
        incident_dict = json.loads(JSONRenderer().render(incident_dict))

        template_context = {
            "title": title,
            "incident_dict": incident_dict,
            "longest_field_name_length": len(max(incident_dict, key=len)),
        }
        subject = f"{settings.NOTIFICATION_SUBJECT_PREFIX}{title}"
        message = render_to_string("notificationprofile/email.txt", template_context)
        html_message = render_to_string("notificationprofile/email.html", template_context)
        send_email_safely(user.email_user, subject=subject, message=message, html_message=html_message)
