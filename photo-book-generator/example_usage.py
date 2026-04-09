#!/usr/bin/env python3
"""
Example usage script demonstrating the photo book generation system
"""

from photobook_generator import PhotoBookGenerator
from pathlib import Path


def example_basic_usage():
    """Basic usage example"""
    print("Example 1: Basic Photo Book Generation")
    print("-" * 50)
    
    # Create generator
    generator = PhotoBookGenerator(
        image_dir="./sample_images",  # Your image directory
        output_dir="./output"
    )
    
    # Generate photo book
    pdf_path = generator.generate_full_pipeline(
        output_filename="my_photobook.pdf",
        title="Summer Vacation 2024"
    )
    
    print(f"Photo book created: {pdf_path}")


def example_advanced_usage():
    """Advanced usage with step-by-step control"""
    print("\nExample 2: Advanced Usage with Custom Configuration")
    print("-" * 50)
    
    generator = PhotoBookGenerator(
        image_dir="./sample_images",
        output_dir="./output",
        use_gpu=False  # Set to True if you have CUDA-enabled GPU
    )
    
    # Step-by-step processing
    print("\n1. Processing images...")
    generator.process_images()
    
    print("\n2. Extracting visual features...")
    generator.extract_visual_features()
    
    print("\n3. Clustering images...")
    generator.cluster_images(n_clusters=5)  # Force 5 clusters
    
    print("\n4. Computing visual weights...")
    generator.compute_visual_weights()
    
    print("\n5. Generating photo book...")
    pdf_path = generator.generate_photobook(
        output_filename="custom_photobook.pdf",
        title="My Custom Photo Book",
        use_chapters=True
    )
    
    # Get statistics
    stats = generator.get_statistics()
    print("\nCollection Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def example_no_chapters():
    """Generate photo book without chapter divisions"""
    print("\nExample 3: Simple Sequential Layout (No Chapters)")
    print("-" * 50)
    
    generator = PhotoBookGenerator(
        image_dir="./sample_images",
        output_dir="./output"
    )
    
    pdf_path = generator.generate_full_pipeline(
        output_filename="sequential_photobook.pdf",
        title="Sequential Photo Book",
        use_chapters=False  # No chapter organization
    )
    
    print(f"Sequential photo book created: {pdf_path}")


if __name__ == "__main__":
    # Choose which example to run
    print("=" * 50)
    print("Photo Book Generator - Usage Examples")
    print("=" * 50)
    
    # Make sure to replace './sample_images' with your actual image directory
    
    # Uncomment the example you want to run:
    
    # example_basic_usage()
    # example_advanced_usage()
    # example_no_chapters()
    
    print("\nNote: Update the image_dir path in this script to your image folder")
    print("Then uncomment one of the example functions above to run it")
