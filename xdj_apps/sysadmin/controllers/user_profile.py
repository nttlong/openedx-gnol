#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Controller này dùng để soạn thảo thông tin cá nhân
"""
import xdj


@xdj.Controller(
    url="users/profile",
    template="users/profile.html"
)
class UserProfileController(xdj.BaseController):
    def on_get(self,model):
        return self.render(model)