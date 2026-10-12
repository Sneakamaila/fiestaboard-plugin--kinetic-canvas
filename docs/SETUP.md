# FiestaBoard Kinetic Canvas Setup Guide

This guide walks you through installing and configuring the **Kinetic Canvas & Acoustic Art** plugin for FiestaBoard.

---

## 🚀 Installation into FiestaBoard

1. Copy or clone this repository into your FiestaBoard `plugins/` directory:
   ```bash
   git clone git@github.com:Sneakamaila/fiestaboard-plugin--kinetic-canvas.git plugins/kinetic_canvas
   ```

2. Restart your FiestaBoard server or container.
3. Open the FiestaBoard Web UI at `http://<your-fiestaboard-host>:5000`.
4. Navigate to **Integrations / Plugins** and locate **Kinetic Canvas & Acoustic Art**.
5. Enable the plugin and select your preferred art and acoustic style!

---

## 🎨 Recommended Configurations

### The Meditative Office Companion
* **Mode:** `zen_chime`
* **Chime Style:** `staccato_snap`
* **Refresh Interval:** `1800` (Every 30 minutes)
* **Quiet Hours:** `18:00` to `09:00`
* *Experience:* Every 30 minutes, a single synchronous mechanical click resets the board into an elegant new visual composition.

### The Living Biosphere (Living Room Display)
* **Mode:** `game_of_life`
* **Refresh Interval:** `300` (Every 5 minutes)
* **Quiet Hours:** `22:30` to `07:30` (Behavior: `silent_hold`)
* *Experience:* Conway's Game of Life unfolds in real-time with living, breathing colors and acoustic pulses reflecting the colony's birth and death rate.

### The Dynamic Weather Sculpture
* **Mode:** `weather`
* **Latitude / Longitude:** Your local coordinates
* **City Name:** Your hometown
* *Experience:* Your Vestaboard visually and acoustically resonates with the wind, rain, and daylight outside your window.
