import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def conectar_db():
    conexion = sqlite3.connect('estanciaFraternidad.db')
    cursor = conexion.cursor()
    return conexion, cursor

def crear_tabla():
    conexion, cursor = conectar_db()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        municipio TEXT,
        Direccion TEXT,
        Celular TEXT,
        genero TEXT,
        fecha_registro DATETIME,
        turno TEXT,
        edad INTEGER
    )
    ''')
    conexion.commit()
    conexion.close()

def insertar_persona(nombre, municipio, direccion, celular, genero, edad):
    fecha_actual = datetime.now()

    # Determinar el turno según la hora actual
    hora_actual = fecha_actual.hour
    if 6 <= hora_actual < 12:
        turno = 'Matutino'
    elif 12 <= hora_actual < 18:
        turno = 'Vespertino'
    else:
        turno = 'Nocturno'

    conexion, cursor = conectar_db()
    cursor.execute('''
    INSERT INTO personas (nombre, municipio, Direccion, Celular, genero, edad, fecha_registro, turno)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, municipio, direccion, celular, genero, edad, fecha_actual, turno))
    conexion.commit()
    conexion.close()

def cons_peredad(criterio, edad):
    conexion, cursor = conectar_db()

    if criterio == 'Mayor':
        cursor.execute('SELECT * FROM personas WHERE edad > ?', (edad,))
    elif criterio == 'Menor':
        cursor.execute('SELECT * FROM personas WHERE edad < ?', (edad,))
    elif criterio == 'Igual':
        cursor.execute('SELECT * FROM personas WHERE edad = ?', (edad,))
    else:
        messagebox.showerror("Criterio inválido", "El criterio seleccionado no es válido.")
        conexion.close()
        return []

    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def cons_nombre(nombre):
    conexion, cursor = conectar_db()
    cursor.execute('SELECT * FROM personas WHERE nombre LIKE ?', ('%' + nombre + '%',))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def cons_fecha(fecha):
    """
    Consulta personas registradas en una fecha específica.
    Formato de fecha esperado: YYYY-MM-DD
    """
    conexion, cursor = conectar_db()
    cursor.execute('SELECT * FROM personas WHERE DATE(fecha_registro) = ?', (fecha,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def cons_rango_fechas(fecha_inicio, fecha_fin):
    """
    Consulta personas registradas entre dos fechas.
    Formato de fechas esperado: YYYY-MM-DD
    """
    conexion, cursor = conectar_db()
    cursor.execute('SELECT * FROM personas WHERE DATE(fecha_registro) BETWEEN ? AND ?', (fecha_inicio, fecha_fin))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def obtener_todos_los_registros():
    conexion, cursor = conectar_db()
    cursor.execute('SELECT * FROM personas')
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def eliminar_persona(id_persona):
    conexion, cursor = conectar_db()
    cursor.execute('DELETE FROM personas WHERE id = ?', (id_persona,))
    conexion.commit()
    conexion.close()

# Interfaz gráfica con Tkinter
def iniciar_interfaz():
    crear_tabla()

    ventana = tk.Tk()
    ventana.title("Registro de Personas - Estancia Fraternidad")
    ventana.geometry("1200x800")  # Aumenté el tamaño para acomodar nuevas secciones

    # Marco principal
    marco = tk.Frame(ventana)
    marco.pack(pady=20)

    # Tabla para mostrar los registros
    columnas = ('id', 'nombre', 'municipio', 'Direccion', 'Celular', 'Genero', 'fecha_registro', 'Turno', 'Edad')
    tabla = ttk.Treeview(marco, columns=columnas, show='headings')
    for col in columnas:
        tabla.heading(col, text=col.capitalize())
        tabla.column(col, width=100, anchor=tk.CENTER)  # Ajuste de ancho y alineación
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Barra de desplazamiento
    scrollbar = ttk.Scrollbar(marco, orient=tk.VERTICAL, command=tabla.yview)
    tabla.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    # Función para actualizar la tabla
    def actualizar_tabla(registros):
        for row in tabla.get_children():
            tabla.delete(row)
        for registro in registros:
            tabla.insert('', tk.END, values=registro)

    # Mostrar todos los registros al iniciar
    registros = obtener_todos_los_registros()
    actualizar_tabla(registros)

    # Sección de botones y entradas
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)

    # Botón para insertar una nueva persona
    def abrir_ventana_insertar():
        ventana_insertar = tk.Toplevel()
        ventana_insertar.title("Registrar Persona")
        ventana_insertar.geometry("400x400")

        campos = ['Nombre', 'Municipio', 'Direccion', 'Celular', 'Edad']
        entradas = {}

        for idx, campo in enumerate(campos):
            etiqueta = tk.Label(ventana_insertar, text=campo)
            etiqueta.grid(row=idx, column=0, padx=5, pady=5, sticky=tk.W)
            entrada = tk.Entry(ventana_insertar)
            entrada.grid(row=idx, column=1, padx=5, pady=5)
            entradas[campo.lower()] = entrada

        # Etiqueta y selector para género
        etiqueta_genero = tk.Label(ventana_insertar, text="Género")
        etiqueta_genero.grid(row=len(campos), column=0, padx=5, pady=5, sticky=tk.W)
        
        opciones_genero = ["Masculino", "Femenino"]
        genero_seleccionado = tk.StringVar()
        combobox_genero = ttk.Combobox(ventana_insertar, textvariable=genero_seleccionado, values=opciones_genero, state="readonly")
        combobox_genero.grid(row=len(campos), column=1, padx=5, pady=5)
        combobox_genero.set("Seleccione...")

        def insertar_datos():
            try:
                nombre = entradas['nombre'].get().strip()
                municipio = entradas['municipio'].get().strip()
                direccion = entradas['direccion'].get().strip()
                celular = entradas['celular'].get().strip()
                genero = genero_seleccionado.get().strip()
                edad_str = entradas['edad'].get().strip()

                if not nombre:
                    messagebox.showerror("Error", "El nombre es obligatorio.")
                    return

                if genero not in opciones_genero:
                    messagebox.showerror("Error", "Debe seleccionar un género válido.")
                    return

                if not edad_str:
                    messagebox.showerror("Error", "La edad es obligatoria.")
                    return

                edad = int(edad_str)

                insertar_persona(nombre, municipio, direccion, celular, genero, edad)
                messagebox.showinfo("Éxito", "Persona registrada correctamente.")
                ventana_insertar.destroy()
                actualizar_tabla(obtener_todos_los_registros())
            except ValueError:
                messagebox.showerror("Error", "La edad debe ser un número entero.")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}")

        boton_guardar = tk.Button(ventana_insertar, text="Guardar", command=insertar_datos)
        boton_guardar.grid(row=len(campos)+1, column=0, columnspan=2, pady=10)

    boton_insertar = tk.Button(frame_botones, text="Insertar Persona", command=abrir_ventana_insertar)
    boton_insertar.grid(row=0, column=0, padx=5, pady=5)

    # Botón para buscar por nombre
    def buscar_por_nombre():
        nombre_buscar = entrada_buscar_nombre.get().strip()
        if not nombre_buscar:
            messagebox.showerror("Error", "Debe ingresar un nombre para buscar.")
            return
        registros = cons_nombre(nombre_buscar)
        actualizar_tabla(registros)

    etiqueta_buscar_nombre = tk.Label(frame_botones, text="Buscar por Nombre:")
    etiqueta_buscar_nombre.grid(row=0, column=1, padx=5)
    entrada_buscar_nombre = tk.Entry(frame_botones)
    entrada_buscar_nombre.grid(row=0, column=2, padx=5)
    boton_buscar_nombre = tk.Button(frame_botones, text="Buscar", command=buscar_por_nombre)
    boton_buscar_nombre.grid(row=0, column=3, padx=5, pady=5)

    # Botón para filtrar por edad
    def filtrar_por_edad():
        criterio = criterio_edad.get()
        try:
            edad_str = entrada_edad.get().strip()
            if not edad_str:
                messagebox.showerror("Error", "Debe ingresar una edad para filtrar.")
                return
            edad = int(edad_str)
            registros = cons_peredad(criterio, edad)
            actualizar_tabla(registros)
        except ValueError:
            messagebox.showerror("Error", "Edad debe ser un número entero.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    opciones_criterio = ['Mayor', 'Menor', 'Igual']
    criterio_edad = tk.StringVar(value='Mayor')

    etiqueta_edad = tk.Label(frame_botones, text="Filtrar por Edad:")
    etiqueta_edad.grid(row=1, column=0, padx=5)
    entrada_edad = tk.Entry(frame_botones)
    entrada_edad.grid(row=1, column=1, padx=5)

    menu_criterio = ttk.Combobox(frame_botones, textvariable=criterio_edad, values=opciones_criterio, state='readonly')
    menu_criterio.grid(row=1, column=2, padx=5)
    menu_criterio.set('Mayor')

    boton_filtrar_edad = tk.Button(frame_botones, text="Filtrar", command=filtrar_por_edad)
    boton_filtrar_edad.grid(row=1, column=3, padx=5, pady=5)

    # Botón para mostrar todos los registros
    def mostrar_todos():
        registros = obtener_todos_los_registros()
        actualizar_tabla(registros)

    boton_mostrar_todos = tk.Button(frame_botones, text="Mostrar Todos", command=mostrar_todos)
    boton_mostrar_todos.grid(row=2, column=0, padx=5, pady=5)

    # Botón para eliminar una persona seleccionada
    def eliminar_seleccion():
        seleccionado = tabla.selection()
        if seleccionado:
            valores = tabla.item(seleccionado)['values']
            id_persona = valores[0]
            confirmar = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el registro con ID {id_persona}?")
            if confirmar:
                eliminar_persona(id_persona)
                messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
                actualizar_tabla(obtener_todos_los_registros())
        else:
            messagebox.showwarning("Seleccionar Registro", "Por favor, seleccione un registro para eliminar.")

    boton_eliminar = tk.Button(frame_botones, text="Eliminar Seleccionado", command=eliminar_seleccion)
    boton_eliminar.grid(row=2, column=1, padx=5, pady=5)


    # Botón para buscar por una fecha específica
    def buscar_por_fecha():
        fecha_buscar = entrada_buscar_fecha.get().strip()
        if not fecha_buscar:
            messagebox.showerror("Error", "Debe ingresar una fecha para buscar.")
            return
        # Validar el formato de la fecha
        try:
            datetime.strptime(fecha_buscar, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "El formato de la fecha debe ser YYYY-MM-DD.")
            return
        registros = cons_fecha(fecha_buscar)
        actualizar_tabla(registros)

    etiqueta_buscar_fecha = tk.Label(frame_botones, text="Buscar por Fecha (YYYY-MM-DD):")
    etiqueta_buscar_fecha.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    entrada_buscar_fecha = tk.Entry(frame_botones)
    entrada_buscar_fecha.grid(row=3, column=1, padx=5, pady=5)
    boton_buscar_fecha = tk.Button(frame_botones, text="Buscar Fecha", command=buscar_por_fecha)
    boton_buscar_fecha.grid(row=3, column=2, padx=5, pady=5)

    # Botón buscar por rango de fechas
    def buscar_por_rango_fechas():
        fecha_inicio = entrada_fecha_inicio.get().strip()
        fecha_fin = entrada_fecha_fin.get().strip()
        if not fecha_inicio or not fecha_fin:
            messagebox.showerror("Error", "Debe ingresar ambas fechas para buscar.")
            return
        # Validar formato de las fechas
        try:
            datetime.strptime(fecha_inicio, '%Y-%m-%d')
            datetime.strptime(fecha_fin, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "El formato de las fechas debe ser YYYY-MM-DD.")
            return
        if fecha_inicio > fecha_fin:
            messagebox.showerror("Error", "La fecha de inicio no puede ser posterior a la fecha de fin.")
            return
        registros = cons_rango_fechas(fecha_inicio, fecha_fin)
        actualizar_tabla(registros)

    etiqueta_fecha_inicio = tk.Label(frame_botones, text="Fecha Inicio (YYYY-MM-DD):")
    etiqueta_fecha_inicio.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    entrada_fecha_inicio = tk.Entry(frame_botones)
    entrada_fecha_inicio.grid(row=4, column=1, padx=5, pady=5)
    etiqueta_fecha_fin = tk.Label(frame_botones, text="Fecha Fin (YYYY-MM-DD):")
    etiqueta_fecha_fin.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
    entrada_fecha_fin = tk.Entry(frame_botones)
    entrada_fecha_fin.grid(row=5, column=1, padx=5, pady=5)
    boton_buscar_rango = tk.Button(frame_botones, text="Buscar Rango Fechas", command=buscar_por_rango_fechas)
    boton_buscar_rango.grid(row=4, column=2, padx=5, pady=5, rowspan=2, sticky=tk.W+tk.E)

    # Botón para limpiar filtros y mostrar todos
    def limpiar_filtros():
        entrada_buscar_nombre.delete(0, tk.END)
        entrada_buscar_fecha.delete(0, tk.END)
        entrada_fecha_inicio.delete(0, tk.END)
        entrada_fecha_fin.delete(0, tk.END)
        entrada_edad.delete(0, tk.END)
        menu_criterio.set('Mayor')
        actualizar_tabla(obtener_todos_los_registros())

    boton_limpiar = tk.Button(frame_botones, text="Limpiar Filtros", command=limpiar_filtros)
    boton_limpiar.grid(row=5, column=3, padx=5, pady=5)

    ventana.mainloop()

# MAIN
if __name__ == "__main__":
    iniciar_interfaz()
