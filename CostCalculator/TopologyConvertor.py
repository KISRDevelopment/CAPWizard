import numpy as np
import numpy.typing as npt 
import pandas as pd

def create_technology_and_fuel_indices(result_df: pd.DataFrame):
    # Create unique identifiers for technologies and fuels
    result_df.loc[:, 'technology'] = result_df['tech_code'] + '___' + result_df['activity_code'].astype(str)
    result_df.loc[:, 'fuel_type'] = result_df['level'] + '___' + result_df['form']

    # Extract unique technology identifiers and fuel types
    technologies = result_df['technology'].unique()
    fuel_types = result_df['fuel_type'].unique()

    # Create mappings for technologies and fuel types to indices
    tech_to_idx = {tech: idx for idx, tech in enumerate(technologies)}
    fuel_to_idx = {fuel: idx for idx, fuel in enumerate(fuel_types)}

    return tech_to_idx, fuel_to_idx, result_df


def create_inp_out(result_df: pd.DataFrame):

    # Get the technology and fuel indices
    tech_to_idx, fuel_to_idx, result_df = create_technology_and_fuel_indices(result_df)

    # Extract unique technology identifiers and fuel types
    technologies = result_df['technology'].unique()
    fuel_types = result_df['fuel_type'].unique()

    # Initialize input and output matrices
    N = len(technologies)
    F = len(fuel_types)
    # Initialize input and output matrices as 2D arrays
    input_matrix = np.zeros((N, F))
    output_matrix = np.zeros((N, F))

    # Populate the matrices
    for _, row in result_df.iterrows():
        tech_idx = tech_to_idx[row['technology']]
        fuel_idx = fuel_to_idx[row['fuel_type']]
        value = row['value']
        if row['type'] in ['main input', 'input']:
            input_matrix[tech_idx, fuel_idx] += value
        elif row['type'] in ['main output', 'output']:
            output_matrix[tech_idx, fuel_idx] += value

    # Invert the fuel dict
    idx_to_fuel = {idx: fuel for fuel, idx in fuel_to_idx.items()}

    # Add resource and demand nodes to balance the matrix
    diff = np.sum(output_matrix - input_matrix, axis=0)
    sensitivity = 0.1
    out_rows = []
    in_rows = []
    new_keys = []
    for i, d in enumerate(diff):
        if d < sensitivity:
            v = np.zeros(len(diff))
            in_rows.append(v.copy())
            v[i] = -d
            out_rows.append(v)
            new_keys.append("%s_resource" % idx_to_fuel[i])
        elif d > sensitivity:
            v = np.zeros(len(diff))
            out_rows.append(v.copy())
            v[i] = d
            in_rows.append(v)
            new_keys.append("%s_demand" % idx_to_fuel[i])

    input_matrix = np.vstack((input_matrix, in_rows))
    output_matrix = np.vstack((output_matrix, out_rows))

    # reindex to include new nodes
    all_keys = technologies.tolist() + new_keys
    tech_to_idx = dict(zip(all_keys, range(len(all_keys))))
    
    return input_matrix, output_matrix, tech_to_idx, fuel_to_idx


def to_network(input_table: npt.NDArray, output_table: npt.NDArray) -> npt.NDArray:
    """
        Takes input and output tables of the shape N (nodes) x F (fuels) and converts
        them into a multi-graph consisting of N nodes. 
        The input and output tables specify the number of units of each fuel consumed/produced by
        each node. 
        The output of the function are the adjaceny matrices, one for each fuel.

        Inputs:
            input_table:    NxF
            output_table:   NxF
        Output:
            As_normed: FxNxN normalized adjacency matrices
            As: FxNxN raw adjacency matrices (these give you the units from A->B)
    """

    # for each fuel, determine how much each node contributes to making
    # that fuel
    output_props = output_table / np.sum(output_table, axis=0)[None, :] # NxF
    output_props = np.nan_to_num(output_props)
    
    # now construct an adjacency matrix for each fuel
    As = []
    for f in range(input_table.shape[1]):
        f_output_prop = output_props[:, [f]] # Nx1
        inputs = input_table[:, f][None, :] # 1xN
        A = np.dot(f_output_prop, inputs) # NxN
        As.append(A)
    As = np.array(As) # FxNxN

    # finally, normalize
    As_normed = As / np.sum(As, axis=(0, 2))[None, :, None] # FxNxN / 1xNx1 = FxNxN
    As_normed = np.nan_to_num(As_normed) # to handle nodes with no outputs
    
    return As_normed, As


def create_cost_dataframe(results):
    split_results = []
    for result in results:
        fuel_level, fuel_form = result['fuel'].split('___')
        src_tech, src_activity = result['src'].split('___')
        dst_tech, dst_activity = result['dst'].split('___')
        
        split_results.append({
            'sheet': result['sheet'],
            'year': result['year'],
            'src_tech_code': src_tech,
            'src_activity_code': src_activity,
            'dst_tech_code': dst_tech,
            'dst_activity_code': dst_activity,
            'level': fuel_level,
            'form': fuel_form,
            'total_cost_USD': result['total_cost'],
            'units_MWyr': result['units']
        })

    return pd.DataFrame(split_results)
