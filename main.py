import matplotlib.pyplot as plt
import numpy as np
import snap
import random
from multiprocessing import Pool

threshold = 2
G = snap.LoadEdgeList(snap.PUNGraph, "ca-GrQc.txt", 0, 1) # Caricamento del grafo

def random_threshold():
    # Generazione di un numero intero casuale
    number = random.randint(1, 100)

    # Applicazione di operazioni al numero
    if number % 2 == 0:
        number += random.randint(1, 10)
    else:
        number -= random.randint(1, 10)

    return number


def to_map_threshold(G, threshold=random_threshold()):
    dict = {}
    for v in G.Nodes():
        dict[v.GetId()] = threshold
    return dict


def main():
    seedset_list = [12,25,50,100,200,300,400,500]
    
    np.random.seed()
    deg = [v.GetDeg() for v in G.Nodes()]
    ##Statistiche del grafo
    print("Numero di nodi: ", G.GetNodes())
    print("Numero di archi: ", G.GetEdges())
    print("Grado medio del grafo è ", np.mean(deg))
    print("Grado massimo: ", G.GetNI(snap.GetMxDegNId(G)).GetDeg())
    print("Diametro (approssimato): ", snap.GetBfsFullDiam(G, 10))
    print("Triangoli: ", snap.GetTriads(G))
    print("Coefficiente di clustering: ", snap.GetClustCf(G))

    # draw_Graph(G)

    # Creazione di un grafo con gli archi positivi e negativi
    edgePositivi = []
    edgeNegativi = []
    # Iterazione sugli archi
    for edge in G.Edges():
        u = edge.GetSrcNId()
        v = edge.GetDstNId()

        r = np.random.uniform(0, 1)  # Numero casuale tra 0 e 1
        if r >= compute_probability(G, u, v):
            edgePositivi.append((u, v))
        else:
            edgeNegativi.append((u, v))

    print("Numero di archi positivi: ", len(edgePositivi))
    print("Numero di archi negativi: ", len(edgeNegativi))

    #parallel_seeds_greedy_difference_max(seedset_list,edgePositivi, edgeNegativi, threshold)
    #parallel_randomWalk(seedset_list, edgePositivi, edgeNegativi)
    parallel_tts(seedset_list,edgePositivi, edgeNegativi)
    
        
#################
def parallel_seeds_greedy_difference_max(seedset_list,edgePositivi, edgeNegativi, threshold):
    avg = []
    
    process_num = len(seedset_list)
    # Creazione degli argomenti per ogni iterazione
    args = [(edgePositivi, edgeNegativi, threshold, seed) for seed in seedset_list]
    # Creazione del pool di processi
    pool = Pool(processes=process_num)
    avg = pool.starmap(test_seeds_greedy_difference_max, args)
 
    # Chiusura del pool
    pool.close() 
             
    draw_avg(avg, seedset_list,"seeds_greedy_difference_max")
def parallel_randomWalk(seedset_list, edgePositivi, edgeNegativi):
    avg = []
    
    process_num = len(seedset_list)
    # Creazione degli argomenti per ogni iterazione
    args = [(seed, edgePositivi, edgeNegativi) for seed in seedset_list]
    # Creazione del pool di processi
    pool = Pool(processes=process_num)
    avg = pool.starmap(test_randomWalk, args)
 
    # Chiusura del pool
    pool.close() 
             
    draw_avg(avg, seedset_list,"randomWalk")
def parallel_tts(seedset_list,edgePositivi, edgeNegativi):
    avg = []
    
    process_num = len(seedset_list)
    # Creazione degli argomenti per ogni iterazione
    args = [(seed,edgePositivi,edgeNegativi) for seed in seedset_list]
    # Creazione del pool di processi
    pool = Pool(processes=process_num)
    
    avg = pool.starmap(test_tts, args)
 
    # Chiusura del pool
    pool.close() 
             
    draw_avg(avg, seedset_list,"tts")
    
# Funzione per il disegno del grafico medie
def draw_avg(avg, seedset_list,graph_name):
    plt.plot(seedset_list, avg, '--b')  # Linea blu
    plt.plot(seedset_list, avg, 'ro')   # Puntini rossi
    plt.xlabel("Seedset",)
    plt.ylabel("Numero medio di nodi infetti")
    plt.title(graph_name.upper())
    
    assex= seedset_list
    plt.xticks(assex)
    
    assey= avg
    plt.yticks(assey)

    plt.savefig("grafici/"+graph_name+".png")

def test_seeds_greedy_difference_max(edgePositivi, edgeNegativi, threshold, k):
    infectedList = []
    for i in range(10):
            S = seeds_greedy_difference_max(G, edgePositivi, edgeNegativi, threshold, k)
            print("Iterazione ",i," Grandezza del seed set: ", len(S))
            infezione = activationFunction(G, S, edgePositivi, edgeNegativi, threshold)
            print("Numero di nodi infetti: ", len(infezione),"\n")
            #print("Nodi infetti: ", infezione)
            
            infectedList.append(len(infezione))
    avg = np.mean(infectedList)
    return avg
    
# Funzione per testare l'algoritmo random walk
def test_randomWalk(seedset, edgePositivi, edgeNegativi):
    infectedList = []
    for i in range(10):
            S = random_walk(G, seedset, 10)
            print("Iterazione ",i," Grandezza del seed set: ", len(S))
            infezione = activationFunction(G, S, edgePositivi, edgeNegativi, threshold)
            print("Numero di nodi infetti: ", len(infezione),"\n")
            #print("Nodi infetti: ", infezione)
            
            infectedList.append(len(infezione))
    avg = np.mean(infectedList)
    return avg 

# Funzione per testare l'algoritmo tts
def test_tts(seed,edgePositivi, edgeNegativi):
    infected_list = []
    for i in range(10):
        S = tts(G,seed)
        infezione = activationFunction(G, S, edgePositivi, edgeNegativi, threshold)
        print("Numero di nodi infetti: ", len(infezione),"\n")
        #print("Nodi infetti: ", infezione)
        
        infected_list.append(len(infezione))
    avg = np.mean(infected_list)
    return avg

# Calcolo della probabilità p(u, v)
def compute_probability(G, u, v):
    deg_u = G.GetNI(u).GetDeg()
    deg_v = G.GetNI(v).GetDeg()
    return 1 / max(deg_u, deg_v)


def seeds_greedy_degree_max(G, edgePositivi):
    # Fissato un intero k, determinare un seed set di dimensione k del grafo con archi positivi e negativi
    k = 3  # Dimensione del seed set
    S = []  # Seed set inizialmente vuoto

    while len(S) < k:
        max_deg = -1  # Conteggio il massimo di adiacenti positivi

        # Trova il nodo con il massimo numero di adiacenti positivi tra i nodi non ancora presenti in S
        for node in G.Nodes():
            if node.GetId() not in S:  # Se il nodo non è già presente in S
                adj_positive = 0  # Variabile per conteggio degli archi positivi adiacenti al nodo corrente
                for edge in edgePositivi:  # Iterazione sugli archi positivi
                    if (
                        edge[0] == node.GetId() or edge[1] == node.GetId()
                    ):  # Se il nodo corrente ha un arco positivo
                        adj_positive += 1  # Incrementa il conteggio degli archi positivi adiacenti al nodo corrente
                if (
                    adj_positive > max_deg
                ):  # Controllo se il corrente è ancora quello con piu adiacenti positivi
                    max_deg = adj_positive
                    max_deg_node = node.GetId()

        S.append(
            max_deg_node
        )  # Aggiungi il nodo con il massimo numero di adiacenti positivi a S

    return S


def seeds_greedy_residual_degree_max(G, edgePositivi):
    # Calcolo dei gradi residui iniziali per ogni nodo
    residual_degrees = {}
    for node in G.Nodes():
        residual_degrees[node.GetId()] = node.GetDeg()

    k = 10  # Dimensione del seed set
    S = []  # Seed set inizialmente vuoto

    while len(S) < k:
        max_deg_residual = -1  # Grado residuo massimo
        max_deg_node = -1  # Nodo con il grado residuo massimo

        # Trova il nodo con il massimo grado residuo e il massimo numero di adiacenti positivi tra i nodi non ancora presenti in S
        for node in G.Nodes():
            if node.GetId() not in S:
                deg_residual = residual_degrees[
                    node.GetId()
                ]  # Grado residuo del nodo corrente
                adj_positive = (
                    0  # Conteggio degli archi positivi adiacenti al nodo corrente
                )
                for edge in edgePositivi:
                    if edge[0] == node.GetId() or edge[1] == node.GetId():
                        adj_positive += 1

                # Questo if ci permette di capire se il nodo corrente ha un grado positivo maggiore del massimo, a parità di grado positivo controlla il grado generale prendendo il massimo,
                # in modo tale da prendere il nodo con maggiori informazioni ma che abbia il maggior numero di adiacenti positivi
                if adj_positive > max_deg_residual or (
                    adj_positive == max_deg_residual
                    and deg_residual > residual_degrees[max_deg_node]
                ):
                    # Se il nodo corrente ha un grado residuo o un numero di adiacenti positivi maggiore del massimo
                    max_deg_residual = adj_positive
                    max_deg_node = node.GetId()

        S.append(
            max_deg_node
        )  # Aggiungi il nodo con il massimo grado residuo e il massimo numero di adiacenti positivi a S

        # Aggiorna i gradi residui dei vicini del nodo selezionato (solo per gli archi positivi)
        for edge in edgePositivi:
            u = edge.GetSrcNId()
            v = edge.GetDstNId()
            if u == max_deg_node:
                residual_degrees[v] -= 1
            elif v == max_deg_node:
                residual_degrees[u] -= 1

    return S


def seeds_greedy_difference_max(G, edgePositivi, edgeNegativi, threshold, k):
    # Calcola il numero di adiacenti positivi e negativi per ogni nodo
    positive_counts = {}
    negative_counts = {}
    for edge in edgePositivi:
        u = edge[0]
        v = edge[1]
        positive_counts[u] = positive_counts.get(u, 0) + 1
        positive_counts[v] = positive_counts.get(v, 0) + 1
    for edge in edgeNegativi:
        u = edge[0]
        v = edge[1]
        negative_counts[u] = negative_counts.get(u, 0) + 1
        negative_counts[v] = negative_counts.get(v, 0) + 1

    # k è la dimensione del seed set
    S = []  # Seed set inizialmente vuoto

    while len(S) < k:
        max_difference = -1  # Differenza massima tra adiacenti positivi e negativi
        max_deg_node = -1  # Nodo con la differenza massima

        # Trova il nodo con la differenza massima tra adiacenti positivi e negativi tra i nodi non ancora presenti in S
        for node in G.Nodes():
            if node.GetId() not in S:
                adj_positive = positive_counts.get(node.GetId(), 0)
                adj_negative = negative_counts.get(node.GetId(), 0)
                if (
                    adj_positive >= adj_negative
                ):  # Se il nodo corrente ha più adiacenti positivi che negativi
                    difference = (
                        adj_positive - adj_negative
                    ) / threshold  # Calcola la differenza tra adiacenti positivi e negativi

                    if difference > max_difference:
                        max_difference = difference
                        max_deg_node = node.GetId()

        S.append(max_deg_node)  # Aggiungi il nodo con la differenza massima a S

        # Aggiorna i conteggi degli archi positivi e negativi dei vicini del nodo selezionato
        for edge in edgePositivi:
            u = edge[0]
            v = edge[1]
            if u == max_deg_node:
                positive_counts[v] = positive_counts.get(v, 0) - 1
            elif v == max_deg_node:
                positive_counts[u] = positive_counts.get(u, 0) - 1

        for edge in edgeNegativi:
            u = edge[0]
            v = edge[1]
            if u == max_deg_node:
                negative_counts[v] = negative_counts.get(v, 0) - 1
            elif v == max_deg_node:
                negative_counts[u] = negative_counts.get(u, 0) - 1

    return S


def tts(G,k):
    """
    Imposta S=0
    Finche ci sono Nodi nel Grafo
        se il nodo ha threshold 0
           per ogni vicino del nodo: decrementa threshold, decrementa il grado, cancellalo dai vicini
        altrimenti
           se esiste un nodo tale che il grado è minore della thresh
               aggiungilo al seedset
               decrementa threshold, decrementa il grado, cancellalo dai vicini
           altrimenti
               prendi v con il ratio piu grande( threshold del nodo/grado * grado+1)
               elimina questo nodo che hai preso
       Togli v da insieme V"""
    Grafo = snap.ConvertGraph(type(G), G)
    thresholdNodes = to_map_threshold(Grafo,2)
    S = []
    while Grafo.GetNodes() != 0:
        deletedNode = None
        for node in Grafo.Nodes():
            if thresholdNodes.get(node.GetId()) == 0: # Caso in cui il nodo ha threshold 0
                for neighbor in node.GetOutEdges(): # Ciclo sui vicini del nodo
                    thresholdNodes[neighbor] = (
                        thresholdNodes[neighbor] - 1 # Decremento il threshold del vicino se maggiore di 0
                        if thresholdNodes[neighbor] - 1 > 0 
                        else 0
                    )
                deletedNode = node.GetId() 
                Grafo.DelNode(deletedNode) # Elimino il nodo dal grafo
            else:
                if node.GetOutDeg() < thresholdNodes[node.GetId()]: # Se il grado del nodo è minore della threshold
                    S.append(node.GetId()) # Aggiungo il nodo al seedset
                    for neighbor in node.GetOutEdges():
                        thresholdNodes[neighbor] = (
                            thresholdNodes[neighbor] - 1 # Decremento il threshold del vicino se maggiore di 0
                            if thresholdNodes[neighbor] - 1 > 0
                            else 0
                        )
                    deletedNode = node.GetId()
                    Grafo.DelNode(deletedNode) # Elimino il nodo dal grafo
        if deletedNode is None: # Se non ho eliminato nessun nodo allora prendo il nodo con il ratio più grande
            max_ratio = -1
            for v in Grafo.Nodes():
                ratio = thresholdNodes[v.GetId()] / (v.GetOutDeg() * v.GetOutDeg() + 1) # Calcolo il ratio
                if ratio > max_ratio:
                    max_ratio = ratio
                    max_ratio_node = v.GetId()
                    Grafo.DelNode(max_ratio_node) # Elimino il nodo dal grafo
                    
    # Prendi i primi k nodi all'interno di S
    S = S[:k]
    return S


def random_walk(G, k, steps):
    # k è la dimensione del Seed Set
    # Steps è il numero di passi del random walk
    S = []  
    
    for _ in range(k):  
        node_id = G.GetRndNId()  # Nodo random iniziale
        visited = set()

        for _ in range(steps):  
            visited.add(node_id)  # Nodo corrente è visited

            node = G.GetNI(node_id)
            neighbors = [node.GetOutNId(e) for e in range(node.GetOutDeg())]  # Salva i vicini del nodo corrente
            
            if not neighbors: # Se il nodo non ha vicini, break
                break  
            
            unvisited_neighbors = [n for n in neighbors if n not in visited]  # Filtra chi sono i vicini non visitati
            if not unvisited_neighbors: # Se non ci sono vicini non visitati, break
                break  

            node_id = random.choice(unvisited_neighbors)  # Sceglie un vicino casuale non visitato come prossimo nodo

        S.append(node_id) 

    return S


def activationFunction(G, S, edgePositivi, edgeNegativi, threshold):
    # definire Insieme degli infetti al tempo t e al tempo t-1
    # Ciclare finché infectedT!=infectedT1
    # Ciclare per ogni nodo non infetto
    # Per ogni nodo v se il numero di archi positivi con gli infetti - il numero di archi negativi con gli infetti è maggiore o uguale alla threshold allora è infetto

    infectedT = []  # Inizializzo l'insieme degli infetti al tempo t
    infectedT1 = S  # Inizializzo l'insieme degli infetti con il seed set #Insieme degli infetti al tempo t-1
    notInfected = []
    for node in G.Nodes():
        if node.GetId() not in infectedT1:
            notInfected.append(node.GetId())  # Insieme dei nodi non infetti

    while (
        infectedT != infectedT1
    ):  # Ciclo finché l'insieme degli infetti al tempo t è diverso dall'insieme degli infetti al tempo t-1
        infectedT = infectedT1
        for v in notInfected:
            positive = 0
            negative = 0
            node = G.GetNI(v)
            for i in range(node.GetOutDeg()):  # Itera sugli archi uscenti
                neighbor_id = node.GetOutNId(i)
                if (v, neighbor_id) in edgePositivi or (
                    neighbor_id,
                    v,
                ) in edgePositivi:  # Se l'arco è positivo
                    if neighbor_id in infectedT1:
                        positive += 1
                elif (v, neighbor_id) in edgeNegativi or (
                    neighbor_id,
                    v,
                ) in edgeNegativi:  # Se l'arco è negativo
                    if neighbor_id in infectedT1:
                        negative += 1
            if positive - negative >= threshold:
                infectedT1.append(v)

    return infectedT1


def draw_Graph(G):
    # Ottieni le coordinate dei nodi
    position = {}
    for node in G.Nodes():
        position[node.GetId()] = (np.random.rand(), np.random.rand())

    # Disegna i nodi e aggiungi i nomi
    plt.figure(figsize=(8, 8))
    plt.axis("off")
    for node in G.Nodes():
        node_id = node.GetId()
        x, y = position[node_id][0], position[node_id][1]
        plt.scatter(x, y, color="blue", edgecolor="black")
        plt.text(x + 0.02, y + 0.02, str(node_id), fontsize=8)

    # Disegna gli archi
    for edge in G.Edges():
        u, v = edge.GetSrcNId(), edge.GetDstNId()
        x = [position[u][0], position[v][0]]
        y = [position[u][1], position[v][1]]
        plt.plot(x, y, color="gray")

    plt.show()


if __name__ == "__main__":
    main()
