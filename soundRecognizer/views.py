from django.shortcuts import render
from django.views import View
from .models import AudioUpload
from .utils import analyze_audio


class IndexView(View):
    template_name = 'soundRecognizer/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        obj = None
        if request.FILES.get('audio'):
            audio_file = request.FILES['audio']
            obj = AudioUpload.objects.create(audio=audio_file)
            obj.title = audio_file.name
            obj.result = analyze_audio(obj.audio.path)
            obj.save()

        return render(request, self.template_name, {'obj': obj})