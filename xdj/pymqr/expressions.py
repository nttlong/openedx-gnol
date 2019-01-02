class rec_process():
    def __init__(self):
        self.max_unop_len=0
        self.max_binop_len=0
        self.index=0
        self.length=0
        self.nodes=[]
        self.ch_i=None
        self.node=None
        self.expr=None
class BinaryExpression():
    def __init__(self, operator, left, right):
        self.operator=operator
        self.left = left
        self.right=right
        if operator in ["||","&&"]:
            self.type=expression_types.LOGICAL_EXP
        else:
            self.type=expression_types.BINARY_EXP
class expression_types:
    COMPOUND = 'Compound'
    IDENTIFIER = 'Identifier'
    MEMBER_EXP = 'MemberExpression'
    LITERAL = 'Literal'
    THIS_EXP = 'ThisExpression'
    CALL_EXP = 'CallExpression'
    UNARY_EXP = 'UnaryExpression'
    BINARY_EXP = 'BinaryExpression'
    LOGICAL_EXP = 'LogicalExpression'
    CONDITIONAL_EXP = 'ConditionalExpression'
    ARRAY_EXP = 'ArrayExpression'
class char_codes:
    PERIOD_CODE = int(46)  # '.'
    COMMA_CODE = int(44)  # ','
    SQUOTE_CODE = int(39)  # single quote
    DQUOTE_CODE = int(34)  # double quotes
    OPAREN_CODE = int(40)  # (
    CPAREN_CODE = int(41)  # )
    OBRACK_CODE = int(91)  # [
    CBRACK_CODE = int(93)  # ]
    QUMARK_CODE = int(63)  # ?
    SEMCOL_CODE = int(59)  # ;
    COLON_CODE = int(58)  # :
binary_ops = {

     '||': 1, '&&': 2, '|': 3,  '^': 4,  '&': 5,
     '==': 6, '!=': 6, '===': 6, '!==': 6,
     '<': 7,  '>': 7,  '<=': 7,  '>=': 7,
     '<<':8,  '>>': 8, '>>>': 8,
     '+': 9, '-': 9,
     '*': 10, '/': 10, '%': 10
				 }
literals = {
    'true': True,
    'false': False,
    'null': None
    }
unary_ops = {'-': True, '!': True, '~': True, '+': True}
isDecimalDigit = lambda (ch): (ch >= 48 and ch <= 57)  # 0...9
#`$` and `_` or A...Z or a...z or any non-ASCII that is not an operator
isIdentifierStart = lambda (ch):(ch == 36) or (ch == 95) or (ch >= 65 and ch <= 90) or (ch >= 97 and ch <= 122) or (ch >= 128 and not binary_ops[chr(ch)])
#`$` and `_` or A...Z or a...z or 0...9 or any non-ASCII that is not an operator
isIdentifierPart = lambda(ch) : (ch == 36) or (ch == 95) or (ch >= 65 and ch <= 90) or (ch >= 97 and ch <= 122) or (ch >= 48 and ch <= 57) or (ch >= 128 and not binary_ops[chr(ch)])

class NumericLiteralExpression():

    def __init__(self,number):
        from exceptions import ValueError
        import datetime
        self.type= expression_types.LITERAL
        self.raw=number
        try:
            self.value=int(number)
        except ValueError as ex:
            try:
                self.value=long(number)
            except ValueError as ex:
                    self.value=float(number)

class StringLiteralExpression():
    def __init__(self,str,quote):
        self.value=str
        self.type=expression_types.LITERAL
        self.raw=quote + str + quote
class ArrayExpression():
    def __init__(self,elements):
        self.type=expression_types.ARRAY_EXP
        self.elements=elements
class UnaryExpression():
    def __init__(self,operator,argument,prefix):
        self.type= expression_types.UNARY_EXP
        self.operator=operator
        self.argument=argument
        self.prefix=prefix
class MemberExpression():
    def __init__(self,computed,_object,property):
        self.type=expression_types.MEMBER_EXP
        self.computed=computed
        self.object=_object
        self.property=property
class CallExpression():
    def __init__(self,arguments,callee):
        self.type=expression_types.CALL_EXP
        self.arguments=arguments
        self.callee=callee
class LiteralExpression():
    def __init__(self,raw):
        self.type=expression_types.LITERAL
        self.value= literals.get(raw)
        self.raw=raw
class ThisExpression():
    def __init__(self):
        self.type=expression_types.THIS_EXP
class IdentifierExpression():
    def __init__(self,name):
        self.type=expression_types.IDENTIFIER
        self.name=name
class ConditionalExpression():
    def __init__(self,test,consequent,alternate):
        self.type=expression_types.CONDITIONAL_EXP
        self.test=test
        self.consequent=consequent
        self.alternate=alternate
class CompoundExpression():
    def __init__(self,body):
        self.type=expression_types.COMPOUND
        self.body=body

class BinaryOperatorInfo():
    def __init__(self,value,prec):
        self.value=value
        self.prec=prec
        """
        "value": biop, "prec": prec
        """

