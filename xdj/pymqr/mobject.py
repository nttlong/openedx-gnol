# encoding=utf8

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import datetime

class __validator_class__(object):
    def __init__(self):
        # self.__properties__ ={}
        self.__data_type__ = None
        self.__require__ = False
        self.__dict__.update({"__properties__":{}})
        self.__dict__.update({"__validator__": False})

        # self.__validator__= False
    def __getattr__(self, item):
        if self.__dict__.get("__validator__",False):
            if not self.__dict__.get("__properties__",{}).has_key(item):
                raise (Exception("'{0}' was not found".format(item)))
        return super(__validator_class__, self).__getattr__(item)
    def __setattr__(self, key, value):
        if key[0:2] == "__":
            super(__validator_class__, self).__setattr__(key, value)
            return
        if self.__dict__.get("__properties_types__",{})!= {}:
            types = self.__dict__.get("__properties_types__")
            if not types.has_key(key):
                raise Exception("'{0}' was not found".format(key))
            v = types[key]
            if v[1] and value == None:
                raise Exception("{0} is require".format(key))
            elif type(value) != v[0]:
                raise Exception("{0} is invalid data type, "
                                "expected {1} but receive {2} with {3}".format(
                    key,v[0],type(value),value
                ))
            super (__validator_class__, self).__setattr__ (key, value)
            return
        if self.__dict__.get("__validator__",False):
            if not self.__properties__.has_key(key):
                raise (Exception("'{0}' was not found".format(key)))




        if value == None:
            super(__validator_class__, self).__setattr__(key, value)
            return
        __data_type__ = self.__dict__.get("__properties__",{}).get('type',None)
        if __data_type__ == "object" and not type(value) is dynamic_object:
            raise Exception("'{0}' is invalid data type, expected type is {1}, but the value is {2}".format(key,__data_type__,value))
        if __data_type__ == "text" and not type(value) in [str,unicode]:
            raise Exception(
                "'{0}' is invalid data type, expected type is {1}, but the value is {2}".format(key, self.__data_type__,
                                                                                                value))
        if __data_type__ == "date" and not type(value) is datetime.datetime:
            raise Exception(
                "'{0}' is invalid data type, expected type is {1}, but the value is {2}".format(key, self.__data_type__,
                                                                                                value))
        if __data_type__ == "bool" and not type(value) is bool:
            raise Exception(
                "'{0}' is invalid data type, expected type is {1}, but the value is {2}".format(key, self.__data_type__,
                                                                                                value))



        super(__validator_class__, self).__setattr__(key, value)
    def __set_config__(self,property,type,require):
        self.__properties__.update({
            property:dict(
                type=type,
                require=require
            )
        })
class dynamic_object(__validator_class__):
    def __init__(self,*args,**kwargs):
        import datetime
        t =datetime.datetime.now()
        import pydocs

        data = kwargs
        if args.__len__()>0:
            data = args[0]
        if data == None:
            self = None
            return
        if data != {}:
            self.__dict__.update({"__validator__": False})
            for _k,v in data.items():
                k = _k
                if isinstance(_k,pydocs.Fields):
                    k = pydocs.get_field_expr(_k,True)

                if k[0:2] != "__" and k.count('.') == 0:
                    self.__properties__.update({k:1})
                    if type(v) is dict:
                        setattr(self,k,dynamic_object(v))
                    elif type(v) is list:
                        values = []
                        for x in v:
                            if type(x) is dict:
                                values.append(dynamic_object(x))
                            else:
                                values.append(x)
                        setattr(self,k,values)
                    else:
                        setattr(self, k, v)
            self.__dict__.update({"__validator__": True})
    def to_dict(self):
        keys = [x for x in self.__dict__.keys() if x[0:2] != "__"]
        if keys == []:
            return None
        ret = {}
        for k in keys:
            v= self.__dict__[k]
            if hasattr(v,"__to_dict__"):
                ret.update({k:v.__to_dict__()})
            elif type(v) is list:
                lst = []
                for x in v:
                    if hasattr(x,"to_dict"):
                        lst.append(x.to_dict())
                    else:
                        lst.append(x)
                ret.update({k: lst})
            else:
                ret.update({k:v})
        return ret
    def __getattr__(self, item):
        if item =="__properties__":
            if self.__dict__.has_key(item):
                return self.__dict__[item]
            else:
                self.__dict__.update({item:{}})
                return self.__dict__[item]

        return super(dynamic_object, self).__getattr__(item)
    def __setattr__(self, key, value):
        if self.__dict__.has_key("__properties__"):
            if not self.__dict__["__properties__"].has_key(key):
                raise Exception("{0} was not found".format(key))
            attr= self.__dict__["__properties__"][key]
            if isinstance(attr,tuple):
                t = attr[0]
                r =attr[1]
                if r==False:
                    if value != None:
                        if t!=type(value):
                            raise Exception("{0} must be {1} not {2} which is equal {3}".format(
                                key,t,type(value),value
                            ))
                else:
                    if t!=type(value):
                        raise Exception("{0} must be {1} not {2} which is equal {3}".format(
                            key, t, type(value), value
                        ))
            elif isinstance(attr,type):
                if value!=None:
                    if attr!=type(value):
                        raise Exception("{0} must be {1} not {2} which is equal {3}".format(
                            key, attr, type(value), value
                        ))

        super(dynamic_object, self).__setattr__(key, value)
    def is_empty(self):
        return self.__dict__ == {}
    def __set_data_field_value__(self,other):
        import pymqr.pydocs
        if not isinstance (other, tuple):
            raise Exception ("Incorect data the data must be (key,value) \n"
                             "key is str, unicode or {0}".format (pymqr.pydocs.Fields))
        key = other[0]
        if isinstance (key, pymqr.pydocs.Fields):
            import pymqr
            key = pymqr.pydocs.get_field_expr (key, True)
        items = key.split ('.')
        ptr = self

        ptr_name = ""
        for i in range (0, items.__len__ () - 1, 1):
            ptr_name = items[i]
            ptr.__dict__.update ({"__validator__": False})
            if not hasattr (ptr, ptr_name):
                setattr (ptr, ptr_name, dynamic_object ())

            _ptr = getattr (ptr, ptr_name)
            if _ptr == None:
                _ptr = dynamic_object ()
                setattr (ptr, ptr_name, _ptr)
            ptr.__dict__.update ({"__validator__": True})
            ptr = _ptr
        ptr.__dict__.update ({"__validator__": True})
        setattr (ptr, items[items.__len__ () - 1], other[1])
    def __lshift__(self, other):
        """

        :param other:
        :return:
        """
        if isinstance(other,tuple):
            self.__set_data_field_value__(other)
        elif isinstance(other,set):
            for item in list(other):
                self.__set_data_field_value__ (item)
    def filter_to_oject(self, *args,**kwargsk):
        import pydocs

        other = args

        field_list = []
        for item in list(other):
            if isinstance(item,pydocs.Fields):
                field_list.append(pydocs.get_field_expr(item,True))
            else:
                field_list.append(item)
        ret = {}
        filter = set(self.__dict__).intersection(field_list)
        for item in list(filter):
            ret.update({
                item:self.__dict__.get(item,None)
            })
        return dynamic_object(ret)









