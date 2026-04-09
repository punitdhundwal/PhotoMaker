"""
Main Integration Module
Combines all subsystems into a complete photo book generation pipeline
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from tqdm import tqdm
import re
from collections import Counter

# Import geopy for location naming
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

from metadata_module import MetadataExtractor, StorylineConstructor, ImageMetadata
from vision_module import (
    VisualFeatureExtractor, ImageClusterer, SimilarityAnalyzer, QualityAnalyzer
)
from layout_module import (
    VisualWeightCalculator, PhotoBookTemplate, LayoutEngine, PDFRenderer
)


# List of common objects/scenes to check for
COMMON_OBJECTS = [
    # Landmarks & Travel (Added for you)
    "Statue of Liberty", "Eiffel Tower", "Taj Mahal", "Colosseum", "Great Wall of China",
    "monument", "statue", "landmark", "USA", "India", "France", "Japan", "travel",
    
    # Nature & Scenery
    "beach", "mountain", "forest", "city", "sunset", "lake", "ocean", "river",
    "park", "garden", "flower", "snow", "desert", "sky", 
    
    # Events & People
    "party", "wedding", "concert", "festival", "baby", "family", "graduation", 
    
    # Objects & Animals
    "cat", "dog", "bird", "wildlife", "food", "car", "boat", "plane", 
    "building", "architecture", "book", "art",
    
    # Technical
    "computer", "screenshot", "diagram", "document"
]

class PhotoBookGenerator:
    """
    Complete photo book generation system
    Orchestrates all modules to create a photo book from image collection
    """
    
    def __init__(self, 
                 image_dir: str,
                 output_dir: str = "./output",
                 use_gpu: bool = False):
        """
        Initialize photo book generator
        """
        self.image_dir = Path(image_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize modules
        print("Initializing modules...")
        self.metadata_extractor = MetadataExtractor()
        self.storyline_constructor = StorylineConstructor()
        self.feature_extractor = VisualFeatureExtractor(
            device='cuda' if use_gpu else 'cpu'
        )
        self.clusterer = ImageClusterer()
        self.similarity_analyzer = SimilarityAnalyzer()
        self.quality_analyzer = QualityAnalyzer()
        self.weight_calculator = VisualWeightCalculator()
        
        # Data storage
        self.metadata_list: List[ImageMetadata] = []
        self.features: Optional[np.ndarray] = None
        self.cluster_labels: Optional[np.ndarray] = None
        self.weights: List[float] = []
        
    def process_images(self, blur_threshold: float = 50.0):
        """Step 1: Extract metadata and filter blurry images"""
        print("\n=== Step 1: Extracting Metadata & Filtering Blur ===")
        all_metadata = self.metadata_extractor.extract_batch(str(self.image_dir))
        
        # Filter blurry images
        self.metadata_list = []
        for meta in tqdm(all_metadata, desc="Checking blur"):
            sharpness = self.quality_analyzer.assess_sharpness(meta.filepath)
            
            # Simple heuristic: images with variance < threshold are likely blurry
            # Adjust threshold as needed (e.g., 50-100 is conservative)
            if sharpness > blur_threshold:
                self.metadata_list.append(meta)
            else:
                # print(f"  Skipped blurry image: {meta.filename} (Score: {sharpness:.1f})")
                pass

        print(f"Processed {len(self.metadata_list)} valid images (removed {len(all_metadata) - len(self.metadata_list)} blurry)")
        
        if not self.metadata_list:
            raise ValueError(f"No valid images found in {self.image_dir}")
        
        # Order by time
        self.metadata_list = self.storyline_constructor.order_by_time(self.metadata_list)
        
        return self
    
    def extract_visual_features(self):
        """Step 2: Extract visual features"""
        print("\n=== Step 2: Extracting Visual Features ===")
        image_paths = [m.filepath for m in self.metadata_list]
        
        print("Computing visual embeddings (this may take a while)...")
        feature_list = []
        for path in tqdm(image_paths, desc="Extracting features"):
            features = self.feature_extractor.extract_features(path)
            feature_list.append(features)
        
        self.features = np.array(feature_list)
        return self
    
    def cluster_images(self, n_clusters: Optional[int] = None):
        """Step 3: Cluster images by visual similarity"""
        print("\n=== Step 3: Clustering Images ===")
        
        if n_clusters:
            self.cluster_labels = self.clusterer.cluster_kmeans(self.features, n_clusters)
        else:
            self.cluster_labels = self.clusterer.auto_cluster(self.features)
        
        return self
    
    def compute_visual_weights(self):
        """Step 4: Compute visual importance weights"""
        print("\n=== Step 4: Computing Visual Weights ===")
        
        self.weights = []
        
        for i, metadata in enumerate(tqdm(self.metadata_list, desc="Computing weights")):
            # Assess quality metrics (re-calculating strictly for weight now)
            sharpness = self.quality_analyzer.assess_sharpness(metadata.filepath)
            face_count = self.quality_analyzer.detect_faces(metadata.filepath)
            
            # Compute uniqueness based on cluster size
            cluster_size = np.sum(self.cluster_labels == self.cluster_labels[i])
            uniqueness = 1.0 / (1.0 + cluster_size / 10.0) 
            
            # Calculate weight
            weight = self.weight_calculator.compute_weight(
                metadata, sharpness, face_count, uniqueness, cluster_size
            )
            self.weights.append(weight)
        
        return self

    def _detect_common_object(self) -> Optional[str]:
        """Detect the most common object/scene in the collection using CLIP"""
        try:
            import torch
            import open_clip
        except ImportError:
            print("Warning: open_clip not installed, cannot detect objects.")
            return None

        print("Analyzing image content for common themes...")
        
        # We need the model from the feature extractor
        # Accessing private attribute strictly for this helper
        if not hasattr(self.feature_extractor, 'model') or self.feature_extractor.model == "fallback":
             # Force load if not loaded
             self.feature_extractor._load_model()

        model = self.feature_extractor.model
        device = self.feature_extractor.device
        
        if model == "fallback":
            return None # Cannot do zero-shot with histogram

        # Encode text descriptions
        tokenizer = open_clip.get_tokenizer('ViT-B-32')
        text_tokens = tokenizer([f"a photo of a {obj}" for obj in COMMON_OBJECTS]).to(device)
        
        with torch.no_grad():
            text_features = model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
            # We already have image features in self.features (numpy)
            # Convert back to torch for similarity calculation
            image_features = torch.from_numpy(self.features).to(device).float()
            
            # Calculate similarity
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            
            # Get top prediction for each image
            top_probs, top_labels = similarity.cpu().topk(1, dim=-1)
            
            # Count occurrences
            detected_objects = [COMMON_OBJECTS[idx] for idx in top_labels.flatten().numpy()]
            
            # Find most common
            if detected_objects:
                most_common, count = Counter(detected_objects).most_common(1)[0]
                percentage = count / len(self.metadata_list)
                
                # If the most common object appears in at least 30% of photos, use it
                if percentage > 0.3:
                    return most_common.title() # e.g. "Beach"

        return None

    def _get_location_name(self) -> Optional[str]:
        """Helper to get location name from metadata"""
        if not HAS_GEOPY: return None
            
        lats = [m.gps_latitude for m in self.metadata_list if m.gps_latitude]
        lons = [m.gps_longitude for m in self.metadata_list if m.gps_longitude]
        
        if not lats: return None
            
        avg_lat = sum(lats) / len(lats)
        avg_lon = sum(lons) / len(lons)
        
        try:
            geolocator = Nominatim(user_agent="photobook_gen_v1")
            location = geolocator.reverse(f"{avg_lat}, {avg_lon}", language='en')
            if location and location.raw.get('address'):
                addr = location.raw['address']
                city = addr.get('city') or addr.get('town') or addr.get('village')
                country = addr.get('country')
                if city and country: return f"{city}, {country}"
                if country: return country
        except:
            pass
        return None

    def generate_photobook(self, output_filename, title, use_chapters):
        """Step 5: Generate final PDF photo book"""
        print("\n=== Step 5: Generating Photo Book ===")
        
        output_path = self.output_dir / output_filename
        template = PhotoBookTemplate("default")
        layout_engine = LayoutEngine(template)
        renderer = PDFRenderer(template)
        
        if use_chapters and self.cluster_labels is not None:
            chapters = []
            for cluster_id in sorted(set(self.cluster_labels)):
                cluster_indices = np.where(self.cluster_labels == cluster_id)[0]
                cluster_images = [self.metadata_list[i].filepath for i in cluster_indices]
                cluster_weights = [self.weights[i] for i in cluster_indices]
                
                # Sort by weight
                sorted_pairs = sorted(zip(cluster_images, cluster_weights), key=lambda x: x[1], reverse=True)
                pages = layout_engine.arrange_images([p[0] for p in sorted_pairs], [p[1] for p in sorted_pairs])
                chapters.append({'name': f'Chapter {cluster_id + 1}', 'pages': pages})
            
            renderer.render_with_chapters(chapters, str(output_path), title)
        else:
            pages = layout_engine.arrange_images([m.filepath for m in self.metadata_list], self.weights)
            renderer.render_photobook(pages, str(output_path), title)
        
        print(f"\n✓ Photo book generated: {output_path}")
        return str(output_path)
    
    def generate_full_pipeline(self,
                              output_filename: str = "photobook.pdf",
                              title: str = "My Photo Book",
                              n_clusters: Optional[int] = None,
                              use_chapters: bool = True) -> str:
        """Run complete pipeline"""
        print("=" * 60)
        print("AUTOMATED PHOTO BOOK GENERATION PIPELINE")
        print("=" * 60)
        
        # Run steps
        self.process_images() # Now includes blur filter
        self.extract_visual_features()
        self.cluster_images(n_clusters)
        self.compute_visual_weights()
        
        # NAMING LOGIC
        final_title = title
        final_filename = output_filename
        
        # 1. Try Location First
        location_name = self._get_location_name()
        
        if location_name:
            print(f"\n🌍 Detected Location: {location_name}")
            if title == "My Photo Book":
                final_title = f"Memories of {location_name}"
                safe_name = re.sub(r'[^a-zA-Z0-9]', '_', location_name)
                final_filename = f"{safe_name}_Photobook.pdf"
        
        # 2. If no location, try Object Detection
        else:
            common_object = self._detect_common_object()
            if common_object:
                print(f"\n🔍 Detected Common Theme: {common_object}")
                if title == "My Photo Book":
                    final_title = f"{common_object} Collection"
                    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', common_object)
                    final_filename = f"{safe_name}_Photobook.pdf"
            else:
                print("\nℹ️ No specific location or theme detected. Using default title.")

        # Update if changed
        if final_title != title:
            print(f"   -> Title updated to: {final_title}")
        if final_filename != output_filename:
            print(f"   -> Filename updated to: {final_filename}")

        pdf_path = self.generate_photobook(final_filename, final_title, use_chapters)
        
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE!")
        print("=" * 60)
        
        return pdf_path
    
    def get_statistics(self) -> Dict:
        """Get statistics about the processed collection"""
        stats = {
            'total_images': len(self.metadata_list),
            'images_with_timestamp': sum(1 for m in self.metadata_list if m.timestamp),
            'images_with_gps': sum(1 for m in self.metadata_list if m.gps_latitude),
            # This missing line caused the error:
            'images_with_camera_info': sum(1 for m in self.metadata_list if m.camera_make),
        }
        
        if self.cluster_labels is not None:
            stats['num_clusters'] = len(set(self.cluster_labels))
        
        if self.weights:
            stats['avg_weight'] = float(np.mean(self.weights))
            stats['max_weight'] = float(np.max(self.weights))
            stats['min_weight'] = float(np.min(self.weights))
        
        return stats