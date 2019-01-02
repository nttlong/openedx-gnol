"""

"""


class PipelineStage(object):
    def __init__(self):
        self.__stage__ = {}

    @property
    def stage(self):
        if self.__stage__ == None:
            self.__stage__ = {}
        return self.__stage__


class Project(PipelineStage):
    def __parse__(self, data):
        import pydocs
        import expression_parser
        ret = {}
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, pydocs.Fields):
                    ret.update({
                        k: pydocs.get_field_expr(v)
                    })
                elif isinstance(v, dict):
                    ret.update({
                        k: self.__parse__(v)
                    })
                elif isinstance(v, tuple):
                    _v = v[0]
                    _p = [x for x in v if v.index(x) > 0]
                    ret.update({
                        k: expression_parser.to_mongobd()
                    })
                elif isinstance(v, pydocs.Fields):
                    if v.__dict__.has_key("__alias__"):
                        ret.update({
                            v.__dict__["__alias__"]: pydocs.get_field_expr(v)
                        })
                    else:
                        ret.update({
                            pydocs.get_field_expr(v, True): 1
                        })
        return ret

    def __init__(self, *args, **kwargs):

        import pydocs
        import expression_parser
        self.__stage__ = {}
        data = kwargs
        if args.__len__() > 0:
            for item in args:
                if type(item) in [str, unicode]:
                    self.__stage__.update({
                        expression_parser.to_mongobd(item): 1
                    })
                elif isinstance(item, tuple):
                    _v = item[0]
                    _p = tuple([x for x in item if item.index(x) > 0])
                    self.__stage__.update({
                        expression_parser.to_mongobd(_v, *_p): 1
                    })
                elif isinstance(item, dict):
                    self.__stage__.update(self.__parse__(item))
                elif isinstance(item, pydocs.Fields):

                    if item.__dict__.has_key("__alias__"):
                        self.__stage__.update({
                            item.__dict__["__alias__"]: pydocs.get_field_expr(item)
                        })
                    else:
                        right = pydocs.get_field_expr(item, True)
                        if type(right) in [str, unicode]:
                            self.__stage__.update({
                                right: 1
                            })
                        elif isinstance(right, dict):
                            self.__stage__.update(right)

            return

            data = args[0]

        for k, v in data.items():
            if type(v) in [str, unicode]:
                self.__stage__.update({
                    k: expression_parser.to_mongobd(v)
                })
            elif isinstance(v, tuple):
                _v = v[0]
                _p = tuple([x for x in v if v.index(x) > 0])
                self.__stage__.update({
                    k: expression_parser.to_mongobd(_v, *_p)
                })
            elif isinstance(v, pydocs.Fields):
                if v.__dict__.has_key("__alias__"):
                    self.__stage__.update({
                        k: pydocs.get_field_expr(v, True)
                    })
                else:
                    self.__stage__.update({
                        k: pydocs.get_field_expr(v, True)
                    })

    def __add_item__(self, item):
        import pydocs
        if item.__dict__.has_key("__alias__"):
            self.stage.update({
                item.__dict__["__alias__"]: pydocs.get_field_expr(item)
            })
        else:
            self.stage.update({
                pydocs.get_field_expr(item, True): 1
            })
        return self

    def __lshift__(self, other):
        return self.__add_item__(other)

    def append(self, other):
        return self.__add_item__(other)


class Match(PipelineStage):
    def __init__(self, expr, *args, **kwargs):
        import pydocs
        import expression_parser
        if isinstance(expr, pydocs.Fields):
            self.__stage__ = pydocs.get_field_expr(expr, True)
        elif type(expr) in [str, unicode]:
            self.__stage__ = expression_parser.to_mongobd_match(expr, *args, **kwargs)


class AddFields(Project):
    pass


class Lookup(PipelineStage):
    def __init__(self, coll, local_field_or_let, foreign_field_or_pipeline, alias):
        import pydocs
        import expression_parser
        import pyquery
        pipeline = None
        local_field = None
        foreign_field = None
        let = None
        is_use_pipeline = False
        if isinstance(foreign_field_or_pipeline, pyquery.query):
            pipeline = foreign_field_or_pipeline
            let = local_field_or_let
            is_use_pipeline = True
        elif isinstance(foreign_field_or_pipeline, pydocs.Fields):
            foreign_field = pydocs.get_field_expr(foreign_field_or_pipeline, True)
            local_field = local_field_or_let
        elif type(foreign_field_or_pipeline) in [str, unicode]:
            foreign_field = foreign_field_or_pipeline
            local_field = local_field_or_let
        if not is_use_pipeline:
            self.__lookup__(coll, local_field, foreign_field, alias)
        else:
            self.__lookup_with_pipeline(coll, let, pipeline, alias)

    def __lookup__(self, coll, localField, foreignField, alias):
        import pydocs
        import documents
        import expression_parser
        _CC = coll
        _LF = localField
        _FF = foreignField
        _AS = alias
        if isinstance(alias,pydocs.Fields):
            _AS = pydocs.get_field_expr(alias,True)
        if type(coll) not in [str, unicode,documents.BaseDocuments]:
            raise Exception("'coll' must be 'str' or 'unicode'")
        if isinstance(coll,documents.BaseDocuments):
            _CC = coll.get_collection_name()
        if type(_AS) not in [str, unicode]:
            raise Exception("'alias' must be 'str' or 'unicode'")
        if isinstance(localField, pydocs.Fields):
            _LF = pydocs.get_field_expr(_LF, True)
        if isinstance(foreignField, pydocs.Fields):
            _FF = pydocs.get_field_expr(_FF, True)
        self.__stage__ = {
            "from": _CC,
            "localField": _LF,
            "foreignField": _FF,
            "as":_AS
        }
        return self

    def __lookup_with_pipeline(self, coll, let, pipeline, alias):
        import pyquery
        import pydocs
        import expression_parser
        _l = let
        if isinstance(alias,pydocs.Fields):
            alias = pydocs.get_field_expr(alias,True)
        if type(coll) not in [str, unicode]:
            raise Exception("'coll' must be 'str' or 'unicode'")
        if type(alias) not in [str, unicode]:
            raise Exception("'alias' must be 'str' or 'unicode'")
        if not (pipeline, pyquery.query):
            raise Exception("'pipeline' must be query")
        if isinstance(let, tuple):
            _l = let[0]
            _params = tuple([x for x in let if let.index(x) > 0])
            _l = expression_parser.to_mongobd(_l, *_params)
        elif isinstance(let, pydocs.Fields):
            _l = let.to_mongodb()
        elif type(let) in [str, unicode]:
            _l = expression_parser.to_mongobd(_l)
        self.__stage__ = {
            "from": coll,
            "pipeline": pipeline.pipeline,
            "as": alias
        }
        if let != None:
            self.__stage__.update({"let": _l})


class Unwind(PipelineStage):
    def __init__(self, expr, includeArrayIndex=None, preserveNullAndEmptyArrays=None):
        import pydocs
        """
        {
          $unwind:
            {
              path: <field path>,
              includeArrayIndex: <string>,
              preserveNullAndEmptyArrays: <boolean>
            }
        }
        :param expr:
        :param args:
        """
        if type(expr) in [str, unicode]:
            self.__stage__ = {
                "path": "$" + expr
            }
        elif isinstance(expr, pydocs.Fields):
            self.__stage__ = {
                "path": pydocs.get_field_expr(expr)
            }
        if includeArrayIndex != None:
            self.__stage__.update({
                "includeArrayIndex": includeArrayIndex
            })
        if preserveNullAndEmptyArrays != None:
            self.__stage__.update({
                "preserveNullAndEmptyArrays": preserveNullAndEmptyArrays
            })


class BucketAuto(PipelineStage):
    def __init__(self, groupBy, buckets, output, granularity=None, *args, **kwargs):
        import pydocs
        import expression_parser
        _groupBy = groupBy
        _buckets = buckets
        _output = output
        _granularity = granularity

        if type(groupBy) in [str, unicode]:
            _groupBy = expression_parser.to_mongobd(groupBy, *args, **kwargs)
        elif isinstance(groupBy, pydocs.Fields):
            _groupBy = pydocs.get_field_expr(groupBy)
        if type(output) in [str, unicode]:
            _output = output
        elif isinstance(output, pydocs.Fields):
            _output = pydocs.get_field_expr(output)
        self.__stage__ = {
            "groupBy": _groupBy,
            "buckets": _buckets,
            "output": _output
        }
        if granularity != None:
            self.__stage__.update({
                "granularity": granularity
            })


class Bukcet(PipelineStage):
    def __init__(self, groupBy, boundaries, default, output, *args, **kwargs):
        import pydocs
        import expression_parser
        _groupBy = groupBy
        _boundaries = boundaries
        _output = output
        _default = default

        if type(groupBy) in [str, unicode]:
            _groupBy = expression_parser.to_mongobd(groupBy, *args, **kwargs)
        elif isinstance(groupBy, pydocs.Fields):
            _groupBy = pydocs.get_field_expr(groupBy)
        if type(output) in [str, unicode]:
            _output = output
        elif isinstance(output, pydocs.Fields):
            _output = pydocs.get_field_expr(output)
        if type(default) in [str, unicode]:
            _default = expression_parser.to_mongobd(default, *args, **kwargs)
        elif isinstance(default, pydocs.Fields):
            _default = pydocs.get_field_expr(default)
        self.__stage__ = {
            "groupBy": _groupBy,
            "boundaries": boundaries,
            "output": _output,
            "default": "default"
        }


class Count(PipelineStage):
    def __init__(self, field=None, *args, **kwargs):
        import pydocs
        import expression_parser
        if field == None:
            field = "ret"
        if isinstance(field, pydocs.Fields):
            self.__stage__ = pydocs.get_field_expr(field, True)
        else:
            self.__stage__ = field


class Facet(PipelineStage):
    def __init__(self, *args, **kwargs):
        import pyquery
        data = kwargs
        self.__stage__ = {}
        if kwargs == {}:
            data = args[0]
        for k, v in data.items():
            if isinstance(v, pyquery.query):
                self.__stage__.update({
                    k, v.pipeline
                })
            else:
                raise Exception("'{0}' must be query")


class Group(PipelineStage):
    def __init__(self, _id, *args, **kwargs):
        import pydocs
        import expression_parser
        __id = _id

        if type(_id) in [str, unicode]:
            __id = expression_parser.to_mongobd(_id, *args, **kwargs)
        elif isinstance(_id, pydocs.Fields):
            __id = pydocs.get_field_expr(_id)
        elif isinstance(_id,tuple):
            _id ==Project(*_id, **kwargs).stage
        elif isinstance(_id,dict):
            self.__stage__ = expression_parser.to_mongobd(_id,*args,**kwargs)
            if not self.__stage__.has_key("_id"):
                self.__stage__.update({"_id":None})
            return self


        _selector = {
            "_id": __id
        }
        if args.__len__()>0:
            for item in args:
                if type(item) in [str,unicode]:
                    _selector.update({
                        item:expression_parser.to_mongobd(item)
                    })
                elif isinstance(item,pydocs.Fields):
                    cValue = item.to_mongodb()
                    if not isinstance(cValue,dict):
                        raise Exception("Select item in group must be alias, not a fiel\n"
                                        "Example: group(None,pymqr.docs.MyFielsdName<<pymqr.funcs.first(pymqr.docs.MyFielsdName)")
                    _selector.update(
                        item.to_mongodb()
                    )

        self.__stage__ = _selector


class ReplaceRoot(PipelineStage):
    def __init__(self, expr, *args, **kwargs):
        import pydocs
        import expression_parser
        if type(expr) in [str, unicode]:
            self.__stage__ = {"newRoot": expression_parser.to_mongobd(expr, *args, **kwargs)}
        elif isinstance(expr, pydocs.Fields):
            self.__stage__ = {"newRoot": pydocs.get_field_expr(expr)}
        elif isinstance(expr, dict):
            data = {}
            for k, v in expr.items():
                _k = k
                if isinstance(k, pydocs.Fields):
                    _k = pydocs.get_field_expr(k, True)
                data.update({
                    _k: pydocs.get_field_expr(v)
                })
            self.__stage__ = {"newRoot": data}


class Sort(PipelineStage):
    def __init__(self, *args, **kwargs):
        import pydocs
        import expression_parser
        import pymongo
        from collections import OrderedDict
        data =  OrderedDict()
        if args.__len__() > 0:
            for item in args:
                if item.items()[0][1] == 1:
                    data[item.items()[0][0]]=pymongo.ASCENDING
                else:
                    data[item.items()[0][0]]=pymongo.DESCENDING

        else:
            for k, v in kwargs.items():
                if type(k) in [str, unicode]:
                    data.update({
                        k: v
                    })
                elif isinstance(k, pydocs.Fields):
                    data.update({
                        pydocs.get_field_expr(k, True): v
                    })
        self.__stage__ = data






