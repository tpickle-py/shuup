SHUUP_REGISTRATION_REQUIRES_ACTIVATION = True

#: The Shuup default registration form for person
#: This overrides the setting from `registration` lib
#: to allow custom logic like receiving the request from kwargs
REGISTRATION_FORM = "shuup.front.apps.registration.forms.PersonRegistrationForm"
