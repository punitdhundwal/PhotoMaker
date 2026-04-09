import os
import numpy as np
from pathlib import Path
from vision_module import VisualFeatureExtractor

p = Path(__file__).parent
img_dir = p / 'demo_images'
images = [str(img_dir / f) for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"Found {len(images)} images in {img_dir}")

extractor = VisualFeatureExtractor()
# Force fallback to basic features to avoid heavy model loading
extractor.use_clip = False

if not images:
    print('No images found; exiting')
else:
    features = extractor.extract_batch(images)
    print('Features shape:', features.shape)
    for i, im in enumerate(images):
        norm = np.linalg.norm(features[i]) if features.shape[1] > 0 else 0
        print(f"{i}: {Path(im).name} -> norm {norm:.4f}")
