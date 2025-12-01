# Modelo Matemático: Problema de Enrutamiento de Vehículos con Ventanas de Tiempo (VRPTW)

## 1. Definición del Problema
El objetivo es determinar un conjunto de rutas para una flota de vehículos que inician y terminan en un depósito central, para satisfacer la demanda de un conjunto de clientes, respetando las restricciones de capacidad y ventanas de tiempo, minimizando la distancia total recorrida.

## 2. Conjuntos e Índices
- $V = \{0, 1, ..., N\}$: Conjunto de nodos, donde $0$ es el depósito y $1, ..., N$ son los clientes.
- $K$: Conjunto de vehículos disponibles.
- $i, j \in V$: Índices para los nodos (origen y destino).
- $k \in K$: Índice para el vehículo.

## 3. Parámetros
- $d_{ij}$: Distancia (o costo) de viajar del nodo $i$ al nodo $j$.
- $q_i$: Demanda del cliente $i$ ($q_0 = 0$).
- $Q$: Capacidad máxima de cada vehículo.
- $[a_i, b_i]$: Ventana de tiempo para el cliente $i$ (tiempo más temprano de inicio, tiempo más tardío de inicio).
- $s_i$: Tiempo de servicio (descarga) en el cliente $i$.

## 4. Variables de Decisión
- $x_{ijk} \in \{0, 1\}$: Variable binaria que vale 1 si el vehículo $k$ viaja del nodo $i$ al nodo $j$, 0 en caso contrario.
- $t_{ik} \ge 0$: Variable continua que indica el tiempo de llegada del vehículo $k$ al nodo $i$.

## 5. Función Objetivo
Minimizar la distancia total recorrida:
$$ \text{Min } Z = \sum_{k \in K} \sum_{i \in V} \sum_{j \in V} d_{ij} x_{ijk} $$

## 6. Restricciones

### 6.1 Flujo de Vehículos
Cada cliente es visitado exactamente una vez por un solo vehículo:
$$ \sum_{k \in K} \sum_{j \in V, j \neq i} x_{ijk} = 1 \quad \forall i \in V \setminus \{0\} $$

Conservación de flujo (si un vehículo entra a un nodo, debe salir):
$$ \sum_{i \in V, i \neq h} x_{ihk} - \sum_{j \in V, j \neq h} x_{hjk} = 0 \quad \forall h \in V \setminus \{0\}, \forall k \in K $$

Cada vehículo sale del depósito y regresa al depósito (a lo sumo una vez):
$$ \sum_{j \in V \setminus \{0\}} x_{0jk} = 1 \quad \forall k \in K $$
$$ \sum_{i \in V \setminus \{0\}} x_{i0k} = 1 \quad \forall k \in K $$

### 6.2 Capacidad
La suma de las demandas en una ruta no debe exceder la capacidad del vehículo:
$$ \sum_{i \in V \setminus \{0\}} q_i \sum_{j \in V, j \neq i} x_{ijk} \le Q \quad \forall k \in K $$

### 6.3 Ventanas de Tiempo y Secuencia
Si el vehículo $k$ viaja de $i$ a $j$, el tiempo de llegada a $j$ debe ser consistente:
$$ x_{ijk} (t_{ik} + s_i + t_{ij} - t_{jk}) \le 0 \quad \forall i, j \in V, \forall k \in K $$
(Nota: Esta se linealiza usualmente con "Big M")

El servicio debe comenzar dentro de la ventana de tiempo:
$$ a_i \le t_{ik} \le b_i \quad \forall i \in V, \forall k \in K $$

## 7. Naturaleza de las Variables
$$ x_{ijk} \in \{0, 1\} $$
$$ t_{ik} \ge 0 $$
