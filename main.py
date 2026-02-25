from kivy.app import App
from kivy.graphics.texture import Texture
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

SEASON_INFO = {

    "Light Spring": {
        "icon": "icons/light_spring.png",
        "bg": "icons/light_spring.png",
        "desc": "Topla • Svjetla • Delikatna",
        "color": (1.00, 0.85, 0.88),
        "gradient": [(1.0, 0.82, 0.86), (1.0, 0.95, 0.70), (0.85, 1.0, 0.90)]
    },

    "True Spring": {
        "icon": "icons/true_spring.png",
        "bg": "icons/true_spring.png",
        "desc": "Topla • Svježa • Živahna",
        "color": (1.00, 0.78, 0.40),
        "gradient": [(1.0, 0.60, 0.30), (1.0, 0.85, 0.20), (0.60, 0.90, 0.40)]
    },

    "Bright Spring": {
        "icon": "icons/bright_spring.png",
        "bg": "icons/bright_spring.png",
        "desc": "Topla • Čista • Kontrastna",
        "color": (1.00, 0.55, 0.35),
        "gradient": [(1.0, 0.30, 0.35), (1.0, 0.80, 0.10), (0.20, 0.90, 0.75)]
    },

    "Light Summer": {
        "icon": "icons/light_summer.png",
        "bg": "icons/light_summer.png",
        "desc": "Hladna • Svjetla • Nježna",
        "color": (0.78, 0.88, 1.00),
        "gradient": [
            (0.82, 0.90, 1.00),  # svijetlo baby plava
            (0.92, 0.88, 0.98),  # hladna puder lila
            (0.88, 0.95, 1.00)  # airy icy plava
        ]
    },
    "True Summer": {
        "icon": "icons/true_summer.png",
        "bg": "icons/true_summer.png",
        "desc": "Hladna • Mutna • Ružičasta",
        "color": (0.60, 0.75, 0.90),
        "gradient": [(0.55, 0.70, 0.88), (0.70, 0.78, 0.92), (0.80, 0.85, 0.95)]
    },

    "Soft Summer": {
        "icon": "icons/soft_summer.png",
        "bg": "icons/soft_summer.png",
        "desc": "Hladna • Mutna • Prigušena",
        "color": (0.65, 0.72, 0.80),
        "gradient": [(0.60, 0.68, 0.75), (0.72, 0.75, 0.82), (0.82, 0.85, 0.90)]
    },
    "Soft Autumn": {
        "icon": "icons/soft_autumn.png",
        "bg": "icons/soft_autumn.png",
        "desc": "Topla • Mutna • Prigušena",
        "color": (0.85, 0.70, 0.55),
        "gradient": [(0.90, 0.72, 0.55), (0.80, 0.65, 0.50), (0.70, 0.55, 0.40)]
    },

    "True Autumn": {
        "icon": "icons/true_autumn.png",
        "bg": "icons/true_autumn.png",
        "desc": "Topla • Bogata • Zemljena",
        "color": (0.80, 0.45, 0.20),
        "gradient": [(0.90, 0.50, 0.20), (0.75, 0.40, 0.15), (0.60, 0.35, 0.10)]
    },

    "Dark Autumn": {
        "icon": "icons/dark_autumn.png",
        "bg": "icons/dark_autumn.png",
        "desc": "Topla • Duboka • Intenzivna",
        "color": (0.55, 0.30, 0.15),
        "gradient": [(0.65, 0.35, 0.15), (0.45, 0.25, 0.10), (0.30, 0.18, 0.08)]
    },

    # ❄️ WINTER
    "Bright Winter": {
        "icon": "icons/bright_winter.png",
        "bg": "icons/bright_winter.png",
        "desc": "Hladna • Čista • Kontrastna",
        "color": (0.30, 0.65, 1.00),
        "gradient": [(0.20, 0.55, 1.00), (0.50, 0.75, 1.00), (0.80, 0.85, 1.00)]
    },

    "True Winter": {
        "icon": "icons/true_winter.png",
        "bg": "icons/true_winter.png",
        "desc": "Hladna • Oštra • Dramatična",
        "color": (0.35, 0.40, 0.75),
        "gradient": [(0.20, 0.30, 0.70), (0.40, 0.50, 0.85), (0.75, 0.80, 1.00)]
    },

    "Dark Winter": {
        "icon": "icons/dark_winter.png",
        "bg": "icons/dark_winter.png",
        "desc": "Hladna • Duboka • Tamna",
        "color": (0.20, 0.20, 0.40),
        "gradient": [(0.15, 0.18, 0.35), (0.25, 0.25, 0.50), (0.40, 0.40, 0.65)]
    }
}


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
            if r > g and r > b:
                if abs(r - g) > 15:
                    return True
    return False


def is_background(r, g, b):
    brightness = (r + g + b) / 3
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if brightness > 210 and s < 0.15: return True
    if brightness < 30: return True
    if s < 0.08 and 40 < brightness < 220: return True
    return False


def is_neutral_or_boring(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return s < 0.10


def color_vibrancy_score(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    score = s * 3.0
    val_score = 1.0 - abs(v - 0.55) * 2
    score += max(val_score, 0) * 1.5
    if is_skin_color(r, g, b):      score -= 2.5
    if is_background(r, g, b):      score -= 3.0
    if is_neutral_or_boring(r, g, b): score -= 2.0
    return score


def get_dominant_color(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None: return (0.5, 0.5, 0.5), "#808080", (128, 128, 128)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h_orig, w_orig = img.shape[:2]

        top, bottom = int(h_orig * 0.20), int(h_orig * 0.90)
        left, right = int(w_orig * 0.15), int(w_orig * 0.85)
        img_crop = img[top:bottom, left:right]
        img_resized = cv2.resize(img_crop, (150, 150))

        img_hsv = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)
        pixels_rgb = img_resized.reshape((-1, 3)).astype(float)
        pixels_hsv = img_hsv.reshape((-1, 3)).astype(float)

        sat_values = pixels_hsv[:, 1] / 255.0
        val_values = pixels_hsv[:, 2] / 255.0
        mask = (sat_values > 0.12) & (val_values > 0.15) & (val_values < 0.97)
        filtered_pixels = pixels_rgb[mask]
        if len(filtered_pixels) < 50: filtered_pixels = pixels_rgb

        n_clusters = max(min(8, len(filtered_pixels) // 10), 3)
        clt = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
        clt.fit(filtered_pixels)

        centers = clt.cluster_centers_
        counts = np.bincount(clt.labels_)

        all_candidates = []
        for i, center in enumerate(centers):
            r = int(np.clip(center[0], 0, 255))
            g = int(np.clip(center[1], 0, 255))
            b = int(np.clip(center[2], 0, 255))
            total_score = color_vibrancy_score(r, g, b) + np.log1p(counts[i]) * 0.3
            all_candidates.append((total_score, r, g, b))

        all_candidates.sort(reverse=True, key=lambda x: x[0])
        _, br, bg, bb = all_candidates[0]

        hex_color = '#{:02x}{:02x}{:02x}'.format(br, bg, bb)
        rgb_kivy = (br / 255, bg / 255, bb / 255)
        return rgb_kivy, hex_color, (br, bg, bb)
    except Exception as ex:
        print(f"Greška: {ex}")
        return (0.5, 0.5, 0.5), "#808080", (128, 128, 128)


# ─────────────────────────────────────────
#  SEASON ENGINE
# ─────────────────────────────────────────

def classify_12_seasons(r, g, b):
    r1, g1, b1 = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r1, g1, b1)
    hue, sat, val = h * 360, s, v

    warm = (0 <= hue <= 50) or (330 <= hue <= 360)
    cool = not warm
    deep = val < 0.40
    light = val > 0.72
    clear = sat > 0.60
    soft = sat < 0.45

    scores = {k: 0 for k in SEASON_INFO}

    if warm:
        for k in ["Light Spring", "True Spring", "Bright Spring", "Soft Autumn", "True Autumn", "Dark Autumn"]:
            scores[k] += 2
    if cool:
        for k in ["Light Summer", "True Summer", "Soft Summer", "Bright Winter", "True Winter", "Dark Winter"]:
            scores[k] += 2

    if sat > 0.65:
        scores["Bright Spring"] += 2;
        scores["Bright Winter"] += 2
        scores["True Spring"] += 1;
        scores["True Winter"] += 1;
        scores["True Autumn"] += 1
    if sat > 0.50:
        scores["True Spring"] += 1;
        scores["True Autumn"] += 1;
        scores["True Winter"] += 1
    if sat < 0.45:
        scores["Soft Summer"] += 2;
        scores["Soft Autumn"] += 2
        scores["Light Summer"] += 1;
        scores["Light Spring"] += 1
    if sat < 0.30:
        scores["Soft Summer"] += 2;
        scores["Soft Autumn"] += 2

    if val > 0.75:
        scores["Light Spring"] += 2;
        scores["Light Summer"] += 2
        scores["Bright Spring"] += 1;
        scores["Bright Winter"] += 1
    if val > 0.85:
        scores["Light Spring"] += 2;
        scores["Light Summer"] += 2
    if val < 0.35:
        scores["Dark Autumn"] += 2;
        scores["Dark Winter"] += 2
        scores["True Autumn"] += 1;
        scores["True Winter"] += 1
    if val < 0.25:
        scores["Dark Autumn"] += 2;
        scores["Dark Winter"] += 2
    if 0.40 <= val <= 0.70:
        for k in ["True Spring", "True Summer", "True Autumn", "True Winter"]: scores[k] += 1

    if warm and deep:               scores["Dark Autumn"] += 2; scores["True Autumn"] += 1
    if cool and deep and clear:     scores["Dark Winter"] += 3; scores["True Winter"] += 1
    if cool and deep and not clear: scores["Dark Winter"] += 1; scores["True Winter"] += 2
    if cool and clear:              scores["Bright Winter"] += 2; scores["True Winter"] += 1
    if warm and clear:              scores["Bright Spring"] += 2; scores["True Spring"] += 1
    if cool and light:              scores["Light Summer"] += 2
    if warm and light:              scores["Light Spring"] += 2
    if warm and soft:               scores["Soft Autumn"] += 2
    if cool and soft:               scores["Soft Summer"] += 2

    if 20 <= hue <= 50:  scores["True Autumn"] += 1; scores["Dark Autumn"] += 1
    if 40 <= hue <= 70:  scores["True Spring"] += 1; scores["Light Spring"] += 1
    if 200 <= hue <= 320: scores["True Summer"] += 1; scores["True Winter"] += 1

    winner = max(scores, key=lambda k: scores[k])
    top_score = scores[winner]
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return winner, scores, sorted_scores[:3], top_score


# ─────────────────────────────────────────
#  WIDGETS
# ─────────────────────────────────────────

class ColorCircle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_rgb = (0.85, 0.85, 0.87)
        self.size_hint = (None, None)
        self.size = (dp(140), dp(140))
        self.draw()

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0, 0, 0.08)
            Ellipse(pos=(self.x + dp(4), self.y - dp(4)), size=self.size)
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
    """
    Veliki card za pobjedničku sezonu sa muted pozadinom sezone.
    Lijevo: krug boje | Desno: logo + naziv + opis + hex
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(160)
        self.spacing = dp(14)
        self.padding = [dp(14), dp(14), dp(14), dp(14)]

        # Pozadina (crtat ćemo u update)
        self._bg_color = (0.9, 0.9, 0.9)
        with self.canvas.before:
            self._bg_rect = Rectangle(
                source="icons/default_bg.png",
                pos=self.pos,
                size=self.size
            )
        self.bind(
            pos=lambda i, v: setattr(self._bg_rect, 'pos', v),
            size=lambda i, v: setattr(self._bg_rect, 'size', v)
        )

        # Lijevo — krug boje
        left_col = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(148))
        self.color_circle = ColorCircle()
        left_col.add_widget(Widget())
        left_col.add_widget(self.color_circle)
        left_col.add_widget(Widget())
        self.add_widget(left_col)

        # Desno — info
        right_col = BoxLayout(orientation="vertical", spacing=dp(3))

        # Logo sezone
        self.logo_img = Image(
            source="",
            size_hint=(None, None),
            size=(dp(54), dp(54)),
        )

        self.season_lbl = Label(
            text="Odaberi sliku",
            font_size=dp(18),
            bold=True,
            color=(0.12, 0.12, 0.30, 1),
            halign="left", valign="middle",
            size_hint_y=None, height=dp(28)
        )
        self.season_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))

        self.desc_lbl = Label(
            text="za analizu boje",
            font_size=dp(12),
            color=(0.40, 0.40, 0.50, 1),
            halign="left", valign="top",
            size_hint_y=None, height=dp(32)
        )
        self.desc_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))

        self.hex_lbl = Label(
            text="",
            font_size=dp(12),
            color=(0.45, 0.45, 0.55, 1),
            halign="left", valign="middle",
            size_hint_y=None, height=dp(20)
        )
        self.hex_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))

        right_col.add_widget(self.logo_img)
        right_col.add_widget(self.season_lbl)
        right_col.add_widget(self.desc_lbl)
        right_col.add_widget(self.hex_lbl)
        right_col.add_widget(Widget())
        self.add_widget(right_col)

    @staticmethod
    def create_multi_gradient(colors, width=512, height=2):
        texture = Texture.create(size=(width, height), colorfmt='rgb')
        texture.wrap = 'clamp_to_edge'

        buf = []
        segments = len(colors) - 1
        segment_width = width / segments

        for x in range(width):
            seg = min(int(x // segment_width), segments - 1)
            t = (x - seg * segment_width) / segment_width

            c1 = colors[seg]
            c2 = colors[seg + 1]

            r = int((c1[0] * (1 - t) + c2[0] * t) * 255)
            g = int((c1[1] * (1 - t) + c2[1] * t) * 255)
            b = int((c1[2] * (1 - t) + c2[2] * t) * 255)

            for _ in range(height):
                buf.extend([r, g, b])

        texture.blit_buffer(bytes(buf), colorfmt='rgb', bufferfmt='ubyte')
        texture.uvsize = (1, -1)
        return texture

    def update(self, season_name, rgb_kivy, hex_color):
        info = SEASON_INFO[season_name]

        texture = self.create_multi_gradient(info["gradient"])

        self.canvas.before.clear()
        with self.canvas.before:
            self._bg_rect = Rectangle(
                texture=texture,
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=lambda i, v: setattr(self._bg_rect, 'pos', v),
            size=lambda i, v: setattr(self._bg_rect, 'size', v)
        )

        # krug
        self.color_circle.update_color(rgb_kivy)

        self.logo_img.opacity = 0

        self.season_lbl.text = season_name
        self.desc_lbl.text = info["desc"]
        self.hex_lbl.text = hex_color.upper()


class ScoreBar(BoxLayout):
    """
    Red: mali logo | naziv | progress bar | bodovi
    Sa muted pozadinom sezone.
    """

    def __init__(self, season_name, score, max_score, rank=0, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(38)
        self.spacing = dp(8)
        self.padding = [dp(10), dp(4), dp(10), dp(4)]

        info = SEASON_INFO[season_name]

        # ── Muted pozadina sezone ──
        sc = info["color"]
        muted = (
            sc[0] * 0.35 + 0.65,
            sc[1] * 0.35 + 0.65,
            sc[2] * 0.35 + 0.65,
        )
        with self.canvas.before:
            Color(*muted, 1)
            self._bg_card = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(10)]
            )
        self.bind(
            pos=lambda i, v: setattr(self._bg_card, 'pos', v),
            size=lambda i, v: setattr(self._bg_card, 'size', v)
        )

        # ── Bar fill boje po ranku ──
        bar_colors = [
            (0.20, 0.50, 0.30, 0.70),  # 1. zelena
            (0.30, 0.45, 0.70, 0.70),  # 2. plava
            (0.55, 0.40, 0.70, 0.70),  # 3. ljubičasta
        ]
        bar_color = bar_colors[rank] if rank < 3 else (0.5, 0.5, 0.5, 0.5)

        # ── Mali logo ──
        if os.path.exists(info["icon"]):
            icon = Image(
                source=info["icon"],
                size_hint=(None, None),
                size=(dp(26), dp(26)),
                pos_hint={"center_y": 0.5}
            )
        else:
            icon = Label(
                text="•",
                size_hint=(None, None),
                size=(dp(26), dp(26)),
                color=(0.3, 0.3, 0.3, 1)
            )
        self.add_widget(icon)

        # ── Naziv ──
        name_lbl = Label(
            text=season_name,
            font_size=dp(11),
            bold=(rank == 0),
            color=(0.15, 0.15, 0.25, 1),
            size_hint_x=None,
            width=dp(88),
            halign="left",
            valign="middle"
        )
        name_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.add_widget(name_lbl)

        # ── Progress bar ──
        bar_container = Widget(size_hint_x=1)
        pct = score / max_score if max_score > 0 else 0

        with bar_container.canvas:
            # Track
            Color(1, 1, 1, 0.50)
            self._track = RoundedRectangle(
                pos=bar_container.pos,
                size=bar_container.size,
                radius=[dp(5)]
            )
            # Fill
            Color(*bar_color)
            self._fill = RoundedRectangle(
                pos=bar_container.pos,
                size=(max(dp(4), bar_container.width * pct), bar_container.height),
                radius=[dp(5)]
            )

        def update_bar(inst, val):
            self._track.pos = inst.pos
            self._track.size = inst.size
            self._fill.pos = inst.pos
            self._fill.size = (max(dp(4), inst.width * pct), inst.height)

        bar_container.bind(pos=update_bar, size=update_bar)
        self.add_widget(bar_container)

        # ── Bodovi ──
        score_lbl = Label(
            text=f"{score}",
            font_size=dp(12),
            bold=True,
            color=(0.20, 0.20, 0.30, 1),
            size_hint_x=None,
            width=dp(26),
            halign="right",
            valign="middle"
        )
        score_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.add_widget(score_lbl)


# ─────────────────────────────────────────
#  GLAVNI LAYOUT
# ─────────────────────────────────────────

class ColorAnalysisLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(16), dp(14), dp(16), dp(14)]
        self.spacing = dp(10)

        # ── Naslov ──
        title = Label(
            text="MySeason", font_size=dp(30), bold=True,
            color=(0.18, 0.18, 0.38, 1), size_hint_y=None, height=dp(44)
        )
        self.add_widget(title)

        subtitle = Label(
            text="Otkrij svoju paletu boja", font_size=dp(13),
            color=(0.55, 0.55, 0.65, 1), size_hint_y=None, height=dp(18)
        )
        self.add_widget(subtitle)

        # ── Winner Card ──
        self.winner_card = WinnerCard()
        self.add_widget(self.winner_card)

        # ── Divider ──
        divider = Widget(size_hint_y=None, height=dp(1))
        with divider.canvas:
            Color(0.80, 0.80, 0.86, 1)
            self._div = RoundedRectangle(pos=divider.pos, size=divider.size)
        divider.bind(
            pos=lambda i, v: setattr(self._div, 'pos', v),
            size=lambda i, v: setattr(self._div, 'size', v)
        )
        self.add_widget(divider)

        # ── Bars naslov ──
        bars_title = Label(
            text="Rezultati po sezonama", font_size=dp(13), bold=True,
            color=(0.28, 0.28, 0.42, 1), size_hint_y=None, height=dp(22),
            halign="left", valign="middle"
        )
        bars_title.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.add_widget(bars_title)

        # ── Bars container ──
        self.bars_container = BoxLayout(
            orientation="vertical", spacing=dp(6),
            size_hint_y=None, height=dp(3 * 44)
        )
        self.bars_container.add_widget(Label(
            text="Ovdje će se prikazati top 3 rezultata",
            font_size=dp(12), color=(0.60, 0.60, 0.66, 1)
        ))
        self.add_widget(self.bars_container)

        self.add_widget(Widget())

        # ── Dugme ──
        pick_btn = Button(
            text="  Odaberi Sliku", font_size=dp(17),
            size_hint=(1, None), height=dp(52),
            background_color=(0.22, 0.48, 0.78, 1),
            color=(1, 1, 1, 1), bold=True
        )
        pick_btn.bind(on_press=self.open_file_chooser)
        self.add_widget(pick_btn)

    def open_file_chooser(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        file_chooser = FileChooserIconView(
            filters=["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]
        )
        content.add_widget(file_chooser)

        btn_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        select_btn = Button(text="Odaberi", background_color=(0.22, 0.48, 0.78, 1), color=(1, 1, 1, 1), bold=True)
        cancel_btn = Button(text="Odustani", background_color=(0.78, 0.22, 0.22, 1), color=(1, 1, 1, 1))
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Odaberi sliku", content=content, size_hint=(0.95, 0.92))

        select_btn.bind(on_press=lambda x: (
            self.analyze_image(file_chooser.selection[0]) or popup.dismiss()
            if file_chooser.selection else None
        ))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()

    def analyze_image(self, path):
        # Reset
        self.winner_card.season_lbl.text = "Analiziranje..."
        self.winner_card.desc_lbl.text = ""
        self.winner_card.hex_lbl.text = ""

        rgb_kivy, hex_color, rgb_raw = get_dominant_color(path)
        r, g, b = rgb_raw
        winner, scores, top3, top_score = classify_12_seasons(r, g, b)

        # ── Update winner card ──
        self.winner_card.update(winner, rgb_kivy, hex_color)

        # ── Update score bars ──
        self.bars_container.clear_widgets()
        max_score = top3[0][1] if top3[0][1] > 0 else 1
        for rank, (season_name, score) in enumerate(top3):
            bar = ScoreBar(
                season_name=season_name,
                score=score,
                max_score=max_score,
                rank=rank
            )
            self.bars_container.add_widget(bar)


class ColorAnalysisApp(App):
    def build(self):
        self.title = "MySeason"
        return ColorAnalysisLayout()


if __name__ == "__main__":
    ColorAnalysisApp().run()
