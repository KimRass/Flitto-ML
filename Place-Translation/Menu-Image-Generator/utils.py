import re
import pyphen
from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
from copy import deepcopy
import torch
import torchvision.transforms as T
from torchvision.utils import make_grid
from pathlib import Path
import numpy as np
import cv2
from tqdm import tqdm

import config

ML_FONT_PATH = "/Users/jongbeomkim/Desktop/workspace/menu_image_generator/fonts/Pretendard-Medium.otf"
ML_BOLD_FONT_PATH = "/Users/jongbeomkim/Desktop/workspace/menu_image_generator/fonts/Pretendard-Bold.otf"
JA_FONT_PATH = "/Users/jongbeomkim/Desktop/workspace/menu_image_generator/fonts/PretendardJP-Bold.otf"
ZH_FONT_PATH = "/Users/jongbeomkim/Desktop/workspace/menu_image_generator/fonts/NotoSansSC-Bold.otf"


def _get_font(lang, font_size, bold=False):
    if lang in ["ko", "en"]:
        if bold:
            font_path = ML_BOLD_FONT_PATH
        else:
            font_path = ML_FONT_PATH
    if lang in ["ja"]:
        font_path = JA_FONT_PATH
    elif lang in ["zh-CN", "zh-TW"]:
        font_path = ZH_FONT_PATH
    font = ImageFont.truetype(font=font_path, size=round(font_size))
    return font


def preprocess_text(text):
    new_text = re.sub(
        pattern=r"""(\s([?,.!"]))|(?<=\[|\(|\<)(.*?)(?=\)|\]|\>)""",
        repl=lambda x: x.group().strip(),
        string=text
    )
    new_text = re.sub(pattern=" *\u00b7 *", repl="\u00b7", string=new_text)
    new_text = re.sub(pattern=r"[·]", repl="・", string=new_text)
    return new_text


def _hyphenate_only_in_middle(word):
    pyphen.language_fallback("en")
    dic = pyphen.Pyphen(lang="en")

    positions = sorted(list(set(dic.positions(word) + [i + 1 for i, c in enumerate(word) if c == "-"])))
    positions = [i for i in positions if i > 2 and i < len(word) - 2]
    if not positions:
        return [word]
    positions = [0] + positions + [len(word)]
    subwords = [word[i: j] if j == len(word) else word[i: j] + "ᴥ" for i, j in zip(positions, positions[1:])]
    subwords = [s.strip() for s in subwords]
    return subwords


def _get_chars_cannot_be_parsed(text):
    not_permit = r"([0-9"
    for char in text:
        try:
            config.JA_PARSER.parse(char, language="ja")
        except Exception:
            not_permit += rf"""{char}"""
    not_permit += r"]+)"
    return not_permit


def _split_by_subword(text, lang, word_level=True, hyphenate=False):
    if lang in config.SCRIPTIO_DISCRETA:
        text = text.replace("・", "・ ")
        if not hyphenate:
            return text.split()
        else:
            text
            [_hyphenate_only_in_middle(word) for word in text.split()]
            return sum([_hyphenate_only_in_middle(word) for word in text.split()], [])
    else:
        if lang == "ja":
            if word_level:
                stack = list()
                not_permit = _get_chars_cannot_be_parsed(text)
                for subtext in re.split(pattern=not_permit, string=text):
                    for subtext2 in re.split(pattern=rf"({config.MUST_PARSED})", string=subtext):
                        try:
                            parsed = config.JA_PARSER.parse(subtext2, language="ja")
                            for chunk in parsed["chunks"]:
                                stack.append(chunk.word)
                                # print(chunk.word)
                        except Exception:
                            stack.append(subtext2)

                new_stack = [""]
                for subtext in stack:
                    popped = new_stack.pop()
                    if popped in list(config.JA_NOT_PERMIT_END) or subtext in list(config.JA_NOT_PERMIT_START):
                        new_stack.append(popped + subtext)
                    else:
                        new_stack.append(popped)
                        new_stack.append(subtext)
                return new_stack[1:]
            else:
                stack = [""]
                for i in range(len(text)):
                    popped = stack.pop()

                    if popped in list(config.JA_NOT_PERMIT_END) or text[i] in list(config.JA_NOT_PERMIT_START):
                        stack.append(popped + text[i])
                    else:
                        stack.append(popped)
                        stack.append(text[i])
                return stack[1:]
        elif lang[: 2] == "zh":
            if lang == "zh-CN":
                parser = config.ZHCN_PARSER
                not_permit_end = config.ZHCN_NOT_PERMIT_END
                not_permit_start = config.ZHCN_NOT_PERMIT_START
            elif lang == "zh-TW":
                parser = config.ZHTW_PARSER
                not_permit_end = config.ZHTW_NOT_PERMIT_END
                not_permit_start = config.ZHTW_NOT_PERMIT_START

            splitted = re.split(pattern=f"""({config.LANG_REGEX[lang]})""", string=text)
            if word_level:
                stack = list()
                for subtext in splitted:
                    if not subtext:
                        continue
                    parsed = parser.parse(subtext)
                    stack.extend(parsed)
            else:
                stack = list()
                for subtext in splitted:
                    if not subtext:
                        continue
                    if re.search(pattern=config.LANG_REGEX[lang], string=subtext):
                        stack.extend(list(subtext))
                    else:
                        stack.append(subtext)

            new_stack = [""]
            for subtext in stack:
                popped = new_stack.pop()
                if popped in list(not_permit_end) or subtext in list(not_permit_start):
                    new_stack.append(popped + subtext)
                else:
                    new_stack.append(popped)
                    new_stack.append(subtext)
            return new_stack[1:]


def _apply_word_wrap(text, lang, lim, word_level=True, hyphenate=False):
    new_text = ""
    if lang in config.SCRIPTIO_DISCRETA:
        for subtext in _split_by_subword(text, lang=lang, word_level=word_level, hyphenate=hyphenate):
            if len(subtext) > lim:
                return ""

            if new_text != "" and new_text[-1] != "ᴥ":
                new_text += " "
            new_text += subtext
            if len(new_text.replace("ᴥ", "").rsplit("\n", 1)[-1]) > lim:
                new_text = new_text[: -len(subtext)]
                new_text += "\n"
                new_text += subtext
        new_text = new_text.replace("-ᴥ\n", "-\n").replace("ᴥ\n", "-\n").replace("ᴥ", "").replace(" \n", "\n")
    else:
        for subtext in _split_by_subword(text, lang=lang, word_level=word_level, hyphenate=hyphenate):
            if len(subtext) > lim:
                return ""

            if len(new_text.rsplit("\n", 1)[-1] + subtext) > lim:
                new_text += "\n"
            new_text += subtext
    if new_text[-1] == "\n":
        new_text = new_text[: -1]
    return new_text


def _get_maximum_line_length(text):
    splitted = text.split("\n")
    max_len = max(map(len, splitted))
    return max_len


def get_line_break_variants(text, lang, n_lines_thresh=4, word_level=True, hyphenate=False):
    if lang in ["ko", "ja", "zh-CN", "zh-TW"]:
        hyphenate = False

    max_len = _get_maximum_line_length(text)
    variants = list()
    for lim in range(max_len + 1):
        wrapped = _apply_word_wrap(text, lim=lim, lang=lang, word_level=word_level, hyphenate=hyphenate)
        if wrapped in variants or wrapped.count("\n") > n_lines_thresh or not wrapped:
            continue
        variants.append(wrapped)
    variants.reverse()
    return variants


def _get_singleline_textbox_coordinates(text, x, y, font_size, lang):
    draw = ImageDraw.Draw(Image.new(mode="L", size=(0, 0)))
    tbox_x1, tbox_y1, tbox_x2, tbox_y2 = draw.textbbox(
        xy=(x, y),
        text=text,
        align="left",
        direction="ltr",
        anchor="lt",
        font=_get_font(lang=lang, font_size=font_size),
    )
    # if text_alignment in ["top", "middle", "bottom"]:
    #     ori_tbox_x1 = deepcopy(tbox_x1)
    #     ori_tbox_x2 = deepcopy(tbox_x2)

    #     tbox_x1 = tbox_x1 - (tbox_y2 - tbox_y1)
    #     tbox_x2 = ori_tbox_x1
    #     tbox_y2 = tbox_y1 + (ori_tbox_x2 - ori_tbox_x1)
    return tbox_x1, tbox_y1, tbox_x2, tbox_y2


def get_w_and_h(img):
    if img.ndim == 2:
        h, w = img.shape
    else:
        h, w, _ = img.shape
    return w, h


def _resize_image(img, w, h):
    ori_w, ori_h = get_w_and_h(img)
    if w < ori_w or h < ori_h:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_LANCZOS4
    resized_img = cv2.resize(src=img, dsize=(w, h), interpolation=interpolation)
    return resized_img


if __name__ == "__main__":
    # text = "2人前御膳"
    text = "8．済州海鮮の鍋・済州焼き太刀魚御膳"
    print(_split_by_subword(text=text, lang="ja"))
    # text = preprocess_text(text)
    # # lang="zh-CN"
    # lang="zh-TW"
    # word_level=True
    # hyphenate=True
    # # print(_split_by_subword(text=text, lang=lang, word_level=word_level, hyphenate=hyphenate))
    # pprint(get_line_break_variants(
    #     text, lang=lang, n_lines_thresh=4, word_level=word_level, hyphenate=hyphenate)
    # )
