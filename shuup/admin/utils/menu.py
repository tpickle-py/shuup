

def is_menu_open(request):
    return bool(request.session.get("menu_open", True))
