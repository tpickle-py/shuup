from shuup.notify.base import Action, Binding, ConstantUse
from shuup.notify.typology import Text


class SetDebugFlag(Action):
    identifier = "set_debug_flag"
    flag_name = Binding("Flag Name", Text, constant_use=ConstantUse.CONSTANT_ONLY, default="debug")

    def execute(self, context):
        context.set(self.get_value(context, "flag_name"), True)
