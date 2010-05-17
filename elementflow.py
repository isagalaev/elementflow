# -*- coding:utf-8 -*-
from xml.sax.saxutils import quoteattr, escape


def attr_str(attrs):
    if not attrs:
        return u''
    return u''.join(u' %s=%s' % (k, quoteattr(v)) for k, v in attrs.iteritems())


class XMLGenerator(object):
    def __init__(self, file, root, attrs={}, **kwargs):
        self.file = file
        self.file.write('<?xml version="1.0" encoding="utf-8"?>')
        self.stack = []
        self.container(root, attrs, **kwargs)

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

    def text(self, value):
        self._write(escape(value))


class NamespacedGenerator(XMLGenerator):
    def __init__(self, file, root, attrs={}, namespaces={}):
        self.namespaces = [set(['xml'])]
        super(NamespacedGenerator, self).__init__(file, root, attrs=attrs, namespaces=namespaces)

    def _process_namespaces(self, name, attrs, namespaces):
        prefixes = self.namespaces[-1]
        if namespaces:
            prefixes |= set(namespaces.keys())
        names = (n for n in [name] + attrs.keys() if ':' in n)
        for name in names:
            prefix = name.split(':')[0]
            if prefix not in prefixes:
                raise ValueError('Unkown namespace prefix: %s' % prefix)
        if namespaces:
            namespaces = dict(
                (u'xmlns:%s' % k if k else u'xmlns', v)
                for k, v in namespaces.iteritems()
            )
            attrs = dict(attrs, **namespaces)
        return attrs, prefixes

    def __exit__(self, exc_type, exc_value, exc_tb):
        super(NamespacedGenerator, self).__exit__(exc_type, exc_value, exc_tb)
        self.namespaces.pop()

    def container(self, name, attrs={}, namespaces={}):
        attrs, prefixes = self._process_namespaces(name, attrs, namespaces)
        self.namespaces.append(prefixes)
        return super(NamespacedGenerator, self).container(name, attrs)

    def element(self, name, attrs={}, namespaces={}, text=u''):
        attrs, prefixes = self._process_namespaces(name, attrs, namespaces)
        super(NamespacedGenerator, self).element(name, attrs, text)


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


def xml(file, root, attrs={}, namespaces={}):
    if namespaces:
        return NamespacedGenerator(file, root, attrs, namespaces)
    else:
        return XMLGenerator(file, root, attrs)
