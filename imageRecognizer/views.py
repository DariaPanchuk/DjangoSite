from django.shortcuts import render
from django.views import View
from .models import ImageUpload
from .utils import classify_image

class IndexView(View):
    template_name = 'imageRecognizer/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        obj = None
        if request.FILES.get('image'):
            img_file = request.FILES['image']
            obj = ImageUpload.objects.create(image=img_file)

            try:
                label, score = classify_image(obj.image.path)
                obj.result = label
                obj.confidence = score
                obj.save()
            except Exception as e:
                print(f"Error: {e}")

        return render(request, self.template_name, {'obj': obj})