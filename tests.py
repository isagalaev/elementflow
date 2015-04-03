# -*- coding:utf-8 -*-
from __future__ import with_statement

import six
import unittest
from io import BytesIO
import xml.etree.cElementTree as ET

import elementflow


def _bytes(value):
    if six.PY2:
        return value
    return bytes(value, encoding='utf-8')


class XML(unittest.TestCase):
    def test_xml(self):
        buffer = BytesIO()
        with elementflow.xml(buffer, u'root') as xml:
            with xml.container(u'container', {u'key': u'"значение"'}):
                xml.text(u'<Текст> контейнера')
                xml.element(u'item')
            xml.element(u'item', text=u'Текст')
        buffer.seek(0)
        tree = ET.parse(buffer)
        buffer = BytesIO()
        tree.write(buffer, encoding='utf-8')
        self.assertEqual(
            buffer.getvalue(),
            _bytes(
                '<root>'
                '<container key="&quot;значение&quot;">'
                  '&lt;Текст&gt; контейнера'
                  '<item />'
                '</container>'
                '<item>Текст</item>'
                '</root>'
            )
        )


    def test_non_well_formed_on_exception(self):
        buffer = BytesIO()
        try:
            with elementflow.xml(buffer, u'root') as xml:
                xml.text(u'Text')
                raise Exception()
        except:
            pass
        buffer.seek(0)
        # Parsing this buffer should cause a parsing error due to unclosed
        # root element
        self.assertRaises(SyntaxError, lambda: ET.parse(buffer))

    def test_comment(self):
        buffer = BytesIO()
        with elementflow.xml(buffer, u'root') as xml:
            xml.comment(u'comment')
        buffer.seek(0)
        self.assertEqual(
            buffer.getvalue(),
            _bytes('<?xml version="1.0" encoding="utf-8"?><root><!--comment--></root>')
        )

    def test_comment_with_double_hyphen(self):
        buffer = BytesIO()
        with elementflow.xml(buffer, u'root') as xml:
            xml.comment(u'--comm-->ent--')
        buffer.seek(0)
        self.assertEqual(
            buffer.getvalue(),
            _bytes('<?xml version="1.0" encoding="utf-8"?><root><!--comm>ent--></root>')
        )

    def test_namespaces(self):
        buffer = BytesIO()
        with elementflow.xml(buffer, 'root', namespaces={'': 'urn:n', 'n1': 'urn:n1'}) as xml:
            xml.element('item')
            with xml.container('n2:item', namespaces={'n2': 'urn:n2'}):
                xml.element('item')
                xml.element('n1:item')
        buffer.seek(0)
        tree = ET.parse(buffer)
        root = tree.getroot()
        self.assertEqual(root.tag, '{urn:n}root')
        self.assertNotEqual(root.find('{urn:n}item'), None)
        self.assertNotEqual(root.find('{urn:n2}item/{urn:n}item'), None)
        self.assertNotEqual(root.find('{urn:n2}item/{urn:n1}item'), None)

    def test_bad_namespace(self):
        buffer = BytesIO()
        def g():
            with elementflow.xml(buffer, 'n1:root', namespaces={'n': 'urn:n'}) as xml:
                pass
        self.assertRaises(ValueError, g)
        def g():
            with elementflow.xml(buffer, 'n:root', attrs={'n1:k': 'v'}, namespaces={'n': 'urn:n'}) as xml:
                pass
        self.assertRaises(ValueError, g)

    def test_map(self):
        data = [(1, u'One'), (2, u'Two'), (3, u'Three')]
        buffer = BytesIO()
        with elementflow.xml(buffer, u'root') as xml:
            xml.map(lambda item: (
                'item',
                {'key': str(item[0])},
                item[1],
            ), data)
            xml.map(lambda item: (item[1],), data)
        buffer.seek(0)
        tree = ET.parse(buffer)
        buffer = BytesIO()
        tree.write(buffer, encoding='utf-8')
        self.assertEqual(
          buffer.getvalue(),
          _bytes(
              '<root>'
                '<item key="1">One</item>'
                '<item key="2">Two</item>'
                '<item key="3">Three</item>'
                '<One /><Two /><Three />'
              '</root>'
          )
        )

    def test_indent(self):
        buffer = BytesIO()
        with elementflow.xml(buffer, u'root', indent = True) as xml:
            with xml.container(u'a'):
                xml.element(u'b', text = ''.join(['blah '] * 20))
                xml.comment(u' '.join(['comment'] * 20))
        buffer.seek(0)
        self.assertEqual(
            buffer.getvalue(),
            _bytes(
"""<?xml version="1.0" encoding="utf-8"?>
<root>
  <a>
    <b>
      blah blah blah blah blah blah blah blah blah blah blah
      blah blah blah blah blah blah blah blah blah
    </b>
    <!--
      comment comment comment comment comment comment comment
      comment comment comment comment comment comment comment
      comment comment comment comment comment comment
    -->
  </a>
</root>
"""))

    def test_indent_nowrap(self):
        buffer = BytesIO()
        with elementflow.xml(buffer, u'root', indent = True, text_wrap = False) as xml:
            with xml.container(u'a'):
                xml.element(u'b', text = ''.join(['blah '] * 20))
                xml.comment(u' '.join(['comment'] * 20))
        buffer.seek(0)
        self.assertEqual(
            buffer.getvalue(),
            _bytes(
"""<?xml version="1.0" encoding="utf-8"?>
<root>
  <a>
    <b>blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah </b>
    <!--comment comment comment comment comment comment comment comment comment comment comment comment comment comment comment comment comment comment comment comment-->
  </a>
</root>
"""))



if __name__ == '__main__':
    unittest.main()
