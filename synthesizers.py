import numpy as np
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline,\
                      StableDiffusionImg2ImgPipeline,\
                      StableDiffusionInpaintPipeline

import params

class Image_synthesizer:
    def __init__(self,
                 device=params.default_device,
                 model_version=params.default_model,
                 revision=params.revision,
                 censor_nsfw=params.censor_nsfw,
                 num_inference_steps=params.num_inference_steps,
                 guidance_scale=params.guidance_scale,
                 seed=params.seed,
                 lock_seed=params.lock_seed,
                 num_images=params.num_images,
                 history_dir=params.history_dir):
        
        self.device = device
        self.version = model_version
        self.model_id = params.models[model_version]
        self.revision = revision
        self._txt2img = StableDiffusionPipeline.from_pretrained(self.model_id,
                                                                revision=revision, 
                                                                torch_dtype=torch.float16,
                                                                use_auth_token=True).to(device)
        self._txt2img.enable_attention_slicing()
        
        self._img2img = StableDiffusionImg2ImgPipeline(vae=self._txt2img.vae,
                                                       text_encoder=self._txt2img.text_encoder,
                                                       tokenizer=self._txt2img.tokenizer,
                                                       unet=self._txt2img.unet,
                                                       scheduler=self._txt2img.scheduler,
                                                       safety_checker=self._txt2img.safety_checker,
                                                       feature_extractor=self._txt2img.feature_extractor).to(device)
        self._img2img.enable_attention_slicing()
        
        self._inpaint = StableDiffusionInpaintPipeline(vae=self._txt2img.vae,
                                                       text_encoder=self._txt2img.text_encoder,
                                                       tokenizer=self._txt2img.tokenizer,
                                                       unet=self._txt2img.unet,
                                                       scheduler=self._txt2img.scheduler,
                                                       safety_checker=self._txt2img.safety_checker,
                                                       feature_extractor=self._txt2img.feature_extractor).to(device)
        self._inpaint.enable_attention_slicing()
        
        self.censor_nsfw = censor_nsfw
        def create_optional_safety_checker():
            base_safety_checker = self._txt2img.safety_checker
            def optional_safety_checker(images, clip_input):
                if self.censor_nsfw:
                    return base_safety_checker(images=images,
                                               clip_input=clip_input)
                else:
                    return (images, [False] * len(images))
            return optional_safety_checker
        self.optional_safety_checker = create_optional_safety_checker()
        
        self._txt2img.safety_checker = self.optional_safety_checker
        self._img2img.safety_checker = self.optional_safety_checker
        self._inpaint.safety_checker = self.optional_safety_checker
        
        self.num_inference_steps = num_inference_steps
        self.guidance_scale = guidance_scale
        self.num_images = num_images
        
        self.history_dir = history_dir
        
        if seed:
            self.seed = seed
        else:
            self.seed = int(np.random.randint(1e16, dtype=np.int64))
        self.lock_seed = lock_seed
    
    def txt2img(self, prompt, negative_prompt, height, width):
        with autocast(self.device):
            generator = torch.Generator(device=self.device).manual_seed(self.seed)
            images = self._txt2img(prompt=self.num_images*[prompt],
                                   negative_prompt=self.num_images*[negative_prompt],
                                   height=height,
                                   width=width,
                                   num_inference_steps=self.num_inference_steps,
                                   guidance_scale=self.guidance_scale,
                                   generator=generator).images
        
        name = "size {}x{}, steps {}, scale {}, seed {}, prompt '{}' .jpg".format(width,
                                                                                  height,
                                                                                  self.num_inference_steps,
                                                                                  self.guidance_scale,
                                                                                  self.seed,
                                                                                  ''.join(c for c in prompt if not c in '.:/\*?<>|"'))
        try:
            for image in images:                                                                        
                image.save('{}/{}'.format(self.history_dir, name))
        except:
            print('Could not save image.')
        
        if not self.lock_seed:
            self.seed = generator.seed()
        
        return images
    
    def img2img(self, negative_prompt, prompt, init_image, strength):
        with autocast(self.device):
            generator = torch.Generator(device=self.device).manual_seed(self.seed)
            images = self._img2img(prompt=self.num_images*[prompt],
                                   negative_prompt=self.num_images*[negative_prompt],
                                   init_image=self.num_images*[init_image],
                                   strength=strength,
                                   num_inference_steps=self.num_inference_steps,
                                   guidance_scale=self.guidance_scale,
                                   generator=generator).images
        width, height = images[0].size
        name = "size {}x{}, steps {}, scale {}, seed {}, prompt '{}' .jpg".format(width,
                                                                                  height,
                                                                                  self.num_inference_steps,
                                                                                  self.guidance_scale,
                                                                                  self.seed,
                                                                                  ''.join(c for c in prompt if not c in '.:/\*?<>|"'))
        
        try:
            for image in images:                                                                        
                image.save('{}/{}'.format(self.history_dir, name))
        except:
            print('Could not save image.')
        
        if not self.lock_seed:
            self.seed = generator.seed()
        
        return images
    
    def inpaint(self, prompt, negative_prompt, init_image, mask_image, strength):
        with autocast(self.device):
            generator = torch.Generator(device=self.device).manual_seed(self.seed)
            images = self._inpaint(prompt=self.num_images*[prompt],
                                   negative_prompt=self.num_images*[negative_prompt],
                                   init_image=self.num_images*[init_image],
                                   mask_image=self.num_images*[mask_image],
                                   strength=strength,
                                   num_inference_steps=self.num_inference_steps,
                                   guidance_scale=self.guidance_scale,
                                   generator=generator).images
        
        width, height = images[0].size
        name = "size {}x{}, steps {}, scale {}, seed {}, prompt '{}' .jpg".format(width,
                                                                                  height,
                                                                                  self.num_inference_steps,
                                                                                  self.guidance_scale,
                                                                                  self.seed,
                                                                                  ''.join(c for c in prompt if not c in '.:/\*?<>|"'))
        try:
            for image in images:
                image.save('{}/{}'.format(self.history_dir, name))
        except:
            print('Could not save image.')
        
        if not self.lock_seed:
            self.seed = generator.seed()
        
        return images
    
    def set_model(self, version):
        del self._txt2img, self._img2img, self._inpaint
        torch.cuda.empty_cache()
        
        self.version = version
        self.model_id = params.models[version]
        self._txt2img = StableDiffusionPipeline.from_pretrained(self.model_id,
                                                                  revision=self.revision, 
                                                                  torch_dtype=torch.float16,
                                                                  use_auth_token=True).to(self.device)
        self._txt2img.enable_attention_slicing()
        
        self._img2img = StableDiffusionImg2ImgPipeline(vae=self._txt2img.vae,
                                                       text_encoder=self._txt2img.text_encoder,
                                                       tokenizer=self._txt2img.tokenizer,
                                                       unet=self._txt2img.unet,
                                                       scheduler=self._txt2img.scheduler,
                                                       safety_checker=self._txt2img.safety_checker,
                                                       feature_extractor=self._txt2img.feature_extractor).to(self.device)
        self._img2img.enable_attention_slicing()
        
        self._inpaint = StableDiffusionInpaintPipeline(vae=self._txt2img.vae,
                                                       text_encoder=self._txt2img.text_encoder,
                                                       tokenizer=self._txt2img.tokenizer,
                                                       unet=self._txt2img.unet,
                                                       scheduler=self._txt2img.scheduler,
                                                       safety_checker=self._txt2img.safety_checker,
                                                       feature_extractor=self._txt2img.feature_extractor).to(self.device)
        self._inpaint.enable_attention_slicing()
        
        self._txt2img.safety_checker = self.optional_safety_checker
        self._img2img.safety_checker = self.optional_safety_checker
        self._inpaint.safety_checker = self.optional_safety_checker
    
    def set_device(self, device):
        self._txt2img.to(device)
        self._img2img.to(device)
        self._inpaint.to(device)
        
        torch.cuda.empty_cache()
        
        self.device = device
    
    def set_seed(self, seed):
        self.seed = seed
    
    def set_inference_steps(self, inference_steps):
        self.num_inference_steps = inference_steps
    
    def set_guidance_scale(self, guidance_scale):
        self.guidance_scale = guidance_scale
    
    def set_num_images(self, num_images):
        self.num_images = num_images
    
    def set_censor(self, censor_nsfw):
        self.censor_nsfw = censor_nsfw
    
    def _save_result(self):
        pass

if __name__=='__main__':
    syn = Image_synthesizer()