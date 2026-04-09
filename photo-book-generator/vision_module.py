"""
Computer Vision & Clustering Module (Student B)
Handles visual feature extraction, similarity computation, and semantic clustering
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import cv2
import torch
from PIL import Image
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from metadata_module import ImageMetadata


class VisualFeatureExtractor:
    """Extract visual embeddings and features from images"""
    
    def __init__(self, model_name: str = 'ViT-B-32', device: Optional[str] = None):
        """
        Initialize feature extractor
        
        Args:
            model_name: CLIP model variant to use
            device: 'cuda', 'cpu', or None for auto-detection
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self._init_clip_model()
    
    def _init_clip_model(self):
        """Initialize CLIP model for embeddings"""
        try:
            import open_clip
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                self.model_name, 
                pretrained='openai'
            )
            self.model = self.model.to(self.device)
            self.model.eval()
            self.use_clip = True
        except Exception as e:
            print(f"Warning: Could not load CLIP model, using basic features: {e}")
            self.use_clip = False
    
    def extract_features(self, image_path: str) -> np.ndarray:
        """
        Extract visual features from an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Feature vector as numpy array
        """
        if self.use_clip:
            return self._extract_clip_features(image_path)
        else:
            return self._extract_basic_features(image_path)
    
    def _extract_clip_features(self, image_path: str) -> np.ndarray:
        """Extract features using CLIP model"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                features = self.model.encode_image(image_input)
                features = features.cpu().numpy().flatten()
                # Normalize
                features = features / np.linalg.norm(features)
            
            return features
        except Exception as e:
            print(f"Error extracting CLIP features for {image_path}: {e}")
            return self._extract_basic_features(image_path)
    
    def _extract_basic_features(self, image_path: str) -> np.ndarray:
        """Fallback: Extract basic color histogram features"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return np.zeros(512)
            
            # Resize for consistent processing
            img = cv2.resize(img, (224, 224))
            
            # Color histograms (HSV)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hist_h = cv2.calcHist([hsv], [0], None, [32], [0, 180])
            hist_s = cv2.calcHist([hsv], [1], None, [32], [0, 256])
            hist_v = cv2.calcHist([hsv], [2], None, [32], [0, 256])
            
            # Concatenate and normalize
            features = np.concatenate([hist_h.flatten(), hist_s.flatten(), hist_v.flatten()])
            features = features / (np.linalg.norm(features) + 1e-7)
            
            # Pad to 512 dimensions
            if len(features) < 512:
                features = np.pad(features, (0, 512 - len(features)))
            else:
                features = features[:512]
            
            return features
        except Exception as e:
            print(f"Error extracting basic features for {image_path}: {e}")
            return np.zeros(512)
    
    def extract_batch(self, image_paths: List[str]) -> np.ndarray:
        """
        Extract features from multiple images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Matrix of features (n_images x feature_dim)
        """
        features_list = []
        for path in image_paths:
            features = self.extract_features(path)
            features_list.append(features)
        
        return np.array(features_list)


class ImageClusterer:
    """Cluster images based on visual similarity"""
    
    def __init__(self):
        pass
    
    def cluster_kmeans(self, 
                      features: np.ndarray,
                      n_clusters: int = 5) -> np.ndarray:
        """
        Cluster images using K-Means
        
        Args:
            features: Feature matrix (n_images x feature_dim)
            n_clusters: Number of clusters
            
        Returns:
            Cluster labels for each image
        """
        if len(features) < n_clusters:
            n_clusters = max(1, len(features) // 2)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features)
        return labels
    
    def cluster_dbscan(self, 
                       features: np.ndarray,
                       eps: float = 0.3,
                       min_samples: int = 2) -> np.ndarray:
        """
        Cluster images using DBSCAN (density-based)
        
        Args:
            features: Feature matrix
            eps: Maximum distance between samples in same cluster
            min_samples: Minimum samples in a neighborhood
            
        Returns:
            Cluster labels (-1 for noise/outliers)
        """
        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        labels = dbscan.fit_predict(features)
        return labels
    
    def auto_cluster(self, features: np.ndarray) -> np.ndarray:
        """
        Automatically determine best clustering approach
        
        Args:
            features: Feature matrix
            
        Returns:
            Cluster labels
        """
        n_images = len(features)
        
        if n_images < 5:
            return np.zeros(n_images, dtype=int)
        elif n_images < 20:
            n_clusters = min(3, n_images // 3)
            return self.cluster_kmeans(features, n_clusters)
        else:
            # Try DBSCAN first
            labels = self.cluster_dbscan(features)
            n_clusters_found = len(set(labels)) - (1 if -1 in labels else 0)
            
            # If too few or too many clusters, use K-Means
            if n_clusters_found < 2 or n_clusters_found > n_images // 3:
                n_clusters = max(3, min(8, n_images // 5))
                return self.cluster_kmeans(features, n_clusters)
            
            return labels
    
    def label_clusters_semantic(self, 
                                features: np.ndarray,
                                labels: np.ndarray,
                                metadata_list: List[ImageMetadata]) -> Dict[int, str]:
        """
        Assign semantic labels to clusters based on common characteristics
        
        Args:
            features: Feature matrix
            labels: Cluster assignments
            metadata_list: List of image metadata
            
        Returns:
            Dictionary mapping cluster IDs to semantic labels
        """
        cluster_labels = {}
        unique_labels = set(labels)
        
        for cluster_id in unique_labels:
            if cluster_id == -1:  # Noise in DBSCAN
                cluster_labels[cluster_id] = "Miscellaneous"
                continue
            
            # Get images in this cluster
            cluster_indices = np.where(labels == cluster_id)[0]
            cluster_metadata = [metadata_list[i] for i in cluster_indices]
            
            # Analyze temporal patterns
            timestamps = [m.timestamp for m in cluster_metadata if m.timestamp]
            if timestamps:
                timestamps.sort()
                time_span = (timestamps[-1] - timestamps[0]).days
                
                if time_span <= 1:
                    label = f"Event_{cluster_id+1}"
                elif time_span <= 7:
                    label = f"Week_{cluster_id+1}"
                else:
                    label = f"Period_{cluster_id+1}"
            else:
                label = f"Group_{cluster_id+1}"
            
            cluster_labels[cluster_id] = label
        
        return cluster_labels


class SimilarityAnalyzer:
    """Analyze visual similarity and construct similarity graphs"""
    
    def __init__(self):
        pass
    
    def compute_similarity_matrix(self, features: np.ndarray) -> np.ndarray:
        """
        Compute pairwise similarity matrix
        
        Args:
            features: Feature matrix (n_images x feature_dim)
            
        Returns:
            Similarity matrix (n_images x n_images)
        """
        similarity = cosine_similarity(features)
        return similarity
    
    def build_similarity_graph(self,
                              features: np.ndarray,
                              threshold: float = 0.5) -> nx.Graph:
        """
        Build a graph where edges connect similar images
        
        Args:
            features: Feature matrix
            threshold: Minimum similarity to create an edge
            
        Returns:
            NetworkX graph
        """
        similarity = self.compute_similarity_matrix(features)
        n_images = len(features)
        
        G = nx.Graph()
        G.add_nodes_from(range(n_images))
        
        for i in range(n_images):
            for j in range(i+1, n_images):
                if similarity[i, j] >= threshold:
                    G.add_edge(i, j, weight=similarity[i, j])
        
        return G
    
    def find_representative_images(self,
                                  features: np.ndarray,
                                  labels: np.ndarray,
                                  n_per_cluster: int = 3) -> Dict[int, List[int]]:
        """
        Find most representative images for each cluster
        
        Args:
            features: Feature matrix
            labels: Cluster labels
            n_per_cluster: Number of representatives per cluster
            
        Returns:
            Dictionary mapping cluster ID to list of image indices
        """
        representatives = {}
        
        for cluster_id in set(labels):
            cluster_indices = np.where(labels == cluster_id)[0]
            cluster_features = features[cluster_indices]
            
            if len(cluster_indices) <= n_per_cluster:
                representatives[cluster_id] = cluster_indices.tolist()
                continue
            
            # Find images closest to cluster centroid
            centroid = cluster_features.mean(axis=0)
            distances = np.linalg.norm(cluster_features - centroid, axis=1)
            
            # Get indices of closest images
            closest_indices = cluster_indices[np.argsort(distances)[:n_per_cluster]]
            representatives[cluster_id] = closest_indices.tolist()
        
        return representatives
    
    def infer_order_from_similarity(self,
                                   features: np.ndarray,
                                   start_idx: int = 0) -> List[int]:
        """
        Infer ordering of images based on visual similarity (narrative flow)
        
        Args:
            features: Feature matrix
            start_idx: Starting image index
            
        Returns:
            List of image indices in inferred order
        """
        n_images = len(features)
        visited = set()
        order = [start_idx]
        visited.add(start_idx)
        
        current_idx = start_idx
        
        while len(visited) < n_images:
            # Find most similar unvisited image
            similarities = []
            for i in range(n_images):
                if i not in visited:
                    sim = cosine_similarity(
                        features[current_idx].reshape(1, -1),
                        features[i].reshape(1, -1)
                    )[0, 0]
                    similarities.append((i, sim))
            
            if not similarities:
                # No more connected images, pick random unvisited
                remaining = set(range(n_images)) - visited
                if remaining:
                    next_idx = remaining.pop()
                else:
                    break
            else:
                # Pick most similar
                next_idx = max(similarities, key=lambda x: x[1])[0]
            
            order.append(next_idx)
            visited.add(next_idx)
            current_idx = next_idx
        
        return order


class QualityAnalyzer:
    """Analyze technical quality of images"""
    
    def __init__(self):
        pass
    
    def assess_sharpness(self, image_path: str) -> float:
        """
        Assess image sharpness using Laplacian variance
        
        Args:
            image_path: Path to image
            
        Returns:
            Sharpness score (higher is sharper)
        """
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return 0.0
            
            # Resize for consistent comparison
            img = cv2.resize(img, (500, 500))
            laplacian = cv2.Laplacian(img, cv2.CV_64F)
            score = laplacian.var()
            return float(score)
        except:
            return 0.0
    
    def detect_faces(self, image_path: str) -> int:
        """
        Detect number of faces in image
        
        Args:
            image_path: Path to image
            
        Returns:
            Number of faces detected
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return 0
            
            # Use Haar Cascade for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            return len(faces)
        except:
            return 0
