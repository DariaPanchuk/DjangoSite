from django.shortcuts import render
from django.views import View
from .models import SpectrumAudio
from .utils import analyze_signal_data


class IndexView(View):
    template_name = 'spectrumRecognizer/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        obj = None
        if request.FILES.get('audio'):
            audio_file = request.FILES['audio']
            obj = SpectrumAudio.objects.create(audio=audio_file)
            obj.title = audio_file.name
            obj.result_text = analyze_signal_data(obj.audio.path)
            obj.save()

        return render(request, self.template_name, {'obj': obj})