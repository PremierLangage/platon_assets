from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.views.decorators.http import require_POST
from django.views import View



@login_required
@require_POST
class EvaluateView(View):
    
    def post(self, request: HttpRequest):
        post = request.POST



@login_required
@require_POST
class BuildView(View):
    
    def post(self, request: HttpRequest):
        post = request.POST
