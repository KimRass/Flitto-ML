import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from skimage.filters import unsharp_mask


def load_image(img_path):
    img_path = str(img_path)
    img = cv2.imread(img_path, flags=cv2.IMREAD_COLOR)
    img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2RGB)
    return img


def _to_pil(img):
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)
    return img


def show_image(img):
    copied_img = img.copy()
    copied_img = _to_pil(copied_img)
    copied_img.show()


def save_image(img, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    _to_pil(img).save(str(path), quality=100, subsampling=0)


def _to_2d(img):
    if img.ndim == 3:
        return img[:, :, 0]
    else:
        return img


def _to_array(img):
    img = np.array(img)
    return img


def _invert_image(img):
    return cv2.bitwise_not(img.astype("uint8"))


def _get_width_and_height(img):
    if img.ndim == 2:
        h, w = img.shape
    else:
        h, w, _ = img.shape
    return w, h


def _resize_image(img, w, h):
    ori_w, ori_h = _get_width_and_height(img)
    if w < ori_w or h < ori_h:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_LANCZOS4
    resized_img = cv2.resize(src=img, dsize=(w, h), interpolation=interpolation)
    return resized_img


def _resize_image_using_shorter_side(img, side_length=1530):
    ori_w, ori_h = _get_width_and_height(img)
    shorter = min(ori_w, ori_h)
    if shorter <= side_length:
        return img
    if ori_w < ori_h:
        resized_img = cv2.resize(
            src=img, dsize=(side_length, round(ori_h * (side_length / ori_w))), interpolation=cv2.INTER_AREA,
        )
    else:
        resized_img = cv2.resize(
            src=img, dsize=(side_length, round(ori_h * (side_length / ori_w))), interpolation=cv2.INTER_AREA,
        )
    return resized_img


def _to_grayscale(img):
    gray_img = cv2.cvtColor(src=img, code=cv2.COLOR_RGB2GRAY)
    return gray_img


def _mask_image(img, mask, invert=False):
    img = _to_array(img)
    mask = _to_2d(_to_array(mask))
    if invert:
        mask = _invert_image(mask)
    return cv2.bitwise_and(src1=img, src2=img, mask=mask.astype("uint8"))


def _get_canvas_same_size_as_image(img, black=False):
    if black:
        return np.zeros_like(img).astype("uint8")
    else:
        return (np.ones_like(img) * 255).astype("uint8")

def _sharpen(img):
    out = unsharp_mask(img, radius=1, amount=1, channel_axis=2)
    out = (out * 255).astype("uint8")
    return out


def to_logo(img):
    img = _resize_image_using_shorter_side(img=img, side_length=60)
    canvas = (np.ones(shape=(60, 60, 3)) * 255).astype("uint8")
    w, h = _get_width_and_height(img)
    canvas[30 - h // 2: 30 + h // 2, 30 - w // 2: 30 + w // 2, :] = img
    return canvas


if __name__ == "__main__":
    img = load_image("/Users/jongbeomkim/Downloads/QR_20230905_1475_LM5WNLI8YM2EPU3QA33H.png")
    logo = to_logo(img)
    save_image(logo, path="/Users/jongbeomkim/Downloads/logo.png")