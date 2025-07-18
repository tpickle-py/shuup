from typing import Optional

from babel.numbers import format_currency, format_number
from django.template import loader

from shuup.utils.django_compat import force_text
from shuup.utils.i18n import get_current_babel_locale
from shuup.utils.numbers import parse_decimal_string


class DashboardBlock:
    type: Optional[str] = None
    sort_order = 0
    SIZES = ("small", "normal", "medium", "large", "full")
    default_size = "normal"

    def __init__(self, id, size=None, color=None, sort_order=0):
        self.id = id
        if size not in self.SIZES:  # pragma: no cover
            size = self.default_size
        self.size = size
        self.color = color
        self.sort_order = sort_order


class DashboardContentBlock(DashboardBlock):
    type = "normal"

    def __init__(self, id, content, size="normal"):
        super().__init__(id=id, size=size)
        self.content = content

    @classmethod
    def by_rendering_template(cls, id, request, template_name, context):
        content = loader.render_to_string(template_name=template_name, context=context, request=request)
        return cls(id=id, content=content)


class DashboardValueBlock(DashboardBlock):
    type = "value"
    default_size = "small"

    def __init__(self, id, value, title, **kwargs):
        super().__init__(id=id, size="small")
        self.value = value
        self.title = title
        self.color = kwargs.pop("color", None)
        self.icon = kwargs.pop("icon", None)
        self.subtitle = kwargs.pop("subtitle", None)
        self.sort_order = kwargs.pop("sort_order", 0)


class DashboardNumberBlock(DashboardValueBlock):
    def __init__(self, id, value, title, **kwargs):
        value = parse_decimal_string(value)
        if int(value) == value:
            value = int(value)
        value = format_number(value, locale=get_current_babel_locale())
        super().__init__(id, value, title, **kwargs)


class DashboardMoneyBlock(DashboardValueBlock):
    def __init__(self, id, value, title, currency, **kwargs):
        self.currency = currency
        value = parse_decimal_string(value)
        value = format_currency(value, currency=self.currency, locale=get_current_babel_locale())
        super().__init__(id, value, title, **kwargs)


class DashboardChartBlock(DashboardBlock):
    type = "chart"
    default_size = "medium"
    BLOCK_TEMPLATE = """
    <div class="color-block block-purple">
        <h2 class="block-title">%(title)s</h2>
        <div class="block-content">
            <canvas id="chart-%(id)s" height="250"></canvas>
        </div>
    </div>
    <script>
    window.CHART_CONFIGS = window.CHART_CONFIGS || {};
    window.CHART_CONFIGS["%(id)s"] = %(config)s;
    </script>
    """

    def get_chart(self):
        """
        Get the actual chart instance for this block.

        :return: The chart (or None, if it can't be rendered)
        :rtype: shuup.admin.dashboard.charts.Chart|None
        """
        return None

    def __init__(self, id, size="normal"):
        super().__init__(id=id, size=size)
        self.content = self._get_content()

    def _get_content(self):
        chart = self.get_chart()
        if not chart:
            return None
        content = self.BLOCK_TEMPLATE % {
            "title": force_text(chart.title),
            "id": self.id,
            "config": chart.get_config_json(),
            "icon": "fa-line-chart",
        }
        return content
