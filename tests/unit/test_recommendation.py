import sys
import os
import importlib
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

rec_module = importlib.import_module("services.recommendation-service.app.main")

calculate_budget_score = rec_module.calculate_budget_score
calculate_interest_score = rec_module.calculate_interest_score
calculate_weather_score = rec_module.calculate_weather_score
calculate_activity_score = rec_module.calculate_activity_score
calculate_distance_score = rec_module.calculate_distance_score

def test_budget_score_calculation():
    score_within = calculate_budget_score(25000.0, 20000.0)
    assert score_within >= 0.8
    assert score_within <= 1.0

    score_over = calculate_budget_score(20000.0, 30000.0)
    assert score_over < 0.8

def test_interest_score_calculation():
    interests = ["Beach", "Adventure"]
    activities = ["Beach Walk", "Water Sports", "Nightlife"]
    score = calculate_interest_score(interests, activities, "Balanced")
    assert score >= 0.70

def test_weather_score_calculation():
    from database.models import WeatherData
    w_good = WeatherData(condition="Sunny & Clear", temperature_celsius=28.0)
    score_good = calculate_weather_score(w_good)
    assert score_good >= 0.90

    w_rain = WeatherData(condition="Heavy Rain", temperature_celsius=22.0)
    score_rain = calculate_weather_score(w_rain)
    assert score_rain < 0.80

def test_distance_score_calculation():
    assert calculate_distance_score(300.0) == 0.95
    assert calculate_distance_score(800.0) == 0.85
    assert calculate_distance_score(2000.0) == 0.65
