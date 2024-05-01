from PIL import Image, ImageChops, ImageDraw
from random import randint
import numpy as np

sprite_base = Image.open("res/spinda_base.png")
sprite_mask = Image.open("res/spinda_mask.png")
spot_masks = [
    Image.open("res/spots/spot_1.png"),
    Image.open("res/spots/spot_2.png"),
    Image.open("res/spots/spot_3.png"),
    Image.open("res/spots/spot_4.png")
]
spot_offsets = [
    (8, 6),
    (32, 7),
    (14, 24),
    (26, 25)
]

def empty_spinda():
    return [
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0)
    ]

def from_personality(pers):
    self = empty_spinda()
    self[0] = (pers & 0x0000000f, (pers & 0x000000f0) >> 4)
    self[1] = ((pers & 0x00000f00) >> 8, (pers & 0x0000f000) >> 12)
    self[2] = ((pers & 0x000f0000) >> 16, (pers & 0x00f00000) >> 20)
    self[3] = ((pers & 0x0f000000) >> 24, (pers & 0xf0000000) >> 28)
    return self

def random_spinda():
    return from_personality(randint(0, 0x100000000))

def get_personality(self):
    pers = 0x00000000
    for i, spot in enumerate(self):
        pers = pers | (spot[0] << i*8) | (spot[1] << i*8+4)
    return pers

def render_pattern(self, only_pattern = False, crop = False):
    # Prepare a result image with the same size as base and bg either black or transparent
    size = sprite_base.size
    img = Image.new('RGBA', size, (0, 0, 0, 255 if only_pattern else 0))

    # When wanting an actual spinda, start by pasting in the base sprite
    if not only_pattern:
        img.paste(sprite_base, (0, 0))

    for index in range(4):
        # Calculate the top-left coordinate for the spot image
        position = (spot_offsets[index][0] + self[index][0],
                    spot_offsets[index][1] + self[index][1])

        # Create a full-size image for the full spot at the desired position,
        #   as composite operation requires same-sized images
        spot_full = Image.new('RGBA', size, (0, 0, 0, 0))
        spot_full.paste(spot_masks[index], position, mask=spot_masks[index])

        # Create temporary mask by combining mask and spot mask
        temp_mask = Image.new('RGBA', size, (0, 0, 0, 0))
        temp_mask.paste(sprite_mask, (0, 0), mask=spot_full)

        if only_pattern:
            # Composite the white spot onto the masked area
            temp_mask = Image.composite(spot_full, temp_mask, temp_mask)

        # Composite the new mask with the current result
        img = Image.composite(temp_mask, img, temp_mask)

    if crop:
        img = img.crop((17, 15, 52, 48))

    return img

def get_difference(spinda, target):
    # Validate the mode will match the type used in the next step
    if target.mode != "RGB":
        target = target.convert("RGB")
    # Compare the resulting images by the total average pixel difference
    result = render_pattern(spinda, only_pattern=True, crop=True).convert("RGB")
    diff = ImageChops.difference(target, result)
    total_diff = 0
    for n, (r, g, b) in diff.getcolors():  # gives a list of counter and RGB values in the image
        total_diff += n*((r+g+b)/3)
    return total_diff

if __name__ == "__main__":
    spin = from_personality(0x7a397866)
    render_pattern(spin)
    #print(hex(get_personality(spin)))