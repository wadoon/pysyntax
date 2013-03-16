#!/usr/bin/python3

#Copyright (c) <year>, <copyright holder>
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the <organization> nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from see import see
from simplegeneric import generic
import ast
from ast import *
#from termcolor import colored
from xtermcolor import colorize
from random import choice,uniform
from contextlib import contextmanager


__author__ = "Alexander Weigl"
__date__ = "2013-03-16"
__license__ = "BSD"


class Indenter(object):
    def __init__(self):
        self._prefix = []        

    def __call__(self,*args):
        print(self,end="")
        print(*args)

    def __str__(self):
        return "".join(self._prefix)

    def _pop(self):
        del self._prefix[-1]

    def _push(self,p):
        self._prefix += (p,) 

    @contextmanager
    def sub(self):
        self._push(randomcolor("│ "))
        yield self 
        self._pop()

    @contextmanager
    def section(self, name):
        self(colorhelper(name))
        self._push(randomcolor("│ "))
        yield self 
        self._pop()
    

    @contextmanager
    def keyword(self, name):
        self(colorkeyword(name))
        self._push(randomcolor("│ "))
        yield self 
        self._pop()        

def p(i, *args):
    i(*args)


def colorname(name):
    return colorize(str(name), ansi= 208)

def colorkeyword(name):
    return colorize(name, ansi = 226)

def colorhelper(text):
    return colorize(text, ansi = 39)

def colorop(name):
    return colorize(str(name), ansi = 189)

def randomcolor(text):
    return colorize(text, ansi = int(uniform(21,231)))

def colorliteral(name):
    return colorize(name, ansi = 129)    

@generic
def show(ast, indent):
    """default"""
    p(indent,type(ast))


@show.when_type(Pass)
def show_pass(p,indent):
    indent(colorkeyword("pass"))

@show.when_type(list)
def show_list(lis,indent):
    for item in lis:        
        show(item, indent)

@show.when_type(Name)
def show_name(name, indent):
    p(indent, colorname(name.id))

@show.when_type(UnaryOp)
def show_unaryop(un,indent):
    op_name = NAMES.get(type(un.op),type(un.op))
    p(indent, "UNARY OP [%s]" % colorop(op_name))
    with indent.sub() as i:
        show(un.operand, i)
        

@show.when_type(BinOp)
def show_binop(bin,indent):
    op_name = NAMES.get(type(bin.op),type(bin.op))
    p(indent, "[%s]" % colorop(op_name))
    with indent.sub() as i:
        show(bin.left, i)
        show(bin.right, i)

@show.when_type(Return)
def show_return(ret,indent):
    p(indent, colorkeyword("RETURN"))
    with indent.sub() as i:
        show(ret.value, i)


@show.when_type(arguments)
def show_arguments(a,indent):
    args = a.args
    defs = a.defaults

    args.reverse()
    defs.reverse()

    defs = expandlist(defs,args)

    alist = list(zip(args,defs))
    alist.reverse()

    argslist = [colorname(var.arg) for (var,val) in alist]

    args   = "*"  +a.vararg if a.vararg else ""
    kwargs = "**" + a.kwarg if a.kwarg else ""

    for [var,val] in alist:
        p(indent, "%s" % colorname(var.arg))
        if val:
            with indent.sub() as i:
                show(val,i)


@show.when_type(Lambda)
def show_lambda(la, indent):
    indent(colorkeyword("lambda"))
    with indent.sub():
        show(la.args , indent)

    indent(colorhelper("body:"))
    with indent.sub():
        show(la.body,indent)

@show.when_type(Module)
def show_module(mod, indent):
    indent("[MODULE]")
    for b in mod.body:
        with indent.sub() as i:
            show(b,indent)

def expandlist(lis, to):
    if type(to) in (list,tuple):
        to = len(to)
    return lis + [None] * (to-len(lis))

@show.when_type(Num)
def show_num(num, indent):
    indent(colorliteral(str(num.n)))

@show.when_type(Assign)
def show_assign(assign, indent):
    indent(colorkeyword("assign"))
    with indent.sub() as i:
        for n in assign.targets:        
            show(n, i)
    p(indent, colorop("="))
    with indent.sub():
        show(assign.value,indent)

@show.when_type(With)
def show_with(wit, indent):
    with indent.keyword("with"):        
        with indent.section("ctx"):
            show(wit.context_expr,indent)

        with indent.section("body"):
            show(wit.body,indent)

@show.when_type(Attribute)
def show_attrib(attrib, indent):
    ctxname = NAMES.get(type(attrib.ctx),type(attrib.ctx))

    with indent.section("attrib [%s]" % ctxname):
        with indent.section("in"):
            show(attrib.value,indent)       
        with indent.section("this"):
            indent(colorname(attrib.attr))
        
@show.when_type(Load)
def show_load(load,indent):
    pass#look(load)

@show.when_type(Index)
def show_index(idx, indent):
    with indent.section("index"):
        show(idx.value, indent)

@show.when_type(Slice)
def show_index(idx, indent):    
    with indent.section("slice"):
        with indent.section("lower"):
            show(idx.lower, indent)

        with indent.section("step"):
            show(idx.step, indent)

        with indent.section("upper"):
            show(idx.upper, indent)


@show.when_type(Subscript)
def show_subscript(ss,indent):
    with indent.section("subscript"):
        show(ss.value,indent)
        show(ss.slice,indent)
        

@show.when_type(ListComp)
def show_listcomp(lc, indent):
    indent(colorhelper("list comprehension"))
    with indent.sub():

        indent(colorhelper("expr"))
        with indent.sub():
            show(lc.elt,indent)

        indent(colorhelper("generators"))
        with indent.sub():
            show(lc.generators, indent)

@show.when_type(Expr)
def show_expr(exp, indent):
    show(exp.value,indent)


@show.when_type(Str)
@show.when_type(str)
def show_str(st, indent):
    try:
        indent(colorliteral("\"%s\"" %  st.s))
    except:
        indent(colorliteral("\"%s\"" %  st))

@show.when_type(ast.Call)
def show_call(call, indent):
    with indent.section("call"):
        show(call.func,indent)
    
    if call.args:
        with indent.section("args"):
            show(call.args,indent)

@show.when_type(comprehension)
def show_compr(com, indent):
    with indent.section("comprehension"):

        with indent.keyword("for"):
            show(com.target,indent)


        with indent.keyword("in"):
            show(com.iter,indent)


        with indent.keyword("if"):
            show(com.ifs,indent)

@show.when_type(Compare)
def show_compare(compare, indent):
#    print(see(compare))
    with indent.section("compare"):
        with indent.section("left"):
            show(compare.left,indent)

        with indent.section("ops"):
            for op in compare.ops:
                indent("| " + colorop(NAMES.get(type(op),str(op))))

        with indent.section("comparators"):
            show(compare.comparators,indent)


@show.when_type(For)
def show_for(fo, indent ):
    with indent.keyword("for"):
        show(fo.target, indent)

    with indent.keyword("in"):    
        show(fo.iter, indent)


@show.when_type(List)
def show_List(l, indent):
    if l.elts:
        with indent.keyword("list("):        
            for item in l.elts:
                show(item,indent)
        indent(colorkeyword(")"))
    else:
        p(indent, colorkeyword("list()"))

@show.when_type(Tuple)
def show_Tuple(l, indent):
    if l.elts:
        with indent.keyword("tuple("):        
            for item in l.elts:
                show(item,indent)
        indent(colorkeyword(")"))
    else:
        p(indent, colorkeyword("tuple()"))

@show.when_type(Dict)
def show_dict(d,indent):
    with indent.section("keys"):
        show(d.keys,indent)
    with indent.section("values"):
        show(d.values,indent)


@show.when_type(Yield)
def show_yield(yiel, indent):
    with indent.keyword("yield"):
        show(yiel.value,indent)

@show.when_type(FunctionDef)
def show_def(func, indent):
    def hasArgs(args):
        return bool(args.args) or args.vararg or args.kwarg

    p(indent,"%s %s %s" % ( colorkeyword("def"),
                                colorname(func.name),
                                colorkeyword(":")))

    if hasArgs(func.args):
        with indent.section("arguments"):    
            show(func.args,indent)
    with indent.section("body"):        
        show(func.body, indent)


@show.when_type(ClassDef)   
def show_class(clazz, indent):
    with indent.keyword("class"):
        indent(clazz.name)        

        with indent.section("bases"):
            show(clazz.bases,indent)

        with indent.section("decorators"):
            show(clazz.decorator_list,indent)

        with indent.section("body"):
            show(clazz.body,indent)
    

@show.when_type(ImportFrom)
def show_importf(impf, indent):
    with indent.section("import from %s" % colorname(str(impf.module))):
        show(impf.names,indent)


@show.when_type(alias)
def show_alias(a, indent):
    indent(colorname(a.name) + colorkeyword(" as ") + colorname(a.asname))


@show.when_type(Import)
def show_import(imp, indent):
    with indent.section("import"):
        show(imp.names,indent)

@show.when_type(If)
def show_if(iff, indent):
    with indent.keyword("if"):
        with indent.section("condition"):
            show(iff.test,indent)

        with indent.section("then"):
            show(iff.body,indent)

        if iff.orelse:
            with indent.section("else"):
                show(iff.orelse,indent)

@show.when_type(While)
def show_while(whil, indent):
    with indent.keyword("while"):
        with indent.section("condition"):
            show(whil.test,indent)

        with indent.section("repeat"):
            show(whil.body,indent)

        if whil.orelse:
            with indent.section("else"):
                show(whil.orelse,indent)


@show.when_type(Raise)
def show_raise(rais,indent):
    with indent.keyword("raise"):        
        show(rais.exc,indent)
        if rais.cause:
            with indent.keyword("from"):
                show(rais.cause,indent)





def look(obj):print(see(obj))

NAMES = {
    Add : "+",
    Sub : "-",
    LtE : "<=",
    Gt : ">",
    GtE:">=",
    Lt :"<",
    Mult: "*",
    Div : "/",
    BitAnd : "&",
    BitOr: "|",
    FloorDiv : "//",  
    Not :"not",
    Invert : "~",
    Mod :"%",
    Load: "LOAD",
    Store: "STORE",

}


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename) as f:
        a = ast.parse(source = f.read())
        show(a,Indenter())
