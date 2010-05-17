# -*- coding:utf-8 -*-
from xml.sax.saxutils import quoteattr, escape


def attr_str(attrs):
    if not attrs:
        return u''
    return u''.join(
        u' %s=%s' % (k, quoteattr(v)) for k, v in attrs.iteritems(),
    )


class XMLGenerator(object):
    def __init__(self, file, root, attrs={}):
        self.file = file
        self.file.write('<?xml version="1.0" encoding="utf-8"?>')
        self.stack = []
        self.container(root, attrs)

    def _write(self, value):
        self.file.write(value.encode('utf-8'))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._write(u'</%s>' % self.stack.pop())

    def container(self, name, attrs={}):
        self._write(u'<%s%s>' % (name, attr_str(attrs)))
        self.stack.append(name)
        return self

    def element(self, name, attrs={}, text=u''):
        bits = [u'<%s%s' % (name, attr_str(attrs))]
        if text:
            bits.append(u'>%s</%s>' % (escape(text), name))
        else:
            bits.append(u'/>')
        self._write(u''.join(bits))

    def text(self, text):
        self._write(escape(text))


xml = XMLGenerator
