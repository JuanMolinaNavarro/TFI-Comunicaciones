import time
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel, amplitude_damping_error, phase_damping_error

st.set_page_config(page_title="Senal cuantica con ruido", page_icon="Q", layout="wide")


def apply_shadcn_dark():
    """Inject a shadcn-inspired dark theme for the whole app."""
    shadcn_css = """
    <style>
    :root {
        --bg: #0b1021;
        --panel: #0f172a;
        --muted: #94a3b8;
        --primary: #7c3aed;
        --primary-strong: #8b5cf6;
        --border: #1f2937;
    }
    .stApp {
        background:
            radial-gradient(circle at 12% 20%, rgba(124, 58, 237, 0.08), transparent 25%),
            radial-gradient(circle at 80% 0%, rgba(245, 158, 11, 0.08), transparent 20%),
            var(--bg);
        color: #e5e7eb;
        font-family: "Inter", "Segoe UI", system-ui, sans-serif;
    }
    .block-container { padding-top: 1.4rem; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%);
        border-right: 1px solid var(--border);
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.35);
    }
    [data-testid="stSidebar"] .block-container { padding: 1.1rem 0.85rem 1.4rem; }
    .sidebar-card {
        padding: 0.85rem 1rem;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: #0b1220;
        margin-bottom: 0.95rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }
    .sidebar-title {
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: 0.01em;
        font-size: 1rem;
        margin-bottom: 0.35rem;
    }
    .sidebar-foot { color: var(--muted); font-size: 0.85rem; margin-top: 0.35rem; }
    .stSlider [data-baseweb="slider"] > div:nth-child(1) {
        background: linear-gradient(90deg, #0d1324, #0b1021);
        border: 1px solid #1f2937;
        border-radius: 12px;
        height: 12px;
    }
    .stSlider [role="slider"] {
        background: radial-gradient(circle at 30% 30%, #e0d7ff, #8b5cf6 65%, #6d28d9);
        border: 0;
        box-shadow: 0 10px 28px rgba(124, 58, 237, 0.35), 0 0 0 1px rgba(139,92,246,0.25);
        width: 18px;
        height: 18px;
    }
    .stSlider [data-testid="stTickBar"] > div { background: linear-gradient(90deg, #312e81, #7c3aed); }
    .stSlider [data-testid="stTickBar"] p { color: #94a3b8 !important; font-weight: 600; }
    .stSelectbox, .stMultiSelect, .stNumberInput, .stTextInput, .stDateInput {
        background: var(--panel);
    }
    .stAlert {
        border-radius: 12px;
        border: 1px solid var(--border);
        background: var(--panel);
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #f8fafc; }
    </style>
    """
    st.markdown(shadcn_css, unsafe_allow_html=True)


apply_shadcn_dark()

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-card">
            <div class="sidebar-title">Quantum Noise Lab</div>
            <div class="sidebar-foot">Explora decoherencia en vivo con un estilo oscuro inspirado en shadcn.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu_styles = {
        "container": {
            "padding": "0.5rem",
            "background": "#0f172a",
            "border-radius": "14px",
            "border": "1px solid #1f2937",
            "box-shadow": "0 10px 26px rgba(0,0,0,0.25)",
        },
        "icon": {"color": "#94a3b8", "font-size": "1rem"},
        "nav-link": {
            "font-size": "0.95rem",
            "padding": "0.6rem 0.75rem",
            "color": "#e2e8f0",
            "border-radius": "12px",
            "margin": "0.2rem 0",
            "background-color": "#0b1220",
            "border": "1px solid #1f2937",
        },
        "nav-link-selected": {
            "background-color": "#111827",
            "color": "#f8fafc",
            "border": "1px solid #7c3aed",
            "box-shadow": "0 0 0 1px rgba(124,58,237,0.35)",
        },
    }

    selected = option_menu(
        "Navegacion",
        ["Simulacion", "Acerca", "Contacto"],
        icons=["activity", "info-circle", "envelope"],
        menu_icon="cast",
        default_index=0,
        styles=menu_styles,
    )

# Controls when in simulation
if selected == "Simulacion":
    st.sidebar.markdown(
        '<div class="sidebar-title" style="margin-top:0.15rem;">Controles</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="sidebar-foot" style="margin-bottom:0.35rem;">Ajusta los sliders para visualizar la decadencia en tiempo real.</div>',
        unsafe_allow_html=True,
    )
    shots = st.sidebar.slider("Shots por punto", min_value=200, max_value=5000, value=2000, step=200)
    paso = st.sidebar.slider("Paso de ruido", min_value=0.01, max_value=0.2, value=0.05, step=0.01)
    max_ruido = st.sidebar.slider("Maximo ruido", min_value=0.2, max_value=1.0, value=1.0, step=0.01)
    intervalo_ms = st.sidebar.slider("Intervalo de actualizacion (ms)", min_value=1, max_value=1500, value=500, step=50)
else:
    shots = 2000
    paso = 0.05
    max_ruido = 1.0
    intervalo_ms = 500


@st.cache_resource
def get_backend():
    return Aer.get_backend("qasm_simulator")


def simular_con_ruido(prob_amp: float, prob_phase: float, shots_local: int) -> float:
    noise = NoiseModel()
    amp_error = amplitude_damping_error(prob_amp)
    phase_error = phase_damping_error(prob_phase)
    noise.add_quantum_error(amp_error, ["h"], [0])
    noise.add_quantum_error(phase_error, ["h"], [0])

    qreg_q = QuantumRegister(1, "q")
    creg_c = ClassicalRegister(1, "c")
    qc = QuantumCircuit(qreg_q, creg_c)
    qc.h(qreg_q[0])
    qc.measure(qreg_q[0], creg_c[0])

    backend = get_backend()
    job = backend.run(qc, noise_model=noise, shots=shots_local)
    result = job.result().get_counts()
    return result.get("1", 0) / shots_local


# ------------------------------------------------------
#                     INTERFAZ STREAMLIT
# ------------------------------------------------------

if selected == "Simulacion":
    st.title("Senal cuantica bajo ruido")
    st.caption("Comparación en tiempo real entre señal ideal y señal degradada por ruido cuántico.")

    placeholder = st.empty()
    niveles = np.arange(0, max_ruido + paso, paso)

    prob1_amp = []
    prob1_phase = []
    ideal = []

    # ---------------------------
    #       LOOP ANIMADO
    # ---------------------------
    for n in niveles:

        # Señal ideal = 0.5 TODO EL TIEMPO
        ideal.append(0.5)

        # Señales con decoherencia
        prob1_amp.append(simular_con_ruido(n, 0, shots))
        prob1_phase.append(simular_con_ruido(0, n, shots))

        # Estilo moderno
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(9.5, 5.25), facecolor="#0b1021")
        fig.patch.set_facecolor("#0b1021")

        # -------------------------------
        #       CURVA IDEAL (NUEVA)
        # -------------------------------
        ax.plot(
            niveles[: len(ideal)],
            ideal,
            label="Señal ideal (sin ruido)",
            color="#FFFFFF",
            linewidth=2,
            linestyle="--",
            alpha=0.8,
        )

        # --------------------------------
        #       RUIDO AMPLITUD
        # --------------------------------
        ax.plot(
            niveles[: len(prob1_amp)],
            prob1_amp,
            label="Decoherencia por amplitud",
            color="#7C3AED",
            linewidth=3,
            alpha=0.9,
        )
        ax.fill_between(niveles[: len(prob1_amp)], prob1_amp, color="#7C3AED", alpha=0.1)

        # --------------------------------
        #       RUIDO FASE
        # --------------------------------
        ax.plot(
            niveles[: len(prob1_phase)],
            prob1_phase,
            label="Decoherencia por fase",
            color="#F59E0B",
            linewidth=3,
            alpha=0.9,
        )
        ax.fill_between(niveles[: len(prob1_phase)], prob1_phase, color="#F59E0B", alpha=0.08)

        ax.set_xlim(0, max_ruido)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Nivel de ruido", color="#E5E7EB", fontsize=11)
        ax.set_ylabel("Probabilidad de medir |1>", color="#E5E7EB", fontsize=11)
        ax.set_title("Comparación de señal ideal vs ruido", color="#FFFFFF", fontsize=14, pad=14)

        ax.set_facecolor("#11162d")
        ax.tick_params(colors="#cbd5e1")
        for spine in ax.spines.values():
            spine.set_color("#1f2937")

        ax.grid(True, color="#1f2937", alpha=0.8, linestyle="--", linewidth=0.8)
        legend = ax.legend(frameon=False, fontsize=10)
        for text in legend.get_texts():
            text.set_color("#E5E7EB")

        placeholder.pyplot(fig)
        time.sleep(intervalo_ms / 1000)

    st.success("Simulacion completada.")

elif selected == "Acerca":
    st.title("Acerca de esta demo")
    st.write(
        """
        Comparación visual entre señal cuántica ideal y señal afectada por decoherencia.
        """
    )
elif selected == "Contacto":
    st.title("Contacto")
    st.write("Autor: demo cuantica. Ajusta el menu para volver a la simulacion.")