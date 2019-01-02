class __page_wrapper__(object):
    def __init__(self,*args,**kwargs):
        self.url=kwargs["url"]
        self.template=kwargs["template"]
    def wrapper(self,*args,**kwargs):
        if issubclass(args[0],object):
            ret = args[0]()
            ret.__dict__.update(dict(
                is_sub_page=True,
                url=self.url,
                template=self.template
            ))
            return ret
        args[0].__dict__.update(dict(
            is_sub_page=True,
            url=self.url,
            template=self.template
        ))
        return args[0]
def Page(*args,**kwargs):
    ret= __page_wrapper__(*args,**kwargs)
    return ret.wrapper