from PIL import Image, ImageChops
import copy
from typing import Any
from dataclasses import dataclass
from modules import shared, masking
from modules.processing import apply_overlay
from yandere_inpaint.options import getYandereInpaintUpscaler, getYandereInpaintTileSize


def areImagesTheSame(image_one, image_two):
    if image_one.size != image_two.size:
        return False

    diff = ImageChops.difference(image_one.convert('RGB'), image_two.convert('RGB'))

    if diff.getbbox():
        return False
    else:
        return True


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
    return apply_overlay(image, paste_to, overlay_image)[0]


def processUpscaler(im):
    upscaler_name = getYandereInpaintUpscaler()
    upscalers = [x for x in shared.sd_upscalers if x.name == upscaler_name]
    if len(upscalers) == 0:
        raise Exception(f"Can't find yandrere inpainting model '{upscaler_name}'. See installation guide")
    else:
        upscaler = upscalers[0]

    old_ESRGAN_tile = shared.opts.ESRGAN_tile
    try:
        shared.opts.ESRGAN_tile = min(getYandereInpaintTileSize(), max(*im.size))
        im = upscaler.scaler.upscale(im, 1, upscaler.data_path)
    finally:
        shared.opts.ESRGAN_tile = old_ESRGAN_tile
    return im



@dataclass
class CacheData:
    image: Any
    mask: Any
    invert: Any
    padding: Any
    result: Any

cachedData = None



def yandereInpaint(image: Image.Image, mask: Image.Image, invert: int, padding: int):
    global cachedData
    result = None
    if cachedData is not None and\
            cachedData.invert == invert and\
            cachedData.padding == padding and\
            areImagesTheSame(cachedData.image, image) and\
            areImagesTheSame(cachedData.mask, mask):
        result = copy.copy(cachedData.result)
        print("yandere inpainted restored from cache")
        shared.state.assign_current_image(result)
    else:
        initMask = mask
        initMaskMaybeInverted = mask
        initImage = image
        if invert:
            mask = ImageChops.invert(mask)
            initMaskMaybeInverted = mask
        mask = mask.convert('1').resize(image.size)
        if padding is not None:
            mask = crop(mask, initMaskMaybeInverted, padding)
            image = crop(image, initMaskMaybeInverted, padding)
        greenFilling = Image.new('RGB', image.size, (0, 255, 0))
        maskedImage = copy.copy(image)
        maskedImage.paste(greenFilling, mask)
        shared.state.textinfo = "yandere inpainting"
        shared.state.assign_current_image(maskedImage)
        result = processUpscaler(maskedImage.convert('RGB')).convert('RGBA')
        shared.state.textinfo = ""
        shared.state.assign_current_image(result)
        if shared.state.interrupted:
            return initImage
        if padding is not None:
            result = uncrop(result, initImage, initMaskMaybeInverted, padding)
        cachedData = CacheData(copy.copy(initImage), copy.copy(initMask), invert, padding, copy.copy(result))
        print("yandere inpainted cached")

    return result
