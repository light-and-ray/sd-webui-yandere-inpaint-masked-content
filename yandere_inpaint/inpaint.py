from PIL import Image, ImageOps
import copy
from typing import Any
from dataclasses import dataclass
from modules.images import resize_image
from modules import shared
from .tools import (crop, uncrop, areImagesTheSame, applyMaskBlur, limitSizeByMinDimension
)
from .options import getYandereInpaintModel, getYandereInpaintTileSize

colorfix = None
try:
    from modules import colorfix
except ImportError:
    try:
        from srmodule import colorfix
    except ImportError:
        pass


def processUpscaler(im):
    upscaler_name = getYandereInpaintModel()
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
    upscaler: Any
    padding: Any
    resolution: Any
    blur: Any
    result: Any

cachedData = None



def yandereInpaint(image: Image, mask: Image, invert: int, upscaler: str, padding: int|None, resolution: int, blur: int):
    global cachedData
    result = None
    if cachedData is not None and\
            cachedData.invert == invert and\
            cachedData.upscaler == upscaler and\
            cachedData.padding == padding and\
            cachedData.resolution == resolution and\
            cachedData.blur == blur and\
            areImagesTheSame(cachedData.image, image) and\
            areImagesTheSame(cachedData.mask, mask):
        result = copy.copy(cachedData.result)
        print("yandere inpainted restored from cache")
        shared.state.assign_current_image(result)
    else:
        forCache = CacheData(image.copy(), mask.copy(), invert, upscaler, padding, resolution, blur, None)
        if invert == 1:
            mask = ImageOps.invert(mask)
        mask = applyMaskBlur(mask, blur)
        initImage = copy.copy(image)
        image = copy.copy(initImage)
        if padding is not None:
            maskNotCropped = mask
            image = crop(image, maskNotCropped, padding)
            mask = crop(mask, maskNotCropped, padding)
        resolution = min(*image.size, resolution)
        newW, newH = limitSizeByMinDimension(image, resolution)
        imageRes = image.resize((newW, newH))
        maskRes = mask.resize((newW, newH))

        greenFilling = Image.new('RGB', imageRes.size, (0, 255, 0))
        maskedImage = imageRes.copy()
        maskedImage.paste(greenFilling, maskRes.convert('1'))
        shared.state.textinfo = "yandere inpainting"
        shared.state.assign_current_image(maskedImage)

        tmpImage = processUpscaler(maskedImage.convert('RGB')).convert('RGBA').resize(imageRes.size)
        inpaintedImage = imageRes
        inpaintedImage.paste(tmpImage, maskRes)
        shared.state.assign_current_image(inpaintedImage)
        w, h = image.size
        shared.state.textinfo = "upscaling yandere inpainted"
        inpaintedImage = inpaintedImage.convert('RGB')
        beforeUpscale = inpaintedImage
        inpaintedImage = resize_image(0, inpaintedImage, w, h, upscaler)
        if colorfix:
            inpaintedImage = colorfix.wavelet_color_fix(inpaintedImage, beforeUpscale.resize(inpaintedImage.size)).convert('RGBA')
        result = image
        result.paste(inpaintedImage, mask)
        if padding is not None:
            result = uncrop(result, initImage, maskNotCropped, padding)
        shared.state.textinfo = ""
        forCache.result = result.copy()
        cachedData = forCache
        print("yandere inpainted cached")

    return result
