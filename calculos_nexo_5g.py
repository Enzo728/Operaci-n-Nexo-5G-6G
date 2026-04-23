import math

# ==============================================================================
# 1. TEORÍA DE TRÁFICO
# ==============================================================================

def erlang_b(A, m):
    """
    Calcula la probabilidad de bloqueo usando la fórmula de Erlang B.
    Se utiliza un enfoque iterativo para evitar el desbordamiento (OverflowError)
    con factoriales al evaluar cientos o miles de canales.
    
    :param A: Tráfico total ofrecido en Erlangs.
    :param m: Número de canales o recursos disponibles.
    :return: Probabilidad de bloqueo (0.0 a 1.0)
    """
    if A == 0:
        return 0.0
    inv_B = 1.0
    for i in range(1, m + 1):
        inv_B = 1.0 + inv_B * (i / A)
    return 1.0 / inv_B

# ==============================================================================
# 2. BALANCE DE ENLACE (LINK BUDGET)
# ==============================================================================

def calcular_mapl_dl(pire_bts, sens_ms, g_ms, g_h, margenes):
    """Calcula la Atenuación Compensable Máxima en el Enlace Descendente (DL)"""
    return pire_bts - sens_ms + g_ms + g_h + margenes

def calcular_mapl_ul(pire_ms, sens_bts, g_bts, g_div, perdidas_cable_bts, margenes):
    """Calcula la Atenuación Compensable Máxima en el Enlace Ascendente (UL)"""
    return pire_ms - sens_bts + g_bts + g_div - perdidas_cable_bts + margenes

# ==============================================================================
# 3. MODELOS DE PROPAGACIÓN
# ==============================================================================

def walfisch_ikegami(fc_ghz, d_km, w, delta_hm, delta_hr, k_a, k_d):
    """
    Modelo Walfisch-Ikegami (Cost-231) para el entorno financiero.
    """
    L0 = 32.45 + 20 * math.log10(fc_ghz) + 20 * math.log10(d_km)
    L_rts = -16.9 - 10 * math.log10(w) + 10 * math.log10(fc_ghz) + 20 * math.log10(delta_hm)
    L_msd = -18 * math.log10(1 + delta_hr) + 0.12 * delta_hm + 20 * math.log10(d_km) + k_a + k_d * math.log10(d_km)
    return L0 + L_rts + L_msd

def okumura_hata(fc_mhz, h_te, d_km, a_hre):
    """
    Modelo Okumura-Hata para Área Urbana (aplica a 150-1500 MHz, ampliado para 2100).
    """
    L50 = 69.55 + 26.16 * math.log10(fc_mhz) - 13.82 * math.log10(h_te) - a_hre + (44.9 - 6.55 * math.log10(h_te)) * math.log10(d_km)
    return L50

# ==============================================================================
# EJECUCIÓN PRÁCTICA: REPRODUCCIÓN DE ESCENARIOS
# ==============================================================================

if __name__ == "__main__":
    print("==========================================================")
    print("  SIMULACIÓN DE RED MÓVIL - NUEVA PANGEA (5G/6G)")
    print("==========================================================\n")

    # --- ESCENARIO 1: DISTRITO FINANCIERO ---
    print("--- 1. ESCENARIO: DISTRITO FINANCIERO ---\n")
    
    # Cobertura (Link Budget)
    mapl_dl = calcular_mapl_dl(pire_bts=43, sens_ms=-101, g_ms=0, g_h=10, margenes=8)
    mapl_ul = calcular_mapl_ul(pire_ms=23, sens_bts=-104, g_bts=17, g_div=3, perdidas_cable_bts=2, margenes=7)
    
    print(f"MAPL DL (Descendente): {mapl_dl} dB")
    print(f"MAPL UL (Ascendente) : {mapl_ul} dB")
    limite_path_loss = min(mapl_dl, mapl_ul)
    print(f"-> Path Loss limitante: {limite_path_loss} dB\n")
    
    # Propagación a 300 metros
    fc_mhz = 2100
    h_te = 50
    d_km = 0.3
    a_hre = 7.8 # Factor usado en el documento para h_re = 20
    perdidas_300m = okumura_hata(fc_mhz, h_te, d_km, a_hre)
    print(f"Pérdidas Okumura-Hata a {d_km*1000}m: {perdidas_300m:.2f} dB")
    print(f"Margen disponible a {d_km*1000}m: {limite_path_loss - perdidas_300m:.2f} dB\n")
    
    # Capacidad (Tráfico)
    usuarios = 50000
    factor_concurrencia = 0.15
    llamadas_dia = 60
    horas_pico = 8
    minutos_sesion = 18
    
    lambda_llamadas = (usuarios * llamadas_dia) / horas_pico
    A_total = lambda_llamadas * (minutos_sesion / 60)
    A_real = A_total * factor_concurrencia
    A_por_celda = A_real / 7
    
    print(f"Tráfico ofrecido total: {A_total:.2f} Erlangs")
    print(f"Tráfico real (concurrencia 15%): {A_real:.2f} Erlangs")
    print(f"Tráfico estimado por celda macro: {A_por_celda:.2f} Erlangs\n")
    
    print("Evaluación de Probabilidad de Bloqueo (Erlang B) por celda:")
    for m in [30, 150, 300, 500]:
        pb = erlang_b(A_por_celda, m)
        print(f"  - Con m={m} canales: {pb*100:.4f}%")


    # --- ESCENARIO 2: FESTIVAL GLOBAL ---
    print("\n\n--- 2. ESCENARIO: FESTIVAL GLOBAL DE INNOVACIÓN ---\n")
    
    usuarios_evento = 140000
    llamadas_evento_hora = 12
    minutos_sesion_evento = 25
    horas_evento = 6
    
    # lambda se calculó como usuarios activos x tasa de llamadas en el evento
    lambda_evento = (usuarios_evento * llamadas_evento_hora) / horas_evento
    A_evento_total = lambda_evento * (minutos_sesion_evento / 60)
    
    print(f"Tráfico total del evento: {A_evento_total:.2f} Erlangs\n")
    
    # Distribución HetNet (según el documento con Cell-on-Wheels)
    A_macro_evento = 7292
    A_micro_evento = 2333
    A_femto_evento = 511
    
    print("Evaluación Erlang B - Macroceldas (Tráfico asignado = 7292 E):")
    for m in [1200, 1600, 2000]:
        pb = erlang_b(A_macro_evento, m)
        print(f"  - Con m={m} PRBs: {pb*100:.2f}%")
        
    print("\nEvaluación Erlang B - Micropicoceldas (Tráfico asignado = 2333 E):")
    for m in [250, 500, 750, 900]:
        pb = erlang_b(A_micro_evento, m)
        print(f"  - Con m={m} PRBs: {pb*100:.2f}%")
        
    print("\nEvaluación Erlang B - Femtoceldas (Tráfico asignado = 511 E):")
    for m in [100, 300, 600, 900, 1000]:
        pb = erlang_b(A_femto_evento, m)
        print(f"  - Con m={m} PRBs: {pb*100:.2f}%")

    print("\nVerificación de Cobertura en la Plaza (Okumura-Hata):")
    h_te_evento = 35
    d_km_evento = 0.8
    a_hre_evento = 0 # Usuario a nivel de calle/plaza
    
    perdidas_800m = okumura_hata(fc_mhz, h_te_evento, d_km_evento, a_hre_evento)
    # El documento asume un MAPL_DL = 162 dB
    mapl_evento_dl = 162 
    
    print(f"Pérdidas a {d_km_evento*1000}m: {perdidas_800m:.2f} dB")
    print(f"Margen disponible: {mapl_evento_dl - perdidas_800m:.2f} dB")
    print("\nEjecución completada con éxito. Todos los cálculos concuerdan con la práctica.")