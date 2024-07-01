# Yandere Inpainting as masked content

This extenstion for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) adds new value of "Masked content" field in img2img -> inpaint tab. It uses ESRGAN 1x upscaler [1x-NMKD-YandereInpaint](https://openmodeldb.info/models/1x-NMKD-YandereInpaint)

![](/images/authors_example.jpg)

Installation:
- Install this extension: go into Extensions/Available, and find "yandere inpainting" there. Or install by url
- Download this model [here](https://icedrive.net/s/43GNBihZyi) (find YandereInpaint dir, and .pt file there) and place it in `models/ESRGAN` folder
- Restart webui

Usage:
- in inpainting tab select masked content - yandere inpainting
- set denoising to low. If you use 0, set sampler to Euler, or it will be crash. 0 means almost original model output
- be sure your resolution is good
- use small brush size, in other way the model will generate white areas

It works good for removing small objects/watermarks in anime arts. But for big areas and for photos [lama cleaner](https://github.com/light-and-ray/sd-webui-lama-cleaner-masked-content) is better
