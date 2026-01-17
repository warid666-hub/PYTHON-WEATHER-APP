import random
import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
import math

# ---------------- API ----------------
API_KEY = "f9c94055fd01fef113b69c9ecea64f0d"

# ---------------- Tkinter Root ----------------
root = tk.Tk()
root.title("Weather App")
root.geometry("400x600")
root.configure(bg="#87ceeb")

# ---------------- Canvas for animations ----------------
canvas = tk.Canvas(root, bg="#87ceeb", highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

# ---------------- Load Images ----------------
sun_img = Image.open("sun.png").resize((150, 150))
sun_photo = ImageTk.PhotoImage(sun_img)

cloud_img = Image.open("cloud.png").resize((450, 250))
cloud_photo = ImageTk.PhotoImage(cloud_img)

rain_images = []
for _ in range(60):
    img = Image.open("raindrop.png").resize((10, 20))
    rain_images.append(ImageTk.PhotoImage(img))

# ---------------- Global Variables ----------------
rain_drops = []
clouds = []
rays = []
sun_id = None

# ---------------- Animations ----------------
def start_real_rain():
    canvas.delete("all")
    rain_drops.clear()
    width = root.winfo_width()
    height = root.winfo_height()
    for img in rain_images:
        x = random.randint(0, width)
        y = random.randint(0, height)
        drop = canvas.create_image(x, y, image=img)
        rain_drops.append(drop)
    animate_real_rain()

def animate_real_rain():
    width = root.winfo_width()
    height = root.winfo_height()
    for drop in rain_drops:
        canvas.move(drop, 3, 18)
        x, y = canvas.coords(drop)
        if y > height:
            canvas.coords(drop, random.randint(0, width), -20)
    root.after(40, animate_real_rain)

def start_clouds():
    canvas.delete("all")
    clouds.clear()
    width = root.winfo_width()
    height = root.winfo_height()
    for i in range(4):
        x = random.randint(0, width)
        y = random.randint(50, height // 2)
        cloud = canvas.create_image(x, y, image=cloud_photo)
        clouds.append(cloud)
    move_clouds()

def move_clouds():
    width = root.winfo_width()
    for cloud in clouds:
        canvas.move(cloud, 1.5, 0)
        x, y = canvas.coords(cloud)
        if x > width + 100:
            canvas.coords(cloud, -100, y)
    root.after(60, move_clouds)

def animate_sun_glow(scale=1.0, growing=True):
    global sun_photo, sun_id
    if sun_id is None:
        return
    new_size = int(150 * scale)
    img = sun_img.resize((new_size, new_size))
    sun_photo = ImageTk.PhotoImage(img)
    canvas.itemconfig(sun_id, image=sun_photo)

    if growing:
        scale += 0.005
        if scale >= 1.1: growing = False
    else:
        scale -= 0.005
        if scale <= 0.9: growing = True

    root.after(30, animate_sun_glow, scale, growing)

def draw_sun_rays():
    global rays
    canvas.delete("rays")
    if sun_id is None: return
    x, y = canvas.coords(sun_id)
    rays.clear()
    for i in range(12):
        angle = i * (360 / 12)
        length = 120
        end_x = x + length * math.cos(math.radians(angle))
        end_y = y + length * math.sin(math.radians(angle))
        ray = canvas.create_line(x, y, end_x, end_y, fill="#ffe066", width=2, tags="rays")
        rays.append(ray)

def rotate_sun_rays(angle=0):
    if sun_id is None: return
    x, y = canvas.coords(sun_id)
    for i, ray in enumerate(rays):
        ray_angle = angle + i * (360 / len(rays))
        length = 120
        end_x = x + length * math.cos(math.radians(ray_angle))
        end_y = y + length * math.sin(math.radians(ray_angle))
        canvas.coords(ray, x, y, end_x, end_y)
    root.after(50, rotate_sun_rays, angle + 2)

# ---------------- Weather Function ----------------
def get_weather():
    city = city_entry.get().strip()
    if city == "":
        messagebox.showerror("Error", "Enter a city name")
        return

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if str(data.get("cod")) != "200":
            messagebox.showerror("Error", "City not found")
            return

        temp = int(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        weather = data["weather"][0]["description"].title()
        icon_code = data["weather"][0]["icon"]

        # -------- Background color ----------
        weather_lower = weather.lower()
        if "rain" in weather_lower:
            bg_color = "#5f9ea0"
        elif "cloud" in weather_lower:
            bg_color = "#778899"
        elif "snow" in weather_lower:
            bg_color = "#f0f8ff"
        else:
            bg_color = "#87ceeb"

        root.configure(bg=bg_color)
        card.configure(bg="#1e293b")
        canvas.delete("all")

        # -------- Animations ----------
        global sun_id
        if "rain" in weather_lower:
            canvas.configure(bg="#5f9ea0")
            start_real_rain()
        elif "cloud" in weather_lower:
            canvas.configure(bg="#b0c4de")
            start_clouds()
        else:
            canvas.configure(bg="#87ceeb")
            sun_id = canvas.create_image(200, 150, image=sun_photo)
            animate_sun_glow()
            draw_sun_rays()
            rotate_sun_rays()

        # -------- Update UI ----------
        temp_label.config(text=f"{temp}°C")
        desc_label.config(text=f"{weather}\nHumidity: {humidity}%")
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_data = requests.get(icon_url).content
        icon_image = Image.open(io.BytesIO(icon_data))
        icon_photo = ImageTk.PhotoImage(icon_image)
        icon_label.config(image=icon_photo)
        icon_label.image = icon_photo

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- UI ----------------
# Card Frame
card = tk.Frame(root, bg="#1e293b", bd=2, relief="ridge")
card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=600)
card.lift() 

title = tk.Label(card, text="Weather App", font=("Segoe UI", 22, "bold"),
                 bg="#1e293b", fg="white")
title.pack(pady=20)

city_entry = tk.Entry(card, font=("Segoe UI", 14), justify="center")
city_entry.pack(pady=10, ipadx=10, ipady=6)

get_btn = tk.Button(card, text="Get Weather", font=("Segoe UI", 12, "bold"),
                    bg="#38bdf8", fg="black", bd=0, command=get_weather)
get_btn.pack(pady=10, ipadx=20, ipady=6)

icon_label = tk.Label(card, bg="#1e293b")
icon_label.pack(pady=10)

info_frame = tk.Frame(card, bg="#1e293b")
info_frame.pack(pady=10, fill="both")

temp_label = tk.Label(info_frame, text="--°C", font=("Segoe UI", 36, "bold"),
                      bg="#1e293b", fg="white")
temp_label.pack()

desc_label = tk.Label(info_frame, text="", font=("Segoe UI", 16),
                      bg="#1e293b", fg="#cbd5f5")
desc_label.pack()

# ---------------- Run App ----------------
root.mainloop()
