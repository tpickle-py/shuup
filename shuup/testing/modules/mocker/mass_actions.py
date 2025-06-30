

from django.utils.translation import ugettext_lazy as _

from shuup.admin.utils.picotable import PicotableMassAction, PicotableMassActionProvider


class DummyPicotableMassAction1(PicotableMassAction):
    label = _("Dummy Mass Action #1")
    identifier = "dummy_mass_action_1"


class DummyPicotableMassAction2(PicotableMassAction):
    label = _("Dummy Mass Action #2")
    identifier = "dummy_mass_action_2"


class DummyMassActionProvider(PicotableMassActionProvider):
    @classmethod
    def get_mass_actions_for_view(cls, view):
        return [
            "shuup.testing.modules.mocker.mass_actions:DummyPicotableMassAction1",
            "shuup.testing.modules.mocker.mass_actions:DummyPicotableMassAction2",
        ]
