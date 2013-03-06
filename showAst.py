#!/usr/bin/python


from simplegeneric import generic
import ast
from ast import *
from termcolor import colored
from random import choice

COLORS =['blue', 'grey', 'yellow', 'green', 'cyan', 'magenta', 'white', 'red']
COLORNUM = 0


class Indenter(object):
    def __init__(self, factor = 2,prfx=""):
        self._factor = factor
        self._prefix = prfx


    def set_prefix(self, prfx):
        self._prefix = prfx
        return self

    def __call__(self,*args):
        print(self,end="")
        print(*args)

    def __str__(self):
        return self._prefix

    def _copy(self):
        return Indenter(self.num, self._factor, self._prefix)

    def __add__(self, obj):
        if type(obj) is str:
            newprfx = self._prefix + obj
        else:
            newprfx = self._prefix + " " * (self._factor*obj)
        return Indenter(self._factor,newprfx)




def p(i, *args):
    i(*args)

def colorname(name):
    return colored(name, 'green')

def colorkeyword(name):
    return colored(name, 'yellow')

def colorhelper(text):
    return colored(text, 'blue')

def colorop(name):
    return colored(name, 'red')

def randomcolor(text):
#    return colored(text, choice(COLORS))
    global COLORNUM
    COLORNUM = (COLORNUM + 1) % len(COLORS)
    return colored(text, COLORS[COLORNUM])


@generic
def show(ast, indent=0):
    """default"""
    p(indent,type(ast))

@show.when_type(list)
def show_list(lis,indent=0):
    for item in lis:
        show(item,indent+randomcolor("| "))

@show.when_type(Name)
def show_name(name, indent):
    p(indent, colorname(name.id))

@show.when_type(BinOp)
def show_binop(bin,indent=0):
    op_name = NAMES.get(type(bin.op),type(bin.op))
    p(indent, "%s" % colorop(op_name))
    show(bin.left, indent + 1)
    show(bin.right, indent + 1)

@show.when_type(Return)
def show_return(ret,indent = 0):
    p(indent, colorkeyword("RETURN"))
    show(ret.value, indent+1)

from see import see

@show.when_type(arguments)
def show_arguments(a,indent):
#    print(see(a))

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
            show(val,indent +  randomcolor("| "))


@show.when_type(Lambda)
def show_lambda(la, indent = 0):
    p(indent,colorkeyword("lambda"))
    show(la.args , indent + 1)
    p(indent,colorhelper("body:"))
    show(la.body,indent + 1)

@show.when_type(Module)
def show_module(mod, indent = 0):
    p(indent, "[MODULE]")
    for b in mod.body:
        show(b,indent + randomcolor("| "))

def expandlist(lis, to):
    if type(to) in (list,tuple):
        to = len(to)

    return lis + [None] * (to-len(lis))

@show.when_type(Num)
def show_num(num, indent = 0):
    p(indent, num.n)

@show.when_type(Assign)
def show_assign(assign, indent = 0):
    p(indent, colorkeyword("assign"))
    for n in assign.targets:
        show(n, indent + 1)
    p(indent, colorop("="))
    show(assign.value,indent+1)

@show.when_type(ListComp)
def show_listcomp(lc, indent = 0):
    p(indent, colorhelper("list comprehension"))
    p(indent+1, colorhelper("expr"))
    show(lc.elt,indent + 2)

    p(indent+1, colorhelper("generators"))
    show(lc.generators, indent +2 )

@show.when_type(ast.Call)
def show_call(call, indent = 0):
    p(indent, colorhelper("call:"))
    show(call.func,indent+1)
    p(indent, colorhelper("args:"))
    show(call.args,indent + 2)

@show.when_type(comprehension)
def show_compr(com, indent = 0):
    p(indent, colorhelper("comprehension"))

    p(indent, colorkeyword("for"))
    show(com.target,indent + 1)

    p(indent, colorkeyword("in"))
    show(com.iter,indent + 1)

    p(indent, colorkeyword("if"))
    show(com.ifs,indent + 1)

@show.when_type(Compare)
def show_compare(compare, indent = 0):
#    print(see(compare))
    p(indent, colorhelper("compare"))

    p(indent, colorhelper("left"))
    show(compare.left,indent+1)

    p(indent, colorhelper("ops"))
    for op in compare.ops:
        p(indent + 1, "| " + colorop(
                NAMES.get(type(op),str(op))))

    p(indent, colorhelper("comparators"))
    show(compare.comparators,indent+1)


@show.when_type(For)
def show_for(fo, indent = 0 ):
    p(indent, colorkeyword("for"))
    show(fo.target, indent + 1)
    p(indent, colorkeyword("in"))
    show(fo.iter,indent+1)


@show.when_type(List)
def show_List(l, indent = 0):
    if l.elts:
        p(indent, colorkeyword("list("))
        for item in l.elts:
            show(item,indent + 1 + "° ")
        p(indent, colorkeyword(")"))
    else:
        p(indent, colorkeyword("list()"))

@show.when_type(Tuple)
def show_Tuple(l, indent = 0):
    if l.elts:
        p(indent, colorkeyword("tuple("))
        for item in l.elts:
            show(item,indent+1)
        p(indent, colorkeyword(")"))
    else:
        p(indent, colorkeyword("tuple()"))




@show.when_type(FunctionDef)
def show_def(func, indent = 0):
    p(indent,"%s %s %s" % ( colorkeyword("def"),
                                colorname(func.name),
                                colorkeyword(":")))
    p(indent+1, colorhelper("arguments:"))
    show(func.args,indent + 1 + randomcolor("| "))
    p(indent+1,colorhelper("body:"))
    show(func.body, indent + 1)



NAMES = {
    Add : "+",
    Sub : "-",
    LtE : "<=",
    Gt : ">",
    GtE:">=",
    Lt :"<"
}


print("Test")
source ="""
a = []
b = [1,2,3]

def add(x,y):
  return x+y

def sub(x,y):
  return x-y

def map(fn,seq):
  a,c = [],1
  for m in seq:
    a.append( fn(m) )
  return a+2

def map2(fn = lambda x: x,seq = []):
  return [ fn(fn(x)) for x in seq if 1<= x <= 10]
"""

a = ast.parse(source = source)
show(a,Indenter())
