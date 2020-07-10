#!/usr/bin/env python3

import glob
import json
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EXCLUDE_TAGS = {
    "repost",
    "regrann",
    "ultimatefrisbeebingo",
    "AirborneTeam",
    "cyclingmanalitoleh",
}
INCLUDE_IMAGES = ("23101181_155043781769865_1657988909629440000_n.jpg",)

CHRONO = 1
REVERSE_CHRONO = 2
RANDOM = 3


def get_images(order=CHRONO):
    images = glob.glob("content/*.jpg")
    with open("content/tiks_ultimate.json") as f:
        data = json.load(f)
    image_names = [
        url.split("?")[0].split("/")[-1]
        for image in data["GraphImages"]
        for url in image["urls"]
        if url.split("?")[0].endswith(INCLUDE_IMAGES)
        or not EXCLUDE_TAGS.intersection([tag.lower() for tag in image.get("tags", [])])
    ]
    ordered_images = [
        f"content/{image}" for image in image_names if image.endswith(".jpg")
    ]
    # FIXME: Get images from videos
    if order == CHRONO:
        ordered_images.reverse()
    elif order == REVERSE_CHRONO:
        pass
    else:
        random.shuffle(ordered_images)
    return ordered_images


def draw_text(width, height):
    txt = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 2000)
    d = ImageDraw.Draw(txt)
    d.text((width * 0.3, 10), "1\n0\n0", font=fnt, fill=(0, 0, 0, 255))
    return txt


def create_collage(base_image, images, pixel_size):
    # Adapted from https://stackoverflow.com/a/35460517
    w, h = base_image.size
    cols, rows = int(w / pixel_size), int(h / pixel_size)
    size = (pixel_size, pixel_size)
    ims = []
    for p in images:
        im = Image.open(p)
        im = get_thumbnail(im, size)
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
    cols = 9
    rows = 16
    thumbnail_width = width // cols
    thumbnail_height = height // rows
    assert thumbnail_height == thumbnail_width
    return thumbnail_width


def get_thumbnail(image, size):
    w, h = image.size
    if abs(w - h) > 1:
        left, right, upper, lower = 0, w, 0, h
        crop = min(w, h)
        if w > crop:
            delta = int((w - crop) / 2)
            left, right = delta, w - delta
        else:
            delta = int((h - crop) / 2)
            upper, lower = delta, h - delta
        image = image.crop((left, upper, right, lower))

    image.thumbnail(size)
    return image


if __name__ == "__main__":
    w, h = 2880, 5120
    images = get_images(CHRONO)
    print(len(images))
    pixel_size = get_thumbnail_size(images, w, h)
    text = draw_text(w, h)
    collage = pixelate(text, pixel_size)
    create_collage(collage, images, pixel_size)
    collage.save("collage.png")
