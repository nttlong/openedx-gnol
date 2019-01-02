#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Controller này dùng để sigout khỏi hệ thống open edx
"""
import xdj


@xdj.Controller(
    url="signout",
    template="sigout.html"
)
class SigOutController(xdj.BaseController):
    def on_get(self,sender):
        if isinstance(sender, xdj.Model):
            from django.contrib.auth import logout
            logout(sender.request)
            return sender.redirect(sender.appUrl)