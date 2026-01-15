from django.shortcuts import render
from django.views import View
from .models import CodeFiles
from .utils import generate_docs

class IndexView(View):
    template_name = 'codeRecognizer/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        obj = None
        if request.FILES.get('code_file'):
            uploaded_file = request.FILES['code_file']
            obj = CodeFiles.objects.create(code_file=uploaded_file)
            obj.title = uploaded_file.name
            obj.generated_docs = generate_docs(obj.code_file.path)
            obj.save()

        return render(request, self.template_name, {'obj': obj})