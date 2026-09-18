import numpy as np

def cosine_distance(source_representation, test_representation):
    a = np.array(source_representation)
    b = np.array(test_representation)
    
    if a.shape != b.shape:
        return 1.0 # Max distance if shapes don't match

    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)

    if a_norm == 0 or b_norm == 0:
        return 1.0

    similarity = np.dot(a, b) / (a_norm * b_norm)
    distance = 1 - similarity
    return distance
