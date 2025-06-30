import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.reports"
    provides = {
        "admin_module": ["shuup.reports.admin_module:ReportsAdminModule"],
        "report_writer_populator": ["shuup.reports.writer.populate_default_writers"],
    }
