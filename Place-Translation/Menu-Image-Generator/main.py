import pandas as pd
import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

from utils import _get_font, _apply_word_wrap, _get_singleline_textbox_coordinates


def load_image(url_or_path):
    url_or_path = str(url_or_path)
    if "http" in url_or_path:
        img = cv2.imdecode(
            np.asarray(bytearray(requests.get(url_or_path).content), dtype="uint8"), flags=cv2.IMREAD_COLOR
        )
    else:
        img = cv2.imread(url_or_path, flags=cv2.IMREAD_COLOR)
    img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2RGB)
    return img


def _to_array(img):
    img = np.array(img)
    return img


def _to_pil(img):
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)
    return img


def _blend_two_images(img1, img2, alpha=0.5):
    img1 = _to_pil(img1)
    img2 = _to_pil(img2)
    img_blended = Image.blend(im1=img1, im2=img2, alpha=alpha)
    return _to_array(img_blended)


def show_image(img1, img2=None, alpha=0.5):
    img1 = _to_pil(img1)
    if img2 is None:
        img1.show()
    else:
        _to_pil(_blend_two_images(img1, img2, alpha=alpha)).show()
        # img2 = _to_pil(img2)
        # img_blended = Image.blend(im1=img1, im2=img2, alpha=alpha)
        # img_blended.show()


def save_image(img, save_path):
    _to_pil(img).save(save_path)


def _render_text(lang, canvas, x, y, text, text_color, font_size, align, anchor, bold):
    pil_canvas = _to_pil(canvas)
    draw = ImageDraw.Draw(pil_canvas)
    draw.text(
        xy=(x, y),
        text=text,
        fill=text_color,
        font=_get_font(lang=lang, font_size=font_size, bold=bold),
        stroke_width=0,
        stroke_fill=None,
        align=align,
        anchor=anchor,
        direction="ltr",
    )
    return _to_array(pil_canvas)


def generate_title_block(
    src_lang, w, h, title1, title1_y, title2, title2_y, text_color, title1_font_size, title2_font_size
):
    title_block = np.full(shape=(h, w, 3), dtype="uint8", fill_value=255)
    ### Render title1.
    title_block = _render_text(
        lang=src_lang,
        canvas=title_block,
        x=w // 2,
        y=title1_y,
        text=title1,
        text_color=text_color,
        font_size=title1_font_size,
        align="center",
        anchor="ms",
        bold=True,
    )
    ### Render title2.
    title_block = _render_text(
        lang=src_lang,
        canvas=title_block,
        x=w // 2,
        y=title2_y,
        text=title2,
        text_color=text_color,
        font_size=title2_font_size,
        align="center",
        anchor="ms",
        bold=True,
    )
    return title_block


def generate_text_block(
    dst_lang,
    w,
    h,
    text,
    text_y,
    text_color,
    text_font_size,
    desc,
    desc_y,
    desc_color,
    desc_font_size,
    price,
    price_y,
    price_color,
    price_font_size,
    line_color,
):
    text_block = np.full(shape=(h, w, 3), dtype="uint8", fill_value=255)
    ### Text
    text_block = _render_text(
        lang=dst_lang,
        canvas=text_block,
        x=70,
        y=text_y,
        text=text,
        text_color=text_color,
        font_size=text_font_size,
        align="left",
        anchor="ls",
        bold=True,
    )
    l, t, r, b = _get_singleline_textbox_coordinates(
        text=text, x=70, y=text_y, font_size=text_font_size, lang=dst_lang,
    )
    # print(l, t, r, b)
    ### Description
    wrapped_desc = _apply_word_wrap(desc, lim=80, lang=dst_lang, word_level=True, hyphenate=True)
    text_block = _render_text(
        lang=dst_lang,
        canvas=text_block,
        x=70,
        y=desc_y,
        text=wrapped_desc,
        text_color=desc_color,
        font_size=desc_font_size,
        align="left",
        anchor="ls",
        bold=False,
    )
    ### Price
    price_y = price_y if desc else desc_y
    text_block = _render_text(
        lang=dst_lang,
        canvas=text_block,
        x=70,
        y=price_y,
        text=price,
        text_color=price_color,
        font_size=price_font_size,
        align="left",
        anchor="ls",
        bold=True,
    )
    cv2.line(
        text_block,
        pt1=(70, round(240 * 0.05)),
        pt2=(w - 70, round(240 * 0.05)),
        color=eval(line_color[3:]),
        thickness=1,
    )
    return text_block


def stack_blocks(block1, block2):
    return np.concatenate([block1, block2], axis=0)


def generate_menu_image(
    src_lang,
    dst_lang,
    w,
    title_block_h,
    title1,
    title1_y,
    title1_font_size,
    title2,
    title2_y,
    title2_font_size,
    text_block_h,
    texts,
    text_y,
    text_font_size,
    descs,
    desc_y,
    desc_font_size,
    prices,
    price_y,
    price_font_size,
    line_color,
    bg_img,
    ad,
):
    menu_img = np.full(shape=(0, w, 3), dtype="uint8", fill_value=255)
    title_block = generate_title_block(
        src_lang=src_lang,
        w=w,
        h=title_block_h,
        title1=title1,
        title1_y=title1_y,
        title2=title2,
        title2_y=title2_y,
        text_color=color1,
        title1_font_size=title1_font_size,
        title2_font_size=title2_font_size,
    )
    # menu_img = stack_blocks(block1=menu_img, block2=title_block)
    text_block = np.full(shape=(0, w, 3), dtype="uint8", fill_value=255)
    for text, price, desc in zip(texts, prices, descs):
        text_block_module = generate_text_block(
            dst_lang=dst_lang,
            w=w,
            h=text_block_h,
            text=text,
            desc=desc,
            price=price,
            text_y=text_y,
            desc_y=desc_y,
            price_y=price_y,
            text_color=color1,
            desc_color=color2,
            price_color=color1,
            text_font_size=text_font_size,
            desc_font_size=desc_font_size,
            price_font_size=price_font_size,
            line_color=line_color,
        )
        text_block = stack_blocks(block1=text_block, block2=text_block_module)
    h, w, _ = text_block.shape
    text_block = _blend_two_images(text_block, bg_img[: h, : w, :], alpha=0.1)

    menu_img = stack_blocks(block1=menu_img, block2=title_block)
    menu_img = stack_blocks(block1=menu_img, block2=text_block)
    menu_img = stack_blocks(block1=menu_img, block2=ad)
    return menu_img


bg_img = load_image("/Users/jongbeomkim/Desktop/workspace/menu_image_generator/정관장_대표_이미지.jpg")

xlsx_path = "/Users/jongbeomkim/Downloads/place_1658_image_6368_20230921_152133901.xlsx"
src_lang = "ko"
dst_lang = "en"
# for dst_lang in ["en", "ja", "zh-CN"]:
df = pd.read_excel(xlsx_path)
# df.columns.tolist()
if dst_lang == "en":
    col = "17_English(English)"
elif dst_lang == "ja":
    col = "30_Japanese(日本語)"
elif dst_lang == "zh-CN":
    col = "11_Chinese (Simplified)(中文(简体))"
# elif dst_lang == "zh-TW":
bg_color = "rgb(228, 228, 228)"
color1 = "rgb(26, 26, 26)"
color2 = "rgb(120, 120, 120)"
line_color = "rgb(230, 230, 230)"

w = 800
title_block_h = 240
title1 = "CHEONG KWAN JANG\n정관장"
title1_y = 90
title1_font_size = 48
title2 = "Main Menu"
title2_y = 210
title2_font_size = 26
text_block_h = 170
# texts = df[col].tolist()
texts = [
    "Red ginseng tablet 240g",
    "Hongsamjeong, EVERYTIME (10ml * 30 packets)",
    "Hongsamjeong EVERYTIME Limited (10ml * 30 packets)",
    "Red Ginseng Tea (3g * 100 packets)",
    "Cheonnokgang pills 12 pils (4g * 12 pils)",
]
text_y = 60
text_font_size = 24
# descs = df["12_Chinese (Traditional)(中文(繁體))"].tolist()
# descs = [""] * len(texts)
descs = [
    "The representative product of Cheong Kwan Jang, a 100% red ginseng extract containing various red ginseng active ingredients, made from 6-year-old red ginseng with 120 years of traditional know-how.",
    "A product that can be easily consumed anywhere, anytime, by simply adding purified water to 6-year-old red ginseng extract",
    "This is a product of concentrated Hongsamjeong limited, which contains 20% of high-quality ginseng, called jisam, from 6-year-old red ginseng.",
    "This product is suitable for everyone, as it preserves the rich and mild taste and aroma of red ginseng. It is also a good product for those who are new to red ginseng.",
    "This is a product in the form of a pill that is made with the know-how of Cheong Kwan Jang, a Korean ginseng company, using antlers, the source of strength, and green antlers (deer tails), the symbol of vitality.",
]
desc_y = 85
desc_font_size = 14
# prices = ["10,000", "12,000", "10,500", "13,000", "10,000", "2,000", "10,000", "2,000"]
prices = ["211,000", "102,000", "133,000", "29,000", "400,000"]
price_y = 150
price_font_size = 18
ad = load_image("/Users/jongbeomkim/Desktop/workspace/menu_image_generator/ad.png")
menu_img = generate_menu_image(
    src_lang=src_lang,
    dst_lang=dst_lang,
    w=w,
    title_block_h=title_block_h,
    title1=title1,
    title1_y=title1_y,
    title1_font_size=title1_font_size,
    title2=title2,
    title2_y=title2_y,
    title2_font_size=title2_font_size,
    text_block_h=text_block_h,
    texts=texts,
    text_y=text_y,
    text_font_size=text_font_size,
    descs=descs,
    desc_y=desc_y,
    desc_font_size=desc_font_size,
    prices=prices,
    price_y=price_y,
    price_font_size=price_font_size,
    line_color=line_color,
    bg_img=bg_img,
    ad=ad,
)
# show_image(menu_img)
# save_image(
#     menu_img,
#     # save_path=f"/Users/jongbeomkim/Desktop/workspace/menu_image_generator/sample_{src_lang}_{dst_lang}.png"
#     save_path=f"/Users/jongbeomkim/Desktop/workspace/menu_image_generator/정관장_{src_lang}_{dst_lang}_bg.png"
# )
