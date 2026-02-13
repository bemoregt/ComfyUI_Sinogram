# ComfyUI_Sinogram

A ComfyUI custom node that generates a **sinogram** from an input image using the **Radon transform** — the mathematical foundation of CT (computed tomography) imaging.

![이미지 스펙트럼 예시](https://github.com/bemoregt/ComfyUI_Sinogram/blob/main/ScrShot%2017.png)

## Overview

The Radon transform projects an image along a set of angles, producing a 2D sinogram where each column represents one projection angle. This node makes it easy to visualize and experiment with sinogram generation directly inside ComfyUI workflows.

## Installation

**Option A — Clone into custom_nodes**
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/bemoregt/ComfyUI_Sinogram.git
```

**Option B — Symbolic link (development)**
```bash
ln -s /path/to/ComfyUI_Sinogram /path/to/ComfyUI/custom_nodes/ComfyUI_Sinogram
```

**Install dependency**
```bash
pip install scikit-image
```

Restart ComfyUI after installation.

## Node

| Field | Value |
|---|---|
| Display name | `Image → Sinogram (Radon)` |
| Category | `image/transform` |
| Input | `IMAGE` |
| Output | `IMAGE` (sinogram) |

## Parameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `image` | — | — | Input image (RGB/RGBA). Converted to grayscale internally. |
| `num_angles` | 180 | 2 – 720 | Number of projection angles. Higher values produce a wider, more detailed sinogram. |
| `angle_start` | 0.0 | 0 – 359° | Starting angle of the projection sweep (degrees). |
| `angle_end` | 180.0 | 1 – 360° | Ending angle of the projection sweep (degrees). |
| `circle` | True | — | If `True`, applies a circular mask before projection (standard CT convention). If `False`, the full square image is used. |
| `normalize` | True | — | If `True`, maps the output to [0, 1]. If `False`, scales by 1/255 and clips. |

## How It Works

1. Convert the input image to **grayscale**.
2. Pad to a **square** canvas (centered), so the Radon transform is well-defined.
3. If `circle=True`, apply a **circular mask** (pixels outside the inscribed circle are set to zero).
4. Compute the **Radon transform** via `skimage.transform.radon` over the specified angle range.
5. **Normalize** the resulting sinogram to [0, 1] (optional).
6. Return as a `(1, H, num_angles, 1)` float32 IMAGE tensor compatible with ComfyUI.

## Output Shape

For an input image of size `H × W`:

```
sinogram shape: (1, max(H,W), num_angles, 1)
```

Each column of the sinogram corresponds to one projection angle; each row corresponds to one detector position.

## Example Workflow

```
Load Image → Image → Sinogram (Radon) → Preview Image
```

You can chain the sinogram output into any standard ComfyUI image node (Save Image, Preview Image, VAE Encode, etc.).

## Dependencies

- `torch`
- `numpy`
- `Pillow`
- `scikit-image`

## License

MIT License

## Author

- [bemoregt](https://github.com/bemoregt)
