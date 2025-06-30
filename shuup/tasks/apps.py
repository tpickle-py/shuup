import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.tasks"
    label = "shuup_tasks"
    default_auto_field = "django.db.models.BigAutoField"
    provides = {
        "admin_module": [
            "shuup.tasks.admin_module.TaskAdminModule",
            "shuup.tasks.admin_module.TaskTypeAdminModule",
        ]
    }
