import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import matplotlib.pyplot as plt

# ==========================================
# FASE 1: DEFINICIÓN DE DATOS (Escenario Ficticio)
# ==========================================

def crear_modelo_datos():
    """Almacena los datos del problema."""
    data = {}
    
    # Coordenadas [x, y]. El primer punto (índice 0) es el DEPÓSITO.
    # Los siguientes son los clientes.
    data['ubicaciones'] = [
        (20, 20), # Depósito (Índice 0)
        (10, 5),  (12, 8),  (2, 15), (6, 12), # Clientes 1-4
        (30, 10), (32, 14), (38, 5), (35, 18),# Clientes 5-8
        (15, 30), (10, 35), (22, 32), (5, 25),# Clientes 9-12
        (35, 30), (40, 25), (32, 38), (28, 35) # Clientes 13-16
    ]
    
    # Demanda de cada ubicación. El depósito (índice 0) tiene demanda 0.
    data['demandas'] = [
        0, # Depósito
        2, 3, 5, 2, # Demandas Clientes 1-4
        4, 2, 6, 3, # Demandas Clientes 5-8
        3, 4, 2, 5, # Demandas Clientes 9-12
        4, 3, 2, 1  # Demandas Clientes 13-16
    ]
    
    data['num_vehiculos'] = 4
    data['capacidad_vehiculo'] = 15
    data['deposito_inicio'] = 0  # Índice donde arrancan los camiones
    
    # Verificación rápida de factibilidad
    total_demanda = sum(data['demandas'])
    capacidad_total = data['num_vehiculos'] * data['capacidad_vehiculo']
    print(f"Demanda Total a entregar: {total_demanda} unidades")
    print(f"Capacidad Total de la flota: {capacidad_total} unidades")
    if total_demanda > capacidad_total:
        print("¡ALERTA! La demanda excede la capacidad total. No hay solución posible.")
        exit()
        
    return data

def calcular_distancia_euclidiana(coords1, coords2):
    """Función auxiliar para calcular distancia entre dos puntos (x,y)."""
    return math.sqrt((coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2)

def crear_matriz_distancias(ubicaciones):
    """Crea una matriz NxN con las distancias entre todos los puntos."""
    n = len(ubicaciones)
    matriz = {}
    for from_node in range(n):
        matriz[from_node] = {}
        for to_node in range(n):
            if from_node == to_node:
                matriz[from_node][to_node] = 0
            else:
                # Usamos distancia euclidiana simple para este ejemplo
                dist = calcular_distancia_euclidiana(ubicaciones[from_node], ubicaciones[to_node])
                # OR-Tools trabaja mejor con enteros, multiplicamos por 100 para mantener precisión
                matriz[from_node][to_node] = int(dist * 100) 
    return matriz

# ==========================================
# FASE 2 & 3: MODELADO Y SOLUCIÓN (OR-Tools)
# ==========================================

def resolver_cvrp():
    # 1. Instanciar los datos
    data = crear_modelo_datos()
    matriz_distancias = crear_matriz_distancias(data['ubicaciones'])

    # 2. Crear el gestor de índices de enrutamiento
    # (Convierte los nodos internos del solver a nuestros índices de clientes)
    manager = pywrapcp.RoutingIndexManager(len(data['ubicaciones']),
                                           data['num_vehiculos'], 
                                           data['deposito_inicio'])

    # 3. Crear el Modelo de Enrutamiento (El cerebro de la operación)
    routing = pywrapcp.RoutingModel(manager)

    # 4. Definir el callback de tránsito (¿Cuánto cuesta ir de A a B?)
    def distance_callback(from_index, to_index):
        # Devuelve la distancia entre dos nodos
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matriz_distancias[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # 5. Definir la Función Objetivo: Minimizar el costo total (distancia) del arco
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 6. Añadir Restricción de CAPACIDAD (El "C" de CVRP)
    def demand_callback(from_index):
        # Devuelve la demanda del nodo que se está visitando
        from_node = manager.IndexToNode(from_index)
        return data['demandas'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # capacidad nula (slack) - no permitimos excederla
        [data['capacidad_vehiculo']] * data['num_vehiculos'], # Capacidad de cada vehículo
        True, # Empezar la ruta con carga acumulada 0
        'Capacidad')

    # 7. Parámetros de Búsqueda (Configurar cómo el solver busca la solución)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    # Primera solución: Usar heurística "Path Cheapest Arc" (rápida pero no óptima)
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    # Búsqueda Local: Usar "Guided Local Search" para mejorar la solución inicial
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 10 # Límite de tiempo para buscar

    # 8. Resolver
    print("\nResolviendo... por favor espere.")
    solution = routing.SolveWithParameters(search_parameters)

    # 9. Resultados
    if solution:
        print("¡Solución encontrada!\n")
        imprimir_solucion_texto(data, manager, routing, solution)
        graficar_solucion(data, manager, routing, solution)
    else:
        print('No se encontró solución.')

# ==========================================
# FASE 4: PRESENTACIÓN DE RESULTADOS (Texto y Gráfico)
# ==========================================

def imprimir_solucion_texto(data, manager, routing, solution):
    """Muestra las rutas detalladas en la consola."""
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehiculos']):
        index = routing.Start(vehicle_id)
        plan_output = 'Ruta para el Vehículo {}:\n'.format(vehicle_id + 1)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demandas'][node_index]
            plan_output += ' {0} (Carga({1})) -> '.format(node_index, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        
        node_index = manager.IndexToNode(index)
        plan_output += ' {0} (Carga Final({1}))\n'.format(node_index, route_load)
        plan_output += 'Distancia de la ruta: {}m (aprox)\n'.format(route_distance)
        plan_output += 'Carga total del vehículo: {}/{}\n'.format(route_load, data['capacidad_vehiculo'])
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('-------------------------')
    print('Distancia Total de toda la flota: {}m (aprox)'.format(total_distance))
    print('Carga Total entregada: {} unidades'.format(total_load))
    print('-------------------------')


def graficar_solucion(data, manager, routing, solution):
    """
    Genera una ventana visual (Matplotlib) con el mapa de las rutas.
    """
    plt.figure(figsize=(10, 8))
    plt.title("Optimización de Rutas Logísticas (CVRP Result)", fontsize=16)

    # 1. Graficar los puntos (Nodos)
    coords = data['ubicaciones']
    
    # Graficar Depósito (Índice 0) en Rojo
    plt.scatter(coords[0][0], coords[0][1], c='red', marker='s', s=150, label='Depósito Central', zorder=5)
    
    # Graficar Clientes en Azul
    for i in range(1, len(coords)):
        plt.scatter(coords[i][0], coords[i][1], c='blue', marker='o', s=80, zorder=4)
        # Añadir etiqueta con ID de cliente y su demanda
        plt.annotate(f"C{i} [{data['demandas'][i]}]", (coords[i][0]+0.5, coords[i][1]+0.5))

    # 2. Graficar las Rutas (Líneas)
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k'] # Colores para distintos vehículos
    
    for vehicle_id in range(data['num_vehiculos']):
        index = routing.Start(vehicle_id)
        ruta_coords_x = []
        ruta_coords_y = []
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            ruta_coords_x.append(coords[node_index][0])
            ruta_coords_y.append(coords[node_index][1])
            index = solution.Value(routing.NextVar(index))
            
        # Añadir el punto final (regreso al depósito)
        node_index = manager.IndexToNode(index)
        ruta_coords_x.append(coords[node_index][0])
        ruta_coords_y.append(coords[node_index][1])
        
        # Dibujar la línea de la ruta
        color_vehiculo = colors[vehicle_id % len(colors)]
        plt.plot(ruta_coords_x, ruta_coords_y, 
                 color=color_vehiculo, 
                 linewidth=2, 
                 linestyle='-', 
                 label=f'Vehículo {vehicle_id + 1}',
                 alpha=0.7)
        
        # Añadir flechas para indicar dirección (opcional pero útil)
        for i in range(len(ruta_coords_x) - 1):
             plt.arrow(ruta_coords_x[i], ruta_coords_y[i], 
                       (ruta_coords_x[i+1]-ruta_coords_x[i])*0.5, # Flecha a mitad de camino
                       (ruta_coords_y[i+1]-ruta_coords_y[i])*0.5, 
                       shape='full', lw=0, length_includes_head=True, head_width=0.8, color=color_vehiculo)

    plt.grid(True, linestyle='--')
    plt.legend(loc='best')
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    
    print("Generando ventana visual con el mapa de rutas...")
    plt.show() # ESTO ABRE LA VENTANA VISUAL

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == '__main__':
    resolver_cvrp()