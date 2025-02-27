import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from sqlalchemy import create_engine, Column, String, Date, CHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Configuración de la conexión a PostgreSQL con SQLAlchemy
DATABASE_URL = "postgresql://sistemashm:Mixcoatl120.@localhost:5432/personas"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Definir la tabla como un modelo ORM
class Persona(Base):
    __tablename__ = "personas"
    cve = Column(String(50), primary_key=True)
    nombre = Column(String(100))
    paterno = Column(String(100))
    materno = Column(String(100))
    fecnac = Column(Date)
    sexo = Column(CHAR(1))
    calle = Column(String(150))
    int = Column(String(50))
    ext = Column(String(50))
    colonia = Column(String(150))
    cp = Column(String(50))
    e = Column(String(50))
    d = Column(String(50))
    m = Column(String(50))
    s = Column(String(50))
    l = Column(String(50))
    mza = Column(String(50))
    consec = Column(String(50))
    cred = Column(String(50))
    folio = Column(String(50))
    nac = Column(String(50))
    curp = Column(String(50))

def insertar_persona():
    try:
        nueva_persona = Persona(
            **{campo: entry.get() for campo, entry in zip(campos, entradas)}
        )
        session.add(nueva_persona)
        session.commit()
        messagebox.showinfo("Éxito", "Persona agregada correctamente")
        listar_personas()
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"No se pudo agregar la persona: {e}")

def listar_personas(filtro=None):
    for row in tabla.get_children():
        tabla.delete(row)
    
    if filtro:
        query = session.query(Persona)
        condiciones = [getattr(Persona, campo).ilike(f'%{filtro}%') for campo in campos]
        query = query.filter(*condiciones)
    
        personas = query.all()
        for persona in personas:
            tabla.insert("", "end", values=[getattr(persona, campo) for campo in campos])

def mostrar_info(event):
    seleccionado = tabla.selection()
    if not seleccionado:
        return
    
    valores = tabla.item(seleccionado, "values")
    ventana = tk.Toplevel(root)
    ventana.title("Información de Persona")
    
    for i, campo in enumerate(campos):
        tk.Label(ventana, text=f"{campo}: {valores[i]}").grid(row=i, column=0, sticky="w", padx=10, pady=2)

def cargar_excel():
    archivo = filedialog.askopenfilename(parent=root, filetypes=[("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*")])
    if not archivo:
        return
    
    try:
        df = pd.read_excel(archivo, engine='openpyxl')
        df.columns = df.columns.str.lower()
        if 'fecnac' in df.columns:
            df['fecnac'] = pd.to_datetime(df['fecnac'], format='%d/%m/%Y', errors='coerce')
            df['fecnac'] = df['fecnac'].apply(lambda x: x.date() if pd.notna(x) else None)
        
        for _, row in df.iterrows():
            datos = row.to_dict()
            if datos.get('fecnac') is None:
                datos['fecnac'] = None
            
            persona = Persona(**datos)
            session.add(persona)
        
        session.commit()
        messagebox.showinfo("Éxito", "Datos importados correctamente")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"No se pudo importar el archivo: {e}")

# Interfaz gráfica
root = tk.Tk()
root.title("Gestión de Personas")
root.geometry("1000x600")

frame_principal = tk.Frame(root)
frame_principal.pack(fill="both", expand=True)

frame_izquierda = tk.Frame(frame_principal)
frame_izquierda.pack(side="left", fill="y", expand=False)

frame_derecha = tk.Frame(frame_principal)
frame_derecha.pack(side="right", fill="both", expand=True)

campos = ["cve", "nombre", "paterno", "materno", "fecnac", "sexo", "calle", "int", "ext", "colonia", "cp", "e", "d", "m", "s", "l","mza","consec", "cred", "folio", "nac", "curp"]
entradas = []

for i, campo in enumerate(campos):
    tk.Label(frame_izquierda, text=campo).grid(row=i, column=0, sticky="w")
    entry = tk.Entry(frame_izquierda)
    entry.grid(row=i, column=1)
    entradas.append(entry)

tk.Button(frame_izquierda, text="Agregar", command=insertar_persona).grid(row=len(campos), column=0, columnspan=2)
tk.Button(frame_izquierda, text="Cargar Excel", command=cargar_excel).grid(row=len(campos)+1, column=0, columnspan=2)

entry_busqueda = tk.Entry(frame_izquierda)
entry_busqueda.grid(row=len(campos)+2, column=1)
tk.Button(frame_izquierda, text="Buscar", command=lambda: listar_personas(entry_busqueda.get())).grid(row=len(campos)+3, column=0, columnspan=2)

frame_tabla = tk.Frame(frame_derecha)
frame_tabla.pack(fill="both", expand=True)

scroll_y = tk.Scrollbar(frame_tabla, orient='vertical')
scroll_x = tk.Scrollbar(frame_tabla, orient='horizontal')

tabla = ttk.Treeview(frame_tabla, columns=campos, show="headings", height=15, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
for col in campos:
    tabla.heading(col, text=col)
    tabla.column(col, width=120, anchor="w")

tabla.pack(fill='both', expand=True)
scroll_y.config(command=tabla.yview)
scroll_x.config(command=tabla.xview)
scroll_y.pack(side='right', fill='y')
scroll_x.pack(side='bottom', fill='x')

tabla.bind("<Double-1>", mostrar_info)

root.mainloop()
