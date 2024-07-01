import modules.scripts
from modules.processing import StableDiffusionProcessingImg2Img
from yandere_inpaint.inpaint import yandereInpaint

INPAINTING_FILL_ELEMENTS = ['img2img_inpainting_fill', 'replacer_inpainting_fill']



class Script(modules.scripts.Script):
    def __init__(self):
        pass

    def title(self):
        return "yandere-inpaint-masked-content"

    def show(self, is_img2img):
        return modules.scripts.AlwaysVisible

    def ui(self, is_img2img):
        pass

    def before_process(self, p: StableDiffusionProcessingImg2Img, *args):
        self.__init__()
        if NEW_ELEMENT_INDEX is None:
            return
        if not hasattr(p, 'inpainting_fill'):
            return
        if p.inpainting_fill != NEW_ELEMENT_INDEX:
            return
        if not (hasattr(p, "image_mask") and bool(p.image_mask)):
            return

        p.init_images[0] = yandereInpaint(p.init_images[0], p.image_mask,
                    p.inpainting_mask_invert)
        p.inpainting_fill = 1 # original


NEW_ELEMENT_INDEX = None

def addIntoMaskedContent(component, **kwargs):
    elem_id = kwargs.get('elem_id', None)
    if elem_id not in INPAINTING_FILL_ELEMENTS:
        return
    newElement = ('yandere inpaint', 'yandere inpaint')
    if newElement not in component.choices:
        component.choices.append(newElement)
    global NEW_ELEMENT_INDEX
    NEW_ELEMENT_INDEX = component.choices.index(newElement)


modules.scripts.script_callbacks.on_after_component(addIntoMaskedContent)
