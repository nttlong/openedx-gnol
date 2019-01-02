#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xdj


@xdj.Controller(
    url="system/users",
    template="system/users.html"
)
class system_user_controller(xdj.BaseController):
    def __init__(self):
        pass
    def __get_user_models__(self):
        from django.contrib.auth import get_user_model
        return get_user_model().objects
    def on_get(self,sender):
        return self.render(sender)
    def doLoadItems(self,sender):
        """
        Hàm này dùng để load danh sách users có phân trang
        :param sender:
        :return:
        """
        from django.db.models import Q

        users = self.__get_user_models__()
        totalItems = 0
        if hasattr(sender.post_data,"search"):
            users=users.filter(Q(username__icontains=sender.post_data.search)|
                               Q(first_name__icontains=sender.post_data.search)|
                               Q(last_name__icontains=sender.post_data.search)|
                               Q(email__icontains=sender.post_data.search))
        totalItems = users.count()
        totalPages=totalItems / sender.post_data.pageSize
        if totalItems % sender.post_data.pageSize >0:
            totalPages=totalPages+1
        items = list(users.values(

            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_superuser",
            "is_staff",
            "last_login",
            "email",
            "date_joined"
        ).all()[sender.post_data.pageSize*sender.post_data.pageIndex:sender.post_data.pageSize])
        return dict(
            items=items,
            totalItems=totalItems,
            totalPages=totalPages
        )
    @xdj.Page(url="user", template="system/user.html")
    class user(object):
        def doLoadItem(self,sender):
            """
            Hàm này dùng để lấy thông tin chi tiết của một user
            :param sender:
            :return:
            """
            users= self.owner.__get_user_models__()
            user = users.filter(username=sender.post_data.username).get()
            return user
        def doUpdateItem(self,sender):
            """
            Cập nhật thông tin tài khoản
            :param sender:
            :return:
            """
            try:
                user_data= xdj.dobject(sender.post_data.user)
                user=self.owner.__get_user_models__().get(username=user_data.username)
                user.first_name= user_data.first_name
                user.last_name = user_data.last_name
                user.email = user_data.email
                user.is_active = user_data.is_active
                user.is_staff = user_data.is_staff
                user.is_superuser=user_data.is_superuser
                user.save()



                x = user
            except Exception as ex:
                raise ex
    @xdj.Page(url="user/reset_password", template="system/user_reset_password.html")
    class password(object):
        def doSave(self,sender):
            pass
