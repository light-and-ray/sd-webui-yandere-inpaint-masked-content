# Yandere Inpainting as masked content

This extenstion for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) adds new value of "Masked content" field in img2img -> inpaint tab. It uses 1x upscaler [1x-NMKD-YandereInpaint](https://openmodeldb.info/models/1x-NMKD-YandereInpaint)

Installation:
- Install this extension: go into Extensions/Available, and find "yandere inpainting" there. Or install by url
- Download this model [here](https://icedrive.net/s/43GNBihZyi) (find YandereInpaint dir, and .pt file there) and place it in `models/ESRGAN` folder
- Restart webui

It works good for removing objects in small inpaint area in arts. But for big areas and for photos [lama cleaner](https://github.com/light-and-ray/sd-webui-lama-cleaner-masked-content) can be better
