


SIMPLE_INPUT_TYPES = (
    "text",
    "hidden",
    "password",
    "submit",
    "image",
    "search",
    "number",
    "email",
    "url",
)


def extract_form_fields(soup):  # pragma: no cover  # noqa (C901)
    # Based on https://gist.github.com/simonw/104413
    "Turn a BeautifulSoup form in to a dict of fields and default values"
    fields = {}
    for input in soup.findAll("input"):
        name = input.get("name")
        value = input.get("value") or ""
        type = input.get("type", "text")
        if not name:
            continue

        if type in SIMPLE_INPUT_TYPES:
            fields[name] = value
            continue

        if type in ("checkbox", "radio"):
            if input.get("checked"):
                value = value or "on"

            if value:
                fields[name] = value
            else:
                fields.setdefault(name, value)
            continue

        assert False, "input type %s not supported" % type

    for textarea in soup.findAll("textarea"):
        name = textarea.get("name")
        if name:
            fields[name] = textarea.string or ""

    # select fields
    for select in soup.findAll("select"):
        options = select.findAll("option")
        selected_options = [option for option in options if option.has_attr("selected")]

        if not selected_options and options:
            selected_options = [options[0]]

        value = [option["value"] for option in selected_options if option["value"]]

        fields[select["name"]] = value or ""

    return fields
