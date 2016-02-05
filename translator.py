# -*- coding: utf-8 -*-
"""
 tmp - tiberius' Text Markup Processor
-----------------------------------------------------------------------
Comment   : Example markup file (for own use in book translation work)
Version   : $Id: translator.py 87 2006-05-20 10:04:07Z tiberius $
Copyright : (C) 2005 by Tiberius Teng <s9256043@mail.cs.nchu.edu.tw>
-----------------------------------------------------------------------
 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or any
 later version.
-----------------------------------------------------------------------
"""
import cPickle, os, re, string, time, tmp, tpg, urllib
import translator_config
import pygments, pygments.lexers, pygments.formatters

from copy import copy as _copy
from pprint import pprint

code_formatter = pygments.formatters.HtmlFormatter(style='default', nobackground=True)
code_start_tag = re.compile('^<div.*?><pre>')
code_end_tag = re.compile('</pre></div>$')

class EnvironmentError(tpg.Error):
    pass

_html_ch = {'<': '&lt;', '>': '&gt;', '"': '&quot;'}

## Simple replacements
########################
br = '<br />'

dash = '&mdash;'
etc = '&hellip;'
integral = '&int;'

ve = '&#8942;'

_and = '&and;'
_or = '&or;'
_not = '&not;'

for j in [
        ['cent', 'euro', 'yen'],
        ['copy', 'reg', 'trade'],
        ['mdash', 'ndash'],
        ['deg', 'permil', 'pound'],
        ['gt', 'lt'],
        ['lceil', 'rceil', 'lfloor', 'rfloor'],
        ['larr', 'uarr', 'rarr', 'darr', 'harr', 'crarr'],
        ['lArr', 'uArr', 'rArr', 'dArr', 'hArr'],
        # http://www.blooberry.com/indexdot/html/tagpages/entities/math.htm
        ['ang', 'cap', 'cup', 'divide', 'empty', 'equiv', 'exist', 'forall',
        # ∠     ∩     ∪     ÷        ∅        ≡       ∃       ∀
         'ge', 'infin', 'isin', 'le', 'nabla', 'ne', 'ni', 'notin',
        # ≥    ∞       ∈      ≤    ∇       ≠    ∋    ∉
         'oplus', 'otimes', 'part', 'perp', 'prod', 'subs', 'sube', 'sum',
        # ⊕       ⊗         ∂      ⊥      ∏      ⊂     ⊆      ∑
         'sups', 'supe', 'times'],
        # ⊃     ⊇      
        ['pi', 'Sigma'],
        #
        ['mu'],
        ]:

    for k in j:
        locals()[k] = '&%s;' % k

clear = '<div style="clear: both;">&nbsp;</div>'

## Hardcoded strings
######################
_styleSheet = """\
/** Column types **/

.col-caution {
    background: #ffd8d9;
}

.col-column {
    background: #d8d8ff;
}

.col-note {
    background: #d8f6ff;
}

.col-exp {
    background: #d8e6ff;
}

.col-tip {
    background: #fffdd8;
}

.col-transnote {
    background: #d9f7d2;
}

/** Box types **/

.comment {
    background: #eee;
    border-color: #aaa;
}

.editor {
    background: #fdd;
    border-color: red;
    color: red;
    margin: 1em 0 !important;
}

.footnote {
    clear: right;
    display: inline;
    float: right;
    font-size: 0.8em;
    margin: 1em !important;
    width: 25em;
}

.pre {
    /*
    background: #ddf;
    border-color: #ccf;
    */
    background: #eee;
    border-color: #888;
}

/** Inline marking styles **/

.orange {
    color: #f60;
}

.redmark {
    color: #f00;
    font-weight: bold;
}

.reset {
    font-weight: normal;
}

.small {
    font-size: 80%;
    color: #009;
}

.smallcaps {
    font-variant: small-caps;
    color: #900;
}

.ybg {
    background: #ff9;
}

a:link, a:visited {
    color: #36a;
    text-decoration: none;
    cursor: pointer;
}

a:active, a:hover {
    color: #73b;
    text-decoration: underline;
}

a.fnanchor {
    font-family: 'Arial', sans-serif;
    font-size: 0.8em;
    vertical-align: super;
    color: red !important;
}

div.footnote a.fnitem {
    color: red !important;
    font-weight: bold;
    font-family: 'Arial', sans-serif;
}

ins {background: #bfb}
del {background: #fcc}
ins,del {text-decoration: none}

blockquote {
    border: 1px solid #88f;
    margin: 1.5em;
    padding: 10px;
}

body:lang(zh-tw) {font-family: 'Palatino Linotype', 'Georgia', '新細明體', 'PMingLiU', serif;}
body:lang(ja)    {font-family: 'Palatino Linotype', 'Georgia', 'メイリオ', 'Meiryo', 'ＭＳ Ｐ明朝', 'MS PMincho', serif;}

body {
    font-family: 'Georgia', serif; /* IE does not support :lang() */
    background: #fff;
    line-height: 1.3;
    margin: 0;
    padding: 0;
}

pre, code, dl#pageList a {
    font-family: 'Consolas', 'Bitstream Vera Sans Mono', 'Monaco', 'Andale Mono', 'Courier New', monospace;
    font-size: 0.95em;
    padding: 0 0.2em;

    white-space: pre-wrap;                  /* css-3 */
    white-space: -moz-pre-wrap !important;  /* Mozilla, since 1999 */
    white-space: -pre-wrap;                 /* Opera 4-6 */
    white-space: -o-pre-wrap;               /* Opera 7 */
    word-wrap: break-word;                  /* Internet Explorer 5.5+ */
}

dl#pageList a {
    white-space: nowrap !important;
}

code {
    color: #741;
}

th.col code {
    color: #fff;
}

div.body {
    background: #fff;
    border-left: 15px solid #ffa;
    padding: 10px 10px 10px 20px;
    text-autospace: ideograph-alpha;
}

div.boxHead, table caption {
    clear: right;
    background: #8de;
    color: #002266;
    margin-top: 1em;
    border-left: 7px solid #3388aa;
    padding: 8px 8px 8px 10px;
    letter-spacing: 1px;
    white-space: nowrap;
}

div.boxHead + pre {
    margin-top: 0;
}

div.box, pre {
    border-width: 1px;
    border-style: solid;
    clear: right;
    margin-bottom: 0;

    padding: 10px;
}

div.box p, td p {
    text-indent: 0;
}

blockquote > *:first-child,
div.box > *:first-child,
div.column > *:first-child,
div.listItem > *:first-child,
table td > *:first-child {
    margin-top: 0; 
}

blockquote > *:last-child,
div.box > *:last-child,
div.column > *:last-child,
div.listItem > *:last-child,
table td > *:last-child {
    margin-bottom: 0; 
}

div.box div.heading {
    margin-left: 32px;
    margin-top: 3px;
}

div.box span.type {
    font-family: 'Impact', serif;
    font-size: 1.2em;
}

div.box span.desc {
    color: #722;
    font-size: 1.2em;
    font-weight: bold;
}

div.columnbox {
    border-color: #aaa;
    margin-top: 1em;
    margin-bottom: 1em;
}

div.footnote p {
    margin: 0;
}

div.footer {
    clear: right;
    margin: 0px;
    padding: 4px;
    text-align: right;
    color: #555;
    border-top: 3px double #aaa;
    background: #ddd;
    font-size: 0.8em;
    font-family: 'Georgia', serif;
}

div.listItem {
    border-bottom: 1px dashed #aaa;
    padding-bottom: 0.5em;
}

div.listItem p:last-child {
    margin-bottom: 0;
}

div.metaInfo {
    padding: 10px;
    border-bottom: 1px solid #aaa;
    border-top: 1px solid #aaa;
    background: #ddd;
}

div.pageSeparator {
/*  border-top: 1px solid #479;
    clear: both; */
    margin: 1em 0 1em 0;
}

div.srcPage {
    background: #dff;
    border: 1px solid #479;
    clear: both;
    color: #479;
    font-family: 'Trebuchet MS', sans-serif;
    font-size: 0.8em;
    margin-left: -42px;
    padding: 1px;
    text-align: center;
    width: 80px;
}

dl {
    margin-left: 20px;
}

dl dt {
    font-weight: bold;
}

dl dt.normal-weight {
    font-weight: normal;
}

dl dd {
    margin-bottom: 1em;
}

dl dd p:first-child {
    margin-top: 0;
}

h1,h2,h3,h4,h5,h6,div.box span.desc {
    /* IE does not support :lang() */
    font-family: 'メイリオ', 'Meiryo', 'Microsoft JhengHei', 'DFKai-SB', sans-serif;
}

h1,h2,h3,h4,h5,h6 {
    color: #3E424E;
}

h1:lang(zh-tw),
h2:lang(zh-tw),
h3:lang(zh-tw),
h4:lang(zh-tw),
h5:lang(zh-tw),
h6:lang(zh-tw),
div.box span.desc:lang(zh-tw) {
    font-family: 'Trebuchet MS', '微軟正黑體', 'Microsoft JhengHei', '標楷體', 'DFKai-SB';
}

h1:lang(ja),
h2:lang(ja),
h3:lang(ja),
h4:lang(ja),
h5:lang(ja),
h6:lang(ja),
div.box span.desc:lang(ja) {
    font-family: 'Trebuchet MS', 'メイリオ', 'Meiryo', 'ＭＳ Ｐゴシック', 'MS PGothic';
}

h1,h2,h3,h4 {
    font-weight: bold;
}

h1,h2,h3 {
    clear: both;
}

h1 {
    border-bottom: 2px solid #00a;
    border-left: 10px solid #00a;
    font-size: 2.2em;
    margin-top: 1.5em;
    margin-right: -10px; 
    margin-left: -30px;
    padding: 6px 16px;
}

h2 {
    border-bottom: 3px double #00f;
    font-size: 1.9em;
    margin-top: 1.3em;
    margin-left: -20px;
    margin-right: -10px;
    padding: 3px 8px;
}

h3 {
    border-left: 8px solid #55f;
    border-bottom: 2px solid #55f;
    font-size: 1.7em;
    margin: 1em 0 0.6em -12px;
    padding: 10px 15px 5px 15px;
}

h4 {
    border-left: 6px double #495F9D;
    border-bottom: 1px solid #B9C0D5;
    font-size: 1.5em; font-weight: normal;
    margin: 1em 0 0.6em -10px;
    padding: 3px 0.6em;
}

h5 {
    border-bottom: 1px dashed #55f;
    border-left: 4px solid #bcf;
    margin: 1em 1em 0.6em -2px;
    padding: 2px 0.4em;
    font-size: 1.4em; font-weight: normal;
}

h6 {
    border-left: 3px solid #495F9D;
    font-size: 1.2em;
    font-weight: normal;
    padding: 1px 0.5em;
    margin: 1em 0 0.6em 0;
}

img {
    /* for IE PNG transparency */
    behavior: url(tmp/pngHack.htc);

    border: 0;
    margin: 10px;
    vertical-align: middle;
}

p img,
li img
{
    margin: 0;
}

img.column {
    float: left;
    display: inline;
    border: 0;
    margin: 0 5px 5px 0;
    padding: 0;
    vertical-align: baseline;
}

img.mimetex {
    background: #ffc;
    padding: 2px !important;
    margin: 0 !important;
}

li {
    /* see div.listItem definition. F**king IE CSS support! */
    padding-top: 0.5em;
}

p {
    padding: 0;
    /* text-indent: 2em; */
}

h1 + p,
h2 + p,
h3 + p,
h4 + p,
h5 + p,
h6 + p,
div.footnote + p {
    text-indent: 0;
}

p.label {
    margin-right: 20% !important;
    margin-left: 44px !important;
    text-indent: 0px;
    padding: 2px;
}

li p {
    text-indent: 0;
}

#metaInfo {
    display: none;
}

#metaInfo li,
.compact li {
    padding: 0;
    border: none;
}

pre {
    clear: right;
    font-size: 0.95em;
    /* see div.box */
}

span.control {
    background: #fec;
    border: 1px solid #fa4;
    color: #d82;
    cursor: pointer;
    font-family: 'Arial', sans-serif;
    font-size: 0.7em;
    margin-left: 15px;
    padding: 3px;
    text-decoration: underline;
}

span.headAnchor {
    color: #722;
    padding-right: 0.5em;
}

kbd.keyboard {
    /* background-color: #eee; */
    background-color: #F9F9F9;
    background-image: -moz-linear-gradient(top, #EEE, #F9F9F9, #EEE);
    background-image: -ms-linear-gradient(top, #EEE, #F9F9F9, #EEE);
    background-image: -o-linear-gradient(top, #EEE, #F9F9F9, #EEE);
    background-image: -webkit-linear-gradient(top, #EEE, #F9F9F9, #EEE);
    background-image: linear-gradient(top, #EEE, #F9F9F9, #EEE);

    border: 1px solid;
    border-bottom-width: 2px;
    border-color: #ccc #555 #555 #ccc;
    -moz-border-radius: 3px;
    -webkit-border-radius: 3px;
    border-radius: 3px;
    font-family: 'Arial', sans-serif;
    padding: 1px 3px;

    -moz-box-shadow: 1px 2px 2px #ddd;
    -webkit-box-shadow: 1px 2px 2px #DDD;
    box-shadow: 1px 2px 2px #DDD;
}

span.label {
    padding: 3px;
    margin: 3px 10px 3px 6px;
    font-size: 0.7em;
    vertical-align: middle;
    font-family: 'Arial', sans-serif;
}

span.url {
    background-color: #6BE593;
    border: 1px solid #0E7931;
    color: #075220;
    margin-left: -40px;
}

table {
    border-collapse: collapse;
    margin-top: 1em;
    margin-bottom: 1em;
}

table caption {
    margin: 0;
    text-align: left;
}

table tr {
    background: #fff;
}

table td, table th {
    padding: 8px 10px;
    vertical-align: top;
    border-bottom: 1px solid #999;
    border-right: 1px solid #999;
}

table td {
    background: #eee;
}

table th {
    font-weight: bold;
}

table th.col {
    background: #38a;
    color: #fff;
}

table th.row {
    background: #ccc;
    text-align: left;
}

/*
u {
    background: #eff;
}
*/

@media print {
    body, table {
        font-size: 10pt;
    }

    div.body {
        margin: 0 0 0 10px;
        border: 0;
    }

    div.metaInfo {
        display: none;
    }

    div.srcPage {
        margin-left: -25px;
        width: 1.5cm;
        padding: 1mm;
        text-align: center;
        border: 1px solid #888888;
    }

    h1, h2, h3, h4, h5, h6, div.boxHead, div.srcPage {
        page-break-after: avoid;
    }
    
    div.footer {
        text-align: center;
    }
}
"""

_pageHead = """\
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="" lang="" dir="ltr">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<title></title>
<style type="text/css"></style>
<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML"></script>
<script type="text/javascript">
MathJax.Hub.Config({
  TeX: {
    noErrors: { disabled: true }
  }
});
</script>
</head>
<body onload="javascript:hasIE_hideAndShow();">
<script type="text/javascript" src="tmp/iedetect.js"></script>
<script type="text/javascript">
function toggle() {
    var obj = document.getElementById("metaInfo");
    obj.style.display = (obj.style.display == 'none') ? 'block' : 'none';
}
</script>
"""

_control = """\
<span class="control" onclick="toggle();"  style="cursor: pointer;">Show/Hide Metadata</span>
"""

_suggestFirefox = """\
<div id="hasIE_level1" style="display: none;">
<div style="background: #ffb; padding: 20px; font-weight: bold;">
本頁有許多舊版 Internet Explorer 無法正確顯示的排版效果，如列表標題、縮排、首段上方留白、旁註等等<br />
因此建議您改用 <a href="http://www.moztw.org/">Mozilla Firefox</a>, <a href="http://www.opera.com/">Opera</a> 或<a href="http://www.microsoft.com/windows/ie/downloads/default.mspx">升級 Internet Explorer</a> 瀏覽本頁，如此可得最正確的結果。
</div>
</div>
"""

_pageTail = """\
<div class="footer">
made with Tiberius' <a href="#">Text Markup Processor</a>, powered by <a href="http://www.python.org/">Python</a><br />
using <i>Translator</i> markup pack - style sheet original designed by <a href="http://d.hatena.ne.jp/buttw/">but</a><br />
auto code syntax highlighting with <a href="http://pygments.pocoo.org/">Pygments</a>.
</div>
</body>
</html>
"""

## Processing state variables
###############################

# body token type:
#    0: not processed
#    1: processed (don't need to escape)
#    2: xref link
#    3: header info

pageEnv = {}

_tableCurCol = 0
_tableCurRow = 0
_tableHeadRow = -1

pageIndex = []
_firstPage = 1

# headerIndex item format: [Title, Level, AnchorName, NumberInFile, [childHeaders]]
headerIndex = []
headerNo = 0
headerTag = {}

mathCount = 0

_fnCount = 1
_fnSerial = 0
_fnItems = {}

_defaultSyntax = ''

warning = []
warnlink = 0

proj = {}

def reset():
    global pageEnv
    global _tableCurCol, _tableCurRow, _tableHeadRow
    global pageIndex, _firstPage
    global headerIndex, headerNo, headerTag
    global mathCount
    global _fnCount, _fnItems, _fnSerial
    global warning, warnlink
    global proj

    pageEnv = {
        'lang': '',
        'title': '',
        'toc': False,
        'pagelist': False,
        'projFile': None
    }

    _tableCurCol = 0
    _tableCurRow = 0
    _tableHeadRow = -1

    pageIndex = []
    _firstPage = 1

    headerIndex = []
    headerNo = 0
    headerTag = {}

    mathCount = 0

    _fnCount = 1
    _fnSerial = 0
    _fnItems = {}

    _defaultSyntax = ''

    warning = []
    warnlink = 0

    proj = {}

## Internal functions
#######################

def _htmlEscape(o):
    o = o.replace('&', '&amp;')
    for (k, v) in _html_ch.items():
        o = o.replace(k, v)
    return o

def _joinBody(b):
    return ''.join(map(lambda x: x[1], b))

def _procBody(b, f):
    return ''.join(map(lambda x: (x[0] and [x[1]] or [f(x[1])])[0] , b))

## Page Configuration & Environment
#####################################

def set(args, body, **kw):
    "(str,)"
    global pageEnv
    pageEnv[args[0]] = _joinBody(body)

# shortcuts for setting commonly used variables

def lang(body, **kw):
    "()"
    global pageEnv
    pageEnv['lang'] = _joinBody(body)

def title(body, **kw):
    "()"
    global pageEnv
    pageEnv['title'] = _joinBody(body)

def filetoc(**kw):
    "()"
    global pageEnv
    pageEnv['toc'] = True

def pagelist(**kw):
    "()"
    global pageEnv
    pageEnv['pagelist'] = True

def project(body, fileName, line, column, **kw):
    "()"
    global headerIndex, pageEnv, pageIndex, proj
    
    
    pageEnv['projFile'] = os.path.join(os.path.dirname(fileName), _joinBody(body) + '.tpd')
    fileName = os.path.basename(fileName)

    if os.path.exists(pageEnv['projFile']):
        try:
            proj = cPickle.load(file(pageEnv['projFile'], 'rb'))
        except:
            raise EnvironmentError((line, column), 'Project file "%s" is not valid, please change project name or delete the file"' % pageEnv['projFile'])

        if fileName in proj:
            del proj[fileName]

    proj[fileName] = {'toc': headerIndex, 'page': pageIndex, 'index': []}

## Global project data construction
#####################################

def _flattenHeaders(l, h):
    l += [[h[0], h[1], h[2], h[3]]]
    for x in h[4]:
        _flattenHeaders(l, x)
    return l
    
def _buildProject():
    headers = {}; pages = {}; indexes = {}

    for fileName in proj:
        # convert file extension once and for all
        htmName = fileName[:fileName.rfind('.')] + '.htm'
        
        # build headers table
        f = []
        for x in proj[fileName]['toc']:
            f += _flattenHeaders([], x)
        for x in f:
            headers[x[2]] = [x[0], htmName, x[3]]

        # build pages table
        f = []
        for x in proj[fileName]['page']:
            pages[x] = htmName

    return headers, pages, indexes

## TOC Pages Helper
######################
def _traverseTocHeader(fileName, header):
    ret = []
    if translator_config.snapshot:
        fileName = fileName.replace('.tm', '.htm')
    for h in header:
        ret += ['<li><a href="%s#header%s">' % (fileName, h[3])]
        if h[2]: ret += ['%s ' % h[2]]
        ret += ['%s</a>' % h[0]]
        
        if h[4]:
            ret += ['<ul>\n%s</ul>\n' % _traverseTocHeader(fileName, h[4])]

        ret += ['</li>\n']

    return ''.join(ret)

def tocfiles(args, body, parser, **kw):
    "()"
    global pageEnv, pageIndex, headerIndex

    # cache format:
    # {'fileName': [lastModified, title, headerIndex] }
    cacheFile = 'index.pickle'
    cache = {}
    cacheModified = 0
    cacheUpdated = 0
    
    fileNames = body[0][1].strip().split('\n')
    ret = []

    # Try to load cache
    if os.path.exists(cacheFile):
        try:
            cache = cPickle.load(file(cacheFile, 'rb'))
            cacheModified = os.stat(cacheFile).st_mtime
        except:
            os.unlink(cacheFile)

    _pageEnv = pageEnv
    
    # pass 1: check for file changes, parse for headers

    for fn in fileNames:
        if not os.path.exists(fn):
            raise EnvironmentError((line, column), 'File %s not found' % fn)

        mtime = os.stat(fn).st_mtime
        
        # rescan the file if modified
        
        if (fn not in cache) or (cache[fn][0] != mtime):
            iparser = tmp.TMP(fn)

            parser.fileNames.append(fn)
            r = iparser(file(fn).read())
            toc = map(lambda x: x[1], filter(lambda x: x[0] == 3, r))[0]
            parser.fileNames.pop()

            cache[fn] = [mtime, pageEnv['title'], toc]
            cacheModified = time.time()
            cacheUpdated = 1

    if cacheUpdated:
        cPickle.dump(cache, file(cacheFile, 'wb'), 2)
    
    pageEnv = _pageEnv
    pageIndex = []
    headerIndex = []

    # pass 2: generate contents
    
    ret += [[1, '<p>cache generated on: %s</p>' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cacheModified))]]
    
    for fn in fileNames:
        ret += _headerWrapper(1)(args=('',), body=[[1, cache[fn][1].split(' : ')[0]]], line='(generated)')
        if cache[fn][1]:
            ret += [[1, '<ul class="compact">%s</ul>\n' % _traverseTocHeader(fn, cache[fn][2])]]

    return ret

## Complex markups
###################

def _makeFootnotes(fn):
    global _fnItems
    
    s = 0
    ret = ['<div class="box comment footnote">']
    for f in fn:
        if not s:
            s = 1
        else:
            ret += ['<br />']
        ret += ['<p><a name="fn%s" /><a href="#fa%s" class="fnitem">*%s</a>:' % (_fnItems[f][0], _fnItems[f][0], _fnItems[f][0]), _fnItems[f][1], '</p>']
        del _fnItems[f]
    ret += ['</div>']
    
    return ret
    
def body(args, body, fileName, line, column, **kw):
    "()"
    global pageEnv, pageIndex, headerIndex
    global _fnItems
    global warning, warnlink

    ret = ''
    fileName = os.path.basename(fileName)
    fileName = fileName[:fileName.rfind('.')] + '.htm'

    if proj:
        from cPickle import dump
        dump(proj, file(pageEnv['projFile'], 'wb'), 2)

        headers, pages, indexes = _buildProject()

        for i in body:
            # make xref links
            if i[0] == 2:
                h = headers.get(i[1][1])
                if h:
                    if h[1] == fileName: h[1] = ''
                    i[1] = '<a href="%s#header%s">%s</a>' % (h[1], h[2], h[0])
                else:
                    warning += ['Line <a href="#warn%d">%s</a>: link tag <b>%s</b> unresolved' % (warnlink, i[1][0], i[1][1])]
                    i[1] = '<b id="warn%d">[ Unresolved link: %s ]</b>' % (warnlink, i[1][1])
                    warnlink += 1

    # check mandatory page configurations

    if not pageEnv['lang']:
        raise EnvironmentError((line, column), 'Document language is not set, please set it with \\lang markup')
    
    if not pageEnv['title']:
        raise EnvironmentError((line, column), 'Document title is not set, please set it with \\title markup')
    
    # <li> bottom border hack
    #=========================
    # when encountering <li id="inner"><div class="listItem"> ... </div></li> </ul> </div></li>
    # i.e. the last <li> of a <ul>, <ol> that enclosed in another <li>
    # then modify the inner <li> so that it doesn't have bottom border

    li = re.compile('<li( value="(?P<value>.*?)")?><div class="listItem">')
    for i in xrange(len(body)):
        r = li.match(body[i][1])
        if r:
            # endtag should be at the tag second next to </div></li>
            endtag = i + body[i][2] + 2

            # skipping whitespace nodes, ensure there's still content
            while body[endtag:endtag+1]:
                if body[endtag][1].strip(): break
                else:
                    endtag += 1
            if not body[endtag:endtag+1]: continue

            if (body[endtag][1] == '</ul>' or body[endtag][1] == '</ol>'):
                # skipping whitespace nodes again, also ensure there's still content
                while body[endtag+1:endtag+2]:
                    if body[endtag+1][1].strip(): break
                    else:
                        endtag += 1
                if not body[endtag+1:endtag+2]: continue

                if body[endtag+1][1] == '</div></li>':
                    value = r.groupdict()['value']
                    if value:
                        value = ' value="%d"' % value
                    else:
                        value = ''
                    body[i] = [1, '<li%s><div class="listitem" style="border: 0;">' % value]

    # join all content into a string
    body = _procBody(body, _htmlEscape)
    
    # convert newlines into <br /> and <p> ... </p>
    # but avoids <pre> section
    sect = re.split('(<[/]?pre.*?>)', body)
    fn = []
    ret = []
    pre = 0
    for x in sect:
        if x[:4] == '<pre':
            pre = 1
        elif x == '</pre>':
            pre = 0

        if pre:
            # catch footnote anchors in content
            for z in re.findall('<!-- footnote (\\d+) -->', x):
                fn += [int(z)]

            ret += [x]

        else:
            #buf = re.sub(r'(?<![>])\n(?!\n)', '', x.replace('\r\n', '\n').strip()).split('\n')

            buf = x.replace('\r\n', '\n').strip().decode('utf-8')
            #file('c:/test1.txt', 'wb').write(buf.encode('utf-8'))
            buf = re.sub(ur'(?<=\w)\n(?=\w)', ' ', buf) # eng-eng
            buf = re.sub(ur'(?<=[\u3000-\u303f\uff01-\uff60\uffe0-\uffe6])\n(?=\w)', '', buf) # eng-punc
            buf = re.sub(ur'(?<=\w)\n(?=[\u3000-\u303f\uff01-\uff60\uffe0-\uffe6])', '', buf) # punc-eng
            buf = re.sub(ur'(?<=[\u3000-\u303f\uff01-\uff60\uffe0-\uffe6])\n(?=[\u3400-\u9fff])', '', buf) # punc-chi
            buf = re.sub(ur'(?<=[\u3400-\u9fff])\n(?=[\u3000-\u303f\uff01-\uff60\uffe0-\uffe6])', '', buf) # chi-punc
            buf = re.sub(ur'(?<=[\u3400-\u9fff])\n(?=[\u3000-\uffff])', '', buf) # chi-chi
            buf = re.sub(ur'(?<=[\u3400-\u9fff])\n(?![\n\u3000-\uffff])', ' ', buf) # chi-eng
            #file('c:/test2.txt', 'wb').write(buf.encode('utf-8'))
            buf = re.sub(ur'(?<![>\n\u3000-\uffff])\n(?=[\u3000-\uffff])', ' ', buf) # eng-chi
            #file('c:/test3.txt', 'wb').write(buf.encode('utf-8'))
            buf = re.sub(ur'(?<![>])\n(?!\n)', '', buf)
            #file('c:/test4.txt', 'wb').write(buf.encode('utf-8'))
            buf = buf.split('\n')
            buf = [x.encode('utf-8') for x in buf]

            for y in buf:
                if not y:
                    ret += ['<br />']
                else:
                    # catch footnote anchors in content
                    for z in re.findall('<!-- footnote (\\d+) -->', y):
                        fn += [int(z)]

                    if (y[0] != '<' and y[-1] != '>') or (y[0:3] in ['<co', '<b>', '<i>', '<sp', '<u>']):
                        # put footnotes at end of paragraph
                        if fn:
                            ret += _makeFootnotes(fn)
                        fn = []
                        
                        ret += ['<p>', y, '</p>']
                    else:
                        ret += [y]

    # dump all orphaned footnotes at last
    if _fnItems: ret += _makeFootnotes(_fnItems.keys()) + ['<div style="clear: right;"></div>']
    
    ret = string.join(ret, '\n')

    # handle metainfo section
    if pageEnv['toc'] or pageEnv['pagelist']:
        meta = ['<div id="metaInfo">\n']

        # generate links to beginning of page
        if pageEnv['pagelist'] and pageIndex:
            max_page_length = max([len(x) for x in pageIndex])
            page_link = '<a href="#page%%s">p.%%%ds</a>' % max_page_length

            def chunks(l, n):
              for i in xrange(0, len(l), n):
                yield l[i:i+n]

            meta += ['<dl id="pageList"><dt>Page list</dt><dd>\n']
            meta += ['<br/>'.join([' / \n'.join(x) for x in chunks([page_link % (x, x) for x in pageIndex], 10)])]
            meta += ['\n</dd></dl>\n']

        # generate table of contents
        if pageEnv['toc']:
            meta += ['<dl><dt>Table of Contents</dt><dd>\n']
            meta += ['<ul id="toc">%s</ul>\n' % _traverseHeader(headerIndex)]
            meta += ['</dd></dl>\n']
            
        meta += ['</div>\n']
    else:
        meta = []

    if warning:
        meta += ['<p style="text-indent: 0;">\n<span class="redmark">Warning:</span><br />\n']
        meta += ['<br />\n'.join(warning), '</p>']

    if meta: meta = '<div class="metaInfo">\n' + _control + ''.join(meta) + '</div>\n'
    else: meta = ''

    return [[1,
        _pageHead.replace('<title></title>', '<title>%s</title>' % _htmlEscape(pageEnv['title'])) \
                 .replace('<style type="text/css"></style>', '<style type="text/css">\n%s</style>' % (_styleSheet + code_formatter.get_style_defs('.highlight') + '\n',)) \
                 .replace('lang=""', 'lang="%s"' % pageEnv['lang']) + meta + _suggestFirefox + \
        '<div class="body">' + ret + '</div>' + \
        _pageTail],
        [3, headerIndex]]

def box(args, body, **kw):
    "((str,''),)"
    return [[1, '<div class="box %s">' % args[0]]] + body + [[1, '</div>']]

def defaultsyntax(body, **kw):
    "()"
    global _defaultSyntax
    _defaultSyntax = _joinBody(body)

def _colorize(body, in_syntax):
    b = _joinBody(body); c = b.decode('utf-8')

    try:
        syntax = in_syntax or _defaultSyntax
        if syntax and syntax != '-':
            lexer = pygments.lexers.get_lexer_by_name(syntax)
        elif syntax != '-':
            lexer = pygments.lexers.guess_lexer(c)
        else:
            lexer = None
    except:
        lexer = None

    if lexer:
        b = pygments.highlight(c, lexer, code_formatter).encode('utf-8')
        b = code_start_tag.sub('', b)
        b = code_end_tag.sub('', b)
        b = b.rstrip()
    else:
        b = _procBody(body, _htmlEscape).rstrip().strip('\r\n')

    return b

def c(args, body, **kw):
    "((str,''),)"

    b = _colorize(body, args[0])

    return [[1, '<code class="highlight">'], [1, b], [1, '</code>']]

def color(args, body, **kw):
    "(str,)"

    return [[1, '<span style="color: %s;">' % args[0]]] + body + [[1, '</span>']]

def code(args, body, **kw):
    "((str,''),(str,''),)"

    b = _colorize(body, args[0])

    if args[1]:
        pre_style = args[1]
    else:
        pre_style = 'pre highlight'

    return [[1, '<pre class="%s">' % pre_style], [1, b], [1, '</pre>']]

def column(args, body, **kw):
    "((str,''),(str,''))"
    columnTitle = {'transnote': "Translator's Note", 'exp': 'Experiment'}
    
    if not args[1]:
        desc = ''
    else:
        desc = '<br /><span class="desc">%s</span>' % args[1]

    return [[1, '<div class="box columnbox col-%s"><img src="tmp/%s.png" class="column" alt="%s" />' % (args[0], args[0], args[0])]] \
            + [[1, '<div class="heading"><span class="type">%s</span>' % columnTitle.get(args[0], args[0].capitalize()) ]] \
            + [[1, desc]] \
            + [[1, '</div>']] \
            + [[1, '<div style="clear: both; padding-bottom: 1em;"></div><div class="column">']] \
            + body \
            + [[1, '\n</div></div>']]

_tableCellFormat = re.compile('^(r(?P<rs>[0-9]+))?(c(?P<cs>[0-9]+))?(?P<v>[tmb])?(?P<h>[lcr])?$')

def _tableCell(tagName, args, body, line, column, cls='', **kw):
    tag = [tagName]; style = []; span = []
    
    # parse table-cell format string
    fmt = _tableCellFormat.match(args[0])
    
    if not fmt:
        raise EnvironmentError((line, column), 'Error in table cell format string')
    
    fmt = fmt.groupdict()
    
    # vertical alignment
    if   fmt['v'] == 't':
        style += ['vertical-align: top;']
    elif fmt['v'] == 'm':
        style += ['vertical-align: middle;']
    elif fmt['v'] == 'b':
        style += ['vertical-align: bottom;']
        
    # text alignment
    if   fmt['h'] == 'l':
        style += ['text-align: left;']
    elif fmt['h'] == 'c':
        style += ['text-align: center;']
    elif fmt['h'] == 'r':
        style += ['text-align: right;']
    
    # row & column span
    if fmt['rs']:
        span += ['rowspan="%d"' % int(fmt['rs'])]
    if fmt['cs']:           
        span += ['colspan="%d"' % int(fmt['cs'])]

    # additional style
    if args[1] != '':
        style += [args[1]]
        
    if style: tag += ['style="%s"' % string.join(style)]
    if cls: tag += ['class="%s"' % cls]
    if span: tag += span
    
    return [[1, '<%s>' % string.join(tag)]] + body + [[1, '</%s>' % tagName]]

def tr(**kw):
    "((str,''),(str,''))"
    global _tableCurRow, _tableCurCol
    _tableCurRow += 1
    _tableCurCol = 0
    
    return _tableCell('tr', **kw)
    
def td(**kw):
    "((str,''),(str,''))"
    global _tableCurCol
    _tableCurCol += 1

    return _tableCell('td', **kw)

def th(args, body, **kw):
    "((str,''),(str,''))"
    global _tableCurRow, _tableCurCol, _tableHeadRow
    _tableCurCol += 1

    if args[1]:
        cls=args[1]
        args[1] = ''
        return _tableCell('th', args=args, cls=cls, body=body, **kw)
    else:
        if _tableHeadRow == -1:
            _tableHeadRow = _tableCurRow
        if _tableCurRow == _tableHeadRow:
            cls='col'
        elif _tableCurCol == 1:
            cls='row'
        else:
            cls=''
        
        return _tableCell('th', args=args, cls=cls, body=body, **kw)
        
def table(args, body, **kw):
    "()"
    global _tableCurRow, _tableCurCol, _tableHeadRow
    _tableCurRow = _tableCurCol = 0
    _tableHeadRow = -1

    return [[1, '<table>\n']] + body + [[1, '</table>']]
    
def link(args, body, line, **kw):
    "((str,''),(int,0))"
    j = _joinBody(body)
    
    if j[0:1] == '=':
        # topic cross-reference
        if not pageEnv['projFile']:
            raise EnvironmentError((line, column), 'You must specify project file with \\project to use \\xref (even with single file)')

        return [[2, [line, j[1:]]]]
    else:
        # normal URLs
        if args[0]:
            if args[1]:
                return [
                    [1, '<p class="label"><span class="label url">URL</span><b>'], [1, args[0]], [1, '</b><br />'],
                    [1, '<a href="%s" target="_blank">' % _htmlEscape(j)], [1, _htmlEscape(j)], [1, '</a></p>']]
            else:
                return [[1, '<a href="%s">' % _htmlEscape(j)], [1, args[0]], [1, '</a>']]
        else:
            return [[1, '<a href="%s">' % _htmlEscape(j)], [1, _htmlEscape(j)], [1, '</a>']]

def ol(args, body, **kw):
    "((str,''),)"

    style = ''
    style_short = {
        '1': 'decimal',
        '01': 'decimal-leading-zero',
        'i': 'lower-roman',
        'I': 'upper-roman',
        'g': 'lower-greek',
        'a': 'lower-alpha',
        'A': 'upper-alpha',
        'C': 'cjk-ideographic'
        }

    if args[0]:
        if args[0] in style_short:
            style = ' style="list-style-type: %s;"' % style_short[args[0]]
        else:
            style = ' style="list-style-type: %s;"' % args[0]

    return [[1, '<ol%s>' % style]] + body + [[1, '</ol>']]

def li(args, body, **kw):
    "((int,0),)"

    value = ''
    if args[0]:
        value = ' value="%s"' % args[0]

    return [[1, '<li%s><div class="listItem">' % value, len(body)]] + body + [[1, '</div></li>']]

## Page number & autolink
###########################

def page(body, line, column, **kw):
    "()"
    global pageEnv, pageIndex, _firstPage

    ret = []
    pages = _joinBody(body).split(',')

    if not _firstPage:
        ret += ['<div class="pageSeparator"></div>']
    else:
        _firstPage = 0

    s = ''      # make xref links

    for p in pages:
        pageIndex.append(p)
        ret += ['<div id="page%s" class="srcPage"%s>p.%s</div>' % (p, s, p)]
        s = ' style="border-top: none;"'

    if not _firstPage:
        ret += ['<div class="pageSeparator"></div>']

    return [[1, '\n'.join(ret)]]

## Header autolink & cross reference
######################################

def _header(lv, args, body, line, **kw):
    global headerNo, headerTag, warning, warnlink
    
    headerNo += 1
    if (not headerIndex):
        headerIndex.append([_joinBody(body), lv, args[0], headerNo, []])
    else:
        curLevel = headerIndex
        while (curLevel[-1][1] < lv and curLevel[-1][4]):
            curLevel = curLevel[-1][4]

        if (curLevel[-1][1] < lv):
            curLevel[-1][4].append([_joinBody(body), lv, args[0], headerNo, []])
        else:
            curLevel.append([_joinBody(body), lv, args[0], headerNo, []])

    if args[0]:
        anchor = '<span class="headAnchor">%s</span>' % args[0]
        dup = headerTag.get(args[0])
        if dup: 
            warning += ['Line <a href="#warn%d">%s</a>: Duplicate tag <b>"%s"</b> with line %s' % (warnlink, line, args[0], dup)]
            anchor = '<a name="warn%d">%s</a>' % (warnlink, anchor)
            warnlink += 1
        headerTag[args[0]] = line

    else:
        anchor = ''

    return [[1, '<h%s id="header%s">%s%s</h%s>' % (lv, headerNo, anchor, _joinBody(body), lv)]]

def _headerWrapper(lv):
    f = lambda **kw: _header(lv, **kw)
    f.func_doc = "((str,''),)"
    return f

def _traverseHeader(header):
    ret = []
    for h in header:
        ret += ['<li><a href="#header%s">' % h[3]]
        if h[2]: ret += ['%s ' % h[2]]
        ret += ['%s</a>' % h[0]]
        
        if h[4]:
            ret += ['\n<ul>\n%s</ul>\n' % _traverseHeader(h[4])]

        ret += ['</li>\n']

    return ''.join(ret)

## Footnote
#############

def fn(body, args, **kw):
    "((str,''),)"
    global _fnCount, _fnItems, _fnSerial

    if args[0]:
        tagName = args[0]
    else:
        tagName = _fnCount
        _fnCount += 1
    
    _fnItems[_fnSerial] = (tagName, re.sub(r'[\r\n]', '', _joinBody(body)))
    tag = '<!-- footnote %d --><a name="fa%s" /><a href="#fn%s" class="fnanchor">*%s</a>' % (_fnSerial, tagName, tagName, tagName)
    _fnSerial += 1

    return [[1, tag]]

## Embedding image support
############################

def img(args, body, **kw):
    "((str,''),)"
    
    b = _joinBody(body)
    if not b: b = 'tmp/placeholder.png'
    return [[1, '<img src="%s" alt="%s" style="%s" />' % (b, b, args[0])]]

def math(body, fileName, **kw):
    "()"
    global mathCount

    b = _joinBody(body)
    cmd = _htmlEscape(b)
    cmdlink = urllib.quote(b)

    if translator_config.snapshot:
        gifname = "%s.math.%d.gif" % (fileName[:fileName.rfind('.')], mathCount); mathCount += 1
        print "Saving formula '%s' into %s" % (b, gifname)
        urllib.urlretrieve("http://tib.tw/~tiberius/cgi-bin/mimetex.cgi?%s" % cmdlink, gifname)
        return [[1, '<img src="%s" alt="%s" class="mimetex" />' % (gifname, cmd)]]

    else:
        return [[1, '<img src="http://tib.tw/~tiberius/cgi-bin/mimetex.cgi?%s" alt="%s" class="mimetex" />' % (cmdlink, cmd)]]
    

## Simple tag-surrounding markups
##################################

def _makeSimpleMacro(str):
    f = lambda **kw: [[1, str[0], len(kw['body'])]] + kw['body'] + [[1, str[1]]]
    f.func_doc = "()"
    return f

_simpleMacros = {
    'b':            ['<b>', '</b>'],
    'caption':      ['<caption>', '</caption>'],
    'dl':           ['<dl>', '</dl>'],
    'dd':           ['<dd>', '</dd>'],
    'dt':           ['<dt>', '</dt>'],
    'dtn':          ['<dt class="normal-weight">', '</dt>'],
    'i':            ['<i>', '</i>'],
    'k':            ['<kbd class="keyboard">', '</kbd>'],
    'm':            ['\\(\\displaystyle ', '\\)'],
    'nobr':         ['<nobr>', '</nobr>'],
    'o':            ['<span class="orange">', '</span>'],
    'p':            ['<p style="text-indent: 0;">', '</p>'],
    'quote':        ['<blockquote>', '</blockquote>'],
    'r':            ['<span class="redmark">', '</span>'],
    's':            ['<span class="small">', '</span>'],
    'sqrt':         ['&radic;<span style="text-decoration: overline;">', '</span>'],
    'sub':          ['<sub>', '</sub>'],
    'sup':          ['<sup>', '</sup>'],
    'sc':           ['<span class="smallcaps">', '</span>'],
    'u':            ['<u>', '</u>'],
    'ul':           ['<ul>', '</ul>'],
    'y':            ['<span class="ybg">', '</span>'],
    'z':            ['<span class="reset">', '</span>'],
    'boxHead':      ['<div class="boxHead">', '</div>'],
}

for k in _simpleMacros:
    _simpleMacros[k] = _makeSimpleMacro(_simpleMacros[k])

for k in xrange(1, 7):
    _simpleMacros['h%s' % k] = _headerWrapper(k)

locals().update(_simpleMacros)

if __name__ == '__main__':
    print 'TMP Translator markup pack'
