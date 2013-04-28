" Vim syntax file
" Language:		TMP (Tiberius' Text Macro Processor
" Maintainer:	Tiberius Teng <tiberiusteng@msn.com>
" Updated:		2005-11-02
if version < 600
	syntax clear
elseif exists("b:current_syntax")
	finish
endif

" syn cluster tmpMarkup contains=tmpMacroCall

syn region tmpMacroParams	contained start="(" skip="\\)" end=")" nextgroup=tmpShortBody,tmpLongBody
syn region tmpLongParams	contained matchgroup=tmpMacroParamDelim start="{" skip="\\}" end="}" contains=tmpMacroCall,tmpMacroParamDelim nextgroup=tmpShortBody,tmpLongBody

syn match  tmpMacroParamDelim	contained "[,:;\(\)=]"

syn match  tmpDefine		"\\\(define\|strip\|ifval\|ifnval\)" nextgroup=tmpMacroParams,tmpLongParams,tmpShortBody,tmpLongBody
syn match  tmpMacroCall		"\\\(define\|strip\|ifval\|ifnval\|b$\|c$\|cl$\|page$\|boxHead$\|caption$\|quote$\|h[123456]$\)\@![^[\](){}\\ ]\+" nextgroup=tmpMacroParams,tmpLongParams,tmpLongBody,tmpShortBody
" syn match  tmpBodyDelimiter	"[[\]]"
" syn match  tmpDoubleQuote	"\(\[\[\|\]\]\)"

syn cluster tmpTags		contains=tmpDefine,tmpMacroCall,tmpTransBold,tmpTransCode,tmpTransPage,tmpTransHead,tmpTransCaption,tmpTransQuote

syn region tmpShortBody		contained matchgroup=tmpBodyDelimiter contains=@tmpTags,tmpSpecialChar transparent start="\["   skip="\\\]" end="\]"
syn region tmpLongBody		contained matchgroup=tmpDoubleQuote   contains=@tmpTags,tmpSpecialChar transparent start="\[\[" skip="\\\]" end="\]\]"

" \b, \c, \code, \c[... \b ...]

syn region tmpTransBold		contains=tmpTransBoldSB,tmpTransBoldLB matchgroup=tmpMacroCall start="\\b\[\@=" skip="\\\]" end="\]\@<="
syn region tmpTransCode		contains=@tmpTransCodeOptions,tmpTransCodeSB,tmpTransCodeLB matchgroup=tmpMacroCall start="\\\(c\|code\|cl\)[[({]\@=" skip="\\\]" end="\]\@<="

syn cluster tmpTransCodeOptions	contains=tmpCodeLongParams,tmpCodeShortParams
syn region tmpCodeLongParams	contained matchgroup=tmpMacroParamDelim start="{" skip="\\}" end="}" contains=tmpMacroCall,tmpMacroParamDelim
syn region tmpCodeShortParams	contained start="(" skip="\\)" end=")"

syn region tmpTransCodeBold	contained contains=tmpTransCodeBoldSB,tmpTransCodeBoldLB matchgroup=tmpMacroCall start="\\b\[\@=" skip="\\\]" end="\]\@<="

syn region tmpTransBoldSB	contained contains=@tmpTags,tmpSpecialChar matchgroup=tmpBodyDelimiter start="\[" skip="\\\]" end="\]"
syn region tmpTransBoldLB	contained contains=@tmpTags,tmpSpecialChar matchgroup=tmpDoubleQuote start="\[\[" skip="\\\]" end="\]\]"

syn region tmpTransCodeSB	contained contains=@tmpTags,tmpSpecialChar,tmpTransCodeBold matchgroup=tmpBodyDelimiter start="\[" skip="\\\]" end="\]"
syn region tmpTransCodeLB	contained contains=@tmpTags,tmpSpecialChar,tmpTransCodeBold matchgroup=tmpDoubleQuote start="\[\[" skip="\\\]" end="\]\]"

syn region tmpTransCodeBoldSB	contained contains=@tmpTags,tmpSpecialChar matchgroup=tmpBodyDelimiter start="\[" skip="\\\]" end="\]"
syn region tmpTransCodeBoldLB	contained contains=@tmpTags,tmpSpecialChar matchgroup=tmpDoubleQuote start="\[\[" skip="\\\]" end="\]\]"

" \quote

syn region tmpTransQuote	contains=tmpTransQuoteSB,tmpTransQuoteLB matchgroup=tmpMacroCall start="\\\(quote\)\[\@=" skip="\\\]" end="\]\@<="

syn region tmpTransQuoteSB	contained contains=@tmpTags,tmpSpecialChar matchgroup=tmpBodyDelimiter start="\[" skip="\\\]" end="\]"
syn region tmpTransQuoteLB	contained contains=@tmpTags,tmpSpecialChar matchgroup=tmpDoubleQuote start="\[\[" skip="\\\]" end="\]\]"

" \page

syn match  tmpTransPageNum	contained "\v\d+"
syn region tmpTransPage		contains=tmpTransPageNum matchgroup=Statement start="\\page\[" end="\]"

" \boxHead, \caption

syn region tmpTransCaption	contains=tmpTransCaptionBody matchgroup=tmpMacroCall start="\v\\(boxHead|caption)\[@=" end="\]\@<="
syn region tmpTransCaptionBody	contained contains=@tmpTags,tmpSpecialChar matchgroup=tmpBodyDelimiter start="\[" skip="\\\]" end="\]"

" \h1, \h2, \h3, \h4, \h5, \h6

syn match  tmpTransHead		"\v\\h[123456]" nextgroup=tmpTransHeadParam,tmpTransHeadBody
syn region tmpTransHeadParam	contained start="(" skip="\\)" end=")" nextgroup=tmpTransHeadBody
syn region tmpTransHeadBody	contained matchgroup=tmpBodyDelimiter start="\[" skip="\\\]" end="\]"

"syn match tmpTransCodeLeftDelim		contained "\["   nextgroup=tmpTransCodeBody

"syn match tmpTransCodeRightDelim	contained "\]"
"syn match tmpTransCodeTag		"\\c\["me=e-1  nextgroup=tmpTransCodeBody
"syn match tmpTransBoldTag		"\\b\["me=e-1  nextgroup=tmpTransBoldBody

syn match  tmpSpecialChar	"\v\\[[)\],\\]"

syn sync fromstart

map <C-B> xi\b[<ESC>pa]
map <C-I> xi\i[<ESC>pa]
map <C-O> xi\o[<ESC>pa]
map <C-D> xi\c[<ESC>pa]
map <C-E> xi\y[<ESC>pa]

if version >= 508 || !exists("did_tmp_syn_inits")
  if version <= 508
    let did_tmp_syn_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif

  hi def under	term=underline cterm=underline gui=underline

  HiLink tmpMacroCall		Function
  HiLink tmpMacroParams		Constant
  HiLink tmpCodeShortParams	Constant
  HiLink tmpBodyDelimiter	Special
  HiLink tmpDoubleQuote		PreProc

  HiLink tmpDefine		PreProc
  HiLink tmpLongParams		Constant
  HiLink tmpCodeLongParams	Constant
  HiLink tmpMacroParamDelim	Statement

  HiLink tmpTransBoldSB SpellRare
  HiLink tmpTransBoldLB SpellRare

  HiLink tmpTransCodeSB		Comment
  HiLink tmpTransCodeLB		Comment

  HiLink tmpTransHead		tmpMacroCall
  HiLink tmpTransHeadParam	tmpMacroParams
  HiLink tmpTransHeadBody	Title

  HiLink tmpSpecialChar		LineNr

  hi def tmpTransCodeBoldSB	gui=undercurl guisp=Magenta guifg=#80a0ff
  hi def tmpTransCodeBoldLB	gui=undercurl guisp=Magenta guifg=#80a0ff

  hi def tmpTransPageNum	gui=bold

  hi def tmpTransQuoteSB	guifg=SeaGreen
  hi def tmpTransQuoteLB	guifg=SeaGreen

  hi def tmpTransCaptionBody	guibg=#003399

  hi def tmpRed			guifg=red

  delcommand HiLink
endif

