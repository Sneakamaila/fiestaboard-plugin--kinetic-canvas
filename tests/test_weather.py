"""Unit tests for weather resonance with mocked Open-Meteo HTTP responses."""

import responses
from plugins.kinetic_canvas.constants import (
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from plugins.kinetic_canvas.generators.weather import WeatherResonanceGenerator


@responses.activate
def test_weather_thunderstorm_mock():
    gen = WeatherResonanceGenerator()
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=52.52&longitude=13.405"
        "&current=temperature_2m,precipitation,wind_speed_10m,weather_code"
    )
    responses.add(
        responses.GET,
        url,
        json={
            "current": {
                "temperature_2m": 24.5,
                "wind_speed_10m": 45.0,
                "precipitation": 12.0,
                "weather_code": 95,  # Thunderstorm
            }
        },
        status=200,
    )

    res = gen.generate(
        None,
        None,
        {"latitude": 52.52, "longitude": 13.405, "demo_mode": False, "city_name": "Berlin"},
        {},
    )
    assert "Gewitter" in res.description
    assert len(res.flagship_matrix) == FLAGSHIP_HEIGHT
    assert len(res.flagship_matrix[0]) == FLAGSHIP_WIDTH


@responses.activate
def test_weather_snow_mock():
    gen = WeatherResonanceGenerator()
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=47.37&longitude=8.54"
        "&current=temperature_2m,precipitation,wind_speed_10m,weather_code"
    )
    responses.add(
        responses.GET,
        url,
        json={
            "current": {
                "temperature_2m": -2.0,
                "wind_speed_10m": 8.0,
                "precipitation": 2.5,
                "weather_code": 71,  # Snow
            }
        },
        status=200,
    )

    res = gen.generate(
        None,
        None,
        {"latitude": 47.37, "longitude": 8.54, "demo_mode": False, "city_name": "Zürich"},
        {},
    )
    assert "Schneefall" in res.description


@responses.activate
def test_weather_sun_mock():
    gen = WeatherResonanceGenerator()
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=41.9&longitude=12.5"
        "&current=temperature_2m,precipitation,wind_speed_10m,weather_code"
    )
    responses.add(
        responses.GET,
        url,
        json={
            "current": {
                "temperature_2m": 28.0,
                "wind_speed_10m": 5.0,
                "precipitation": 0.0,
                "weather_code": 0,  # Clear sky
            }
        },
        status=200,
    )

    res = gen.generate(
        None,
        None,
        {"latitude": 41.9, "longitude": 12.5, "demo_mode": False, "city_name": "Rom"},
        {},
    )
    assert "Klar" in res.description or "Sonnig" in res.description


@responses.activate
def test_weather_http_failure_fallback():
    gen = WeatherResonanceGenerator()
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=50.0&longitude=10.0"
        "&current=temperature_2m,precipitation,wind_speed_10m,weather_code"
    )
    responses.add(responses.GET, url, status=500)

    # Should gracefully fallback to calm demo mode without throwing
    res = gen.generate(
        None,
        None,
        {"latitude": 50.0, "longitude": 10.0, "demo_mode": False},
        {},
    )
    assert len(res.flagship_matrix) == FLAGSHIP_HEIGHT
    assert res.metadata["is_demo"] is True
