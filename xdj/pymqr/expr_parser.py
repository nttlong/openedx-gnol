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

PERIOD_CODE = 46 # '.'
COMMA_CODE  = 44 # ','
SQUOTE_CODE = 39 #single quote
DQUOTE_CODE = 34 #double quotes
OPAREN_CODE = 40 # (
CPAREN_CODE = 41 # )
OBRACK_CODE = 91 # [
CBRACK_CODE = 93 # ]
QUMARK_CODE = 63 # ?
SEMCOL_CODE = 59 # ;
COLON_CODE  = 58 # :
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
isDecimalDigit = lambda ch: (ch >= 48 and ch <= 57)
#`$` and `_` or A...Z or a...z or any non-ASCII that is not an operator
isIdentifierStart = lambda ch:(ch == 36) or (ch == 95) or (ch >= 65 and ch <= 90) or (ch >= 97 and ch <= 122) or (ch >= 128 and not(binary_ops.has_key(chr(ch))))
# `$` and `_` or A...Z or a...z or any non-ASCII that is not an operator
isIdentifierPart = lambda  ch: (ch == 36) or (ch == 95) or (ch >= 65 and ch <= 90) or (ch >= 97 and ch <= 122) or (ch >= 48 and ch <= 57) or (ch >= 128 and not (binary_ops.has_key(chr(ch))))

#Utility function (gets called from multiple places)
#Also note that `a && b` and `a || b` are *logical* expressions, not binary expressions
def createBinaryExpression(operator, left, right):
    type = lambda :LOGICAL_EXP if  (operator == '||' or operator == '&&') else BINARY_EXP
    return dict(
        type=type,
        operator=operator,
        left=left,
        right = right
    )
def gobbleBinaryOp(index,expr,max_binop_len):
    if not type(index) is int:
        return
    """
     Search for the operation portion of the string (e.g. `+`, `===`)
    Start by taking the longest possible binary operations (3 characters: `===`, `!==`, `>>>`)
    and move down from 3 to 2 to 1 character until a matching binary operation is found
    then, return that binary operation
    :return:
    """
    index, expr=gobbleSpaces(index,expr)
    biop = None
    to_check = expr[index: max_binop_len]
    tc_len = to_check.__len__()
    while tc_len > 0:
        """
        Don't accept a binary op when it is an identifier.
        Binary ops that start with a identifier-valid character must be followed
        by a non identifier-part valid character
        """
        if binary_ops.has_key(to_check) and\
            (
                not (isIdentifierStart(exprICode(index))) or
                (
                        (index+to_check.__len__()<expr.__len__()) and\
                        not(isIdentifierPart(exprICode(index+to_check.__len__())))

                )
            ):
            index += tc_len
            return index,to_check
        return index,False
def exprI(i,expr):
    return expr[i]
def exprICode(i,expr):
    try:
        return ord(expr[i])
    except Exception as ex:
        return
def getMaxKeyLen(obj):
    max_len = 0

    for key, value in obj.items():
        len = key.__len__()
        if len > max_len:
            max_len = len
    return max_len
def gobbleToken(index,expr,max_unop_len,length):
    ch= None
    to_check = None
    tc_len = None
    index, expr=gobbleSpaces(index,expr)
    ch = exprICode(index,expr)
    if isDecimalDigit(ch) or ch == PERIOD_CODE: #Char code 46 is a dot `.` which can start off a numeric literal
        return gobbleNumericLiteral(index,expr)
    elif ch == SQUOTE_CODE or ch == DQUOTE_CODE: #Single or double quotes
        return gobbleStringLiteral(index,expr)
    elif ch == OBRACK_CODE:
        return gobbleArray(index,expr)
    else:
        to_check = expr[index: max_unop_len]
        tc_len = to_check.__len__()
        while tc_len>0:
            """
            Don't accept an unary op when it is an identifier
            Unary ops that start with a identifier-valid character must be followed
            by a non identifier-part valid character
            """
            if unary_ops.has_key(to_check) and\
                    (
                       (not(isIdentifierStart(exprICode(index))))or
                       (
                               (index+to_check.__len__() < expr.__len__()) and\
                               (not(isIdentifierPart(exprICode(index+to_check.__len__()))))

                       )
                    ):
                index += tc_len
                return {
                    "type": UNARY_EXP,
                    "operator": to_check,
                    "argument": gobbleToken(),
                    "prefix": True
                }
            to_check = to_check[0:tc_len]
            tc_len-=1
        if isIdentifierStart(ch) or ch==OPAREN_CODE:
            return gobbleVariable(index,expr,length)
    return index,False
def gobbleSpaces(index,expr):
    if not type(index) is int:
        return

    """
    Push `index` up to the next non-space character
    :return:
    """
    ch=exprICode(index,expr)
    while ch in [32,9,10,13]:
        ch=exprICode(index,expr)
        index = index +1
    return index,expr
def gobbleBinaryExpression(index,expr,length,max_binop_len):
    if not type(index) is int:
        return
    ch_i = None
    node = None
    biop = None
    prec = None
    stack = None
    biop_info = None
    left = None
    right = None
    i = None
    #First, try to get the leftmost thing
    #Then, check to see if there's a binary operator operating on that leftmost thing
    index,left = gobbleToken(index,expr,max_binop_len,length)
    index,biop = gobbleBinaryOp(index,expr,max_binop_len)
    if not biop: #If there wasn't a binary operator, just return the leftmost node
        return index,left
    #Otherwise, we need to start a stack to properly place the binary operations in their
    #precedence structure
    index, prec =binaryPrecedence(biop)
    biop_info = {"value": biop, "prec": prec}
    index,right = gobbleToken()
    if not right:
        raise Exception("Expected expression after {0} , {1}".format(biop, index))
    stack = [left, biop_info, right]
    #Properly deal with precedence using [recursive descent](http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm)
    index,biop = gobbleBinaryOp()
    while biop:
        index,prec = binaryPrecedence(biop)
        index,biop = gobbleBinaryOp()
        if prec==0:
            break
        biop_info = {"value": biop, "prec": prec}
        #// Reduce: make a binary expression from the three topmost entries.
        while stack.__len__() > 2 and prec <= stack[stack.length - 2]["prec"]:
            right = stack.pop()
            biop = stack.pop()["value"]
            left = stack.pop()
            node = createBinaryExpression(biop, left, right)
            stack.push(node)

        node =gobbleToken()
        if not node:
            raise Exception("Expected expression after ".format(biop, index))
        stack.push(biop_info, node)
    i = stack.length - 1
    node = stack[i]
    while i>1:
        node = createBinaryExpression(stack[i - 1]["value"], stack[i - 2], node)
        i -= 2
    return node
#The main parsing function. Much of this code is dedicated to ternary expressions
def gobbleExpression(index,expr,length,max_binop_len):
    """
    The main parsing function. Much of this code is dedicated to ternary expressions
    :return:
    """
    """
    var test = gobbleBinaryExpression(),
                             consequent, alternate;
    """
    index,test = gobbleBinaryExpression(index,expr,length,max_binop_len)
    consequent = None
    alternate = None
    index, expr=gobbleSpaces(index,expr)
    if exprICode(index,expr)== QUMARK_CODE:#Ternary expression: test ? consequent : alternate
        index = index +1
        consequent = gobbleExpression()
        if not consequent:
            raise Exception('Expected expression {0}'.format(index))
        gobbleSpaces()
        if exprICode(index) == COLON_CODE:
            index = index +1
            alternate = gobbleExpression()
            if not alternate:
                raise Exception('Expected expression {0}'.format(index))

            return index,{
                "type": CONDITIONAL_EXP,
                "test": test,
                "consequent": consequent,
                "alternate": alternate
            }
        else:
            raise Exception("Expected :{0}".format(index))
    else:
        return index,test
# Returns the precedence of a binary operator or `0` if it isn't a binary operator
def binaryPrecedence(op_val):
    return binary_ops.get(op_val, 0)
def gobbleNumericLiteral(index,expr):
    number = ''
    ch = None
    chCode = None
    while isDecimalDigit(exprICode(index,expr)):
        index+=1
        number += exprI(index,expr)
    if exprICode(index,expr) == PERIOD_CODE:#can start with a decimal marker
        index+=1
        number += exprI(index,expr)
        while isDecimalDigit(exprICode(index,expr)):
            index +=1
            number += exprI(index,expr)
    ch = exprI(index,expr)
    if ch in ['e','E']:#exponent marker
        index +=1
        number += exprI(index,expr)
        ch = exprI(index)
        if ch in ['+','-']:#exponent sign
            index+=1
            number += exprI(index,expr)
        while isDecimalDigit(exprICode(index,expr)):
            index+=1
            number += exprI(index,expr)

        if not isDecimalDigit(exprICode(index-1,expr)):
            raise Exception('Expected exponent {0} at {1}'.format (number + exprI(index),index))
    chCode = exprICode(index,expr)
    #Check to make sure this isn't a variable name that start with a number (123abc)
    if isIdentifierStart(exprICode(index,expr)):
        raise Exception("Variable names cannot start with a number {0} at {1}".format(number + exprI(index),index))
    elif chCode == PERIOD_CODE:
        raise Exception('Unexpected period {0}'.format(index))
    return index,{
        "type": LITERAL,
        "value": number,#float(number)
        "raw": number
    }
def gobbleStringLiteral(index,expr,length):
    str = ''
    index +=1
    quote = exprI(index)
    closed = False
    ch= None
    while index <length:
        index+=1
        ch = exprI(index)
        if ch == quote:
            closed = True
            break
        elif ch=="\\":# Check for all of the common escape codes
            if ch == "n":
                str += '\\n'
            elif ch== 'r':
                str += '\\n'
            elif ch=='t':
                str += '\\n'
            elif ch=='b':
                str += '\\n'
            elif ch== 'f':
                str+="\\f"
            elif ch == "v":
                str+="\\0xB"
            else:
                str+=ch
        else:
            str += ch
    if not closed:
        raise Exception('Unclosed quote after {0} at {1}"'.format(str , index));
    return index,{
        "type": LITERAL,
        "value": str,
        "raw": quote + str + quote
    }
def gobbleIdentifier(index,expr,length):
    ch = exprICode(index,expr)
    start = index
    identifier=None
    if isIdentifierStart(ch):
        index+=1
    else:
        raise Exception('Unexpected '.format(exprI(index), index))
    while index<length:
        ch = exprICode(index,expr)
        if isIdentifierPart(ch):
            index+=1
        else:
            break
    identifier = expr[start: index]
    if literals.has_key(identifier):
        return index,{
            "type": LITERAL,
            "value": literals[identifier],
            "raw": identifier
            }
    elif identifier=="this":
        return index,{ "type": THIS_EXP }
    else:
        return index,{
            "type": IDENTIFIER,
            "name": identifier
        }
def gobbleArguments(index,expr,length,termination):

    ch_i=None
    args = []
    node=None
    closed = False
    while index < length:
        index, expr=gobbleSpaces(index,expr)
        ch_i = exprICode(index)
        if ch_i == termination:
            closed = True
            index+=1
            break;
        elif ch_i == COMMA_CODE:
            index+=1
        else:
            node = gobbleExpression()
            if not node or node["type"]==COMPOUND:
                raise Exception('Expected comma {)}'.format(index))
            args.append(node)

    if not closed:
         raise Exception('Expected {0} at {1}'.format(chr(termination),index))
    return args
def gobbleVariable(index,expr,length):
    ch_i=None
    node=None
    if ch_i == OPAREN_CODE:
        index,node = gobbleGroup(index,expr)
    else:
        index,node = gobbleIdentifier(index,expr,length)
    index,expr=gobbleSpaces(index,expr)
    ch_i = exprICode(index,expr)
    while ch_i == PERIOD_CODE or ch_i == OBRACK_CODE or ch_i == OPAREN_CODE:
        index+=1
        if ch_i == PERIOD_CODE:
            gobbleSpaces()
            node = {
                "type": MEMBER_EXP,
                "computed": False,
                "object": node,
                "property": gobbleIdentifier()
            }
        elif ch_i == OBRACK_CODE:
            node = {
                "type": MEMBER_EXP,
                "computed": True,
                "object": node,
                "property": gobbleExpression()
            }
            gobbleSpaces()
            ch_i = exprICode(index)
            if ch_i != CBRACK_CODE:
                raise Exception('Unclosed ['+ index.__str__())
            index+=1
        elif ch_i == OPAREN_CODE:
            node = {
                "type": CALL_EXP,
                'arguments': gobbleArguments(CPAREN_CODE),
                "callee": node
            }
        gobbleSpaces()
        ch_i = exprICode(index)
    return index,node
def gobbleGroup(index,expr):
    index+=1
    index,node = gobbleExpression(index,expr)
    gobbleSpaces()
    if exprICode(index)== CPAREN_CODE:
        index+=1
        return index,node
    else:
        raise Exception('Unclosed ('+ index.__str__())
def gobbleArray(index,expr):
    index+=1
    return index,{
        "type": ARRAY_EXP,
        "elements": gobbleArguments(CBRACK_CODE)
    }
def parse_to_tree(expr):
    """

    :param expr:
    :return:
    """
    max_unop_len = getMaxKeyLen(unary_ops)
    max_binop_len = getMaxKeyLen(binary_ops)
    #`index` stores the character number we are currently at while `length` is a constant
    #All of the gobbles below will modify `index` as we move along
    index = 0
    length = expr.__len__()


    nodes = []
    ch_i=None
    node=None
    while index < length:
        ch_i = exprICode(index,expr)
        if ch_i == SEMCOL_CODE or ch_i == COMMA_CODE:
            index+=1
        else:
            index,node = gobbleExpression(index,expr,length,max_binop_len)
            if node:
                nodes.append(node)
            elif index < length:
                raise Exception('Unexpected "{0}" at {1}'.format(exprI(index,expr), index))

    if nodes.length == 1:
        return nodes[0]
    else:
        return {
            "type": COMPOUND,
            "body": nodes
        }

