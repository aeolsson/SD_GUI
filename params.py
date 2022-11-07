history_dir = './history'

# paths to weights
models = {"base": "./dreambooth/models/stable-diffusion-v1-4/fp16/base"}
default_model = "base"

devices = ('cuda', 'cpu')
default_device = 'cuda'

# Initial model settings
revision = 'fp16'
censor_nsfw = True
seed = None
lock_seed = False
num_inference_steps = 30
guidance_scale = 12
width = 512
height = 512
num_images = 1