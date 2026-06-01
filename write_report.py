from pathlib import Path
content = r'''\documentclass[10pt,twocolumn]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{microtype}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{geometry}
\usepackage[numbers,sort&compress]{natbib}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\geometry{top=2.0cm,bottom=2.0cm,left=1.8cm,right=1.8cm}
\titlespacing*{\section}{0pt}{*2}{*1}
\titlespacing*{\subsection}{0pt}{*1.5}{*0.8}
\setlength{\parskip}{0.4ex}
\setlength{\parindent}{0.8em}
\renewcommand{\abstractname}{Resumen}
\renewcommand{\figurename}{Figura}
\renewcommand{\tablename}{Tabla}
\title{Topología del Metro de la Ciudad de México y la Propagación de COVID-19: Un Análisis de Redes, Simulaciones SIR y Validación por Alcaldía}
\author{Proyecto de Análisis de Redes\\[1ex]}
\date{\today}
\begin{document}
\maketitle
\begin{abstract}
Este trabajo analiza la relación entre la topología de la red del Metro de la Ciudad de México y la propagación de COVID-19 durante 2020-2021. Se construyó un grafo de 162 estaciones y 684 conexiones, ponderado por afluencia promedio de pasajeros, y se estimaron métricas de grado, centralidad de intermediación, cercanía y clustering. Se realizaron simulaciones SIR sobre la red real y en tres redes sintéticas (Erdős--Rényi, Watts--Strogatz y Barabási--Albert). Además, se validó la capacidad explicativa de las métricas de red mediante un modelo Random Forest con validación cruzada Leave-One-Out sobre 10 alcaldías de la CDMX. El análisis revela propiedades pequeño-mundo en la red del Metro, picos de infección menores que en redes sintéticas aleatorias y una capacidad predictiva limitada cuando se usan sólo métricas de red agregadas.
\end{abstract}
\section{Introducción}
La red del Metro de la Ciudad de México conecta 162 estaciones y moviliza millones de usuarios al día. En un contexto epidémico, esta infraestructura funciona como un canal de transmisión potencial, donde la topología de la red puede modular la velocidad y la intensidad de la difusión de un patógeno. En este estudio se investiga si las métricas estructurales del Metro (como grado, betweenness y clustering) explican la propagación espacial de COVID-19 entre alcaldías.

La pandemia de COVID-19 ha motivado diversos estudios sobre movilidad y redes de transporte como factores de riesgo epidemiológico \citep{pastor2001epidemic, newman2003structure, barabasi1999emergence}. En particular, las propiedades pequeño-mundo y las conexiones de alta centralidad suelen asociarse con mayor facilidad de propagación. Sin embargo, la topología real de una red de metro, embebida en dimensiones geográficas y con restricciones lineales, puede diferir de redes aleatorias idealizadas.

Este trabajo propone un análisis integral que combina: (1) construcción de la red de Metro ponderada por afluencia de pasajeros, (2) cálculo de métricas de red, (3) simulaciones SIR en la red real y en redes sintéticas, y (4) validación predictiva mediante aprendizaje automático a nivel de alcaldía.
\section{Datos y métodos}
\subsection{Fuentes de datos}
Se trabajó con tres fuentes principales:
\begin{itemize}[nosep,leftmargin=*]
\item Afluencia del Metro (2020-2021): 142,545 registros diarios con fecha, línea, estación y afluencia.
\item Casos COVID-19 en la CDMX (2020-2021): 1,025,436 registros confirmados de casos positivos con alcaldía de residencia.
\item Coordenadas geográficas de estaciones: 162 estaciones con latitud y longitud.
\end{itemize}

\subsection{Construcción de la red}
La red se modeló como un grafo no dirigido $G=(V,E)$, donde cada estación es un nodo y cada conexión entre estaciones consecutivas en una misma línea es una arista. El peso de cada arista $(i,j)$ se definió como el promedio de afluencia de las estaciones $i$ y $j$ durante 2020, de modo que los caminos entre estaciones reflejan también el volumen de pasajeros.

Se obtuvieron 162 nodos y 684 aristas. La red es conectada y su componente principal abarca todas las estaciones consideradas.

\subsection{Métricas de red}
Para cada estación se calcularon:
\begin{itemize}[nosep,leftmargin=*]
\item grado $k_i$,\
\item grado ponderado $k_i^w$,\
\item centralidad de intermediación $C_B(i)$,\
\item centralidad de cercanía $C_C(i)$,\
\item coeficiente de clustering local $C_i$.
\end{itemize}
Además, se estimaron métricas globales: diámetro, longitud promedio del camino, coeficiente de clustering global y densidad.

\subsection{Simulaciones SIR}
Se implementó un modelo SIR discreto sobre los nodos de la red. En cada paso temporal, un nodo infectado puede contagiar a un vecino susceptible con probabilidad $\beta=0.3$, y puede recuperarse con probabilidad $\gamma=0.1$. Se realizaron 5 simulaciones iniciadas desde las tres estaciones con mayor betweenness y 5 simulaciones iniciadas desde tres estaciones seleccionadas aleatoriamente.

Para comparar, se generaron tres redes sintéticas con los mismos 162 nodos:
\begin{itemize}[nosep,leftmargin=*]
\item Erdős--Rényi: probabilidad $p$ ajustada a 684 aristas esperadas.
\item Watts--Strogatz: $k=4$, $p=0.1$.
\item Barabási--Albert: $m=2$.
\end{itemize}
En cada red sintética se ejecutaron 5 simulaciones SIR con los mismos parámetros.

\subsection{Validación por alcaldía}
Se asignaron estaciones a alcaldías mediante sus coordenadas geográficas. Se agregaron las métricas de red por alcaldía: betweenness promedio, grado promedio, clustering promedio y suma de grado ponderado. Estas características se usaron para predecir el total de casos COVID en 10 alcaldías mediante un Random Forest con validación cruzada Leave-One-Out.

\section{Resultados}
\subsection{Estructura de la red}
La Tabla~\ref{tab:global_metrics} resume las métricas globales de la red.
\begin{table}[t]
\centering
\caption{Métricas globales de la red del Metro de la CDMX.}
\label{tab:global_metrics}
\begin{tabular}{lc}
\toprule
Métrica & Valor \\
\midrule
Nodos & 162 \\
Aristas & 684 \\
Densidad & 0.0524 \\
Diámetro & 4 \\
Longitud promedio del camino & 2.2545 \\
Clustering global & 0.5783 \\
Grado promedio & 8.44 \\
\bottomrule
\end{tabular}
\end{table}

La red presenta características pequeño-mundo: distancia promedio corta, alta agrupación local y baja densidad. Este patrón indica que la red es suficientemente conectada para permitir rutas cortas, pero conserva una restricción geométrica por el trazado físico de las líneas.

\begin{figure*}[t]
\centering
\includegraphics[width=0.92\linewidth]{red_metro_geografica.png}
\caption{Red del Metro de la CDMX en coordenadas geográficas. El tamaño de nodo es proporcional a la centralidad de intermediación y el color refleja el grado ponderado.}
\label{fig:metro_geo}
\end{figure*}

\subsection{Estaciones de mayor importancia}
Las estaciones con mayor centralidad de intermediación fueron Santa Anita, Chabacano y Morelos. Estas estaciones actúan como puentes que conectan subredes y, por tanto, son nodos críticos para la propagación.

\begin{figure}[t]
\centering
\includegraphics[width=0.98\linewidth]{top10_estaciones.png}
\caption{Top 10 estaciones por centralidad de intermediación.}
\label{fig:top10}
\end{figure}

\subsection{Simulaciones SIR}
En la red real del Metro, el pico promedio de infección fue 47.84\%. Las redes sintéticas mostraron picos mucho mayores: 78.89\% para Erdős--Rényi, 74.32\% para Watts--Strogatz y 66.79\% para Barabási--Albert.

Los resultados sugieren que la red real del Metro, aunque pequeño-mundo, es menos susceptible a picos extremos que redes aleatorias con la misma densidad, probablemente debido a la geometría espacial y la estructura lineal de las conexiones.

\begin{figure*}[t]
\centering
\includegraphics[width=0.92\linewidth]{comparacion_SIR.png}
\caption{Comparación de trayectorias SIR entre la red real y tres redes sintéticas.}
\label{fig:sir_comparison}
\end{figure*}

\subsection{Validación de predicción por alcaldía}
El modelo Random Forest con validación Leave-One-Out obtuvo:
\begin{itemize}[nosep,leftmargin=*]
\item $R^{2} = -1.0641$,
\item MAE = 59,291 casos,
\item RMSE = 67,266 casos.
\end{itemize}

La capacidad predictiva es muy limitada, lo que indica que las métricas de red agregadas no capturan por sí solas la variación espacial de casos COVID entre alcaldías.

\begin{figure}[t]
\centering
\includegraphics[width=0.98\linewidth]{feature_importances.png}
\caption{Importancias de las características en el modelo Random Forest.}
\label{fig:feature_importances}
\end{figure}

Las importancias indican que el grado promedio es la característica más influyente (0.369), seguido por el clustering promedio (0.270), la suma de grado ponderado (0.203) y la betweenness promedio (0.159).

\begin{figure}[t]
\centering
\includegraphics[width=0.98\linewidth]{predicho_vs_real.png}
\caption{Casos predichos versus casos reales por alcaldía. La dispersión muestra el bajo ajuste del modelo.}
\label{fig:pred_real}
\end{figure}

\section{Discusión}
El análisis confirma que la red del Metro exhibe características de tipo pequeño-mundo. La alta agrupación local (0.5783) y la distancia promedio corta (2.25) explican por qué los procesos de contagio pueden propagarse con rapidez, pero también muestran que la red es más conservadora que redes sintéticas aleatorias.

La comparación SIR sugiere que la topología real del Metro reduce el pico de infección frente a redes Erdős--Rényi y Watts--Strogatz de igual tamaño y densidad. Esto se debe a que la red real está embebida en un espacio físico con líneas y terminales que limitan las rutas de transmisión, en contraste con las estructuras más densas y uniformes de las redes sintéticas.

Sin embargo, el fracaso del modelo Random Forest indica que las métricas de red no son suficientes para explicar totalmente la incidencia de COVID-19. Factores no incluidos en este estudio, como densidad demográfica, mitigación sanitaria, composición socioeconómica y comportamiento de los usuarios, probablemente tienen un peso mayor en la variación de casos entre alcaldías.

\subsection{Limitaciones}
Entre las principales limitaciones se encuentran:
\begin{itemize}[nosep,leftmargin=*]
\item Mapeo aproximado de estaciones a alcaldías basado en coordenadas, que puede introducir errores de asignación.
\item Agregación espacial estática que no incorpora la dinámica temporal de las olas de COVID-19.
\item Exclusión de variables socioeconómicas y de movilidad adicionales fuera del Metro.
\end{itemize}

\section{Conclusiones}
Se construyó un análisis estructural y epidemiológico de la red del Metro de la CDMX durante 2020-2021. La red presenta propiedades pequeño-mundo y picos de infección menores que los de redes sintéticas aleatorias. No obstante, la capacidad predictiva de las métricas de red agregadas es limitada, lo que sugiere que la incidencia de COVID-19 depende de múltiples factores más allá de la topología del transporte.

\section*{Referencias}
\bibliographystyle{plainnat}
\begin{thebibliography}{9}
\bibitem[Barabási \& Albert(1999)]{barabasi1999emergence}
A.-L. Barabási and R. Albert. 1999. Emergence of scaling in random networks. \textit{Science}, 286(5439):509--512.
\bibitem[Newman(2003)]{newman2003structure}
M. E. J. Newman. 2003. The structure and function of complex networks. \textit{SIAM Review}, 45(2):167--256.
\bibitem[Pastor-Satorras \& Vespignani(2001)]{pastor2001epidemic}
R. Pastor-Satorras and A. Vespignani. 2001. Epidemic spreading in scale-free networks. \textit{Physical Review Letters}, 86(14):3200--3203.
\bibitem[Watts \& Strogatz(1998)]{watts1998collective}
D. J. Watts and S. H. Strogatz. 1998. Collective dynamics of small-world networks. \textit{Nature}, 393(6684):440--442.
\bibitem[Cormack et al.(2009)]{Cormack2009ReciprocalRF}
G. V. Cormack, C. L. A. Clarke, and S. Buettcher. 2009. Reciprocal rank fusion outperforms condorcet and individual rank learning methods. \textit{SIGIR}, pages 758--759.
\end{thebibliography}
\end{document}
'''
Path('reporte/reporte_final.tex').write_text(content, encoding='utf-8')
print('[OK] reporte_final.tex actualizado')
