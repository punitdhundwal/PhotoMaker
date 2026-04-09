# Technical Documentation

## System Architecture

### Overview
The Photo Book Generator follows a modular pipeline architecture with three core subsystems that work together to transform unstructured image collections into professionally laid-out photo books.

```
Input Images → Metadata → Features → Clustering → Weights → Layout → PDF
     ↓           (A)        (B)         (B)        (C)       (C)      (C)
  [Files]    [Timeline] [Embeddings] [Groups]   [Scores]  [Pages] [Output]
```

## Module A: Metadata & Story Logic

### Components

#### MetadataExtractor
**Purpose**: Extract and normalize EXIF metadata from images

**Key Methods**:
- `extract_metadata(image_path)`: Extract comprehensive metadata from single image
- `extract_batch(image_dir)`: Process entire directory
- `_parse_pil_exif()`: Primary EXIF parser using PIL
- `_parse_exifread()`: Fallback parser using exifread library
- `_parse_gps()`: Extract and convert GPS coordinates

**Metadata Fields**:
- `filepath`: Absolute path to image
- `filename`: File name
- `timestamp`: Capture date/time (DateTime or fallback to file mtime)
- `gps_latitude/longitude`: GPS coordinates in decimal degrees
- `camera_make/model`: Camera information
- `width/height`: Image dimensions
- `orientation`: EXIF orientation flag
- `has_metadata`: Boolean indicating if EXIF was found

**Fallback Strategy**:
1. Try PIL EXIF extraction
2. If fails, try exifread library
3. If no timestamp found, use file modification time
4. Mark `has_metadata=False` if EXIF missing

#### StorylineConstructor
**Purpose**: Order and organize images into narrative structure

**Key Methods**:
- `order_by_time()`: Sort images chronologically
- `detect_time_gaps()`: Identify chapter boundaries based on time gaps
- `group_by_location()`: Cluster images by GPS proximity

**Algorithms**:

1. **Temporal Ordering**:
   ```python
   sorted(metadata_list, key=lambda x: x.timestamp or datetime.min)
   ```

2. **Time Gap Detection**:
   - Default threshold: 6 hours
   - Creates new chapter when gap exceeds threshold
   - Handles missing timestamps gracefully

3. **Geographic Clustering**:
   - Uses Haversine formula for distance calculation
   - Default proximity threshold: 10km
   - Simple distance-based grouping algorithm

**Haversine Distance**:
```
a = sin²(Δlat/2) + cos(lat₁) × cos(lat₂) × sin²(Δlon/2)
c = 2 × atan2(√a, √(1−a))
d = R × c  (R = 6371 km)
```

## Module B: Computer Vision & Clustering

### Components

#### VisualFeatureExtractor
**Purpose**: Extract deep visual features from images

**Models**:
- **Primary**: CLIP (Contrastive Language-Image Pre-training)
  - Default: ViT-B-32 (Vision Transformer, Base, 32x32 patches)
  - Output: 512-dimensional embedding
  - Pre-trained on 400M image-text pairs

- **Fallback**: Color Histogram
  - HSV color space
  - 32 bins per channel (H, S, V)
  - Total: 96 dimensions, padded to 512

**Feature Extraction Pipeline**:
```
Image → Preprocessing → Model → L2 Normalization → Feature Vector
  ↓         (resize)      ↓         (unit norm)          ↓
 PIL       224x224    ViT/CNN        ||v|| = 1        512-dim
```

#### ImageClusterer
**Purpose**: Group similar images into semantic clusters

**Algorithms**:

1. **K-Means Clustering**:
   - Partitions images into k groups
   - Minimizes within-cluster sum of squares
   - Good for balanced, spherical clusters
   - O(n·k·i·d) complexity

2. **DBSCAN (Density-Based Spatial Clustering)**:
   - Finds arbitrary-shaped clusters
   - Parameters: eps (neighborhood radius), min_samples
   - Handles outliers (label = -1)
   - Good for varying cluster sizes

3. **Auto-Clustering**:
   ```python
   if n_images < 5: 
       1 cluster (all together)
   elif n_images < 20:
       3 clusters (K-Means)
   else:
       Try DBSCAN, fallback to K-Means if poor results
   ```

**Semantic Labeling**:
- Analyzes temporal patterns within clusters
- Labels based on time span:
  - ≤1 day: "Event_N"
  - ≤7 days: "Week_N"
  - >7 days: "Period_N"

#### SimilarityAnalyzer
**Purpose**: Compute pairwise similarities and relationships

**Similarity Metric**:
- Cosine Similarity: cos(θ) = (A·B) / (||A|| ||B||)
- Range: -1 (opposite) to 1 (identical)
- Normalized features ensure ||A|| = ||B|| = 1

**Graph Construction**:
- Nodes: Images
- Edges: Similarity > threshold (default 0.5)
- Weight: Cosine similarity value
- Used for narrative flow inference

**Narrative Ordering Algorithm**:
```python
1. Start from image i
2. Mark i as visited
3. Find most similar unvisited image j
4. Move to j, mark as visited
5. Repeat until all visited
```

#### QualityAnalyzer
**Purpose**: Assess technical quality of images

**Metrics**:

1. **Sharpness** (Laplacian Variance):
   ```
   Score = Var(∇²I)
   where ∇²I = Laplacian(Image)
   ```
   - Higher variance = sharper image
   - Typical range: 0-1000

2. **Face Detection**:
   - Haar Cascade classifier
   - Counts number of faces
   - More faces often = more important

## Module C: Layout, Templates & PDF Output

### Components

#### VisualWeightCalculator
**Purpose**: Compute importance score for each image

**Weight Formula**:
```
W = 0.25×Sharpness + 0.25×Faces + 0.20×Uniqueness + 
    0.15×Resolution + 0.15×Metadata
```

**Component Scores**:

1. **Sharpness**: 
   - Normalized to [0,1] assuming max ~500
   - `min(sharpness/500, 1.0)`

2. **Faces**:
   - Capped at 5 faces
   - `min(face_count/5, 1.0)`

3. **Uniqueness**:
   - Inverse of cluster size
   - `1.0 / (1.0 + cluster_size/10)`

4. **Resolution**:
   - Based on megapixels
   - `min(megapixels/12, 1.0)`

5. **Metadata Quality**:
   - Timestamp: +0.4
   - GPS: +0.3
   - Camera: +0.3

#### PhotoBookTemplate
**Purpose**: Define page layouts and dimensions

**Page Specifications**:
- Default: A4 (210mm × 297mm)
- Margins: 0.5 inch
- Usable area: page_size - 2×margin

**Layout Types**:

1. **single_full**: One large image covering most of page
2. **single_portrait**: One portrait-oriented image centered
3. **double_horizontal**: Two images side by side
4. **double_vertical**: Two images stacked vertically
5. **triple**: One large + two smaller images
6. **grid_4**: Four images in 2×2 grid

**Layout Structure**:
```python
[(x, y, width, height), ...]  # List of boxes for image placement
```

#### LayoutEngine
**Purpose**: Automatically select and arrange layouts

**Layout Selection Logic**:
```python
if n_images == 1:
    if portrait: 'single_portrait'
    else: 'single_full'
elif n_images == 2:
    if landscape: 'double_vertical'
    else: 'double_horizontal'
elif n_images == 3:
    'triple'
else:
    'grid_4'
```

**Arrangement Strategy**:
- High-weight images (>0.8): Own page
- Medium-weight (>0.6): Pair with one other
- Lower weight: Group up to 4 images

#### PDFRenderer
**Purpose**: Generate final PDF document

**Rendering Pipeline**:
```
1. Create canvas with page size
2. Render title page
3. For each page:
   a. Get layout template
   b. Place images in boxes
   c. Fit images maintaining aspect ratio
   d. Draw borders
   e. Add page number
4. Save PDF
```

**Image Fitting Algorithm**:
```python
aspect = width / height
if aspect > box_aspect:
    # Width-constrained
    fit_width = box_width
    fit_height = box_width / aspect
else:
    # Height-constrained
    fit_height = box_height
    fit_width = box_height * aspect

# Center in box
x_offset = (box_width - fit_width) / 2
y_offset = (box_height - fit_height) / 2
```

## Integration Layer

### PhotoBookGenerator
**Purpose**: Orchestrate complete pipeline

**Pipeline Stages**:

1. **Process Images**:
   - Extract metadata from all images
   - Order by timestamp
   - Output: List of ImageMetadata objects

2. **Extract Features**:
   - Compute visual embeddings
   - Progress tracking with tqdm
   - Output: Feature matrix (n_images × 512)

3. **Cluster Images**:
   - Apply clustering algorithm
   - Label clusters semantically
   - Output: Cluster labels + semantic names

4. **Compute Weights**:
   - Assess quality metrics
   - Calculate importance scores
   - Output: Weight vector (n_images,)

5. **Generate Photo Book**:
   - Arrange images into pages
   - Render to PDF
   - Output: PDF file path

**Data Flow**:
```
Images → Metadata[] → Features[n×512] → Labels[n] → Weights[n] → Pages[] → PDF
```

## Performance Considerations

### Computational Complexity

**Metadata Extraction**: O(n)
- n = number of images
- ~0.1s per image

**Feature Extraction**: O(n·m)
- n = number of images
- m = model inference time
- ~0.5s per image (CPU), ~0.05s (GPU)

**Clustering**: 
- K-Means: O(n·k·i·d)
  - k = clusters, i = iterations, d = dimensions
  - ~1s for 100 images
- DBSCAN: O(n²) worst case, O(n log n) average

**Similarity Matrix**: O(n²·d)
- Quadratic in number of images
- Consider sampling for n > 1000

**PDF Rendering**: O(p)
- p = number of pages
- ~0.2s per page

### Memory Usage

**Feature Matrix**: n × 512 × 8 bytes
- 100 images: ~400 KB
- 1000 images: ~4 MB

**Image Loading**: Temporary
- One image at a time for features
- All images loaded during PDF rendering

**Recommendations**:
- <50 images: CPU fine
- 50-200 images: GPU recommended
- >200 images: GPU + batch processing

## Error Handling

### Graceful Degradation

1. **Missing EXIF**: Use file modification time
2. **CLIP fails**: Fallback to color histograms
3. **Clustering fails**: Single cluster (sequential)
4. **Image load fails**: Skip with warning
5. **No faces detected**: Face score = 0

### Validation

- Check directory exists
- Verify image formats
- Ensure output directory writable
- Validate cluster numbers

## Testing

### Unit Tests (Recommended)
```python
# Test metadata extraction
def test_metadata_extraction():
    extractor = MetadataExtractor()
    metadata = extractor.extract_metadata("test.jpg")
    assert metadata.filepath is not None
    
# Test feature extraction
def test_feature_extraction():
    extractor = VisualFeatureExtractor()
    features = extractor.extract_features("test.jpg")
    assert features.shape == (512,)
    
# Test clustering
def test_clustering():
    features = np.random.randn(10, 512)
    clusterer = ImageClusterer()
    labels = clusterer.cluster_kmeans(features, 3)
    assert len(labels) == 10
```

### Integration Test
```python
def test_full_pipeline():
    generator = PhotoBookGenerator("test_images")
    pdf_path = generator.generate_full_pipeline(
        output_filename="test.pdf",
        title="Test Book"
    )
    assert Path(pdf_path).exists()
```

## Extension Points

### Adding New Layouts
```python
# In PhotoBookTemplate.get_layout()
'custom_layout': [
    (x1, y1, w1, h1),
    (x2, y2, w2, h2),
    # ...
]
```

### Custom Clustering
```python
# In ImageClusterer
def cluster_custom(self, features):
    # Your algorithm
    return labels
```

### Additional Metadata
```python
# In ImageMetadata model
class ImageMetadata(BaseModel):
    # ... existing fields ...
    focal_length: Optional[float] = None
    iso: Optional[int] = None
```

### Custom Weight Calculation
```python
# In VisualWeightCalculator
def compute_custom_weight(self, ...):
    # Your weighting formula
    return weight
```

## Best Practices

1. **Organize by Event**: Images from single event cluster better
2. **Consistent Quality**: Mix of quality levels works well
3. **Metadata Matters**: Images with EXIF produce better results
4. **GPU for Scale**: Use GPU for >50 images
5. **Review Clusters**: Check cluster count makes sense
6. **Test Layouts**: Preview different layout options

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow processing | Large images, CPU mode | Resize images, use GPU |
| Poor clustering | Too few/many clusters | Adjust n_clusters parameter |
| Bad layouts | Wrong aspect ratios | Check layout selection logic |
| Missing timestamps | No EXIF data | Files use mtime automatically |
| CLIP not loading | Missing dependencies | Falls back to color histograms |
| Out of memory | Too many images | Process in batches |

## References

### Papers & Resources
- CLIP: "Learning Transferable Visual Models From Natural Language Supervision" (Radford et al., 2021)
- K-Means: MacQueen, 1967
- DBSCAN: Ester et al., 1996

### Libraries
- [ReportLab](https://www.reportlab.com/): PDF generation
- [OpenCLIP](https://github.com/mlfoundations/open_clip): CLIP models
- [scikit-learn](https://scikit-learn.org/): Clustering algorithms
