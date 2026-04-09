# Quick Start Guide

Get started with the Photo Book Generator in 5 minutes!

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Image processing (Pillow, OpenCV)
- Computer vision (PyTorch, CLIP)
- Clustering (scikit-learn)
- PDF generation (ReportLab)

### 2. Verify Installation

```bash
python test_installation.py
```

You should see all tests passing with ✓ marks.

## Basic Usage

### Method 1: Command Line (Easiest)

```bash
# Generate a photo book from a folder
python main.py generate /path/to/your/photos --title "My Photo Book"
```

That's it! You'll find `photobook.pdf` in the `./output` directory.

### Method 2: Python Script

Create a file `my_photobook.py`:

```python
from photobook_generator import PhotoBookGenerator

# Initialize generator with your image folder
generator = PhotoBookGenerator(
    image_dir="./my_vacation_photos",
    output_dir="./output"
)

# Generate photo book
pdf_path = generator.generate_full_pipeline(
    output_filename="vacation_2024.pdf",
    title="Summer Vacation 2024"
)

print(f"Done! Photo book saved to: {pdf_path}")
```

Run it:
```bash
python my_photobook.py
```

## Common Use Cases

### 1. Event Photo Book (e.g., Wedding, Birthday)

```bash
python main.py generate ./wedding_photos \
    --title "Sarah & John's Wedding" \
    --chapters \
    --output wedding_book.pdf
```

### 2. Travel Photo Book

```bash
python main.py generate ./europe_trip \
    --title "European Adventure 2024" \
    --clusters 8 \
    --chapters
```

### 3. Portfolio (No Chapters)

```bash
python main.py generate ./portfolio \
    --title "Photography Portfolio" \
    --no-chapters \
    --output portfolio.pdf
```

## Command-Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--output-dir` | `-o` | Where to save output | `-o ./books` |
| `--output` | `-f` | PDF filename | `-f mybook.pdf` |
| `--title` | `-t` | Book title | `-t "My Book"` |
| `--clusters` | `-c` | Number of clusters | `-c 5` |
| `--chapters` | | Use chapter organization | `--chapters` |
| `--no-chapters` | | Sequential layout | `--no-chapters` |
| `--gpu` | | Use GPU acceleration | `--gpu` |

## Python API

### Step-by-Step Control

For more control, process each step individually:

```python
from photobook_generator import PhotoBookGenerator

generator = PhotoBookGenerator(image_dir="./photos")

# Step 1: Extract metadata
generator.process_images()
print(f"Found {len(generator.metadata_list)} images")

# Step 2: Extract visual features
generator.extract_visual_features()
print(f"Extracted features: {generator.features.shape}")

# Step 3: Cluster images
generator.cluster_images(n_clusters=5)

# Step 4: Compute weights
generator.compute_visual_weights()

# Step 5: Generate PDF
pdf_path = generator.generate_photobook(
    output_filename="custom_book.pdf",
    title="My Custom Book"
)

# Get statistics
stats = generator.get_statistics()
print(f"Created book with {stats['num_clusters']} chapters")
```

## Example Directory Structure

```
my-project/
├── photos/                 # Your images here
│   ├── IMG_001.jpg
│   ├── IMG_002.jpg
│   └── ...
├── output/                 # Generated PDFs appear here
│   └── photobook.pdf
├── main.py                 # CLI script
├── photobook_generator.py  # Main code
└── requirements.txt        # Dependencies
```

## Tips for Best Results

### 📸 Image Organization
- **Single Event**: Photos from one event cluster better
- **Time Order**: Images with timestamps order automatically
- **Location Data**: GPS coordinates enable location-based grouping

### 🎨 Quality
- **Mixed Sizes**: System handles different resolutions
- **Variety**: Mix of portraits and landscapes looks good
- **Metadata**: Images with EXIF data produce better results

### ⚡ Performance
- **<50 images**: Works fine on CPU
- **50-200 images**: Use `--gpu` flag if available
- **>200 images**: Consider breaking into multiple books

### 🎯 Clustering
- **Auto**: Let system decide cluster count (recommended)
- **Manual**: Use `--clusters N` for specific number
- **Too many clusters**: Each image in own chapter (bad)
- **Too few clusters**: Everything grouped together (bad)
- **Sweet spot**: Usually 3-8 clusters for 50-200 images

## Troubleshooting

### "No valid images found"
**Problem**: System can't find images  
**Solution**: Check that your folder has .jpg, .jpeg, .png, .tiff, or .bmp files

### Slow performance
**Problem**: Taking too long to process  
**Solution**: 
- Use `--gpu` flag if you have CUDA-enabled GPU
- Process fewer images at once
- Reduce image resolution before processing

### Out of memory
**Problem**: System crashes during processing  
**Solution**:
- Close other applications
- Process smaller batches
- Resize images to smaller dimensions

### Poor clustering
**Problem**: Images grouped oddly  
**Solution**:
- Try specifying `--clusters N` manually
- Ensure images are from similar events/contexts
- Check that images have varied content

## Next Steps

1. ✅ Generated your first photo book? Great!
2. 📖 Read the full [README.md](README.md) for detailed features
3. 🔧 Check [DOCUMENTATION.md](DOCUMENTATION.md) for technical details
4. 💡 See [example_usage.py](example_usage.py) for more examples

## Quick Reference

### Generate Basic Book
```bash
python main.py generate ./photos
```

### With Custom Title
```bash
python main.py generate ./photos --title "My Book"
```

### With Specific Clusters
```bash
python main.py generate ./photos --clusters 5
```

### Without Chapters
```bash
python main.py generate ./photos --no-chapters
```

### Use GPU
```bash
python main.py generate ./photos --gpu
```

### Full Command
```bash
python main.py generate ./photos \
    --output-dir ./books \
    --output my_book.pdf \
    --title "Amazing Photos" \
    --clusters 6 \
    --chapters \
    --gpu
```

## Getting Help

### Command Help
```bash
python main.py --help
python main.py generate --help
```

### Check Version
```bash
python main.py version
```

### Analyze Collection (No PDF)
```bash
python main.py analyze ./photos --output analysis.json
```

## Common Workflows

### Workflow 1: Quick Photo Book
```bash
# Just give me a photo book!
python main.py generate ./photos
```
Output: `./output/photobook.pdf`

### Workflow 2: Custom Settings
```python
from photobook_generator import PhotoBookGenerator

gen = PhotoBookGenerator("./photos")
gen.generate_full_pipeline(
    output_filename="my_book.pdf",
    title="Custom Title",
    n_clusters=4,
    use_chapters=True
)
```

### Workflow 3: Analyze First, Then Generate
```bash
# Step 1: Analyze
python main.py analyze ./photos

# Review the statistics

# Step 2: Generate with informed settings
python main.py generate ./photos --clusters 5
```

---

**Need more help?** Check the full documentation or example scripts!
