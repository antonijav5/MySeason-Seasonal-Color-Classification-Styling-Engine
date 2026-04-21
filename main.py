from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse, RoundedRectangle, Line, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
import cv2
import numpy as np
from sklearn.cluster import KMeans
import colorsys
import os

Window.clearcolor = (0.96, 0.96, 0.98, 1)

# ─────────────────────────────────────────
#  SEASON PALETTE DATABASE
#  Sources: The Concept Wardrobe, Elemental Colour, Kettlewell
#  Each season has ~20 signature HEX colors from real palettes
# ─────────────────────────────────────────

SEASON_PALETTES = {
    "Light Spring": [
        # Warm, light, delicate — peachy pinks, warm creams, light corals
        "#F9C6B0", "#F4A88A", "#F2C4CE", "#F7B2A0", "#FADADD",
        "#F9E4B7", "#FFF0C8", "#E8F5C8", "#B8E0C8", "#A8D8B0",
        "#F5C5A3", "#FDEBD0", "#F8BBD0", "#FFE0B2", "#DCEDC8",
        "#F48FB1", "#FFCCBC", "#FFF9C4", "#C8E6C9", "#B2EBF2",
    ],
    "True Spring": [
        # Warm, fresh, vivid — golden yellows, warm greens, bright corals
        "#FF6B35", "#FF8C42", "#FFA726", "#FFD54F", "#A5D63F",
        "#66BB6A", "#26A69A", "#FF7043", "#FFAB40", "#D4E157",
        "#FF5722", "#FFC107", "#CDDC39", "#4CAF50", "#00BCD4",
        "#FF6F00", "#F9A825", "#558B2F", "#00838F", "#EF6C00",
    ],
    "Bright Spring": [
        # Warm+cool, clear, high contrast — electric, saturated
        "#FF1744", "#FF4081", "#FF6D00", "#FFEA00", "#00E676",
        "#00B0FF", "#D500F9", "#FF3D00", "#F50057", "#C6FF00",
        "#1DE9B6", "#00E5FF", "#FF6E40", "#FFFF00", "#69F0AE",
        "#FF4081", "#E040FB", "#40C4FF", "#FF6D00", "#B2FF59",
    ],
    "Light Summer": [
        # Cool, light, airy — powder blue, lavender, soft rose
        "#B3D9F2", "#C5CAE9", "#E1BEE7", "#F8BBD0", "#BBDEFB",
        "#D1C4E9", "#FCE4EC", "#E3F2FD", "#EDE7F6", "#F3E5F5",
        "#B2EBF2", "#C8E6C9", "#F0F4C3", "#DCEDC8", "#CFD8DC",
        "#90CAF9", "#9FA8DA", "#CE93D8", "#F48FB1", "#80DEEA",
    ],
    "True Summer": [
        # Cool, muted, rosy — dusty rose, soft blue, muted lavender
        "#9E8FA3", "#8B7D8E", "#A67B9B", "#7B8FA6", "#8FA69E",
        "#B08EA0", "#7494A8", "#9AA894", "#A89AA4", "#7D9E9A",
        "#C4A0B0", "#8499A8", "#A8B899", "#9490A8", "#A89088",
        "#D4A0B0", "#88A4B8", "#B4C4A4", "#A090B4", "#C4A898",
    ],
    "Soft Summer": [
        # Cool, very muted, grayed — cocoa rose, dusty blue, greyed lilac
        "#9E8C8C", "#8C9EA0", "#9E9A8C", "#8C8E9E", "#A09090",
        "#8C9E96", "#968C9E", "#9E9488", "#889E94", "#9A8E9A",
        "#B0A0A0", "#A0B0B0", "#B0B0A0", "#A0A0B0", "#B0A8A0",
        "#A89898", "#98A8A8", "#A8A898", "#9898A8", "#A8A098",
    ],
    "Soft Autumn": [
        # Warm, muted, earthy — camel, warm taupe, muted terracotta
        "#C4956A", "#B8845A", "#C4A882", "#8C7055", "#B89878",
        "#A88068", "#C4B090", "#907060", "#B8A080", "#786050",
        "#D4A878", "#A09070", "#C8B898", "#887060", "#C0A888",
        "#BCA080", "#907868", "#C4AC88", "#886858", "#B89870",
    ],
    "True Autumn": [
        # Warm, rich, earthy — rust, olive, warm brown, pumpkin
        "#C0392B", "#E67E22", "#D35400", "#8B4513", "#A0522D",
        "#CD853F", "#B8860B", "#6B8E23", "#556B2F", "#8B6914",
        "#CC5500", "#B7410E", "#A0522D", "#8B7355", "#DAA520",
        "#C04000", "#8B4513", "#D2691E", "#6B8E23", "#BC8F5F",
    ],
    "Dark Autumn": [
        # Warm, deep, intense — burgundy, dark olive, chocolate
        "#4A0E0E", "#6B2D2D", "#8B4513", "#4A3728", "#5C4033",
        "#3D4A1A", "#4A3D1A", "#6B4226", "#2D4A3E", "#4A3520",
        "#7B3B2A", "#3B4A1E", "#5A3825", "#2E4A3A", "#6B4030",
        "#8B2020", "#4A5020", "#6A3020", "#305040", "#7A4828",
    ],
    "Bright Winter": [
        # Cool, clear, high contrast — electric blue, hot pink, pure white
        "#0000FF", "#FF0080", "#00FF80", "#FF4500", "#8000FF",
        "#00BFFF", "#FF1493", "#00FF7F", "#FF6347", "#7B68EE",
        "#0080FF", "#FF007F", "#00FFD1", "#FF3300", "#6600FF",
        "#00A8FF", "#FF0066", "#00FF99", "#FF2200", "#5500FF",
    ],
    "True Winter": [
        # Cool, sharp, dramatic — navy, pure white, black, icy pink
        "#0D1B4B", "#1A237E", "#283593", "#3949AB", "#FFFFFF",
        "#212121", "#37474F", "#B0BEC5", "#FF80AB", "#EA80FC",
        "#C62828", "#00838F", "#00695C", "#1565C0", "#6A1B9A",
        "#880E4F", "#01579B", "#006064", "#1B5E20", "#311B92",
    ],
    "Dark Winter": [
        # Cool, deep, dark — deep plum, dark navy, black cherry
        "#1A0A2E", "#0D1B2E", "#1A0A1A", "#0D1A0D", "#2E0D1A",
        "#1A1A2E", "#0A1A2E", "#2E1A1A", "#1A2E1A", "#2E1A2E",
        "#2D0A3D", "#0A2D3D", "#3D0A2D", "#0A3D2D", "#2D2D0A",
        "#1E0A3A", "#0A1E3A", "#3A0A1E", "#0A3A1E", "#1E1E0A",
    ],
}

SEASON_INFO = {
    "Light Spring":  {"icon": "icons/light_spring.png",  "desc": "Warm • Light • Delicate",     "color": (1.00, 0.85, 0.88), "gradient": [(1.0,0.82,0.86),(1.0,0.95,0.70),(0.85,1.0,0.90)]},
    "True Spring":   {"icon": "icons/true_spring.png",   "desc": "Warm • Fresh • Vivid",         "color": (1.00, 0.78, 0.40), "gradient": [(1.0,0.60,0.30),(1.0,0.85,0.20),(0.60,0.90,0.40)]},
    "Bright Spring": {"icon": "icons/bright_spring.png", "desc": "Warm • Clear • Contrasted",    "color": (1.00, 0.55, 0.35), "gradient": [(1.0,0.30,0.35),(1.0,0.80,0.10),(0.20,0.90,0.75)]},
    "Light Summer":  {"icon": "icons/light_summer.png",  "desc": "Cool • Light • Gentle",        "color": (0.78, 0.88, 1.00), "gradient": [(0.82,0.90,1.00),(0.92,0.88,0.98),(0.88,0.95,1.00)]},
    "True Summer":   {"icon": "icons/true_summer.png",   "desc": "Cool • Muted • Rosy",          "color": (0.60, 0.75, 0.90), "gradient": [(0.55,0.70,0.88),(0.70,0.78,0.92),(0.80,0.85,0.95)]},
    "Soft Summer":   {"icon": "icons/soft_summer.png",   "desc": "Cool • Muted • Grayed",        "color": (0.65, 0.72, 0.80), "gradient": [(0.60,0.68,0.75),(0.72,0.75,0.82),(0.82,0.85,0.90)]},
    "Soft Autumn":   {"icon": "icons/soft_autumn.png",   "desc": "Warm • Muted • Earthy",        "color": (0.85, 0.70, 0.55), "gradient": [(0.90,0.72,0.55),(0.80,0.65,0.50),(0.70,0.55,0.40)]},
    "True Autumn":   {"icon": "icons/true_autumn.png",   "desc": "Warm • Rich • Earthy",         "color": (0.80, 0.45, 0.20), "gradient": [(0.90,0.50,0.20),(0.75,0.40,0.15),(0.60,0.35,0.10)]},
    "Dark Autumn":   {"icon": "icons/dark_autumn.png",   "desc": "Warm • Deep • Intense",        "color": (0.55, 0.30, 0.15), "gradient": [(0.65,0.35,0.15),(0.45,0.25,0.10),(0.30,0.18,0.08)]},
    "Bright Winter": {"icon": "icons/bright_winter.png", "desc": "Cool • Clear • Contrasted",    "color": (0.30, 0.65, 1.00), "gradient": [(0.20,0.55,1.00),(0.50,0.75,1.00),(0.80,0.85,1.00)]},
    "True Winter":   {"icon": "icons/true_winter.png",   "desc": "Cool • Sharp • Dramatic",      "color": (0.35, 0.40, 0.75), "gradient": [(0.20,0.30,0.70),(0.40,0.50,0.85),(0.75,0.80,1.00)]},
    "Dark Winter":   {"icon": "icons/dark_winter.png",   "desc": "Cool • Deep • Dark",           "color": (0.20, 0.20, 0.40), "gradient": [(0.15,0.18,0.35),(0.25,0.25,0.50),(0.40,0.40,0.65)]},
}


# ─────────────────────────────────────────
#  PALETTE-BASED CLASSIFIER
# ─────────────────────────────────────────

def hex_to_rgb(hex_color):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        return None
    try:
        return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    except:
        return None


def rgb_to_lab(r, g, b):
    """Convert RGB to CIE Lab for perceptual color distance"""
    # Normalize
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # Linearize
    def linearize(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = linearize(r), linearize(g), linearize(b)

    # RGB to XYZ (D65)
    X = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    Y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    Z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    # Normalize by D65
    X, Y, Z = X / 0.95047, Y / 1.00000, Z / 1.08883

    # XYZ to Lab
    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    L = 116 * f(Y) - 16
    a = 500 * (f(X) - f(Y))
    b_val = 200 * (f(Y) - f(Z))

    return L, a, b_val


def color_distance_lab(r1, g1, b1, r2, g2, b2):
    """Perceptual color distance using CIE76 in Lab space"""
    L1, a1, b1v = rgb_to_lab(r1, g1, b1)
    L2, a2, b2v = rgb_to_lab(r2, g2, b2)
    return ((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1v - b2v) ** 2) ** 0.5


def classify_12_seasons(r, g, b):
    """
    Palette proximity classifier.

    For each season, compute the average distance from the input color
    to the closest N palette swatches.
    Closer = higher score.

    Also adds HSV-based scoring as a secondary signal.
    """

    # ── STEP 1: Palette proximity (primary signal) ──
    proximity_scores = {}

    for season, palette_hexes in SEASON_PALETTES.items():
        distances = []
        for hex_val in palette_hexes:
            rgb2 = hex_to_rgb(hex_val)
            if rgb2:
                d = color_distance_lab(r, g, b, rgb2[0], rgb2[1], rgb2[2])
                distances.append(d)

        distances.sort()
        # Use closest 5 swatches — average proximity
        top_n = distances[:5]
        avg_dist = sum(top_n) / len(top_n) if top_n else 999

        # Convert distance to score: closer = higher
        proximity_scores[season] = avg_dist

    # Normalize: invert so lower distance = higher score
    max_dist = max(proximity_scores.values())
    palette_score = {
        k: (max_dist - v) / max_dist * 20
        for k, v in proximity_scores.items()
    }

    # ── STEP 2: HSV analytical scoring (secondary signal) ──
    r1, g1, b1_n = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r1, g1, b1_n)
    hue = h * 360
    sat = s
    val = v

    warm  = (0 <= hue <= 55) or (330 <= hue <= 360)
    cool  = not warm
    deep  = val < 0.38
    light = val > 0.70
    clear = sat > 0.55
    soft  = sat < 0.40
    very_deep  = val < 0.25
    very_light = val > 0.85
    very_clear = sat > 0.75
    very_soft  = sat < 0.25

    hsv_scores = {k: 0.0 for k in SEASON_INFO}

    # Temperature — strong signal
    if warm:
        for k in ["Light Spring","True Spring","Bright Spring","Soft Autumn","True Autumn","Dark Autumn"]:
            hsv_scores[k] += 3.0
    if cool:
        for k in ["Light Summer","True Summer","Soft Summer","Bright Winter","True Winter","Dark Winter"]:
            hsv_scores[k] += 3.0

    # Value
    if very_light:
        hsv_scores["Light Spring"]  += 3.0
        hsv_scores["Light Summer"]  += 3.0
    elif light:
        hsv_scores["Light Spring"]  += 2.0
        hsv_scores["Light Summer"]  += 2.0
        hsv_scores["Bright Spring"] += 1.0
        hsv_scores["Bright Winter"] += 1.0

    if very_deep:
        hsv_scores["Dark Autumn"]   += 3.0
        hsv_scores["Dark Winter"]   += 3.0
    elif deep:
        hsv_scores["Dark Autumn"]   += 2.0
        hsv_scores["Dark Winter"]   += 2.0
        hsv_scores["True Autumn"]   += 1.0
        hsv_scores["True Winter"]   += 1.0

    if 0.38 <= val <= 0.70:
        for k in ["True Spring","True Summer","True Autumn","True Winter"]:
            hsv_scores[k] += 1.0

    # Chroma
    if very_clear:
        hsv_scores["Bright Spring"] += 3.0
        hsv_scores["Bright Winter"] += 3.0
    elif clear:
        hsv_scores["Bright Spring"] += 2.0
        hsv_scores["Bright Winter"] += 2.0
        hsv_scores["True Spring"]   += 1.0
        hsv_scores["True Winter"]   += 1.0
        hsv_scores["True Autumn"]   += 1.0

    if very_soft:
        hsv_scores["Soft Summer"]   += 3.0
        hsv_scores["Soft Autumn"]   += 3.0
    elif soft:
        hsv_scores["Soft Summer"]   += 2.0
        hsv_scores["Soft Autumn"]   += 2.0
        hsv_scores["Light Summer"]  += 1.0
        hsv_scores["Light Spring"]  += 1.0

    # Fine combinations
    if warm and very_deep:  hsv_scores["Dark Autumn"]   += 3.0
    if cool and very_deep:  hsv_scores["Dark Winter"]   += 3.0
    if warm and deep:       hsv_scores["Dark Autumn"]   += 2.0; hsv_scores["True Autumn"]  += 1.0
    if cool and deep and clear:     hsv_scores["Dark Winter"]   += 3.0; hsv_scores["True Winter"]  += 1.0
    if cool and deep and not clear: hsv_scores["True Winter"]   += 2.0; hsv_scores["Dark Winter"]  += 1.0
    if cool and very_clear: hsv_scores["Bright Winter"] += 3.0
    if warm and very_clear: hsv_scores["Bright Spring"] += 3.0
    if cool and clear:      hsv_scores["Bright Winter"] += 2.0; hsv_scores["True Winter"]  += 1.0
    if warm and clear:      hsv_scores["Bright Spring"] += 2.0; hsv_scores["True Spring"]  += 1.0
    if cool and light:      hsv_scores["Light Summer"]  += 2.0
    if warm and light:      hsv_scores["Light Spring"]  += 2.0
    if warm and soft:       hsv_scores["Soft Autumn"]   += 2.0
    if cool and soft:       hsv_scores["Soft Summer"]   += 2.0

    # Hue specifics
    if 0   <= hue <= 20:   hsv_scores["True Autumn"] += 1.0; hsv_scores["Dark Autumn"]  += 1.0  # red-orange
    if 20  <= hue <= 50:   hsv_scores["True Autumn"] += 1.0; hsv_scores["True Spring"]  += 0.5  # orange-gold
    if 50  <= hue <= 80:   hsv_scores["True Spring"] += 1.0; hsv_scores["Light Spring"] += 0.5  # yellow-green
    if 80  <= hue <= 150:  hsv_scores["True Autumn"] += 0.5; hsv_scores["True Spring"]  += 0.5  # green
    if 180 <= hue <= 220:  hsv_scores["True Summer"] += 1.0; hsv_scores["Light Summer"] += 0.5  # blue-cyan
    if 220 <= hue <= 270:  hsv_scores["True Winter"] += 1.0; hsv_scores["Dark Winter"]  += 0.5  # blue-violet
    if 270 <= hue <= 320:  hsv_scores["True Summer"] += 1.0; hsv_scores["True Winter"]  += 0.5  # violet-magenta
    if 320 <= hue <= 360:  hsv_scores["True Winter"] += 1.0; hsv_scores["Dark Winter"]  += 0.5  # magenta-red

    # ── STEP 3: Combine ──
    # Palette proximity is primary (weight 0.65)
    # HSV analytics is secondary (weight 0.35)
    hsv_max = max(hsv_scores.values()) if max(hsv_scores.values()) > 0 else 1
    hsv_norm = {k: v / hsv_max * 20 for k, v in hsv_scores.items()}

    final_scores = {}
    for k in SEASON_INFO:
        final_scores[k] = round(palette_score[k] * 0.65 + hsv_norm[k] * 0.35, 2)

    winner        = max(final_scores, key=lambda k: final_scores[k])
    top_score     = final_scores[winner]
    sorted_scores = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    top3          = sorted_scores[:3]

    return winner, final_scores, top3, top_score


# ─────────────────────────────────────────
#  SMART DOMINANT COLOR ENGINE
# ─────────────────────────────────────────

def is_skin_color(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    hue = h * 360
    if 5 <= hue <= 25 and 0.10 <= s <= 0.60 and v > 0.35:
        return True
    if r > 95 and g > 40 and b > 20:
        if max(r, g, b) - min(r, g, b) > 15:
            if r > g and r > b and abs(r - g) > 15:
                return True
    return False


def is_background(r, g, b):
    brightness = (r + g + b) / 3
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if brightness > 210 and s < 0.15: return True
    if brightness < 30: return True
    if s < 0.08 and 40 < brightness < 220: return True
    return False


def color_vibrancy_score(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    score = s * 3.0 + max(1.0 - abs(v - 0.55) * 2, 0) * 1.5
    if is_skin_color(r, g, b):          score -= 2.5
    if is_background(r, g, b):          score -= 3.0
    if s < 0.10:                        score -= 2.0
    return score


def get_dominant_color(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None: return (0.5, 0.5, 0.5), "#808080", (128, 128, 128)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h_orig, w_orig = img.shape[:2]

        img_crop    = img[int(h_orig*0.20):int(h_orig*0.90), int(w_orig*0.15):int(w_orig*0.85)]
        img_resized = cv2.resize(img_crop, (150, 150))
        img_hsv     = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)

        pixels_rgb = img_resized.reshape((-1, 3)).astype(float)
        pixels_hsv = img_hsv.reshape((-1, 3)).astype(float)
        sat_v = pixels_hsv[:, 1] / 255.0
        val_v = pixels_hsv[:, 2] / 255.0

        mask = (sat_v > 0.12) & (val_v > 0.15) & (val_v < 0.97)
        filtered = pixels_rgb[mask]
        if len(filtered) < 50: filtered = pixels_rgb

        n = max(min(8, len(filtered) // 10), 3)
        clt = KMeans(n_clusters=n, n_init=10, random_state=42)
        clt.fit(filtered)

        counts = np.bincount(clt.labels_)
        candidates = []
        for i, c in enumerate(clt.cluster_centers_):
            r, g, b = int(np.clip(c[0],0,255)), int(np.clip(c[1],0,255)), int(np.clip(c[2],0,255))
            candidates.append((color_vibrancy_score(r,g,b) + np.log1p(counts[i])*0.3, r, g, b))

        candidates.sort(reverse=True)
        _, br, bg, bb = candidates[0]
        hex_color = '#{:02x}{:02x}{:02x}'.format(br, bg, bb)
        return (br/255, bg/255, bb/255), hex_color, (br, bg, bb)
    except Exception as ex:
        print(f"Error: {ex}")
        return (0.5, 0.5, 0.5), "#808080", (128, 128, 128)


# ─────────────────────────────────────────
#  WIDGETS
# ─────────────────────────────────────────

class ColorCircle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_rgb = (0.85, 0.85, 0.87)
        self.size_hint = (None, None)
        self.size      = (dp(140), dp(140))
        self.draw()

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0, 0, 0.08)
            Ellipse(pos=(self.x+dp(4), self.y-dp(4)), size=self.size)
            Color(*self.color_rgb, 1)
            Ellipse(pos=self.pos, size=self.size)
            Color(1, 1, 1, 0.6)
            Line(circle=(self.center_x, self.center_y, dp(70)), width=dp(2.5))

    def update_color(self, rgb):
        self.color_rgb = rgb
        self.draw()

    def on_pos(self, *args):  self.draw()
    def on_size(self, *args): self.draw()


class WinnerCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height      = dp(160)
        self.spacing     = dp(14)
        self.padding     = [dp(14), dp(14), dp(14), dp(14)]

        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(
            pos =lambda i, v: setattr(self._bg_rect, 'pos',  v),
            size=lambda i, v: setattr(self._bg_rect, 'size', v)
        )

        left_col = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(148))
        self.color_circle = ColorCircle()
        left_col.add_widget(Widget())
        left_col.add_widget(self.color_circle)
        left_col.add_widget(Widget())
        self.add_widget(left_col)

        right_col = BoxLayout(orientation="vertical", spacing=dp(3))
        self.logo_img = Image(source="", size_hint=(None,None), size=(dp(54),dp(54)))
        self.season_lbl = Label(text="Pick an image", font_size=dp(18), bold=True,
            color=(0.12,0.12,0.30,1), halign="left", valign="middle",
            size_hint_y=None, height=dp(28))
        self.season_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        self.desc_lbl = Label(text="or enter a HEX color", font_size=dp(12),
            color=(0.40,0.40,0.50,1), halign="left", valign="top",
            size_hint_y=None, height=dp(32))
        self.desc_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        self.hex_lbl = Label(text="", font_size=dp(12), color=(0.45,0.45,0.55,1),
            halign="left", valign="middle", size_hint_y=None, height=dp(20))
        self.hex_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))

        right_col.add_widget(self.logo_img)
        right_col.add_widget(self.season_lbl)
        right_col.add_widget(self.desc_lbl)
        right_col.add_widget(self.hex_lbl)
        right_col.add_widget(Widget())
        self.add_widget(right_col)

    @staticmethod
    def make_gradient(colors, width=512, height=2):
        tex = Texture.create(size=(width, height), colorfmt='rgb')
        tex.wrap = 'clamp_to_edge'
        segs = len(colors) - 1
        sw   = width / segs
        buf  = []
        for x in range(width):
            seg = min(int(x // sw), segs - 1)
            t   = (x - seg * sw) / sw
            c1, c2 = colors[seg], colors[seg+1]
            buf += [int((c1[i]*(1-t)+c2[i]*t)*255) for i in range(3)] * height
        tex.blit_buffer(bytes(buf), colorfmt='rgb', bufferfmt='ubyte')
        tex.uvsize = (1, -1)
        return tex

    def update(self, season_name, rgb_kivy, hex_color):
        info    = SEASON_INFO[season_name]
        texture = self.make_gradient(info["gradient"])

        self.canvas.before.clear()
        with self.canvas.before:
            self._bg_rect = Rectangle(texture=texture, pos=self.pos, size=self.size)
        self.bind(
            pos =lambda i,v: setattr(self._bg_rect,'pos',v),
            size=lambda i,v: setattr(self._bg_rect,'size',v)
        )

        self.color_circle.update_color(rgb_kivy)

        if os.path.exists(info["icon"]):
            self.logo_img.source  = info["icon"]
            self.logo_img.opacity = 1
        else:
            self.logo_img.opacity = 0

        self.season_lbl.text = season_name
        self.desc_lbl.text   = info["desc"]
        self.hex_lbl.text    = hex_color.upper()


class ScoreBar(BoxLayout):
    def __init__(self, season_name, score, max_score, rank=0, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height      = dp(38)
        self.spacing     = dp(8)
        self.padding     = [dp(10), dp(4), dp(10), dp(4)]

        info  = SEASON_INFO[season_name]
        sc    = info["color"]
        muted = (sc[0]*0.35+0.65, sc[1]*0.35+0.65, sc[2]*0.35+0.65)

        with self.canvas.before:
            Color(*muted, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(
            pos =lambda i,v: setattr(self._bg,'pos',v),
            size=lambda i,v: setattr(self._bg,'size',v)
        )

        bar_colors = [(0.20,0.50,0.30,0.75),(0.30,0.45,0.70,0.75),(0.55,0.40,0.70,0.75)]
        bar_color  = bar_colors[rank] if rank < 3 else (0.5,0.5,0.5,0.5)

        if os.path.exists(info["icon"]):
            self.add_widget(Image(source=info["icon"], size_hint=(None,None),
                size=(dp(26),dp(26)), pos_hint={"center_y":0.5}))
        else:
            self.add_widget(Label(text="•", size_hint=(None,None),
                size=(dp(26),dp(26)), color=(0.3,0.3,0.3,1)))

        name_lbl = Label(text=season_name, font_size=dp(11), bold=(rank==0),
            color=(0.15,0.15,0.25,1), size_hint_x=None, width=dp(88),
            halign="left", valign="middle")
        name_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        self.add_widget(name_lbl)

        bar = Widget(size_hint_x=1)
        pct = score / max_score if max_score > 0 else 0
        with bar.canvas:
            Color(1,1,1,0.50)
            self._track = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[dp(5)])
            Color(*bar_color)
            self._fill  = RoundedRectangle(pos=bar.pos,
                size=(max(dp(4), bar.width*pct), bar.height), radius=[dp(5)])

        def upd(inst, val):
            self._track.pos  = inst.pos;  self._track.size = inst.size
            self._fill.pos   = inst.pos;  self._fill.size  = (max(dp(4), inst.width*pct), inst.height)

        bar.bind(pos=upd, size=upd)
        self.add_widget(bar)

        score_lbl = Label(text=f"{score:.1f}", font_size=dp(11), bold=True,
            color=(0.20,0.20,0.30,1), size_hint_x=None, width=dp(32),
            halign="right", valign="middle")
        score_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        self.add_widget(score_lbl)


# ─────────────────────────────────────────
#  MAIN LAYOUT
# ─────────────────────────────────────────

class ColorAnalysisLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding     = [dp(16), dp(14), dp(16), dp(14)]
        self.spacing     = dp(10)

        self.add_widget(Label(text="MySeason", font_size=dp(30), bold=True,
            color=(0.18,0.18,0.38,1), size_hint_y=None, height=dp(44)))
        self.add_widget(Label(text="Discover your color season", font_size=dp(13),
            color=(0.55,0.55,0.65,1), size_hint_y=None, height=dp(18)))

        self.winner_card = WinnerCard()
        self.add_widget(self.winner_card)

        divider = Widget(size_hint_y=None, height=dp(1))
        with divider.canvas:
            Color(0.80,0.80,0.86,1)
            self._div = RoundedRectangle(pos=divider.pos, size=divider.size)
        divider.bind(pos=lambda i,v: setattr(self._div,'pos',v),
                     size=lambda i,v: setattr(self._div,'size',v))
        self.add_widget(divider)

        bars_title = Label(text="Season scores", font_size=dp(13), bold=True,
            color=(0.28,0.28,0.42,1), size_hint_y=None, height=dp(22),
            halign="left", valign="middle")
        bars_title.bind(size=lambda i,v: setattr(i,'text_size',v))
        self.add_widget(bars_title)

        self.bars_container = BoxLayout(orientation="vertical", spacing=dp(6),
            size_hint_y=None, height=dp(3*44))
        self.bars_container.add_widget(Label(
            text="Results will appear here",
            font_size=dp(12), color=(0.60,0.60,0.66,1)))
        self.add_widget(self.bars_container)

        self.add_widget(Widget())

        # HEX input row
        hex_row = BoxLayout(size_hint=(1,None), height=dp(48), spacing=dp(8))
        self.hex_input = TextInput(hint_text="#A1B2C3", multiline=False,
            font_size=dp(16), background_color=(1,1,1,1),
            foreground_color=(0.1,0.1,0.1,1), padding=[dp(10),dp(10)])
        hex_btn = Button(text="Analyse HEX", size_hint_x=None, width=dp(140),
            background_color=(0.35,0.60,0.35,1), color=(1,1,1,1), bold=True)
        hex_btn.bind(on_press=self.analyze_hex)
        hex_row.add_widget(self.hex_input)
        hex_row.add_widget(hex_btn)
        self.add_widget(hex_row)

        pick_btn = Button(text="  Pick Image", font_size=dp(17),
            size_hint=(1,None), height=dp(52),
            background_color=(0.22,0.48,0.78,1), color=(1,1,1,1), bold=True)
        pick_btn.bind(on_press=self.open_file_chooser)
        self.add_widget(pick_btn)

    def _update_results(self, rgb_kivy, hex_color, rgb_raw):
        r, g, b = rgb_raw
        winner, scores, top3, top_score = classify_12_seasons(r, g, b)
        self.winner_card.update(winner, rgb_kivy, hex_color)
        self.bars_container.clear_widgets()
        max_score = top3[0][1] if top3[0][1] > 0 else 1
        for rank, (season_name, score) in enumerate(top3):
            self.bars_container.add_widget(ScoreBar(
                season_name=season_name, score=score,
                max_score=max_score, rank=rank))

    def analyze_hex(self, instance):
        rgb = hex_to_rgb(self.hex_input.text)
        if not rgb:
            self.winner_card.season_lbl.text = "Invalid HEX"
            self.winner_card.desc_lbl.text   = "Format: #RRGGBB"
            return
        r, g, b = rgb
        self._update_results((r/255, g/255, b/255), self.hex_input.text, rgb)

    def open_file_chooser(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        fc = FileChooserIconView(filters=["*.jpg","*.jpeg","*.png","*.bmp","*.webp"])
        content.add_widget(fc)
        bl = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        ok = Button(text="Select", background_color=(0.22,0.48,0.78,1), color=(1,1,1,1), bold=True)
        cn = Button(text="Cancel", background_color=(0.78,0.22,0.22,1), color=(1,1,1,1))
        bl.add_widget(ok); bl.add_widget(cn)
        content.add_widget(bl)
        popup = Popup(title="Select image", content=content, size_hint=(0.95,0.92))
        ok.bind(on_press=lambda x: (self.analyze_image(fc.selection[0]) or popup.dismiss()) if fc.selection else None)
        cn.bind(on_press=lambda x: popup.dismiss())
        popup.open()

    def analyze_image(self, path):
        self.winner_card.season_lbl.text = "Analysing..."
        self.winner_card.desc_lbl.text   = ""
        self.winner_card.hex_lbl.text    = ""
        rgb_kivy, hex_color, rgb_raw = get_dominant_color(path)
        self._update_results(rgb_kivy, hex_color, rgb_raw)


class ColorAnalysisApp(App):
    def build(self):
        self.title = "MySeason"
        return ColorAnalysisLayout()


if __name__ == "__main__":
    ColorAnalysisApp().run()