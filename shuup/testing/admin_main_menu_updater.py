

from shuup.admin.menu import PRODUCTS_MENU_CATEGORY
from shuup.core.utils.menu import MainMenuUpdater


class TestAdminMainMenuUpdater(MainMenuUpdater):
    updates = {
        PRODUCTS_MENU_CATEGORY: [
            {"identifier": "test_0", "title": "Test 0"},
            {"identifier": "test_1", "title": "Test 1"},
        ],
    }
