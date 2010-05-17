# -*- coding:utf-8 -*-

class XMLGenerator(object):
    def __init__(self, file, root):
        self.file = file
        self.file.write('<?xml version="1.0" encoding="utf-8"?>')
        self.stack = []
        self.container(root)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.file.write('</%s>' % self.stack.pop())

    def container(self, name):
        self.file.write('<%s>' % name)
        self.stack.append(name)
        return self

    def element(self, name):
        self.file.write('<%s/>' % name)


xml = XMLGenerator
