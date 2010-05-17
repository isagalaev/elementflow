# -*- coding:utf-8 -*-
from xml.sax.saxutils import quoteattr, escape


def attr_str(attrs):
    if not attrs:
        return u''
    return u''.join(
        u' %s=%s' % (k, quoteattr(v)) for k, v in attrs.iteritems()
    )


class XMLGenerator(object):
    def __init__(self, file, root, attrs={}, namespaces={}):
        self.file = file
        self.file.write('<?xml version="1.0" encoding="utf-8"?>')
        self.stack = []
        self.namespaces = [set(['xml'])]
        self.container(root, attrs, namespaces)

    def _write(self, value):
        self.file.write(value.encode('utf-8'))

    def _process_namespaces(self, name, attrs, namespaces):
        prefixes = self.namespaces[-1] | set(namespaces.keys())
        names = (n for n in [name] + attrs.keys() if ':' in n)
        for name in names:
            prefix = name.split(':')[0]
            if prefix not in prefixes:
                raise ValueError('Unkown namespace prefix: %s' % prefix)
        namespaces = dict(
            (u'xmlns:%s' % k if k else u'xmlns', v)
            for k, v in namespaces.iteritems()
        )
        return dict(attrs, **namespaces), prefixes

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._write(u'</%s>' % self.stack.pop())
        self.namespaces.pop()

    def container(self, name, attrs={}, namespaces={}):
        attrs, prefixes = self._process_namespaces(name, attrs, namespaces)
        self._write(u'<%s%s>' % (name, attr_str(attrs)))
        self.stack.append(name)
        self.namespaces.append(prefixes)
        return self

    def element(self, name, attrs={}, namespaces={}, text=u''):
        attrs, prefixes = self._process_namespaces(name, attrs, namespaces)
        bits = [u'<%s%s' % (name, attr_str(attrs))]
        if text:
            bits.append(u'>%s</%s>' % (escape(text), name))
        else:
            bits.append(u'/>')
        self._write(u''.join(bits))

    def text(self, text):
        self._write(escape(text))


class Queue(object):
    def __init__(self):
        self.data = bytearray()

    def __len__(self):
        return len(self.data)

    def write(self, value):
        self.data.extend(value)

    def pop(self):
        result = str(self.data)
        self.data = bytearray()
        return result


xml = XMLGenerator
