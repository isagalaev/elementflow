# -*- coding:utf-8 -*-
import unittest
from cStringIO import StringIO
import xml.etree.cElementTree as ET

import elementflow

class XML(unittest.TestCase):
    def test_xml(self):
        buffer = StringIO()
        with elementflow.xml(buffer, 'root') as xml:
            with xml.container('container'):
                xml.element('item')
            xml.element('item')
        buffer.seek(0)
        tree = ET.parse(buffer)
        buffer = StringIO()
        tree.write(buffer, encoding='utf-8')
        self.assertEqual(
          buffer.getvalue(),
          '<root>'
            '<container>'
              '<item />'
            '</container>'
            '<item />'
          '</root>'
        )

if __name__ == '__main__':
    unittest.main()
