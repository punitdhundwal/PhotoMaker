#!/usr/bin/env python3
"""
Installation verification and system test script
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required = {
        'PIL': 'Pillow',
        'exifread': 'exifread',
        'piexif': 'piexif',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'networkx': 'networkx',
        'reportlab': 'reportlab',
        'typer': 'typer',
        'tqdm': 'tqdm',
        'pydantic': 'pydantic',
    }
    
    optional = {
        'torch': 'torch',
        'open_clip': 'open-clip-torch',
        'hdbscan': 'hdbscan',
    }
    
    missing = []
    
    # Check required packages
    for module, package in required.items():
        try:
            importlib.import_module(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (REQUIRED)")
            missing.append(package)
    
    # Check optional packages
    print("\nOptional packages (for enhanced features):")
    for module, package in optional.items():
        try:
            importlib.import_module(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ⚠ {package} (optional, will use fallback)")
    
    return len(missing) == 0


def check_modules():
    """Check if project modules are present"""
    print("\nChecking project modules...")
    
    modules = [
        'metadata_module',
        'vision_module',
        'layout_module',
        'photobook_generator',
    ]
    
    all_present = True
    for module in modules:
        module_file = Path(f"{module}.py")
        if module_file.exists():
            print(f"  ✓ {module}.py")
        else:
            print(f"  ✗ {module}.py (MISSING)")
            all_present = False
    
    return all_present


def run_basic_import_test():
    """Try importing main modules"""
    print("\nTesting module imports...")
    
    try:
        from metadata_module import MetadataExtractor
        print("  ✓ MetadataExtractor")
    except Exception as e:
        print(f"  ✗ MetadataExtractor: {e}")
        return False
    
    try:
        from vision_module import VisualFeatureExtractor
        print("  ✓ VisualFeatureExtractor")
    except Exception as e:
        print(f"  ✗ VisualFeatureExtractor: {e}")
        return False
    
    try:
        from layout_module import PhotoBookTemplate
        print("  ✓ PhotoBookTemplate")
    except Exception as e:
        print(f"  ✗ PhotoBookTemplate: {e}")
        return False
    
    try:
        from photobook_generator import PhotoBookGenerator
        print("  ✓ PhotoBookGenerator")
    except Exception as e:
        print(f"  ✗ PhotoBookGenerator: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Photo Book Generator - Installation Verification")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Project Modules", check_modules()))
    results.append(("Import Tests", run_basic_import_test()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All tests passed! System is ready to use.")
        print("\nTry running:")
        print("  python main.py --help")
        print("  python example_usage.py")
        return 0
    else:
        print("\n❌ Some tests failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
