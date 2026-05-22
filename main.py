import flet as ft
import json
import os

ARCHIVO_DATOS = "datos_garaje_v12.json"

MANTENIMIENTOS_REF = {
    "Aceite": 7500, "Filtro Aceite": 13000, "Filtro Aire": 25000,
    "Filtro Habitaculo": 25000, "Bujias": 50000, "Correas Aux": 65000, 
    "Distribucion": 85000, "Neumaticos": 40000, "Pastillas Freno": 50000, 
    "Discos Freno": 80000
}

RUTAS_DEFECTO = {
    "💼 Trabajo (Ida/Vuelta)": 30.0,
    "🛒 Supermercado": 12.5,
    "⛰️ Escapada Finde": 150.0
}

class MiGarajeMovilApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Garaje Pro"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#121824"
        self.page.padding = 15
        
        self.datos = self.cargar_datos()
        self.coche_activo = list(self.datos.keys())[0]
        
        # Elementos de interfaz globales
        self.combo = ft.Dropdown(
            options=[ft.dropdown.Option(c) for c in self.datos.keys()],
            value=self.coche_activo,
            on_change=self.cambiar_de_coche,
            expand=True,
            color="#ffffff",
            border_color="#38bdf8"
        )
        
        self.contenido_pestana = ft.Container(expand=True)
        
        # Barra de navegación inferior (Idéntica a tus 3 pestañas)
        self.nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.⚡, label="ESTADO"),
                ft.NavigationDestination(icon=ft.icons.BUILD, label="HISTORIAL"),
                ft.NavigationDestination(icon=ft.icons.PLACE, label="RUTAS"),
            ],
            selected_index=0,
            on_change=self.navegar,
            bgcolor="#1e2640",
        )
        
        # Inicializar inputs para la pestaña de historial
        self.inputs_km = {}
        self.inputs_nota = {}
        
        # Construcción de la App
        self.page.add(
            ft.Row([
                self.combo,
                ft.IconButton(ft.icons.ADD, on_click=self.añadir_vehiculo, icon_color="#22c55e"),
                ft.IconButton(ft.icons.EDIT, on_click=self.editar_nombre_vehiculo, icon_color="#eab308"),
                ft.IconButton(ft.icons.DELETE, on_click=self.eliminar_vehiculo, icon_color="#ef4444")
            ]),
            self.contenido_pestana,
            self.nav_bar
        )
        
        self.dibujar_todo()

    def cargar_datos(self):
        if os.path.exists(ARCHIVO_DATOS):
            try:
                with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                for coche in datos:
                    if "rutas" not in datos[coche]:
                        datos[coche]["rutas"] = RUTAS_DEFECTO.copy()
                    datos[coche]["km"] = float(datos[coche]["km"])
                return datos
            except: pass
        
        return {
            "Mi Coche": {
                "km": 0.0, 
                "piezas": {n: {"km": 0, "nota": ""} for n in MANTENIMIENTOS_REF},
                "rutas": RUTAS_DEFECTO.copy()
            }
        }

    def guardar(self):
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(self.datos, f, indent=4)

    def cambiar_de_coche(self, e):
        self.coche_activo = self.combo.value
        self.dibujar_todo()

    def navegar(self, e):
        self.dibujar_todo()

    def dibujar_todo(self):
        idx = self.nav_bar.selected_index
        if idx == 0:
            self.dibujar_estado()
        elif idx == 1:
            self.dibujar_historial()
        elif idx == 2:
            self.dibujar_rutas()

    # --- PESTAÑA 1: ESTADO ACTUAL (IDÉNTICA A TU TKINTER) ---
    def dibujar_estado(self):
        coche = self.datos[self.coche_activo]
        km_pantalla = int(coche["km"])
        
        # Dropdown para simular "Estoy en el coche"
        self.combo_rutas_drive = ft.Dropdown(
            options=[ft.dropdown.Option(r) for r in coche["rutas"].keys()],
            value=list(coche["rutas"].keys())[0] if coche["rutas"] else None,
            expand=True,
            border_color="#94a3b8"
        )
        
        lista_piezas = ft.ListView(expand=True, spacing=8)
        
        for p, intervalo in MANTENIMIENTOS_REF.items():
            info = coche["piezas"].get(p, {"km": 0, "nota": ""})
            uso = km_pantalla - info["km"]
            
            color_alerta = "#10b981" 
            if uso >= intervalo: color_alerta = "#ef4444" 
            elif uso >= intervalo * 0.8: color_alerta = "#f97316" 
            
            # Replicar lógica de botones de enlaces (🔗 Link o ℹ️ Info)
            btn_nota = None
            if info["nota"]:
                txt_b = "🔗 Link" if info["nota"].startswith("http") else "ℹ️ Info"
                btn_nota = ft.TextButton(
                    txt_b, 
                    on_click=lambda e, url=info["nota"]: self.page.launch_url(url) if url.startswith("http") else self.mostrar_alerta("Ficha de Repuesto", url),
                    style=ft.ButtonStyle(color="#38bdf8")
                )

            lista_piezas.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.VerticalDivider(width=5, color=color_alerta, thickness=5),
                        ft.Column([
                            ft.Text(p, weight=ft.FontWeight.BOLD, size=15, color="#ffffff"),
                            ft.Text(f"Uso: {uso:,} / {intervalo:,} km".replace(",", "."), color="#94a3b8", size=13)
                        ], expand=True),
                        btn_nota if btn_nota else ft.Container()
                    ]),
                    bgcolor="#1e2640",
                    padding=10,
                    border_radius=10
                )
            )

        self.contenido_pestana.content = ft.Column([
            # Header Card
            ft.Container(
                content=ft.Column([
                    ft.Text(self.coche_activo.upper(), size=11, color="#94a3b8", weight=ft.FontWeight.BOLD),
                    ft.Text(f"{km_pantalla:,} KM".replace(",", "."), size=26, color="#38bdf8", weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("MODIFICAR KM MANUAL", on_click=self.set_km_coche, bgcolor="#2563eb", color="white", size=12)
                ]),
                bgcolor="#1e2640", padding=15, border_radius=12
            ),
            # Card "Estoy en el coche"
            ft.Container(
                content=ft.Column([
                    ft.Text("🚗 ESTOY EN EL COCHE", size=12, color="#38bdf8", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        self.combo_rutas_drive,
                        ft.ElevatedButton("SUMAR", on_click=self.sumar_ruta_automatica, bgcolor="#22c55e", color="white")
                    ])
                ]),
                bgcolor="#1e2640", padding=12, border_radius=12
            ),
            lista_piezas
        ], expand=True)
        self.page.update()

    # --- PESTAÑA 2: CONFIGURAR ÚLTIMO CAMBIO ---
    def dibujar_historial(self):
        coche = self.datos[self.coche_activo]
        lista_inputs = ft.ListView(expand=True, spacing=8)
        
        self.inputs_km.clear()
        self.inputs_nota.clear()
        
        for p in MANTENIMIENTOS_REF:
            info = coche["piezas"].get(p, {"km": 0, "nota": ""})
            
            input_km = ft.TextField(value=str(info["km"]), width=80, text_align=ft.TextAlign.CENTER, bgcolor="#121824", border_radius=6, border_width=0)
            input_nota = ft.TextField(value=info["nota"], expand=True, bgcolor="#121824", border_radius=6, border_width=0, hint_text="Nota o Link")
            
            self.inputs_km[p] = input_km
            self.inputs_nota[p] = input_nota
            
            lista_inputs.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(p, weight=ft.FontWeight.BOLD, color="#ffffff", size=14),
                        ft.Row([
                            ft.Text("KM:", color="#94a3b8", size=12),
                            input_km,
                            ft.Text("Nota:", color="#94a3b8", size=12),
                            input_nota
                        ])
                    ]),
                    bgcolor="#1e2640", padding=10, border_radius=10
                )
            )
            
        self.contenido_pestana.content = ft.Column([
            ft.Text("CONFIGURAR ÚLTIMO CAMBIO", weight=ft.FontWeight.BOLD, color="#ffffff", size=14),
            lista_inputs,
            ft.ElevatedButton("GUARDAR CAMBIOS", on_click=self.guardar_historial, bgcolor="#22c55e", color="white", width=500)
        ], expand=True)
        self.page.update()

    # --- PESTAÑA 3: GESTIONAR RUTAS ---
    def dibujar_rutas(self):
        coche = self.datos[self.coche_activo]
        lista_rutas = ft.ListView(expand=True, spacing=8)
        self.inputs_rutas = {}
        
        for r_nombre, r_km in coche.get("rutas", {}).items():
            input_r_km = ft.TextField(value=str(r_km), width=70, text_align=ft.TextAlign.CENTER, bgcolor="#121824", border_width=0)
            self.inputs_rutas[r_nombre] = input_r_km
            
            lista_rutas.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(r_nombre, weight=ft.FontWeight.BOLD, color="#ffffff", expand=True),
                        input_r_km,
                        ft.Text("km", color="#94a3b8"),
                        ft.IconButton(ft.icons.CLOSE, on_click=lambda e, name=r_nombre: self.borrar_ruta_individual(name), icon_color="#ef4444")
                    ]),
                    bgcolor="#1e2640", padding=10, border_radius=10
                )
            )
            
        self.contenido_pestana.content = ft.Column([
            ft.Row([
                ft.Text("MIS RUTAS HABITUALES", weight=ft.FontWeight.BOLD, color="#ffffff", expand=True),
                ft.ElevatedButton("+ Nueva Ruta", on_click=self.crear_nueva_ruta, bgcolor="#22c55e", color="white")
            ]),
            lista_rutas,
            ft.ElevatedButton("GUARDAR DISTANCIAS DE RUTAS", on_click=self.guardar_cambios_rutas, bgcolor="#2563eb", color="white", width=500)
        ], expand=True)
        self.page.update()

    # --- ACCIONES LOGICAS COPIADAS FIELMENTE DE TU SCRIPT ---
    def set_km_coche(self, e):
        def salvar(ev):
            if dialog_input.value:
                self.datos[self.coche_activo]["km"] = float(dialog_input.value)
                self.guardar()
                self.page.dialog.open = False
                self.dibujar_todo()

        dialog_input = ft.TextField(label="Kilómetros", value=str(int(self.datos[self.coche_activo]["km"])))
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Odometer"),
            content=dialog_input,
            actions=[ft.ElevatedButton("OK", on_click=salvar)]
        )
        self.page.dialog.open = True
        self.page.update()

    def sumar_ruta_automatica(self, e):
        ruta_seleccionada = self.combo_rutas_drive.value
        if ruta_seleccionada:
            kms_a_sumar = self.datos[self.coche_activo]["rutas"][ruta_seleccionada]
            self.datos[self.coche_activo]["km"] += kms_a_sumar
            self.guardar()
            self.dibujar_todo()
            self.mostrar_alerta("Viaje Registrado", f"Se han sumado {kms_a_sumar} km a tu {self.coche_activo}.")

    def guardar_historial(self, e):
        try:
            km_max_coche = int(self.datos[self.coche_activo]["km"])
            for p in MANTENIMIENTOS_REF:
                km_pieza = int(self.inputs_km[p].value)
                if km_pieza > km_max_coche:
                    self.mostrar_alerta("Error", f"'{p}' tiene {km_pieza} km, superando los {km_max_coche} km del coche.")
                    return
            
            for p in MANTENIMIENTOS_REF:
                self.datos[self.coche_activo]["piezas"][p] = {
                    "km": int(self.inputs_km[p].value),
                    "nota": self.inputs_nota[p].value
                }
            self.guardar()
            self.dibujar_todo()
            self.mostrar_alerta("Éxito", "Historial actualizado.")
        except ValueError:
            self.mostrar_alerta("Error", "Introduce números enteros válidos.")

    def crear_nueva_ruta(self, e):
        def salvar_ruta(ev):
            nombre = input_nom.value.strip()
            kms_str = input_km.value.strip().replace(",", ".")
            if nombre and kms_str:
                try:
                    self.datos[self.coche_activo]["rutas"][nombre] = float(kms_str)
                    self.guardar()
                    self.page.dialog.open = False
                    self.dibujar_todo()
                except ValueError: pass

        input_nom = ft.TextField(label="Nombre de la ruta")
        input_km = ft.TextField(label="Distancia en km (Ej: 1.5)")
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Nueva Ruta"),
            content=ft.Column([input_nom, input_km], compact=True, height=120),
            actions=[ft.ElevatedButton("Guardar", on_click=salvar_ruta)]
        )
        self.page.dialog.open = True
        self.page.update()

    def guardar_cambios_rutas(self, e):
        try:
            for rn in self.inputs_rutas:
                valor_str = self.inputs_rutas[rn].value.replace(",", ".")
                self.datos[self.coche_activo]["rutas"][rn] = float(valor_str)
            self.guardar()
            self.dibujar_todo()
            self.mostrar_alerta("Éxito", "Rutas updated.")
        except ValueError:
            self.mostrar_alerta("Error", "Introduce números válidos.")

    def borrar_ruta_individual(self, nombre_ruta):
        del self.datos[self.coche_activo]["rutas"][nombre_ruta]
        self.guardar()
        self.dibujar_todo()

    def añadir_vehiculo(self, e):
        def salvar_coche(ev):
            n = input_coche.value.strip()
            if n:
                if n in self.datos: return
                self.datos[n] = {
                    "km": 0.0, 
                    "piezas": {p: {"km": 0, "nota": ""} for p in MANTENIMIENTOS_REF},
                    "rutas": RUTAS_DEFECTO.copy()
                }
                self.guardar()
                self.combo.options.append(ft.dropdown.Option(n))
                self.combo.value = n
                self.coche_activo = n
                self.page.dialog.open = False
                self.dibujar_todo()

        input_coche = ft.TextField(label="Nombre de coche/moto")
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Nuevo Vehículo"),
            content=input_coche,
            actions=[ft.ElevatedButton("Añadir", on_click=salvar_coche)]
        )
        self.page.dialog.open = True
        self.page.update()

    def editar_nombre_vehiculo(self, e):
        def renombrar(ev):
            nuevo = input_ren.value.strip()
            if nuevo and nuevo != self.coche_activo:
                self.datos[nuevo] = self.datos.pop(self.coche_activo)
                self.guardar()
                self.coche_activo = nuevo
                self.combo.options = [ft.dropdown.Option(c) for c in self.datos.keys()]
                self.combo.value = nuevo
                self.page.dialog.open = False
                self.dibujar_todo()

        input_ren = ft.TextField(label="Nuevo nombre", value=self.coche_activo)
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Renombrar"),
            content=input_ren,
            actions=[ft.ElevatedButton("Cambiar", on_click=renombrar)]
        )
        self.page.dialog.open = True
        self.page.update()

    def eliminar_vehiculo(self, e):
        if len(self.datos) <= 1:
            self.mostrar_alerta("Atención", "No puedes dejar el garaje vacío.")
            return
        
        def confirmar_borrado(ev):
            del self.datos[self.coche_activo]
            self.guardar()
            self.coche_activo = list(self.datos.keys())[0]
            self.combo.options = [ft.dropdown.Option(c) for c in self.datos.keys()]
            self.combo.value = self.coche_activo
            self.page.dialog.open = False
            self.dibujar_todo()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Borrar"),
            content=ft.Text(f"¿Eliminar permanentemente {self.coche_activo}?"),
            actions=[ft.ElevatedButton("Sí, Borrar", on_click=confirmar_borrado, bgcolor="#ef4444", color="white")]
        )
        self.page.dialog.open = True
        self.page.update()

    def mostrar_alerta(self, titulo, mensaje):
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: setattr(self.page.dialog, "open", False) or self.page.update())]
        )
        self.page.dialog.open = True
        self.page.update()

if __name__ == "__main__":
    ft.app(target=MiGarajeMovilApp)