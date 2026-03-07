import numpy as np

from databases.database import read_identity_vector


def cosine_similarity(vectorX, vectorY):
    
    similarity = (np.dot(vectorX, vectorY) / (np.linalg.norm(vectorX) * np.linalg.norm(vectorY)))

    return similarity

def iv_cosine_similarity(vector, THRESHOLD: float = 0.6):
    list_identitiy_vectors = [np.frombuffer(iv.embedding, dtype=np.float32) for iv in read_identity_vector()]

    for iv in list_identitiy_vectors:

        if cosine_similarity(iv, vector.flatten()) >= THRESHOLD:
            return True


