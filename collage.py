#!/usr/bin/env python3

import glob
from math import sqrt
import json


from PIL import Image, ImageDraw, ImageFont


def get_images():
    images = glob.glob("content/*.jpg")
    with open("content/tiks_ultimate.json") as f:
        data = json.load(f)
    image_names = [
        url.split("?")[0].split("/")[-1]
        for image in data["GraphImages"]
        for url in image["urls"]
    ]
    ordered_images = [f"content/{image}" for image in image_names]
    # FIXME: Get images from videos
    return sorted(images, key=lambda x: ordered_images.index(x), reverse=True)


def draw_text(width, height):
    # make a blank image for the text, initialized to transparent text color
    txt = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 2000)

    d = ImageDraw.Draw(txt)
    d.text((width / 5, 10), "1\n0\n0", font=fnt, fill=(0, 0, 0, 255))
    return txt


def create_collage(width, height, images):
    # Adapted from https://stackoverflow.com/a/35460517
    n = len(images)
    k = sqrt((width * height) / n)
    cols = int(n / height * k) + 1
    rows = int(n / width * k) + 1
    thumbnail_width = width // cols
    thumbnail_height = height // rows
    size = thumbnail_width, thumbnail_height
    new_im = Image.new("RGB", (width, height))
    ims = []
    for p in images:
        im = Image.open(p)
        im.thumbnail(size)
        ims.append(im)
    i = 0
    x = 0
    y = 0
    for col in range(cols):
        for row in range(rows):
            if i >= n:
                break
            new_im.paste(ims[i], (x, y))
            i += 1
            y += thumbnail_height
        x += thumbnail_width
        y = 0
    new_im = new_im.convert("RGBA")
    return new_im


if __name__ == "__main__":
    images = get_images()
    w, h = 2880, 5120
    collage = create_collage(w, h, images)
    text = draw_text(w, h)
    out = Image.alpha_composite(collage, text)
    out.save("collage.png")
