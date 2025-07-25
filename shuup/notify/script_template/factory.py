from shuup.notify.script_template.generic import GenericSendEmailScriptTemplate


def generic_send_email_script_template_factory(identifier, event, name, description, help_text, initial=None):
    """
    A factory to create a generic script template based on `GenericSendEmailScriptTemplate` class.

    :param str identifier: a unique identifier for this ScriptTemplate with a max of 64 characters
    :param shuup.notify.Event event: the event class which will be used to trigger the notification
    :param str name: the name of the ScriptTemplate
    :param str description: the description of the ScriptTemplate to present to the user
    :param str help_text: a text to help users understand how this script will work
    :param dict|None initial: the initial data to use in forms or None
    """
    attrs = {}
    attrs.setdefault("identifier", identifier)
    attrs.setdefault("event", event)
    attrs.setdefault("name", name)
    attrs.setdefault("description", description)
    attrs.setdefault("help_text", help_text)
    attrs.setdefault("initial", initial or {})
    return type("GenericSendEmailScriptTemplate", (GenericSendEmailScriptTemplate,), attrs)
