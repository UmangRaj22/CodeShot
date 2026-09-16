from django.shortcuts import render
from django.http import HttpResponse
import base64
from .utils import create_code_image

def home(request):
    image = None

    if request.method == "POST":
        code = request.POST.get("code")
        lang = request.POST.get("lang")
        theme = request.POST.get("theme")
        line_numbers = request.POST.get("line_numbers") == "on"
        mac_buttons = request.POST.get("mac_buttons") == "on"

        img = create_code_image(
            code, lang, theme,
            line_numbers,
            None,
            mac_buttons,
            False,
            20,
            False,
            ""
        )

        img_bytes = img.getvalue()

        if request.POST.get("export_png") == "1":
            response = HttpResponse(img_bytes, content_type="image/png")
            response["Content-Disposition"] = 'attachment; filename="codeshot.png"'
            return response

        image = "data:image/png;base64," + base64.b64encode(img_bytes).decode()

    return render(request, "index.html", {"image": image})
