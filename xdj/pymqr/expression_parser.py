import compilers
import expressions
avgFuncs=";avg;sum;min;max;push;addToSet;strLenBytes;strLenCP;strLenBytes;sqrt;toString;type;last;first;literal;"
op={
    "==":"$eq",
    "!=":"$ne",
    ">":"$gt",
    "<":"$lt",
    ">=":"$gte",
    "<=":"$lte",
    "+":"$add",
    "-":"$subtract",
    "*":"$multiply",
    "/":"$divide",
    "%":"$mod",
    "^":"$pow"
}
mathOp=";$add;$subtract;$multiply;$divide;$mod;";
matchOp=";$eq;$ne;$gt;$lt;$gte;$lte;";
logical={
        "&&":"$and",
        "||":"$or",
        "and":"$and",
        "or":"$or"
}
def do_part_with_params(expr,*args,**kwargs):
    params =[]
    if kwargs=={}:
        for i in range(0,args.__len__(),1):
            expr=expr.replace("{"+i.__str__()+"}","$get_params("+i.__str__()+")")
            params.append(args[i])
    else:
        i=0
        for k,v in kwargs.items():
            expr = expr.replace("@" + k  , "$get_params(" + i.__str__() + ")")
            params.append(v)
            i+=1
    return expr,params

def to_mongobd(expr,*args,**kwargs):
    if type(expr) not in [str,unicode]:
        return expr
    _expr,params = do_part_with_params(expr,*args,**kwargs)
    tree=compilers.compile_expression(_expr)
    return to_mongodb_expr(tree,params,True)
def to_mongobd_match(expr,*args,**kwargs):
    _expr,params = do_part_with_params(expr,*args,**kwargs)
    tree=compilers.compile_expression(_expr)
    return to_mongodb_expr(tree,params,False)



def to_mongodb_expr(fx,params,forSelect=False,forNot=False,prefix=None):
    import re
    if isinstance(fx,expressions.StringLiteralExpression):
        return fx.value
    if isinstance(fx,expressions.NumericLiteralExpression):
        return fx.value
    if isinstance(fx,expressions.UnaryExpression):
        if fx.type=="-":
            return -1*to_mongodb_expr(fx.argument,params,forSelect,True)
        if fx.type=="!":
            if(forSelect):
                ret={
                    "$not":[to_mongodb_expr(fx.argument,params,forSelect)]
                }
                return ret
            else:
                ret=to_mongodb_expr(fx.argument,params,forSelect,True)
                return ret

    if isinstance(fx,expressions.IdentifierExpression):
        if prefix!=None:
            return prefix+fx.name
        else:
            return fx.name

    if isinstance(fx,expressions.MemberExpression):
        left = to_mongodb_expr(fx.object, params, forSelect)
        if prefix!=None:
            if fx.property.name:
                if type(left) in [str,unicode]:
                    return prefix + left + "." + fx.property.name
                else:
                    return prefix + left.name + "." + fx.property.name
            else:
                return prefix + left.name + "." + fx.property.raw
        else:
            if fx.property.name:
                if type(left) in [str,unicode]:
                    return left + "." + fx.property.name
                return left.name + "." + fx.property.name
            else:
                if type(left) in [str,unicode]:
                    return left + "." + fx.property.raw
                return left.name + "." + fx.property.raw

    if isinstance(fx,expressions.BinaryExpression):
        right = to_mongodb_expr(fx.right, params, True, False, prefix)
        left = to_mongodb_expr(fx.left, params, True, False, prefix)
        if fx.operator=="==":
            if type(left) in [str,unicode]:
                if type(right) in [str,unicode] and (not forSelect):
                    left = to_mongodb_expr(fx.left, params, True, False)
                    if forNot:
                        return {
                            left:{
                                "$ne": re.compile("^"+right+"$",re.IGNORECASE)
                            }
                        }
                    else:
                        return {
                            left: {
                                "$regex": re.compile("^" + right + "$", re.IGNORECASE)
                            }
                        }
                if not forSelect:
                    return {
                        to_mongodb_expr(fx.left,params,True,False,prefix):right
                    }
                else:
                    return {
                        "$eq":[to_mongodb_expr(fx.left,params,True,False,"$"),
                               to_mongodb_expr(fx.right,params,True,False,"$")]
                    }
        mOp=op.get(fx.operator)
        if mOp != None:
            if not forSelect and matchOp.index(mOp)>-1:
                return {
                    left:{
                        mOp:right
                    }
                }
            return {
                mOp:[
                    to_mongodb_expr(fx.left,params,True,False,"$"),
                    to_mongodb_expr(fx.right,params,True,False,"$")
                ]
            }
        if fx.type==expressions.expression_types.LOGICAL_EXP:
            return {
                logical.get(fx.operator):[
                    to_mongodb_expr(fx.left,params,True,forNot),
                    to_mongodb_expr(fx.right,params,True,forNot)
                ]
            }

    if isinstance(fx,expressions.CallExpression):
        if fx.callee.name=="exists":
            return {
                to_mongodb_expr(fx.arguments[0],params,True,forNot):{
                    "$exists":not forNot
                }
            }
        if avgFuncs.find(";"+fx.callee.name+";")>-1:
            return {
                "$" + fx.callee.name:to_mongodb_expr(fx.arguments[0],True,False,"$")
            }
        if fx.callee.name=="$get_params":
            return params[fx.arguments[0].value]
        if fx.callee.name=="expr":
            return {
                "$expr":to_mongodb_expr(fx.arguments[0],params,True,forNot,"$")
            }
        if fx.callee.name=="expr":
            left=to_mongodb_expr(fx.arguments[0],params,True,forNot)
            right=to_mongodb_expr(fx.arguments[1],params,True,forNot)
            if fx.arguments.__len__()==2:
                if forNot:
                    ret={
                        left:{
                            "$ne":{
                                "$regex":re.compile(right)
                            }
                        }
                    }
                else:
                    ret={
                        left:{
                            "$regex":re.compile(right)
                        }
                    }
            elif fx.arguments.__len__()==3:
                ret={
                    left:{
                        "$regex":re.compile(right,to_mongodb_expr(fx.arguments[2],params,True,forNot))
                    }
                }
            return ret
        if fx.callee.name=="switch":
            ret={
                "$switch":{
                    "branches":[],
                    "default":to_mongodb_expr(fx.arguments[fx.arguments.__len__()-1],params,True,forNot,"$")
                }
            }
            for i in range(0,fx.arguments.__len__()-1,1):
                ret["$switch"]["branches"].append(to_mongodb_expr(fx.arguments[i],params,True,forNot,"$"))
            return ret
        if fx.callee.name=="case":
            if fx.arguments.__len__()<2:
                raise Exception("'case' must have 2 params: the first is logical and second for true case")
            return {
                "case":to_mongodb_expr(fx.arguments[0],params,True,forNot,"$"),
                "then":to_mongodb_expr(fx.arguments[1],params,True,forNot,"$")
            }
        if fx.callee.name in ["if","iif"]:
            return {
                "$cond":{
                    "if":to_mongodb_expr(fx.arguments[0],params,True,forNot,"$"),
                    "then":to_mongodb_expr(fx.arguments[1],params,True,forNot,"$"),
                    "else":to_mongodb_expr(fx.arguments[2],params,True,forNot)
                }
            }
        if fx.callee.name=="in" and not forSelect:
            field=to_mongodb_expr(fx.arguments[0],params,True,forNot)
            if type(field) not in [str,unicode]:
                raise Exception("match or where with $in must be begin with field name, not object")
            return {
                field:{
                    "$in":to_mongodb_expr(fx.arguments[1],params,True,forNot,"$")
                }
            }
        if fx.callee.name=="dateToString":
            paramIndexs = ['date','format', 'timezone']
            ret={
                "$dateToString":{}
            }
            for i in range(0,fx.arguments.__len__(),1):
                ret["$dateToString"].update({
                    paramIndexs[i]:to_mongodb_expr(fx.arguments[i],params,True,forNot,"$")
                })
            return ret
        if fx.callee.name=="dateFromString":
            paramIndexs = ['dateString', 'format', 'timezone', 'onNull', 'onError']
            ret={
                "$dateFromString":{}
            }
            for i in range(0,fx.arguments.__len__(),1):
                ret["$dateFromString"].update({
                    paramIndexs[i]: to_mongodb_expr(fx.arguments[i], params, True, forNot, "$")
                })
            return ret
        if fx.callee.name=="dateToParts":
            paramIndexs=['date','timezone','iso8601']
            ret={
                "$dateToParts":{}
            }
            for i in range(0, fx.arguments.__len__(), 1):
                ret["$dateToParts"].update({
                    paramIndexs[i]: to_mongodb_expr(fx.arguments[i], params, True, forNot, "$")
                })
            return ret;
        if fx.callee.name in ["hour","minute","dayOfMonth","dayOfYear",'second']:
            paramIndexs=["date","timezone"]
            ret={
                "$"+fx.callee.name:{}
            }
            for i in range(0, fx.arguments.__len__(), 1):
                ret["$"+fx.callee.name].update({
                    paramIndexs[i]: to_mongodb_expr(fx.arguments[i], params, True, forNot, "$")
                })
            return ret
        if fx.callee.name=="dateFromParts":
            paramIndexs = ["year", "month", "day", "hour", "minute", "second", "millisecond", "timezone"]
            ret = {"$dateFromParts":{}}
            for i in range(0, fx.arguments.__len__(), 1):
                ret["$dateFromParts"].update({
                    paramIndexs[i]: to_mongodb_expr(fx.arguments[i], params, True, forNot, "$")
                })
            return ret
        if fx.callee.name in ["rtrim","ltrim"]:
            paramIndexs = ["input", "chars"]
            ret={"$"+fx.callee.name:{}}
            for i in range(0, fx.arguments.__len__(), 1):
                ret["$"+fx.callee.name].update({
                    paramIndexs[i]: to_mongodb_expr(fx.arguments[i], params, True, forNot, "$")
                })
            return ret
        if fx.callee.name=="ceil":
            return {
                "$ceil":to_mongodb_expr(fx.arguments[0], params, True, forNot, "$")
            }
        if fx.callee.name in ["arrayToObject",'reverseArray']:
            return {
                "$" + fx.callee.name:to_mongodb_expr(fx.arguments[0],params,True,forNot,"$")
            }
        if fx.callee.name=="reduce":
            paramIndexs = ["input", "initialValue", "in"]
            ret={
                "$" + fx.callee.name:{}
            }
            for i in range(0, fx.arguments.__len__(), 1):
                ret["$"+fx.callee.name].update({
                    paramIndexs[i]: to_mongodb_expr(fx.arguments[i], params, True, forNot, "$")
                })
            return ret
        if fx.callee.name=="convert":
            paramIndexs = ['input', 'to', 'onNull', 'onError']
            ret={"$convert":{}}
            for i in range(0, fx.arguments.__len__(), 1):
                ret["$convert"].update({
                    paramIndexs[i]: to_mongodb_expr(fx.arguments[i], params, True, forNot, "$")
                })
            return ret
        if fx.callee.name=='filter':
            ret = {}
            paramIndexs = ['input', 'as', 'cond']
            prefix = ["$", None, "$"]
            for i in range(0, fx.arguments.__len__(), 1):
                ret["$filter"].update({
                    paramIndexs[i]: to_mongodb_expr(fx.arguments[i], params, True, forNot, prefix[i])
                })
            return ret
        if fx.callee.name=="type":
            if fx.arguments.__len__()==2:
                field = to_mongodb_expr(fx.arguments[0], params, True, forNot, "$")
                val = to_mongodb_expr(fx.arguments[1], params, True, forNot, "$")
                if forNot:
                    return {
                        field:{
                            "$not":{
                                "$type":val
                            }
                        }
                    }
                else:
                    return {
                        field:{
                            "$type":val
                        }
                    }
            else:
                return {
                    "$type":to_mongodb_expr(fx.arguments[0], params, True, forNot, "$")
                }
        if fx.callee.name=="size":
            return {
                "$size":to_mongodb_expr(fx.arguments[0],params,True,forNot,"$")
            }
        if fx.callee.name=="mergeObjects":
            if fx.arguments.__len__()==1:
                return {
                    "$mergeObjects": to_mongodb_expr(fx.arguments[0], params, True, forNot, "$")
                }
            else:
                ret={
                    "$mergeObjects":[]
                }
                for arg in fx.arguments:
                    ret["$mergeObjects"].append(to_mongodb_expr(arg,params,True,forNot,"$"))
                return ret
        ret={"$"+fx.callee.name:[]}

        for arg in fx.arguments:
            ret["$"+fx.callee.name].append(to_mongodb_expr(arg,params,True,forNot,"$"))
        return ret
