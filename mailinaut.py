# mailinaut.py
# -*- coding: utf-8 -*-

import jinja2

from jinja2 import TemplateNotFound, TemplatesNotFound

import markdown2

import smtplib

try:                   # Python 2.7+
    from collections import Iterator
except ImportError:    # Python 3.3+
    from collections.abc import Iterator

from collections import OrderedDict

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class FiletypeHandler(object):

    def __init__(self, template):
        self.template = template


class TextHandler(FiletypeHandler):

    def render(self, context):
        return MIMEText(self.template.render(**context), 'plain')


class HTMLHandler(FiletypeHandler):

    def render(self, context):
        return MIMEText(self.template.render(**context), 'html')


class MarkdownHandler(FiletypeHandler):
    def render(self, context):
        rendered = self.template.render(**context)
        return MIMEText(markdown2.markdown(rendered), 'html')

class HandlerNotFound(Exception):
    pass

filetype_handlers = OrderedDict()


def register_handler(handler, *extensions):
    for extension in extensions:
        filetype_handlers[extension] = handler

register_handler(TextHandler, 'txt')
register_handler(HTMLHandler, 'htm', 'html')
register_handler(MarkdownHandler, 'md')

template_folders = ['templates']

environment = None


def reload_environment():
    # This function is automatically called the first time a Message object
    # is created. This allows the user to modify template_folders before
    # creating a message.
    global environment
    loader = jinja2.FileSystemLoader(template_folders)
    environment = jinja2.Environment(loader=loader)


class Message(object):

    def __init__(self, handlers):
        self.handlers = handlers

    @classmethod
    def from_templates(cls, templates):
        """
        Constructs a message from a template name.

        Templates are loaded from the /templates directory under the script that sends the email.

        :param templates: A single, or list of templates to render
        :returns An instance of the Message class tied to the specified templates
        """
        if environment is None:
            reload_environment()

        handlers = []

        if isinstance(templates, str):
            for extension, handler in filetype_handlers.iteritems():
                try:
                    template = environment.get_template(templates + '.' +
                                                        extension)
                    handlers.append(handler(template))
                except TemplateNotFound:
                    pass
            if not len(handlers):
                raise TemplatesNotFound((templates,))
        elif isinstance(templates, Iterator):
            for name, extension in ((template, template.split('.')[-1])
                                    for template in templates):
                try:
                    template = environment.get_template(name)
                    handler = filetype_handlers[extension]
                    handlers.append(handler(template))
                except KeyError:
                    raise HandlerNotFound
        return cls(handlers)

    def render(self, subject, context):
        """
        Renders the email with the given context

        :param subject: The message subject
        :param context: A dictionary of variables for the template
        """
        messages = [handler.render(context) for handler in self.handlers]

        if len(messages) == 1:
            self.message = messages[0]
        elif len(messages) > 1:
            self.message = MIMEMultipart('alternative')

            for submessage in messages:
                self.message.attach(submessage)

        self.message['Subject'] = subject

    def send(self, fromaddress, toaddress, login=None, **kwargs):
        """
        Sends the message

        :param fromaddress: The from address of the email
        :param toaddress: A single, or list of destination addresses
        :param login: (optional) A tuple of username and password
        :param kwargs: (optional) Additional keyword args can be used to pass configuration options off to the SMTP library
        """
        ssl = kwargs.get('ssl', False)

        # Construct the message itself
        self.message['From'] = fromaddress

        if isinstance(toaddress, str):
            self.message['To'] = toaddress
        elif isinstance(toaddress, Iterator):
            self.message['To'] = ', '.join(toaddress)

        # Hook up to the SMTP server
        SMTP = smtplib.SMTP_SSL if ssl else smtplib.SMTP

        config = {
            'host': 'localhost',
            'port': 465 if ssl else 25
        }

        # Overlay additional onto the SMTP configuration
        config.update(kwargs)

        connection = SMTP(**config)

        if login is not None:
            user, password = login
            connection.login(user, password)

        connection.sendmail(fromaddress, toaddress, self.message.as_string())

        connection.quit()

from_templates = Message.from_templates
