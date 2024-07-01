from modules import shared
import gradio as gr

ORIGINAL_NAME = '1x_NMKD-YandereInpaint_375000_G'


def getYandereInpaintUpscaler():
    res = shared.opts.data.get("yandere_inpaint_upscaler_name", ORIGINAL_NAME)
    return res

yandere_upscaler_settings = {
    'yandere_inpaint_upscaler_name': shared.OptionInfo(
                ORIGINAL_NAME,
                "Override yandere inpaint upscaler name",
                gr.Textbox,
            ),
}

shared.options_templates.update(shared.options_section(('upscaling', 'Upscaling'), yandere_upscaler_settings))

