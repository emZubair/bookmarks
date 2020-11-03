from django.http import HttpResponseBadRequest


def ajax_required(f):
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__

    return wrap


def self_view_not_allowed(f):
    def wrap(request, *args, **kwargs):
        username = kwargs.get('username', None)
        if username and request.user.username == username:
            return HttpResponseBadRequest()
        return f(request, username, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__

