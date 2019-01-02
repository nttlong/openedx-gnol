import xdj
@xdj.Controller(
    url="",
    template="index.html"
)
class IndexControler(xdj.BaseController):
    def __init__(self):
        x=1
    def on_get(self,model):
        import branding
        model.data = xdj.dobject()
        model.data.courses = branding.get_visible_courses()
        for item in model.data.courses:
            item.key = item.id.html_id()
        return self.render(model)