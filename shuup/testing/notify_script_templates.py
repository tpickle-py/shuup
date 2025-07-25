from shuup.notify.base import ScriptTemplate
from shuup.notify.conditions import BooleanEqual
from shuup.notify.models import Script
from shuup.notify.script import Step, StepNext
from shuup.simple_supplier.notify_events import AlertLimitReached


class DummyScriptTemplate(ScriptTemplate):
    identifier = "dummy_script_template"
    name = "A Dummy Script Template"
    description = "More Texts"
    help_text = "A good help here"

    def create_script(self, shop, form=None):
        condition = BooleanEqual({"v1": {"constant": True}, "v2": {"constant": False}})
        script = Script(
            event_identifier=AlertLimitReached.identifier,
            name="Dummy Alert",
            enabled=True,
            shop=shop,
        )
        script.set_steps([Step(next=StepNext.STOP, conditions=(condition,))])
        script.save()
        return script

    def can_edit_script(self):
        return False

    def update_script(self, form):
        return self.script_instance
