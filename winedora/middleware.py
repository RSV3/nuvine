from django.contrib.auth.models import User


class ImpersonateMiddleware(object):
    def process_request(self, request):
        try:
            # __temp_impersonate - use when you only want to impersonate for a single page
            # __impersonate - use when you want to impersonate for an entire flow
            if request.user.is_superuser and "__temp_impersonate" in request.GET:
                impersonate_id = int(request.GET["__temp_impersonate"])
                request.user = User.objects.get(id=impersonate_id)
                return

            if request.user.is_superuser and "__impersonate" in request.GET:
                request.session['impersonate_id'] = int(request.GET["__impersonate"])
            elif "__unimpersonate" in request.GET:
                impersonator = User.objects.get(id=request.session['impersonator'])
                request.user = impersonator
                del request.session['impersonate_id']
                del request.session['impersonator']

            if request.user.is_superuser and 'impersonate_id' in request.session:
                request.session['impersonator'] = request.user.id
                u = User.objects.get(id=request.session['impersonate_id'])
                request.user = u
        except:
            # __impersonate values was not an int or
            # or __unimpersonate  not in request.session
            # the user does not exist
            pass
