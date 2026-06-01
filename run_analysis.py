#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Redes Sociales: Metro CDMX y COVID-19 (2020-2021)
Script completo para análisis de la red del Metro y propagación de COVID-19
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd

# Configurar encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import random
import pickle
import glob

# ==================== CONFIGURACIÓN ====================
warnings.filterwarnings('ignore')
random.seed(42)
np.random.seed(42)
os.makedirs('resultados', exist_ok=True)
os.makedirs('reporte', exist_ok=True)

# Usar backend sin GUI
import matplotlib
matplotlib.use('Agg')

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("=" * 80)
print("ANÁLISIS DE REDES SOCIALES: METRO CDMX Y COVID-19 (2020-2021)")
print("=" * 80)
print(f"Inicio: {datetime.now().isoformat()}\n")

# ==================== PASO 0: CARGA E INSPECCIÓN ====================
print("\n" + "=" * 80)
print("PASO 0: CARGA E INSPECCIÓN DE DATOS")
print("=" * 80)

try:
    df_metro = pd.read_csv('afluenciastc_2020_2021.csv', encoding='utf-8')
    df_covid = pd.read_csv('COVID19MEXICO2020_2021_CDMX.csv', encoding='utf-8')
    df_coords = pd.read_csv('estaciones_coords.csv', encoding='utf-8')
    print("[OK] Archivos CSV cargados exitosamente")
except Exception as e:
    print(f"[ERROR] Error al cargar CSV: {e}")
    sys.exit(1)

print(f"\nDatos de Afluencia del Metro:")
print(f"  Shape: {df_metro.shape}")
print(f"  Columnas: {list(df_metro.columns)}")

print(f"\nDatos de COVID-19:")
print(f"  Shape: {df_covid.shape}")
print(f"  Columnas: {list(df_covid.columns)}")

print(f"\nDatos de Coordenadas:")
print(f"  Shape: {df_coords.shape}")
print(f"  Columnas: {list(df_coords.columns)}")

# Preparar datos
df_metro['fecha'] = pd.to_datetime(df_metro['fecha'])
df_metro['anio'] = df_metro['anio'].astype(int)
df_metro_2020 = df_metro[df_metro['anio'] == 2020].copy()

df_metro['estacion'] = df_metro['estacion'].str.strip()
df_coords['estacion'] = df_coords['estacion'].str.strip()

print(f"\n[OK] Estaciones unicas: {df_metro['estacion'].nunique()}")
print(f"[OK] Lineas unicas: {df_metro['linea'].nunique()}")

# ==================== PASO 1: CONSTRUCCIÓN DE RED ====================
print("\n" + "=" * 80)
print("PASO 1: CONSTRUCCIÓN DE LA RED DEL METRO")
print("=" * 80)

G = nx.Graph()
afluencia_promedio = df_metro_2020.groupby('estacion')['afluencia'].mean()

# Crear nodos
estaciones_coords_dict = {}
for _, row in df_coords.iterrows():
    estacion = row['estacion']
    G.add_node(estacion, lat=row['lat'], lng=row['lng'])
    estaciones_coords_dict[estacion] = (row['lat'], row['lng'])

# Crear aristas
print("Creando aristas entre estaciones adyacentes...")
aristas_por_linea = {}

for linea in df_metro_2020['linea'].unique():
    estaciones_linea = df_metro_2020[df_metro_2020['linea'] == linea].groupby('fecha')['estacion'].apply(list)
    
    for fecha, estaciones in estaciones_linea.items():
        for i in range(len(estaciones) - 1):
            u, v = estaciones[i], estaciones[i+1]
            
            if u in G and v in G:
                weight_u = afluencia_promedio.get(u, 0)
                weight_v = afluencia_promedio.get(v, 0)
                avg_weight = (weight_u + weight_v) / 2
                
                if G.has_edge(u, v):
                    G[u][v]['weight'] = (G[u][v]['weight'] + avg_weight) / 2
                else:
                    G.add_edge(u, v, weight=avg_weight, linea=linea)
                    if linea not in aristas_por_linea:
                        aristas_por_linea[linea] = 0
                    aristas_por_linea[linea] += 1

print(f"\n✓ Red construida:")
print(f"  Nodos (estaciones): {G.number_of_nodes()}")
print(f"  Aristas (conexiones): {G.number_of_edges()}")
print(f"  Densidad: {nx.density(G):.6f}")

nx.write_graphml(G, 'resultados/metro_network.graphml')
print(f"✓ Red guardada: resultados/metro_network.graphml")

# ==================== PASO 2: ANÁLISIS ESTRUCTURAL ====================
print("\n" + "=" * 80)
print("PASO 2: ANÁLISIS ESTRUCTURAL DE LA RED")
print("=" * 80)

print("Calculando métricas de centralidad...")

node_metrics = {}
degree = dict(G.degree())
weighted_degree = dict(G.degree(weight='weight'))
betweenness = nx.betweenness_centrality(G, weight='weight')
closeness = nx.closeness_centrality(G, distance='weight')
clustering = nx.clustering(G)

for nodo in G.nodes():
    node_metrics[nodo] = {
        'grado': degree[nodo],
        'grado_ponderado': weighted_degree[nodo],
        'betweenness': betweenness[nodo],
        'closeness': closeness[nodo],
        'clustering': clustering[nodo],
        'lat': G.nodes[nodo].get('lat', None),
        'lng': G.nodes[nodo].get('lng', None)
    }

df_metrics = pd.DataFrame(node_metrics).T.reset_index()
df_metrics.columns = ['estacion', 'grado', 'grado_ponderado', 'betweenness', 'closeness', 'clustering', 'lat', 'lng']
df_metrics.to_csv('resultados/node_metrics.csv', index=False)
print(f"✓ Métricas guardadas: resultados/node_metrics.csv")

# Métricas globales
print(f"\nMétricas Globales:")
if nx.is_connected(G):
    diametro = nx.diameter(G)
    promedio_camino = nx.average_shortest_path_length(G)
    print(f"  Diámetro: {diametro}")
    print(f"  Longitud promedio del camino: {promedio_camino:.4f}")
else:
    largest_cc = max(nx.connected_components(G), key=len)
    G_temp = G.subgraph(largest_cc)
    diametro = nx.diameter(G_temp)
    promedio_camino = nx.average_shortest_path_length(G_temp)
    print(f"  Diámetro (componente principal): {diametro}")
    print(f"  Longitud promedio del camino (componente principal): {promedio_camino:.4f}")

clustering_global = nx.average_clustering(G)
densidad = nx.density(G)
grado_promedio = sum(degree.values()) / len(degree)

print(f"  Coeficiente de clustering global: {clustering_global:.4f}")
print(f"  Densidad: {densidad:.6f}")
print(f"  Grado promedio: {grado_promedio:.4f}")

grados = list(degree.values())
print(f"\nDistribución de grado:")
print(f"  Mín: {min(grados)}, Máx: {max(grados)}, Media: {np.mean(grados):.2f}, Mediana: {np.median(grados):.0f}")

# ==================== PASO 3: VISUALIZACIONES ====================
print("\n" + "=" * 80)
print("PASO 3: VISUALIZACIONES DE LA RED")
print("=" * 80)

# 1. Red geográfica
print("Creando visualización 1: Red Geográfica...")
fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
pos = {nodo: (G.nodes[nodo]['lng'], G.nodes[nodo]['lat']) for nodo in G.nodes()}

betweenness_vals = np.array([betweenness[n] for n in G.nodes()])
weighted_degree_vals = np.array([weighted_degree[n] for n in G.nodes()])
size_nodes = 300 + 2700 * (betweenness_vals - betweenness_vals.min()) / (betweenness_vals.max() - betweenness_vals.min() + 1e-9)

nx.draw_networkx_edges(G, pos, alpha=0.2, width=0.5, edge_color='gray', ax=ax)
nodes = nx.draw_networkx_nodes(G, pos, node_size=size_nodes, node_color=weighted_degree_vals,
                               cmap='YlOrRd', alpha=0.8, ax=ax)

top_10_nodes = df_metrics.nlargest(10, 'betweenness')['estacion'].tolist()
labels = {n: n if n in top_10_nodes else '' for n in G.nodes()}
nx.draw_networkx_labels(G, pos, labels, font_size=6, ax=ax)

ax.set_title('Red del Metro CDMX: Topología Geográfica\n(Tamaño = Betweenness, Color = Grado Ponderado)', fontsize=14, fontweight='bold')
ax.set_xlabel('Longitud', fontsize=11)
ax.set_ylabel('Latitud', fontsize=11)
cbar = plt.colorbar(nodes, ax=ax, label='Grado Ponderado')
ax.axis('off')
plt.tight_layout()
plt.savefig('resultados/red_metro_geografica.png', dpi=300, bbox_inches='tight')
print("✓ Guardado: red_metro_geografica.png")
plt.close()

# 2. Distribución de grado
print("Creando visualización 2: Distribución de Grado...")
fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
grados_count = pd.Series(grados).value_counts().sort_index()
ax.loglog(grados_count.index, grados_count.values, 'o-', linewidth=2, markersize=8, color='darkblue')
ax.set_xlabel('Grado (log)', fontsize=12)
ax.set_ylabel('Frecuencia (log)', fontsize=12)
ax.set_title('Distribución de Grado - Red del Metro CDMX', fontsize=14, fontweight='bold')
ax.grid(True, which='both', alpha=0.3)
plt.tight_layout()
plt.savefig('resultados/distribucion_grado.png', dpi=300, bbox_inches='tight')
print("✓ Guardado: distribucion_grado.png")
plt.close()

# 3. Top 10 estaciones
print("Creando visualización 3: Top 10 Estaciones...")
top_10 = df_metrics.nlargest(10, 'betweenness')[['estacion', 'betweenness']]
fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
ax.barh(range(len(top_10)), top_10['betweenness'].values, color='steelblue')
ax.set_yticks(range(len(top_10)))
ax.set_yticklabels(top_10['estacion'].values, fontsize=10)
ax.set_xlabel('Centralidad de Intermediación (Betweenness)', fontsize=12)
ax.set_title('Top 10 Estaciones del Metro por Centralidad de Intermediación', fontsize=14, fontweight='bold')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('resultados/top10_estaciones.png', dpi=300, bbox_inches='tight')
print("✓ Guardado: top10_estaciones.png")
plt.close()

# ==================== PASO 4: SIMULACIÓN SIR REAL ====================
print("\n" + "=" * 80)
print("PASO 4: SIMULACIÓN SIR EN RED REAL")
print("=" * 80)

def simulate_sir(graph, initial_nodes, beta=0.3, gamma=0.1, max_time=200):
    """Simular modelo SIR en un grafo"""
    n = graph.number_of_nodes()
    state = np.zeros(n, dtype=int)
    node_list = list(graph.nodes())
    node_to_idx = {node: i for i, node in enumerate(node_list)}
    
    for node in initial_nodes:
        state[node_to_idx[node]] = 1
    
    susceptible = [np.sum(state == 0)]
    infected = [np.sum(state == 1)]
    recovered = [np.sum(state == 2)]
    
    for t in range(max_time):
        new_state = state.copy()
        for node in graph.nodes():
            i = node_to_idx[node]
            if state[i] == 1:
                for neighbor in graph.neighbors(node):
                    j = node_to_idx[neighbor]
                    if state[j] == 0 and np.random.random() < beta:
                        new_state[j] = 1
            if state[i] == 1 and np.random.random() < gamma:
                new_state[i] = 2
        
        state = new_state
        susceptible.append(np.sum(state == 0))
        infected.append(np.sum(state == 1))
        recovered.append(np.sum(state == 2))
        
        if infected[-1] == 0:
            break
    
    return {
        'susceptible': susceptible,
        'infected': infected,
        'recovered': recovered,
        'peak_infected': max(infected),
        'peak_infected_pct': max(infected) / n * 100,
        'time_to_peak': infected.index(max(infected))
    }

print("Modelo SIR implementado (β=0.3, γ=0.1)")

top_3_betweenness = df_metrics.nlargest(3, 'betweenness')['estacion'].tolist()
print(f"\nTop 3 estaciones por betweenness:")
for i, estacion in enumerate(top_3_betweenness, 1):
    print(f"  {i}. {estacion}")

print("\nEjecutando 5 simulaciones desde top-3 nodos...")
results_high_betweenness = []
for sim in range(5):
    np.random.seed(42 + sim)
    random.seed(42 + sim)
    result = simulate_sir(G, top_3_betweenness, beta=0.3, gamma=0.1, max_time=200)
    results_high_betweenness.append(result)
    print(f"  Sim {sim+1}: Peak={result['peak_infected_pct']:.1f}%, Time={result['time_to_peak']}")

print("\nEjecutando 5 simulaciones desde nodos aleatorios...")
random_nodes_list = [random.sample(list(G.nodes()), 3) for _ in range(5)]
results_random = []
for sim in range(5):
    np.random.seed(42 + 5 + sim)
    random.seed(42 + 5 + sim)
    result = simulate_sir(G, random_nodes_list[sim], beta=0.3, gamma=0.1, max_time=200)
    results_random.append(result)
    print(f"  Sim {sim+1}: Peak={result['peak_infected_pct']:.1f}%, Time={result['time_to_peak']}")

print("\nCreando visualización SIR...")
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

for i, result in enumerate(results_high_betweenness):
    tiempo = range(len(result['infected']))
    infected_pct = np.array(result['infected']) / G.number_of_nodes() * 100
    ax.plot(tiempo, infected_pct, linewidth=2, alpha=0.7, label=f'High Betweenness Sim {i+1}', linestyle='-')

for i, result in enumerate(results_random):
    tiempo = range(len(result['infected']))
    infected_pct = np.array(result['infected']) / G.number_of_nodes() * 100
    ax.plot(tiempo, infected_pct, linewidth=2, alpha=0.7, label=f'Random Sim {i+1}', linestyle='--')

ax.set_xlabel('Tiempo (días)', fontsize=12)
ax.set_ylabel('Infectados (%)', fontsize=12)
ax.set_title('Simulación SIR en Red Real del Metro CDMX\n(β=0.3, γ=0.1)', fontsize=14, fontweight='bold')
ax.legend(fontsize=8, loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('resultados/simulacion_SIR_real.png', dpi=300, bbox_inches='tight')
print("✓ Guardado: simulacion_SIR_real.png")
plt.close()

# ==================== PASO 5: REDES SINTÉTICAS ====================
print("\n" + "=" * 80)
print("PASO 5: COMPARACIÓN CON REDES SINTÉTICAS")
print("=" * 80)

n_nodes = G.number_of_nodes()
n_edges = G.number_of_edges()
avg_degree = 2 * n_edges / n_nodes

print(f"Parámetros de la red real: {n_nodes} nodos, {n_edges} aristas, grado promedio: {avg_degree:.2f}")

p = 2 * n_edges / (n_nodes * (n_nodes - 1))
G_er = nx.erdos_renyi_graph(n_nodes, p, seed=42)
print(f"✓ Erdős-Rényi: {G_er.number_of_nodes()} nodos, {G_er.number_of_edges()} aristas")

k = int(avg_degree)
G_ws = nx.watts_strogatz_graph(n_nodes, k, p=0.1, seed=42)
print(f"✓ Watts-Strogatz: {G_ws.number_of_nodes()} nodos, {G_ws.number_of_edges()} aristas")

G_ba = nx.barabasi_albert_graph(n_nodes, 2, seed=42)
print(f"✓ Barabási-Albert: {G_ba.number_of_nodes()} nodos, {G_ba.number_of_edges()} aristas")

def run_sir_simulations(graph, n_sims=5, initial_size=3):
    results = []
    for sim in range(n_sims):
        np.random.seed(42 + sim)
        random.seed(42 + sim)
        initial = random.sample(list(graph.nodes()), min(initial_size, graph.number_of_nodes()))
        result = simulate_sir(graph, initial, beta=0.3, gamma=0.1, max_time=200)
        results.append(result)
    return results

print("\nEjecutando simulaciones SIR en redes sintéticas...")
results_er = run_sir_simulations(G_er, n_sims=5)
print(f"  Erdős-Rényi - Peak promedio: {np.mean([r['peak_infected_pct'] for r in results_er]):.1f}%")

results_ws = run_sir_simulations(G_ws, n_sims=5)
print(f"  Watts-Strogatz - Peak promedio: {np.mean([r['peak_infected_pct'] for r in results_ws]):.1f}%")

results_ba = run_sir_simulations(G_ba, n_sims=5)
print(f"  Barabási-Albert - Peak promedio: {np.mean([r['peak_infected_pct'] for r in results_ba]):.1f}%")

peaks_real = [r['peak_infected_pct'] for r in results_high_betweenness + results_random]
peaks_er = [r['peak_infected_pct'] for r in results_er]
peaks_ws = [r['peak_infected_pct'] for r in results_ws]
peaks_ba = [r['peak_infected_pct'] for r in results_ba]

print(f"\nComparación de picos de infección:")
print(f"  Real: {np.mean(peaks_real):.1f}% ± {np.std(peaks_real):.1f}%")
print(f"  ER: {np.mean(peaks_er):.1f}% ± {np.std(peaks_er):.1f}%")
print(f"  WS: {np.mean(peaks_ws):.1f}% ± {np.std(peaks_ws):.1f}%")
print(f"  BA: {np.mean(peaks_ba):.1f}% ± {np.std(peaks_ba):.1f}%")

print(f"\nTests Mann-Whitney U (Real vs Sintéticas):")
u_er, p_er = stats.mannwhitneyu(peaks_real, peaks_er)
u_ws, p_ws = stats.mannwhitneyu(peaks_real, peaks_ws)
u_ba, p_ba = stats.mannwhitneyu(peaks_real, peaks_ba)
print(f"  Real vs ER: U={u_er:.1f}, p={p_er:.4f}")
print(f"  Real vs WS: U={u_ws:.1f}, p={p_ws:.4f}")
print(f"  Real vs BA: U={u_ba:.1f}, p={p_ba:.4f}")

print("\nCreando visualización de comparación...")
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

for i, result in enumerate(results_high_betweenness):
    tiempo = range(len(result['infected']))
    infected_pct = np.array(result['infected']) / G.number_of_nodes() * 100
    ax.plot(tiempo, infected_pct, linewidth=1.5, alpha=0.6, color='red', linestyle='-')

for i, result in enumerate(results_er):
    tiempo = range(len(result['infected']))
    infected_pct = np.array(result['infected']) / G_er.number_of_nodes() * 100
    ax.plot(tiempo, infected_pct, linewidth=1.5, alpha=0.6, color='blue', linestyle='--')

for i, result in enumerate(results_ws):
    tiempo = range(len(result['infected']))
    infected_pct = np.array(result['infected']) / G_ws.number_of_nodes() * 100
    ax.plot(tiempo, infected_pct, linewidth=1.5, alpha=0.6, color='green', linestyle=':')

for i, result in enumerate(results_ba):
    tiempo = range(len(result['infected']))
    infected_pct = np.array(result['infected']) / G_ba.number_of_nodes() * 100
    ax.plot(tiempo, infected_pct, linewidth=1.5, alpha=0.6, color='orange', linestyle='-.')

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='red', lw=2, linestyle='-', label='Red Real'),
    Line2D([0], [0], color='blue', lw=2, linestyle='--', label='Erdős-Rényi'),
    Line2D([0], [0], color='green', lw=2, linestyle=':', label='Watts-Strogatz'),
    Line2D([0], [0], color='orange', lw=2, linestyle='-.', label='Barabási-Albert')
]
ax.legend(handles=legend_elements, fontsize=11, loc='best')

ax.set_xlabel('Tiempo (días)', fontsize=12)
ax.set_ylabel('Infectados (%)', fontsize=12)
ax.set_title('Comparación SIR: Red Real vs Redes Sintéticas\n(β=0.3, γ=0.1)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('resultados/comparacion_SIR.png', dpi=300, bbox_inches='tight')
print("✓ Guardado: comparacion_SIR.png")
plt.close()

# ==================== PASO 6: MACHINE LEARNING ====================
print("\n" + "=" * 80)
print("PASO 6: VALIDACIÓN CON MACHINE LEARNING")
print("=" * 80)

alcaldias_bounds = {
    'Cuauhtémoc': {'lat_min': 19.390, 'lat_max': 19.435, 'lng_min': -99.150, 'lng_max': -99.120},
    'Miguel Hidalgo': {'lat_min': 19.400, 'lat_max': 19.490, 'lng_min': -99.230, 'lng_max': -99.140},
    'Venustiano Carranza': {'lat_min': 19.390, 'lat_max': 19.470, 'lng_min': -99.100, 'lng_max': -99.000},
    'Benito Juárez': {'lat_min': 19.330, 'lat_max': 19.420, 'lng_min': -99.200, 'lng_max': -99.130},
    'Coyoacán': {'lat_min': 19.300, 'lat_max': 19.380, 'lng_min': -99.250, 'lng_max': -99.140},
    'Iztapalapa': {'lat_min': 19.290, 'lat_max': 19.420, 'lng_min': -99.100, 'lng_max': -98.950},
    'Gustavo A. Madero': {'lat_min': 19.460, 'lat_max': 19.570, 'lng_min': -99.150, 'lng_max': -99.020},
    'Álvaro Obregón': {'lat_min': 19.300, 'lat_max': 19.450, 'lng_min': -99.350, 'lng_max': -99.200},
    'Iztacalco': {'lat_min': 19.370, 'lat_max': 19.430, 'lng_min': -99.100, 'lng_max': -99.020},
    'Tláhuac': {'lat_min': 19.240, 'lat_max': 19.360, 'lng_min': -99.100, 'lng_max': -98.950},
    'Tlalpan': {'lat_min': 19.200, 'lat_max': 19.330, 'lng_min': -99.250, 'lng_max': -99.050},
    'Xochimilco': {'lat_min': 19.250, 'lat_max': 19.330, 'lng_min': -99.200, 'lng_max': -99.030},
    'Azcapotzalco': {'lat_min': 19.450, 'lat_max': 19.570, 'lng_min': -99.350, 'lng_max': -99.200},
    'La Magdalena Contreras': {'lat_min': 19.250, 'lat_max': 19.380, 'lng_min': -99.350, 'lng_max': -99.240},
    'Milpa Alta': {'lat_min': 19.150, 'lat_max': 19.300, 'lng_min': -99.150, 'lng_max': -99.000},
}

estacion_alcaldia = {}
for _, row in df_metrics.iterrows():
    estacion = row['estacion']
    lat, lng = row['lat'], row['lng']
    
    alcaldia = None
    for alc, bounds in alcaldias_bounds.items():
        if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
            bounds['lng_min'] <= lng <= bounds['lng_max']):
            alcaldia = alc
            break
    
    estacion_alcaldia[estacion] = alcaldia if alcaldia else 'Otra'

print(f"Estaciones mapeadas a alcaldías: {len(estacion_alcaldia)}")
df_metrics['alcaldia'] = df_metrics['estacion'].map(estacion_alcaldia)

df_alcaldia_metrics = []
for alcaldia in df_metrics['alcaldia'].unique():
    if pd.isna(alcaldia):
        continue
    
    subset = df_metrics[df_metrics['alcaldia'] == alcaldia]
    metrics = {
        'alcaldia': alcaldia,
        'mean_betweenness': subset['betweenness'].mean(),
        'mean_grado': subset['grado'].mean(),
        'mean_clustering': subset['clustering'].mean(),
        'total_grado_ponderado': subset['grado_ponderado'].sum(),
        'n_estaciones': len(subset)
    }
    df_alcaldia_metrics.append(metrics)

df_alcaldia_metrics = pd.DataFrame(df_alcaldia_metrics)
print(f"✓ Métricas por alcaldía: {len(df_alcaldia_metrics)}")

municipio_map = {
    1: 'Cuauhtémoc', 2: 'Miguel Hidalgo', 3: 'Venustiano Carranza',
    4: 'Benito Juárez', 5: 'Coyoacán', 6: 'Iztapalapa', 7: 'Gustavo A. Madero',
    8: 'Álvaro Obregón', 9: 'Iztacalco', 10: 'La Magdalena Contreras',
    11: 'Milpa Alta', 12: 'Tláhuac', 13: 'Tlalpan', 14: 'Xochimilco',
    15: 'Azcapotzalco', 16: 'Coyoacán'
}

df_covid['MUNICIPIO_RES'] = df_covid['MUNICIPIO_RES'].astype(int)
df_covid['alcaldia'] = df_covid['MUNICIPIO_RES'].map(municipio_map)
df_covid['FECHA_INGRESO'] = pd.to_datetime(df_covid['FECHA_INGRESO'])

covid_alcaldia = df_covid.groupby('alcaldia').size().reset_index(name='total_casos')
print(f"✓ Casos COVID por alcaldía: {len(covid_alcaldia)}")

df_ml = pd.merge(df_alcaldia_metrics, covid_alcaldia, on='alcaldia', how='inner')
print(f"✓ Datos merged para ML: {len(df_ml)} alcaldías")

X = df_ml[['mean_betweenness', 'mean_grado', 'mean_clustering', 'total_grado_ponderado']].values
y = df_ml['total_casos'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("\nEntrenando Random Forest con Leave-One-Out CV...")
rf = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42, n_jobs=-1)
loo = LeaveOneOut()

y_pred = np.zeros(len(y))
for train_idx, test_idx in loo.split(X_scaled):
    X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    rf.fit(X_train, y_train)
    y_pred[test_idx] = rf.predict(X_test)

r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(np.mean((y - y_pred) ** 2))

print(f"✓ Resultados Random Forest (LOO-CV):")
print(f"  R²: {r2:.4f}")
print(f"  MAE: {mae:.2f} casos")
print(f"  RMSE: {rmse:.2f} casos")

rf.fit(X_scaled, y)
feature_names = ['Mean Betweenness', 'Mean Degree', 'Mean Clustering', 'Total Weighted Degree']
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]

print(f"\nImportancia de features:")
for i in indices:
    print(f"  {feature_names[i]}: {importances[i]:.4f}")

with open('resultados/modelo_rf.pkl', 'wb') as f:
    pickle.dump((rf, scaler), f)

# Visualizaciones ML
print("\nCreando visualizaciones de ML...")

fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
colors = plt.cm.viridis(np.linspace(0, 1, len(indices)))
y_pos = np.arange(len(indices))
ax.barh(y_pos, importances[indices], color=colors)
ax.set_yticks(y_pos)
ax.set_yticklabels([feature_names[i] for i in indices], fontsize=11)
ax.set_xlabel('Importancia Relativa', fontsize=12)
ax.set_title('Importancia de Features - Random Forest\n(LOO-CV, predicción de casos COVID)', fontsize=14, fontweight='bold')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('resultados/feature_importances.png', dpi=300, bbox_inches='tight')
print("✓ Guardado: feature_importances.png")
plt.close()

fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
ax.scatter(y, y_pred, s=100, alpha=0.7, edgecolors='black', linewidth=1.5)

min_val = min(y.min(), y_pred.min())
max_val = max(y.max(), y_pred.max())
ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Predicción perfecta')

for i, alcaldia in enumerate(df_ml['alcaldia']):
    ax.annotate(alcaldia, (y[i], y_pred[i]), fontsize=8, alpha=0.7, 
                xytext=(5, 5), textcoords='offset points')

ax.set_xlabel('Casos Reales', fontsize=12)
ax.set_ylabel('Casos Predichos', fontsize=12)
ax.set_title(f'Predicciones vs Valores Reales (R²={r2:.4f}, MAE={mae:.0f})', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('resultados/predicho_vs_real.png', dpi=300, bbox_inches='tight')
print("✓ Guardado: predicho_vs_real.png")
plt.close()

# ==================== PASO 7: EXPORTACIÓN ====================
print("\n" + "=" * 80)
print("PASO 7: EXPORTACIÓN DE RESULTADOS")
print("=" * 80)

df_metrics.to_csv('resultados/node_metrics.csv', index=False)
df_alcaldia_metrics.to_csv('resultados/alcaldia_metrics.csv', index=False)
df_ml.to_csv('resultados/ml_data.csv', index=False)
print("✓ CSV guardados")

resumen_metricas = {
    "proyecto": "Análisis de Redes Sociales: Metro CDMX y COVID-19",
    "fecha_generacion": datetime.now().isoformat(),
    "metricas_globales": {
        "nodos_estaciones": G.number_of_nodes(),
        "aristas_conexiones": G.number_of_edges(),
        "densidad": round(nx.density(G), 4),
        "diametro": int(diametro),
        "longitud_promedio_camino": round(float(promedio_camino), 4),
        "coeficiente_clustering_global": round(clustering_global, 4),
        "grado_promedio": round(grado_promedio, 4)
    },
    "distribucion_grado": {
        "minimo": int(min(grados)),
        "maximo": int(max(grados)),
        "media": round(float(np.mean(grados)), 4),
        "mediana": round(float(np.median(grados)), 4),
        "desv_est": round(float(np.std(grados)), 4)
    },
    "top_10_estaciones": df_metrics.nlargest(10, 'betweenness')[['estacion', 'betweenness', 'grado_ponderado']].to_dict('records'),
    "simulaciones_sir": {
        "red_real": {
            "peak_infectados_promedio_pct": round(np.mean(peaks_real), 2),
            "peak_infectados_std": round(np.std(peaks_real), 2),
            "desde_high_betweenness_peak": [round(r['peak_infected_pct'], 2) for r in results_high_betweenness],
            "desde_random_peak": [round(r['peak_infected_pct'], 2) for r in results_random]
        },
        "erdos_renyi": {
            "peak_infectados_promedio_pct": round(np.mean(peaks_er), 2),
            "peak_infectados_std": round(np.std(peaks_er), 2)
        },
        "watts_strogatz": {
            "peak_infectados_promedio_pct": round(np.mean(peaks_ws), 2),
            "peak_infectados_std": round(np.std(peaks_ws), 2)
        },
        "barabasi_albert": {
            "peak_infectados_promedio_pct": round(np.mean(peaks_ba), 2),
            "peak_infectados_std": round(np.std(peaks_ba), 2)
        },
        "tests_mann_whitney": {
            "real_vs_erdos_renyi": {"U": round(float(u_er), 2), "p_value": round(float(p_er), 4)},
            "real_vs_watts_strogatz": {"U": round(float(u_ws), 2), "p_value": round(float(p_ws), 4)},
            "real_vs_barabasi_albert": {"U": round(float(u_ba), 2), "p_value": round(float(p_ba), 4)}
        }
    },
    "machine_learning": {
        "modelo": "Random Forest",
        "validacion_cruzada": "Leave-One-Out (LOO)",
        "features": feature_names,
        "r2_score": round(r2, 4),
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "feature_importances": {name: round(float(imp), 4) for name, imp in zip(feature_names, importances)},
        "n_alcaldias": len(df_ml),
        "casos_covid_total": int(y.sum())
    },
    "datos_procesados": {
        "estaciones_unicas": int(df_metro['estacion'].nunique()),
        "lineas_metro": int(df_metro['linea'].nunique()),
        "casos_covid_cdmx_2020_2021": int(len(df_covid)),
        "alcaldias_procesadas": len(df_alcaldia_metrics)
    }
}

with open('resultados/resumen_metricas.json', 'w', encoding='utf-8') as f:
    json.dump(resumen_metricas, f, ensure_ascii=False, indent=2)
print("✓ resumen_metricas.json guardado")

archivos = glob.glob('resultados/*')
print(f"\n✓ Archivos en resultados/ ({len(archivos)} archivos):")
for archivo in sorted(archivos):
    size = os.path.getsize(archivo)
    size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
    print(f"  - {os.path.basename(archivo)} ({size_str})")

print("\n" + "=" * 80)
print("PROYECTO COMPLETADO")
print("=" * 80)
print(f"Fin: {datetime.now().isoformat()}")
print("\n✓ Todos los análisis han sido completados exitosamente")
