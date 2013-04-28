# -*- coding: utf-8 -*-
"""
 tmp - tiberius' Text Markup Processor
-----------------------------------------------------------------------
Comment   : Main source file (parser, built-in markups)
Version   : $Id: tmp.py 85 2006-04-24 16:55:44Z tiberius $
Copyright : (C) 2005 by Tiberius Teng <s9256043@mail.cs.nchu.edu.tw>
-----------------------------------------------------------------------
 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or any
 later version.
-----------------------------------------------------------------------
"""
import copy, glob, sys, tpg
from pprint import pprint

try:
    from IPython.Debugger import Pdb
    def trace():
        Pdb().set_trace()
except:
    import pdb
    def trace():
        pdb.set_trace()

class MarkupError(tpg.Error):
    pass

class TMP(tpg.Parser):
    r"""
    set lexer = ContextSensitiveLexer

    # allows \[ \\ \]

    token normal_text   '(\\\[|[^\\\]]|\\\\|\\\])+' $lambda b: b.replace('\\\\', '\\').replace('\\]', ']').replace('\\[', '[')

    # allow anything except \ ( ) { } [ ] <spaces>

    token markup_name   '[^\\\(\)\{\}\][\s]+';
    
    token old_markup_param  '([^,\\)]|\\\\|\\,|\\\))*';

    token identifier    '[a-zA-Z_][a-zA-Z0-9_]*';

    # allow anything except ; \ but allow \; \\

    token decl_literal       '([^,\\\)]|\\,|\\\\|\\\))+' $lambda b: b.replace('\\;', ';').replace('\\\\', '\\').replace('\)', ')')

    # allows \; \\ \}

    token param_literal '([^,\\\}]|\\,|\\\\|\\})+' $lambda b: b.replace('\\,', ',').replace('\\\\', '\\').replace('\\}', '}')

    token verbatim_literal '([^\\\]]|\\\])+' $lambda b: b.replace('\\]', ']')

    token esc_r_bracket '\](?!\])';

    token comma         ',';
    token colon         ':';
    token equals        '=';

    token back_slash    '\\';

    token l_paren       '\(';
    token r_paren       '\)';
    token l_bracket     '\[';
    token r_bracket     '\]';
    token l_curly       '\{';
    token r_curly       '\}';

    token spaces        '\s*';

    token define_cmd    'define';

    token verbatim_cmd  'v';

    # $self.parseTree(r)$

    START/$self.parseTree(r)$ ->
        $r = []
        ( normal_text/v     $r += [[0, v]]
        | verbatim/v        $r += [[0, v]]
        | markup_call/v     $r += v
        | r_bracket/v       $r += [[0, v]]
        )*
        ;

    short_content/r ->
        $r = []
        ( normal_text/v     $r += [[0, v]]
        | verbatim/v        $r += [[0, v]]
        | markup_call/v     $r += v
        )*
        ;

    long_content/r ->
        $r = []
        ( normal_text/v     $r += [[0, v]]
        | esc_r_bracket/v   $r += [[0, v]]
        | verbatim/v        $r += [[0, v]]
        | markup_call/v     $r += v
        )*
        ;

    arg_content/r ->
        $r = []
        ( param_literal/v   $r += [[0, v]]
        | markup_call/v     $r += v
        )*
        ;

    markup_param_decl/r ->
        spaces
        identifier/i        $r = [i, None, None]
        spaces
        (
            (
                colon
                spaces
                identifier/t    $r[1] = t # type converter
                spaces
            )?
            (
                equals
                spaces
                decl_literal/d   $r[2] = d # default value
                spaces
            )?
        )?
        ;

    markup_call/$[[t, name, param, body, line, column]]$ -> 
        $t = 0
        back_slash $line = self.line(); column = self.column()
        (
            # markup signature for definition
            $t = -3
            define_cmd/n  $name = n
            l_curly
            markup_name $param = [markup_name, []]
            l_paren
            (
                markup_param_decl/v $param[1] += [v]
                (
                    comma markup_param_decl/v $param[1] += [v]
                )*
            )?
            spaces
            r_paren
            r_curly
        |
            markup_name/n $name = n
            (
                # old calling method
                $t = -1
                l_paren
                old_markup_param/p      $param =  [p]
                (
                    comma
                    old_markup_param/p  $param += [p]
                )*
                r_paren/v
            |
                # new calling method
                $t = -2
                l_curly
                arg_content/p     $param =  [p]
                (
                    comma
                    arg_content/p $param += [p]
                )*
                r_curly
            |
                $param = ''; t = -1
            )
        )
        (
            l_bracket l_bracket
            long_content/s  $body = s
            r_bracket r_bracket
        |
            l_bracket
            short_content/s $body = s
            r_bracket
        |
            verbatim/v      $body = [[0, v]]
        |
            markup_call/m   $body = m
        |
            $body = []
        )
        ;

    verbatim/r ->
        back_slash verbatim_cmd l_bracket l_bracket
        verbatim_content/v      $r = v
        r_bracket r_bracket
        ;

    verbatim_content/r ->
        $r = ''
        ( verbatim_literal/v    $r += v
        | esc_r_bracket/v       $r += v
        | back_slash/v          $r += v
        )*
        ;

    """

    def __init__(self, fileName):
        tpg.Parser.__init__(self)

        # defined markups (commands)

        # format: markup_name: [func, signature, required_params_count]
        #         signature:   [typeConverter, (typeConverter, defaultValue), ... ]

        # will generate metadata for built-in commands later

        self.markups = {
            'ifnval':   self.ifnval,
            'ifval':    self.ifval,
            'include':  self.includeFile,
            'strip':    self.strip,
            'use':      self.useMarkupPack,
        }

        # defined macros (lazy-evaluated strings)
        # format: macro_name: [file, line, column, signature, content]
        #         signature:  [[name, type, default], ...]
        self.macros = {}

        self.fileName = fileName
        self.fileNames = [fileName]

        # prepare metadata for built-in commands

        for k in self.markups:
            self.markups[k] = [self.markups[k], eval(self.markups[k].im_func.func_doc), 1]

        self.markups['strip'][2] = 0

    ## Built-in Markups
    ###################

    def includeFile(self, line, column, args, **kw):
        "(str,)"
        try:
            f = file(args[0]).read()
        except:
            raise MarkupError((line, column), 'Error opening file "%s" for include' % args[0]) 

        x = TMP(args[0])
        x.fileNames = self.fileNames
        x.markups.update(self.markups)

        self.fileNames.append(args[0])
        ret = x(f)
        self.fileNames.pop()

        self.macros.update(x.macros)

        return ret

    def useMarkupPack(self, args, line, column, **kw):
        "(str,)"

        loadedMarkups = __import__(args[0]).__dict__
        reload(__import__(args[0]))

        if callable(loadedMarkups.get('reset')):
            loadedMarkups['reset']()

        # Pre-process markup definition file
        for k in loadedMarkups:
            n = loadedMarkups[k]

            # Check for markup name duplications
            if k in self.markups:
                raise MarkupError((line, column), 'Markup name "%s" conflict with built-in or previously loaded markup' % args[0])

            # Try converting callable objects into markup
            # (check parameter-specification strings, calcuate mandatory parameter counts)
            if callable(n):
                try:
                    # Get & check spec string
                    markupParamSpec = eval(n.func_doc)
                    if type(markupParamSpec) != tuple: continue

                    # Count mandatory parameters
                    reqParams = 0; optional = 0; valid = 1
                    for p in markupParamSpec:
                        if (optional and type(p) != tuple):
                            raise MarkupError((line, column), 'Markup "%s" with illegal parameter spec (non-default after default)' % \
                                args[0])
                            #valid = 0
                            #break

                        elif ((not optional) and type(p) != tuple):
                            reqParams += 1

                        elif ((not optional) and type(p) == tuple):
                            optional = 1

                    if valid:
                        loadedMarkups[k] = [loadedMarkups[k], markupParamSpec, reqParams]
                except:
                    pass

        self.markups.update(loadedMarkups)

    def strip(self, body, **kw):
        "()"
        l = len(body)

        for i in [xrange(l), xrange(l-1, -1, -1)]:
            for j in i:
                body[j][1] = body[j][1].strip()
                if body[j][1]: break

        return body

    def ifval(self, params, body, **kw):
        "((str,''),)"
        if params[0]:
            return body
        else:
            return []

    def ifnval(self, params, body, **kw):
        "((str,''),)"
        if not params[0]:
            return body
        else:
            return []

    def expandMacro(self, macroName, params, body, line, column):
        mFile, mLine, mColumn, mSignature, mContent = self.macros[macroName]

        # avoid modifying original subtree
        mContent = copy.deepcopy(mContent)

        #print 'calling (macro) %s' % macroName
        #pprint(params)

        # parameters check
        paramCount = len(params)
        
        if paramCount < mSignature[1]:
            raise MarkupError((line, column), 'Called macro "%s" with too few parameters: expected %s, got %s' % \
                    (macroName, mSignature[1], paramCount))

        if paramCount > len(mSignature[0]):
            raise MarkupError((line, column), 'Too many arguments for macro "%s"; at most %s, got %s' % (macroName, len(mSignature[0]), paramCount))

        # Do type conversion
        paramPos = 0; realParams = {'body': body}

        for s in mSignature[0]:
            try:
                if s[2] != None:
                    if (paramPos >= paramCount) or (not params[paramPos]):
                        realParams[s[0]] = s[2]
                    else:
                        realParams[s[0]] = params[paramPos]
                else:
                    realParams[s[0]] = params[paramPos]
            except:
                raise MarkupError((line, column), 'Error converting argument "%s" of macro "%s"; was trying to convert %s into %s' % \
                    (s[0], macroName, repr(params[paramPos]), repr(s[1])))

            paramPos += 1
        
        return self.expandTreeMacros(mContent, realParams, '%s@%s:%s:%s' % (macroName, mFile, mLine, mColumn))

    def callMarkup(self, markupName, args, body, line, column):
        """Calls a markup, performing argument sanity checks.
        """

        # Get the function object of specified markup
        try:
            markup = self.markups[markupName]
        except KeyError:
            raise MarkupError((line, column), 'Markup "%s" not found' % markupName)
            #return []

        if callable(markup[0]):
            # Handle callable-type markups (method instance, function, class, ...)
            #######################################################################
            # Get markup's parameter specification
            try:
                meta = self.markups[markupName][1:3]
            except KeyError:
                raise MarkupError((line, column), 'Callable "%s" is not available as a markup (no parameter spec found)' % \
                    markupName)

            spec = meta[0]
            argCount = len(args)

            args = map(lambda x: x.replace('\\,', ',').replace('\\)', ')').replace('\\\\', '\\'), args)

            # Check parameter numbers
            if argCount < meta[1]:
                raise MarkupError((line, column), 'Called markup "%s" with too few parameters: expected %s, got %s' % \
                    (markupName, meta[1], len(args)))

            # Do type conversion
            argPos = 0; realArgs = []

            for x in spec:
                try:
                    if type(x) == tuple:
                        if (argPos >= argCount) or (not args[argPos]):
                            realArgs.append(x[1])
                        else:
                            realArgs.append(x[0](args[argPos]))
                    else:
                        realArgs.append(x(args[argPos]))

                except:
                    raise MarkupError((line, column), 'Error converting parameter %s of markup "%s"; was trying to convert %s into %s' % \
                        (x, markupName, repr(args[argPos]), repr(x)))

                argPos += 1

            # Pass additional parameters as-is
            # (to let markup implement their own, possibly more complex, checks)
            while argPos < argCount:
                realArgs.append(args[argPos])
                argPos += 1

            ret = markup[0](**{'args': realArgs, 'body': body, 'fileName': self.fileName, 'params': realArgs, 'parser': self, 'line': line, 'column': column})

            if ret == None:
                return []
            else:
                return ret

        elif type(markup) == str:
            # Simple string substitution markup
            return [[1, markup]] + body

    def defineMacro(self, macroName, params, body, line, column):
        """Defines a lazy-evaluated macro.
        """

        if macroName != 'define':
            raise MarkupError((line, column), 'Macro signature is only valid for \\define.')

        macroName = params[0]
        signature = params[1] # format is [name, type, default]
        
        if macroName in self.macros:
            p = self.macros[macroName]
            raise MarkupError((line, column), 'Redefinition of macro "%s": Previous defined at %s:%s:%s' % (macroName, p[0], p[1], p[2]))

        # Count mandatory parameters and evaluate converters/default values

        req = 0; optional = 0; valid = 1

        for p in signature:
            if (optional and p[2] == None):
                raise MarkupError((line, column), 'Macro "%s" with illegal parameter spec (non-default after default)' % macroName)

            elif ((not optional) and p[2] == None):
                req += 1

            elif ((not optional) and p[2] != None):
                optional = 1

            try:
                if p[1]: p[1] = eval(p[1])
                if p[2]: p[2] = eval(p[2])
            except:
                raise MarkupError((line, column), 'Argument "%s" of macro "%s" is invalid' % (p[0], macroName))

        self.macros[macroName] = [self.fileName, line, column, [signature, req], body]

    def expandTreeMacros(self, l, params={}, macro=None):
        """First pass - Including files, defining macros, expanding macros.
        """

        r = []

        for node in l:
            if  node[0] == -1:
                # old calling syntax
                if node[1] in params:
                    # expanding parameter
                    if not (node[2] == '' and node[3] == []):
                        raise MarkupError((node[4], node[5]), 'Expanding parameter "%s" of macro "%s" with arguments/contents -- possibly misuse' % 
                            (node[1], macro))
                
                    v = params[node[1]]

                    if type(v) == list:
                        r += self.expandTreeMacros(v, params, macro)
                    else:
                        r += [[0, str(params[node[1]])]]
                else:
                    if node[1] in self.macros:
                        # a macro to expand
                        r += self.expandMacro(node[1], node[2], self.expandTreeMacros(node[3], params, macro), node[4], node[5])
                    else:
                        # calling markup - not now, excluding 'include'
                        if node[1] == 'include':
                            r += self.callMarkup(node[1], node[2], self.expandTreeMacros(node[3], params, macro), node[4], node[5])
                        else:
                            r += [[-1, node[1], node[2], self.expandTreeMacros(node[3], params, macro), node[4], node[5]]]

            elif node[0] == -2:
                # new calling syntax
                if node[1] == 'define' and len(node[2]) == 1 and len(node[2][0]) == 1 and node[2][0][0][0] == 0:
                    # defining a new macro (without parameters)
                    self.defineMacro(node[1], [node[2][0][0][1], []], node[3], node[4], node[5])

                else:
                    if node[1] in self.macros:
                        # a macro to expand
                        #args = map(lambda x: ''.join(map(lambda y: y[1], self.expandTreeMacros(x, params, macro))), node[2])
                        #args = map(lambda x: self.expandTreeMacros(x, params, macro), node[2])
                        args = [self.expandTreeMacros(x, params, macro) for x in node[2]]
                        r += self.expandMacro(node[1], args, self.expandTreeMacros(node[3], params, macro), node[4], node[5])

                    else:
                        # won't actually call markups now, only expands body, except 'include'
                        # but since new syntax allows markup/macros in arguments, so resolve them now
                        #args = map(lambda x: self.expandTreeMacros(x, params, macro), node[2])
                        args = [self.expandTreeMacros(x, params, macro) for x in node[2]]

                        if node[1] == 'include':
                            #args = map(lambda x: ''.join(map(lambda y: y[1], x)), args)
                            args = [''.join([y[1] for y in x]) for x in args]
                            r += self.callMarkup(node[1], args, self.expandTreeMacros(node[3], params, macro), node[4], node[5])
                        else:
                            r += [[-2, node[1], args, self.expandTreeMacros(node[3], params, macro), node[4], node[5]]]

            elif node[0] == -3:
                # defining a new macro (with parameters)
                self.defineMacro(node[1], node[2], node[3], node[4], node[5])

            else:
                # text/metadata node
                r += [node]

        return r

    def callTreeMarkups(self, l):
        """Second pass - execute all markups.
        """

        r = []

        for node in l:
            if  node[0] == -1:
                # call markup (old way)
                #print '(old) %s' % node[2]
                r += self.callMarkup(node[1], node[2], self.callTreeMarkups(node[3]), node[4], node[5])

            elif node[0] == -2:
                # call markup (new way)
                args = map(lambda x: ''.join(map(lambda y: y[1], self.callTreeMarkups(x))), node[2])
                r += self.callMarkup(node[1], args, self.callTreeMarkups(node[3]), node[4], node[5])

            else:
                # text/metadata node
                r += [node]

        return r

    def parseTree(self, l):
        #pprint(l, file('%s.0.txt' % self.fileName, 'w'))
        l = self.expandTreeMacros(l)
        #pprint(l, file('%s.1.txt' % self.fileName, 'w'))
        l = self.callTreeMarkups(l)
        #pprint(l, file('%s.2.txt' % self.fileName, 'w'))

        return l

#######################################################################
## Command-line execution handler

def filterMeta(x):
    if x[0] < 2:
        return x[1]
    else:
        return ''

if __name__ == '__main__':
    import os
    import translator_config

    try:
        import psyco
        psyco.profile(watermark=0.02)
        print 'Psyco enabled.'
    except:
        pass

    translator_config.snapshot = 1
    
    print sys.argv
    if len(sys.argv) < 2:
        print "Usage: %s <infile> [<infile2> ...]" % sys.argv[0]
        sys.exit(1)

    if len(sys.argv) == 2:
        files = glob.glob(sys.argv[1])
    else:
        files = sys.argv[1:]

    for fileName in files:
        try:
            tmp = TMP(fileName)
            tmp.verbose = 2
            r = tmp(file(fileName).read())
            #print '<doc>' + ''.join(map(xmltag, r)) + '</doc>'
            #print ''.join(map(filterMeta, r)).strip()
            file(fileName[:fileName.rfind('.')] + '.htm', 'w').write(''.join(map(filterMeta, r)).strip())
            print 'Processed %s' % fileName
        except tpg.Error, x:
            srcPath = os.path.abspath(tmp.fileNames[-1])
            src = file(srcPath).read()

            if (x.column > 40):
                prefix = '... '
                start = x.column - 20
            else:
                prefix = ''
                start = 0

            print 'while processing %s:' % srcPath
            print '%s\n' % str(x)
            print '%s%s' % (prefix, src.split('\n')[x.line-1][start:start+65])
            print '%s%s^\n' % (prefix, ' ' * (x.column - start - 1))
