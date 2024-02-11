import numpy as np 
import numpy.typing as npt 
from collections import defaultdict


def calculate_costs(As_normed, As, V, F, tech_to_idx, fuel_to_idx, sheet, year):
    idx_to_tech = {idx: tech for tech, idx in tech_to_idx.items()}
    idx_to_fuel = {idx: fuel for fuel, idx in fuel_to_idx.items()}

    TECHS = len(tech_to_idx)  # Number of technologies
    FUELS = len(fuel_to_idx)  # Number of fuels

    results = []  # List to store results

    for fuel_idx in range(FUELS):
        for src_idx in range(TECHS):
            for dst_idx in range(TECHS):
                params = {'src': src_idx, 'dst': dst_idx, 'fuel': fuel_idx, 'max_visits': 20}
                total_cost = calculate_cost(As_normed, V, F, **params)
                if total_cost:
                    units = As[params['fuel'], params['src'], params['dst']]
                    results.append({
                        'sheet': sheet,
                        'year': year,
                        'fuel': idx_to_fuel[fuel_idx],
                        'src': idx_to_tech[src_idx],
                        'dst': idx_to_tech[dst_idx],
                        'total_cost': total_cost,
                        'units': units
                    })
    return results


def calculate_cost(A: npt.NDArray, 
                   V: npt.NDArray, 
                   F: npt.NDArray, 
                   src: int, 
                   dst: int,
                   fuel: int,
                   max_visits: int = 5) -> float:
    """
        Calculates the cost of specific edge on a multi-graph.
        The graph consists of multiple "layers", which correspond to fuels in our case.
        Each layer is a directed graph that is represented via an adjacency matrix.
        Entry f, i, j in the adjacency matrix is the weight of the fuel f from node i to node j 
        (normalized with respect to all outputs of node i, across all fuels).
        The weight of edge f,i,j here is the proportion of node i's total VOM that is allocated to the edge.

        Inputs:
            A: adjacency matrices for all layers of shape = Fuels x Nodes x Nodes. 
               The matrix should satisfy the condition that Ac = np.sum(A, axis=0) is row-normal.
               That is, each row in Ac should sum to one.
            V: total VOM vector for each node (length = Nodes)
            F: total FOM vector for each node (length = Nodes)
            src: source node id
            dst: destination node id
            fuel: fuel or layer id
            max_visits: maximum number an edge can be visited before stopping
        Outputs:
            cost: the cost of the given edge. 
    """
    # no connection, stop
    if A[fuel, src, dst] == 0:
        return 0
    
    visit_count = defaultdict(int)

    # add to visit count
    visit_count[src] += 1

    # get the VOM for orginating node
    src_vom =  V[src] * 1000

    # get the FOM for orginating node
    src_fom =  F[src] * 1000

    # from this point on, we do not care about multi-edges, so we collapse them
    Acollapsed = np.sum(A, axis=0) # Nodes x Nodes

    # compute cost
    cost = A[fuel, src, dst] * (src_vom + src_fom + sum(calculate_cost_inner(Acollapsed, V, F, src=s, dst=src, visit_count=visit_count, max_visits=max_visits)
                                                        for s in range(A.shape[1])))
    
    return cost 


def calculate_cost_inner(A: npt.NDArray, 
                   V: npt.NDArray, 
                   F: npt.NDArray, 
                   src: int, 
                   dst: int,
                   visit_count: defaultdict,
                   max_visits: int = 5) -> float:
    
    # no connection, stop
    if A[src, dst] == 0:
        return 0
    
    # add to visit count
    visit_count[src] += 1

    # visited this node many times ...
    if visit_count[src] > max_visits:
        return 0
    
    # get the VOM for orginating node
    src_vom =  V[src] * 1000

    # get the FOM for orginating node
    src_fom =  F[src] * 1000

    # compute cost
    cost = A[src, dst] * (src_vom + src_fom + sum(calculate_cost_inner(A, V, F, src=s, dst=src, visit_count=visit_count, max_visits=max_visits)
                                                  for s in range(A.shape[0])))

    return cost
