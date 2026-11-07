import base64
import io

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PIL import Image, UnidentifiedImageError

from .utils import GRADIENT_PAIRS, WALLPAPER_PAIRS, create_code_image


def _read_integer(post, name, default, minimum, maximum):
    value = post.get(name, str(default))
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name.replace('_', ' ').capitalize()} must be a whole number.")
    if not minimum <= value <= maximum:
        raise ValueError(
            f"{name.replace('_', ' ').capitalize()} must be between {minimum} and {maximum}."
        )
    return value


def home(request):
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    image = None
    error = None
    values = request.POST if request.method == "POST" else {}
    gradient_choices = [
        (index, f"Gradient {index + 1:02}")
        for index in range(len(GRADIENT_PAIRS) * 4)
    ]
    wallpaper_choices = [
        (index, f"macOS wallpaper {index + 1:02}")
        for index in range(len(WALLPAPER_PAIRS))
    ]

    if request.method == "POST":
        try:
            backdrop_type = request.POST.get("backdrop_type", "gradient")
            if backdrop_type not in {"gradient", "wallpaper", "solid", "image"}:
                raise ValueError("Choose a supported backdrop type.")

            backdrop_image = None
            if backdrop_type == "image":
                uploaded = request.FILES.get("backdrop_image")
                if not uploaded:
                    raise ValueError("Choose an image to use as the backdrop.")
                if uploaded.size > 8 * 1024 * 1024:
                    raise ValueError("Backdrop images must be 8 MB or smaller.")
                with Image.open(uploaded) as source:
                    if source.format not in {"PNG", "JPEG", "WEBP", "GIF"}:
                        raise ValueError("Use a PNG, JPEG, WebP, or GIF image.")
                    if source.width * source.height > 25_000_000:
                        raise ValueError("Backdrop images must be no larger than 25 megapixels.")
                    source.verify()
                uploaded.seek(0)
                backdrop_image = uploaded.read()

            options = {
                "backdrop_type": backdrop_type,
                "gradient_index": _read_integer(request.POST, "gradient_index", 0, 0, 91),
                "wallpaper_index": _read_integer(request.POST, "wallpaper_index", 0, 0, 18),
                "background_color": request.POST.get("background_color", "#4536a3"),
                "backdrop_image": backdrop_image,
                "aspect_ratio": request.POST.get("aspect_ratio", "16:9"),
                "auto_adjust_width": request.POST.get("auto_adjust_width") == "on",
                "margin_vertical": _read_integer(request.POST, "margin_vertical", 24, 0, 240),
                "margin_horizontal": _read_integer(request.POST, "margin_horizontal", 24, 0, 240),
                "padding_vertical": _read_integer(request.POST, "padding_vertical", 24, 0, 160),
                "padding_horizontal": _read_integer(request.POST, "padding_horizontal", 32, 0, 160),
                "drop_shadow": request.POST.get("drop_shadow") == "on",
                "shadow_x": _read_integer(request.POST, "shadow_x", 0, -100, 100),
                "shadow_y": _read_integer(request.POST, "shadow_y", 12, -100, 100),
                "shadow_blur": _read_integer(request.POST, "shadow_blur", 24, 0, 100),
                "shadow_spread": _read_integer(request.POST, "shadow_spread", 0, -40, 100),
                "corner_radius": _read_integer(request.POST, "corner_radius", 16, 0, 64),
                "font_size": _read_integer(request.POST, "font_size", 16, 10, 36),
                "export_scale": _read_integer(request.POST, "export_scale", 1, 1, 3),
                "show_title": request.POST.get("show_title") == "on",
                "window_title": request.POST.get("window_title", "Untitled"),
            }
            if options["aspect_ratio"] not in {
                "original", "1:1", "4:3", "3:2", "16:9", "9:16", "2:3", "3:4"
            }:
                raise ValueError("Choose a supported aspect ratio.")

            rendered_image = create_code_image(
                request.POST.get("code"),
                request.POST.get("lang"),
                request.POST.get("theme"),
                request.POST.get("line_numbers") == "on",
                request.POST.get("font"),
                request.POST.get("mac_buttons") == "on",
                request.POST.get("background_gradient") == "on",
                options["padding_vertical"],
                request.POST.get("watermark") == "on",
                request.POST.get("watermark_text", ""),
                options,
            )
            image_bytes = rendered_image.getvalue()

            if request.POST.get("export_png") == "1":
                response = HttpResponse(image_bytes, content_type="image/png")
                response["Content-Disposition"] = 'attachment; filename="codeshot.png"'
                return response

            image = "data:image/png;base64," + base64.b64encode(image_bytes).decode()
        except ValueError as exc:
            error = str(exc)
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
            error = "The selected backdrop could not be read as a supported image."

    if is_ajax:
        if error:
            return JsonResponse({"error": error}, status=400)
        return JsonResponse({"image": image})

    return render(request, "index.html", {
        "image": image,
        "error": error,
        "values": values,
        "gradient_choices": gradient_choices,
        "wallpaper_choices": wallpaper_choices,
    })
