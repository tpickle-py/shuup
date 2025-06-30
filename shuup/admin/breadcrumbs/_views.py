from shuup.admin.base import MenuEntry


class BreadcrumbedView(object):
    def get_breadcrumb_parents(self):
        return [MenuEntry(text=self.parent_name, url=self.parent_url)]
