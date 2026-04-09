"""
Metadata Extraction Module (Student A)
Handles EXIF extraction, normalization, and time/location-based ordering
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import exifread
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
from pydantic import BaseModel


class ImageMetadata(BaseModel):
    """Structured metadata for an image"""
    filepath: str
    filename: str
    timestamp: Optional[datetime] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    orientation: Optional[int] = None
    has_metadata: bool = True
    
    class Config:
        arbitrary_types_allowed = True


class MetadataExtractor:
    """Extracts and normalizes EXIF metadata from images"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    
    def extract_metadata(self, image_path: str) -> ImageMetadata:
        """
        Extract comprehensive metadata from an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            ImageMetadata object with extracted information
        """
        filepath = Path(image_path)
        
        # Basic file info
        metadata = {
            'filepath': str(filepath.absolute()),
            'filename': filepath.name,
        }
        
        try:
            # Try PIL first for basic metadata
            with Image.open(image_path) as img:
                metadata['width'], metadata['height'] = img.size
                
                # Extract EXIF data
                exif_data = img._getexif()
                if exif_data:
                    metadata.update(self._parse_pil_exif(exif_data))
                else:
                    # Fallback to exifread
                    metadata.update(self._parse_exifread(image_path))
                    
        except Exception as e:
            # Fallback: use file modification time
            metadata['timestamp'] = datetime.fromtimestamp(os.path.getmtime(image_path))
            metadata['has_metadata'] = False
        
        # If still no timestamp, use file modification time
        if not metadata.get('timestamp'):
            metadata['timestamp'] = datetime.fromtimestamp(os.path.getmtime(image_path))
            
        return ImageMetadata(**metadata)
    
    def _parse_pil_exif(self, exif_data: dict) -> dict:
        """Parse EXIF data from PIL"""
        result = {}
        
        # Map EXIF tag IDs to names
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            
            if tag == 'DateTime' or tag == 'DateTimeOriginal':
                try:
                    result['timestamp'] = datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                except:
                    pass
            elif tag == 'Make':
                result['camera_make'] = str(value).strip()
            elif tag == 'Model':
                result['camera_model'] = str(value).strip()
            elif tag == 'Orientation':
                result['orientation'] = int(value)
            elif tag == 'GPSInfo':
                gps_data = self._parse_gps(value)
                if gps_data:
                    result.update(gps_data)
        
        return result
    
    def _parse_gps(self, gps_info: dict) -> Optional[dict]:
        """Parse GPS coordinates from EXIF GPS data"""
        try:
            gps_data = {}
            for tag_id, value in gps_info.items():
                tag = GPSTAGS.get(tag_id, tag_id)
                gps_data[tag] = value
            
            if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                lat = self._convert_to_degrees(gps_data['GPSLatitude'])
                lon = self._convert_to_degrees(gps_data['GPSLongitude'])
                
                if gps_data.get('GPSLatitudeRef') == 'S':
                    lat = -lat
                if gps_data.get('GPSLongitudeRef') == 'W':
                    lon = -lon
                    
                return {
                    'gps_latitude': lat,
                    'gps_longitude': lon
                }
        except:
            pass
        return None
    
    def _convert_to_degrees(self, value) -> float:
        """Convert GPS coordinates to decimal degrees"""
        d, m, s = value
        return float(d) + float(m) / 60.0 + float(s) / 3600.0
    
    def _parse_exifread(self, image_path: str) -> dict:
        """Fallback parser using exifread library"""
        result = {}
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)
                
                # Extract timestamp
                for date_tag in ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime']:
                    if date_tag in tags:
                        try:
                            date_str = str(tags[date_tag])
                            result['timestamp'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                            break
                        except:
                            pass
                
                # Extract camera info
                if 'Image Make' in tags:
                    result['camera_make'] = str(tags['Image Make']).strip()
                if 'Image Model' in tags:
                    result['camera_model'] = str(tags['Image Model']).strip()
                    
        except:
            pass
        return result
    
    def extract_batch(self, image_dir: str) -> List[ImageMetadata]:
        """
        Extract metadata from all images in a directory
        
        Args:
            image_dir: Directory containing images
            
        Returns:
            List of ImageMetadata objects
        """
        image_dir = Path(image_dir)
        metadata_list = []
        
        for file_path in image_dir.rglob('*'):
            if file_path.suffix.lower() in self.supported_formats:
                try:
                    metadata = self.extract_metadata(str(file_path))
                    metadata_list.append(metadata)
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")
        
        return metadata_list


class StorylineConstructor:
    """Constructs visual storylines from metadata"""
    
    def __init__(self):
        pass
    
    def order_by_time(self, metadata_list: List[ImageMetadata]) -> List[ImageMetadata]:
        """
        Order images chronologically
        
        Args:
            metadata_list: List of image metadata
            
        Returns:
            Sorted list of metadata
        """
        return sorted(metadata_list, key=lambda x: x.timestamp or datetime.min)
    
    def detect_time_gaps(self, 
                        metadata_list: List[ImageMetadata],
                        gap_threshold_hours: float = 6.0) -> List[List[ImageMetadata]]:
        """
        Detect time gaps to separate different events/chapters
        
        Args:
            metadata_list: Sorted list of metadata
            gap_threshold_hours: Minimum gap to consider a new chapter
            
        Returns:
            List of chapters (each chapter is a list of metadata)
        """
        if not metadata_list:
            return []
        
        sorted_metadata = self.order_by_time(metadata_list)
        chapters = []
        current_chapter = [sorted_metadata[0]]
        
        for i in range(1, len(sorted_metadata)):
            prev_time = sorted_metadata[i-1].timestamp
            curr_time = sorted_metadata[i].timestamp
            
            if prev_time and curr_time:
                time_diff = (curr_time - prev_time).total_seconds() / 3600.0
                
                if time_diff > gap_threshold_hours:
                    # Start new chapter
                    chapters.append(current_chapter)
                    current_chapter = [sorted_metadata[i]]
                else:
                    current_chapter.append(sorted_metadata[i])
            else:
                current_chapter.append(sorted_metadata[i])
        
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters
    
    def group_by_location(self, 
                         metadata_list: List[ImageMetadata],
                         distance_threshold_km: float = 10.0) -> Dict[str, List[ImageMetadata]]:
        """
        Group images by geographic proximity
        
        Args:
            metadata_list: List of metadata with GPS data
            distance_threshold_km: Maximum distance to consider same location
            
        Returns:
            Dictionary mapping location names to image lists
        """
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            """Calculate distance between two GPS coordinates in km"""
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r
        
        # Filter images with GPS data
        gps_metadata = [m for m in metadata_list if m.gps_latitude and m.gps_longitude]
        
        if not gps_metadata:
            return {'Unknown Location': metadata_list}
        
        # Simple clustering by distance
        location_groups = []
        
        for metadata in gps_metadata:
            added = False
            for group in location_groups:
                # Check if close to any image in this group
                sample = group[0]
                distance = haversine(
                    metadata.gps_longitude, metadata.gps_latitude,
                    sample.gps_longitude, sample.gps_latitude
                )
                if distance < distance_threshold_km:
                    group.append(metadata)
                    added = True
                    break
            
            if not added:
                location_groups.append([metadata])
        
        # Create result dictionary
        result = {}
        for i, group in enumerate(location_groups):
            location_name = f"Location_{i+1}"
            result[location_name] = group
        
        # Add images without GPS to unknown
        no_gps = [m for m in metadata_list if not (m.gps_latitude and m.gps_longitude)]
        if no_gps:
            result['Unknown Location'] = no_gps
        
        return result
