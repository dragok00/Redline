from redline.celery import app
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from time import sleep
import random


logger = get_task_logger(__name__)

def generate_code_task():
    return random.randint(100000, 999999)


@app.task(name = 'send_email_task')
def send_mail_task(subject, message, email_from, recipient_list):
    context = {
        'registration_code': message,
    }

    html_content = render_to_string('registration_code.html', context)

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        message,
        email_from,
        [recipient_list]
    )

    email.attach_alternative(html_content, 'text/html')

    email.send()
