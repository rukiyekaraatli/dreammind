import torch
from typing import Optional
from loguru import logger

try:
    from diffusers import StableDiffusionPipeline
except ImportError:
    StableDiffusionPipeline = None

# Model cache ve yükleme
_sd_pipe: Optional[StableDiffusionPipeline] = None

def get_sd_pipeline() -> Optional[StableDiffusionPipeline]:
    """ss
    Stable Diffusion pipeline'ı cache'li şekilde yükler.
    """
    global _sd_pipe
    if _sd_pipe is not None:
        return _sd_pipe
    if StableDiffusionPipeline is None:
        logger.error("diffusers paketi yüklü değil.")
        return None
    try:
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
        _sd_pipe = pipe
        return pipe
    except Exception as e:
        logger.error(f"Stable Diffusion yüklenemedi: {e}")
        return None

def generate_dream_image(prompt: str, seed: Optional[int] = None) -> Optional[str]:
    """
    Verilen prompt ile rüya görseli üretir. Başarılıysa geçici bir dosya yolunu döner.
    """
    pipe = get_sd_pipeline()
    if pipe is None:
        return None
    try:
        generator = torch.Generator(device=pipe.device)
        if seed is not None:
            generator = generator.manual_seed(seed)
        with torch.autocast("cuda" if torch.cuda.is_available() else "cpu"):
            image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5, generator=generator).images[0]
        # Geçici dosyaya kaydet
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        logger.error(f"Görsel üretim hatası: {e}")
        return None 