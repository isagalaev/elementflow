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

if __name__ == '__main__':
    unittest.main()
