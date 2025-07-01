from django.utils.translation import ugettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import ChoicesFilter, Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import get_person_contact
from shuup.tasks.models import Task, TaskStatus, TaskType


class TaskListView(PicotableListView):
    model = Task
    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="name",
            display="name",
            filter_config=TextFilter(filter_field="name", placeholder=_("Filter by name...")),
        ),
        Column(
            "creator",
            _("Creator"),
            display="get_creator_name_display",
            filter_config=TextFilter(filter_field="creator__name", placeholder=_("Filter by creator...")),
        ),
        Column(
            "status",
            _("Status"),
            filter_config=ChoicesFilter(TaskStatus.choices),
            class_name="text-center",
        ),
        Column(
            "priority",
            _("Priority"),
            display="get_priority_display",
            class_name="text-center",
        ),
        Column(
            "comments",
            _("Comments"),
            sort_field="comments",
            display="get_comments_count",
            class_name="text-center",
        ),
    ]
    toolbar_buttons_provider_key = "task_list_toolbar_provider"
    mass_actions_provider_key = "task_list_actions_provider"

    def get_comments_count(self, instance, **kwargs):
        return instance.comments.for_contact(get_person_contact(self.request.user)).count()

    def get_queryset(self):
        """
        Return a queryset of Task objects filtered for the current shop.

        This method retrieves the current shop from the request and returns
        all Task instances associated with that shop using the custom
        'for_shop' manager method.

        Returns:
            QuerySet: A queryset of Task objects for the current shop.
        """

        return Task.objects.for_shop(get_shop(self.request))

    def get_creator_name_display(self, instance, **kwargs):
        if not instance.creator or not instance.creator.name:
            return f"No name set (id: {getattr(instance.creator, 'id', 'unknown')})"
        return instance.creator.name

    def get_priority_display(self, instance, **kwargs):
        return f"{instance.priority}"


class TaskTypeListView(PicotableListView):
    model = TaskType
    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="name",
            display="name",
            filter_config=TextFilter(filter_field="translations__name", placeholder=_("Filter by name...")),
        )
    ]

    def get_queryset(self):
        return TaskType.objects.filter(shop=get_shop(self.request))
