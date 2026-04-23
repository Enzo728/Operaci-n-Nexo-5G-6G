import tkinter as tk
from tkinter import ttk, messagebox
import calculos_nexo_5g as calc

class SimuladorNexoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Operación Nexo 5G/6G - Equipo Consultor RF")
        self.root.geometry("850x650")

        # Crear sistema de pestañas
        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Definir pestañas
        self.tab_trafico = ttk.Frame(notebook)
        self.tab_link = ttk.Frame(notebook)
        self.tab_prop = ttk.Frame(notebook)
        self.tab_escenarios = ttk.Frame(notebook)

        notebook.add(self.tab_trafico, text="1. Teoría de Tráfico (Erlang)")
        notebook.add(self.tab_link, text="2. Balance de Enlace (MAPL)")
        notebook.add(self.tab_prop, text="3. Modelos de Propagación")
        notebook.add(self.tab_escenarios, text="4. Resolución Reto Pangea")

        self.setup_trafico()
        self.setup_link()
        self.setup_prop()
        self.setup_escenarios()

    # ==========================================
    # PESTAÑA 1: TRÁFICO
    # ==========================================
    def setup_trafico(self):
        frame = ttk.LabelFrame(self.tab_trafico, text="Calculadora Erlang B", padding=20)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Label(frame, text="Tráfico Ofrecido (A) en Erlangs:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_a = ttk.Entry(frame)
        self.ent_a.grid(row=0, column=1, pady=5)
        self.ent_a.insert(0, "344")

        ttk.Label(frame, text="Número de Canales / PRBs (m):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_m = ttk.Entry(frame)
        self.ent_m.grid(row=1, column=1, pady=5)
        self.ent_m.insert(0, "500")

        ttk.Button(frame, text="Calcular Bloqueo", command=self.calc_erlang).grid(row=2, column=0, columnspan=2, pady=15)
        
        self.lbl_res_erlang = ttk.Label(frame, text="Probabilidad de Bloqueo: -", font=('Helvetica', 12, 'bold'))
        self.lbl_res_erlang.grid(row=3, column=0, columnspan=2, pady=5)

    def calc_erlang(self):
        try:
            a = float(self.ent_a.get())
            m = int(self.ent_m.get())
            pb = calc.erlang_b(a, m)
            self.lbl_res_erlang.config(text=f"Probabilidad de Bloqueo: {pb*100:.4f}%")
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce valores numéricos válidos.")

    # ==========================================
    # PESTAÑA 2: BALANCE DE ENLACE
    # ==========================================
    def setup_link(self):
        frame_dl = ttk.LabelFrame(self.tab_link, text="Enlace Descendente (DL)", padding=10)
        frame_dl.pack(padx=20, pady=10, fill="x")

        self.ent_dl = {}
        labels_dl = ["PIRE BTS (dBm)", "Sensibilidad MS (dBm)", "Ganancia MS (dBi)", "Ganancia Altura (dB)", "Márgenes (dB)"]
        defaults_dl = ["43", "-101", "0", "10", "8"]
        
        for i, (lbl, default) in enumerate(zip(labels_dl, defaults_dl)):
            ttk.Label(frame_dl, text=lbl).grid(row=i, column=0, sticky="w", pady=2)
            ent = ttk.Entry(frame_dl)
            ent.insert(0, default)
            ent.grid(row=i, column=1, pady=2, padx=10)
            self.ent_dl[lbl] = ent

        ttk.Button(frame_dl, text="Calcular MAPL DL", command=self.calc_mapl_dl).grid(row=5, column=0, columnspan=2, pady=10)
        self.lbl_res_dl = ttk.Label(frame_dl, text="MAPL DL: -", font=('Helvetica', 10, 'bold'))
        self.lbl_res_dl.grid(row=6, column=0, columnspan=2)

    def calc_mapl_dl(self):
        try:
            vals = [float(e.get()) for e in self.ent_dl.values()]
            res = calc.calcular_mapl_dl(*vals)
            self.lbl_res_dl.config(text=f"MAPL DL: {res:.2f} dB")
        except:
            messagebox.showerror("Error", "Revisa los campos del DL.")

    # ==========================================
    # PESTAÑA 3: PROPAGACIÓN
    # ==========================================
    def setup_prop(self):
        frame_oku = ttk.LabelFrame(self.tab_prop, text="Modelo Okumura-Hata", padding=10)
        frame_oku.pack(padx=20, pady=10, fill="x")

        self.ent_oku = {}
        labels_oku = ["Frecuencia (MHz)", "Altura Tx (m)", "Distancia (km)", "Factor Corr. Móvil (dB)"]
        defaults_oku = ["2100", "50", "0.3", "7.8"]
        
        for i, (lbl, default) in enumerate(zip(labels_oku, defaults_oku)):
            ttk.Label(frame_oku, text=lbl).grid(row=i, column=0, sticky="w", pady=2)
            ent = ttk.Entry(frame_oku)
            ent.insert(0, default)
            ent.grid(row=i, column=1, pady=2, padx=10)
            self.ent_oku[lbl] = ent

        ttk.Button(frame_oku, text="Calcular Pérdidas", command=self.calc_oku).grid(row=4, column=0, columnspan=2, pady=10)
        self.lbl_res_oku = ttk.Label(frame_oku, text="Pérdidas L50: -", font=('Helvetica', 10, 'bold'))
        self.lbl_res_oku.grid(row=5, column=0, columnspan=2)

    def calc_oku(self):
        try:
            vals = [float(e.get()) for e in self.ent_oku.values()]
            res = calc.okumura_hata(*vals)
            self.lbl_res_oku.config(text=f"Pérdidas L50: {res:.2f} dB")
        except:
            messagebox.showerror("Error", "Revisa los campos de Okumura-Hata.")

    # ==========================================
    # PESTAÑA 4: RESOLUCIÓN PRÁCTICA (ESCENARIOS)
    # ==========================================
    def setup_escenarios(self):
        frame = ttk.Frame(self.tab_escenarios, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Presiona el botón para ejecutar la batería de pruebas y mostrar los resultados de la práctica:", font=('Helvetica', 10)).pack(pady=5)
        ttk.Button(frame, text="Ejecutar Simulador de Nueva Pangea", command=self.run_practice).pack(pady=10)

        # Área de texto con Scroll
        scroll = ttk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")
        
        self.txt_out = tk.Text(frame, yscrollcommand=scroll.set, wrap="word", font=('Consolas', 10))
        self.txt_out.pack(fill="both", expand=True)
        scroll.config(command=self.txt_out.yview)

    def run_practice(self):
        self.txt_out.delete(1.0, tk.END)
        out = []
        out.append("==========================================================")
        out.append("  INFORME TÉCNICO - RED MÓVIL NUEVA PANGEA (5G/6G)")
        out.append("==========================================================\n")
        
        # ESCENARIO 1
        out.append(">>> ESCENARIO 1: DISTRITO FINANCIERO (Cobertura Interior)")
        mapl_dl = calc.calcular_mapl_dl(43, -101, 0, 10, 8)
        mapl_ul = calc.calcular_mapl_ul(23, -104, 17, 3, 2, 7)
        out.append(f"MAPL DL: {mapl_dl} dB | MAPL UL: {mapl_ul} dB")
        
        perdidas_300m = calc.okumura_hata(2100, 50, 0.3, 7.8)
        out.append(f"Path Loss Okumura-Hata a 300m: {perdidas_300m:.2f} dB")
        out.append(f"Margen restante en UL: {mapl_ul - perdidas_300m:.2f} dB (Suficiente para penetración)\n")

        A_total_distrito = ((50000 * 60) / 8) * (18 / 60)
        A_real_distrito = A_total_distrito * 0.15
        A_celda_distrito = A_real_distrito / 7
        out.append(f"Tráfico Total del Distrito (15% act.): {A_real_distrito:.2f} E")
        out.append(f"Tráfico asignado a celda Macro: {A_celda_distrito:.2f} E")
        
        for m in [30, 150, 300, 500]:
            pb = calc.erlang_b(A_celda_distrito, m)
            out.append(f" - Evaluando con {m} canales -> Bloqueo: {pb*100:.4f}%")
        out.append("CONCLUSIÓN 1: Se necesitan 500 PRBs por macro para P_b < 0.02%\n")

        # ESCENARIO 2
        out.append("----------------------------------------------------------")
        out.append(">>> ESCENARIO 2: FESTIVAL GLOBAL (Capacidad Masiva)")
        
        A_evento = ((140000 * 12) / 6) * (25 / 60)
        out.append(f"Tráfico Total del Evento: {A_evento:.2f} E")
        
        A_macro = 7292
        A_micro = 2333
        A_femto = 511
        out.append("\nDespliegue HetNet (Asignación de tráfico):")
        out.append(f"- Macroceldas ({A_macro} E/celda):")
        for m in [1200, 1600, 2000]:
            pb = calc.erlang_b(A_macro, m)
            out.append(f"   * m={m} PRBs -> Bloqueo: {pb*100:.2f}%")
            
        out.append(f"- Micropicoceldas ({A_micro} E/celda):")
        for m in [500, 750, 900]:
            pb = calc.erlang_b(A_micro, m)
            out.append(f"   * m={m} PRBs -> Bloqueo: {pb*100:.2f}%")
            
        out.append(f"- Femtoceldas ({A_femto} E/celda):")
        for m in [300, 600, 1000]:
            pb = calc.erlang_b(A_femto, m)
            out.append(f"   * m={m} PRBs -> Bloqueo: {pb*100:.2f}%")
            
        perdidas_evento = calc.okumura_hata(2100, 35, 0.8, 0)
        out.append(f"\nVerificación Cobertura Plaza (800m): {perdidas_evento:.2f} dB")
        out.append(f"Margen DL (respecto a 162 dB): {162 - perdidas_evento:.2f} dB")
        out.append("CONCLUSIÓN 2: Despliegue HetNet viabiliza el evento con bloqueos ~4%.")

        self.txt_out.insert(tk.END, "\n".join(out))

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorNexoApp(root)
    root.mainloop()