# -*- coding:utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.web

import snippets


class HelloWorldHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello, World!')


class MemoryHandler(tornado.web.RequestHandler):
    def get(self):
        count = int(self.get_argument('count', 10))
        self.set_header('Content-Type', 'application/xml')

        snippets.ef_generator(self, count)



class StreamingHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        count = int(self.get_argument('count', 10))
        bufsize = int(self.get_argument('bufsize', 16 * 1024))

        self.iterator = snippets.ef_iterator(count, bufsize)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.set_header('Content-Type', 'application/xml')
        self.next()

    def next(self):
        try:
            self.write(self.iterator.next())
            self.flush()
            self.ioloop.add_callback(self.next)
        except StopIteration:
            self.finish()


application = tornado.web.Application([
    (r"/", HelloWorldHandler),
    (r"/stream", StreamingHandler),
    (r"/memory", MemoryHandler),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    print 'Running...'
    tornado.ioloop.IOLoop.instance().start()
