from mod_python import apache
import os, tmp, tpg

try:
    import psyco
    psyco.profile(watermark=0.02)
except:
    pass

def handler(req):
    req.content_type = 'text/html; charset=UTF-8'

    os.chdir(os.path.dirname(req.filename))
    parser = tmp.TMP(req.filename)

    try:
        r = parser(file(req.filename).read())
        req.write(''.join(map(tmp.filterMeta, r)).strip())

    except tpg.Error, x:
        srcPath = os.path.abspath(parser.fileNames[-1])
        src = file(srcPath).read()

        req.write('<html><body><pre>')
        req.write('while processing <b>%s</b>:\n' % srcPath)
        req.write('%s\n\n' % str(x))

        try:
            line = src.split('\n')[x.line-1]
            req.write('%s<span style="background-color: #ff8">%s</span>\n' % (line[:x.column], line[x.column:]))
        except:
            pass

        req.write('</pre></body></html>')

    return apache.OK
