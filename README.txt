===========
elementflow
===========

Elementflow is a Python library for generating XML as a stream. Some existing
XML producing libraries (like ElementTree, lxml) build a whole XML tree in
memory and then serialize it. It might be inefficient for moderately large XML
payloads (think of a content-oriented Web service producing lots of XML data
output). Python's built-in xml.sax.saxutils.XMLGenerator is very low-level and
requires closing elements by hand.

Also, most XML libraries, to be honest, suck when dealing with namespaces.

Usage
=====

Basic XML generation::

    import elementflow
    file = open('text.xml', 'w') # can be any  object with .write() method

    with elementflow.xml(file, u'root') as xml:
        xml.element(u'item', attrs={u'key': u'value'}, text=u'text')
        with xml.container(u'container', attrs={u'key': u'value'}):
            xml.text(u'text')
            xml.element(u'subelement', text=u'subelement text')

Using ``with`` is required to properly close container elements. The library
expects unicode strings on input and produces utf-8 encoded output (you *may*
omit those "u"s for purely ASCII strings if you want to, Python will convert
the, automatically).

XML with namespaces::

    with elementflow.xml(file, 'root', namespaces={'': 'urn:n', 'n1': 'urn:n1'}) as xml:
        xml.element('item')
        with xml.container('container', namespaces={'n2': 'urn:n2'):
            xml.element('n1:subelement')
            xml.element('n2:subelement')

Elements with namespaces are defined using prefixes. You can define namespaces
at the root level and for any container. The library will check for namespace
prefixes that wasn't defined beforehand and will raise ValueError in that case.

Pretty-printing is also supported::

    with elementflow.xml(file, 'root', indent=True):
        # ...

In some cases it's more convenient to have such XML producer as a Python
iterator. This is easily done by wrapping XML generation code into a generator
function::

    def g():
        xml = elementflow.xml(elementflow.Queue(), 'root')
        with xml:
            for item in collection:
                xml.element(...)
            yield xml.file.pop()
        yield xml.file.pop()

``elementflow.Queue()`` is a temporary buffer that accepts data from an XML
generator and is cleared upon calling .pop() on it. You also might want to
yield data from the iterator only when this buffer reaches a certain size::

    if len(xml.file) > BUFSIZE:
        yield xml.file.pop()
