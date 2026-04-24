import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from datetime import datetime
import re

# ==============================
# CONFIG
# ==============================
ARCHIVO_CATEGORIAS = "categorias_codigoV2.txt"
ARCHIVO_LOG = "ventas_log.csv"

# ==============================
# ESTADO
# ==============================
imagenes = []
index = 0
categorias = set()
uso_categorias = {}
fecha_carpeta = None

# ==============================
# NORMALIZAR
# ==============================
def normalizar(texto):
    return texto.strip().lower().replace(" ", "_")

# ==============================
# CARGAR CATEGORÍAS
# ==============================
if os.path.exists(ARCHIVO_CATEGORIAS):
    with open(ARCHIVO_CATEGORIAS, "r", encoding="utf-8") as f:
        for linea in f:
            cat = linea.strip()
            if cat:
                categorias.add(cat)
                uso_categorias[cat] = 0

# ==============================
# UI
# ==============================
root = Tk()
root.title("Registro de Ventas")

ancho = root.winfo_screenwidth()
alto = root.winfo_screenheight()
root.geometry(f"{int(ancho*0.9)}x{int(alto*0.7)}")

frame_principal = Frame(root)
frame_principal.pack(fill="both", expand=True)

# IZQUIERDA
frame_izq = Frame(frame_principal)
frame_izq.pack(side="left", padx=10, pady=10)

label_img = Label(frame_izq)
label_img.pack()

label_info = Label(frame_izq, text="")
label_info.pack()

# DERECHA
frame_der = Frame(frame_principal)
frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)

entry = Entry(frame_der, font=("Arial", 16))
entry.pack(fill="x")
entry.focus()

frame_lista = Frame(frame_der)
frame_lista.pack(fill="both", expand=True)

scrollbar = Scrollbar(frame_lista)
scrollbar.pack(side="right", fill="y")

listbox = Listbox(frame_lista, height=15, yscrollcommand=scrollbar.set)
listbox.pack(side="left", fill="both", expand=True)

scrollbar.config(command=listbox.yview)

# ==============================
# FUNCIONES
# ==============================

def extraer_fecha(nombre_carpeta):
    match = re.search(r"\d{4}-\d{2}-\d{2}", nombre_carpeta)
    if match:
        return match.group()
    return datetime.now().strftime("%Y-%m-%d")


def cargar_carpeta():
    global imagenes, index, fecha_carpeta

    carpeta = filedialog.askdirectory()
    if not carpeta:
        return

    nombre = os.path.basename(carpeta)
    fecha_carpeta = extraer_fecha(nombre)

    archivos = os.listdir(carpeta)
    imagenes = [
        os.path.join(carpeta, f)
        for f in archivos
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]

    index = 0
    mostrar_imagen()
    actualizar_lista()


def mostrar_imagen():
    global img_tk

    if index >= len(imagenes):
        label_info.config(text="✅ Terminado")
        label_img.config(image="")
        return

    path = imagenes[index]

    try:
        img = Image.open(path)
        img.thumbnail((700, 700))
        img_tk = ImageTk.PhotoImage(img)

        label_img.config(image=img_tk)
        label_info.config(
            text=f"{index+1}/{len(imagenes)} | {os.path.basename(path)} | 📅 {fecha_carpeta}"
        )
    except:
        avanzar_imagen()


def actualizar_lista(event=None):
    texto = entry.get().lower()
    listbox.delete(0, END)

    coincidencias = [c for c in categorias if texto in c.lower()]
    coincidencias.sort(key=lambda x: (-uso_categorias.get(x, 0), x))

    for cat in coincidencias[:20]:
        listbox.insert(END, cat)

    if listbox.size() > 0:
        listbox.selection_set(0)

# ==============================
# REGISTRAR VENTA (ROBUSTO)
# ==============================
def registrar_venta(event=None):
    if index >= len(imagenes):
        return

    texto = entry.get().strip()
    if not texto:
        return

    partes = texto.split()

    # ===== CANTIDAD SEGURA =====
    cantidad = 1

    if len(partes) >= 2 and partes[-1].isdigit():
        posible = int(partes[-1])

        if 1 <= posible <= 20:
            cantidad = posible
            partes = partes[:-1]

    referencia_input = " ".join(partes)

    referencia_final = None

    # 1. exacto
    if referencia_input in categorias:
        referencia_final = referencia_input

    # 2. solo ID
    elif referencia_input.isdigit():
        for cat in categorias:
            if cat.startswith(referencia_input + "_"):
                referencia_final = cat
                break

    # 3. listbox
    elif listbox.size() > 0 and listbox.curselection():
        referencia_final = listbox.get(listbox.curselection())

    else:
        referencia_final = referencia_input

    if not referencia_final:
        print("⚠️ No se pudo determinar referencia")
        return

    # modelos_id
    try:
        modelos_id = referencia_final.split("_")[0]
    except:
        print("⚠️ Error con referencia")
        return

    fecha = fecha_carpeta

    # ===== GUARDAR CSV =====
    if not os.path.exists(ARCHIVO_LOG) or os.path.getsize(ARCHIVO_LOG) == 0:
     with open(ARCHIVO_LOG, "w", encoding="utf-8") as f:
        f.write("fecha,cantidad,modelos_id\n")

    with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
        f.write(f"{fecha},{cantidad},{modelos_id}\n")

    print(f"💰 Venta: {modelos_id} x{cantidad}")

    uso_categorias[referencia_final] = uso_categorias.get(referencia_final, 0) + 1

    entry.delete(0, END)
    actualizar_lista()


def avanzar_imagen():
    global index
    index += 1
    entry.delete(0, END)
    actualizar_lista()
    mostrar_imagen()


def skip(event=None):
    avanzar_imagen()

# ==============================
# MOUSE (ROBUSTO)
# ==============================
def seleccionar_con_mouse(event):
    widget = event.widget
    try:
        idx = widget.nearest(event.y)
        categoria = widget.get(idx)

        texto_actual = entry.get().strip()
        partes = texto_actual.split()

        cantidad = ""

        if len(partes) >= 2 and partes[-1].isdigit():
            posible = int(partes[-1])
            if 1 <= posible <= 20:
                cantidad = partes[-1]

        nuevo = categoria

        if cantidad:
            nuevo += f" {cantidad}"

        entry.delete(0, END)
        entry.insert(0, nuevo)

    except:
        pass


def doble_click(event):
    seleccionar_con_mouse(event)
    registrar_venta()


def scroll_mouse(event):
    listbox.yview_scroll(int(-1*(event.delta/120)), "units")

# ==============================
# TECLADO
# ==============================
def mover_seleccion(event):
    if listbox.size() == 0:
        return

    listbox.focus_set()

    i = listbox.curselection()
    i = i[0] if i else 0

    if event.keysym == "Down":
        i = min(i + 1, listbox.size() - 1)
    elif event.keysym == "Up":
        i = max(i - 1, 0)

    listbox.selection_clear(0, END)
    listbox.selection_set(i)
    listbox.activate(i)

    return "break"

# ==============================
# BINDS
# ==============================
entry.bind("<KeyRelease>", actualizar_lista)
entry.bind("<Return>", registrar_venta)
entry.bind("<Down>", mover_seleccion)
entry.bind("<Up>", mover_seleccion)

listbox.bind("<Button-1>", seleccionar_con_mouse)
listbox.bind("<Double-Button-1>", doble_click)
listbox.bind("<MouseWheel>", scroll_mouse)
listbox.bind("<Return>", lambda e: registrar_venta())


root.bind("<Right>", skip)

# BOTONES
frame_botones = Frame(root)
frame_botones.pack(pady=10)

Button(frame_botones, text="📂 Seleccionar carpeta", command=cargar_carpeta).pack(side="left", padx=5)
Button(frame_botones, text="⏭ Skip (S / →)", command=skip).pack(side="left", padx=5)

actualizar_lista()
root.mainloop()