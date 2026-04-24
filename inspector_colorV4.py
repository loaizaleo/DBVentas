import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

# ==============================
# CONFIG
# ==============================
RADIO_MUESTRA = 3

img_original = None
img_tk = None
escala_x = 1
escala_y = 1

ultimo_rgb = None
ultimo_hex = ""


# ==============================
# UTILIDADES
# ==============================
def rgb_a_hex(rgb):
    return '#%02x%02x%02x' % rgb


# ==============================
# CARGAR IMAGEN
# ==============================
def cargar_imagen():
    global img_original, img_tk, escala_x, escala_y

    ruta = filedialog.askopenfilename(
        filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")]
    )

    if not ruta:
        return

    img_original = Image.open(ruta).convert("RGB")

    max_w, max_h = 900, 700
    img_preview = img_original.copy()
    img_preview.thumbnail((max_w, max_h))

    escala_x = img_original.width / img_preview.width
    escala_y = img_original.height / img_preview.height

    img_tk = ImageTk.PhotoImage(img_preview)

    canvas.config(width=img_preview.width, height=img_preview.height)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=img_tk)


# ==============================
# DETECTAR COLOR
# ==============================
def obtener_color(event):
    global ultimo_rgb, ultimo_hex

    if img_original is None:
        return

    x = int(event.x * escala_x)
    y = int(event.y * escala_y)

    if x < 0 or y < 0 or x >= img_original.width or y >= img_original.height:
        return

    x1 = max(0, x - RADIO_MUESTRA)
    x2 = min(img_original.width, x + RADIO_MUESTRA + 1)
    y1 = max(0, y - RADIO_MUESTRA)
    y2 = min(img_original.height, y + RADIO_MUESTRA + 1)

    if x2 <= x1 or y2 <= y1:
        return

    zona = np.array(img_original.crop((x1, y1, x2, y2)))

    rgb = tuple(np.mean(zona.reshape(-1, 3), axis=0).astype(int))
    hex_color = rgb_a_hex(rgb)

    ultimo_rgb = rgb
    ultimo_hex = hex_color

    label_rgb.config(text=f"RGB: {rgb}")
    label_hex.config(text=f"HEX: {hex_color}")
    muestra_color.config(bg=hex_color)

    
# ==============================
# COPIAR RGB
# ==============================
def copiar_color(event):
    if ultimo_rgb is None:
        return

    r, g, b = map(int, ultimo_rgb)
    texto_rgb = f"{r} {g} {b}"

    root.clipboard_clear()
    root.clipboard_append(texto_rgb)

    # Guardar HEX congelado en casilla
    entry_hex.delete(0, tk.END)
    entry_hex.insert(0, ultimo_hex)

    label_hex.config(text=f"RGB copiado: {texto_rgb}")

# ==============================
# COPIAR HEX
# ==============================
def copiar_hex():
    texto_hex = entry_hex.get().strip()

    if not texto_hex:
        return

    root.clipboard_clear()
    root.clipboard_append(texto_hex)

    label_hex.config(text=f"HEX copiado: {texto_hex}")

# ==============================
# MOSTRAR RGB MANUAL
# ==============================
def mostrar_rgb_manual():
    texto = entry_rgb.get().strip()

    try:
        texto = texto.replace(",", " ")
        partes = [int(x) for x in texto.split()]

        if len(partes) != 3:
            raise ValueError

        if not all(0 <= v <= 255 for v in partes):
            raise ValueError

        hex_color = rgb_a_hex(tuple(partes))

        muestra_manual.config(bg=hex_color)

    except:
        messagebox.showerror(
            "Error",
            "Ingresa RGB válido.\nEjemplo:\n248 247 253"
        )


# ==============================
# UI PRINCIPAL
# ==============================
root = tk.Tk()
root.title("Inspector de Color RGB")
root.geometry("1100x550")

frame_principal = tk.Frame(root)
frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

# ------------------------------
# PANEL IZQUIERDO
# ------------------------------
frame_izq = tk.Frame(frame_principal)
frame_izq.pack(side="left", fill="both", expand=True)

btn = tk.Button(frame_izq, text="Cargar Imagen", command=cargar_imagen)
btn.pack(pady=5)

canvas = tk.Canvas(frame_izq, bg="gray")
canvas.pack(fill="both", expand=True)

canvas.bind("<Motion>", obtener_color)
canvas.bind("<Button-1>", copiar_color)

# ------------------------------
# PANEL DERECHO
# ------------------------------
frame_der = tk.Frame(frame_principal, width=300)
frame_der.pack(side="right", fill="y", padx=20)

label_rgb = tk.Label(frame_der, text="RGB:")
label_rgb.pack(pady=5)

label_hex = tk.Label(frame_der, text="HEX:")
label_hex.pack(pady=5)

tk.Label(frame_der, text="Color Detectado:").pack()
muestra_color = tk.Label(frame_der, bg="white", width=20, height=3)
muestra_color.pack(pady=5)

tk.Label(frame_der, text="Ingresar RGB manual:").pack(pady=(20, 5))

entry_rgb = tk.Entry(frame_der, width=25)
entry_rgb.pack()

btn_mostrar = tk.Button(
    frame_der,
    text="Mostrar Color",
    command=mostrar_rgb_manual
)
btn_mostrar.pack(pady=5)

tk.Label(frame_der, text="Color Manual:").pack()
muestra_manual = tk.Label(frame_der, bg="white", width=20, height=3)
muestra_manual.pack(pady=5)

# ------------------------------
# HEX MANUAL
# ------------------------------
tk.Label(frame_der, text="Valor HEX:").pack(pady=(20, 5))

entry_hex = tk.Entry(frame_der, width=25)
entry_hex.pack()

btn_copiar_hex = tk.Button(
    frame_der,
    text="Copiar HEX",
    command=copiar_hex
)
btn_copiar_hex.pack(pady=5)

root.mainloop()