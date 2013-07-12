Mailinaut: sending templated emails with ease
====

Mailinaut is a small Python module designed to simplify sending templated multipart e-mails. Here's how it works: let's say we want to send our users a welcome e-mail. We store the different parts of the e-mail as separate files in our template folder, like this:

templates/hello.html

```html
<html><head></head><body>
<<<<<<< HEAD
	<p>Hello, {{ name }}. Welcome to the future.
=======
  <p>Hello, {{ name }}. Welcome to the future.
>>>>>>> 9905dd3e10165af5bfb6f6c280eeca617e318a36
</html></body>
```

templates/hello.txt

```
Hello, {{ name }}. Welcome to the future.
```

Then, on our greeting script, we write something like this:

```python
import mailinaut

greeting = mailinaut.from_templates('hello')
greeting.render(subject="The future", context={'name': 'John Doe'})
greeting.send('me@example.com', 'you@example.com')
```

And voila! If you've ever used Flask, this will ring a bell: Just like Flask greases the wheels so that Jinja2 and Werkzeug work in harmony, Mailinaut aims to do the same between Jinja2 and Python's smtplib and email standard libraries.

Oooh, nicey! What else can it do?
====

Right now? Not much. I've just started this. If you want to help, please serve yourself! Here's some things I think it should do:

* Sending attachments (this one should be easy to beginners, methinks)
* Hidden destinataries on sending
* Rendering Markdown templates to HTML
* Print money (one can only dream...)

If you manage to do any of those, feel free to send me a pull request!

Documentation?
====

_But I'm le tired!_ Fiiine, here's an overview:

mailinator.from_templates(templates)

This is an alias to mailinator.Message.from_templates, which is a class method. 
It takes a string containing a filename without its extension or a list of strings containing filenames with extensions. The former looks for files with that name of known handled extensions, and raises a TemplatesNotFound error if no files are found. The latter looks for files with that name and extension, and raises a TemplateNotFound error if any of them are missing, or a HandlerNotFound error if there is no known handler for any or some of the files' extensions.
It returns a Message object.

mailinator.Message.render(subject, context)

This takes the subject of the e-mail as a string and the context for the template *as a dictionary* and renders the template accordingly. It returns nothing.

mailinator.Message.send(from, to, login=None, ssl=False, **kwargs)

This takes a sender email as a string, a receiver email as either a string or a list of receiver emails, and a bunch of other stuff. The login argument, if provided, must be a tuple (user, password). Look at smtplib's SMTP and SMTP_SSL for the other stuff.

mailinator.register_handler(handler, *extensions)

<<<<<<< HEAD
It takes a file type handler and a bunch of extensions which it is supposed to handle and makes it so that it handles them. Easy peasy.
=======
It takes a file type handler and a bunch of extensions which it is supposed to handle and makes it so that it handles them. Easy peasy.
>>>>>>> 9905dd3e10165af5bfb6f6c280eeca617e318a36
