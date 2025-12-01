import pandas as pd
import numpy as np
import os
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model():
    """Almacena los datos para el problema."""
    data = {}
    
    # Cargar datos
    df_clientes = pd.read_csv(os.path.join('data', 'clientes.csv'))
    df_vehiculos = pd.read_csv(os.path.join('data', 'vehiculos.csv'))
    
    # Coordenadas
    # El nodo 0 es el depósito (primera fila del CSV si se generó correctamente)
    # Aseguramos que el depósito sea el índice 0 en la lista de ubicaciones
    locations = list(zip(df_clientes['x'], df_clientes['y']))
    data['locations'] = locations
    
    # Matriz de distancias (Euclidiana)
    num_locations = len(locations)
    dist_matrix = {}
    for from_node in range(num_locations):
        dist_matrix[from_node] = {}
        for to_node in range(num_locations):
            if from_node == to_node:
                dist_matrix[from_node][to_node] = 0
            else:
                x1, y1 = locations[from_node]
                x2, y2 = locations[to_node]
                dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                dist_matrix[from_node][to_node] = int(dist * 100) # OR-Tools trabaja con enteros
    
    data['distance_matrix'] = dist_matrix
    
    # Ventanas de tiempo
    # Convertir a una lista de tuplas (inicio, fin)
    data['time_windows'] = list(zip(df_clientes['ventana_inicio'], df_clientes['ventana_fin']))
    
    # Demandas
    data['demands'] = df_clientes['demanda'].tolist()
    
    # Vehículos
    data['num_vehicles'] = len(df_vehiculos)
    data['vehicle_capacities'] = df_vehiculos['capacidad'].tolist()
    
    # Depósito
    data['depot'] = 0
    
    # Tiempos de servicio
    data['service_time'] = df_clientes['tiempo_servicio'].tolist()
    
    return data

def print_solution(data, manager, routing, solution):
    """Imprime la solución en consola."""
    print(f'Objetivo: {solution.ObjectiveValue()}')
    total_distance = 0
    total_load = 0
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Ruta para el vehículo {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += '{0} Carga({1}) Tiempo({2},{3}) -> '.format(
                node_index, route_load, solution.Min(time_var), solution.Max(time_var))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        
        time_var = time_dimension.CumulVar(index)
        plan_output += '{0} Carga({1}) Tiempo({2},{3})\n'.format(
            manager.IndexToNode(index), route_load, solution.Min(time_var), solution.Max(time_var))
        plan_output += 'Distancia de la ruta: {}m\n'.format(route_distance/100) # Convertir de vuelta
        plan_output += 'Carga de la ruta: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
        
    print('Distancia total de todas las rutas: {}m'.format(total_distance/100))
    print('Carga total de todas las rutas: {}'.format(total_load))

def solve_vrp(data):
    """Resuelve el VRP con los datos proporcionados."""
    # Crear el gestor de índices de enrutamiento
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    
    # Crear el modelo de enrutamiento
    routing = pywrapcp.RoutingModel(manager)
    
    # Definir callback de costo (distancia)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Añadir restricción de Capacidad
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
    
    # Añadir restricción de Ventanas de Tiempo
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Tiempo de servicio + tiempo de viaje
        # La matriz de distancia está escalada por 100, así que dividimos por 100 para obtener km (y minutos a 1km/min)
        service_time = data['service_time'][from_node]
        travel_time = int(data['distance_matrix'][from_node][to_node] / 100)
        return service_time + travel_time
        
    time_callback_index = routing.RegisterTransitCallback(time_callback)
    
    routing.AddDimension(
        time_callback_index,
        3000,  # allow waiting time (slack)
        3000,  # maximum time per vehicle
        False,  # Don't force start cumul to zero
        'Time')
    
    time_dimension = routing.GetDimensionOrDie('Time')
    
    # Añadir restricciones de ventanas de tiempo para cada ubicación
    for location_idx, time_window in enumerate(data['time_windows']):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        
    # Instanciar las heurísticas de búsqueda
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    # Resolver el problema
    solution = routing.SolveWithParameters(search_parameters)
    return solution, routing, manager

def main():
    """Entrada principal del programa."""
    # Instanciar los datos
    data = create_data_model()
    
    solution, routing, manager = solve_vrp(data)
    
    # Imprimir solución
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print('No se encontró solución.')

if __name__ == '__main__':
    main()
