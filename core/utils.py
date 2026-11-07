import io
import math

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATH = Path(__file__).resolve().parent / "fonts" / "DejaVuSansMono.ttf"

# =========================================================
# HIGH RESOLUTION RENDERING
# =========================================================

SCALE = 4

GRADIENT_PAIRS = (
    ("#4f46e5", "#06b6d4"), ("#7c3aed", "#ec4899"),
    ("#2563eb", "#a855f7"), ("#0f766e", "#22c55e"),
    ("#ea580c", "#facc15"), ("#be123c", "#fb7185"),
    ("#0f172a", "#475569"), ("#1d4ed8", "#38bdf8"),
    ("#6d28d9", "#c084fc"), ("#047857", "#a3e635"),
    ("#c2410c", "#fb923c"), ("#9f1239", "#f472b6"),
    ("#164e63", "#2dd4bf"), ("#312e81", "#818cf8"),
    ("#713f12", "#fbbf24"), ("#365314", "#bef264"),
    ("#831843", "#f9a8d4"), ("#1e3a8a", "#60a5fa"),
    ("#581c87", "#d8b4fe"), ("#134e4a", "#5eead4"),
    ("#7f1d1d", "#fca5a5"), ("#1f2937", "#9ca3af"),
    ("#4338ca", "#f0abfc"),
)

WALLPAPER_PAIRS = (
    ("#0b1c2c", "#086788"), ("#071a35", "#6941c6"),
    ("#172554", "#db2777"), ("#102a43", "#2dd4bf"),
    ("#312e81", "#f97316"), ("#3b0764", "#e11d48"),
    ("#052e16", "#65a30d"), ("#111827", "#2563eb"),
    ("#431407", "#f59e0b"), ("#164e63", "#a855f7"),
    ("#1e1b4b", "#06b6d4"), ("#500724", "#fb7185"),
    ("#082f49", "#38bdf8"), ("#365314", "#facc15"),
    ("#292524", "#c2410c"), ("#172554", "#4f46e5"),
    ("#0f172a", "#14b8a6"), ("#3f1d2e", "#fb923c"),
    ("#202124", "#8b5cf6"),
)

GRADIENT_DIRECTIONS = (0, 90, 45, 135)


# =========================================================
# COLOR HELPERS
# =========================================================

def _hex_to_rgb(value):
    value = (value or "#0f172a").lstrip("#")

    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)

    try:
        return tuple(
            int(value[i:i + 2], 16)
            for i in (0, 2, 4)
        )
    except Exception:
        return (15, 23, 42)


def _mix_colors(color_a, color_b, weight):
    color_a = _hex_to_rgb(color_a)
    color_b = _hex_to_rgb(color_b)

    weight = max(0, min(1, weight))

    return tuple(
        int(
            color_a[i] * (1 - weight)
            + color_b[i] * weight
        )
        for i in range(3)
    )


def _rgb_to_hex(color):
    return "#{:02x}{:02x}{:02x}".format(*color)


# =========================================================
# THEME PALETTES
# =========================================================

def _theme_palette(theme_name):

    palette = {

        "dracula": {
            "background": "#46358a",
            "background_top": "#17152f",
            "code": "#282a36",
            "accent": "#bd93f9",
        },

        "monokai": {
            "background": "#9f413d",
            "background_top": "#6d2f2d",
            "code": "#272822",
            "accent": "#f8f8f2",
        },

        "github-dark": {
            "background": "#263b52",
            "background_top": "#172333",
            "code": "#0d1117",
            "accent": "#58a6ff",
        },

        "one-dark": {
            "background": "#303b52",
            "background_top": "#202735",
            "code": "#282c34",
            "accent": "#61afef",
        },

        "nord": {
            "background": "#394451",
            "background_top": "#29313b",
            "code": "#2e3440",
            "accent": "#88c0d0",
        },

        "solarized-dark": {
            "background": "#315b60",
            "background_top": "#183f43",
            "code": "#002b36",
            "accent": "#2aa198",
        },

        "solarized-light": {
            "background": "#c8c0a8",
            "background_top": "#aaa28d",
            "code": "#fdf6e3",
            "accent": "#268bd2",
        },

        "gruvbox-dark": {
            "background": "#6f4932",
            "background_top": "#443025",
            "code": "#282828",
            "accent": "#fabd2f",
        },

        "gruvbox-light": {
            "background": "#c8a96b",
            "background_top": "#a98950",
            "code": "#fbf1c7",
            "accent": "#d79921",
        },

        "native": {
            "background": "#3d4650",
            "background_top": "#242b32",
            "code": "#202020",
            "accent": "#ffffff",
        },

        "friendly": {
            "background": "#64748b",
            "background_top": "#475569",
            "code": "#f0f0f0",
            "accent": "#268bd2",
        },

        "bw": {
            "background": "#555555",
            "background_top": "#222222",
            "code": "#000000",
            "accent": "#ffffff",
        },

        "pastie": {
            "background": "#68705e",
            "background_top": "#444b3e",
            "code": "#ffffff",
            "accent": "#333333",
        },

        "vim": {
            "background": "#253525",
            "background_top": "#182418",
            "code": "#000000",
            "accent": "#55aa55",
        },
    }

    theme_key = (theme_name or "dracula").lower()
    if theme_key in palette:
        return palette[theme_key]

    style_background = get_style_by_name(theme_key).background_color or "#282a36"
    return {
        "background": _rgb_to_hex(
            _mix_colors(style_background, "#ffffff", 0.2)
        ),
        "background_top": _rgb_to_hex(
            _mix_colors(style_background, "#000000", 0.2)
        ),
        "code": style_background,
        "accent": "#d9f85b",
    }


# =========================================================
# FONT LOADER
# =========================================================

def _load_font(size, preferred=None):

    candidates = []

    if preferred:
        candidates.append(preferred)

    candidates.extend([
        "DejaVuSansMono.ttf",
        "DejaVuSans.ttf",
        "Consolas.ttf",
        "arial.ttf",
        "Arial.ttf",
    ])

    for font_path in candidates:
        try:
            return ImageFont.truetype(
                font_path,
                size
            )
        except Exception:
            pass

    return ImageFont.load_default()


# =========================================================
# CREATE CODE IMAGE
# =========================================================

def create_code_image(
    code,
    lang,
    theme,
    line_numbers,
    font_name,
    mac_buttons,
    bg_gradient,
    padding,
    watermark,
    watermark_text,
    options=None
):
    options = options or {}
    scale_multiplier = max(1, min(3, int(options.get("export_scale", 1))))
    SCALE = 4 * scale_multiplier

    # -----------------------------------------------------
    # DEFAULT CODE
    # -----------------------------------------------------

    if not code:
        code = "print('Hello, CodeShot!')"

    # -----------------------------------------------------
    # GET LEXER
    # -----------------------------------------------------

    try:
        lexer = get_lexer_by_name(lang)
    except Exception:
        lexer = guess_lexer(code)

    # -----------------------------------------------------
    # THEME
    # -----------------------------------------------------

    palette = _theme_palette(theme)

    outer_background = palette["background"]
    outer_top = palette["background_top"]
    code_background = palette["code"]

    # -----------------------------------------------------
    # FONT
    # -----------------------------------------------------

    try:
        if font_name:
            ImageFont.truetype(
                font_name,
                24
            )
    except Exception:
        font_name = None

    # -----------------------------------------------------
    # PYGMENTS
    #
    # Everything is rendered at 4× resolution.
    # -----------------------------------------------------

    font_size = max(10, min(36, int(options.get("font_size", 16))))
    formatter_kwargs = {
        "style": theme or "dracula",

        # We draw line numbers ourselves.
        "line_numbers": False,

        # Render the code at 4× for a crisp final image.
        "font_size": font_size * SCALE,

        # Compact line spacing keeps tall snippets manageable.
        "line_pad": 6 * SCALE,
        "font_name": str(FONT_PATH),
    }

    if font_name:
        formatter_kwargs["font_name"] = font_name

    formatter = ImageFormatter(
        **formatter_kwargs
    )

    # -----------------------------------------------------
    # SYNTAX HIGHLIGHTING
    # -----------------------------------------------------

    code_img_data = highlight(
        code,
        lexer,
        formatter
    )

    code_img = Image.open(
        io.BytesIO(code_img_data)
    ).convert("RGBA")

    # -----------------------------------------------------
    # CODE LINES
    # -----------------------------------------------------

    lines = code.splitlines()

    if not lines:
        lines = [""]

    line_count = len(lines)

    # -----------------------------------------------------
    # MANUAL LINE NUMBER GUTTER
    # -----------------------------------------------------

    if line_numbers:

        gutter_width = 70 * SCALE

        number_font = _load_font(
            max(9, int(font_size * 0.8)) * SCALE
        )

    else:

        gutter_width = 0
        number_font = None

    # -----------------------------------------------------
    # CODE AREA
    # -----------------------------------------------------

    code_area_width = (
        code_img.width
        + gutter_width
        + 12 * SCALE
    )

    code_area_height = (
        code_img.height
        + 12 * SCALE
    )

    code_area = Image.new(
        "RGBA",
        (
            code_area_width,
            code_area_height
        ),
        _hex_to_rgb(code_background) + (255,)
    )
    if not options.get("auto_adjust_width", True):
        fixed_width = max(code_area_width, 720 * SCALE)
        if fixed_width > code_area_width:
            fixed_area = Image.new(
                "RGBA",
                (fixed_width, code_area_height),
                _hex_to_rgb(code_background) + (255,),
            )
            fixed_area.alpha_composite(code_area)
            code_area = fixed_area
            code_area_width = fixed_width

    code_draw = ImageDraw.Draw(
        code_area
    )

    # -----------------------------------------------------
    # MANUAL LINE NUMBERS
    # -----------------------------------------------------

    if line_numbers:

        # ImageFormatter spacing:
        # font_size + 2 × line_pad
        line_height = (font_size + 12) * SCALE

        number_color = (
            105,
            112,
            128,
            185
        )

        for index in range(line_count):

            number = str(index + 1)

            bbox = number_font.getbbox(
                number
            )

            number_width = (
                bbox[2]
                - bbox[0]
            )

            number_x = (
                gutter_width
                - number_width
                - 16 * SCALE
            )

            number_y = (
                6 * SCALE
                + index * line_height
            )

            code_draw.text(
                (
                    number_x,
                    number_y
                ),
                number,
                fill=number_color,
                font=number_font
            )

    # -----------------------------------------------------
    # ADD HIGHLIGHTED CODE
    # -----------------------------------------------------

    code_area.alpha_composite(
        code_img,
        (
            gutter_width
            + 8 * SCALE,
            6 * SCALE
        )
    )

    # -----------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------

    pad_x = max(0, min(160, int(options.get("padding_horizontal", padding or 32))))
    pad_y = max(0, min(160, int(options.get("padding_vertical", padding or 24))))
    margin_x = max(0, min(240, int(options.get("margin_horizontal", 24))))
    margin_y = max(0, min(240, int(options.get("margin_vertical", 24))))
    shadow_extent_x = (
        abs(max(-100, min(100, int(options.get("shadow_x", 0)))))
        + max(0, min(100, int(options.get("shadow_blur", 24))))
        + max(0, min(100, int(options.get("shadow_spread", 0))))
        + 8
    )
    shadow_extent_y = (
        abs(max(-100, min(100, int(options.get("shadow_y", 12)))))
        + max(0, min(100, int(options.get("shadow_blur", 24))))
        + max(0, min(100, int(options.get("shadow_spread", 0))))
        + 8
    ) if options.get("drop_shadow", True) else 0

    # Top space for Mac buttons
    header_height = 48

    window_width = (
        code_area.width
        + pad_x * 2 * SCALE
    )

    window_height = (
        code_area.height
        + header_height * SCALE
        + pad_y * 2 * SCALE
    )

    canvas_width = (
        window_width
        + (margin_x + shadow_extent_x) * 2 * SCALE
    )

    canvas_height = (
        window_height
        + (margin_y + shadow_extent_y) * 2 * SCALE
    )

    aspect_ratio = options.get("aspect_ratio", "original")
    ratios = {
        "1:1": (1, 1), "4:3": (4, 3), "3:2": (3, 2),
        "16:9": (16, 9), "9:16": (9, 16), "2:3": (2, 3),
        "3:4": (3, 4),
    }
    if aspect_ratio in ratios:
        ratio_width, ratio_height = ratios[aspect_ratio]
        ratio_unit = max(
            math.ceil(canvas_width / (ratio_width * SCALE)),
            math.ceil(canvas_height / (ratio_height * SCALE)),
        )
        canvas_width = ratio_unit * ratio_width * SCALE
        canvas_height = ratio_unit * ratio_height * SCALE

    # -----------------------------------------------------
    # MAIN CANVAS
    # -----------------------------------------------------

    canvas = Image.new(
        "RGBA",
        (
            canvas_width,
            canvas_height
        ),
        (0, 0, 0, 255)
    )

    # -----------------------------------------------------
    # OUTER BACKGROUND
    # -----------------------------------------------------

    background = Image.new(
        "RGBA",
        (
            canvas_width,
            canvas_height
        ),
        (0, 0, 0, 255)
    )

    backdrop_type = options.get("backdrop_type", "gradient")
    gradient_index = max(0, min(91, int(options.get("gradient_index", 0))))
    wallpaper_index = max(0, min(18, int(options.get("wallpaper_index", 0))))
    if backdrop_type == "solid":
        background_color = _hex_to_rgb(options.get("background_color", outer_background))
        background = Image.new("RGBA", (canvas_width, canvas_height), background_color + (255,))
    elif backdrop_type == "image" and options.get("backdrop_image"):
        with Image.open(io.BytesIO(options["backdrop_image"])) as backdrop:
            backdrop = backdrop.convert("RGBA")
            fit_ratio = max(canvas_width / backdrop.width, canvas_height / backdrop.height)
            resized = backdrop.resize(
                (math.ceil(backdrop.width * fit_ratio), math.ceil(backdrop.height * fit_ratio)),
                Image.Resampling.LANCZOS,
            )
            left = (resized.width - canvas_width) // 2
            top = (resized.height - canvas_height) // 2
            resized = resized.crop((left, top, left + canvas_width, top + canvas_height))
            base_color = _hex_to_rgb(options.get("background_color", outer_background))
            base = Image.new("RGBA", (canvas_width, canvas_height), base_color + (255,))
            background = Image.alpha_composite(base, resized)
    else:
        if backdrop_type == "wallpaper":
            start_hex, end_hex = WALLPAPER_PAIRS[wallpaper_index]
            angle = 45
        elif backdrop_type == "gradient":
            start_hex, end_hex = GRADIENT_PAIRS[gradient_index % len(GRADIENT_PAIRS)]
            angle = GRADIENT_DIRECTIONS[gradient_index // len(GRADIENT_PAIRS)]
        else:
            start_hex, end_hex = outer_top, outer_background
            angle = 0

        start = Image.new("RGBA", (canvas_width, canvas_height), _hex_to_rgb(start_hex) + (255,))
        end = Image.new("RGBA", (canvas_width, canvas_height), _hex_to_rgb(end_hex) + (255,))
        mask = Image.linear_gradient("L").resize((canvas_width, canvas_height))
        if angle:
            mask = mask.rotate(angle, resample=Image.Resampling.BICUBIC).resize(
                (canvas_width, canvas_height)
            )
        background = Image.composite(end, start, mask)

    # -----------------------------------------------------
    # OPTIONAL GLOW
    # -----------------------------------------------------

    if bg_gradient and backdrop_type not in ("solid", "image"):

        glow_layer = Image.new(
            "RGBA",
            (
                canvas_width,
                canvas_height
            ),
            (0, 0, 0, 0)
        )

        glow_draw = ImageDraw.Draw(
            glow_layer
        )

        accent_rgb = _hex_to_rgb(
            palette["accent"]
        )

        glow_draw.ellipse(
            (
                -200 * SCALE,
                -180 * SCALE,
                int(canvas_width * 0.65),
                int(canvas_height * 0.75)
            ),
            fill=(
                accent_rgb[0],
                accent_rgb[1],
                accent_rgb[2],
                28
            )
        )

        glow_layer = glow_layer.filter(
            ImageFilter.GaussianBlur(
                60 * SCALE
            )
        )

        background = Image.alpha_composite(
            background,
            glow_layer
        )

    canvas.alpha_composite(
        background
    )

    # -----------------------------------------------------
    # WINDOW POSITION
    # -----------------------------------------------------

    window_x = (
        canvas_width
        - window_width
    ) // 2

    window_y = (
        canvas_height
        - window_height
    ) // 2

    # -----------------------------------------------------
    # SHADOW
    # -----------------------------------------------------

    shadow_enabled = options.get("drop_shadow", True)
    shadow_x = max(-100, min(100, int(options.get("shadow_x", 0)))) * SCALE
    shadow_y = max(-100, min(100, int(options.get("shadow_y", 12)))) * SCALE
    shadow_blur = max(0, min(100, int(options.get("shadow_blur", 24)))) * SCALE
    shadow_spread = max(-40, min(100, int(options.get("shadow_spread", 0)))) * SCALE
    shadow_padding = shadow_blur + abs(shadow_x) + abs(shadow_y) + abs(shadow_spread) + 8 * SCALE
    shadow = Image.new(
        "RGBA",
        (window_width + shadow_padding * 2, window_height + shadow_padding * 2),
        (0, 0, 0, 0)
    )
    shadow_draw = ImageDraw.Draw(shadow)
    if shadow_enabled:
        shadow_draw.rounded_rectangle(
            (
                shadow_padding - shadow_spread,
                shadow_padding - shadow_spread,
                shadow_padding + window_width + shadow_spread,
                shadow_padding + window_height + shadow_spread
            ),
            radius=max(0, 16 * SCALE + shadow_spread),
            fill=(0, 0, 0, 115)
        )
        if shadow_blur:
            shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        canvas.alpha_composite(
            shadow,
            (
                window_x + shadow_x - shadow_padding,
                window_y + shadow_y - shadow_padding
            )
        )

    # -----------------------------------------------------
    # MAIN CODE WINDOW
    # -----------------------------------------------------

    window = Image.new(
        "RGBA",
        (
            window_width,
            window_height
        ),
        (0, 0, 0, 0)
    )

    window_draw = ImageDraw.Draw(
        window
    )

    # -----------------------------------------------------
    # SINGLE DARK CODE CARD
    # -----------------------------------------------------

    corner_radius = max(0, min(64, int(options.get("corner_radius", 16)))) * SCALE
    window_draw.rounded_rectangle(
        (
            0,
            0,
            window_width - 1,
            window_height - 1
        ),
        radius=corner_radius,
        fill=_hex_to_rgb(
            code_background
        ) + (255,)
    )

    # -----------------------------------------------------
    # MODERN MACOS TRAFFIC LIGHTS
    #
    # IMPORTANT:
    # Drawn at 4× resolution.
    # Then entire image is downsampled.
    # This creates smooth anti-aliased circles.
    # -----------------------------------------------------

    if mac_buttons:

        button_radius = 7 * SCALE

        button_y = 22 * SCALE

        button_start_x = 28 * SCALE

        button_gap = 23 * SCALE

        mac_colors = [
            (255, 95, 87, 255),      # Red
            (254, 188, 46, 255),     # Yellow
            (40, 201, 64, 255),      # Green
        ]

        for index, color in enumerate(mac_colors):

            center_x = (
                button_start_x
                + index * button_gap
            )

            window_draw.ellipse(
                (
                    center_x - button_radius,
                    button_y - button_radius,
                    center_x + button_radius,
                    button_y + button_radius
                ),
                fill=color
            )

    if options.get("show_title", False):
        title = str(options.get("window_title", "Untitled"))[:100]
        title_font = _load_font(13 * SCALE)
        title_width = window_draw.textbbox((0, 0), title, font=title_font)[2]
        window_draw.text(
            ((window_width - title_width) // 2, 15 * SCALE),
            title,
            fill=(220, 220, 220, 210),
            font=title_font,
        )

    # -----------------------------------------------------
    # CODE CONTENT
    # -----------------------------------------------------

    window.alpha_composite(
        code_area,
        (
            pad_x * SCALE,
            header_height * SCALE
        )
    )

    # -----------------------------------------------------
    # SUBTLE BORDER
    # -----------------------------------------------------

    window_draw.rounded_rectangle(
        (
            0,
            0,
            window_width - 1,
            window_height - 1
        ),
        radius=corner_radius,
        outline=(
            255,
            255,
            255,
            16
        ),
        width=1 * SCALE
    )

    # -----------------------------------------------------
    # ADD WINDOW TO CANVAS
    # -----------------------------------------------------

    canvas.alpha_composite(
        window,
        (
            window_x,
            window_y
        )
    )

    # -----------------------------------------------------
    # WATERMARK
    # -----------------------------------------------------

    if watermark and watermark_text:

        watermark_font = _load_font(
            15 * SCALE
        )

        canvas_draw = ImageDraw.Draw(
            canvas
        )

        bbox = canvas_draw.textbbox(
            (0, 0),
            watermark_text,
            font=watermark_font
        )

        text_width = (
            bbox[2]
            - bbox[0]
        )

        text_height = (
            bbox[3]
            - bbox[1]
        )

        canvas_draw.text(
            (
                canvas_width
                - text_width
                - 30 * SCALE,

                canvas_height
                - text_height
                - 22 * SCALE
            ),
            watermark_text,
            fill=(
                255,
                255,
                255,
                120
            ),
            font=watermark_font
        )

    # -----------------------------------------------------
    # DOWN-SAMPLE 4× → 1×
    #
    # This is what makes:
    # - Mac buttons smooth
    # - text smoother
    # - line numbers smoother
    # - rounded corners cleaner
    # -----------------------------------------------------

    final_width = canvas_width // SCALE
    final_height = canvas_height // SCALE

    canvas = canvas.resize(
        (
            final_width,
            final_height
        ),
        Image.Resampling.LANCZOS
    )

    # -----------------------------------------------------
    # EXPORT PNG
    # -----------------------------------------------------

    output = io.BytesIO()

    canvas.convert(
        "RGB"
    ).save(
        output,
        format="PNG",
        optimize=True
    )

    output.seek(0)

    return output