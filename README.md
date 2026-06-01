# Topología del Metro CDMX y Propagación de COVID-19: Análisis de Redes Complejas

> Un análisis integrado de la red del Sistema de Transporte Colectivo Metro de la Ciudad de México y su relación con la propagación de COVID-19 durante 2020-2021, utilizando teoría de redes complejas, simulaciones SIR y aprendizaje automático.

## Resumen Ejecutivo

Este proyecto investiga cómo la topología de la red del Metro CDMX influye en la propagación de COVID-19 entre alcaldías. A través de:

- **162 estaciones** y **183 conexiones** ponderadas por afluencia diaria
- **Métricas de red compleja**: betweenness, closeness, clustering, grado ponderado
- **Simulaciones SIR** en la red real vs. tres redes sintéticas de referencia
- **Validación con Machine Learning** (Random Forest)

---

## Estructura del Proyecto

```
.
├── README.md                              # Este archivo
├── filtrar.py                             # Filtrado y limpieza de datos COVID-19
├── filtrar_metro.py                       # Filtrado de datos de afluencia del Metro
├── analysis.py                            # Pipeline principal de análisis
├── run_analysis.py                        # Ejecutor del análisis completo
│
├── reporte/
│   ├── reporte_final.tex                  # Manuscrito principal en LaTeX
│   ├── logo_unam.png                      # Logo UNAM
│   ├── logo_iimas.png                     # Logo IIMAS
│   ├── red_metro_geografica.png          # Visualización geográfica de la red
│   ├── top10_estaciones.png              # Estaciones con mayor betweenness
│   ├── comparacion_SIR.png               # Comparación de simulaciones SIR
│   ├── feature_importances.png           # Importancia de características ML
│   └── predicho_vs_real.png              # Validación del modelo Random Forest
│
├── resultados/                            # Outputs del análisis
│   ├── node_metrics.csv                   # Métricas por estación (162 registros)
│   ├── alcaldia_metrics.csv              # Métricas agregadas por alcaldía
│   ├── ml_data.csv                        # Features y target para ML
│   ├── resumen_metricas.json             # Resumen global de la red
│   ├── metro_network.graphml             # Red en formato GraphML
│   ├── modelo_rf.pkl                     # Modelo Random Forest entrenado
│   └── [*.png]                           # Visualizaciones detalladas
│
├── COVID19MEXICO2020_2021_CDMX.csv        # Datos COVID filtrados (CDMX)
├── afluenciastc_2020_2021.csv            # Datos de afluencia del Metro filtrados
├── estaciones_coords.csv                 # Coordenadas geográficas de estaciones
└── proyecto_redes.ipynb                  # Notebook de analisis exploratorio
```

---

## Inicio Rápido

### Requisitos

- Python 3.10+
- Dependencias: `pandas`, `numpy`, `networkx`, `matplotlib`, `seaborn`, `scipy`, `scikit-learn`

```bash
pip install pandas numpy networkx matplotlib seaborn scipy scikit-learn
```

### Ejecución

1. **Filtrar y preparar datos:**
   ```bash
   python filtrar.py
   python filtrar_metro.py
   ```

2. **Ejecutar análisis completo:**
   ```bash
   python analysis.py
   ```
   Genera 13 archivos en `resultados/` incluyendo métricas, simulaciones y visualizaciones.

## Datos de Entrada

### 1. COVID-19
**Fuente:** [Dirección General de Epidemiología, Secretaría de Salud de México](https://www.gob.mx/salud/documentos/datos-abiertos-bases-historicas-direccion-general-de-epidemiologia)
- Bases históricas 2020-2021
- Filtrados: CDMX (ENTIDAD_RES = 09) + confirmados (CLASIFICACION_FINAL ∈ {1,2,3})
- Agregación: mensual por alcaldía

### 2. Afluencia del Metro
**Fuente:** [Portal de Datos Abiertos CDMX](https://datos.cdmx.gob.mx/dataset/afluencia-diaria-del-metro-cdmx)
- Usuarios que ingresan diariamente por estación (2020-2021)
- Utilizado: promedio diario 2020 como peso de nodos

### 3. Coordenadas de Estaciones
**Fuente:** [GitHub - Juan Bosco Mendoza Vega](https://github.com/jboscomendoza/coordenadas_metro_cdmx)
- Latitud, longitud y línea de cada estación
- 162 estaciones del Sistema de Transporte Colectivo

---

## Metodología

### Construcción de la Red

La red se representa como grafo no dirigido G = (V, E):
- **V:** 162 estaciones
- **E:** 183 conexiones (adyacentes dentro de cada línea)
- **Pesos:** $w_{ij} = \frac{\bar{a}_i + \bar{a}_j}{2}$ (promedio de afluencia)

### Métricas de Red

| Métrica | Descripción |
|---------|-------------|
| **Grado** | Número de estaciones adyacentes |
| **Grado Ponderado** | Suma de pesos de aristas incidentes |
| **Betweenness** | Proporción de caminos cortos que pasan por el nodo |
| **Closeness** | Inversa de la suma de distancias |
| **Clustering Local** | Proporción de triángulos en la vecindad |

**Resultados globales:**
- Densidad: 0.0524
- Diámetro: 4
- Camino promedio: 2.25
- Clustering global: 0.5783
- Grado promedio: 8.44

### Simulaciones SIR

Modelo discreto con parámetros:
- **β = 0.3:** probabilidad de contagio por arista por timestep
- **γ = 0.1:** probabilidad de recuperación
- **Duraciones:** hasta 200 pasos o eliminar infectados

**Configuraciones:**
- Red real: inicio en nodos de mayor betweenness vs. aleatorio
- Redes sintéticas: Erdős–Rényi, Watts–Strogatz, Barabási–Albert

### Validación Predictiva

Random Forest con Leave-One-Out CV (LOO-CV):
- **Features:** betweenness, grado, clustering promedio por alcaldía + grado ponderado
- **Target:** casos COVID acumulados por alcaldía
- **Muestra:** 10 alcaldías con datos completos

---

## Resultados Principales

### 1. Estructura de la Red
La red exhibe propiedades **pequeño-mundo**:
- Alto clustering local (0.58) indica zonas densamente interconectadas
- Diámetro bajo (4) permite rutas cortas entre estaciones distantes
- Grado promedio (8.44) revela conectividad moderada

**Estaciones críticas (top-5 betweenness):**
1. Santa Anita
2. Chabacano
3. Morelos
4. La Paz
5. Balderas

### 2. Simulaciones SIR

| Red | Pico de Infección | Tiempo al Pico |
|-----|------------------|-----------------|
| **Real (Metro)** | 47.84% | ~25 steps |
| Erdős–Rényi | 78.89% | ~18 steps |
| Watts–Strogatz | 74.32% | ~20 steps |
| Barabási–Albert | 66.79% | ~22 steps |

**Interpretación:** La geometría física y restricciones terminales del Metro reducen la propagación epidémica en ~38% vs. redes sintéticas equivalentes.

### 3. Validación ML

**Desempeño del Random Forest (LOO-CV):**
- R² = -1.06 (indica poder predictivo nulo)
- MAE = 59,291 casos
- RMSE = 67,266 casos

**Importancia de características:**
- Grado promedio: 36.9%
- Clustering promedio: 27.0%
- Grado ponderado: 20.3%
- Betweenness promedio: 15.9%

**Conclusión:** Las métricas topológicas no son suficientes para explicar patrones espaciales de COVID-19. Factores adicionales (demografía, socioeconómicos, políticas) son necesarios.

---

## Archivos de Salida Clave

### Datos

| Archivo | Descripción | Registros |
|---------|-------------|-----------|
| `COVID19MEXICO2020_2021_CDMX.csv` | Casos COVID filtrados | ~200K |
| `afluenciastc_2020_2021.csv` | Afluencia diaria filtrada | ~1.8M |
| `resultados/node_metrics.csv` | Métricas por estación | 162 |
| `resultados/alcaldia_metrics.csv` | Agregados por alcaldía | 10 |

### Modelos

- `resultados/metro_network.graphml` — Red en GraphML (importable en Gephi)
- `resultados/modelo_rf.pkl` — Random Forest entrenado (Python pickle)

### Visualizaciones

Todas en formato PNG 300 dpi:
- `red_metro_geografica.png` — Mapa georreferenciado
- `top10_estaciones.png` — Estaciones críticas
- `comparacion_SIR.png` — Dinámicas de epidemia
- `feature_importances.png` — Contribución de variables
- `predicho_vs_real.png` — Validación del modelo

---

## Reporte

El manuscrito completo está en ** `reporte/PYARS_ErickFabian.pdf`** listo tambien para compilación en Overleaf de la carpeta `reporte/`.

**Secciones incluidas:**
- Introducción y estado del arte
- Métodos y fuentes de datos
- Resultados cuantitativos
- Simulaciones SIR
- Validación predictiva
- Discusión e implicaciones para salud pública
- Referencias bibliográficas

**Para compilar a PDF localmente:**
```bash
cd reporte
pdflatex reporte_final.tex
```

---

## Implicaciones para Salud Pública

1. **Identificación de nodos críticos:** Estaciones con alto betweenness y grado ponderado son puntos clave para intervenciones focalizadas.

2. **Mitigación espacial:** La topología del Metro naturalmente amortigua propagación vs. redes idealizadas; sin embargo, la geometría física no es factor dominante en explicar COVID-19.

3. **Enfoque integrado:** Las políticas deben combinar datos de red con covariables demográficas, epidemiológicas y de comportamiento.

---

## 🔧 Tecnologías Utilizadas

- **Python 3.10** — Lenguaje principal
- **NetworkX** — Análisis de redes
- **Pandas & NumPy** — Procesamiento de datos
- **Matplotlib & Seaborn** — Visualización
- **Scikit-learn** — Machine Learning
- **LaTeX** — Reporte académico
- **Git & GitHub** — Control de versiones

---

## Referencias

1. Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of small-world networks. *Nature*, 393(6684), 440–442.

2. Barabási, A.-L., & Albert, R. (1999). Emergence of scaling in random networks. *Science*, 286(5439), 509–512.

3. Newman, M. E. J. (2003). The structure and function of complex networks. *SIAM Review*, 45(2), 167–256.

4. Pastor-Satorras, R., & Vespignani, A. (2001). Epidemic spreading in scale-free networks. *Physical Review Letters*, 86(14), 3200–3203.

---

## Autor

**Proyecto Final de la Materia Analisis de Redes Complejas**  
Análisis topológico del Metro CDMX y COVID-19 | 2020-2021

---

## Contacto

Para preguntas o sugerencias sobre el análisis, datos o metodología, favor de consultar la documentación en `reporte/PYARS_ErickFabian.pdf` o abrir un issue en este repositorio.

---

**Última actualización:** Junio 2026
