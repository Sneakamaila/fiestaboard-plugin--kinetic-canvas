"""Weather resonance generator: maps ambient meteorological conditions to kinetic art."""

from __future__ import annotations
import math
import random
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from ..constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_VIOLET,
    COLOR_WHITE,
    COLOR_YELLOW,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from .base import GenerationResult, GeneratorBase

# WMO Weather interpretation codes
# 0: Clear sky
# 1, 2, 3: Mainly clear, partly cloudy, overcast
# 45, 48: Fog
# 51-55: Drizzle
# 61-65: Rain
# 71-75: Snow
# 80-82: Rain showers
# 95-99: Thunderstorm


class WeatherResonanceGenerator(GeneratorBase):
    """Translates real-time weather (sun, wind, rain, storm) into abstract kinetic compositions."""

    @property
    def name(self) -> str:
        return "weather"

    @property
    def display_name(self) -> str:
        return "Weather Resonance (Wetter-Resonanz)"

    def _fetch_weather(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch current weather from Open-Meteo or return demo weather."""
        is_demo = config.get("demo_mode", False)
        lat = config.get("latitude")
        lon = config.get("longitude")

        if is_demo or lat is None or lon is None:
            # Simulated realistic weather
            return {
                "temperature": 18.5,
                "wind_speed": 14.0,  # km/h
                "precipitation": 1.2,  # mm
                "weather_code": 61,  # Rain
                "city": config.get("city_name") or "Demo Station",
                "is_demo": True,
            }

        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,precipitation,wind_speed_10m,weather_code"
            )
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json().get("current", {})

            return {
                "temperature": data.get("temperature_2m", 20.0),
                "wind_speed": data.get("wind_speed_10m", 10.0),
                "precipitation": data.get("precipitation", 0.0),
                "weather_code": int(data.get("weather_code", 0)),
                "city": config.get("city_name") or f"{lat:.2f}, {lon:.2f}",
                "is_demo": False,
            }
        except Exception:
            # Fallback to calm demo
            return {
                "temperature": 19.0,
                "wind_speed": 12.0,
                "precipitation": 0.0,
                "weather_code": 1,
                "city": config.get("city_name") or "Offline Fallback",
                "is_demo": True,
            }

    def _render_canvas(
        self,
        width: int,
        height: int,
        weather: Dict[str, Any],
        rng: random.Random,
    ) -> List[List[int]]:
        """Generate abstract visual representation corresponding to meteorological parameters."""
        w_code = weather["weather_code"]
        wind = weather["wind_speed"]
        precip = weather["precipitation"]
        temp = weather["temperature"]

        grid = [[COLOR_BLACK for _ in range(width)] for _ in range(height)]

        # Determine dominant theme
        if w_code in [95, 96, 99]:
            # Thunderstorm: violent electric diagonal fissures
            for r in range(height):
                strike_c = int((width / height) * r + rng.randint(-1, 1)) % width
                for c in range(width):
                    if abs(c - strike_c) <= 1:
                        grid[r][c] = rng.choice([COLOR_YELLOW, COLOR_VIOLET, COLOR_WHITE])
                    elif rng.random() < 0.15:
                        grid[r][c] = COLOR_RED
                    else:
                        grid[r][c] = COLOR_BLACK

        elif w_code in [51, 53, 55, 61, 63, 65, 80, 81, 82] or precip > 0.1:
            # Rain: vertical / slanted rain needles
            # Wind creates slant
            slant = max(-2, min(2, int(wind / 15.0)))
            drop_density = min(0.45, 0.12 + (precip * 0.08))

            for c in range(width):
                if rng.random() < drop_density:
                    for r in range(height):
                        sc = (c + r * slant) % width
                        if rng.random() < 0.6:
                            grid[r][sc] = rng.choice([COLOR_BLUE, COLOR_WHITE])

        elif w_code in [71, 73, 75, 85, 86]:
            # Snow: gentle crystal distribution
            for r in range(height):
                for c in range(width):
                    if (r + c) % 3 == 0 and rng.random() < 0.35:
                        grid[r][c] = COLOR_WHITE
                    elif rng.random() < 0.1:
                        grid[r][c] = COLOR_BLUE

        elif w_code in [0, 1]:
            # Sun / Clear: radiant central warmth
            cx = (width - 1) / 2.0
            cy = (height - 1) / 2.0
            for r in range(height):
                for c in range(width):
                    dist = math.sqrt(((c - cx) / (width / 2.0)) ** 2 + ((r - cy) / (height / 2.0)) ** 2)
                    if dist < 0.35:
                        grid[r][c] = COLOR_YELLOW
                    elif dist < 0.7:
                        grid[r][c] = COLOR_ORANGE if temp >= 15 else COLOR_WHITE
                    elif dist < 1.0 and temp >= 25:
                        grid[r][c] = COLOR_RED
                    else:
                        grid[r][c] = COLOR_BLACK

        else:
            # Cloudy / Overcast / Fog: stratified horizontal atmospheric layers
            for r in range(height):
                layer_color = COLOR_WHITE if r % 2 == 0 else COLOR_BLUE
                for c in range(width):
                    # Wind creates horizontal wave displacement
                    wave = int(math.sin(c * 0.5 + r) * 2)
                    if rng.random() < 0.4:
                        grid[r][(c + wave) % width] = layer_color

        return grid

    def generate(
        self,
        previous_flagship: Optional[List[List[int]]],
        previous_note: Optional[List[List[int]]],
        config: Dict[str, Any],
        state: Dict[str, Any],
    ) -> GenerationResult:
        weather = self._fetch_weather(config)
        rng = random.Random(int(time.time() / 60))  # Stable within 1 minute

        flagship = self._render_canvas(FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, weather, rng)
        note = self._render_canvas(NOTE_WIDTH, NOTE_HEIGHT, weather, rng)

        w_code = weather["weather_code"]
        if w_code in [95, 96, 99]:
            condition = "Gewitter (Elektrische Turbulenz)"
        elif w_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            condition = "Regen (Kinetischer Niederschlag)"
        elif w_code in [71, 73, 75]:
            condition = "Schneefall (Kristallines Rauschen)"
        elif w_code in [0, 1]:
            condition = "Klar / Sonnig (Radiante Ruhe)"
        else:
            condition = "Bewölkt / Atmosphärische Schichten"

        title = f"Wetter-Resonanz — {weather['city']}"
        desc = (
            f"{condition}: {weather['temperature']}°C, "
            f"Wind {weather['wind_speed']} km/h, Regen {weather['precipitation']} mm."
        )

        return GenerationResult(
            flagship_matrix=flagship,
            note_matrix=note,
            title=title,
            description=desc,
            metadata=weather,
        )
