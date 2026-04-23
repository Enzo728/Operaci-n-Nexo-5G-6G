import math
import tkinter as tk
from tkinter import ttk, messagebox
import calculos_nexo_5g as calc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class SimuladorNexoApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Simulador Operación Nexo 5G/6G - Equipo Consultor RF')
        self.root.geometry('900x700')
        self.root.configure(bg='#e5ecf7')
        self.root.resizable(True, True)  # Permitir redimensionamiento

        # Variable para controlar pantalla completa
        self.fullscreen = False

        # Atajo de teclado para pantalla completa (F11)
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)

        self.setup_style()

        header = ttk.Frame(self.root, padding=(20, 16), style='Header.TFrame')
        header.pack(fill='x')

        # Frame para título (izquierda)
        title_frame = ttk.Frame(header)
        title_frame.pack(side='left', fill='x', expand=True)

        ttk.Label(title_frame, text='Simulador Nexo 5G/6G', style='Title.TLabel').pack(anchor='w')
        ttk.Label(title_frame, text='Interfaz técnica para análisis de tráfico, enlace y propagación.', style='Subtitle.TLabel').pack(anchor='w', pady=(4, 0))

        # Frame para botones (derecha)
        button_frame = ttk.Frame(header)
        button_frame.pack(side='right')

        # Botón de pantalla completa
        self.fullscreen_btn = ttk.Button(button_frame, text='⛶ Pantalla Completa', command=self.toggle_fullscreen, style='Accent.TButton')
        self.fullscreen_btn.pack(pady=(0, 4))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=18, pady=(0, 18))

        self.tab_trafico = ttk.Frame(notebook)
        self.tab_link = ttk.Frame(notebook)
        self.tab_prop = ttk.Frame(notebook)
        self.tab_escenarios = ttk.Frame(notebook)
        self.tab_reto = ttk.Frame(notebook)

        notebook.add(self.tab_trafico, text='Tráfico (Erlang)')
        notebook.add(self.tab_link, text='Balance de Enlace')
        notebook.add(self.tab_prop, text='Propagación')
        notebook.add(self.tab_escenarios, text='Escenarios')
        notebook.add(self.tab_reto, text='Reto Nueva Pangea')

        self.setup_trafico()
        self.setup_link()
        self.setup_prop()
        self.setup_escenarios()
        self.setup_reto()

    def setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TNotebook.Tab', padding=(16, 10), font=('Segoe UI', 10, 'bold'))
        style.configure('TLabelFrame', background='#f8fbff', borderwidth=1, relief='solid')
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#1f3a72', background='#e5ecf7')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground='#4f5f7a', background='#e5ecf7')
        style.configure('Section.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#1b2e56', background='#f8fbff')
        style.configure('Result.TLabel', font=('Segoe UI', 10, 'bold'), foreground='#0b2f55', background='#f8fbff')
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))

    def toggle_fullscreen(self, event=None):
        """Alterna entre pantalla completa y modo ventana"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)

        # Actualizar texto del botón
        if self.fullscreen:
            self.fullscreen_btn.config(text='⛶ Salir Pantalla Completa')
        else:
            self.fullscreen_btn.config(text='⛶ Pantalla Completa')

        return 'break'

    def exit_fullscreen(self, event=None):
        """Sale de pantalla completa"""
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes('-fullscreen', False)
        return 'break'

    def create_input_card(self, parent, title, description):
        frame = ttk.LabelFrame(parent, text=title, padding=16)
        frame.pack(padx=18, pady=18, fill='x')
        ttk.Label(frame, text=description, style='Subtitle.TLabel', wraplength=760).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))
        return frame

    def create_chart_frame(self, parent, title):
        frame = ttk.LabelFrame(parent, text=title, padding=12)
        frame.pack(padx=18, pady=(0, 18), fill='both', expand=True)
        return frame

    def _clear_canvas(self, attr_name):
        canvas = getattr(self, attr_name, None)
        if canvas:
            canvas.get_tk_widget().destroy()
            setattr(self, attr_name, None)

    def _draw_chart(self, parent, fig, attr_name):
        self._clear_canvas(attr_name)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=6)
        setattr(self, attr_name, canvas)

    def setup_trafico(self):
        frame = self.create_input_card(self.tab_trafico, 'Calculadora Erlang B', 'Calcula la probabilidad de bloqueo sobre el número de recursos disponibles y el tráfico ofrecido.')

        ttk.Label(frame, text='Tráfico ofrecido A (Erlangs):').grid(row=1, column=0, sticky='w', pady=6)
        self.ent_a = ttk.Entry(frame, width=20)
        self.ent_a.grid(row=1, column=1, pady=6, padx=(10, 0), sticky='w')
        self.ent_a.insert(0, '344')

        ttk.Label(frame, text='Canales / PRBs (m):').grid(row=2, column=0, sticky='w', pady=6)
        self.ent_m = ttk.Entry(frame, width=20)
        self.ent_m.grid(row=2, column=1, pady=6, padx=(10, 0), sticky='w')
        self.ent_m.insert(0, '500')

        ttk.Separator(frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=12)

        btn = ttk.Button(frame, text='Calcular Bloqueo', command=self.calc_erlang, style='Accent.TButton')
        btn.grid(row=4, column=0, columnspan=2, pady=(0, 12), sticky='w')

        self.lbl_res_erlang = ttk.Label(frame, text='Probabilidad de Bloqueo: -', style='Result.TLabel')
        self.lbl_res_erlang.grid(row=5, column=0, columnspan=2, sticky='w')

        self.graph_trafico_frame = self.create_chart_frame(self.tab_trafico, 'Erlang B: Bloqueo vs Canales')
        fig = plt.Figure(figsize=(8, 2.4), dpi=90)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Presiona Calcular Bloqueo para visualizar la curva de Erlang B.', ha='center', va='center', fontsize=10, color='#33415c')
        ax.axis('off')
        self._draw_chart(self.graph_trafico_frame, fig, 'erlang_canvas')

    def calc_erlang(self):
        try:
            # Validar campos numéricos
            try:
                a = float(self.ent_a.get())
                m = int(float(self.ent_m.get()))  # Convertir a float primero para manejar decimales
            except ValueError:
                messagebox.showerror('Error', 'Por favor, introduce valores numéricos válidos.')
                return

            # Validar rangos
            if a < 0:
                messagebox.showerror('Error', 'El tráfico ofrecido debe ser mayor o igual a cero.')
                return
            if m <= 0:
                messagebox.showerror('Error', 'El número de canales debe ser mayor que cero.')
                return

            pb = calc.erlang_b(a, m)
            self.lbl_res_erlang.config(text=f'Probabilidad de Bloqueo: {pb*100:.4f}%')
            self.draw_erlang_graph(a, m)
        except Exception as e:
            messagebox.showerror('Error', f'Error en el cálculo Erlang B: {str(e)}')

    def draw_erlang_graph(self, a, m):
        max_x = max(100, m)
        step = max(1, max_x // 60)
        x_values = list(range(10, max_x + 1, step))
        y_values = [calc.erlang_b(a, xi) * 100 for xi in x_values]

        fig = plt.Figure(figsize=(8, 2.4), dpi=90)
        ax = fig.add_subplot(111)
        ax.plot(x_values, y_values, color='#1f4f91', linewidth=2)
        ax.axvline(m, color='#d1495b', linestyle='--', linewidth=1)
        ax.scatter([m], [calc.erlang_b(a, m) * 100], color='#d1495b')
        ax.set_title('Curva de Bloqueo Erlang B', fontsize=11)
        ax.set_xlabel('Canales / PRBs (m)')
        ax.set_ylabel('Probabilidad de Bloqueo (%)')
        ax.grid(alpha=0.3)
        if max(y_values) > 0:
            ax.set_ylim(0, max(y_values) * 1.05)
        ax.set_xlim(min(x_values), max_x)
        self._draw_chart(self.graph_trafico_frame, fig, 'erlang_canvas')

    def setup_link(self):
        frame_dl = self.create_input_card(self.tab_link, 'Enlace Descendente (MAPL)', 'Calcula la atenuación máxima compensable para el enlace descendente usando parámetros de BTS y MS.')

        labels_dl = ['PIRE BTS (dBm)', 'Sensibilidad MS (dBm)', 'Ganancia MS (dBi)', 'Ganancia Altura (dB)', 'Márgenes (dB)']
        defaults_dl = ['43', '-101', '0', '10', '8']
        self.ent_dl = {}

        for i, (lbl, default) in enumerate(zip(labels_dl, defaults_dl), start=1):
            ttk.Label(frame_dl, text=lbl).grid(row=i, column=0, sticky='w', pady=6)
            ent = ttk.Entry(frame_dl, width=20)
            ent.insert(0, default)
            ent.grid(row=i, column=1, pady=6, padx=(10, 0), sticky='w')
            self.ent_dl[lbl] = ent

        ttk.Separator(frame_dl, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky='ew', pady=12)
        btn = ttk.Button(frame_dl, text='Calcular MAPL DL', command=self.calc_mapl_dl, style='Accent.TButton')
        btn.grid(row=7, column=0, columnspan=2, sticky='w')

        self.lbl_res_dl = ttk.Label(frame_dl, text='MAPL DL: -', style='Result.TLabel')
        self.lbl_res_dl.grid(row=8, column=0, columnspan=2, sticky='w', pady=(12, 0))

    def calc_mapl_dl(self):
        try:
            # Validar que todos los campos sean numéricos
            vals = []
            for e in self.ent_dl.values():
                try:
                    val = float(e.get())
                    vals.append(val)
                except ValueError:
                    messagebox.showerror('Error', 'Todos los campos deben contener valores numéricos válidos.')
                    return

            res = calc.calcular_mapl_dl(*vals)
            self.lbl_res_dl.config(text=f'MAPL DL: {res:.2f} dB')
        except Exception as e:
            messagebox.showerror('Error', f'Error en el cálculo MAPL DL: {str(e)}')

    def setup_prop(self):
        frame_oku = self.create_input_card(self.tab_prop, 'Modelo Okumura-Hata', 'Calcula las pérdidas de propagación L50 utilizando parámetros de frecuencia, altura y distancia.')

        labels_oku = ['Frecuencia (MHz)', 'Altura Tx (m)', 'Distancia (km)', 'Factor Corr. Móvil (dB)']
        defaults_oku = ['2100', '50', '0.3', '7.8']
        self.ent_oku = {}

        for i, (lbl, default) in enumerate(zip(labels_oku, defaults_oku), start=1):
            ttk.Label(frame_oku, text=lbl).grid(row=i, column=0, sticky='w', pady=6)
            ent = ttk.Entry(frame_oku, width=20)
            ent.insert(0, default)
            ent.grid(row=i, column=1, pady=6, padx=(10, 0), sticky='w')
            self.ent_oku[lbl] = ent

        ttk.Separator(frame_oku, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky='ew', pady=12)
        btn = ttk.Button(frame_oku, text='Calcular Pérdidas', command=self.calc_oku, style='Accent.TButton')
        btn.grid(row=6, column=0, columnspan=2, sticky='w')

        self.lbl_res_oku = ttk.Label(frame_oku, text='Pérdidas L50: -', style='Result.TLabel')
        self.lbl_res_oku.grid(row=7, column=0, columnspan=2, sticky='w', pady=(12, 0))

        self.graph_prop_frame = self.create_chart_frame(self.tab_prop, 'Pérdidas por distancia')
        fig = plt.Figure(figsize=(8, 2.4), dpi=90)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Presiona Calcular Pérdidas para ver el comportamiento con la distancia.', ha='center', va='center', fontsize=10, color='#33415c')
        ax.axis('off')
        self._draw_chart(self.graph_prop_frame, fig, 'prop_canvas')

    def calc_oku(self):
        try:
            # Validar que todos los campos sean numéricos
            vals = []
            for e in self.ent_oku.values():
                try:
                    val = float(e.get())
                    vals.append(val)
                except ValueError:
                    messagebox.showerror('Error', 'Todos los campos deben contener valores numéricos válidos.')
                    return

            fc_mhz, h_te, d_km, a_hre = vals

            # Validar rangos físicos
            if fc_mhz <= 0:
                messagebox.showerror('Error', 'La frecuencia debe ser mayor que cero.')
                return
            if h_te <= 0:
                messagebox.showerror('Error', 'La altura del transmisor debe ser mayor que cero.')
                return
            if d_km <= 0:
                messagebox.showerror('Error', 'La distancia debe ser mayor que cero.')
                return

            res = calc.okumura_hata(fc_mhz, h_te, d_km, a_hre)
            self.lbl_res_oku.config(text=f'Pérdidas L50: {res:.2f} dB')
            self.draw_prop_graph(fc_mhz, h_te, a_hre)

        except Exception as e:
            messagebox.showerror('Error', f'Error inesperado en el cálculo: {str(e)}')

    def draw_prop_graph(self, fc_mhz, h_te, a_hre):
        distances = [i * 0.05 for i in range(2, 41)]
        losses = [calc.okumura_hata(fc_mhz, h_te, d, a_hre) for d in distances]

        fig = plt.Figure(figsize=(8, 2.4), dpi=90)
        ax = fig.add_subplot(111)
        ax.plot(distances, losses, color='#1f4f91', linewidth=2)
        ax.set_title('Pérdidas Okumura-Hata vs Distancia', fontsize=11)
        ax.set_xlabel('Distancia (km)')
        ax.set_ylabel('Pérdidas L50 (dB)')
        ax.grid(alpha=0.3)
        self._draw_chart(self.graph_prop_frame, fig, 'prop_canvas')

    def setup_escenarios(self):
        frame = ttk.Frame(self.tab_escenarios, padding=16)
        frame.pack(fill='both', expand=True)

        header = ttk.Frame(frame)
        header.pack(fill='x', pady=(0, 10))
        ttk.Label(header, text='Visualización de Escenarios', style='Section.TLabel').pack(side='left', anchor='w')
        ttk.Button(header, text='Generar Informe', command=self.run_practice, style='Accent.TButton').pack(side='right')

        info = ttk.Label(frame, text='Presentación visual de los resultados de cobertura y capacidad para cada escenario.', style='Subtitle.TLabel')
        info.pack(fill='x')

        self.scenario1_frame = ttk.LabelFrame(frame, text='Escenario 1 - Distrito Financiero', padding=14)
        self.scenario1_frame.pack(fill='x', pady=(12, 10))

        self.scenario1_summary = {}
        labels1 = ['MAPL DL', 'MAPL UL', 'Path Loss 300m', 'Margen UL', 'Tráfico celda macro']
        for i, label in enumerate(labels1):
            ttk.Label(self.scenario1_frame, text=label + ':').grid(row=i, column=0, sticky='w', pady=4)
            value = ttk.Label(self.scenario1_frame, text='-', style='Result.TLabel')
            value.grid(row=i, column=1, sticky='w', pady=4, padx=(8, 0))
            self.scenario1_summary[label] = value

        self.scenario2_frame = ttk.LabelFrame(frame, text='Escenario 2 - Festival Global', padding=14)
        self.scenario2_frame.pack(fill='both', expand=True)

        summary_frame = ttk.Frame(self.scenario2_frame)
        summary_frame.pack(fill='x', pady=(0, 12))
        ttk.Label(summary_frame, text='Tráfico total evento:', style='Section.TLabel').grid(row=0, column=0, sticky='w')
        self.scenario2_total = ttk.Label(summary_frame, text='-', style='Result.TLabel')
        self.scenario2_total.grid(row=0, column=1, sticky='w', padx=(8, 0))

        self.scenario2_table = ttk.Treeview(self.scenario2_frame, columns=('tipo', 'prbs', 'bloqueo'), show='headings', height=8)
        self.scenario2_table.heading('tipo', text='Tipo de Celda')
        self.scenario2_table.heading('prbs', text='PRBs evaluados')
        self.scenario2_table.heading('bloqueo', text='Bloqueo (%)')
        self.scenario2_table.column('tipo', width=180)
        self.scenario2_table.column('prbs', width=120, anchor='center')
        self.scenario2_table.column('bloqueo', width=120, anchor='center')
        self.scenario2_table.pack(fill='x')

        self.scenario2_chart_frame = self.create_chart_frame(self.scenario2_frame, 'Comparativa de Bloqueo por PRBs')
        fig = plt.Figure(figsize=(8, 2.4), dpi=90)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Genera el informe para visualizar la comparativa de bloqueo.', ha='center', va='center', fontsize=10, color='#33415c')
        ax.axis('off')
        self._draw_chart(self.scenario2_chart_frame, fig, 'scenario_canvas')

    def setup_reto(self):
        frame = ttk.Frame(self.tab_reto, padding=16)
        frame.pack(fill='both', expand=True)

        header = ttk.Frame(frame)
        header.pack(fill='x', pady=(0, 10))
        ttk.Label(header, text='Resultados del Reto Nueva Pangea', style='Section.TLabel').pack(side='left', anchor='w')
        ttk.Button(header, text='Calcular Resultados', command=self.calculate_reto_results, style='Accent.TButton').pack(side='right')

        info = ttk.Label(frame, text='Cálculos de ruido, sensibilidad, cobertura y capacidad para los dos escenarios del reto.', style='Subtitle.TLabel')
        info.pack(fill='x')

        cards_frame = ttk.Frame(frame)
        cards_frame.pack(fill='x', pady=(12, 10))

        self.reto_cards = {}
        for i, title in enumerate(['RX Noise', 'Cobertura A', 'Cobertura B', 'Diseño A', 'Diseño B']):
            card = ttk.LabelFrame(cards_frame, text=title, padding=10)
            card.grid(row=0, column=i, padx=6, sticky='nsew')
            cards_frame.columnconfigure(i, weight=1)
            value = ttk.Label(card, text='-', style='Result.TLabel')
            value.pack(anchor='center')
            self.reto_cards[title] = value

        split_frame = ttk.Frame(frame)
        split_frame.pack(fill='both', expand=True)

        self.reto_table_a = ttk.Treeview(split_frame, columns=('reuse', 'channels', 'r_capacity'), show='headings', height=4)
        self.reto_table_a.heading('reuse', text='N reutilización')
        self.reto_table_a.heading('channels', text='Canales/sector')
        self.reto_table_a.heading('r_capacity', text='Radio capacidad (km)')
        self.reto_table_a.column('reuse', width=110, anchor='center')
        self.reto_table_a.column('channels', width=120, anchor='center')
        self.reto_table_a.column('r_capacity', width=140, anchor='center')
        self.reto_table_a.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=4)

        self.reto_table_b = ttk.Treeview(split_frame, columns=('channels', 'r_capacity'), show='headings', height=4)
        self.reto_table_b.heading('channels', text='Canales celda')
        self.reto_table_b.heading('r_capacity', text='Radio capacidad (km)')
        self.reto_table_b.column('channels', width=120, anchor='center')
        self.reto_table_b.column('r_capacity', width=140, anchor='center')
        self.reto_table_b.grid(row=0, column=1, sticky='nsew', padx=(8, 0), pady=4)

        split_frame.columnconfigure(0, weight=1)
        split_frame.columnconfigure(1, weight=1)

        self.reto_chart_frame = self.create_chart_frame(frame, 'Comparativa de radios: cobertura vs capacidad')

    def noise_floor(self, bandwidth_hz=20e6, nf_db=7):
        return -174 + 10 * math.log10(bandwidth_hz) + nf_db

    def sensitivity(self, snr_db, nf_db=7, bandwidth_hz=20e6, L_impl=2):
        return self.noise_floor(bandwidth_hz, nf_db) + snr_db + L_impl

    def coverage_radius_lp(self, L_max_db, offset_db, coef):
        exponent = (L_max_db - offset_db) / coef
        return 10 ** exponent

    def max_traffic_for_blocking(self, m, target_pb=0.02):
        low, high = 0.0, 20000.0
        for _ in range(50):
            mid = (low + high) / 2
            if calc.erlang_b(mid, m) > target_pb:
                high = mid
            else:
                low = mid
        return low

    def capacity_radius(self, traffic_density, m, target_pb=0.02):
        if traffic_density <= 0 or m <= 0:
            return 0.0
        A_max = self.max_traffic_for_blocking(m, target_pb)
        area_km2 = A_max / traffic_density
        if area_km2 <= 0:
            return 0.0
        return math.sqrt(area_km2 / 2.598076211)

    def calculate_reto_results(self):
        P_tx = 43
        G_t = 18
        G_r = 0
        L_impl = 2
        L_extra = 12
        NF = 7
        BW = 20e6

        # Escenario A: Distrito Financiero
        snr_a = 15
        users_a = 2500
        call_rate_a = 3
        call_duration_a = 2
        reuse_options = [3, 4, 7]
        sectors_a = 3

        # Escenario B: Festival Global
        snr_b = 5
        users_b = 8000
        call_rate_b = 5
        call_duration_b = 1
        split_options = [100, 50]

        noise = self.noise_floor(BW, NF)
        sens_a = self.sensitivity(snr_a, NF, BW, L_impl)
        sens_b = self.sensitivity(snr_b, NF, BW, L_impl)

        L_max_a = P_tx + G_t + G_r - L_extra - sens_a
        L_max_b = P_tx + G_t + G_r - L_extra - sens_b

        r_coverage_a = self.coverage_radius_lp(L_max_a, 135, 35)
        r_coverage_b = self.coverage_radius_lp(L_max_b, 120, 30)

        A_user_a = call_rate_a * (call_duration_a / 60)
        A_user_b = call_rate_b * (call_duration_b / 60)
        density_a = users_a * A_user_a
        density_b = users_b * A_user_b

        capacity_data_a = []
        for reuse in reuse_options:
            channels_sector = max(1, int(100 // (sectors_a * reuse)))
            r_capacity = self.capacity_radius(density_a, channels_sector)
            capacity_data_a.append((reuse, channels_sector, r_capacity))

        capacity_data_b = []
        for channels in split_options:
            r_capacity = self.capacity_radius(density_b, channels)
            capacity_data_b.append((channels, r_capacity))

        chosen_a = min(r_coverage_a, max(item[2] for item in capacity_data_a))
        chosen_b = min(r_coverage_b, max(item[1] for item in capacity_data_b))

        self.reto_cards['RX Noise'].config(text=f'{noise:.1f} dBm')
        self.reto_cards['Cobertura A'].config(text=f'{r_coverage_a:.2f} km')
        self.reto_cards['Cobertura B'].config(text=f'{r_coverage_b:.2f} km')
        self.reto_cards['Diseño A'].config(text=f'{chosen_a:.2f} km')
        self.reto_cards['Diseño B'].config(text=f'{chosen_b:.2f} km')

        self.reto_table_a.delete(*self.reto_table_a.get_children())
        for reuse, channels, r_capacity in capacity_data_a:
            self.reto_table_a.insert('', 'end', values=(f'N={reuse}', channels, f'{r_capacity:.2f}'))

        self.reto_table_b.delete(*self.reto_table_b.get_children())
        for channels, r_capacity in capacity_data_b:
            self.reto_table_b.insert('', 'end', values=(channels, f'{r_capacity:.2f}'))

        labels = ['Cobertura A', 'Capacidad A', 'Cobertura B', 'Capacidad B']
        values = [r_coverage_a, chosen_a, r_coverage_b, chosen_b]
        fig = plt.Figure(figsize=(8, 2.4), dpi=90)
        ax = fig.add_subplot(111)
        ax.bar(labels, values, color=['#1f4f91', '#4f7a9d', '#1f4f91', '#d1495b'])
        ax.set_title('Radios de Cobertura vs Capacidad', fontsize=11)
        ax.set_ylabel('Radio (km)')
        ax.grid(axis='y', alpha=0.3)
        for i, v in enumerate(values):
            ax.text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom', fontsize=9)
        self._draw_chart(self.reto_chart_frame, fig, 'reto_canvas')

    def run_practice(self):
        mapl_dl = calc.calcular_mapl_dl(43, -101, 0, 10, 8)
        mapl_ul = calc.calcular_mapl_ul(23, -104, 17, 3, 2, 7)
        perdidas_300m = calc.okumura_hata(2100, 50, 0.3, 7.8)
        margen_ul = mapl_ul - perdidas_300m
        A_total_distrito = ((50000 * 60) / 8) * (18 / 60)
        A_real_distrito = A_total_distrito * 0.15
        A_celda_distrito = A_real_distrito / 7

        self.scenario1_summary['MAPL DL'].config(text=f'{mapl_dl:.1f} dB')
        self.scenario1_summary['MAPL UL'].config(text=f'{mapl_ul:.1f} dB')
        self.scenario1_summary['Path Loss 300m'].config(text=f'{perdidas_300m:.2f} dB')
        self.scenario1_summary['Margen UL'].config(text=f'{margen_ul:.2f} dB')
        self.scenario1_summary['Tráfico celda macro'].config(text=f'{A_celda_distrito:.2f} Erlangs')

        A_evento = ((140000 * 12) / 6) * (25 / 60)
        self.scenario2_total.config(text=f'{A_evento:.2f} Erlangs')

        self.scenario2_table.delete(*self.scenario2_table.get_children())
        scenario_values = []

        for m in [1200, 1600, 2000]:
            pb = calc.erlang_b(7292, m) * 100
            self.scenario2_table.insert('', 'end', values=('Macroceldas', m, f'{pb:.2f}'))
            scenario_values.append((f'Macro {m}', pb))

        for m in [500, 750, 900]:
            pb = calc.erlang_b(2333, m) * 100
            self.scenario2_table.insert('', 'end', values=('Micropicoceldas', m, f'{pb:.2f}'))
            scenario_values.append((f'Micro {m}', pb))

        for m in [300, 600, 1000]:
            pb = calc.erlang_b(511, m) * 100
            self.scenario2_table.insert('', 'end', values=('Femtoceldas', m, f'{pb:.2f}'))
            scenario_values.append((f'Femto {m}', pb))

        self.draw_scenario_chart(scenario_values)

    def draw_scenario_chart(self, values):
        labels = [item[0] for item in values]
        bloqueos = [item[1] for item in values]

        fig = plt.Figure(figsize=(8, 2.4), dpi=90)
        ax = fig.add_subplot(111)
        colors = ['#1f4f91' if 'Macro' in label else '#4f7a9d' if 'Micro' in label else '#d1495b' for label in labels]
        ax.bar(labels, bloqueos, color=colors)
        ax.set_title('Bloqueo estimado por tipo de celda y PRBs', fontsize=11)
        ax.set_ylabel('Bloqueo (%)')
        ax.set_xticklabels(labels, rotation=40, ha='right')
        ax.grid(axis='y', alpha=0.3)
        self._draw_chart(self.scenario2_chart_frame, fig, 'scenario_canvas')

if __name__ == '__main__':
    root = tk.Tk()
    app = SimuladorNexoApp(root)
    root.mainloop()
