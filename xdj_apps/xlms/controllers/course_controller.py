import xdj
from xdj_apps.xlms.controllers.commons import base_controller


@xdj.Controller(
    url="course/(?P<course_id>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)",
    template="course.html",
    params=["course_id"]
)
class CourseController(base_controller.XlmsController):
    def on_get(self,model):
        #/home/nttlong/code/edx-hawthorn.2-3/apps/edx/edx-platform/lms/djangoapps/courseware/courses.py
        #'/opt/edx-hawthorn.2-3/apps/edx/edx-platform/common/lib/xmodule/xmodule/modulestore/django.py'
        #'/opt/edx-hawthorn.2-3/apps/edx/venvs/edxapp/lib/python2.7/site-packages/opaque_keys/__init__.py'
        # courseware_outline = commons.course_get_tab_course(model.request, model.params.course_id)
        # home_fragment_view.render_to_fragment(request, course_id=course_id, **kwargs)
        if isinstance(model,xdj.Model):
            import urllib

            courseware_outline, privilege = self.get_course_outline(model, model.params.course_id)

            if privilege() =="need_login":
                return model.redirect(model.appUrl+"/"+self.rel_login_url+"?next="+urllib.quote(model.currentUrl,""))
            if privilege() =="deny":
                return model.redirect(model.appUrl+"/"+self.rel_login_url+"?next="+urllib.quote(model.currentUrl,""))



            model.outline = courseware_outline
            return self.render(model)
    @xdj.Page(
        url="details",
        template="course_details.html"
    )
    class detail(object):
        def on_get(self,model):
            import lms.djangoapps.courseware.views as V
            import courseware.views.index as I
            #/home/nttlong/code/edx-hawthorn.2-3/apps/edx/edx-platform/lms/djangoapps/courseware/views/index.py
            x = I.CoursewareIndex().render(request)
            return self.render(model)