import math
import os
import matplotlib.pyplot as plt
import numpy as np
import snap
import time


start_time = time.time()

np.random.seed()

G = snap.LoadEdgeList(snap.PUNGraph, 'ca-GrQc.txt', 0, 1)
deg = [v.GetDeg() for v in G.Nodes()]

##Statistiche del grafo
print("Numero di nodi: ", G.GetNodes())
print("Numero di archi: ", G.GetEdges())
print("Grado medio del grafo è ",np.mean(deg))
print("Grado massimo: ", G.GetNI(snap.GetMxDegNId(G)).GetDeg())
print("Diametro (approssimato): ", snap.GetBfsFullDiam(G, 10))
print("Triangoli: ", snap.GetTriads(G))
print("Coefficiente di clustering: ", snap.GetClustCf(G))

# Calcolo della probabilità p(u, v)
def compute_probability(u, v):
    deg_u = G.GetNI(u).GetDeg()
    deg_v = G.GetNI(v).GetDeg()
    return 1 / max(deg_u, deg_v)

if(0):# DEBUG
    # Iterazione sugli archi
    for edge in G.Edges():
        u = edge.GetSrcNId()
        v = edge.GetDstNId()
        prob = compute_probability(u, v)
        print("Probabilità p({},{}) = {}".format(u, v, prob))

#Creazione di un grafo con gli archi positivi e negativi    
edgePositivi = []
edgeNegativi = []
# Iterazione sugli archi
for edge in G.Edges():
    u = edge.GetSrcNId()
    v = edge.GetDstNId()
    
    r = np.random.uniform(0, 1) # Numero casuale tra 0 e 1
    if r >= compute_probability(u, v):
        edgePositivi.append((u,v)) 
    else:
        edgeNegativi.append((u,v)) 
    
print("Numero di archi positivi: ", len(edgePositivi))
print("Numero di archi negativi: ", len(edgeNegativi))
print(edgePositivi)
#################

def seeds_greedy_degree_max():
    # Fissato un intero k, determinare un seed set di dimensione k del grafo con archi positivi e negativi
    k = 10  # Dimensione del seed set
    S = []  # Seed set inizialmente vuoto

    while len(S) < k:
        max_deg = -1  # Conteggio il massimo di adiacenti positivi

        # Trova il nodo con il massimo numero di adiacenti positivi tra i nodi non ancora presenti in S
        for node in G.Nodes():
            if node.GetId() not in S: # Se il nodo non è già presente in S
                adj_positive = 0  # Variabile per conteggio degli archi positivi adiacenti al nodo corrente
                for edge in edgePositivi: # Iterazione sugli archi positivi
                    if edge[0] == node.GetId() or edge[1] == node.GetId(): # Se il nodo corrente ha un arco positivo
                        adj_positive += 1 # Incrementa il conteggio degli archi positivi adiacenti al nodo corrente
                if adj_positive > max_deg: # Controllo se il corrente è ancora quello con piu adiacenti positivi
                    max_deg = adj_positive
                    max_deg_node = node.GetId()

        S.append(max_deg_node)  # Aggiungi il nodo con il massimo numero di adiacenti positivi a S

    print("Seed set di dimensione", k, ":", S)


def seeds_greedy_residual_degree_max():
    # Il grado residuo di un nodo rappresenta il numero di archi rimanenti che il nodo ha verso altri nodi non ancora selezionati come seed.
    # Calcolo dei gradi residui iniziali per ogni nodo
    residual_degrees = {}
    for node in G.Nodes():
        residual_degrees[node.GetId()] = node.GetDeg()
        
    k = 10  # Dimensione del seed set
    S = []  # Seed set inizialmente vuoto

    while len(S) < k:
        max_deg = -1  # Conteggio il massimo di adiacenti positivi

        # Trova il nodo con il massimo numero di adiacenti positivi tra i nodi non ancora presenti in S
        for node in G.Nodes():
            if node.GetId() not in S: # Se il nodo non è già presente in S
                adj_positive = 0  # Variabile per conteggio degli archi positivi adiacenti al nodo corrente
                for edge in edgePositivi: # Iterazione sugli archi positivi
                    if edge[0] == node.GetId() or edge[1] == node.GetId(): # Se il nodo corrente ha un arco positivo
                        adj_positive += 1 # Incrementa il conteggio degli archi positivi adiacenti al nodo corrente
                if adj_positive > max_deg: # Controllo se il corrente è ancora quello con piu adiacenti positivi
                    max_deg = adj_positive
                    max_deg_node = node.GetId()

        S.append(max_deg_node)  # Aggiungi il nodo con il massimo numero di adiacenti positivi a S
        # Aggiorna i gradi residui dei vicini del nodo selezionato
        for edge in G.Edges():
            u = edge.GetSrcNId()
            v = edge.GetDstNId()
            if u == max_deg_node:
                residual_degrees[v] -= 1
            elif v == max_deg_node:
                residual_degrees[u] -= 1