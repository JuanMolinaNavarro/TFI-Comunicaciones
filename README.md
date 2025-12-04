# Simulador de ruido cuántico (Streamlit)

Aplicación web en Streamlit que simula la decoherencia de un qubit aplicando ruido de amplitud y de fase con Qiskit Aer. A medida que aumenta el nivel de ruido, se grafica en tiempo real la probabilidad de medir el estado |1> y se compara contra la señal ideal sin ruido.

## ¿Para qué sirve?

- Visualizar cómo la decoherencia afecta a un qubit en un circuito básico (puerta H y medición).
- Ajustar parámetros de simulación (shots, paso de ruido, nivel máximo y frecuencia de actualización) y ver al instante su impacto.
- Mostrar dos canales de ruido independientes (amplitud y fase) frente a la señal ideal en una sola gráfica.
- Explorar la demo desde una interfaz oscura con navegación lateral (“Simulación”, “Acerca” y “Contacto”).

## Librerías utilizadas

- `streamlit` y `streamlit_option_menu` para la interfaz y navegación.
- `matplotlib` para la gráfica en tiempo real.
- `numpy` para generar los niveles de ruido.
- `qiskit` y `qiskit_aer` para simular el circuito y aplicar el modelo de ruido (amplitude damping y phase damping).
- `time` de la librería estándar para controlar el intervalo de actualización.

## Cómo ejecutar

1) Crea un entorno:
   - PowerShell: `python -m venv .venv; .venv\\Scripts\\Activate.ps1`
2) Instalar dependencias:
   - `pip install streamlit matplotlib numpy qiskit qiskit-aer streamlit-option-menu`
3) Iniciar la app:
   - `streamlit run streamlit_app.py`

El navegador abrirá la interfaz con el menú lateral. Ajusta los sliders en “Simulación” para ver la comparación en tiempo real entre la señal ideal y la degradada por ruido.
