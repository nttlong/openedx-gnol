#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Controller này dùng để xem danh sách khóa học
"""
import xdj


@xdj.Controller(
    url="couserware/courses",
    template="couserware/courses.html"
)
class couserware_couser_controller(xdj.BaseController):
    def on_get(self,sender):
        return self.render(sender)
    def doLoadItems(self,sender):
        """
        https://programtalk.com/python-examples-amp/student.models.anonymous_id_for_user/
        :param sender:
        :return:
        """

        import branding
        import courseware
        from xdj_models.enities import courseware as cw
        from xdj import pymqr
        from xdj import medxdb
        from django.contrib.auth.models import User
        import sysadmin
        import datetime
        from django.db.models import Q

        # courseware.models.StudentModule.objects.all()[0].student.last_name
        ret = branding.get_visible_courses()
        qr = pymqr.query(medxdb.db(), cw.modulestore_active_versions)
        for item in ret:
            # course = courseware.models.StudentModule.objects.get(course_id=item.id)
            x = qr.new().match(pymqr.filters.org == item.id.org)\
                .match(pymqr.filters.run == item.id.run)\
                .match(pymqr.filters.course == item.id.course).object
            from xdj_models.models import course_authors
            fx=course_authors.course_authors()
            item.course_id=item.id.__str__()
            if not x.is_empty():
                authors= User.objects.filter(id=x.edited_by)
                if authors.__len__()>0:
                    sql_items=course_authors.course_authors.objects.filter(Q(user_id=x.edited_by)&Q(course_id=item.id.__str__())).count()
                    item.author= xdj.dobject(username=authors[0].username)
                    if sql_items==0:
                        fx.user_id = x.edited_by
                        fx.course_id = item.id.__str__()
                        fx.created_on = datetime.datetime.now()
                        fx.save()
            item.totalActiveStudent=courseware.models.StudentModule.objects.filter(course_id=item.id).filter(module_type="course").count()
            """Tính số học viên đang tương tác với khóa học"""

        return ret
    def doDeleteItem(self,sender):
        from opaque_keys import edx
        course_id = edx.locator.CourseLocator.from_string(sender.post_data.course_id)
        import openedx.core.djangoapps.models as md
        modulestorr = md.course_details.modulestore()
        modulestorr.delete_course(course_id,sender.user.id)
        """Xóa khóa học, người xóa là user đang đăng nhập"""
        return {}

