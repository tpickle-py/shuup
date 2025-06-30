import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.themes.classic_gray"
    label = "shuup_themes_classic_gray"
    provides = {
        "xtheme": "shuup.themes.classic_gray.theme:ClassicGrayTheme",
    }
