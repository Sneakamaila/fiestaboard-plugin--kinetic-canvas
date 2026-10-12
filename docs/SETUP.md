# FiestaBoard Kinetic Canvas Setup & Layout Guide 🎨

This guide walks you through installing, configuring, and layouting your **Kinetic Canvas & Acoustic Art** pages in FiestaBoard.

---

## 🚀 1. Installation into FiestaBoard

1. In the FiestaBoard Web UI, go to **Plugins / Store**, search for **Kinetic Canvas & Acoustic Art** (or install from GitHub repository `Sneakamaila/fiestaboard-plugin--kinetic-canvas`).
2. Click **Install**.
3. Enable the plugin under **Integrations > Kinetic Canvas**.

---

## 📐 2. How to Layout Your Pages (Super Easy!)

You have two great ways to set up your pages:

### Option A: The 1-Click Template (Recommended — Zero Typing!)
When you install the plugin, FiestaBoard offers a pre-built **Demo Page**:
* Simply click **„Add Demo Page / Aus Vorlage erstellen“**.
* FiestaBoard automatically creates a complete, perfectly formatted 6-line page using:
  ```text
  {{kinetic_canvas.flagship_line1}}
  {{kinetic_canvas.flagship_line2}}
  {{kinetic_canvas.flagship_line3}}
  {{kinetic_canvas.flagship_line4}}
  {{kinetic_canvas.flagship_line5}}
  {{kinetic_canvas.flagship_line6}}
  ```
* **Switch Layouts in Settings:** You don't need to touch the page layout again! In the plugin settings (**Settings > Board Layout Preset**), choose:
  * **Pure Full-Screen Canvas (`full_canvas`):** 100% abstract art across all 6 rows.
  * **Art Canvas with Sound Badge (`canvas_with_info`):** 4 rows of art, Row 5 shows the artwork title, Row 6 shows the acoustic waveform `[ ▂▄▆█▆▄▂ ]` and mechanical clicks!

---

### Option B: Manual Layout Presets

If you prefer to manually craft or customize your FiestaBoard pages, copy and paste these exact templates:

#### Layout 1: Pure Full-Screen Canvas (Vestaboard Flagship 22×6)
Line by line:
1. `{{kinetic_canvas.canvas_flagship_line1}}`
2. `{{kinetic_canvas.canvas_flagship_line2}}`
3. `{{kinetic_canvas.canvas_flagship_line3}}`
4. `{{kinetic_canvas.canvas_flagship_line4}}`
5. `{{kinetic_canvas.canvas_flagship_line5}}`
6. `{{kinetic_canvas.canvas_flagship_line6}}`

#### Layout 2: Art with Title & Acoustic Score (Vestaboard Flagship 22×6)
Line by line:
1. `{{kinetic_canvas.canvas_flagship_line1}}`
2. `{{kinetic_canvas.canvas_flagship_line2}}`
3. `{{kinetic_canvas.canvas_flagship_line3}}`
4. `{{kinetic_canvas.canvas_flagship_line4}}`
5. `{{kinetic_canvas.title}}`
6. `[{{kinetic_canvas.acoustic_sparkline}}] {{kinetic_canvas.total_clicks}} CLICKS`

#### Layout 3: Vestaboard Note (15×3)
Line by line:
1. `{{kinetic_canvas.note_line1}}`
2. `{{kinetic_canvas.note_line2}}`
3. `{{kinetic_canvas.note_line3}}`

---

## 🎨 3. Recommended Experiences & Styles

### 🟥 The Modern Art Gallery (Mondrian)
* **Mode:** `mondrian`
* **Layout Preset:** `full_canvas`
* **Refresh:** `600` (Every 10 minutes)
* *Experience:* Pure Piet Mondrian abstract compositions with bold primary color fields and black dividers.

### 🧬 The Living Biosphere (Conway's Game of Life)
* **Mode:** `game_of_life`
* **Layout Preset:** `canvas_with_info`
* **Refresh:** `300` (Every 5 minutes)
* *Experience:* Watch generations evolve in real-time. Sound cascades reflect births and deaths; Row 6 visualizes the biological pulse.

### 🔔 The Zen Meditation Chime
* **Mode:** `zen_chime`
* **Chime Style:** `staccato_snap` (or `acoustic_wave`)
* **Refresh:** `1800` (Every 30 minutes)
* *Experience:* Acts like a modern mechanical grandfather clock. Exactly on schedule, an audible acoustic chime snaps across the board, revealing a serene new abstract canvas.

### 🌦️ The Ambient Weather Sculpture
* **Mode:** `weather`
* **Latitude / Longitude:** Your local GPS coordinates
* **City Name:** Your hometown
* *Experience:* Resonates with outdoor weather: rain streaks, radiant sun rings, or stormy fissures.
