import os, tmp, tpg

try:
    import psyco
    psyco.profile(watermark=0.02)
except:
    pass

def tm_filter(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])

    fn = environ['PATH_TRANSLATED']
    os.chdir(os.path.dirname(fn))
    parser = tmp.TMP(fn)

    try:
        r = parser(file(fn).read())
        yield ''.join(map(tmp.filterMeta, r)).strip()

    except tpg.Error, x:
        srcPath = os.path.abspath(parser.fileNames[-1])
        src = file(srcPath).read()

        yield '<html><body><pre>'
        yield 'while processing <b>%s</b>:\n' % srcPath
        yield '%s\n\n' % str(x)

        try:
            line = src.split('\n')[x.line-1]
            yield '%s<span style="background-color: #ff8">%s</span>\n' % (line[:x.column], line[x.column:])
        except:
            pass

        yield '</pre></body></html>'

application = tm_filter

#if __name__ == '__main__':
#    from flup.server.fcgi import WSGIServer
#    WSGIServer(tm_filter, bindAddress=('', 6238)).run()
