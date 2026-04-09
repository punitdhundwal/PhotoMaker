#!/usr/bin/env python3
"""
Command-line interface for Photo Book Generator
"""

import typer
from pathlib import Path
from typing import Optional
import json

from photobook_generator import PhotoBookGenerator

app = typer.Typer(help="Automated Photo Book Generation System")


@app.command()
def generate(
    image_dir: str = typer.Argument(..., help="Directory containing images"),
    output_dir: str = typer.Option("./output", "--output-dir", "-o", help="Output directory"),
    output_filename: str = typer.Option("photobook.pdf", "--output", "-f", help="Output PDF filename"),
    title: str = typer.Option("My Photo Book", "--title", "-t", help="Photo book title"),
    n_clusters: Optional[int] = typer.Option(None, "--clusters", "-c", help="Number of clusters (auto if not specified)"),
    use_chapters: bool = typer.Option(True, "--chapters/--no-chapters", help="Organize into chapters"),
    use_gpu: bool = typer.Option(False, "--gpu/--no-gpu", help="Use GPU for feature extraction"),
):
    """
    Generate a photo book from a directory of images
    """
    # Validate input directory
    if not Path(image_dir).exists():
        typer.echo(f"Error: Image directory '{image_dir}' does not exist", err=True)
        raise typer.Exit(1)
    
    # Create generator
    generator = PhotoBookGenerator(
        image_dir=image_dir,
        output_dir=output_dir,
        use_gpu=use_gpu
    )
    
    # Run pipeline
    try:
        pdf_path = generator.generate_full_pipeline(
            output_filename=output_filename,
            title=title,
            n_clusters=n_clusters,
            use_chapters=use_chapters
        )
        
        # Show statistics
        stats = generator.get_statistics()
        typer.echo("\n📊 Collection Statistics:")
        typer.echo(f"  Total images: {stats['total_images']}")
        typer.echo(f"  Images with timestamp: {stats['images_with_timestamp']}")
        typer.echo(f"  Images with GPS: {stats['images_with_gps']}")
        typer.echo(f"  Images with camera info: {stats['images_with_camera_info']}")
        if 'num_clusters' in stats:
            typer.echo(f"  Number of clusters: {stats['num_clusters']}")
        
        typer.echo(f"\n✅ Success! Photo book saved to: {pdf_path}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def analyze(
    image_dir: str = typer.Argument(..., help="Directory containing images"),
    output_json: Optional[str] = typer.Option(None, "--output", "-o", help="Save analysis to JSON file"),
):
    """
    Analyze image collection without generating photo book
    """
    if not Path(image_dir).exists():
        typer.echo(f"Error: Image directory '{image_dir}' does not exist", err=True)
        raise typer.Exit(1)
    
    generator = PhotoBookGenerator(image_dir=image_dir)
    
    try:
        generator.process_images()
        generator.extract_visual_features()
        generator.cluster_images()
        generator.compute_visual_weights()
        
        stats = generator.get_statistics()
        
        typer.echo("\n📊 Image Collection Analysis:")
        typer.echo(f"  Total images: {stats['total_images']}")
        typer.echo(f"  Images with metadata: {stats['images_with_timestamp']}")
        typer.echo(f"  Images with GPS: {stats['images_with_gps']}")
        typer.echo(f"  Number of clusters: {stats.get('num_clusters', 'N/A')}")
        typer.echo(f"  Average quality weight: {stats.get('avg_weight', 0):.3f}")
        
        if output_json:
            with open(output_json, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            typer.echo(f"\n✅ Analysis saved to: {output_json}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information"""
    typer.echo("Photo Book Generator v1.0.0")
    typer.echo("Automated Visual Storytelling System")


if __name__ == "__main__":
    app()
