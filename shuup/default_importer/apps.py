import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.default_importer"
    provides = {
        "importers": [
            "shuup.default_importer.importers.ProductImporter",
            "shuup.default_importer.importers.PersonContactImporter",
            "shuup.default_importer.importers.CompanyContactImporter",
        ],
    }
