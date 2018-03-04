import re
import string
import random
from flask_mail import Message
from flask import current_app, render_template

from pingyou import mail
from pingyou.common.email_template import CODE_EMAIL_BODY_html, CODE_EMAIL_BODY_txt
from pingyou.common import redis_handle


def clear_str(s):
    dr = re.compile(r'</?\w+[^>]*>', re.S)
    s = re.sub(dr, '', s)
    return s


def api_response(data=None, status_code=200):
    if data is None:
        data = {}
    return {'data': data}, status_code, {'Access-Control-Allow-Origin': '*'}


def mail_generator(template: str, format_map: dict) -> str:
    return template.format_map(format_map)


def send_email(to, subject, context, **kwargs):
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = mail_generator(CODE_EMAIL_BODY_txt, context)
    msg.html = mail_generator(CODE_EMAIL_BODY_html, context)
    mail.send(msg)


def generate_code(user):
    source = string.ascii_letters + string.digits
    code = random.sample(source, 5)
    redis_handle.save_code(user.id, code)


def verify_code(user, code):
    r_code = redis_handle.get_code(user.id)
    if r_code == code:
        return True
    return False
