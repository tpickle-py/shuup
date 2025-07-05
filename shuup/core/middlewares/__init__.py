# Middleware package for Shuup core

from .weak_password_middleware import WeakPasswordInterceptMiddleware

__all__ = ["WeakPasswordInterceptMiddleware"]
