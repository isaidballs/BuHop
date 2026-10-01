# 16-Bit Retro Bunny Grid Navigation (Euclidean Algorithm)

An interactive, 16-bit retro arcade-style application demonstrating **Robot Grid Navigation using the Euclidean Algorithm (GCD)**.

The robot is reimagined as a cute pixelated bunny that hops across a coordinate grid towards the carrots cache located at origin `(0, 0)`. The shortest path and minimal uniform step size are calculated using Euclid's GCD algorithm.

---

## Screen Layout (3 Distinct Boxes)

1. **Box 1: Main Arena (Bunny Hopper Grid)**
   - Procedural 16-bit pixel sprites for Bunny and Carrots at `(0, 0)`.
   - 60 FPS parabolic hopping animation with landing dust puffs.
   - Dynamic grid scaling adapting to any input coordinates.
   - Glowing neon dashed hop path and waypoints.

2. **Box 2: Euclid's Algorithm Calculation Engine**
   - Step-by-step Division Algorithm breakdown ($A = B \cdot q + r$).
   - Quantum GCD step size badge.
   - Planned hop sequence with real-time active hop tracking highlighted in glowing retro green.
   - Distance and hop efficiency metrics.

3. **Box 3: Input Area & Mission Control**
   - Coordinate inputs for starting position $(X, Y)$.
   - Quick presets: `(12, 18)`, `(24, 36)`, `(15, 25)`, `(28, 21)`, `(35, 14)`.
   - Speed selector: `Slow`, `Normal`, `Fast`.
   - Controls: `▶ START HOPPING`, `⏭ STEP` (step-by-step manual advance), `↺ RESET`.
   - **`🎆 END SCREEN`** arcade button.

---

## End Screen Celebration (Fireworks Particle Effects)

Pressing the **`🎆 END SCREEN`** button launches a full-screen retro arcade celebration featuring:
- Dynamic particle physics simulation (rising rocket trails, gravity, drag, sparkling embers).
- Multi-colored bursts (Electric Cyan, Hot Pink, Sunburst Yellow, Lime Green, Vivid Orange, Violet).
- **Interactive**: Clicking anywhere on the splash screen launches a custom firework explosion at the cursor.
- Big bold retro title:
  ```
  ROBOT GRID NAVIGATION
  USING EUCLIDEAN ALGORITHM
  ```
- Summary statistics and return button to jump back into the grid arena.

---

## 8-Bit Retro Audio Synthesizer

Built-in chiptune sound generator using the browser's native **Web Audio API** (zero external MP3 files):
- Bouncy upward sweep on hops.
- Low thud on landings.
- Chiptune victory arpeggios when reaching `(0, 0)` and opening the end screen.
- Explosive sawtooth detonations on fireworks.
- Mute/Unmute toggle button.

---

## How to Run

### Web Application (Recommended)
Simply open `index.html` in any web browser:
```bash
open index.html
```
Or serve locally:
```bash
python3 -m http.server 8080
```
Then visit `http://localhost:8080/`.

### Python Desktop App (Tkinter)
```bash
python3 rabbit_grid_euclidean.py
```
