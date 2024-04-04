import re

def read_c2m_distance_from_log(log_file_path):
    #Read Mean Distance and Standard Deviation from a log file.
    with open(log_file_path, 'r') as file:
        log_content = file.read()
        
   # Regular expression to extract mean distance and standard deviation
    pattern = r"Mean distance = (-?[\d\.]+(?:e-?\d+)?) / std deviation = (-?[\d\.]+(?:e-?\d+)?)"
    
    # Find matches in the log data
    matches = re.findall(pattern, log_content)
    mean_distance = []; std_deviation= []
    for match in matches:
        mean_distance.append(match[0]); std_deviation.append(match[1])
    
    # print
    print("Cloud to Mesh Distance:")
    print("-" * 40)
    print("Global Mesh Registration")
    print(f"Mean distance: {mean_distance[0]}, Standard deviation: {std_deviation[0]}")
    print("-" * 20)
    print("Closest Point Registration Procedure (ICP)")
    print(f"Mean distance: {mean_distance[1]}, Standard deviation: {std_deviation[1]}")
    
    return mean_distance , std_deviation
    