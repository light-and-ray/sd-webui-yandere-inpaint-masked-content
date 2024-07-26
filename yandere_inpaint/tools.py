import numpy as np
import cv2
from PIL import Image, ImageChops
from modules import shared, errors, masking
from modules.processing import apply_overlay


def crop(image: Image.Image, origMask: Image.Image, padding: int):
    crop_region = masking.get_crop_region(origMask, padding)
    crop_region = masking.expand_crop_region(crop_region, 1, 1, origMask.width, origMask.height)
    return image.crop(crop_region)

def uncrop(image: Image.Image, origImage: Image.Image, origMask: Image.Image, padding: int):
    crop_region = masking.get_crop_region(origMask, padding)
    crop_region = masking.expand_crop_region(crop_region, 1, 1, origMask.width, origMask.height)
    x1, y1, x2, y2 = crop_region
    paste_to = (x1, y1, x2-x1, y2-y1)
    image_masked = Image.new('RGBa', (origImage.width, origImage.height))
    image_masked.paste(origImage.convert("RGBA").convert("RGBa"), mask=ImageChops.invert(origMask))
    overlay_image = image_masked.convert('RGBA')
    return apply_overlay(image.convert("RGB"), paste_to, overlay_image)[0].convert("RGBA")



def areImagesTheSame(image_one, image_two):
    if image_one.size != image_two.size:
        return False

    diff = ImageChops.difference(image_one.convert('RGB'), image_two.convert('RGB'))

    if diff.getbbox():
        return False
    else:
        return True



def limitSizeByMinDimension(image: Image.Image, size):
    w, h = image.size
    k = size / min(w, h)
    newW = w * k
    newH = h * k

    return int(newW), int(newH)



def applyMaskBlur(image_mask, mask_blur):
    originalMode = image_mask.mode
    if mask_blur > 0:
        np_mask = np.array(image_mask).astype(np.uint8)
        kernel_size = 2 * int(2.5 * mask_blur + 0.5) + 1
        np_mask = cv2.GaussianBlur(np_mask, (kernel_size, kernel_size), mask_blur)
        image_mask = Image.fromarray(np_mask).convert(originalMode)
    return image_mask
