#!/usr/bin/env python3

import glob
from math import sqrt
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


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
    txt = Image.new("RGBA", (width, height), (255, 255, 255, 0))

    fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 2000)

    d = ImageDraw.Draw(txt)
    d.text((width * 0.3, 10), "1\n0\n0", font=fnt, fill=(0, 0, 0, 255))
    return txt


def create_collage(base_image, images, pixel_size):
    # Adapted from https://stackoverflow.com/a/35460517
    w, h = base_image.size
    cols, rows = int(w / pixel_size), int(h / pixel_size)
    print(cols, rows)
    size = (pixel_size, pixel_size)
    ims = []
    for p in images:
        im = Image.open(p)
        im.thumbnail(size)
        ims.append(im)
    i = 0
    for col in range(cols):
        for row in range(rows):
            if i >= len(images):
                break
            position = (col * pixel_size, row * pixel_size)
            r, g, b = base_image.getpixel(position)[:3]
            if r == 0 and g == 0 and b == 0:
                continue
            base_image.paste(ims[i], position)
            i += 1
    base_image = base_image.convert("RGBA")
    return base_image


def pixelate(image, pixel_size):
    image = image.convert("1")
    w, h = image.size
    array = np.uint8(np.array(image) * 255)
    for i in range(int(h / pixel_size)):
        for j in range(int(w / pixel_size)):
            window = array[
                i * pixel_size : (i + 1) * pixel_size,
                j * pixel_size : (j + 1) * pixel_size,
            ]
            if window.sum() / 255 < pixel_size * pixel_size * 0.7:
                window[:, :] = 0
            else:
                window[:, :] = 255
    return Image.fromarray(array).convert("RGBA")


def get_thumbnail_size(images, width, height):
    n = len(images)
    k = sqrt((width * height) / n)
    cols = int(n / height * k) + 1
    rows = int(n / width * k) + 1
    thumbnail_width = width // cols
    thumbnail_height = height // rows
    assert thumbnail_height == thumbnail_width
    return thumbnail_width


if __name__ == "__main__":
    images = get_images()
    w, h = 2880, 5120
    pixel_size = get_thumbnail_size(images, w, h)
    text = draw_text(w, h)
    text = pixelate(text, pixel_size)
    collage = create_collage(text, images, pixel_size)
    # out = Image.alpha_composite(collage, text)
    out = text
    out.save("collage.png")
