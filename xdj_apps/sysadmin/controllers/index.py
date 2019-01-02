#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xdj


class obj(object):
    pass
def create(dict):
    ret = obj()
    ret.__dict__.update(dict)
    return ret
# from . import base
@xdj.Controller(
    url="",
    template="index.html"
)
class index(xdj.BaseController):
    """
    Trang index
    """
    def __init__(self):
        x=1
    def on_get(self,sender):
        sender.menu=[
            create(dict(
                caption="Hệ thống",
                items=[
                    create(dict(
                        caption="Người dùng",
                        page="system/users"

                    )),
                    xdj.dobject(
                        caption="Email",
                        page="system/email_settings"
                    )
                ]
            )),
            xdj.dobject(
                caption="Khóa học",
                items=[
                    dict(
                        caption="Khóa học",
                        page="couserware/courses"
                    )
                ]
                )
        ]
        return self.render(sender)