# -*- coding:utf-8 -*-
import sys
import xml.etree.cElementTree as ET

import elementflow

def ef_iterator(count, bufsize):
    with elementflow.xml(elementflow.Queue(), 'contacts') as xml:
        for i in range(count):
            with xml.container('person', {'id': unicode(i)}):
                xml.element('name', text='John & Smith')
                xml.element('email', text='john.smith@megacorp.com')
                with xml.container('phones'):
                    xml.element('phone', {'type': 'work'}, text='123456')
                    xml.element('phone', {'type': 'home'}, text='123456')
            if len(xml.file) > bufsize:
                yield xml.file.pop()
    yield xml.file.pop()


def ef_generator(file, count):
    with elementflow.xml(file, 'contacts') as xml:
        for i in range(count):
            with xml.container('person', {'id': unicode(i)}):
                xml.element('name', text='John & Smith')
                xml.element('email', text='john.smith@megacorp.com')
                with xml.container('phones'):
                    xml.element('phone', {'type': 'work'}, text='123456')
                    xml.element('phone', {'type': 'home'}, text='123456')

def et_generator(file, count):
    root = ET.Element('contacts')
    for i in range(count):
        person = ET.SubElement(root, 'person', {'id': unicode(i)})
        ET.SubElement(person, 'name').text = 'John & Smith'
        ET.SubElement(person, 'email').text = 'john.smith@megacorp.com'
        phones = ET.SubElement(person, 'phones')
        ET.SubElement(phones, 'phone', {'type': 'work'}).text = '123456'
        ET.SubElement(phones, 'phone', {'type': 'home'}).text = '123456'
    ET.ElementTree(root).write(file, encoding='utf-8')


if __name__ == '__main__':
    ef_generator(sys.stdout, 40000)
