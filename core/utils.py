import io

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import ImageFormatter
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATH = Path(__file__).resolve().parent / "fonts" / "DejaVuSansMono.ttf"

# =========================================================
# HIGH RESOLUTION RENDERING
# =========================================================

SCALE = 4


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

    return palette.get(
        (theme_name or "dracula").lower(),
        palette["dracula"]
    )


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
    watermark_text
):

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

    formatter_kwargs = {
        "style": theme or "dracula",

        # We draw line numbers ourselves.
        "line_numbers": False,

        # 24px final → 96px rendering
        "font_size": 24 * SCALE,

        # 10px final → 40px rendering
        "line_pad": 10 * SCALE,
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
            20 * SCALE
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
        + 20 * SCALE
    )

    code_area_height = (
        code_img.height
        + 20 * SCALE
    )

    code_area = Image.new(
        "RGBA",
        (
            code_area_width,
            code_area_height
        ),
        _hex_to_rgb(code_background) + (255,)
    )

    code_draw = ImageDraw.Draw(
        code_area
    )

    # -----------------------------------------------------
    # MANUAL LINE NUMBERS
    # -----------------------------------------------------

    if line_numbers:

        # ImageFormatter spacing:
        # font_size + 2 × line_pad
        line_height = (
            (24 + 20)
            * SCALE
        )

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
                10 * SCALE
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
            10 * SCALE
        )
    )

    # -----------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------

    pad = max(
        28,
        int(padding or 28)
    )

    outer_margin = 48

    # Top space for Mac buttons
    header_height = 48

    window_width = (
        code_area.width
        + pad * 2 * SCALE
    )

    window_height = (
        code_area.height
        + header_height * SCALE
        + pad * SCALE
    )

    canvas_width = (
        window_width
        + outer_margin * 2 * SCALE
    )

    canvas_height = (
        window_height
        + outer_margin * 2 * SCALE
    )

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

    bg_draw = ImageDraw.Draw(
        background
    )

    start = _hex_to_rgb(
        outer_top
    )

    end = _hex_to_rgb(
        outer_background
    )

    for y in range(canvas_height):

        ratio = (
            y
            / max(
                canvas_height - 1,
                1
            )
        )

        r = int(
            start[0] * (1 - ratio)
            + end[0] * ratio
        )

        g = int(
            start[1] * (1 - ratio)
            + end[1] * ratio
        )

        b = int(
            start[2] * (1 - ratio)
            + end[2] * ratio
        )

        bg_draw.line(
            (
                0,
                y,
                canvas_width,
                y
            ),
            fill=(
                r,
                g,
                b,
                255
            )
        )

    # -----------------------------------------------------
    # OPTIONAL GLOW
    # -----------------------------------------------------

    if bg_gradient:

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

    shadow = Image.new(
        "RGBA",
        (
            window_width + 40 * SCALE,
            window_height + 40 * SCALE
        ),
        (0, 0, 0, 0)
    )

    shadow_draw = ImageDraw.Draw(
        shadow
    )

    shadow_draw.rounded_rectangle(
        (
            15 * SCALE,
            15 * SCALE,
            window_width + 15 * SCALE,
            window_height + 15 * SCALE
        ),
        radius=18 * SCALE,
        fill=(
            0,
            0,
            0,
            115
        )
    )

    shadow = shadow.filter(
        ImageFilter.GaussianBlur(
            15 * SCALE
        )
    )

    canvas.alpha_composite(
        shadow,
        (
            window_x - 20 * SCALE,
            window_y + 15 * SCALE
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

    window_draw.rounded_rectangle(
        (
            0,
            0,
            window_width - 1,
            window_height - 1
        ),
        radius=16 * SCALE,
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

    # -----------------------------------------------------
    # CODE CONTENT
    # -----------------------------------------------------

    window.alpha_composite(
        code_area,
        (
            pad * SCALE,
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
        radius=16 * SCALE,
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