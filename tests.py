# -*- coding:utf-8 -*-
import unittest
from cStringIO import StringIO
import xml.etree.cElementTree as ET

import elementflow

class XML(unittest.TestCase):
    def test_xml(self):
        buffer = StringIO()
        with elementflow.xml(buffer, u'root') as xml:
            with xml.container(u'container', {u'key': u'"значение"'}):
                xml.text(u'<Текст> контейнера')
                xml.element(u'item')
            xml.element(u'item', text=u'Текст')
        buffer.seek(0)
        tree = ET.parse(buffer)
        buffer = StringIO()
        tree.write(buffer, encoding='utf-8')
        self.assertEqual(
          buffer.getvalue(),
          '<root>'
            '<container key="&quot;значение&quot;">'
              '&lt;Текст&gt; контейнера'
              '<item />'
            '</container>'
            '<item>Текст</item>'
          '</root>'
        )

    def test_non_well_formed_on_exception(self):
        buffer = StringIO()
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

    def test_namespaces(self):
        buffer = StringIO()
        with elementflow.xml(buffer, 'root', namespaces={'': 'urn:n', 'n1': 'urn:n1'}) as xml:
            xml.element('item')
            with xml.container('n2:item', namespaces={'n2': 'urn:n2'}):
                xml.element('item')
                xml.element('n1:item')
        buffer.seek(0)
        tree = ET.parse(buffer)
        root = tree.getroot()
        self.assertEquals(root.tag, '{urn:n}root')
        self.assertNotEqual(root.find('{urn:n}item'), None)
        self.assertNotEqual(root.find('{urn:n2}item/{urn:n}item'), None)
        self.assertNotEqual(root.find('{urn:n2}item/{urn:n1}item'), None)

    def test_bad_namespace(self):
        buffer = StringIO()
        def g():
            with elementflow.xml(buffer, 'n1:root', namespaces={'n': 'urn:n'}) as xml:
                pass
        self.assertRaises(ValueError, g)
        def g():
            with elementflow.xml(buffer, 'n:root', attrs={'n1:k': 'v'}, namespaces={'n': 'urn:n'}) as xml:
                pass
        self.assertRaises(ValueError, g)


if __name__ == '__main__':
    unittest.main()
