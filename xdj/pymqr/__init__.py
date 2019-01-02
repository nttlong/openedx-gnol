VERSION = [1,0,2,"beta",6]
def get_version():
    return VERSION[0].__str__()+\
           "."+VERSION[1].__str__()+\
           "."+VERSION[2].__str__()+\
           "."+VERSION[3].__str__()+\
           "."+VERSION[4].__str__()
import documents
def create_model(name,required,indexes,fields):
    """
    :param name:
    :param indexes:
    :param fields:
    :return:

    """
    import pymodel
    # type: (str,object, list(pymodel.Index), object) -> object
    return pymodel.create_model(name,required,indexes,fields)
def query(*args,**kwargs):
    # type: (object, object) -> pyquery.query
    """

    :param args:
    :param kwargs:
    :return:
    create queryable for monongodb with aggregate pipeline support and CRUID opreator
    """
    import pyquery
    return pyquery.query(*args,**kwargs)
def __docs__():
    """
    create Mongodb parable expresion
    :return:
    """
    import pydocs
    return pydocs.Fields()
def __filters__():
    """
    create Mongodb filterable expression
    :return:
    """
    import pydocs
    return pydocs.Fields(None,True)

def compile(exr):
    """
    :rtype: dict
    """
    import pydocs
    if not isinstance(exr,pydocs.Fields):
        raise Exception("invalid data type")
    return exr.__tree__
import pyfuncs as funcs
docs=__docs__()
filters = __filters__()
# from pymodel import Index,IndexOption,FieldInfo
# def create_index(fields,options):
#     import pymodel
#     return pymodel.Index(fields,options)
# from pydocs import BSON_select, BSON_doc
