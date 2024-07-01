from PIL import Image, ImageChops
import copy
from typing import Any
from dataclasses import dataclass
from modules import shared, errors
from yandere_inpaint.options import getYandereInpaintUpscaler, getYandereInpaintTileSize


def areImagesTheSame(image_one, image_two):
    if image_one.size != image_two.size:
        return False

    diff = ImageChops.difference(image_one.convert('RGB'), image_two.convert('RGB'))

    if diff.getbbox():
        return False
    else:
        return True


@dataclass
class CacheData:
    image: Any
    mask: Any
    invert: Any
    result: Any

cachedData = None



def processUpscaler(im):
    upscaler_name = getYandereInpaintUpscaler()
    upscalers = [x for x in shared.sd_upscalers if x.name == upscaler_name]
    if len(upscalers) == 0:
        raise Exception(f"Can't find yandrere inpainting model '{upscaler_name}'. See installation guide")
    else:
        upscaler = upscalers[0]

    old_ESRGAN_tile = shared.opts.ESRGAN_tile
    try:
        shared.opts.ESRGAN_tile = getYandereInpaintTileSize()
        im = upscaler.scaler.upscale(im, 1, upscaler.data_path)
    finally:
        shared.opts.ESRGAN_tile = old_ESRGAN_tile
    return im


def yandereInpaint(image: Image.Image, mask: Image.Image, invert: int):
    global cachedData
    result = None
    if cachedData is not None and\
            cachedData.invert == invert and\
            areImagesTheSame(cachedData.image, image) and\
            areImagesTheSame(cachedData.mask, mask):
        result = copy.copy(cachedData.result)
        print("yandere inpainted restored from cache")
        shared.state.assign_current_image(result)
    else:
        initMask = mask
        if invert:
            mask = ImageChops.invert(mask)
        mask = mask.convert('1').resize(image.size)
        greenFilling = Image.new('RGB', image.size, (0, 255, 0))
        maskedImage = copy.copy(image)
        maskedImage.paste(greenFilling, mask)
        shared.state.textinfo = "yandere inpainting"
        shared.state.assign_current_image(maskedImage)
        result = processUpscaler(maskedImage.convert('RGB')).convert('RGBA')
        shared.state.textinfo = ""
        shared.state.assign_current_image(result)
        if shared.state.interrupted:
            return image
        cachedData = CacheData(copy.copy(image), copy.copy(initMask), invert, copy.copy(result))
        print("yandere inpainted cached")

    return result
