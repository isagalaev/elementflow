# -*- coding:utf-8 -*-
'''
Library for generating XML as a stream without first building a tree in memory.

Basic usage::

    import elementflow
    file = open('text.xml', 'w') # can be any  object with .write() method

    with elementflow.xml(file, u'root') as xml:
        xml.element(u'item', attrs={u'key': u'value'}, text=u'text')
        with xml.container(u'container', attrs={u'key': u'value'}):
            xml.text(u'text')
            xml.element(u'subelement', text=u'subelement text')

Usage with namespaces::

    with elementflow.xml(file, 'root', namespaces={'': 'urn:n', 'n1': 'urn:n1'}) as xml:
        xml.element('item')
        with xml.container('container', namespaces={'n2': 'urn:n2'):
            xml.element('n1:subelement')
            xml.element('n2:subelement')

Pretty-printing::

    with elementflow.xml(file, 'root', indent=True):
        # ...

'''
import textwrap
import codecs

def escape(value):
    if '&' not in value and '<' not in value:
        return value
    return value.replace('&', '&amp;').replace('<', '&lt;')

def quoteattr(value):
    if '&' in value or '<' in value or '"' in value:
        value = value.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
    return u'"%s"' % value

def attr_str(attrs):
    if not attrs:
        return u''
    return u''.join([u' %s=%s' % (k, quoteattr(v)) for k, v in attrs.iteritems()])


class XMLGenerator(object):
    '''
    Basic generator without support for namespaces or pretty-printing.

    Constructor accepts:

    - file: an object receiving XML output, anything with .write()
    - root: name of the root element
    - attrs: attributes dict

    Constructor will implicitly open a root container element, you don't need
    to call .container() for it
    '''
    def __init__(self, file, root, attrs={}, **kwargs):
        self.file = codecs.getwriter('utf-8')(file)
        self.file.write(u'<?xml version="1.0" encoding="utf-8"?>')
        self.stack = []
        self.container(root, attrs, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type:
            return
        self.file.write(u'</%s>' % self.stack.pop())

    def container(self, name, attrs={}):
        '''
        Opens a new element containing sub-elements and text nodes.
        Intends to be used under ``with`` statement.
        '''
        self.file.write(u'<%s%s>' % (name, attr_str(attrs)))
        self.stack.append(name)
        return self

    def element(self, name, attrs={}, text=u''):
        '''
        Generates a single element, either empty or with a text contents.
        '''
        if text:
            self.file.write(u'<%s%s>%s</%s>' % (name, attr_str(attrs), escape(text), name))
        else:
            self.file.write(u'<%s%s/>' % (name, attr_str(attrs)))

    def text(self, value):
        '''
        Generates a text in currently open container.
        '''
        self.file.write(escape(value))


class NamespacedGenerator(XMLGenerator):
    '''
    XML generator with support for namespaces.
    '''
    def __init__(self, file, root, attrs={}, namespaces={}):
        self.namespaces = [set(['xml'])]
        super(NamespacedGenerator, self).__init__(file, root, attrs=attrs, namespaces=namespaces)

    def _process_namespaces(self, name, attrs, namespaces):
        prefixes = self.namespaces[-1]
        if namespaces:
            prefixes |= set(namespaces.keys())
        names = [n for n in [name] + attrs.keys() if ':' in n]
        for name in names:
            prefix = name.split(':')[0]
            if prefix not in prefixes:
                raise ValueError('Unkown namespace prefix: %s' % prefix)
        if namespaces:
            namespaces = dict([
                (u'xmlns:%s' % k if k else u'xmlns', v)
                for k, v in namespaces.iteritems()
            ])
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


class IndentingGenerator(NamespacedGenerator):
    '''
    XML generator with pretty-printing.
    '''
    def _fill(self, value, indent=None):
        if indent is None:
            indent = u'  ' * len(self.stack)
        width = max(20, 70 - len(indent))
        tw = textwrap.TextWrapper(width=width, initial_indent=indent, subsequent_indent=indent)
        return u'\n%s' % tw.fill(value)

    def __exit__(self, *args, **kwargs):
        self.file.write(u'\n%s' % (u'  ' * (len(self.stack) - 1)))
        super(IndentingGenerator, self).__exit__(*args, **kwargs)
        if not self.stack:
            self.file.write(u'\n')

    def container(self, *args, **kwargs):
        self.file.write(u'\n%s' % (u'  ' * len(self.stack)))
        return super(IndentingGenerator, self).container(*args, **kwargs)

    def element(self, name, attrs={}, namespaces={}, text=u''):
        indent = u'  ' * len(self.stack)
        self.file.write(u'\n%s' % indent)
        if len(text) > 70:
            fill = self._fill(text, indent + u'  ')
            text = u'%s\n%s' % (fill, indent)
        return super(IndentingGenerator, self).element(name, attrs, namespaces, text)

    def text(self, value):
        super(IndentingGenerator, self).text(self._fill(value))


class Queue(object):
    '''
    In-memory queue for using as a temporary buffer in xml generator.
    '''
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


def xml(file, root, attrs={}, namespaces={}, indent=False):
    '''
    Creates a streaming XML generator.

    Parameters:

    - file: an object receiving XML output, anything with .write()
    - root: name of the root element
    - attrs: attributes dict
    - namespaces: namespaces dict {prefix: uri}, default namespace has prefix ''
    - indent: whether to pretty-print XML, True or False (default)
    '''
    if indent:
        return IndentingGenerator(file, root, attrs, namespaces)
    elif namespaces:
        return NamespacedGenerator(file, root, attrs, namespaces)
    else:
        return XMLGenerator(file, root, attrs)
