# -*- coding:utf-8 -*-
from django import http

import snippets


def index(request):
    return http.HttpResponse('Hello, World!')

def stream(request):
    count = int(request.GET.get('count', 10))
    bufsize = int(request.GET.get('bufsize', 16 * 1024))

    return http.HttpResponse(
        snippets.ef_iterator(count, bufsize),
        content_type='application/xml',
    )

def memory(request):
    count = int(request.GET.get('count', 10))

    response = http.HttpResponse('', content_type='application/xml')
    snippets.ef_generator(response, count)
    return response
