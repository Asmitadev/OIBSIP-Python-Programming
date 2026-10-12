# OIBSIP Task 4 - Basic Weather App

## Project Overview
The Basic Weather App is a Python GUI application developed as part of the Oasis Infobyte (OIBSIP) Python Programming Internship. It allows users to search for a city and view its current weather information through a simple and user-friendly interface.

## Features
- Search weather by city name
- Display current temperature in Celsius
- Show weather conditions such as clear sky, cloudy, and rain
- Display the feels-like temperature
- Show relative humidity
- Clear button to reset the search and results
- Maximized graphical interface using Tkinter
- Fetch live weather data without requiring an API key
- Error handling for invalid city names and connection problems

## Technologies Used
- Python
- Tkinter
- Requests library
- Open-Meteo Geocoding API
- Open-Meteo Weather API

## Project Structure
```text
Python-Task4-WeatherApp/
├── weather_app.py
├── README.md
└── .gitignore
```

## Requirements
- Python 3.x
- Requests library
- Internet connection

Tkinter is included with many standard Python installations.

## Installation and Execution

1. Install Python from https://www.python.org/ if it is not already installed.
2. Install the required library:

   ```bash
   pip install requests
   ```

3. Open the project folder in VS Code.
4. Run the application:

   ```bash
   python weather_app.py
   ```

5. Enter a city name and click **Get Weather** to view the current weather information.

## Weather Data
This application uses the Open-Meteo Geocoding API to locate cities and the Open-Mete