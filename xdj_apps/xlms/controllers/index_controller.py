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
        model.items = branding.get_visible_courses()
        return self.render(model)