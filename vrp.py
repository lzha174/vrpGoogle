"""Simple Vehicles Routing Problem (VRP).

   This is a sample using the routing library python wrapper to solve a VRP
   problem.
   A description of the problem can be found here:
   http://en.wikipedia.org/wiki/Vehicle_routing_problem.

   Distances are in meters.
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
from data import *


def getDistance(origins):
    # importing required libraries
    API_key = apik
    gmaps = googlemaps.Client(key=API_key)
    result = gmaps.distance_matrix(origins, origins, mode='driving')
    distanceMatrix = []
    for elements in result['rows']:
        # every row is distance from one origin to all other destinations
        row = []
        print(elements)
        for element in elements['elements']:
            value = element['distance']['value']
            #print(value)
            row.append(value)
        distanceMatrix.append(row)
    # json method of response object
    print(distanceMatrix)
    return distanceMatrix


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    #data['distance_matrix'] =getDistance(addresses)
    data['distance_matrix'] = getStaticDistance()
    data['num_vehicles'] = 4
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""

    print(f'Objective: {solution.ObjectiveValue()}')
    max_route_distance = 0
    routes = []
    for vehicle_id in range(data['num_vehicles']):
        path = []
        index = routing.Start(vehicle_id)
        next = solution.Value(routing.NextVar(index))
        if routing.IsEnd(next): continue
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            path.append(manager.IndexToNode(previous_index))
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        path.append(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
        routes.append(path)
    print('Maximum of the route distances: {}m'.format(max_route_distance))
    return routes



def solvevrp():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        200000,  # vehicle maximum travel distance in meter
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    routes = []
    # Print solution on console.
    if solution:
        routes = print_solution(data, manager, routing, solution)
    else:
        print('No solution found !')

    # create a new strin array
    routesNames = []
    for route in routes:
        names = [addresses[i] for i in route]
        routesNames.append(names)
    print(routesNames)
    return routesNames