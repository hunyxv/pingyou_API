from flask_mail import Message
from flask import current_app

from pingyou import mail
from pingyou.common.email_template import CODE_EMAIL_BODY_html, CODE_EMAIL_BODY_txt


def mail_generator(template: str, format_map: dict) -> str:
    return template.format_map(format_map)


def send_email(to, subject, context, **kwargs):
    print(to)
    msg = Message(
        current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] +
        subject,
        sender=current_app.config['FLASKY_MAIL_SENDER'],
        recipients=[to])
    msg.body = mail_generator(CODE_EMAIL_BODY_txt, context)
    msg.html = mail_generator(CODE_EMAIL_BODY_html, context)
    mail.send(msg)
