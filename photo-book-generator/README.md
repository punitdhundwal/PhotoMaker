# Automated Photo Book Generation System

A complete Python-based system for automatically organizing image collections into coherent visual narratives and generating printable photo books in PDF format.

## 🎯 Project Overview

This system automatically:
- Extracts and processes image metadata (EXIF, timestamps, GPS)
- Orders images into visual storylines
- Clusters images by visual similarity and content
- Computes visual importance weights
- Generates professional photo book layouts
- Exports high-quality PDF photo books

## 🏗️ System Architecture

The system consists of three main modules:

### Module A: Metadata & Story Logic
- **File**: `metadata_module.py`
- EXIF extraction and normalization
- Time and location-based ordering
- Storyline construction logic
- Handling missing/conflicting metadata
- Time gap detection for chapter separation
- Geographic clustering

### Module B: Computer Vision & Clustering
- **File**: `vision_module.py`
- Visual feature extraction using CLIP embeddings
- Similarity computation and clustering (K-Means, DBSCAN)
- Semantic labeling of image groups
- Quality assessment (sharpness, face detection)
- Similarity graph construction

### Module C: Layout, Templates & PDF Output
- **File**: `layout_module.py`
- Visual weight computation
- Automatic layout selection
- Photo book template system
- PDF generation and rendering
- Multi-page layout optimization

### Integration Layer
- **File**: `photobook_generator.py`
- Orchestrates all modules
- Complete pipeline execution
- Statistics and reporting

## 📋 Requirements

### Python Version
- Python 3.10 or higher

### Core Dependencies
```bash
pip install -r requirements.txt
```

Key libraries:
- **Image Processing**: Pillow, exifread, piexif, opencv-python
- **Computer Vision**: torch, torchvision, open-clip-torch
- **Clustering**: numpy, scikit-learn, hdbscan
- **Visualization**: networkx
- **PDF Generation**: reportlab
- **CLI**: typer, tqdm

## 🚀 Installation

1. **Clone or download the system:**
```bash
# If you have the files, navigate to the directory
cd photo-book-generator
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify installation:**
```bash
python main.py version
```

## 💡 Usage

### Quick Start (Command Line)

Generate a photo book from a directory of images:

```bash
python main.py generate /path/to/your/images --title "My Photo Book"
```

### Basic Usage Example

```python
from photobook_generator import PhotoBookGenerator

# Create generator
generator = PhotoBookGenerator(
    image_dir="./my_photos",
    output_dir="./output"
)

# Generate photo book
pdf_path = generator.generate_full_pipeline(
    output_filename="vacation_2024.pdf",
    title="Summer Vacation 2024"
)

print(f"Photo book created: {pdf_path}")
```

### Advanced Usage

```python
# Step-by-step processing with custom configuration
generator = PhotoBookGenerator(
    image_dir="./photos",
    output_dir="./output",
    use_gpu=True  # Use GPU if available
)

# Process images
generator.process_images()

# Extract visual features
generator.extract_visual_features()

# Cluster with specific number of groups
generator.cluster_images(n_clusters=5)

# Compute importance weights
generator.compute_visual_weights()

# Generate photo book
pdf_path = generator.generate_photobook(
    output_filename="custom_book.pdf",
    title="My Custom Photo Book",
    use_chapters=True
)

# Get statistics
stats = generator.get_statistics()
print(stats)
```

### Command-Line Options

```bash
# Full pipeline with all options
python main.py generate ./photos \
    --output-dir ./output \
    --output my_photobook.pdf \
    --title "My Amazing Photos" \
    --clusters 5 \
    --chapters \
    --gpu

# Analyze collection without generating PDF
python main.py analyze ./photos --output analysis.json

# Show help
python main.py --help
```

## 📁 Project Structure

```
photo-book-generator/
├── metadata_module.py          # Module A: Metadata extraction
├── vision_module.py            # Module B: Computer vision
├── layout_module.py            # Module C: Layout & PDF
├── photobook_generator.py      # Main integration pipeline
├── main.py                     # Command-line interface
├── example_usage.py            # Usage examples
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### Template Customization

Modify layout templates in `layout_module.py`:

```python
template = PhotoBookTemplate("custom", page_size=A4)
# Adjust margins, layouts, etc.
```

### Feature Extraction

Choose different CLIP models:

```python
feature_extractor = VisualFeatureExtractor(
    model_name='ViT-B-32',  # or 'ViT-L-14', etc.
    device='cuda'
)
```

### Clustering Parameters

Adjust clustering behavior:

```python
# Auto-clustering
generator.cluster_images()

# Fixed number of clusters
generator.cluster_images(n_clusters=5)
```

## 📊 Features

### Metadata Processing
✅ EXIF timestamp extraction  
✅ GPS coordinate parsing  
✅ Camera information  
✅ Automatic time-based ordering  
✅ Fallback to file modification dates  

### Visual Analysis
✅ Deep learning feature extraction (CLIP)  
✅ Color histogram fallback  
✅ Sharpness assessment  
✅ Face detection  
✅ Similarity computation  

### Clustering & Organization
✅ K-Means clustering  
✅ DBSCAN density-based clustering  
✅ Automatic cluster number selection  
✅ Semantic labeling  
✅ Time-gap chapter detection  

### Layout & Design
✅ Multiple layout templates  
✅ Automatic layout selection  
✅ Aspect ratio optimization  
✅ Visual weight-based arrangement  
✅ Chapter organization  

### PDF Output
✅ High-quality image rendering  
✅ Aspect ratio preservation  
✅ Title and chapter pages  
✅ Page numbering  
✅ Professional borders  

## 🎓 Learning Outcomes

This project demonstrates:
- **Modular system design** combining metadata and visual analysis
- **Computer vision** with pretrained models
- **Clustering algorithms** and similarity-based reasoning
- **Automated layout generation** from algorithmic results
- **Technical collaboration** in a software project

## 📝 Example Workflows

### 1. Vacation Photos
```python
generator = PhotoBookGenerator("vacation_photos")
pdf = generator.generate_full_pipeline(
    title="Europe Trip 2024",
    use_chapters=True  # Separate by location/time
)
```

### 2. Event Photography
```python
generator = PhotoBookGenerator("wedding_photos")
generator.process_images()
generator.extract_visual_features()
generator.cluster_images(n_clusters=8)  # Ceremony, reception, etc.
pdf = generator.generate_photobook(title="Sarah & John's Wedding")
```

### 3. Portfolio
```python
generator = PhotoBookGenerator("portfolio")
pdf = generator.generate_full_pipeline(
    title="Photography Portfolio",
    use_chapters=False  # Sequential, curated order
)
```

## ⚠️ Limitations

- **Performance**: Feature extraction can be slow for large collections (100+ images)
- **GPU recommended**: For collections >50 images
- **Memory**: Large images may require significant RAM
- **Metadata**: Not all images have complete EXIF data
- **Clustering**: Quality depends on visual diversity

## 🔍 Troubleshooting

### Issue: "No valid images found"
**Solution**: Ensure images are in supported formats (.jpg, .jpeg, .png, .tiff, .bmp)

### Issue: Slow feature extraction
**Solution**: Use GPU mode with `use_gpu=True` or reduce image count

### Issue: Poor clustering results
**Solution**: Try specifying `n_clusters` manually or adjust collection size

### Issue: CLIP model not loading
**Solution**: System will fall back to basic color histogram features

## 🚀 Future Enhancements

Potential improvements:
- Web interface for easier use
- More layout templates
- Text overlay and captions
- OCR for automatically detecting text in images
- Cloud storage integration
- Batch processing of multiple collections
- Custom styling and themes

## 📄 License

This is an academic/educational project developed according to the specifications in the project requirements document.

## 👥 Module Responsibilities

### Student A - Metadata & Story Logic
- `metadata_module.py`
- EXIF extraction, time/location ordering, storyline construction

### Student B - Computer Vision & Clustering
- `vision_module.py`
- Feature extraction, similarity analysis, clustering, quality assessment

### Student C - Layout & PDF Output
- `layout_module.py`
- Weight computation, template design, layout algorithms, PDF rendering

### Integration
- `photobook_generator.py` - Complete pipeline
- `main.py` - CLI interface
- `example_usage.py` - Usage demonstrations

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Generate basic photo book | `python main.py generate ./photos` |
| With custom title | `python main.py generate ./photos --title "My Book"` |
| Specify clusters | `python main.py generate ./photos --clusters 5` |
| Without chapters | `python main.py generate ./photos --no-chapters` |
| Use GPU | `python main.py generate ./photos --gpu` |
| Analyze only | `python main.py analyze ./photos` |
| Show version | `python main.py version` |
| Get help | `python main.py --help` |

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review example_usage.py for working examples
3. Ensure all dependencies are installed correctly
4. Verify image directory contains valid image files

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: 2024
