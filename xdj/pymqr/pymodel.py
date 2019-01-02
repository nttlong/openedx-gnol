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

        data = kwargs
        if args.__len__()>0:
            data = args[0]
        if data == None:
            self = None
            return
        if data != {}:
            self.__dict__.update({"__validator__": False})
            for k,v in data.items():
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
                    if hasattr(x,"__to_dict__"):
                        lst.append(x.__to_dict__())
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
        properties_types = self.__dict__.get("__properties_types__",{})
        if properties_types!= {}:
            if not properties_types.has_key(key):
                raise Exception("'{0}' was not found")
            if properties_types[key][1] and value!=None:
                if properties_types[key][0] != type(value):
                    raise Exception ("'{0}' is invalid data type. The exprected "
                                     "data type is {1}, but receive {2} with value {3}".format(
                        key,properties_types[key][0],type(value),value
                    ))


        super(dynamic_object, self).__setattr__(key, value)
    def is_empty(self):
        return self.__dict__ == {}