#!/usr/bin/env python3
"""
Demo script - Creates sample images and generates a demo photo book
This helps test the system without needing actual photos
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime, timedelta
import piexif
import sys

def create_sample_images(output_dir: str = "./demo_images", n_images: int = 20):
    """
    Create sample images for testing
    
    Args:
        output_dir: Where to save sample images
        n_images: Number of images to create
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    print(f"Creating {n_images} sample images in {output_dir}...")
    
    colors = [
        ("Beach", (135, 206, 250)),    # Sky blue
        ("Forest", (34, 139, 34)),      # Forest green
        ("Sunset", (255, 140, 0)),      # Orange
        ("City", (128, 128, 128)),      # Gray
        ("Mountain", (139, 90, 43)),    # Brown
    ]
    
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(n_images):
        # Random theme
        theme_name, color = random.choice(colors)
        
        # Create image
        width, height = random.choice([(800, 600), (600, 800), (1024, 768)])
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)
        
        # Add some variation
        for _ in range(5):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            
            # FIX: Ensure coordinates are sorted (x1 < x2, y1 < y2)
            real_x1, real_x2 = sorted([x1, x2])
            real_y1, real_y2 = sorted([y1, y2])
            
            shade = tuple(max(0, c + random.randint(-50, 50)) for c in color)
            # Use the sorted coordinates
            draw.rectangle([real_x1, real_y1, real_x2, real_y2], fill=shade)
        
        # Add text
        try:
            text = f"{theme_name} #{i+1}"
            draw.text((20, 20), text, fill=(255, 255, 255))
        except:
            pass  # Font not available
        
        # Create EXIF with timestamp
        timestamp = base_time + timedelta(hours=i * 6)  # 6 hour gaps
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Demo Camera",
                piexif.ImageIFD.Model: b"Test Model",
            },
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: timestamp.strftime("%Y:%m:%d %H:%M:%S").encode(),
                piexif.ExifIFD.DateTimeDigitized: timestamp.strftime("%Y:%m:%d %H:%M:%S").encode(),
            }
        }
        
        exif_bytes = piexif.dump(exif_dict)
        
        # Save image
        filename = f"demo_image_{i+1:03d}.jpg"
        filepath = output_path / filename
        img.save(filepath, "JPEG", exif=exif_bytes, quality=95)
    
    print(f"✓ Created {n_images} sample images")
    return str(output_path)


def run_demo():
    """Run complete demo"""
    print("=" * 60)
    print("Photo Book Generator - Demo")
    print("=" * 60)
    
    # Create sample images
    print("\n1. Creating sample images...")
    try:
        image_dir = create_sample_images(n_images=15)
    except Exception as e:
        print(f"Error creating images: {e}")
        return 1
    
    # Generate photo book
    print("\n2. Generating photo book...")
    try:
        from photobook_generator import PhotoBookGenerator
    except ImportError as e:
        print(f"Error importing generator: {e}")
        print("Make sure you have created vision_module.py as instructed.")
        return 1
    
    generator = PhotoBookGenerator(
        image_dir=image_dir,
        output_dir="./demo_output"
    )
    
    try:
        pdf_path = generator.generate_full_pipeline(
            output_filename="demo_photobook.pdf",
            title="Demo Photo Book",
            use_chapters=True
        )
        
        # Show statistics
        stats = generator.get_statistics()
        print("\n3. Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "=" * 60)
        print("✅ Demo Complete!")
        print("=" * 60)
        print(f"\nDemo photo book: {pdf_path}")
        print(f"Sample images: {image_dir}")
        print("\nYou can now:")
        print("1. Check the generated PDF")
        print("2. Examine the sample images")
        print("3. Try with your own photos!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Check if vision_module.py exists")
        print("2. Install missing dependencies: pip install -r requirements.txt")
        return 1
    
    return 0


def cleanup_demo():
    """Remove demo files"""
    import shutil
    
    print("Cleaning up demo files...")
    
    dirs_to_remove = ["./demo_images", "./demo_output"]
    
    for dir_path in dirs_to_remove:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_path}")
    
    print("✓ Cleanup complete")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_demo()
    else:
        sys.exit(run_demo())