"""
Retro 16-Bit Bunny Grid Navigation using Euclidean Algorithm (GCD)
==================================================================
A 16-bit arcade-style Tkinter application structured into 3 distinct boxes:
1. Box 1 (Main Screen): Retro 16-bit pixel grid arena with animated hopping bunny & carrots at (0,0)
2. Box 2 (Calculation Engine): Step-by-step Euclidean Algorithm breakdown and hop trajectory logger
3. Box 3 (Input Area & Controls): Coordinate inputs, quick presets, hop speed, navigation buttons & End Screen trigger
4. End Screen / Splash Screen: Dynamic multi-color fireworks particle simulation with retro arcade banner:
   "ROBOT GRID NAVIGATION USING EUCLIDEAN ALGORITHM"
"""

import math
import random
import tkinter as tk
from tkinter import messagebox


# ==============================================================================
# 16-BIT RETRO COLOR PALETTE & SPRITE DEFINITIONS
# ==============================================================================
PALETTE = {
    "bg_dark": "#0a0a14",
    "box_bg": "#121324",
    "box_border": "#3b426b",
    "box_border_light": "#5c69a6",
    "box_inner": "#181a30",
    "accent_neon": "#00ffcc",
    "accent_pink": "#ff3399",
    "accent_yellow": "#ffea00",
    "accent_green": "#00e676",
    "accent_orange": "#ff9100",
    "accent_purple": "#b388ff",
    "text_light": "#e0e6ed",
    "text_dim": "#7e8b9b",
    "grid_bg": "#0d0f1f",
    "grid_line": "#191d38",
    "grid_axis": "#39437a",
    "grid_dot": "#252b4d",
}

# 16x16 Pixel Bunny Sprite Matrix (Idle)
BUNNY_SPRITE_IDLE = [
    "....WW....WW....",
    "...WPPW..WPPW...",
    "...WPPW..WPPW...",
    "...WPPW..WPPW...",
    "....WWWWWWWW....",
    "...WWWWWWWWWW...",
    "..WWBWWWWWWBWW..",
    "..WWBWWPPWWBWW..",
    "..WRWWWPPEWWRAW.",
    "..WWWWWWWWWWWW..",
    "...WWWWWWWWWW...",
    "...WWWWWWWWWW...",
    "..WWWWWWWWWWWW..",
    "..WWW.WWWW.WWW..",
    "...SS..SS...SS..",
    "................",
]

# 16x16 Pixel Bunny Sprite Matrix (Hopping in mid-air)
BUNNY_SPRITE_HOP = [
    "...WW......WW...",
    "..WPPW....WPPW..",
    "..WPPW....WPPW..",
    "...WWWWWWWWWW...",
    "..WWWWWWWWWWWW..",
    ".WWBWWWWWWWWBWW.",
    ".WWBWWPPPEWWBWW.",
    ".WRWWWWPPWWWRAW.",
    "..WWWWWWWWWWWW..",
    "...WWWWWWWWWW...",
    "....WWWWWWWW....",
    "..WWWWWWWWWWWW..",
    ".WWWW......WWWW.",
    ".SS..........SS.",
    "................",
    "................",
]

# 14x14 Pixel Carrot Sprite Matrix at Origin (0, 0)
CARROT_SPRITE = [
    ".....GG.GG....",
    "....GLLGGGL...",
    ".....GGGG.....",
    "...OOOOOOOO...",
    "..OYYOOOODDO..",
    "..OYOOOOODDO..",
    "...OOOOODDO...",
    "...OYOOODDO...",
    "....OOOODO....",
    "....OYOODO....",
    ".....OODO.....",
    ".....OOO......",
    "......OO......",
    ".......O......",
]


class RetroPixelRenderer:
    """Renders 16-bit pixel-art character matrices directly onto Tkinter Canvas."""

    PALETTE_MAP = {
        "W": "#f5f5ff",
        "S": "#c2c8d8",
        "P": "#ff6699",
        "B": "#12131e",
        "E": "#ffffff",
        "R": "#ff3b75",
        "A": "#ff3b75",
        "G": "#00b33c",
        "L": "#44ff77",
        "O": "#ff7700",
        "Y": "#ffcc00",
        "D": "#c44000",
    }

    @classmethod
    def draw_sprite(cls, canvas, sprite_lines, cx, cy, pixel_size=2):
        """Draws a pixel matrix centered at canvas position (cx, cy)."""
        rows = len(sprite_lines)
        cols = len(sprite_lines[0])
        start_x = cx - (cols * pixel_size) / 2
        start_y = cy - (rows * pixel_size) / 2
        items = []

        for r, row in enumerate(sprite_lines):
            for c, char in enumerate(row):
                if char != "." and char in cls.PALETTE_MAP:
                    color = cls.PALETTE_MAP[char]
                    x0 = start_x + c * pixel_size
                    y0 = start_y + r * pixel_size
                    x1 = x0 + pixel_size
                    y1 = y0 + pixel_size
                    item = canvas.create_rectangle(
                        x0, y0, x1, y1, fill=color, outline=color
                    )
                    items.append(item)
        return items


# ==============================================================================
# FIREWORKS PARTICLE SYSTEM
# ==============================================================================
class Particle:
    """Represents an exploding firework spark with velocity, gravity, and drag."""

    def __init__(self, x, y, color, vx, vy, life, size=3, gravity=0.16, drag=0.96):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.drag = drag

    def update(self):
        self.vx *= self.drag
        self.vy = self.vy * self.drag + self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0


class Rocket:
    """Represents a rising firework rocket with spark trail that detonates at apex."""

    def __init__(self, x, target_y, color):
        self.x = x
        self.y = 800
        self.target_y = target_y
        self.color = color
        self.vy = -random.uniform(10.0, 15.0)
        self.vx = random.uniform(-0.9, 0.9)
        self.exploded = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.09  # upward deceleration
        if self.y <= self.target_y or self.vy >= -1.0:
            self.exploded = True
        return not self.exploded


# ==============================================================================
# MAIN APPLICATION CLASS
# ==============================================================================
class RabbitEuclideanNavApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RABBIT GRID NAVIGATION - EUCLIDEAN ALGORITHM")
        self.root.geometry("1240x840")
        self.root.minsize(1050, 720)
        self.root.configure(bg=PALETTE["bg_dark"])

        # Navigation State Variables
        self.start_x = 12
        self.start_y = 18
        self.gcd_val = 6
        self.euc_steps = []
        self.path = []
        self.current_step_idx = 0
        self.is_animating = False
        self.animation_job = None
        self.anim_speed_ms = 400

        # Smooth Sub-Hop Interpolation State
        self.hop_substep = 0
        self.total_substeps = 8
        self.current_pos = (float(self.start_x), float(self.start_y))
        self.target_pos = (float(self.start_x), float(self.start_y))
        self.jump_height = 0.0

        # Dust Puff Particles on Grid
        self.dust_particles = []

        # End Screen / Splash State
        self.in_end_screen = False
        self.firework_particles = []
        self.firework_rockets = []
        self.splash_canvas = None
        self.splash_job = None
        self.btn_splash_back = None

        self.calculate_euclidean_steps(self.start_x, self.start_y)
        self.setup_ui()
        self.root.bind("<Configure>", self.on_window_resize)

    # --------------------------------------------------------------------------
    # MATHEMATICAL ENGINE: EUCLIDEAN ALGORITHM & PATHFINDING
    # --------------------------------------------------------------------------
    def calculate_euclidean_steps(self, a, b):
        """Calculates step-by-step Euclidean Algorithm and planned grid navigation path."""
        self.euc_steps = []
        x, y = max(a, b), min(a, b)
        step_num = 1

        while y != 0:
            q = x // y
            r = x % y
            self.euc_steps.append({
                "step": step_num,
                "a": x,
                "b": y,
                "q": q,
                "r": r,
                "expr": f"{x} = {y} × {q} + {r}",
            })
            x, y = y, r
            step_num += 1

        self.gcd_val = x if x != 0 else 1

        # Generate shortest grid hop path towards (0, 0)
        self.path = [(a, b)]
        cx, cy = a, b
        step_delta = self.gcd_val

        while cx > 0 or cy > 0:
            if cx >= cy and cx > 0:
                cx = max(0, cx - step_delta)
            elif cy > 0:
                cy = max(0, cy - step_delta)
            self.path.append((cx, cy))

        self.current_step_idx = 0
        self.current_pos = (float(a), float(b))
        self.target_pos = (float(a), float(b))
        return self.gcd_val

    # --------------------------------------------------------------------------
    # UI SETUP: 3-BOX ARCHITECTURE
    # --------------------------------------------------------------------------
    def setup_ui(self):
        self.setup_top_banner()

        # Main Workspace Container: Box 1 (Left) and Box 2 (Right)
        self.main_container = tk.Frame(self.root, bg=PALETTE["bg_dark"])
        self.main_container.pack(fill="both", expand=True, padx=14, pady=(2, 6))

        # BOX 1: Main Screen (Retro Grid Canvas)
        self.setup_box1_arena()

        # BOX 2: Euclid's Calculation Engine Panel
        self.setup_box2_math()

        # BOX 3: Input Area & Mission Control (Bottom)
        self.setup_box3_controls()

        # Initial Render
        self.root.after(100, self.refresh_all_views)

    def setup_top_banner(self):
        banner_frame = tk.Frame(self.root, bg="#121324", bd=2, relief="solid")
        banner_frame.pack(fill="x", padx=14, pady=(8, 4))

        title_box = tk.Frame(banner_frame, bg="#121324")
        title_box.pack(pady=4)

        tk.Label(
            title_box,
            text="★ 16-BIT RETRO MATH ARENA ★",
            font=("Courier", 10, "bold"),
            fg=PALETTE["accent_yellow"],
            bg="#121324",
        ).pack(side="top")

        tk.Label(
            title_box,
            text="ROBOT GRID NAVIGATION USING EUCLIDEAN ALGORITHM",
            font=("Courier", 14, "bold"),
            fg=PALETTE["accent_neon"],
            bg="#121324",
        ).pack(side="top", pady=1)

    def setup_box1_arena(self):
        """BOX 1: Main screen showing bunny movements on retro pixel grid."""
        box1_outer = tk.Frame(
            self.main_container,
            bg=PALETTE["box_border"],
            bd=2,
            relief="solid",
        )
        box1_outer.pack(side="left", fill="both", expand=True, padx=(0, 6))

        box1_header = tk.Frame(box1_outer, bg=PALETTE["box_bg"])
        box1_header.pack(fill="x")
        tk.Label(
            box1_header,
            text="[ 1. MAIN ARENA: BUNNY HOPPER GRID ]",
            font=("Courier", 11, "bold"),
            fg=PALETTE["accent_neon"],
            bg=PALETTE["box_bg"],
            padx=8,
            pady=4,
        ).pack(side="left")

        self.lbl_arena_status = tk.Label(
            box1_header,
            text="STATUS: READY TO HOP",
            font=("Courier", 9, "bold"),
            fg=PALETTE["accent_green"],
            bg=PALETTE["box_bg"],
            padx=8,
        )
        self.lbl_arena_status.pack(side="right")

        # Pixel Grid Canvas
        self.canvas = tk.Canvas(
            box1_outer,
            bg=PALETTE["grid_bg"],
            bd=0,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=3, pady=3)

    def setup_box2_math(self):
        """BOX 2: Euclid's algorithm step-by-step calculations."""
        box2_outer = tk.Frame(
            self.main_container,
            bg=PALETTE["box_border"],
            bd=2,
            relief="solid",
            width=430,
        )
        box2_outer.pack(side="right", fill="both", expand=False, padx=(6, 0))
        box2_outer.pack_propagate(False)

        box2_header = tk.Frame(box2_outer, bg=PALETTE["box_bg"])
        box2_header.pack(fill="x")
        tk.Label(
            box2_header,
            text="[ 2. EUCLID'S ALGORITHM CALCULATION ]",
            font=("Courier", 11, "bold"),
            fg=PALETTE["accent_pink"],
            bg=PALETTE["box_bg"],
            padx=8,
            pady=4,
        ).pack(side="left")

        content_frame = tk.Frame(box2_outer, bg=PALETTE["box_inner"])
        content_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Card A: GCD Result Badge
        self.gcd_card = tk.Frame(
            content_frame,
            bg="#1c1f38",
            bd=1,
            relief="ridge",
            padx=8,
            pady=6,
        )
        self.gcd_card.pack(fill="x", padx=4, pady=4)

        self.lbl_gcd_title = tk.Label(
            self.gcd_card,
            text=f"GREATEST COMMON DIVISOR = {self.gcd_val}",
            font=("Courier", 12, "bold"),
            fg=PALETTE["accent_yellow"],
            bg="#1c1f38",
        )
        self.lbl_gcd_title.pack(anchor="w")

        self.lbl_gcd_rule = tk.Label(
            self.gcd_card,
            text=f"Bunny moves in quantum leaps of {self.gcd_val} units.",
            font=("Courier", 9),
            fg=PALETTE["text_light"],
            bg="#1c1f38",
        )
        self.lbl_gcd_rule.pack(anchor="w", pady=(2, 0))

        # Card B: Euclidean Division Step-by-Step
        euc_box = tk.LabelFrame(
            content_frame,
            text=" DIVISION ALGORITHM STEPS ",
            font=("Courier", 9, "bold"),
            fg=PALETTE["accent_neon"],
            bg=PALETTE["box_inner"],
            bd=1,
            relief="solid",
        )
        euc_box.pack(fill="x", padx=4, pady=4)

        self.lbl_euc_text = tk.Label(
            euc_box,
            text="",
            font=("Courier", 10, "bold"),
            fg=PALETTE["text_light"],
            bg="#131528",
            justify="left",
            padx=8,
            pady=6,
            anchor="w",
        )
        self.lbl_euc_text.pack(fill="x", padx=4, pady=4)

        # Card C: Real-Time Grid Hop Sequence
        seq_box = tk.LabelFrame(
            content_frame,
            text=" PLANNED HOP SEQUENCE ",
            font=("Courier", 9, "bold"),
            fg=PALETTE["accent_purple"],
            bg=PALETTE["box_inner"],
            bd=1,
            relief="solid",
        )
        seq_box.pack(fill="both", expand=True, padx=4, pady=4)

        self.txt_hops = tk.Text(
            seq_box,
            font=("Courier", 9),
            bg="#101222",
            fg=PALETTE["text_light"],
            bd=0,
            padx=8,
            pady=6,
            wrap="word",
            height=8,
        )
        self.txt_hops.pack(fill="both", expand=True, padx=4, pady=4)
        self.txt_hops.tag_config(
            "active",
            background="#2a452a",
            foreground=PALETTE["accent_green"],
            font=("Courier", 9, "bold"),
        )
        self.txt_hops.tag_config(
            "done",
            foreground="#607085",
        )

        # Card D: Efficiency & Invariant Notes
        stats_card = tk.Frame(content_frame, bg="#15172b", bd=1, relief="ridge", padx=6, pady=4)
        stats_card.pack(fill="x", padx=4, pady=(2, 4))
        self.lbl_metrics = tk.Label(
            stats_card,
            text="Total Hops: 0 | Distance to Origin: 0",
            font=("Courier", 8, "bold"),
            fg=PALETTE["text_dim"],
            bg="#15172b",
        )
        self.lbl_metrics.pack(anchor="w")

    def setup_box3_controls(self):
        """BOX 3: Input Area & Mission Control (Bottom panel)."""
        box3_outer = tk.Frame(
            self.root,
            bg=PALETTE["box_border"],
            bd=2,
            relief="solid",
        )
        box3_outer.pack(fill="x", padx=14, pady=(0, 10))

        box3_header = tk.Frame(box3_outer, bg=PALETTE["box_bg"])
        box3_header.pack(fill="x")
        tk.Label(
            box3_header,
            text="[ 3. INPUT AREA & MISSION CONTROL ]",
            font=("Courier", 11, "bold"),
            fg=PALETTE["accent_yellow"],
            bg=PALETTE["box_bg"],
            padx=8,
            pady=3,
        ).pack(side="left")

        ctrl_inner = tk.Frame(box3_outer, bg=PALETTE["box_inner"], padx=10, pady=8)
        ctrl_inner.pack(fill="x")

        # 1. Coordinate Inputs
        input_subframe = tk.Frame(ctrl_inner, bg=PALETTE["box_inner"])
        input_subframe.pack(side="left", padx=(0, 15))

        tk.Label(
            input_subframe,
            text="START (X, Y):",
            font=("Courier", 10, "bold"),
            fg=PALETTE["accent_neon"],
            bg=PALETTE["box_inner"],
        ).pack(side="left", padx=(0, 6))

        self.entry_x = tk.Entry(
            input_subframe,
            font=("Courier", 12, "bold"),
            width=4,
            justify="center",
            bg="#0f111f",
            fg=PALETTE["accent_yellow"],
            insertbackground="white",
            relief="solid",
            bd=1,
        )
        self.entry_x.insert(0, str(self.start_x))
        self.entry_x.pack(side="left", padx=2)

        tk.Label(
            input_subframe,
            text=",",
            font=("Courier", 14, "bold"),
            fg="white",
            bg=PALETTE["box_inner"],
        ).pack(side="left", padx=1)

        self.entry_y = tk.Entry(
            input_subframe,
            font=("Courier", 12, "bold"),
            width=4,
            justify="center",
            bg="#0f111f",
            fg=PALETTE["accent_yellow"],
            insertbackground="white",
            relief="solid",
            bd=1,
        )
        self.entry_y.insert(0, str(self.start_y))
        self.entry_y.pack(side="left", padx=2)

        # 2. Preset Buttons
        presets_frame = tk.Frame(ctrl_inner, bg=PALETTE["box_inner"])
        presets_frame.pack(side="left", padx=(0, 15))

        tk.Label(
            presets_frame,
            text="PRESETS:",
            font=("Courier", 9, "bold"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["box_inner"],
        ).pack(side="left", padx=(0, 4))

        for px, py in [(12, 18), (24, 36), (15, 25), (28, 21), (35, 14)]:
            b = tk.Button(
                presets_frame,
                text=f"{px},{py}",
                font=("Courier", 8, "bold"),
                bg="#232742",
                fg=PALETTE["text_light"],
                activebackground=PALETTE["accent_neon"],
                activeforeground="black",
                relief="flat",
                bd=1,
                padx=4,
                pady=1,
                command=lambda x=px, y=py: self.apply_preset(x, y),
            )
            b.pack(side="left", padx=2)

        # 3. Speed Control
        speed_frame = tk.Frame(ctrl_inner, bg=PALETTE["box_inner"])
        speed_frame.pack(side="left", padx=(0, 15))

        tk.Label(
            speed_frame,
            text="SPEED:",
            font=("Courier", 9, "bold"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["box_inner"],
        ).pack(side="left", padx=(0, 4))

        self.speed_var = tk.StringVar(value="Normal")
        for label, val in [("Slow", 600), ("Normal", 350), ("Fast", 120)]:
            rb = tk.Radiobutton(
                speed_frame,
                text=label,
                variable=self.speed_var,
                value=label,
                font=("Courier", 8),
                fg=PALETTE["text_light"],
                bg=PALETTE["box_inner"],
                selectcolor="#101222",
                activebackground=PALETTE["box_inner"],
                command=lambda v=val: self.set_speed(v),
            )
            rb.pack(side="left")

        # 4. Action Buttons
        actions_frame = tk.Frame(ctrl_inner, bg=PALETTE["box_inner"])
        actions_frame.pack(side="right")

        self.btn_run = tk.Button(
            actions_frame,
            text="▶ START HOPPING",
            font=("Courier", 10, "bold"),
            bg="#00b359",
            fg="black",
            activebackground=PALETTE["accent_green"],
            relief="solid",
            bd=2,
            padx=10,
            pady=4,
            command=self.start_navigation,
        )
        self.btn_run.pack(side="left", padx=4)

        self.btn_step = tk.Button(
            actions_frame,
            text="⏭ STEP",
            font=("Courier", 9, "bold"),
            bg="#2c3e6b",
            fg=PALETTE["text_light"],
            activebackground=PALETTE["accent_neon"],
            activeforeground="black",
            relief="solid",
            bd=1,
            padx=8,
            pady=4,
            command=self.step_forward,
        )
        self.btn_step.pack(side="left", padx=4)

        self.btn_reset = tk.Button(
            actions_frame,
            text="↺ RESET",
            font=("Courier", 9, "bold"),
            bg="#36394e",
            fg=PALETTE["text_light"],
            relief="solid",
            bd=1,
            padx=8,
            pady=4,
            command=self.reset_simulation,
        )
        self.btn_reset.pack(side="left", padx=4)

        # 5. USER REQUESTED: END SCREEN BUTTON
        self.btn_end = tk.Button(
            actions_frame,
            text="🎆 END SCREEN",
            font=("Courier", 10, "bold"),
            bg="#ff0066",
            fg="white",
            activebackground="#ff3399",
            activeforeground="white",
            relief="solid",
            bd=2,
            padx=10,
            pady=4,
            command=self.show_end_screen,
        )
        self.btn_end.pack(side="left", padx=(10, 0))

    # --------------------------------------------------------------------------
    # CONTROLS & EVENT HANDLERS
    # --------------------------------------------------------------------------
    def apply_preset(self, x, y):
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, str(x))
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(y))
        self.reset_simulation()

    def set_speed(self, ms):
        self.anim_speed_ms = ms

    def on_window_resize(self, event):
        if hasattr(self, "canvas") and not self.in_end_screen:
            self.draw_grid_and_bunny()

    def parse_inputs(self):
        try:
            x = int(self.entry_x.get().strip())
            y = int(self.entry_y.get().strip())
            if x < 0 or y < 0 or (x == 0 and y == 0):
                raise ValueError
            return x, y
        except ValueError:
            messagebox.showerror(
                "Invalid Coordinates",
                "Please enter positive integers for X and Y coordinates (e.g., 12, 18).",
            )
            return None, None

    def refresh_all_views(self):
        """Updates Box 2 (Math Engine), Box 1 (Canvas Grid), and Status Labels."""
        self.lbl_gcd_title.config(
            text=f"GREATEST COMMON DIVISOR = {self.gcd_val}"
        )
        self.lbl_gcd_rule.config(
            text=f"Bunny hops Left or Down in quantum leaps of {self.gcd_val} units."
        )

        lines = []
        for s in self.euc_steps:
            lines.append(f"Step {s['step']}: {s['expr']}")
        lines.append(f"Result:  GCD({self.start_x}, {self.start_y}) = {self.gcd_val}")
        self.lbl_euc_text.config(text="\n".join(lines))

        self.txt_hops.config(state="normal")
        self.txt_hops.delete("1.0", tk.END)
        for i in range(len(self.path) - 1):
            hop_str = f"Hop {i+1:02d}: ({self.path[i][0]:2d}, {self.path[i][1]:2d}) ──▶ ({self.path[i+1][0]:2d}, {self.path[i+1][1]:2d})\n"
            self.txt_hops.insert(tk.END, hop_str)
        self.txt_hops.insert(tk.END, f"Target: (00, 00) ★ CARROTS SECURED! ✓\n")
        self.txt_hops.config(state="disabled")

        self.update_sequence_highlight()

        total_hops = len(self.path) - 1
        dist = self.start_x + self.start_y
        self.lbl_metrics.config(
            text=f"Total Hops: {total_hops} | Manhattan Dist: {dist} | Quantum Step: {self.gcd_val}"
        )

        self.draw_grid_and_bunny()

    def update_sequence_highlight(self):
        """Highlights the active hop step in Box 2."""
        self.txt_hops.config(state="normal")
        self.txt_hops.tag_remove("active", "1.0", tk.END)
        self.txt_hops.tag_remove("done", "1.0", tk.END)

        for i in range(self.current_step_idx):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            self.txt_hops.tag_add("done", line_start, line_end)

        active_line = self.current_step_idx + 1
        self.txt_hops.tag_add("active", f"{active_line}.0", f"{active_line}.end")
        self.txt_hops.see(f"{active_line}.0")
        self.txt_hops.config(state="disabled")

    # --------------------------------------------------------------------------
    # BOX 1: RETRO GRID CANVAS RENDERING & PARABOLIC HOP
    # --------------------------------------------------------------------------
    def draw_grid_and_bunny(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            return

        cw = self.canvas.winfo_width() or 680
        ch = self.canvas.winfo_height() or 520
        self.canvas.delete("all")

        margin_left = 65
        margin_bottom = 50
        margin_top = 40
        margin_right = 50

        limit_x = max(20, self.start_x + 2)
        limit_y = max(20, self.start_y + 2)

        usable_w = max(100, cw - margin_left - margin_right)
        usable_h = max(100, ch - margin_top - margin_bottom)
        scale_x = usable_w / limit_x
        scale_y = usable_h / limit_y

        def grid_to_canvas(gx, gy):
            cx = margin_left + gx * scale_x
            cy = (ch - margin_bottom) - gy * scale_y
            return cx, cy

        # Draw 16-Bit Retro Scanline / Grid
        for gx in range(0, limit_x + 1, 2):
            cx, cy0 = grid_to_canvas(gx, 0)
            cx, cy1 = grid_to_canvas(gx, limit_y)
            self.canvas.create_line(
                cx, cy0, cx, cy1, fill=PALETTE["grid_line"], width=1
            )
            # Coordinate label pills
            self.canvas.create_rectangle(
                cx - 11, ch - margin_bottom + 8,
                cx + 11, ch - margin_bottom + 24,
                fill="#16182c", outline=PALETTE["box_border"],
            )
            self.canvas.create_text(
                cx, ch - margin_bottom + 16,
                text=str(gx), font=("Courier", 8, "bold"),
                fill=PALETTE["accent_yellow"],
            )

        for gy in range(0, limit_y + 1, 2):
            cx0, cy = grid_to_canvas(0, gy)
            cx1, cy = grid_to_canvas(limit_x, gy)
            self.canvas.create_line(
                cx0, cy, cx1, cy, fill=PALETTE["grid_line"], width=1
            )
            # Y axis pills
            self.canvas.create_rectangle(
                margin_left - 34, cy - 8,
                margin_left - 8, cy + 8,
                fill="#16182c", outline=PALETTE["box_border"],
            )
            self.canvas.create_text(
                margin_left - 21, cy,
                text=str(gy), font=("Courier", 8, "bold"),
                fill=PALETTE["accent_yellow"],
            )

        # Coordinate Axes with neon arrows
        ox, oy = grid_to_canvas(0, 0)
        max_cx, _ = grid_to_canvas(limit_x, 0)
        _, max_cy = grid_to_canvas(0, limit_y)
        self.canvas.create_line(ox, oy, max_cx + 15, oy, fill=PALETTE["accent_neon"], width=2, arrow=tk.LAST)
        self.canvas.create_line(ox, oy, ox, max_cy - 15, fill=PALETTE["accent_neon"], width=2, arrow=tk.LAST)

        self.canvas.create_text(max_cx + 25, oy, text="X", font=("Courier", 10, "bold"), fill=PALETTE["accent_neon"])
        self.canvas.create_text(ox, max_cy - 25, text="Y", font=("Courier", 10, "bold"), fill=PALETTE["accent_neon"])

        # Origin Carrot Target at (0, 0)
        self.canvas.create_rectangle(
            ox - 24, oy - 24, ox + 24, oy + 24,
            fill="#1d261e", outline=PALETTE["accent_green"], width=1, dash=(3, 2)
        )
        RetroPixelRenderer.draw_sprite(self.canvas, CARROT_SPRITE, ox, oy, pixel_size=2)
        self.canvas.create_text(
            ox + 46, oy + 12,
            text="CARROTS (0,0)",
            font=("Courier", 8, "bold"),
            fill=PALETTE["accent_green"],
        )

        # Start Coordinate Marker
        sx, sy = grid_to_canvas(self.start_x, self.start_y)
        self.canvas.create_rectangle(
            sx - 28, sy - 38, sx + 28, sy - 18,
            fill="#261a35", outline=PALETTE["accent_pink"], width=1
        )
        self.canvas.create_text(
            sx, sy - 28,
            text=f"START ({self.start_x},{self.start_y})",
            font=("Courier", 7, "bold"),
            fill=PALETTE["accent_pink"],
        )

        # Completed Hop Trails
        for i in range(1, self.current_step_idx + 1):
            p1 = self.path[i - 1]
            p2 = self.path[i]
            x1, y1 = grid_to_canvas(*p1)
            x2, y2 = grid_to_canvas(*p2)
            self.canvas.create_line(x1, y1, x2, y2, fill="#501a35", width=4)
            self.canvas.create_line(x1, y1, x2, y2, fill=PALETTE["accent_pink"], width=2, dash=(4, 3))
            self.canvas.create_oval(x2 - 3, y2 - 3, x2 + 3, y2 + 3, fill=PALETTE["accent_yellow"], outline="black")

        # Draw Dust Puff Particles
        surviving_dust = []
        for d in self.dust_particles:
            d["x"] += d["vx"]
            d["y"] += d["vy"]
            d["life"] -= 1
            if d["life"] > 0:
                self.canvas.create_oval(
                    d["x"] - d["size"], d["y"] - d["size"],
                    d["x"] + d["size"], d["y"] + d["size"],
                    fill=d["color"], outline=""
                )
                surviving_dust.append(d)
        self.dust_particles = surviving_dust

        # Current Bunny Position (Interpolated with Parabolic Jump Arc)
        cur_gx, cur_gy = self.current_pos
        cur_cx, cur_cy = grid_to_canvas(cur_gx, cur_gy)
        cur_cy -= self.jump_height  # Parabolic vertical bounce

        # Draw Bunny Sprite
        sprite = BUNNY_SPRITE_HOP if self.jump_height > 2.0 else BUNNY_SPRITE_IDLE
        RetroPixelRenderer.draw_sprite(self.canvas, sprite, cur_cx, cur_cy, pixel_size=2)

        # Coordinate pill below bunny
        display_gx = round(cur_gx)
        display_gy = round(cur_gy)
        self.canvas.create_rectangle(
            cur_cx - 24, cur_cy + 18, cur_cx + 24, cur_cy + 30,
            fill="#121324", outline=PALETTE["accent_neon"], width=1
        )
        self.canvas.create_text(
            cur_cx, cur_cy + 24,
            text=f"({display_gx},{display_gy})",
            font=("Courier", 8, "bold"),
            fill=PALETTE["accent_neon"],
        )

    def spawn_dust_puff(self, cx, cy):
        """Spawns 16-bit dust particles when bunny lands."""
        for _ in range(6):
            self.dust_particles.append({
                "x": cx + random.uniform(-6, 6),
                "y": cy + 12 + random.uniform(-2, 2),
                "vx": random.uniform(-1.5, 1.5),
                "vy": random.uniform(-0.8, -0.1),
                "life": random.randint(6, 12),
                "size": random.choice([2, 3]),
                "color": random.choice(["#5c69a6", "#39437a", "#ffcc00"]),
            })

    # --------------------------------------------------------------------------
    # NAVIGATION LOGIC & SMOOTH PARABOLIC HOP ANIMATION
    # --------------------------------------------------------------------------
    def start_navigation(self):
        if self.is_animating:
            return

        x, y = self.parse_inputs()
        if x is None:
            return

        if (x != self.start_x or y != self.start_y) or self.current_step_idx >= len(self.path) - 1:
            self.start_x, self.start_y = x, y
            self.calculate_euclidean_steps(x, y)
            self.refresh_all_views()

        self.is_animating = True
        self.btn_run.config(state="disabled")
        self.lbl_arena_status.config(text="STATUS: BUNNY HOPPING...", fg=PALETTE["accent_yellow"])
        self.prepare_next_hop()

    def prepare_next_hop(self):
        if not self.is_animating:
            return

        if self.current_step_idx < len(self.path) - 1:
            self.hop_from = self.path[self.current_step_idx]
            self.hop_to = self.path[self.current_step_idx + 1]
            self.hop_substep = 0
            self.animate_hop_substep()
        else:
            self.is_animating = False
            self.btn_run.config(state="normal")
            self.lbl_arena_status.config(text="STATUS: CARROTS REACHED! (0,0) ★", fg=PALETTE["accent_green"])
            self.jump_height = 0.0
            self.current_pos = (float(self.path[-1][0]), float(self.path[-1][1]))
            self.draw_grid_and_bunny()

    def animate_hop_substep(self):
        if not self.is_animating:
            return

        self.hop_substep += 1
        t = self.hop_substep / float(self.total_substeps)

        # Linear coordinate interpolation
        gx = (1.0 - t) * self.hop_from[0] + t * self.hop_to[0]
        gy = (1.0 - t) * self.hop_from[1] + t * self.hop_to[1]
        self.current_pos = (gx, gy)

        # Parabolic jump arc: height peak in the middle
        max_bounce = 24.0
        self.jump_height = 4.0 * max_bounce * t * (1.0 - t)

        self.draw_grid_and_bunny()

        substep_delay = max(15, self.anim_speed_ms // self.total_substeps)

        if self.hop_substep < self.total_substeps:
            self.animation_job = self.root.after(substep_delay, self.animate_hop_substep)
        else:
            # Landed!
            self.current_step_idx += 1
            self.current_pos = (float(self.hop_to[0]), float(self.hop_to[1]))
            self.jump_height = 0.0
            self.update_sequence_highlight()

            # Land dust
            cw = self.canvas.winfo_width() or 680
            ch = self.canvas.winfo_height() or 520
            margin_left, margin_bottom = 65, 50
            limit_x = max(20, self.start_x + 2)
            limit_y = max(20, self.start_y + 2)
            scale_x = max(100, cw - margin_left - 50) / limit_x
            scale_y = max(100, ch - 40 - margin_bottom) / limit_y
            lcx = margin_left + self.hop_to[0] * scale_x
            lcy = (ch - margin_bottom) - self.hop_to[1] * scale_y
            self.spawn_dust_puff(lcx, lcy)
            self.draw_grid_and_bunny()

            # Continue to next hop after a small landing pause
            pause_delay = max(40, self.anim_speed_ms // 3)
            self.animation_job = self.root.after(pause_delay, self.prepare_next_hop)

    def step_forward(self):
        if self.is_animating:
            return
        if self.current_step_idx < len(self.path) - 1:
            self.current_step_idx += 1
            self.current_pos = (float(self.path[self.current_step_idx][0]), float(self.path[self.current_step_idx][1]))
            self.jump_height = 0.0
            self.draw_grid_and_bunny()
            self.update_sequence_highlight()
            if self.current_step_idx == len(self.path) - 1:
                self.lbl_arena_status.config(text="STATUS: CARROTS REACHED! (0,0) ★", fg=PALETTE["accent_green"])

    def reset_simulation(self):
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.is_animating = False
        self.btn_run.config(state="normal")

        x, y = self.parse_inputs()
        if x is not None:
            self.start_x, self.start_y = x, y
            self.calculate_euclidean_steps(x, y)

        self.current_step_idx = 0
        self.current_pos = (float(self.start_x), float(self.start_y))
        self.jump_height = 0.0
        self.lbl_arena_status.config(text="STATUS: READY TO HOP", fg=PALETTE["accent_green"])
        self.refresh_all_views()

    # --------------------------------------------------------------------------
    # USER REQUESTED: END SCREEN WITH FIREWORK PARTICLE EFFECTS
    # --------------------------------------------------------------------------
    def show_end_screen(self):
        """Displays celebration splash screen with fireworks and bold 16-bit title."""
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.is_animating = False
        self.btn_run.config(state="normal")

        self.in_end_screen = True
        self.firework_particles.clear()
        self.firework_rockets.clear()

        # Full overlay canvas
        self.splash_canvas = tk.Canvas(
            self.root,
            bg="#05050d",
            bd=0,
            highlightthickness=0,
        )
        self.splash_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Allow user to click to detonate custom fireworks at cursor!
        self.splash_canvas.bind("<Button-1>", self.on_splash_click)

        # Launch initial salvo of rockets
        for _ in range(4):
            self.launch_rocket()

        self.splash_frame = 0
        self.update_splash_animation()

    def launch_rocket(self, start_x=None, target_y=None):
        cw = self.splash_canvas.winfo_width() or 1240
        ch = self.splash_canvas.winfo_height() or 840
        x = start_x if start_x is not None else random.randint(150, max(200, cw - 150))
        ty = target_y if target_y is not None else random.randint(110, max(180, int(ch * 0.52)))
        colors = [
            PALETTE["accent_neon"],
            PALETTE["accent_pink"],
            PALETTE["accent_yellow"],
            PALETTE["accent_green"],
            PALETTE["accent_orange"],
            PALETTE["accent_purple"],
            "#ffffff",
            "#ff0055",
            "#00ffff",
        ]
        color = random.choice(colors)
        rocket = Rocket(x, ty, color)
        self.firework_rockets.append(rocket)

    def detonate_firework(self, x, y, color):
        """Spawns 50-80 sparkling particles expanding in radial geometry."""
        num_particles = random.randint(55, 80)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 9.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(28, 56)
            size = random.choice([2, 3, 4])
            p = Particle(x, y, color, vx, vy, life, size=size)
            self.firework_particles.append(p)

    def on_splash_click(self, event):
        colors = [
            PALETTE["accent_neon"],
            PALETTE["accent_pink"],
            PALETTE["accent_yellow"],
            PALETTE["accent_green"],
            "#ffffff",
        ]
        self.detonate_firework(event.x, event.y, random.choice(colors))

    def update_splash_animation(self):
        if not self.in_end_screen or not self.splash_canvas.winfo_exists():
            return

        cw = self.splash_canvas.winfo_width() or 1240
        ch = self.splash_canvas.winfo_height() or 840
        self.splash_canvas.delete("all")
        self.splash_frame += 1

        # Periodic rocket launch
        if self.splash_frame % 15 == 0 and len(self.firework_rockets) < 6:
            self.launch_rocket()

        # Update and draw rockets
        surviving_rockets = []
        for r in self.firework_rockets:
            alive = r.update()
            if alive:
                self.splash_canvas.create_oval(
                    r.x - 3, r.y - 3, r.x + 3, r.y + 3,
                    fill=r.color, outline="white"
                )
                self.splash_canvas.create_line(
                    r.x, r.y + 2, r.x - r.vx * 3, r.y + 10,
                    fill=r.color, width=2
                )
                surviving_rockets.append(r)
            else:
                self.detonate_firework(r.x, r.y, r.color)
        self.firework_rockets = surviving_rockets

        # Update and draw particles
        surviving_particles = []
        for p in self.firework_particles:
            alive = p.update()
            if alive:
                s = p.size if p.life > 10 else max(1, p.size - 1)
                self.splash_canvas.create_oval(
                    p.x - s, p.y - s, p.x + s, p.y + s,
                    fill=p.color, outline=""
                )
                surviving_particles.append(p)
        self.firework_particles = surviving_particles

        # Draw Big Bold Retro Arcade Banner Text:
        # "ROBOT GRID NAVIGATION USING EUCLIDEAN ALGORITHM"
        cx = cw / 2
        cy_top = ch * 0.28

        text_line1 = "ROBOT GRID NAVIGATION"
        text_line2 = "USING EUCLIDEAN ALGORITHM"

        # 3D Shadow Layers
        self.splash_canvas.create_text(
            cx + 4, cy_top + 4,
            text=text_line1,
            font=("Courier", 26, "bold"),
            fill="#4a0e4e",
            justify="center",
        )
        self.splash_canvas.create_text(
            cx + 4, cy_top + 50,
            text=text_line2,
            font=("Courier", 24, "bold"),
            fill="#122a5e",
            justify="center",
        )

        self.splash_canvas.create_text(
            cx + 2, cy_top + 2,
            text=text_line1,
            font=("Courier", 26, "bold"),
            fill=PALETTE["accent_pink"],
            justify="center",
        )
        self.splash_canvas.create_text(
            cx + 2, cy_top + 48,
            text=text_line2,
            font=("Courier", 24, "bold"),
            fill=PALETTE["accent_neon"],
            justify="center",
        )

        self.splash_canvas.create_text(
            cx, cy_top,
            text=text_line1,
            font=("Courier", 26, "bold"),
            fill="#ffffff",
            justify="center",
        )
        self.splash_canvas.create_text(
            cx, cy_top + 46,
            text=text_line2,
            font=("Courier", 24, "bold"),
            fill=PALETTE["accent_yellow"],
            justify="center",
        )

        # Subtitle
        sub_y = cy_top + 105
        self.splash_canvas.create_text(
            cx, sub_y,
            text="★ MISSION COMPLETE: BUNNY HARVESTED ALL CARROTS AT (0, 0) ★",
            font=("Courier", 12, "bold"),
            fill=PALETTE["accent_green"],
        )

        # Stats Card
        card_w, card_h = 560, 110
        card_y = sub_y + 35
        self.splash_canvas.create_rectangle(
            cx - card_w/2, card_y,
            cx + card_w/2, card_y + card_h,
            fill="#10132b", outline=PALETTE["box_border_light"], width=2
        )

        total_hops = len(self.path) - 1
        stat_line1 = f"STARTING COORDINATES : ({self.start_x}, {self.start_y})  ➔  TARGET: (0, 0)"
        stat_line2 = f"GREATEST COMMON DIVISOR : {self.gcd_val} (MINIMAL QUANTUM HOP SIZE)"
        stat_line3 = f"TOTAL HOPS TAKEN        : {total_hops} HOPS TO REACH ORIGIN"
        self.splash_canvas.create_text(
            cx, card_y + 26, text=stat_line1, font=("Courier", 10, "bold"), fill=PALETTE["text_light"]
        )
        self.splash_canvas.create_text(
            cx, card_y + 54, text=stat_line2, font=("Courier", 10, "bold"), fill=PALETTE["accent_neon"]
        )
        self.splash_canvas.create_text(
            cx, card_y + 82, text=stat_line3, font=("Courier", 10, "bold"), fill=PALETTE["accent_yellow"]
        )

        # Center Dancing Bunny & Carrot Sprites
        bunny_y = card_y + card_h + 45
        sprite_bunny = BUNNY_SPRITE_HOP if (self.splash_frame % 20 < 10) else BUNNY_SPRITE_IDLE
        RetroPixelRenderer.draw_sprite(self.splash_canvas, sprite_bunny, cx - 40, bunny_y, pixel_size=3)
        RetroPixelRenderer.draw_sprite(self.splash_canvas, CARROT_SPRITE, cx + 40, bunny_y, pixel_size=3)

        btn_y = bunny_y + 55
        self.splash_canvas.create_text(
            cx, btn_y,
            text="[ Click anywhere on screen to launch your own fireworks! ]",
            font=("Courier", 9),
            fill=PALETTE["text_dim"],
        )

        # Return Button
        if self.btn_splash_back is None or not self.btn_splash_back.winfo_exists():
            self.btn_splash_back = tk.Button(
                self.splash_canvas,
                text="◀ RETURN TO GRID ARENA",
                font=("Courier", 11, "bold"),
                bg="#00cc66",
                fg="black",
                activebackground=PALETTE["accent_green"],
                relief="solid",
                bd=2,
                padx=16,
                pady=6,
                command=self.close_end_screen,
            )
            self.splash_canvas.create_window(cx, btn_y + 45, window=self.btn_splash_back)

        self.splash_job = self.root.after(33, self.update_splash_animation)

    def close_end_screen(self):
        """Dismisses the fireworks splash screen and returns to main arena."""
        self.in_end_screen = False
        if self.splash_job:
            self.root.after_cancel(self.splash_job)
            self.splash_job = None
        if self.btn_splash_back:
            self.btn_splash_back.destroy()
            self.btn_splash_back = None
        if self.splash_canvas:
            self.splash_canvas.destroy()
            self.splash_canvas = None
        self.draw_grid_and_bunny()


if __name__ == "__main__":
    root = tk.Tk()
    app = RabbitEuclideanNavApp(root)
    root.mainloop()
