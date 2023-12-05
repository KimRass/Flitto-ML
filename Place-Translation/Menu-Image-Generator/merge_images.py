from PIL import Image, ImageOps
from pathlib import Path
from tqdm import tqdm
import numpy as np
import argparse


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--save_dir", type=str, required=True)

    args = parser.parse_args()
    return args


def get_bg_color(image):
    img = np.array(image).astype("float")
    img[1: -1, 1: -1, :] = np.nan
    mean = np.nanmean(img)
    if mean >= 127.5:
        bg_color = (0, 0, 0)
    else:
        bg_color = (255, 255, 255)
    return bg_color


def merge_images(img_paths, pad=5):
    ws = list()
    hs = list()
    for img_path in img_paths:
        image = Image.open(img_path)
        w, h = image.size
        ws.append(w)
        hs.append(h)
    max_w = max(ws)
    max_h = max(hs)

    bg_color = get_bg_color(image)
    merged = Image.new(mode="RGB", size=(max_w * 2 + pad * 3, max_h + pad * 2), color=bg_color)
    for idx, img_path in enumerate(img_paths):
        image = Image.open(img_path)
        w, h = image.size
        new_image = T.Pad(
            ((max_w - w) // 2, (max_h - h) // 2, (max_w - w) - (max_w - w) // 2, (max_h - h) - (max_h - h) // 2)
        )(image)
        merged.paste(new_image, (pad + (idx % 2) * (max_w + pad), pad + (idx // 2) * (max_h + pad)))
    return merged


def merge_images2(image1, image2, pad=5):
    w1, h1 = image1.size
    w2, h2 = image2.size
    max_h = max(h1, h2)

    resized_image1 = image1.resize(size=(round(w1 * max_h / h1), max_h), resample=Image.LANCZOS)
    resized_image2 = image2.resize(size=(round(w2 * max_h / h2), max_h), resample=Image.LANCZOS)
    w1, _ = resized_image1.size
    w2, _ = resized_image2.size

    bg_color = get_bg_color(image1)
    merged = Image.new(mode="RGB", size=((w1 + w2) + pad * 3, max_h + pad * 2), color=bg_color)
    merged.paste(resized_image1, (pad, pad))
    merged.paste(resized_image2, (pad + w1 + pad, pad))
    return merged


if __name__ == "__main__":
    args = get_args()

    for subdir in tqdm(list(Path(args.data_dir).glob("**/"))):
        img_paths = sorted(
            [
                img_path
                for img_path
                in subdir.glob("*")
                if "item-" in img_path.name and img_path.suffix in [".jpg", ".jpeg"]
            ]
        )
        for idx in range(0, len(img_paths), 2):
            trg = img_paths[idx: idx + 2]
            image1 = Image.open(trg[0]).convert("RGB")
            image1 = ImageOps.exif_transpose(image1)
            if len(trg) == 2:
                image2 = Image.open(trg[1]).convert("RGB")
                image2 = ImageOps.exif_transpose(image2)
                merged = merge_images2(image1, image2, pad=10)
            else:
                merged = image1
            save_path = Path(args.save_dir)/f"{subdir.name}/{str(idx // 2 + 1)}.jpg"
            save_path.parent.mkdir(exist_ok=True, parents=True)
            merged.save(save_path)
