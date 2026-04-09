"""
Layout, Templates & PDF Output Module (Student C)
Handles visual weight computation, layout generation, and PDF rendering
With Dynamic Color Extraction AND Smart Decorations
"""

import math
import random
from typing import List, Dict, Tuple, Optional
import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from sklearn.cluster import KMeans
from metadata_module import ImageMetadata

# --- DECORATION ENGINE ---
class DecorationPainter:
    """Draws thematic elements (Flowers, Cameras, Bows) based on context"""
    
    def determine_style(self, title: str) -> str:
        t = title.lower()
        if any(x in t for x in ['screenshot', 'code', 'computer', 'tech', 'screen', 'game']):
            return "tech"
        elif any(x in t for x in ['nature', 'flower', 'garden', 'forest', 'park', 'spring']):
            return "nature"
        elif any(x in t for x in ['party', 'birthday', 'wedding', 'celebration', 'fun']):
            return "party"
        else:
            return "minimal"

    def draw_decorations(self, c: canvas.Canvas, style: str, width: float, height: float, theme_color):
        """Draws scattered decorations on the page background"""
        c.saveState()
        
        # Make decorations subtle
        c.setFillColor(theme_color.clone(alpha=0.15))
        c.setStrokeColor(theme_color.clone(alpha=0.15))
        
        # 1. TECH STYLE (Cameras & Crosshairs)
        if style == "tech":
            # Draw grid lines
            self._draw_grid(c, width, height)
            # Draw random Camera icons
            for _ in range(5):
                x = random.randint(50, int(width)-50)
                y = random.randint(50, int(height)-50)
                self._draw_camera_icon(c, x, y, size=30)

        # 2. NATURE STYLE (Flowers & Leaves)
        elif style == "nature":
            for _ in range(8):
                x = random.randint(30, int(width)-30)
                y = random.randint(30, int(height)-30)
                self._draw_flower_icon(c, x, y, size=random.randint(20, 40))

        # 3. PARTY STYLE (Bows & Confetti)
        elif style == "party":
            for _ in range(10):
                x = random.randint(30, int(width)-30)
                y = random.randint(30, int(height)-30)
                if random.random() > 0.5:
                    self._draw_bow_icon(c, x, y, size=30)
                else:
                    c.circle(x, y, random.randint(2, 6), fill=1, stroke=0)

        c.restoreState()

    def _draw_grid(self, c, w, h):
        """Draws technical looking grid dots"""
        step = 50
        for x in range(0, int(w), step):
            for y in range(0, int(h), step):
                if random.random() > 0.8: # Random missing dots
                    c.circle(x, y, 1, fill=1, stroke=0)
        # Corner brackets
        m = 20
        l = 40
        c.setLineWidth(2)
        # Top Left
        c.line(m, h-m, m+l, h-m)
        c.line(m, h-m, m, h-m-l)
        # Bottom Right
        c.line(w-m, m, w-m-l, m)
        c.line(w-m, m, w-m, m+l)

    def _draw_camera_icon(self, c, x, y, size):
        """Draws a simple camera symbol"""
        w = size
        h = size * 0.7
        # Body
        c.rect(x - w/2, y - h/2, w, h, fill=1, stroke=0)
        # Lens
        c.saveState()
        c.setFillColor(colors.white.clone(alpha=0.3)) # Lighter lens
        c.circle(x, y, h/2.5, fill=1, stroke=0)
        c.restoreState()
        # Flash bump
        c.rect(x, y + h/2, w/3, h/4, fill=1, stroke=0)

    def _draw_flower_icon(self, c, x, y, size):
        """Draws a 5-petal flower"""
        r = size / 3
        # Draw 5 petals
        for i in range(5):
            angle = (i * 2 * math.pi) / 5
            px = x + math.cos(angle) * r
            py = y + math.sin(angle) * r
            c.circle(px, py, r, fill=1, stroke=0)
        # Center
        c.saveState()
        c.setFillColor(colors.white.clone(alpha=0.5))
        c.circle(x, y, r/1.5, fill=1, stroke=0)
        c.restoreState()

    def _draw_bow_icon(self, c, x, y, size):
        """Draws a cute bow tie shape"""
        half = size / 2
        p = c.beginPath()
        # Left Triangle
        p.moveTo(x, y)
        p.lineTo(x - half, y + half/2)
        p.lineTo(x - half, y - half/2)
        p.close()
        # Right Triangle
        p.moveTo(x, y)
        p.lineTo(x + half, y + half/2)
        p.lineTo(x + half, y - half/2)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        # Center knot
        c.circle(x, y, size/5, fill=1, stroke=0)


# --- EXISTING CLASSES (Kept same, just integrated painter) ---

class ColorThemeGenerator:
    """Extracts dominant colors from images"""
    def extract_theme(self, image_paths: List[str], sample_size: int = 5) -> Dict:
        # (Same logic as before, just compact for brevity)
        try:
            pixel_data = []
            samples = image_paths if len(image_paths) < sample_size else np.random.choice(image_paths, sample_size, replace=False)
            for path in samples:
                with Image.open(path) as img:
                    img = img.resize((100, 100)).convert('RGB')
                    pixel_data.append(np.array(img).reshape(-1, 3))
            
            if not pixel_data: return self._get_fallback()
            
            kmeans = KMeans(n_clusters=5, n_init=5).fit(np.vstack(pixel_data))
            colors_sorted = sorted(kmeans.cluster_centers_.astype(int), key=lambda c: sum(c))
            
            darkest, lightest = colors_sorted[0], colors_sorted[-1]
            accent = max(kmeans.cluster_centers_, key=lambda c: max(c)-min(c))
            
            # Helper to convert
            def to_rl(c): return colors.Color(c[0]/255, c[1]/255, c[2]/255)

            if sum(darkest) < 150: # Dark Mode
                bg, txt = to_rl(darkest), to_rl(lightest)
            else: # Light Mode
                bg, txt = to_rl(lightest), to_rl(darkest)

            return {
                "bg_color": bg, "text_color": txt, "accent_color": to_rl(accent),
                "border_color": txt, "border_width": 2,
                "font_title": "Helvetica-Bold", "font_body": "Helvetica"
            }
        except: return self._get_fallback()

    def _get_fallback(self):
        return {"bg_color": colors.white, "text_color": colors.black, "accent_color": colors.red, "border_color": colors.black, "border_width": 1, "font_title": "Helvetica-Bold", "font_body": "Helvetica"}

class VisualWeightCalculator:
    def compute_weight(self, metadata, sharpness=0, face_count=0, uniqueness=0.5, cluster_size=1):
        # Simplified weight logic
        return min(sharpness/500, 1)*0.3 + min(face_count/5, 1)*0.3 + uniqueness*0.2 + (0.4 if metadata.timestamp else 0)*0.2

class PhotoBookTemplate:
    def __init__(self, name: str, page_size=A4):
        self.name, self.page_size = name, page_size
        self.width, self.height = page_size
        self.margin = 0.5 * inch
        self.usable_width = self.width - 2 * self.margin
        self.usable_height = self.height - 2 * self.margin
    
    def get_layout(self, layout_type: str) -> List[Tuple[float, float, float, float]]:
        m, uw, uh = self.margin, self.usable_width, self.usable_height
        # Standard layouts
        return {
            'single_full': [(m, m + 1.5*inch, uw, uh - 2.5*inch)],
            'single_portrait': [(self.width/2 - 3*inch, m + 1.5*inch, 6*inch, 7*inch)],
            'double_horizontal': [(m, m + 4.8*inch, uw, 3.5*inch), (m, m + 1.0*inch, uw, 3.5*inch)],
            'double_vertical': [(m, m + 2*inch, uw/2 - 0.1*inch, 5*inch), (m + uw/2 + 0.1*inch, m + 2*inch, uw/2 - 0.1*inch, 5*inch)],
            'triple': [(m, m + 5.5*inch, uw, 3*inch), (m, m + 2.0*inch, uw/2 - 0.1*inch, 3*inch), (m + uw/2 + 0.1*inch, m + 2.0*inch, uw/2 - 0.1*inch, 3*inch)],
            'grid_4': [(m, m + 5.2*inch, uw/2 - 0.1*inch, 3*inch), (m + uw/2 + 0.1*inch, m + 5.2*inch, uw/2 - 0.1*inch, 3*inch), (m, m + 1.8*inch, uw/2 - 0.1*inch, 3*inch), (m + uw/2 + 0.1*inch, m + 1.8*inch, uw/2 - 0.1*inch, 3*inch)]
        }.get(layout_type, [(m, m + 1.5*inch, uw, uh - 2.5*inch)])

class LayoutEngine:
    def __init__(self, template): self.template = template
    def arrange_images(self, image_paths, weights):
        pages = []
        i = 0
        while i < len(image_paths):
            remaining = len(image_paths) - i
            n = 1 if remaining == 1 or weights[i] > 0.8 else min(4, remaining)
            layout = {1: 'single_full', 2: 'double_horizontal', 3: 'triple', 4: 'grid_4'}.get(n, 'grid_4')
            pages.append({'images': image_paths[i:i+n], 'layout': layout, 'weights': weights[i:i+n]})
            i += n
        return pages

class PDFRenderer:
    """Render photo book to PDF with DYNAMIC style AND DECORATIONS"""
    
    def __init__(self, template: PhotoBookTemplate):
        self.template = template
        self.theme = None
        self.theme_gen = ColorThemeGenerator()
        self.painter = DecorationPainter() # Initialize our new painter

    def _draw_background(self, c: canvas.Canvas, title_for_style: str):
        # 1. Fill Color
        c.setFillColor(self.theme["bg_color"])
        c.rect(0, 0, self.template.width, self.template.height, fill=1, stroke=0)
        
        # 2. Draw Decorations based on Title
        # We determine style (tech/nature/party) from the title
        style = self.painter.determine_style(title_for_style)
        self.painter.draw_decorations(c, style, self.template.width, self.template.height, self.theme["accent_color"])

    def _draw_header_footer(self, c, title, page_num):
        w = self.template.width
        c.setStrokeColor(self.theme["accent_color"])
        c.setLineWidth(1)
        c.line(0.5*inch, 0.8*inch, w - 0.5*inch, 0.8*inch)
        c.setFont(self.theme["font_body"], 10)
        c.setFillColor(self.theme["text_color"])
        c.drawRightString(w - 0.5*inch, 0.5*inch, f"Page {page_num}")
        c.drawString(0.5*inch, 0.5*inch, title)

    def render_photobook(self, pages, output_path, title="Photo Book", chapters=None):
        all_images = []
        for p in pages: all_images.extend(p['images'])
        self.theme = self.theme_gen.extract_theme(all_images)
        
        c = canvas.Canvas(output_path, pagesize=self.template.page_size)
        self._render_title_page(c, title)
        c.showPage()
        
        for i, page in enumerate(pages):
            self._draw_background(c, title) # Pass title to trigger decorations
            self._render_page_content(c, page)
            self._draw_header_footer(c, title, i + 1)
            c.showPage()
        c.save()

    def render_with_chapters(self, chapters, output_path, title):
        all_images = []
        for ch in chapters:
            for p in ch['pages']: all_images.extend(p['images'])
        self.theme = self.theme_gen.extract_theme(all_images)
        
        c = canvas.Canvas(output_path, pagesize=self.template.page_size)
        self._render_title_page(c, title)
        c.showPage()
        
        page_count = 1
        for chapter in chapters:
            self._render_chapter_divider(c, chapter['name'], title)
            c.showPage()
            for page in chapter['pages']:
                self._draw_background(c, title) # Pass title here too
                self._render_page_content(c, page)
                self._draw_header_footer(c, title, page_count)
                c.showPage()
                page_count += 1
        c.save()

    def _render_title_page(self, c, title):
        self._draw_background(c, title)
        w, h = self.template.width, self.template.height
        c.setFillColor(self.theme["accent_color"])
        c.rect(0, h/2 - 60, w, 120, fill=1, stroke=0)
        c.setFont(self.theme["font_title"], 36)
        c.setFillColor(self.theme["bg_color"])
        c.drawCentredString(w/2, h/2 - 10, title)

    def _render_chapter_divider(self, c, name, title):
        self._draw_background(c, title)
        w, h = self.template.width, self.template.height
        c.setFont(self.theme["font_title"], 32)
        c.setFillColor(self.theme["accent_color"])
        c.drawCentredString(w/2, h/2, name)

    def _render_page_content(self, c, page):
        boxes = self.template.get_layout(page['layout'])
        for img_path, (x, y, w, h) in zip(page['images'], boxes):
            try: self._draw_image_fitted(c, img_path, x, y, w, h)
            except: pass

    def _draw_image_fitted(self, c, img_path, x, y, max_w, max_h):
        with Image.open(img_path) as img:
            iw, ih = img.size
            aspect = iw / ih
            if aspect > max_w / max_h: w = max_w; h = max_w / aspect
            else: h = max_h; w = max_h * aspect
            fx, fy = x + (max_w - w)/2, y + (max_h - h)/2
            
            # Shadow
            c.setFillColor(colors.black.clone(alpha=0.3))
            c.rect(fx + 4, fy - 4, w, h, fill=1, stroke=0)
            # Border
            c.setFillColor(self.theme["border_color"])
            b = self.theme["border_width"]
            c.rect(fx - b, fy - b, w + 2*b, h + 2*b, fill=1, stroke=0)
            
            c.drawImage(img_path, fx, fy, width=w, height=h, preserveAspectRatio=True)