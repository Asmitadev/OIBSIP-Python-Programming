import tkinter as tk
from tkinter import messagebox
import requests
import threading

# ---------- COLORS ----------
BG = "#EAF2F8"
WHITE = "#FFFFFF"
BLUE = "#1769AA"
DARK = "#17324D"
GREY = "#64748B"


# ---------- WEATHER CONDITION ----------
def get_condition(code):
    conditions = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Heavy Drizzle",
        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Slight Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        80: "Rain Showers",
        81: "Moderate Rain Showers",
        82: "Heavy Rain Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Hail",
        99: "Severe Thunderstorm"
    }
    return conditions.get(code, "Variable Conditions")


# ---------- FETCH WEATHER ----------
def fetch_weather(city):
    try:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=15
        )
        geo_response.raise_for_status()
        places = geo_response.json().get("results", [])

        if not places:
            root.after(0, lambda: show_error(
                "City not found. Please check the city name."
            ))
            return

        place = places[0]

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": (
                    "temperature_2m,apparent_temperature,"
                    "relative_humidity_2m,weather_code"
                ),
                "timezone": "auto"
            },
            timeout=15
        )
        weather_response.raise_for_status()
        current = weather_response.json()["current"]

        root.after(
            0,
            lambda: update_weather(place, current)
        )

    except requests.exceptions.RequestException:
        root.after(0, lambda: show_error(
            "Connection failed. Check your internet and try again."
        ))
    except (KeyError, ValueError, IndexError):
        root.after(0, lambda: show_error(
            "Unable to read weather data. Please try again."
        ))


# ---------- SEARCH BUTTON ----------
def search_weather(event=None):
    city = city_entry.get().strip()

    if not city:
        messagebox.showwarning(
            "City Required",
            "Please enter a city name."
        )
        city_entry.focus_set()
        return

    search_button.config(state="disabled", text="Loading...")
    status_label.config(text="Fetching current weather...")

    threading.Thread(
        target=fetch_weather,
        args=(city,),
        daemon=True
    ).start()


# ---------- UPDATE WEATHER DISPLAYS ----------
def update_weather(place, data):
    search_button.config(state="normal", text="Get Weather")

    city_label.config(
        text=f"{place['name']}, {place.get('country', '')}"
    )

    temp_value.config(text=f"{data['temperature_2m']} °C")
    condition_value.config(
        text=get_condition(data["weather_code"])
    )
    feels_value.config(
        text=f"{data['apparent_temperature']} °C"
    )
    humidity_value.config(
        text=f"{data['relative_humidity_2m']}%"
    )

    status_label.config(text="Weather updated successfully.")


# ---------- ERROR MESSAGE ----------
def show_error(message):
    search_button.config(state="normal", text="Get Weather")
    status_label.config(text=message)
    messagebox.showerror("Weather App", message)


# ---------- CLEAR BUTTON ----------
def clear_all():
    city_entry.delete(0, tk.END)

    city_label.config(text="Search for a city")
    temp_value.config(text="-- °C")
    condition_value.config(text="--")
    feels_value.config(text="-- °C")
    humidity_value.config(text="-- %")

    status_label.config(text="Enter a city to view its weather.")
    search_button.config(state="normal", text="Get Weather")
    city_entry.focus_set()


# ---------- WEATHER CARD ----------
def create_card(parent, title, initial_value):
    card = tk.Frame(
        parent,
        bg=WHITE,
        padx=20,
        pady=25,
        highlightbackground="#D5E1EB",
        highlightthickness=1
    )

    tk.Label(
        card,
        text=title,
        font=("Arial", 13, "bold"),
        bg=WHITE,
        fg=GREY
    ).pack(pady=(5, 15))

    value = tk.Label(
        card,
        text=initial_value,
        font=("Arial", 22, "bold"),
        bg=WHITE,
        fg=BLUE,
        wraplength=280
    )
    value.pack(expand=True)

    return card, value


# ---------- MAIN WINDOW ----------
root = tk.Tk()
root.title("OIBSIP Task 4 - Basic Weather App")
root.configure(bg=BG)
root.state("zoomed")
root.minsize(800, 600)

main = tk.Frame(root, bg=BG, padx=35, pady=20)
main.pack(fill="both", expand=True)

# Heading
tk.Label(
    main,
    text="WEATHER APP",
    font=("Arial", 30, "bold"),
    bg=BG,
    fg=DARK
).pack(pady=(5, 5))

tk.Label(
    main,
    text="Check the current weather in your city",
    font=("Arial", 13),
    bg=BG,
    fg=GREY
).pack(pady=(0, 20))

# City input section
search_frame = tk.Frame(main, bg=WHITE, padx=20, pady=18)
search_frame.pack(fill="x", pady=(0, 20))

tk.Label(
    search_frame,
    text="Enter City Name",
    font=("Arial", 12, "bold"),
    bg=WHITE,
    fg=DARK
).pack(anchor="w", pady=(0, 8))

search_row = tk.Frame(search_frame, bg=WHITE)
search_row.pack(fill="x")

city_entry = tk.Entry(
    search_row,
    font=("Arial", 15),
    relief="solid",
    bd=1
)
city_entry.pack(
    side="left", fill="x", expand=True,
    ipady=10, padx=(0, 10)
)
city_entry.insert(0, "Mumbai")

search_button = tk.Button(
    search_row,
    text="Get Weather",
    command=search_weather,
    font=("Arial", 11, "bold"),
    bg=BLUE,
    fg="white",
    activebackground="#12558B",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    padx=22,
    pady=10
)
search_button.pack(side="left", padx=(0, 10))

clear_button = tk.Button(
    search_row,
    text="Clear",
    command=clear_all,
    font=("Arial", 11, "bold"),
    bg="#DCE6F0",
    fg=DARK,
    relief="flat",
    cursor="hand2",
    padx=25,
    pady=10
)
clear_button.pack(side="left")

# Selected city
city_label = tk.Label(
    main,
    text="Search for a city",
    font=("Arial", 20, "bold"),
    bg=BG,
    fg=DARK
)
city_label.pack(pady=(0, 15))

# Four weather displays
cards_frame = tk.Frame(main, bg=BG)
cards_frame.pack(fill="both", expand=True)

for col in range(2):
    cards_frame.grid_columnconfigure(col, weight=1, uniform="cards")

for row in range(2):
    cards_frame.grid_rowconfigure(row, weight=1, uniform="cards")

card1, temp_value = create_card(
    cards_frame, "TEMPERATURE", "-- °C"
)
card1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

card2, condition_value = create_card(
    cards_frame, "WEATHER CONDITION", "--"
)
card2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

card3, feels_value = create_card(
    cards_frame, "FEELS LIKE", "-- °C"
)
card3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

card4, humidity_value = create_card(
    cards_frame, "HUMIDITY", "-- %"
)
card4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

# Status message
status_label = tk.Label(
    main,
    text="Enter a city to view its weather.",
    font=("Arial", 10),
    bg=BG,
    fg=GREY
)
status_label.pack(pady=(12, 5))

tk.Label(
    main,
    text="OIBSIP | Python Programming Internship",
    font=("Arial", 9),
    bg=BG,
    fg=GREY
).pack(pady=(0, 5))

# Enter key also searches
root.bind("<Return>", search_weather)
city_entry.focus_set()

root.mainloop()