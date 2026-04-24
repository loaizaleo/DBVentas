import os
import shutil
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

# ==============================
# CONFIG
# ==============================
DESTINO_BASE = "clasificados"
#ARCHIVO_CATEGORIAS = "categorias_reordenado.txt"
ARCHIVO_CATEGORIAS = "categorias_codigoV2.txt"
# ==============================
# ESTADO
# ==============================
imagenes = []
index = 0
historial = []
categorias = set()
uso_categorias = {}
ultima_categoria = None

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

if os.path.exists(DESTINO_BASE):
    for nombre in os.listdir(DESTINO_BASE):
        categorias.add(nombre)
        uso_categorias.setdefault(nombre, 0)

# ==============================
# UI
# ==============================
# ==============================
# UI
# ==============================
root = Tk()
root.title("Clasificador PRO")
ancho = root.winfo_screenwidth()
alto = root.winfo_screenheight()

# usar 90% del tamaño de la pantalla
root.geometry(f"{int(ancho*0.9)}x{int(alto*0.7)}")

# Frame principal horizontal
frame_principal = Frame(root)
frame_principal.pack(fill="both", expand=True)

# ===== IZQUIERDA (IMAGEN) =====
frame_izq = Frame(frame_principal)
frame_izq.pack(side="left", padx=10, pady=10)

label_img = Label(frame_izq)
label_img.pack()

label_info = Label(frame_izq, text="")
label_info.pack()

# ===== DERECHA (CONTROL) =====
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

def cargar_carpeta():
    global imagenes, index

    carpeta = filedialog.askdirectory()
    if not carpeta:
        return

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
            text=f"{index+1}/{len(imagenes)} | {os.path.basename(path)}"
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


def obtener_categoria():
    texto = normalizar(entry.get())

    if listbox.size() > 0 and listbox.curselection():
        return listbox.get(listbox.curselection())

    return texto


def clasificar(event=None):
    global index, ultima_categoria

    if index >= len(imagenes):
        return

    categoria = obtener_categoria()
    if not categoria:
        return

    if categoria not in categorias:
        categorias.add(categoria)
        uso_categorias[categoria] = 0
        with open(ARCHIVO_CATEGORIAS, "a", encoding="utf-8") as f:
            f.write(categoria + "\n")

    uso_categorias[categoria] += 1
    ultima_categoria = categoria

    destino_carpeta = os.path.join(DESTINO_BASE, categoria)
    os.makedirs(destino_carpeta, exist_ok=True)

    origen = imagenes[index]
    destino = os.path.join(destino_carpeta, os.path.basename(origen))

    shutil.move(origen, destino)
    historial.append((destino, origen))

    avanzar_imagen()


def clasificar_repetir(event=None):
    if ultima_categoria:
        entry.delete(0, END)
        entry.insert(0, ultima_categoria)
        clasificar()


def avanzar_imagen():
    global index

    index += 1
    entry.delete(0, END)
    actualizar_lista()
    mostrar_imagen()


def undo(event=None):
    global index

    if not historial:
        return

    destino, origen = historial.pop()

    try:
        shutil.move(destino, origen)
        index -= 1
        mostrar_imagen()
    except:
        pass


# ==============================
# MOUSE
# ==============================

def seleccionar_con_mouse(event):
    widget = event.widget
    try:
        index_sel = widget.nearest(event.y)
        widget.selection_clear(0, END)
        widget.selection_set(index_sel)

        categoria = widget.get(index_sel)
        entry.delete(0, END)
        entry.insert(0, categoria)
    except:
        pass


def doble_click(event):
    seleccionar_con_mouse(event)
    clasificar()


def scroll_mouse(event):
    listbox.yview_scroll(int(-1*(event.delta/120)), "units")


# ==============================
# TECLADO
# ==============================

def mover_seleccion(event):
    if listbox.size() == 0:
        return

    # mover foco al listbox
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

# ========================================
# FUNCION DE SALTAR O PASAR SIN CLASIFICAR
# ========================================
def skip(event=None):
    global index

    if index >= len(imagenes):
        return

    index += 1
    entry.delete(0, END)
    actualizar_lista()
    mostrar_imagen()

# ==============================
# BINDS
# ==============================

entry.bind("<KeyRelease>", actualizar_lista)
entry.bind("<Return>", clasificar)
entry.bind("<Shift-Return>", clasificar_repetir)
entry.bind("<Down>", mover_seleccion)
entry.bind("<Up>", mover_seleccion)

listbox.bind("<Button-1>", seleccionar_con_mouse)
listbox.bind("<Double-Button-1>", doble_click)
listbox.bind("<MouseWheel>", scroll_mouse)
listbox.bind("<Return>", lambda e: clasificar())

root.bind("<Control-z>", undo)
root.bind("<space>", skip)

frame_botones = Frame(root)
frame_botones.pack(pady=10)

Button(frame_botones, text="📂 Seleccionar carpeta", command=cargar_carpeta).pack(side="left", padx=5)
Button(frame_botones, text="⏭ Skip (Espacio)", command=skip).pack(side="left", padx=5)

actualizar_lista()
root.mainloop()