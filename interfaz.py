import customtkinter as ctk

from multiprocessing import (
    Process,
    Queue,
    Semaphore,
    Lock,
    Event,
    Value,
)

from queue import Empty

from simulacion import proceso_vehiculo


class InterfazParqueadero(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Parqueadero Concurrente")
        self.geometry("1150x760")
        self.minsize(1050, 700)

        self.configure(
            fg_color="#0F172A"
        )

        self.capacidad = 4

        self.puestos = []
        self.procesos = []

        self.vehiculos_espera = {}
        self.vehiculo_puesto = {}

        self.cola_eventos = None

        self.semaforo = None
        self.lock = None
        self.evento_apertura = None

        self.dentro = None
        self.atendidos = None
        self.recaudo = None

        self.simulacion_activa = False

        self.crear_interfaz()

        self.after(
            100,
            self.revisar_eventos
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar_aplicacion
        )

    def crear_interfaz(self):

        titulo = ctk.CTkLabel(
            self,
            text="PARQUEADERO CONCURRENTE",
            font=("Segoe UI", 28, "bold"),
            text_color="white"
        )

        titulo.pack(
            pady=(18, 3)
        )

        subtitulo = ctk.CTkLabel(
            self,
            text=(
                "Simulación visual de procesos "
                "y mecanismos de sincronización"
            ),
            font=("Segoe UI", 14),
            text_color="#94A3B8"
        )

        subtitulo.pack(
            pady=(0, 12)
        )

        frame_config = ctk.CTkFrame(
            self,
            fg_color="#111827",
            corner_radius=14
        )

        frame_config.pack(
            fill="x",
            padx=30,
            pady=(5, 10)
        )

        ctk.CTkLabel(
            frame_config,
            text="Cantidad de vehículos",
            font=("Segoe UI", 12, "bold"),
            text_color="#CBD5E1"
        ).grid(
            row=0,
            column=0,
            padx=20,
            pady=(12, 5)
        )

        self.entry_vehiculos = ctk.CTkEntry(
            frame_config,
            width=140,
            justify="center"
        )

        self.entry_vehiculos.insert(
            0,
            "8"
        )

        self.entry_vehiculos.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 12)
        )

        self.boton_preparar = ctk.CTkButton(
            frame_config,
            text="PREPARAR",
            width=140,
            command=self.preparar_simulacion
        )

        self.boton_preparar.grid(
            row=1,
            column=1,
            padx=10
        )

        self.boton_abrir = ctk.CTkButton(
            frame_config,
            text="ABRIR PARQUEADERO",
            width=170,
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.abrir_parqueadero,
            state="disabled"
        )

        self.boton_abrir.grid(
            row=1,
            column=2,
            padx=10
        )

        self.boton_reiniciar = ctk.CTkButton(
            frame_config,
            text="REINICIAR",
            width=130,
            fg_color="#475569",
            hover_color="#334155",
            command=self.reiniciar
        )

        self.boton_reiniciar.grid(
            row=1,
            column=3,
            padx=10
        )

        frame_tarjetas = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        frame_tarjetas.pack(
            pady=5
        )

        self.label_capacidad = self.crear_tarjeta(
            frame_tarjetas,
            "CAPACIDAD",
            str(self.capacidad),
            0
        )

        self.label_disponibles = self.crear_tarjeta(
            frame_tarjetas,
            "DISPONIBLES",
            str(self.capacidad),
            1
        )

        self.label_dentro = self.crear_tarjeta(
            frame_tarjetas,
            "DENTRO",
            "0",
            2
        )

        self.label_esperando = self.crear_tarjeta(
            frame_tarjetas,
            "ESPERANDO",
            "0",
            3
        )

        self.label_atendidos = self.crear_tarjeta(
            frame_tarjetas,
            "ATENDIDOS",
            "0",
            4
        )

        self.label_recaudo = self.crear_tarjeta(
            frame_tarjetas,
            "RECAUDO",
            "$0",
            5
        )

        frame_principal = ctk.CTkFrame(
            self,
            fg_color="#111827",
            corner_radius=18
        )

        frame_principal.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(10, 20)
        )

        frame_principal.grid_columnconfigure(
            0,
            weight=3
        )

        frame_principal.grid_columnconfigure(
            1,
            weight=1
        )

        frame_principal.grid_rowconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            frame_principal,
            text="ZONA DE PARQUEO",
            font=("Segoe UI", 18, "bold"),
            text_color="#60A5FA"
        ).grid(
            row=0,
            column=0,
            pady=12
        )

        ctk.CTkLabel(
            frame_principal,
            text="ZONA DE ESPERA",
            font=("Segoe UI", 18, "bold"),
            text_color="#FBBF24"
        ).grid(
            row=0,
            column=1,
            pady=12
        )

        self.frame_parqueadero = ctk.CTkFrame(
            frame_principal,
            fg_color="#1E293B",
            corner_radius=15
        )

        self.frame_parqueadero.grid(
            row=1,
            column=0,
            padx=(20, 10),
            pady=(0, 20),
            sticky="nsew"
        )

        for columna in range(2):

            self.frame_parqueadero.grid_columnconfigure(
                columna,
                weight=1
            )

        for fila in range(2):

            self.frame_parqueadero.grid_rowconfigure(
                fila,
                weight=1
            )

        for puesto in range(
            self.capacidad
        ):

            fila = puesto // 2
            columna = puesto % 2

            espacio = ctk.CTkFrame(
                self.frame_parqueadero,
                fg_color="#14532D",
                corner_radius=15,
                border_width=2,
                border_color="#22C55E"
            )

            espacio.grid(
                row=fila,
                column=columna,
                padx=15,
                pady=15,
                sticky="nsew"
            )

            ctk.CTkLabel(
                espacio,
                text=f"PUESTO {puesto + 1}",
                font=("Segoe UI", 15, "bold"),
                text_color="white"
            ).pack(
                pady=(20, 5)
            )

            estado = ctk.CTkLabel(
                espacio,
                text="LIBRE",
                font=("Segoe UI", 22, "bold"),
                text_color="#4ADE80"
            )

            estado.pack(
                pady=12
            )

            pid_label = ctk.CTkLabel(
                espacio,
                text="",
                font=("Segoe UI", 11),
                text_color="#BFDBFE"
            )

            pid_label.pack()

            self.puestos.append({
                "frame": espacio,
                "estado": estado,
                "pid": pid_label,
                "ocupado": False,
            })

        self.frame_espera = (
            ctk.CTkScrollableFrame(
                frame_principal,
                fg_color="#1E293B",
                corner_radius=15
            )
        )

        self.frame_espera.grid(
            row=1,
            column=1,
            padx=(10, 20),
            pady=(0, 20),
            sticky="nsew"
        )

        self.label_estado = ctk.CTkLabel(
            self,
            text=(
                "● Listo para preparar "
                "la simulación"
            ),
            font=("Segoe UI", 12, "bold"),
            text_color="#60A5FA"
        )

        self.label_estado.pack(
            pady=(0, 12)
        )

    def crear_tarjeta(
        self,
        padre,
        titulo,
        valor,
        columna
    ):

        tarjeta = ctk.CTkFrame(
            padre,
            width=155,
            height=82,
            fg_color="#1E293B",
            corner_radius=13
        )

        tarjeta.grid(
            row=0,
            column=columna,
            padx=5
        )

        tarjeta.grid_propagate(
            False
        )

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            font=("Segoe UI", 10, "bold"),
            text_color="#94A3B8"
        ).pack(
            pady=(10, 0)
        )

        label_valor = ctk.CTkLabel(
            tarjeta,
            text=valor,
            font=("Segoe UI", 22, "bold"),
            text_color="white"
        )

        label_valor.pack()

        return label_valor

    def preparar_simulacion(self):

        if self.simulacion_activa:
            return

        try:

            cantidad = int(
                self.entry_vehiculos.get()
            )

            if cantidad <= 0:
                raise ValueError

        except ValueError:

            self.label_estado.configure(
                text=(
                    "● Ingrese una cantidad "
                    "válida"
                ),
                text_color="#F87171"
            )

            return

        self.limpiar_visual()

        self.cola_eventos = Queue()

        self.semaforo = Semaphore(
            self.capacidad
        )

        self.lock = Lock()

        self.evento_apertura = Event()

        self.dentro = Value(
            "i",
            0,
            lock=False
        )

        self.atendidos = Value(
            "i",
            0,
            lock=False
        )

        self.recaudo = Value(
            "i",
            0,
            lock=False
        )

        self.procesos = []

        self.simulacion_activa = True

        for vehiculo in range(
            1,
            cantidad + 1
        ):

            proceso = Process(
                target=proceso_vehiculo,
                args=(
                    vehiculo,
                    self.semaforo,
                    self.lock,
                    self.evento_apertura,
                    self.dentro,
                    self.atendidos,
                    self.recaudo,
                    self.cola_eventos,
                ),
                name=f"Vehiculo-{vehiculo}"
            )

            self.procesos.append(
                proceso
            )

            proceso.start()

        self.boton_preparar.configure(
            state="disabled"
        )

        self.boton_abrir.configure(
            state="normal"
        )

        self.label_estado.configure(
            text=(
                "● Procesos creados. "
                "El parqueadero continúa cerrado."
            ),
            text_color="#FBBF24"
        )

    def abrir_parqueadero(self):

        if self.evento_apertura is None:
            return

        self.evento_apertura.set()

        self.boton_abrir.configure(
            state="disabled"
        )

        self.label_estado.configure(
            text=(
                "● Parqueadero abierto. "
                "Los procesos pueden continuar."
            ),
            text_color="#4ADE80"
        )

    def revisar_eventos(self):

        if self.cola_eventos is not None:

            while True:

                try:

                    evento = (
                        self.cola_eventos.get_nowait()
                    )

                except Empty:
                    break

                self.procesar_evento(
                    evento
                )

        self.actualizar_contadores()

        self.after(
            100,
            self.revisar_eventos
        )

    def procesar_evento(
        self,
        evento
    ):

        tipo = evento["tipo"]
        vehiculo = evento["vehiculo"]
        pid = evento["pid"]

        if tipo == "creado":

            self.agregar_espera(
                vehiculo,
                pid,
                "Esperando apertura"
            )

        elif tipo == "esperando":

            self.actualizar_estado_espera(
                vehiculo,
                "Esperando cupo"
            )

        elif tipo == "entra":

            self.quitar_espera(
                vehiculo
            )

            self.ocupar_puesto(
                vehiculo,
                pid
            )

        elif tipo == "sale":

            self.liberar_puesto(
                vehiculo
            )

            self.label_estado.configure(
                text=(
                    f"● Auto {vehiculo} salió. "
                    f"Pago: ${evento['pago']:,}"
                ),
                text_color="#60A5FA"
            )

    def agregar_espera(
        self,
        vehiculo,
        pid,
        estado
    ):

        frame = ctk.CTkFrame(
            self.frame_espera,
            fg_color="#334155",
            corner_radius=10
        )

        frame.pack(
            fill="x",
            pady=5,
            padx=4
        )

        ctk.CTkLabel(
            frame,
            text=f"AUTO {vehiculo}",
            font=("Segoe UI", 14, "bold"),
            text_color="#FBBF24"
        ).pack(
            pady=(7, 0)
        )

        label_estado = ctk.CTkLabel(
            frame,
            text=estado,
            font=("Segoe UI", 11),
            text_color="#CBD5E1"
        )

        label_estado.pack()

        ctk.CTkLabel(
            frame,
            text=f"PID {pid}",
            font=("Segoe UI", 10),
            text_color="#94A3B8"
        ).pack(
            pady=(0, 7)
        )

        self.vehiculos_espera[
            vehiculo
        ] = {
            "frame": frame,
            "estado": label_estado,
        }

    def actualizar_estado_espera(
        self,
        vehiculo,
        estado
    ):

        if vehiculo in self.vehiculos_espera:

            self.vehiculos_espera[
                vehiculo
            ]["estado"].configure(
                text=estado
            )

    def quitar_espera(
        self,
        vehiculo
    ):

        if vehiculo in self.vehiculos_espera:

            self.vehiculos_espera[
                vehiculo
            ]["frame"].destroy()

            del self.vehiculos_espera[
                vehiculo
            ]

    def ocupar_puesto(
        self,
        vehiculo,
        pid
    ):

        for indice, puesto in enumerate(
            self.puestos
        ):

            if not puesto["ocupado"]:

                puesto["ocupado"] = True

                puesto["frame"].configure(
                    fg_color="#1E3A8A",
                    border_color="#60A5FA"
                )

                puesto["estado"].configure(
                    text=f"AUTO {vehiculo}",
                    text_color="white"
                )

                puesto["pid"].configure(
                    text=f"PID {pid}"
                )

                self.vehiculo_puesto[
                    vehiculo
                ] = indice

                break

    def liberar_puesto(
        self,
        vehiculo
    ):

        if vehiculo not in self.vehiculo_puesto:
            return

        indice = self.vehiculo_puesto[
            vehiculo
        ]

        puesto = self.puestos[
            indice
        ]

        puesto["ocupado"] = False

        puesto["frame"].configure(
            fg_color="#14532D",
            border_color="#22C55E"
        )

        puesto["estado"].configure(
            text="LIBRE",
            text_color="#4ADE80"
        )

        puesto["pid"].configure(
            text=""
        )

        del self.vehiculo_puesto[
            vehiculo
        ]

    def actualizar_contadores(self):

        if self.dentro is None:
            return

        if self.lock is not None:

            with self.lock:

                dentro = self.dentro.value
                atendidos = self.atendidos.value
                recaudo = self.recaudo.value

        else:

            dentro = 0
            atendidos = 0
            recaudo = 0

        disponibles = (
            self.capacidad - dentro
        )

        esperando = len(
            self.vehiculos_espera
        )

        self.label_disponibles.configure(
            text=str(disponibles)
        )

        self.label_dentro.configure(
            text=str(dentro)
        )

        self.label_esperando.configure(
            text=str(esperando)
        )

        self.label_atendidos.configure(
            text=str(atendidos)
        )

        self.label_recaudo.configure(
            text=f"${recaudo:,}"
        )

        if (
            self.simulacion_activa
            and self.procesos
            and all(
                not proceso.is_alive()
                for proceso in self.procesos
            )
        ):

            self.simulacion_activa = False

            self.label_estado.configure(
                text=(
                    "● Simulación finalizada "
                    "correctamente"
                ),
                text_color="#4ADE80"
            )

    def limpiar_visual(self):

        for vehiculo in list(
            self.vehiculos_espera.keys()
        ):

            self.quitar_espera(
                vehiculo
            )

        self.vehiculo_puesto.clear()

        for puesto in self.puestos:

            puesto["ocupado"] = False

            puesto["frame"].configure(
                fg_color="#14532D",
                border_color="#22C55E"
            )

            puesto["estado"].configure(
                text="LIBRE",
                text_color="#4ADE80"
            )

            puesto["pid"].configure(
                text=""
            )

        self.label_disponibles.configure(
            text=str(self.capacidad)
        )

        self.label_dentro.configure(
            text="0"
        )

        self.label_esperando.configure(
            text="0"
        )

        self.label_atendidos.configure(
            text="0"
        )

        self.label_recaudo.configure(
            text="$0"
        )

    def detener_procesos(self):

        for proceso in self.procesos:

            if proceso.is_alive():

                proceso.terminate()

            proceso.join(
                timeout=0.3
            )

        self.procesos = []

    def reiniciar(self):

        self.detener_procesos()

        self.simulacion_activa = False

        self.cola_eventos = None

        self.semaforo = None
        self.lock = None
        self.evento_apertura = None

        self.dentro = None
        self.atendidos = None
        self.recaudo = None

        self.limpiar_visual()

        self.boton_preparar.configure(
            state="normal"
        )

        self.boton_abrir.configure(
            state="disabled"
        )

        self.label_estado.configure(
            text=(
                "● Listo para preparar "
                "la simulación"
            ),
            text_color="#60A5FA"
        )

    def cerrar_aplicacion(self):

        self.detener_procesos()

        self.destroy()