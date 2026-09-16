import io
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import ImageFormatter
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageFilter


def create_code_image(code, lang, theme, line_numbers, font_name, mac_buttons, bg_gradient, padding, watermark, watermark_text):

    try:
        lexer = get_lexer_by_name(lang)
    except Exception:
        lexer = guess_lexer(code)

    try:
        if font_name:
            ImageFont.truetype(font_name, 24)
    except Exception:
        font_name = None

    formatter_kwargs = {
        'style': theme,
        'line_numbers': line_numbers,
        'font_size': 24,
        'line_pad': 12,
    }
    if font_name:
        formatter_kwargs['font_name'] = font_name

    formatter = ImageFormatter(**formatter_kwargs)
    code_img_data = highlight(code, lexer, formatter)
    code_img = Image.open(io.BytesIO(code_img_data)).convert('RGBA')

    style_bg = getattr(formatter.style, 'background_color', '#0b1020')
    try:
        bg_rgb = ImageColor.getrgb(style_bg)
    except Exception:
        bg_rgb = (15, 23, 42)

    bg_base = (13, 19, 31)
    bg_accent = (22, 34, 52)
    if bg_gradient:
        bg_base = (14, 27, 39)
        bg_accent = (20, 40, 52)

    header_height = 58
    radius = 26
    inner_padding = 26
    shadow_offset = 18
    margin = 80

    win_w = code_img.width + (padding * 2) + (inner_padding * 2)
    win_h = code_img.height + header_height + padding + (inner_padding * 2)
    canvas_w = win_w + (margin * 2)
    canvas_h = win_h + (margin * 2)

    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(canvas)

    if bg_gradient:
        for y in range(canvas_h):
            ratio = y / max(1, canvas_h - 1)
            r = int(bg_base[0] * (1 - ratio) + bg_accent[0] * ratio)
            g = int(bg_base[1] * (1 - ratio) + bg_accent[1] * ratio)
            b = int(bg_base[2] * (1 - ratio) + bg_accent[2] * ratio)
            c_draw.line((0, y, canvas_w, y), fill=(r, g, b, 255))

        glow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse((40, 30, canvas_w - 60, canvas_h - 80), fill=(90, 140, 255, 48))
        glow_draw.ellipse((canvas_w // 2 - 220, -80, canvas_w // 2 + 220, 260), fill=(35, 211, 173, 34))
        canvas = Image.alpha_composite(canvas, glow)

    else:
        c_draw.rectangle((0, 0, canvas_w, canvas_h), fill=(11, 17, 28, 255))

    for x in range(0, canvas_w, 24):
        for y in range(0, canvas_h, 24):
            alpha = 20 if ((x // 24 + y // 24) % 2 == 0) else 12
            c_draw.ellipse((x, y, x + 2, y + 2), fill=(255, 255, 255, alpha))

    shadow = Image.new('RGBA', (win_w, win_h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle((0, 0, win_w, win_h), radius=radius, fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))

    pos_x = (canvas_w - win_w) // 2
    pos_y = (canvas_h - win_h) // 2
    canvas.paste((0, 0, 0, 0), (pos_x + shadow_offset, pos_y + shadow_offset, pos_x + win_w + shadow_offset, pos_y + win_h + shadow_offset), shadow)

    window = Image.new('RGBA', (win_w, win_h), (0, 0, 0, 0))
    w_draw = ImageDraw.Draw(window)
    w_draw.rounded_rectangle((0, 0, win_w, win_h), radius=radius, fill=(bg_rgb[0], bg_rgb[1], bg_rgb[2], 255))

    border = Image.new('RGBA', (win_w, win_h), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    border_draw.rounded_rectangle((0, 0, win_w, win_h), radius=radius, outline=(255, 255, 255, 28), width=2)
    window = Image.alpha_composite(window, border)

    if mac_buttons:
        btn_y = 20
        buttons = [
            ('#FF5F57', 22),
            ('#FFBD2E', 44),
            ('#28C840', 66),
        ]
        for color, x in buttons:
            w_draw.ellipse((x, btn_y, x + 12, btn_y + 12), fill=color)

        try:
            title_font = ImageFont.truetype('arial.ttf', 13)
        except Exception:
            title_font = ImageFont.load_default()

        title_text = 'CodeShot'
        title_w = title_font.getbbox(title_text)[2]
        w_draw.text(((win_w - title_w) / 2, 18), title_text, font=title_font, fill=(200, 216, 228, 180))

    content_x = inner_padding
    content_y = header_height + padding // 2
    window.paste(code_img, (content_x, content_y), code_img)

    canvas.paste(window, (pos_x, pos_y), window)

    if watermark and watermark_text:
        try:
            wm_font = ImageFont.truetype('arial.ttf', 20)
        except Exception:
            wm_font = ImageFont.load_default()

        bbox = c_draw.textbbox((0, 0), watermark_text, font=wm_font)
        text_w = bbox[2] - bbox[0]
        c_draw.text((canvas_w - text_w - 36, canvas_h - 42), watermark_text, fill=(255, 255, 255, 90), font=wm_font)

    rgb_canvas = Image.new('RGB', canvas.size, (0, 0, 0))
    rgb_canvas.paste(canvas, mask=canvas.split()[-1])

    output = io.BytesIO()
    rgb_canvas.save(output, format='PNG')
    output.seek(0)

    return output