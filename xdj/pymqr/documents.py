__fields_types__ = "__fields_types__"  # key of field type
__fields_docs__ = "__fields_docs__"  # key of field value
__fields_default_value__ = "__fields_default_value__"  # key of default value field
__model_name__ = "__model_name__"  # type: str # key of model name
__unique_keys__ = None
__collections_unique__= None
import uuid
import datetime
class ___CollectionMapClassWrapper__():
    def __init__(self,name):
        self.name = name
    def wrapper(self,*args,**kwargs):
        ret = None
        if self.name == None:
            ret = args[0].__new__ (BaseDocuments, self.name, args[0].__dict__)
            ret.__dict__.update ({
                "__origin__": args[0] ()
            })
            return ret
        global __unique_keys__
        if __unique_keys__ == None:
            __unique_keys__= {}
        global __collections_unique__
        if __collections_unique__ == None:
            __collections_unique__ = {}

        ret = args[0].__new__(BaseDocuments,self.name,args[0].__dict__)
        if __unique_keys__.has_key(args[0]):
            __collections_unique__.update({
                self.name:{
                    "fields":__unique_keys__.get(args[0]),
                    "has_built":False
                }
            })
        ret.__dict__.update ({
            "__collection_name__": self.name,
            "__origin__":args[0]()
        })
        return ret

def EmbeddedField(obj,name,require,default):
    obj_type = EmbededDocument () (getattr (type (obj), name))
    obj.__dict__.update ({
        name: (obj_type, require, default)
    })
def EmbeddedFieldArray(obj,name,require):
    obj_type = getattr(type(obj),name)
    if not isinstance(obj_type,BaseDocuments):
        obj_type=EmbededDocument()(getattr(type(obj),name))
    if not require:
        obj.__dict__.update ({
            name: ([obj_type], require)
        })
    else:
        obj.__dict__.update ({
            name: ([obj_type], require,[])
        })
def Collection(*args,**kwargs):
    ret = ___CollectionMapClassWrapper__(args[0])
    return ret.wrapper
def FormModel(*args,**kwargs):
    ret = ___CollectionMapClassWrapper__(None)
    return ret.wrapper

def EmbededDocument(*args,**kwargs):
    def wrapper(*args,**kwargs):
        ret = args[0].__new__(BaseDocuments,None,args[0].__dict__)
        if not isinstance(args[0],object):
            ret.__dict__.update ({
                "__origin__": args[0] ()
            })
        else:
            ret.__dict__.update ({
                "__origin__": args[0]
            })
        return ret
    return wrapper
# def EmbededArray(*args,**kwargs):
#     def wrapper(*args,**kwargs):
#         ret = args[0].__new__(BaseEmbedArray,None,args[0].__dict__)
#         ret.__dict__.update ({
#             "__origin__": args[0] ()
#         })
#         return ret
#     return wrapper
class exceptions():
    class InvalidDataType(Exception):
        def __init__(self, field_name, expectect_data_type, receive_data_type):
            self.message = "The data type of {0} is {1}, not {2}".format(field_name, expectect_data_type,
                                                                         receive_data_type)
            self.field_name = field_name
            self.expectect_data_type = expectect_data_type
            self.receive_data_type = receive_data_type
            super(Exception, self).__init__(self.message)

    class MissingData(Exception):
        def __init__(self, field_name):
            self.message = "{0} is require".format(field_name)
            self.field_name = field_name
            super(Exception, self).__init__(self.message)


class __GOBBLE__():
    @staticmethod
    def get_dict_fields(data):
        if isinstance(data, dict):
            if not data.has_key(__fields_docs__):
                data.update({__fields_docs__: {}})
            return data[__fields_docs__]
        else:
            raise Exception("invalid param")

    @staticmethod
    def get_dict_fields_type(data):
        if isinstance(data, dict):
            if not data.has_key(__fields_types__):
                data.update({__fields_types__: {}})
            return data[__fields_types__]
        else:
            raise Exception("invalid param")

    @staticmethod
    def get_dict_default_value(data):
        if isinstance(data, dict):
            if not data.has_key(__fields_default_value__):
                data.update({__fields_default_value__: {}})
            return data[__fields_default_value__]
        else:
            raise Exception("invalid param")

    # @staticmethod
    # def set_attr_field(param, key, value):
    #     if isinstance(value, BaseEmbededDoc):
    #         for k, v in value.__dict__.items():
    #             param.update({
    #                 key + "." + k: v
    #             })
    #             __GOBBLE__.gobble_attr_field(param, key + "." + k, v)

    @staticmethod
    def dictionary(value):
        if isinstance(value, dict):
            import pydocs
            ret_val = {}
            for k, v in value.items():
                _k = k
                if isinstance(k, pydocs.Fields):
                    _k = pydocs.get_field_expr(k, True)
                ret_val.update({_k: __GOBBLE__.dictionary(v)})
            return ret_val
        else:
            return value
    @staticmethod
    def get_fields_info(data):
        _data =data
        if not isinstance(data,dict):
            if hasattr(data,"__dict__"):
                _data =data.__dict__
        ret = {}
        for k,v in _data.items():
            if not (k.__len__()>2 and k[0:2] == "__" and k[k.__len__():k.__len__()-2] =="__"):
                ret.update({k:v})
        return ret
    @staticmethod
    def get_from_dict(data):
        import pydocs
        ret = {}
        if isinstance(data,dict):
            for k,v in data.items():
                _k = k
                if isinstance(k,pydocs.Fields):
                    _k = pydocs.get_field_expr(k,True)
                ret.update({
                    _k: __GOBBLE__.get_from_dict(v)
                })
        else:
            return data
        return ret



# class BaseDocumentsInstance(object):
#     def __setattr__(self, key, value):
#         if not self.__dict__["__type__"].has_key(key):
#             raise exceptions.MissingData(key)
#         if value != None and type(value) != self.__dict__["__type__"][key]:
#             raise exceptions.InvalidDataType(key, self.__dict__["__type__"][key], type(value))
#         self.__dict__.update({
#             key: value
#         })
#
#     def doc(self):
#         import pydocs
#         return pydocs.Fields()
#
#     def filter(self):
#         import pydocs
#         return pydocs.Fields(None, True)
#
#     # def __setitem__(self, key, value):
#     #     x=item


class BaseDocuments(object):
    def __init__(self):
        import pydocs

        self.__dict__ = {
            __fields_types__: {},
            __fields_docs__: pydocs.Fields()
        }

    def __getattr__(self, field):
        import pydocs
        ret = pydocs.Fields(field)
        org = getattr(self.__origin__,field)
        my_docs= self.__dict__.get("__document__",self)
        if isinstance(org,list) and org.__len__()>0:
            ret.__dict__.update ({
                "__origin__": org[0],
                "__parent__":self,
                "__document__":my_docs
            })
        else:
            ret.__dict__.update({
                "__origin__":org,
                "__parent__": self,
                "__document__": my_docs
            })
        ret.__dict__.update({
            "__type__":type(self.__origin__).__dict__.get(ret.__name__,None),
            "__field_name__":field
        })
        return ret


    def get_collection_name(self):
        return self.__dict__.get("__collection_name__", None)
    def load(self,*args,**kwargs):
        if args.__len__()>0:
            return self.object(args[0])
        else:
            return self.object(kwargs)
    def create(self):
        import pydocs
        import types
        from inspect import isfunction


        field_types = None
        if self.__dict__.has_key("__origin__"):
            if hasattr(self.__dict__,"__dict__"):
                field_types = __GOBBLE__.get_fields_info (self.__dict__["__origin__"].__dict__)
            elif isinstance(self.__dict__["__origin__"],type) and issubclass(self.__dict__["__origin__"],object):
                field_types = __GOBBLE__.get_fields_info(self.__dict__["__origin__"]())
            else:
                field_types = __GOBBLE__.get_fields_info (self.__dict__["__origin__"])

        else:
            self.__dict__.update({
                "__origin__":self.__dict__
            })
            field_types = __GOBBLE__.get_fields_info (self.__dict__["__origin__"])
        field_defaults = __GOBBLE__.get_dict_default_value(self.__dict__)
        ret ={}
        ret_type ={}


        for k, v in field_types.items():
            data_type = v
            is_require = False
            if isinstance(v,tuple):
                fn = None

                if v.__len__()==1:
                    v=v[0]
                if v.__len__()>1:
                    is_require =v[1]
                    data_type =v[0]
                if v.__len__() > 2:
                    fn = v[2]
                    if isinstance(fn,types.BuiltinFunctionType):
                        fn = fn()
                    elif isfunction(fn):
                        fn = fn()
                if is_require and fn == None:
                    if data_type in [int,float]:
                        fn =0
                    elif data_type in [str,unicode]:
                        if v.__len__()>2:
                            fn =  v[2]
                        else:
                            fn= None
                        if callable(fn):
                            fn=fn()
                    elif data_type == bool:
                        fn =False
                    elif data_type == uuid.UUID:
                        fn = uuid.uuid4()
                    elif data_type == datetime.datetime:
                        fn = (lambda: v[2] if v.__len__() > 2 else datetime.datetime.now())()
                    elif isinstance(v[0],BaseDocuments):
                        fn = v[0].create()

                ret.update ({
                    k: fn
                })
                ret_type.update ({
                    k: (data_type,is_require)
                })
            if isinstance(v,BaseDocuments):
                ret.update({
                    k:v.object()
                })
                ret_type.update({
                    k:(BaseDocuments,False)
                })
            if isinstance(v,BaseEmbedArray):
                ret.update({
                    k:[]
                })
                ret_type.update({
                    k:(BaseDocuments,False)
                })
            if isinstance(v,list):
                ret.update({
                    k:[]
                })
                ret_type.update({
                    k:(BaseDocuments,False)
                })
            if isinstance(v,type):
                ret.update ({
                    k: None
                })
                ret_type.update ({
                    k: (v,False)
                })

        import mobject
        ret_obj = mobject.dynamic_object(ret)
        ret_obj.__dict__.update({
            "__properties_types__":ret_type
        })
        return ret_obj

    def __lshift__(self, other):
        # if other == {}:
        #     raise Exception("Can not fill data into {0} with empty dict".format(type(self)))
        import mobject
        ret = self.create()
        ret.__dict__.update(__GOBBLE__.get_from_dict(other))
        return  ret

    def __is_contains_field__(self, item):
        import pydocs
        _field_ = item
        if isinstance(item, pydocs.Fields):
            _field_ = pydocs.get_field_expr(item, True)
        items = _field_.split('.')
        if items.__len__() == 1:
            return __GOBBLE__.get_dict_fields_type(self.__dict__).has_key(items[0])
        else:
            next_field = ".".join([x for x in items if items.index(x) > 0])
            child_object = __GOBBLE__.get_dict_fields_type(self.__dict__)[items[0]]()
            return child_object.__is_contains_field__(next_field)

    def __contains__(self, item):
        _is_check_one_of_ = False
        _fields = item
        if isinstance(item, set):
            _fields = list(item)
            _is_check_one_of_ = True
        if isinstance(item, tuple):
            _fields = list(item)
        if not isinstance(_fields, list):
            _fields = [_fields]
        if _is_check_one_of_:
            ok = False
            index = 0
            while index < _fields.__len__():
                if self.__is_contains_field__(_fields[index]):
                    return True
                else:
                    index += 1
            return False
        else:
            ok = True
            index = 0
            while index < _fields.__len__():
                ok = ok and self.__is_contains_field__(_fields[index])
                if not ok:
                    return ok
                else:
                    index += 1
            return ok

class BaseEmbedArray(BaseDocuments):
    pass
class __UniqueIndex__wrapper__():
    def __init__(self,fields):
        self.__fields__ = fields

    def wrapper(self,*args,**kwargs):
        global __unique_keys__
        if __unique_keys__ == None:
            __unique_keys__ = {}
        __unique_keys__.update({
            args[0]:self.__fields__
        })
        return args[0]
def UniqueIndex(*args,**kwargs):
    ret = __UniqueIndex__wrapper__(args)
    return ret.wrapper
