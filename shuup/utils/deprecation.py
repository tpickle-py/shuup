#!/usr/bin/env python


class RemovedInShuup20Warning(PendingDeprecationWarning):
    pass


class RemovedFromShuupWarning(DeprecationWarning):
    pass


RemovedInFutureShuupWarning = RemovedInShuup20Warning
