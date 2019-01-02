import mobject
from . import errors
def __build_data__(data):
    ret ={}
    if isinstance(data,dict):
        import pydocs
        invalid_items = [x for x,y in data.items() if type(x) not in [str,unicode,pydocs.Fields]]
        if invalid_items.__len__()>0:
            raise Exception("{0} with type {4} is invalid data type of key."
                            " The valid data type of key is"
                            "{1},{2} or {3}"
                            .format(invalid_items[0], str,unicode,pydocs.Fields,type(invalid_items[0])))
        for k,v in data.items():
            if isinstance(k,pydocs.Fields):
                field_name = pydocs.get_field_expr(k,True)
                if type(field_name) not in [str,unicode]:
                    raise Exception("{0} is not str".format(field_name))
                ret.update({
                    pydocs.get_field_expr(k,True):__build_data__(v)
                })
            elif hasattr(v,"to_dict"):
                ret.update ({
                    pydocs.get_field_expr(k,True): __build_data__ (v.to_dict())
                })
            else:
                ret.update ({
                    k: __build_data__ (v)
                })
    elif hasattr(data,"to_dict"):
        return __build_data__(data.to_dict())
    elif hasattr(data,"__dict__"):
        return __build_data__ (data.__dict__)
    else:
        return data
    return ret


class entity():
    def __init__(self,owner,where={}):
        import pyquery
        if isinstance(owner,pyquery.query):
            self.owner=owner
            self.__data__=None
            self.__insert_data__=None
            self.__where__=where
        else:
            raise Exception("the owner must be 'pyquery.query'")
    def insert(self,*args,**kwargs):
        if args.__len__()>0:
            if args.__len__()==1:
                self.__insert_data__=args[0]
            else:
                self.__insert_data__=list(args)
        else:
            self.__insert_data__=kwargs
        self.__insert_data__ = __build_data__(self.__insert_data__)
        return self
    def find(self):
        return self.owner.coll.find(self.__where__)
    def find_one(self):
        ret = self.owner.coll.find_one(self.__where__)
        self.__where__ = None
        return ret

    @property
    def item(self):
        import datetime
        ret = self.find_one()
        return ret
    @property
    def items(self):
        return self.find()
    @property
    def objects(self):
        ret= self.find()
        for item in ret:
            yield mobject.dynamic_object(item)
    @property
    def object(self):
        import datetime
        obj = self.find_one ()
        ret =mobject.dynamic_object(obj)
        return ret
    def __do_insert_one__(self,data):
        import pymongo
        try:
            ret= self.owner.coll.insert_one(data)
            data.update({
                "_id":ret.inserted_id
            })
            return data,None,ret
        except pymongo.errors.DuplicateKeyError as ex:
            return data, errors.__duplicate__(self.owner.coll,ex), None

    def __do_insert_many__(self,items):
        try:
            ret= self.owner.coll.insert_many(items)
            for i in range(0,ret.inserted_ids.__len__(),1):
                items[i].update({
                    "_id":ret.inserted_ids[i]
                })
            return items,None,ret
        except pymongo.errors.DuplicateKeyError as ex:
            return items, errors.__duplicate__ (self.owner.coll, ex), ret

    def __do_update_data__(self,data):
        import pymongo
        try:
            ret = self.owner.coll.update_many(self.__where__,data)
            return data,None,ret
        except pymongo.errors.DuplicateKeyError as ex:
            return data,  errors.__duplicate__ (self.owner.coll, ex), None

    def commit(self):
        import pymongo
        if self.__insert_data__!=None:
            if type(self.__insert_data__) is list:
                ret, err, result = self.__do_insert_many__ (self.__insert_data__)
                return ret, err, result


            else:
                ret, err, result = self.__do_insert_one__ (self.__insert_data__)
                return ret, err, result
        elif self.__data__!=None:
            ret, err, result = self.__do_update_data__ (self.__data__)
            return ret, err, result

        else:
            return None,"Nothing to commit"
    def set(self,*args,**kwargs):
        _data=kwargs
        if args.__len__()==1:
            _data=args[0]
        if self.__data__== None:
            self.__data__={}
        self.__data__.update({
            "$set": __build_data__(_data)
        })
        return self
    def push(self,*args,**kwargs):
        _data=kwargs
        if args.__len__()==1:
            _data=args[0]
        if self.__data__== None:
            self.__data__={}
        self.__data__.update({
            "$push":  __build_data__(_data)
        })
        return self
    def addToSet(self,*args,**kwargs):
        _data=kwargs
        if args.__len__()==1:
            _data=args[0]
        if self.__data__== None:
            self.__data__={}
        self.__data__.update({
            "$addToSet":  __build_data__(_data)
        })
        return self
    def pull(self,expr,*args,**kwargs):
        import expression_parser
        _data=expression_parser.to_mongobd_match(expr,*args,**kwargs)
        if self.__data__== None:
            self.__data__={}
        self.__data__.update({
            "$pull": _data
        })
        return self
    def inc(self,*args,**kwargs):
        _data=kwargs
        if args.__len__()==1:
            _data=args[0]
        if self.__data__== None:
            self.__data__={}
        self.__data__.update({
            "$inc": __build_data__(_data)
        })
        return self
    def mul(self,*args,**kwargs):
        _data=kwargs
        if args.__len__()==1:
            _data=args[0]
        if self.__data__== None:
            self.__data__={}
        self.__data__.update({
            "$mul": _data
        })
        return self
    def delete(self):
        ret = None
        try:
            ret = self.owner.coll.detele_many (self.__where__)
            return self.__where__,None,ret
        except Exception as ex:
            return None,ex,ret





