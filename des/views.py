from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
async def index(request):
    return HttpResponse("Hello, async Django!")
