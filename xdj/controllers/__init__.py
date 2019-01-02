#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 ____     _  ____  _      _____ ____
/  _ \   / |/  _ \/ \  /|/  __//  _ \
| | \|   | || / \|| |\ ||| |  _| / \|
| |_/|/\_| || |-||| | \||| |_//| \_/|
\____/\____/\_/ \|\_/  \|\____\\____/


"""
__lang_cache__ ={}
__build_cached__ = None
import threading
lock = threading.Lock()
class Res(object):
    """
    This class sever for language resource item getter with three level
    1- Global:The item apply at global could be access for all application
    2- Application:The item apply at application could be access for all view in application
    3- View:The item apply at view could be access for specific view in application
    """
    def __init__(self,on_get_lang_item,app_name,view_name):
        if app_name==None:
            raise Exception("app_name can not be None")
        self.app_name=app_name
        self.view_name=view_name
        self.on_get_lang_item=on_get_lang_item
    def g(self,key,value=None):
        """
        Get global language item resource
        :param key:
        :param value:
        :return:
        """
        from django.utils import translation

        if value==None:
            key = key.rstrip(" ").lstrip(" ")
            value=key
        key=key.lower()
        _key="lang={0};app={1};view={2};key={3}".format(
            translation.get_language(),
            "-",
            "-",
            key
        )
        if not __lang_cache__.has_key(_key):
            try:
                lock.acquire()
                __lang_cache__.update({_key:self.on_get_lang_item(translation.get_language(),"-","-",key,value)})
                if type(__lang_cache__[_key]) not in [str,unicode]:
                    raise Exception("{0} in {1} must return 'str' or 'unicode' value".format(
                        "on_get_language_resource_item",
                        self.on_get_lang_item.func_code.co_filename
                    ))
                lock.release()
                return __lang_cache__[_key]
            except Exception as ex:
                lock.release()
                raise ex
        else:
            return __lang_cache__[_key]
    def a(self,key,value=None):
        """
        Get application language resource
        :param key:
        :param value:
        :return:
        """
        from django.utils import translation

        if value == None:
            key = key.rstrip(" ").lstrip(" ")
            value = key
        key = key.lower()
        _key = "lang={0};app={1};view={2};key={3}".format(
            translation.get_language(),
            self.app_name,
            "-",
            key
        )
        if not __lang_cache__.has_key(_key):
            try:
                lock.acquire()
                __lang_cache__.update({_key: self.on_get_lang_item(translation.get_language(), self.app_name, "-", key, value)})
                if type(__lang_cache__[_key]) not in [str,unicode]:
                    raise Exception("{0} in {1} must return 'str' or 'unicode' value".format(
                        "on_get_language_resource_item",
                        self.on_get_lang_item.func_code.co_filename
                    ))
                lock.release()
                return __lang_cache__[_key]
            except Exception as ex:
                lock.release()
                raise ex
        else:
            return __lang_cache__[_key]
    def v(self,key,value=None):
        """
        Get View Item reources
        :param key:
        :param value:
        :return:
        """
        from django.utils import translation
        if value == None:
            key = key.rstrip(" ").lstrip(" ")
            value = key
        key = key.lower()
        _key = "lang={0};app={1};view={2};key={3}".format(
            translation.get_language(),
            self.app_name,
            self.view_name,
            key
        )
        if not __lang_cache__.has_key(_key):
            try:
                lock.acquire()
                __lang_cache__.update({_key:self.on_get_lang_item(translation.get_language(), self.app_name, self.view_name, key, value)})
                if type(__lang_cache__[_key]) not in [str,unicode]:
                    raise Exception("{0} in {1} must return 'str' or 'unicode' value".format(
                        "on_get_language_resource_item",
                        self.on_get_lang_item.func_code.co_filename
                    ))

                lock.release()
                return __lang_cache__[_key]
            except Exception as ex:
                lock.release()
                raise ex
        else:
            return __lang_cache__[_key]
    def __floordiv__(self, other):
        """
        Get global application resource at html template can be use _//"My label"
        :param other:
        :return:
        """
        if isinstance(other,tuple):
            if other.__len__()>1:
                return self.g(other[0],other[1])
            elif other.__len__()>0:
                return self.g(other[0])
        elif type(other) in [str,unicode]:
            return  self.g(other)
    def __gt__(self, other):
        """
        Get Language resource at view at html template can be use _>"My Lable"
        :param other:
        :return:
        """
        if isinstance(other,tuple):
            if other.__len__()>1:
                return self.v(other[0],other[1])
            elif other.__len__()>0:
                return self.v(other[0])
        elif type(other) in [str,unicode]:
            return  self.v(other)
    def __rshift__(self, other):
        """
        Get application resource at template can be use _>>"My lable"
        :param other:
        :return:
        """
        if isinstance(other,tuple):
            if other.__len__()>1:
                return self.a(other[0],other[1])
            elif other.__len__()>0:
                return self.a(other[0])
        elif type(other) in [str,unicode]:
            return  self.a(other)
class PostData(object):
    pass
class ModelUser(object):
    def __init__(self):
        self.username=""
        self.is_staff=False
        self.is_superuser=False
        self.is_active=False
    def is_anonymous(self):
        return

def to_json(data):
    import xdj.JSON
    return xdj.JSON.to_json(data)


class Model(object):
    def __init__(self):


        self.request = None
        self.response = None
        self.absUrl = None
        self.appUrl = None
        self.static = None
        self.redirect = None
        self.user= ModelUser()
        self.csrf_token = None
        self.post_data= PostData();
        self.settings=None
        self.to_json= to_json

    def debugger(self):
        print "debugger"



class __controller_wrapper__(object):
    """
    Controllwer wrapper class
    """
    def __init__(self,*args,**kwargs):
        self.url=kwargs["url"]
        self.template=kwargs["template"]
        self.controllerClass=None
        self.params = kwargs.get("params",[])

    def wrapper(self,*args,**kwargs):
        import xdj
        if issubclass(args[0],BaseController):
            self.controllerClass=args[0]
            self.instance = self.controllerClass.__new__(self.controllerClass)
            # self.instance =BaseController.__new__(self.controllerClass)
            super(self.controllerClass, self.instance).__init__()
            self.instance.__init__()
            self.instance.url=self.url
            self.instance.template = self.template
            self.instance.sub_pages = [v for k, v in self.controllerClass.__dict__.items() if hasattr(v, "is_sub_page")]
            for item in self.instance.sub_pages:
                item.owner=self.instance
                class cls_exec_request(object):
                    def __init__(self,obj):
                        self.obj=obj
                    def exec_request_get(self,request,*args,**kwargs):
                        model = self.obj.owner.create_client_model(request)
                        model.params = xdj.dobject(kwargs)
                        def do_rendert(model):
                            return self.obj.owner.render_with_template(model, self.obj.template)
                        self.obj.render = do_rendert
                        if hasattr(self.obj,"on_get"):
                            return  self.obj.on_get(model)
                        return self.obj.owner.render_with_template(model,self.obj.template)
                item.exec_request_get=cls_exec_request(item).exec_request_get


            xdj.__controllers__.append(self)
        else:
            raise Exception("{0} mus be inherit from {1}".format(self.controllerClass,BaseController))

def __createModelFromRequest__(request,rel_login_url,res,host_dir,on_authenticate,settings):
    from django.shortcuts import redirect
    from django.template.context_processors import csrf

    model = Model();
    model.request = request
    model.currentUrl = request.build_absolute_uri()
    model.absUrl = model.currentUrl[0:model.currentUrl.__len__() - request.path.__len__()]
    model.appUrl = model.absUrl + "/" + host_dir
    model.static = model.appUrl + "/static"
    model.redirect = redirect
    model._ = res
    model.user = request.user
    model.csrf_token = csrf(request)["csrf_token"]
    model.settings = settings

    return model
def Controller(*args,**kwargs):
    ret = __controller_wrapper__(*args,**kwargs)
    return ret.wrapper
class BaseController(object):
    def __init__(self):
        self.app_name = None
        self.app_dir = None
        self.url = None
        self.template = None
        self.on_get_language_resource_item=None
        self.on_authenticate = None
        self.rel_login_url = None
        self.params = None
    def create_client_model(self, request):
        model = __createModelFromRequest__(
            request, self.rel_login_url, self.res, self.host_dir, self.on_authenticate, self.settings
        )
        return model
    def __view_exec__(self,request,*args,**kwargs):
        import xdj
        from django.http import HttpResponse
        from django.shortcuts import redirect
        model = self.create_client_model(request)
        model.params = xdj.dobject(*args, **kwargs)
        if request.build_absolute_uri(self.rel_login_url).lower() != model.currentUrl.lower():
            if not self.on_authenticate(model):
                return redirect(model.appUrl + "/" + self.rel_login_url)
        if request.method == 'GET':
            return self.on_get(model)
        if request.method == 'POST':
            if not request.META.has_key("HTTP_AJAX_POST"):
                model.post_data.__dict__.update(
                    request._get_post()
                )
                return self.on_post(model)
            else:
                try:
                    from xdj import JSON
                    if request.body.__len__()>0:
                        model.post_data.__dict__.update(JSON.from_json(request.body))
                    method_name = request.META["HTTP_AJAX_POST"]
                    method_items = method_name.split('.')
                    obj= self
                    for i in range(0,method_items.__len__()-1):
                        obj=getattr(obj,method_items[i])
                    method_exec = getattr(obj,method_items[method_items.__len__()-1])
                    ret = method_exec(model)
                    json_data = JSON.to_json(ret)
                    return HttpResponse(json_data, content_type="application/json")
                except AttributeError as ex:
                    raise Exception("{0} was not found in {1} or error '{2}'".format(
                        request.META["HTTP_AJAX_POST"],
                        self.on_get.im_func.func_code.co_filename,
                        ex.message
                    ))
    def render_with_template(self,model,template):
        if isinstance(model,Model):
            from django.http import HttpResponse
            import os
            from mako.lookup import TemplateLookup
            viewpath=os.sep.join([self.app_dir,"views"])

            ret_res = None
            mylookup = TemplateLookup(directories=[viewpath],
                                      default_filters=['decode.utf8'],
                                      input_encoding='utf-8',
                                      output_encoding='utf-8',
                                      encoding_errors='replace',

                                      )
            d=model.__dict__
            ret_res = mylookup.get_template(template).render(**d)
            return HttpResponse(ret_res)
        else:
            raise Exception("{0} is not instance of {1}".format(
                type(model),
                Model
            ))
    def render(self,model):
        return self.render_with_template(model,self.template)

