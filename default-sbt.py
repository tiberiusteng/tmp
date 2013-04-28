# -*- coding: utf-8 -*-
"""
    pygments.styles.default-sbt
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Modified from the default highlighting style.
    Differentiates attribute and string

    :copyright: 2007 by Tiberius Teng.
    :copyright: 2006 by Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic


class DefaultSbtStyle(Style):
    """
    The default style (inspired by Emacs 22).
    """

    background_color = "#f2f2f2"
    default_style = ""

    styles = {
        Comment:                   "italic #408080",
        Comment.Preproc:           "noitalic",

        #Keyword:                   "bold #AA22FF",
        Keyword:                   "bold #008000",
        Keyword.Pseudo:            "nobold",
        Keyword.Type:              "",

        Operator:                  "#666666",
        Operator.Word:             "bold #AA22FF",

        #Name.Builtin:              "#AA22FF",
        Name.Builtin:              "#008000",
        #Name.Function:             "#00A000",
        Name.Function:             "#BC7A00",
        Name.Class:                "#0000FF",
        Name.Namespace:            "bold #0000FF",
        Name.Exception:            "bold #D2413A",
        #Name.Variable:             "#B8860B",
        Name.Variable:             "#19177C",
        Name.Constant:             "#880000",
        Name.Label:                "#A0A000",
        Name.Entity:               "bold #999999",
        #Name.Attribute:            "#BB4444",
        #Name.Attribute:            "#705406",
        Name.Attribute:            "#7D6029",
        Name.Tag:                  "bold #008000",
        Name.Decorator:            "#AA22FF",

        #String:                    "#BB4444",
        String:                    "#BA2121",
        String.Doc:                "italic",
        String.Interpol:           "bold #BB6688",
        String.Escape:             "bold #BB6622",
        String.Regex:              "#BB6688",
        #String.Symbol:             "#B8860B",
        String.Symbol:             "#19177C",
        String.Other:              "#008000",
        Number:                    "#666666",

        Generic.Heading:           "bold #000080",
        Generic.Subheading:        "bold #800080",
        Generic.Deleted:           "#A00000",
        Generic.Inserted:          "#00A000",
        Generic.Error:             "#FF0000",
        Generic.Emph:              "italic",
        Generic.Strong:            "bold",
        Generic.Prompt:            "bold #000080",
        Generic.Output:            "#888",
        Generic.Traceback:         "#04D",

        Error:                     "border:#FF0000"
    }
