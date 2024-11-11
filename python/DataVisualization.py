from io import BytesIO
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
from datetime import datetime
import requests
import DataLoader

class WeatherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.forecast_frames = []
        self.image_cache = {}

    def run(self):
        root = self.root
        root.title("Weather Forecast App")
        root.geometry("1280x720")
        root.resizable(False, False)

        # Create search bar
        self.search_val = tk.StringVar()
        self.search_entry = ttk.Entry(root, textvariable=self.search_val)
        self.search_entry.pack(pady=10)

        self.results_list = tk.Listbox(root, width=30, height=5)
        self.results_list.pack()

        # Create data containers
        self.create_tiles()

        # Update container data
        def update_results(*args):
            search = self.search_val.get().lower()
            self.results_list.delete(0, tk.END)

            cities = self.get_cities()

            if search:
                results = [city["name"] for city in cities if search in city["name"].lower()]
                for city in results[:5]:
                    self.results_list.insert(tk.END, city)
            
        self.search_val.trace_add("write", update_results)

        # Select city from ListBox
        def select_city(event):
            current_selection = self.results_list.curselection()
            if current_selection:
                selected_city = self.results_list.get(current_selection)
                self.search_val.set(selected_city)
                self.results_list.delete(0, tk.END)
                self.forecast_data = self.get_forecast()
                self.update_forecast_display()
        
        self.results_list.bind("<Double-1>", select_city)

        root.mainloop()

    # Creates the containers for each forecast interval
    def create_tiles(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=20, expand=True, fill=tk.BOTH)

        for i in range(2):  # 2 filas
            for j in range(4):  # 4 columnas
                tile = tk.Frame(frame, relief=tk.RAISED, borderwidth=1)
                tile.grid(row=i, column=j, padx=10, pady=10, sticky="nsew")
                
                date_label = tk.Label(tile, text="Fecha")
                date_label.pack(pady=5)
                
                temp_label = tk.Label(tile, text="Temperatura")
                temp_label.pack(pady=5)
                
                image_label = tk.Label(tile)
                image_label.pack(pady=5)
                
                desc_label = tk.Label(tile, text="Descripción")
                desc_label.pack(pady=5)
                
                self.forecast_frames.append({
                    "date": date_label,
                    "temp": temp_label,
                    "image": image_label,
                    "desc": desc_label
                })
        
        for i in range(2):
            frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            frame.grid_columnconfigure(j, weight=1)

    # Updates the forecast data in the containers
    def update_forecast_display(self):
        for i, day_forecast in enumerate(self.forecast_data[:8]):
            dt = datetime.fromtimestamp(day_forecast["dt"]).strftime("%A - %H:%M")
            temp = f"{day_forecast["main"]["temp"]} °C"
            desc = day_forecast["weather"][0]["description"]
            icon_code = day_forecast["weather"][0]["icon"]

            self.forecast_frames[i]["date"].config(text=dt)
            self.forecast_frames[i]["temp"].config(text=temp)
            self.get_image(self.forecast_frames[i]["image"], icon_code, desc)
            self.forecast_frames[i]["desc"].config(text=desc)

    # Returns the list of cities available for forecasting
    def get_cities(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "..", "sources", "cities.json")

        with open(file_path, encoding="utf8") as file:
                data = json.load(file)

        return data["results"]
    
    # Returns an image based on the forecast
    def get_image(self, image_label, icon_code, desc):
        if desc in self.image_cache:
            image_label.config(image=self.image_cache[desc])
        else:
            response = requests.get(f"https://openweathermap.org/img/wn/{icon_code}@4x.png")
            img_data = Image.open(BytesIO(response.content))
            img = ImageTk.PhotoImage(img_data.resize((100, 100)))  # Ajusta el tamaño según necesites
            self.image_cache[desc] = img
            image_label.config(image=img)
            image_label.image = img  # Mantener una referencia
    
    # Returns the forecast data
    def get_forecast(self):
        data = DataLoader.get_weather_data(self.search_val.get())
        return data