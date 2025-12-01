# Informe Técnico: Optimización de Rutas y Asignación de Recursos en Logística de Última Milla

**Estudiante:** Rúbel Maneiro  
**Asignatura:** Optimización de Sistemas de Información  
**Fecha:** Noviembre 2025

---

## 1. Fase 1: Análisis del Sistema Actual

### 1.1 Identificación del Proceso
El proceso analizado corresponde a la distribución de última milla de la empresa ficticia **"Logística Rápida S.A."**.
- **Entradas:** Pedidos de clientes con ubicación y ventana de tiempo, flota de vehículos disponible.
- **Recursos:** Un almacén central y una flota de 4 vehículos con capacidad de 100 unidades cada uno.
- **Salidas:** Rutas de entrega asignadas a cada vehículo.

### 1.2 Definición del Problema
La empresa enfrenta ineficiencias en sus rutas actuales, lo que resulta en distancias recorridas excesivas y riesgo de incumplimiento de ventanas de tiempo. El objetivo es minimizar la distancia total recorrida garantizando el servicio a todos los clientes dentro de sus horarios preferidos.

### 1.3 Datos del Escenario
Se generaron datos sintéticos para 20 clientes y 1 almacén:
- **Ubicaciones:** Coordenadas (X, Y) en un rango de +/- 50km.
- **Demandas:** Entre 5 y 20 unidades por cliente.
- **Ventanas de Tiempo:** Horarios de apertura y cierre específicos.

---

## 2. Fase 2: Modelado de Optimización

El problema se modeló como un **VRPTW (Vehicle Routing Problem with Time Windows)**.

### 2.1 Variables de Decisión
- $x_{ijk}$: Variable binaria (1 si el vehículo $k$ viaja de $i$ a $j$, 0 si no).
- $t_{ik}$: Tiempo de llegada del vehículo $k$ al cliente $i$.

### 2.2 Función Objetivo
Minimizar la distancia total:
$$ \text{Min } Z = \sum_{k \in K} \sum_{i \in V} \sum_{j \in V} d_{ij} x_{ijk} $$

### 2.3 Restricciones Principales
1.  **Flujo:** Cada cliente es visitado una sola vez.
2.  **Capacidad:** La carga total no excede la capacidad del vehículo ($Q=100$).
3.  **Tiempo:** El servicio inicia dentro de la ventana $[a_i, b_i]$.

*(Ver documento `docs/Modelo_Matematico.md` para la formulación completa)*

---

## 3. Fase 3: Implementación y Resultados

### 3.1 Herramienta Utilizada
Se utilizó **Python** con la librería **Google OR-Tools**, empleando el solver de enrutamiento (`pywrapcp`).

### 3.2 Resultados del Escenario Base
- **Vehículos utilizados:** 4
- **Capacidad:** 100 unidades
- **Distancia Total Optimizada:** **579.84 km**
- **Cumplimiento:** 100% de entregas y ventanas de tiempo.

### 3.3 Análisis de Sensibilidad

Se evaluaron dos escenarios adicionales para medir el impacto de los recursos:

| Escenario | Descripción | Distancia Total | Cambio % | Observación |
|---|---|---|---|---|
| **Base** | 4 Vehículos, Cap. 100 | **579.84 km** | - | Solución óptima base. |
| **Flota Reducida** | 3 Vehículos, Cap. 100 | **Infactible** | N/A | No es posible cumplir con todas las restricciones (tiempo/capacidad) con menos vehículos. |
| **Mayor Capacidad** | 4 Vehículos, Cap. 150 | **552.72 km** | **-4.68%** | Aumentar la capacidad permite rutas más eficientes (menos retornos al depósito). |

---

## 4. Conclusiones

1.  **Optimización Lograda:** El modelo matemático permitió generar rutas eficientes que cumplen con todas las complejas restricciones de ventanas de tiempo, algo difícil de lograr manualmente.
2.  **Impacto de la Flota:** El análisis de sensibilidad reveló que la flota actual de 4 vehículos es **crítica**; reducirla a 3 hace imposible la operación bajo las condiciones actuales.
3.  **Mejora Potencial:** Aumentar la capacidad de los vehículos en un 50% (de 100 a 150) permitiría reducir la distancia recorrida en casi un **5%**, lo que sugiere que invertir en vehículos más grandes podría traer ahorros operativos en combustible y mantenimiento a largo plazo.

---
**Archivos Entregables:**
- `src/generar_datos.py`: Generador de instancias.
- `src/optimize.py`: Solver principal.
- `src/analisis_sensibilidad.py`: Script de comparación de escenarios.
- `data/`: Archivos CSV con los datos utilizados.
