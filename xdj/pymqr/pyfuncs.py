import re
import inspect
def __avg_consume__(*args,**kwargs):
    fn = "$" + inspect.stack()[1][3]
    if args.__len__() ==1:
        return __create_item__(fn,args[0])
    elif args.__len__()>1:
        ret = {
            fn: []
        }
        for item in args:
            ret[fn].append(__get_field_expr__(item))
        return __create__(ret)
def __get_field_expr__(x):
    import pydocs
    if isinstance(x,pydocs.Fields):
        if x.__tree__==None:
            return "$"+x.__name__
        else:
            return x.__tree__
    else:
        return x
def __create__(expr):
    import pydocs
    ret = pydocs.Fields()
    setattr(ret, "__tree__", expr)
    return ret
def __create_array__(fn,*args):
    ret = {
        fn: []
    }
    for item in args:
        ret[fn].append(__get_field_expr__(item))
    return __create__(ret)
def __comsume_with_array__(*args):
    fn= "$"+inspect.stack()[1][3]

    ret = {
        fn: []
    }
    for item in args:
        ret[fn].append(__get_field_expr__(item))
    return __create__(ret)
def __create_item__(fn,item):
    ret = {
        fn: __get_field_expr__(item)
    }
    return __create__(ret)
def __comsume_with_item__(item):
    fn = "$" + inspect.stack()[1][3]

    ret = {
        fn: __get_field_expr__(item)
    }
    return __create__(ret)


def regex(field, partern, ignore_case=True):
    import pydocs
    if  isinstance(field,pydocs.Fields):
        if ignore_case:
            field.__tree__={
                field.__name__:{
                    "$regex":re.compile(partern,re.IGNORECASE)
                }
            }
            return field
        else:
            field.__tree__ = {
                field.__name__: {
                    "$regex": re.compile(partern)
                }
            }
            return field
def concat(*args,**kwargs):
    import pydocs
    expr = {
        "$concat": []
    }
    for item in args:
        if isinstance(item, pydocs.Fields):
            expr["$concat"].append(__get_field_expr__(item))
        else:
            expr["$concat"].append(item)
    ret = pydocs.Fields()
    setattr(ret, "__tree__", expr)
    return ret
def iif(test,true_case,flase_case):
    """
    { $cond: { if: <boolean-expression>, then: <true-case>, else: <false-case-> } }
    :param test:
    :param true_case:
    :param flase_case:
    :return:
    """
    import pydocs
    expr={
        "$cond":{
            "if":__get_field_expr__(test),
            "then":__get_field_expr__(true_case),
            "else":__get_field_expr__(flase_case)
        }
    }
    ret = pydocs.Fields()
    setattr(ret, "__tree__", expr)
    return ret
def case(test,result):
    """
     { case: <expression>, then: <expression> }
    :param test:
    :param result:
    :return:
    """
    import pydocs
    expr = {
        "case":__get_field_expr__(test),
        "then":__get_field_expr__(result)

    }
    ret = pydocs.Fields()
    setattr(ret, "__tree__", expr)
    return ret
def switch(*args,**kwargs):
    """
    $switch: { branches: [{ case: <expression>, then: <expression> },{ case: <expression>, then: <expression> },..],default: <expression>}
    :param args:
    :param kwargs:
    :return:
    """
    import pydocs
    branches=[]
    default=__get_field_expr__(args[args.__len__()-1])
    # default = __get_field_expr__(args[args.__len__() - 1])
    # list_of_args = [x for x in args if args.index(x) < args.__len__() - 1]
    # for item in list_of_args:
    #     if isinstance(item,pydocs.Fields):
    #         branches.append(item.to_mongodb())
    #     else:
    #         branches.append(item)
    m = args.__len__()
    for i in pyrange(0,m-1,1):
        item  = args[i]
        if isinstance(item,pydocs.Fields):
            branches.append(item.to_mongodb())
        else:
            branches.append(item)
    #     branches.append(__get_field_expr__(getattr(args[i],"__tree__")))

    expr={
        "$switch":{
            "branches":branches,
            "default":default
        }
    }
    ret = pydocs.Fields()
    setattr(ret, "__tree__", expr)
    return ret
def abs(expr):
    return __create__({
        "$abs":__get_field_expr__(expr)
    })
def addToSet(expr):
    return __create__({
        "$addToSet": __get_field_expr__(expr)
    })
def allElementsTrue(*args):
    ret ={
        "$allElementsTrue":[]
    }
    for item in args:
        ret["$allElementsTrue"].append(__get_field_expr__(item))
    return __create__(ret)
def And(*args):
    return __create_array__("$and",*args)
def add(*args):
    """
    { $add: [ <expression1>, <expression2>, ... ] }
    :param args:
    :return:
    """
    return __create_array__("$add", *args)
def anyElementTrue(*args):
    return __create_array__("$anyElementTrue", *args)
def arrayElemAt(*args):
    return __create_array__("$arrayElemAt", *args)
def arrayToObject(expr):
    """
    { $arrayToObject: <expression> }
    :param expr:
    :return:
    """
    return __create_item__("$arrayToObject",expr)
def expr(expr):
    """
    { $expr: <expression> }
    :param expr:
    :return:
    """
    return __create_item__("$expr",expr)
def avg(*args,**kwargs):
    """
        { $avg: <expression> }
        :param expr:
        :return:
        """
    return __avg_consume__(*args,**kwargs)
def ceil(expr):
    """
    { $ceil: <number> }
    :return:
    """
    return __create_item__("$ceil", expr)
def cmp(expr1,expr2):
    """
    { $cmp: [ <expression1>, <expression2> ] }
    :return:
    """
    return __create_array__("$cmp", expr1,expr2)
def concatArrays(*args):
    """
    { $concatArrays: [ <array1>, <array2>, ... ] }
    :return:
    """
    return __comsume_with_array__(*args)
def convert(input,to,onError=None,onNull=None):
    """
    {
       $convert:
          {
             input: <expression>,
             to: <type expression>,
             onError: <expression>,  // Optional.
             onNull: <expression>    // Optional.
          }
    }
    :return:
    """
    ret_data=dict(
        input=__get_field_expr__(input),
        to=__get_field_expr__(to)
    )
    if onError!=None:
        ret_data.update({
            "onError":__get_field_expr__(onError)
        })
    if onNull!=None:
        ret_data.update({
            "onNull":__get_field_expr__(onNull)
        })
    return __create_item__("$convert",ret_data)
def dateFromParts(year,month=None,day=None,hour=None,minute=None,second=None,milliseconds=None,timezone=None):
    """
    { $dateFromParts :
        {'year': <year>, 'month': <month>, 'day': <day>,
        'hour': <hour>, 'minute': <minute>, 'second': <second>,
        'milliseconds': <ms>, 'timezone': <tzExpression>
        }
    }
    :return:
    """
    ret_data={
        "year":year
    }
    optionals=dict(
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        milliseconds=milliseconds,
        timezone=timezone
    )
    for k,v in optionals.items():
        if v!=None:
            ret_data.update({
                k:v
            })
    return __create_item__("$dateFromParts",ret_data)
def dateToParts(date,timezone=None,iso8601=None):
    """
    {
        $dateToParts: {
            'date' : <dateExpression>,
            'timezone' : <timezone>,
            'iso8601' : <boolean>
        }
    }
    :return:
    """
    optionals=dict(
        timezone=timezone,
        iso8601=iso8601
    )
    ret_data={
        "date":date
    }
    for k,v in optionals.items():
        if v!=None:
            ret_data.update({
                k:v
            })
    return __create_item__("$dateToParts",ret_data)
def dateFromString(dateString,format=None,timezone=None,onError=None,onNull=None):
    """
    { $dateFromString: {
         dateString: <dateStringExpression>,
         format: <formatStringExpression>,
         timezone: <tzExpression>,
         onError: <onErrorExpression>,
         onNull: <onNullExpression>
    } }
    :return:
    """
    ret_data={
        "dateString":dateString
    }
    optionals=dict(
        format=format,
        timezone=timezone,
        onNull=onNull,
        onError=onError
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$dateFromString", ret_data)
def dateToString(date,format=None,timezone=None,onNull=None):
    """
    { $dateToString: {
        date: <dateExpression>,
        format: <formatString>,
        timezone: <tzExpression>,
        onNull: <expression>
    } }
    :return:
    """
    ret_data = {
        "date": date
    }
    optionals = dict(
        format=format,
        timezone=timezone,
        onNull=onNull
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$dateToString", ret_data)
def dayOfMonth(date,timezone=None):
    """
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": date
    }
    optionals = dict(
        timezone=timezone
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$dayOfMonth", ret_data)
def dayOfWeek(date,timezone=None):
    """
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": date
    }
    optionals = dict(
        timezone=timezone
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$dayOfWeek", ret_data)
def dayOfYear(date,timezone=None):
    """
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": date
    }
    optionals = dict(
        timezone=timezone
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$dayOfYear", ret_data)

def filter(field,iter,cond):
    """
    { $filter: { input: <array>, as: <string>, cond: <expression> } }
    :return:
    """
    import pydocs

    return __create_item__("$filter", {
        "input":__get_field_expr__(field),
        "as":pydocs.get_field_expr(iter,True),
        "cond":__get_field_expr__(cond)
    })
def first(*args, **kwargs):
    """
    { $first: <expression> }
    :param field:
    :return:
    """
    return __avg_consume__(*args, **kwargs)
def floor(field):
    """
    { $floor: <number> }
    :param field:
    :return:
    """
    return __comsume_with_item__(field)
def hour(date,timezone=None):
    """
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": date
    }
    optionals = dict(
        timezone=timezone
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$hour", ret_data)
def ifNull(field,replacement):
    """
    { $ifNull: [ <expression>, <replacement-expression-if-null> ] }
    :return:
    """
    return __create_array__("$ifNull",field,replacement)
def In(field,items):
    """
    { $in: [ <expression>, <array expression> ] }
    :return:
    """
    _items=[]
    for item in items:
        _items.append(__get_field_expr__(item))
    return __create__({
        "$in":_items
    })
def indexOfArray(items,field,start=None,end=None):
    """
    { $indexOfArray: [ <array expression>, <search expression>, <start>, <end> ] }
    :return:
    """
    _items=[
        __get_field_expr__(items),
        __get_field_expr__(field)
    ]
    if start!=None:
        _items.append(__get_field_expr__(start))
    if end!=None:
        _items.append(__get_field_expr__(end))
    return __create__({
        "$indexOfArray":_items
    })
def indexOfBytes(field1,field2,start=None,end=None):
    """
    { $indexOfBytes: [ <string expression>, <substring expression>, <start>, <end> ] }
    :return:
    """
    _items = [
        __get_field_expr__(field1),
        __get_field_expr__(field2)
    ]
    if start != None:
        _items.append(__get_field_expr__(start))
    if end != None:
        _items.append(__get_field_expr__(end))
    return __create__({
        "$indexOfArray": _items
    })
def indexOfCP(field1,field2,start=None,end=None):
    """
    { $indexOfCP: [ <string expression>, <substring expression>, <start>, <end> ] }
    :return:
    """
    _items = [
        __get_field_expr__(field1),
        __get_field_expr__(field2)
    ]
    if start != None:
        _items.append(__get_field_expr__(start))
    if end != None:
        _items.append(__get_field_expr__(end))
    return __create__({
        "$indexOfCP": _items
    })
def isArray(field):
    """
    { $isArray: [ <expression> ] }
    :return:
    """
    return __comsume_with_item__(field)
def isoDayOfWeek(date,timezone=None):
    """
    { $isoDayOfWeek: <dateExpression> }
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": date
    }
    optionals = dict(
        timezone=timezone
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$isoDayOfWeek", ret_data)
def isoWeek(date,timezone=None):
    """
    { $isoWeek: <dateExpression> }
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": date
    }
    optionals = dict(
        timezone=timezone
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$isoWeek", ret_data)
def isoWeekYear(date,timezone=None):
    """
    { $isoWeekYear: <dateExpression> }
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": date
    }
    optionals = dict(
        timezone=timezone
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: v
            })
    return __create_item__("$isoWeekYear", ret_data)
def last(*args, **kwargs):
    """
    { $last: <expression> }
    :return:
    """
    return __avg_consume__(*args, **kwargs)


def let(vars,In):
    """
    {
      $let:
         {
           vars: { <var1>: <expression>, ... },
           in: <expression>
         }
    }
    :return:
    """
    _vars={}
    for k,v in vars.items():
        _vars.update({
            k:__get_field_expr__(v)
        })
    return __create__({
        "$let":{
            "vars":_vars,
            "in":__get_field_expr__(In)
        }
    })
def literal(value):
    """
    { $literal: <value> }
    :return:
    """
    return __comsume_with_item__(value)
def lg(value):
    """
    { $literal: <value> }
    :return:
    """
    return __comsume_with_item__(value)
def log(value):
    """
    { $literal: <value> }
    :return:
    """
    return __comsume_with_item__(value)

def log10(value):
    """
    { $literal: <value> }
    :return:
    """
    return __comsume_with_item__(value)
def ltrim(field,chars=None):
    """
    { $ltrim: { input: <string>,  chars: <string> } }
    :return:
    """
    ret_data = {
        "input": field
    }
    optionals = dict(
        chars=chars
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: __get_field_expr__(v)
            })
    return __create_item__("$trim", ret_data)
def map(field,In,alias):
    from . import pydocs
    from . import pyaggregatebuilders
    """
    { $map: { input: <expression>, as: <string>, in: <expression> } }
    :return:
    """
    _In = pyaggregatebuilders.Project(*In).stage
    ret_data={
        "$map":{
            "input":pydocs.get_field_expr(field),
            "as":pydocs.get_field_expr(alias,True),
            "in":_In
        }
    }
    return __create__(ret_data)
def max(*args,**kwargs):
    """
    { $max: <expression> }
    :return:
    """
    return __avg_consume__(*args,**kwargs)
def mergeObjects(*args):
    """
    { $mergeObjects: [ <document1>, <document2>, ... ] }
    :return:
    """
    return __comsume_with_array__(*args)
def meta(field):
    """
    { $meta: <metaDataKeyword> }
    :return:
    """
    return __comsume_with_item__(field)
def min(*args,**kwargs):
    """
    { $min: <metaDataKeyword> }
    :return:
    """
    return __avg_consume__(*args,**kwargs)
def millisecond(date,timezone):
    """
    { $millisecond: <dateExpression> }
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": __get_field_expr__(date)
    }
    optionals = dict(
        timezone=__get_field_expr__(timezone)
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: __get_field_expr__(v)
            })
    return __create_item__("$millisecond", ret_data)
def minute(date,timezone):
    """
    { $minute: <dateExpression> }
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": __get_field_expr__(date)
    }
    optionals = dict(
        timezone=__get_field_expr__(timezone)
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: __get_field_expr__(v)
            })
    return __create_item__("$minute", ret_data)
def month(date,timezone):
    """
    { $month: <dateExpression> }
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": __get_field_expr__(date)
    }
    optionals = dict(
        timezone=__get_field_expr__(timezone)
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: __get_field_expr__(v)
            })
    return __create_item__("$month", ret_data)
def Not(field):
    return __create__({
        "$not":__get_field_expr__(field)
    })
def objectToArray(field):
    """
    { $objectToArray: <object> }
    :return:
    """
    return __comsume_with_item__(field)
def pow(number,exponent):
    """
    { $pow: [ <number>, <exponent> ] }
    :return:
    """
    return __create__({
        "$pow":[
            __get_field_expr__(number),
            __get_field_expr__(exponent)
        ]
    })
def push(field):
    """
    { $push: <expression> }
    :return:
    """
    return __comsume_with_item__(field)
pyrange = range
def range(start,end,step=None):
    """
    { $range: [ <start>, <end>, <non-zero step> ] }
    :return:
    """
    ret_data=[__get_field_expr__(start),__get_field_expr__(end)]

    if step!=None:
        ret_data.append(__get_field_expr__(step))
    return __create__({
        "$range":ret_data
    })
def reduce(field,initialValue,In):
    """
    {
        $reduce: {
            input: <array>,
            initialValue: <expression>,
            in: <expression>
        }
    }
    :return:
    """
    return __create_item__("$reduce",{
        "input":__get_field_expr__(field),
        "initialValue":__get_field_expr__(initialValue),
        "in":__get_field_expr__(In)
    })
def reverseArray(field):
    """
    { $reverseArray: <array expression> }
    :return:
    """
    return __comsume_with_item__(field)

def rtrim(field,chars=None):
    """
    { $rtrim: { input: <string>,  chars: <string> } }
    :return:
    """
    ret_data = {
        "input": field
    }
    optionals = dict(
        chars=chars
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: __get_field_expr__(v)
            })
    return __create_item__("$rrim", ret_data)
def second(date,timezone):
    """
    { $second: <dateExpression> }
    { date: <dateExpression>, timezone: <tzExpression> }
    :return:
    """
    ret_data = {
        "date": __get_field_expr__(date)
    }
    optionals = dict(
        timezone=__get_field_expr__(timezone)
    )
    for k, v in optionals.items():
        if v != None:
            ret_data.update({
                k: __get_field_expr__(v)
            })
    return __create_item__("$second", ret_data)
def setDifference(*args,**kwargs):
    """
    { $setDifference: [ <expression1>, <expression2> ] }
    :return:
    """
    return __avg_consume__(*args,**kwargs)
def setEquals(*args,**kwargs):
    """
    { $setEquals: [ <expression1>, <expression2>, ... ] }
    :return:
    """
    return __avg_consume__(*args, **kwargs)
def setIntersection(*args, **kwargs):
    """
    { $setIntersection: [ <array1>, <array2>, ... ] }
    :return:
    """
    return __avg_consume__(*args, **kwargs)
def setIsSubset(field1,field2):
    """
    { $setIsSubset: [ <expression1>, <expression2> ] }
    :return:
    """
    return __comsume_with_array__(field1, field2)
def setUnion(*args,**kwargs):
    """{ $setUnion: [ <expression1>, <expression2>, ... ] }"""
    return __avg_consume__(*args,**kwargs)
def size(field):
    """
    { $size: <expression> }
    :return:
    """
    return __comsume_with_item__(field)
def slice(field,n,position=None):
    """
    { $slice: [ <array>, <position>, <n> ] }
    :return:
    """
    if position!=None:
        return __comsume_with_array__(field,
                                      position,
                                      n)
    else:
        return __comsume_with_array__(field,
                                      position)
def split(field,delimiter):
    """
    { $split: [ <string expression>, <delimiter> ] }
    :return:
    """
    return __comsume_with_array__(
        field,
        delimiter
    )
def sqrt(field):
    """
    { $sqrt: <number> }
    :return:
    """
    return __comsume_with_item__(field)
def stdDevPop(*args,**kwargs):
    """
       { $stdDevPop: <number> }
       :return:
       """
    return __avg_consume__(*args,**kwargs)

def stdDevSamp(*args,**kwargs):
    """
           { $stdDevSamp: <number> }
           :return:
           """
    return __avg_consume__(*args, **kwargs)
def strcasecmp(field1,field2):
    """
    { $strcasecmp: [ <expression1>, <expression2> ] }
    :return:
    """
    return __comsume_with_array__(
        field1,
        field2
    )
def strLenBytes(field):
    """
    { $strLenBytes: <string expression> }
    :return:
    """
    return __comsume_with_item__(field)
def strLenCP(field):
    """
    { $strLenCP: <string expression> }
    :return:
    """
    return __comsume_with_item__(field)
def substr(field,start,length):
    """
    { $substr: [ <string>, <start>, <length> ] }
    :return:
    """
    return __comsume_with_array__(
        field,
        start,
        length
    )
def substrBytes(field,index,count):
    """
    { $substrBytes: [ <string expression>, <byte index>, <byte count> ] }
    :return:
    """
    return __comsume_with_array__(
        field,
        index,
        count
    )
def substrCP(field,index,count):
    """
    { $substrCP: [ <string expression>, <code point index>, <code point count> ] }
    :return:
    """
    return __comsume_with_array__(
        field,
        index,
        count
    )
def sum(*args,**kwargs):
    return __avg_consume__(*args,**kwargs)
def stdDevSamp(*args,**kwargs):
    return __avg_consume__(*args, **kwargs)
def stdDevPop(*args,**kwargs):
    return __avg_consume__(*args, **kwargs)
def toBool(field):
    """
    {
       $toBool: <expression>
    }
    :return:
    """
    return __comsume_with_item__(field)
def toDate(field):
    """
    {
       $toBool: <expression>
    }
    :return:
    """
    return __comsume_with_item__(field)
def toDecimal(field):
    return __comsume_with_item__(field)
def toDouble(field):
    return __comsume_with_item__(field)
def toInt(field):
    return __comsume_with_item__(field)
def toLong(field):
    return __comsume_with_item__(field)
def toObjectId(field):
    return __comsume_with_item__(field)
def toString(field):
    return __comsume_with_item__(field)
def toLower(field):
    return __comsume_with_item__(field)
def toUpper(field):
    return __comsume_with_item__(field)
def trim(field):
    return __comsume_with_item__(field)
def trunc(field):
    return __comsume_with_item__(field)
def type(field):
    return __comsume_with_item__(field)
def week(field,timezone=None):
    if timezone:
        return __create_item__("$week",{
            "date": __get_field_expr__(field),
            "timezone":timezone
        })
    else:
        return __comsume_with_item__(field)
def year(field,timezone=None):
    if timezone:
        return __create_item__("$year",{
            "date": __get_field_expr__(field),
            "timezone":timezone
        })
    else:
        return __comsume_with_item__(field)
def zip(field):
    return __comsume_with_item__(field)



