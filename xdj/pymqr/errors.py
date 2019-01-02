import pymongo
from enum import Enum
__index_info__ = None
import threading
lock = threading.Lock()
class ErrorType(Enum):
    none = 0
    duplicate = 1
    unknown = -1
class DataException(Exception):
    def __init__(self, message, errors):
        self._error_type = ErrorType.none
        self._fields=[]
        self._index_name = ""
        self._code =0
        if errors == None:
            self.error_type = ErrorType.unknown
        self._fields = errors.get("fields",[])
        self._index_name = errors.get("index","")
        self._collection_name =  errors.get("collection_name","")
        self._code = errors.get("code",0)
        self._error_type = ErrorType.duplicate
        super (DataException, self).__init__ (message)
        self.errors = errors
    @property
    def error_type(self):
        return self._error_type
    @property
    def fields(self):
        return self._fields
    @property
    def index_name(self):
        return self._index_name
    @property
    def code(self):
        return self._code


def __duplicate__(coll,ex):
    import inspect
    if isinstance(ex,pymongo.errors.DuplicateKeyError):
        global __index_info__
        if __index_info__ == None:
            __index_info__ = {}
        index_name = ex.message.split (':')[2].rstrip (' ').lstrip (' ').split (' ')[0].rstrip (' ').lstrip (' ')

        if isinstance(coll,pymongo.mongo_client.database.Collection):
            if not __index_info__.has_key(coll.name):
                lock.acquire()
                try:
                    __index_info__.update({
                        coll.name:coll.index_information()
                    })
                    lock.release()

                except Exception as ex:
                    lock.release()
            index = __index_info__[coll.name]
            return DataException(ex.message,dict(
                collection_name=coll.name,
                code=ex.code,
                index = index_name,
                fields = [x[0] for x in index[index_name]["key"]]
            ))
        else:
            raise Exception("The first param must be '{0}'".format(
                pymongo.mongo_client.database.Database
            ))
def __unknown__(coll,ex):
    return DataException (ex.message, None )
