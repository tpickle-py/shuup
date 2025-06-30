from shuup.front.utils.order_source import BaseLinePropertiesDescriptor, LineProperty


class TestLinePropertiesDescriptor(BaseLinePropertiesDescriptor):
    @classmethod
    def get_line_properties(cls, line, **kwargs):
        yield LineProperty("Type", str(line.type))
