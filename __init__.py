import torch
import numpy as np
from PIL import Image, ImageOps
from skimage.transform import radon, rescale


class Image2Sinogram:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "num_angles": ("INT", {
                    "default": 180,
                    "min": 2,
                    "max": 720,
                    "step": 1,
                    "tooltip": "투영 각도 수 (클수록 sinogram이 세밀)"
                }),
                "angle_start": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 359.0,
                    "step": 1.0,
                    "tooltip": "시작 각도 (도)"
                }),
                "angle_end": ("FLOAT", {
                    "default": 180.0,
                    "min": 1.0,
                    "max": 360.0,
                    "step": 1.0,
                    "tooltip": "끝 각도 (도)"
                }),
                "circle": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "True: 원형 마스크 적용 (CT 방식), False: 전체 이미지 사용"
                }),
                "normalize": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "출력 sinogram을 0~1 범위로 정규화"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("sinogram",)
    FUNCTION = "compute_sinogram"
    CATEGORY = "image/transform"
    DESCRIPTION = "이미지에 Radon 변환을 적용하여 sinogram을 생성합니다."

    def compute_sinogram(self, image, num_angles, angle_start, angle_end, circle, normalize):
        # image: [B, H, W, C] float32 tensor (0~1)
        img_np = 255.0 * image[0].cpu().numpy()
        pil_img = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))

        # 그레이스케일 변환
        gray = np.array(ImageOps.grayscale(pil_img)).astype(np.float64)

        # 정사각형으로 맞추기 (radon은 정사각형 입력 권장)
        h, w = gray.shape
        size = max(h, w)
        square = np.zeros((size, size), dtype=np.float64)
        y_off = (size - h) // 2
        x_off = (size - w) // 2
        square[y_off:y_off + h, x_off:x_off + w] = gray

        # circle=True 시 원형 마스크 적용 (경고 방지)
        if circle:
            cy, cx = size / 2, size / 2
            radius = size / 2
            Y, X = np.ogrid[:size, :size]
            mask = (X - cx) ** 2 + (Y - cy) ** 2 <= radius ** 2
            square *= mask

        # 투영 각도 배열
        theta = np.linspace(angle_start, angle_end, num_angles, endpoint=False)

        # Radon 변환 → sinogram shape: (size, num_angles)
        sinogram = radon(square, theta=theta, circle=circle)

        # 정규화
        if normalize:
            s_min, s_max = sinogram.min(), sinogram.max()
            if s_max > s_min:
                sinogram = (sinogram - s_min) / (s_max - s_min)
            else:
                sinogram = np.zeros_like(sinogram)
        else:
            sinogram = sinogram / 255.0
            sinogram = np.clip(sinogram, 0, 1)

        # (H_sino, W_sino) → (1, H_sino, W_sino, 1) tensor
        sino_tensor = torch.from_numpy(sinogram.astype(np.float32)).unsqueeze(0).unsqueeze(-1)

        return (sino_tensor,)


NODE_CLASS_MAPPINGS = {
    "Image2Sinogram": Image2Sinogram
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Image2Sinogram": "Image → Sinogram (Radon)"
}
