import os
from django.shortcuts import render
from django.views import View
from .models import VideoUpload
from .utils import analyze_video_file, download_video_temp


class IndexView(View):
    template_name = 'videoRecognizer/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        obj = None
        error_msg = None

        if request.FILES.get('video'):
            video_file = request.FILES['video']
            obj = VideoUpload.objects.create(video=video_file)
            # Викликаємо нову функцію analyze_video_file
            obj.result = analyze_video_file(obj.video.path)
            obj.save()

        elif request.POST.get('url'):
            user_url = request.POST.get('url')
            temp_path, title = download_video_temp(user_url)

            if temp_path and os.path.exists(temp_path):
                obj = VideoUpload.objects.create(url=user_url)
                result_text = analyze_video_file(temp_path)

                if title:
                    obj.title = title

                obj.result = result_text
                obj.save()

                try:
                    os.remove(temp_path)
                except Exception as e:
                    print(f"Не вдалося видалити файл: {e}")
            else:
                error_msg = "Не вдалося завантажити відео (перевірте доступність)"

        return render(request, self.template_name, {'obj': obj, 'error': error_msg})