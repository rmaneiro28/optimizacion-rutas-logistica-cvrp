import pulp
import math

def calcular_distancia(p1, p2):
    """Calcula distancia euclidiana entre dos coordenadas (x,y)"""
    return math.sqrt((p1[0] - p2[0])*2 + (p1[1] - p2[1])*2)

print("--- SISTEMA DE OPTIMIZACIÓN LOGÍSTICA (VRP) ---")
print("Por favor, ingresa los datos de tu escenario.")
print("-" * 50)

# --- FASE 1: RECOLECCIÓN DE DATOS (INTERACTIVA) ---

# 1. Datos del Vehículo
capacidad_vehiculo = float(input("¿Cuál es la capacidad máxima de carga del vehículo (ej. 100)? "))
num_vehiculos = int(input("¿Cuántos vehículos tienes disponibles? "))

# 2. Datos del Almacén (Depósito)
print("\n--- Datos del Almacén Central (Nodo 0) ---")
deposito_x = float(input("Coordenada X del almacén: "))
deposito_y = float(input("Coordenada Y del almacén: "))
# El almacén es el nodo 0, demanda 0
nodos = {0: {'x': deposito_x, 'y': deposito_y, 'demanda': 0}}

# 3. Datos de los Clientes
num_clientes = int(input("\n¿Cuántos clientes hay que visitar? "))

for i in range(1, num_clientes + 1):
    print(f"\n--- Cliente {i} ---")
    cx = float(input(f"Coordenada X del Cliente {i}: "))
    cy = float(input(f"Coordenada Y del Cliente {i}: "))
    dem = float(input(f"Demanda del Cliente {i}: "))
    nodos[i] = {'x': cx, 'y': cy, 'demanda': dem}

# Lista de todos los clientes (sin el almacén) y lista de todos los nodos
clientes = [i for i in range(1, num_clientes + 1)]
todos_nodos = [0] + clientes

# Calcular Matriz de Distancias (Costos)
distancias = {}
for i in todos_nodos:
    for j in todos_nodos:
        if i != j:
            p1 = (nodos[i]['x'], nodos[i]['y'])
            p2 = (nodos[j]['x'], nodos[j]['y'])
            distancias[(i, j)] = calcular_distancia(p1, p2)

print("\n" + "="*50)
print("PROCESANDO MODELO MATEMÁTICO...")
print("="*50)

# --- FASE 2: MODELADO (PuLP) ---

# Crear el problema de minimización
prob = pulp.LpProblem("VRP_Optimización_Logística", pulp.LpMinimize)

# VARIABLES DE DECISIÓN
# x[i,j] = 1 si se viaja de i a j, 0 si no
x = pulp.LpVariable.dicts("ruta", distancias, cat='Binary')

# u[i] = variable auxiliar para evitar subtours (MTZ constraints)
# Representa el orden/carga acumulada al llegar al cliente i
u = pulp.LpVariable.dicts("u", clientes, lowBound=0, upBound=capacidad_vehiculo, cat='Continuous')

# FUNCIÓN OBJETIVO: Minimizar distancia total
prob += pulp.lpSum([distancias[(i, j)] * x[(i, j)] for (i, j) in distancias])

# RESTRICCIONES

# 1. Cada cliente debe ser visitado exactamente una vez (entrada y salida)
for j in clientes:
    prob += pulp.lpSum([x[(i, j)] for i in todos_nodos if i != j]) == 1 # Entrar
    prob += pulp.lpSum([x[(j, i)] for i in todos_nodos if i != j]) == 1 # Salir

# 2. Restricciones de flujo en el depósito (salen K vehículos, entran K vehículos)
# Nota: Esto fuerza a usar todos los vehículos o permitir vueltas vacías. 
# Para flexibilizar, usamos <= num_vehiculos
prob += pulp.lpSum([x[(0, j)] for j in clientes]) <= num_vehiculos
prob += pulp.lpSum([x[(j, 0)] for j in clientes]) <= num_vehiculos

# 3. Eliminación de Subtours y Capacidad (Fórmula MTZ)
for i in clientes:
    for j in clientes:
        if i != j:
            demanda_j = nodos[j]['demanda']
            # u_i - u_j + Capacidad * x_ij <= Capacidad - demanda_j
            prob += u[i] - u[j] + capacidad_vehiculo * x[(i, j)] <= capacidad_vehiculo - demanda_j

# Restricción adicional para vincular la carga inicial (base)
for i in clientes:
     prob += u[i] >= nodos[i]['demanda']
     prob += u[i] <= capacidad_vehiculo

# --- FASE 3: SOLUCIÓN ---

# Resolver
# Ocultamos el log del solver para que se vea limpio (msg=0)
prob.solve(pulp.PULP_CBC_CMD(msg=0)) 

# --- FASE 4: RESULTADOS ---

print(f"Estado de la solución: {pulp.LpStatus[prob.status]}")

if pulp.LpStatus[prob.status] == 'Optimal':
    print(f"Distancia Total Mínima: {pulp.value(prob.objective):.2f} unidades de distancia")
    print("\n--- RUTAS OPTIMIZADAS ---")
    
    # Algoritmo simple para reconstruir e imprimir las rutas ordenadas
    rutas_encontradas = []
    visitados = set()
    
    # Buscar arcos que salen del depósito (0)
    for j in clientes:
        if x[(0, j)].varValue is not None and x[(0, j)].varValue > 0.9:
            # Inicio de una ruta
            ruta_actual = [0, j]
            visitados.add(j)
            carga_actual = nodos[j]['demanda']
            
            nodo_actual = j
            while nodo_actual != 0:
                siguiente_encontrado = False
                for k in todos_nodos:
                    if k != nodo_actual and (nodo_actual, k) in x:
                        if x[(nodo_actual, k)].varValue is not None and x[(nodo_actual, k)].varValue > 0.9:
                            ruta_actual.append(k)
                            if k != 0:
                                visitados.add(k)
                                carga_actual += nodos[k]['demanda']
                            nodo_actual = k
                            siguiente_encontrado = True
                            break
                if not siguiente_encontrado:
                    break # Seguridad
            
            print(f"Vehículo: {' -> '.join(map(str, ruta_actual))} | Carga Total: {carga_actual}")
else:
    print("No se encontró una solución óptima (revisa si la capacidad de los vehículos es suficiente).")