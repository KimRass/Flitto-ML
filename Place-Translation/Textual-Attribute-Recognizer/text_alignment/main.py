import pandas as pd
from PIL import Image, ImageDraw
from torchvision.utils import make_grid
import torchvision.transforms.functional as TF
import torch
from pathlib import Path


def get_bboxes(txt_path):
    bboxes = list()
    with open(txt_path, mode="r") as f:
        for line in f:
            line = line.strip().replace("\ufeff", "")
            l, t, r, b, _, text_alignment = line.split("ᴥ")
            l = round(float(l.strip()))
            t = round(float(t.strip()))
            r = round(float(r.strip()))
            b = round(float(b.strip()))
            text_alignment = text_alignment.strip()
            bboxes.append((l, t, r, b, text_alignment))

    bboxes = pd.DataFrame(bboxes, columns=("l", "t", "r", "b", "text_alignment"))
    bboxes["area"] = bboxes.apply(
        lambda x: max(0, (x["r"] - x["l"]) * (x["b"] - x["t"])), axis=1,
    )
    bboxes = bboxes[bboxes["area"] > 0]
    return bboxes


cnt = 0
leng_sum = 0
data_dir = "/Users/jongbeomkim/Documents/datasets/menu_images"
for txt_path in Path(data_dir).glob("**/*.txt"):
    with open(txt_path, mode="r") as f:
        leng_sum += len(f.readlines())
        cnt += 1
leng_sum / cnt * 1000





image = Image.open("/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/text_alignment/125_257_original.jpg")
# image.show()
txt_path = "/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/text_alignment/125_257_label.txt"
bboxes = get_bboxes(txt_path)

colors = {"left": "rgb(150, 0, 0)", "center": "rgb(0, 150, 0)", "right": "rgb(0, 0, 150)"}
canvas = Image.new(mode="RGB", size=image.size, color="rgb(0, 0, 0)")
draw = ImageDraw.Draw(canvas)
for row in bboxes.itertuples():
    draw.rectangle(
        xy=(row.l, row.t, row.r, row.b),
        outline=colors[row.text_alignment],
        fill=colors[row.text_alignment],
        width=1,
    )
blended = Image.blend(image, canvas, alpha=0.6)
# blended.show()
blended.save("/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/resources/125_257_label.jpg")



image1 = Image.open("/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/text_alignment/125_257_original.jpg").convert("RGB")
image2 = Image.open("/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/text_alignment/125_257_as_is.png").convert("RGB")
image3 = Image.open("/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/text_alignment/125_257_to_be.png").convert("RGB")
w1, h1 = image1.size
w2, h2 = image2.size
w3, h3 = image3.size
w = min([w1, w2, w3])
h = min([h1, h2, h3])
image1 = image1.resize(size=(w, h))
image2 = image2.resize(size=(w, h))
image3 = image3.resize(size=(w, h))

image1 = TF.to_tensor(image1.resize(size=(w, h)))[None, :]
image2 = TF.to_tensor(image2.resize(size=(w, h)))[None, :]
image3 = TF.to_tensor(image3.resize(size=(w, h)))[None, :]
image = torch.cat([image1, image2, image3])
image = TF.to_pil_image(make_grid(image, pad_value=1, padding=10))
image.save("/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/text_alignment/resources/125_257_text_alignment.jpg")


ls = list()
for idx in range(10):
    img_path = f"/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/resources/character_background_{idx}.jpg"
    temp_image = Image.open(img_path)
    temp_image = TF.to_tensor(temp_image)[None, :]
    ls.append(temp_image)
image = torch.cat(ls)
image = TF.to_pil_image(make_grid(image, pad_value=1, padding=1, nrow=len(ls) // 2))
# image.show()
image.save("/Users/jongbeomkim/Desktop/workspace/Flitto-Image-Processing/Place-Translation/Textual-Attribute-Recognizer/resources/text_border.jpg")
