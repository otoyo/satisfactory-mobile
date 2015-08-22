from functools import wraps
from django.http import Http404

def post_required(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            raise Http404
        return f(request, *args, **kwargs)
    return wrapper
