## Introduzione

Le interazioni negative sono un fenomeno comune in molti aspetti della società e nelle tecnologie digitali, come le reti social e siti di recensioni come Trustpilot e TripAdvisor. Su queste piattaforme, gli utenti possono esprimere valutazioni positive o negative non solo sui servizi o sui luoghi visitati, ma anche sulle persone che hanno fornito un servizio o gestito un'attività. Queste recensioni possono avere un impatto notevole sull'immagine e sulla reputazione di un'azienda o di un servizio, e possono influenzare le decisioni degli altri utenti.

Analogamente, sulle piattaforme di social media come Facebook o Twitter, gli utenti possono seguire o bloccare altri utenti, creando una dinamica di interazione sia positiva che negativa.

Queste dinamiche non sono limitate al mondo digitale, ma si possono trovare anche in altri contesti come le competizioni tra nazioni o i legami nei sistemi ferromagnetici. 

Le 'signed networks' sono un concetto importante che si riferisce a reti in cui esistono sia interazioni positive che negative.

Una signed network può essere modellata attraverso un grafo non direzionato G=(V, E+ U E-)

* (u,v)∈E+ significa che c’è una interazione positiva tra u e v  
* (u,v)∈E- significa che c’è una interazione negativa tra u e v

* N+(u) = insieme degli adiacenti di u collegati attraverso link positivi.
* N-(u) = insieme degli adiacenti di u collegati attraverso link negativi.

L'obiettivo di questo progetto è stato:

A partire da un grafo G =(V, E), fissato una threshold function costante, un intero k e data una distribuzione di probabilità associata agli archi di G siamo andati a:

1. Costruire la signed network G = (V,  E+ U E-).
2. Determinare il seed-set S, con |S|=k, applicando i seguenti algoritmi: 
* seeds\_greedy\_difference\_max
* random\_walk
* target\_set\_selection
3. Eseguire il processo di attivazione per determinare l’insieme dei nodi attivati.
4. Ripetere 10 volte gli step 1. 2. e 3. calcolando la media della size dell’insieme dei nodi attivati.
5. Rappresentare con grafici i risultati ottenuti.

## Dataset

Il dataset utilizzato è Arxiv GR-QC (General Relativity and Quantum Cosmology), una rete di collaborazione proveniente dall’archivio scientifico arXiv \[1\], esso tratta delle collaborazioni scientifiche tra autori che hanno sottomesso i loro paper nella categoria di Relatività Generale e Cosmologia Quantistica.\[2\]
Si tratta di un grafo non orientato dove è presented un arco da i a j se l’autore i−esimo è co-autore di un paper con l’autore j−esimo. 

Se un articolo contiene k autori si ottiene un grafo fortemente connesso su k nodi. 

La rete ha le seguenti caratteristiche:

* 5242 nodi e 14496 archi 
* Grado medio: 5.53
* Grado massimo: 81
* Diametro: 13
* Coefficiente di clustering:  0.53
* Triangoli: 48285.
 

## Dettagli implementativi

Il progetto è stato implementato utilizzando il linguaggio Python nella versione 3.7.9 e la libreria SNAP per la manipolazione delle strutture dati a grafo.

Innanzitutto è stato necessario caricare il grafo presente nel file `ca-GrQc.txt`

`G = snap.LoadEdgeList(snap.PUNGraph, "ca-GrQc.txt", 0, 1)`

è stato creata la signed network

```plaintext
# Creazione di un grafo con gli archi positivi e negativi
edgePositivi = []
edgeNegativi = []
# Iterazione sugli archi
for edge in G.Edges():
u = edge.GetSrcNId()
v = edge.GetDstNId()

r = np.random.uniform(0, 1) # Numero casuale tra 0 e 1
if r >= compute_probability(G, u, v):
edgePositivi.append((u, v))
else:
edgeNegativi.append((u, v))
```

Successivamente viene calcolato il Seedset S con i tre algoritmi scelti

## Seeds Greedy Difference Max

```plaintext
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
S = [] # Seed set inizialmente vuoto

while len(S) < k: max_difference=-1 # Differenza massima tra adiacenti positivi e negativi max_deg_node=-1 # Nodo con la differenza massima # Trova il nodo con la differenza massima tra adiacenti positivi e negativi tra i nodi non ancora presenti in S for node in G.Nodes(): if node.GetId() not in S: adj_positive=positive_counts.get(node.GetId(), 0) adj_negative=negative_counts.get(node.GetId(), 0) if ( adj_positive>= adj_negative
    ): # Se il nodo corrente ha più adiacenti positivi che negativi
    difference = (
    adj_positive - adj_negative
    ) / threshold # Calcola la differenza tra adiacenti positivi e negativi
    
    if difference > max_difference:
    max_difference = difference
    max_deg_node = node.GetId()
    
    S.append(max_deg_node) # Aggiungi il nodo con la differenza massima a S
    
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
    ```
    
    ### Target Set Selection
    
    ```plaintext
    def tts(G,k):
    Grafo = snap.ConvertGraph(type(G), G)
    thresholdNodes = to_map_threshold(Grafo,2)
    S = []
    while Grafo.GetNodes() != 0:
    deletedNode = None
    for node in Grafo.Nodes():
    if thresholdNodes.get(node.GetId()) == 0:
    for neighbor in node.GetOutEdges():
    thresholdNodes[neighbor] = (
    thresholdNodes[neighbor] - 1
    if thresholdNodes[neighbor] - 1 > 0
    else 0
    )
    deletedNode = node.GetId()
    Grafo.DelNode(deletedNode)
    else:
    if node.GetOutDeg() < thresholdNodes[node.GetId()]: S.append(node.GetId()) for neighbor in node.GetOutEdges(): thresholdNodes[neighbor]=( thresholdNodes[neighbor] - 1 if thresholdNodes[neighbor] - 1> 0
        else 0
        )
        deletedNode = node.GetId()
        Grafo.DelNode(deletedNode)
        if deletedNode is None:
        max_ratio = -1
        for v in Grafo.Nodes():
        ratio = thresholdNodes[v.GetId()] / (v.GetOutDeg() * v.GetOutDeg() + 1)
        if ratio > max_ratio:
        max_ratio = ratio
        max_ratio_node = v.GetId()
        Grafo.DelNode(max_ratio_node)
        
        # Prendi i primi k nodi all'interno di S
        S = S[:k]
        return S
        ```
        
        ### Random Walk
        
        L'algoritmo da noi scelto per la selezione del Seed Set è il Random Walk, esso funziona nel seguente modo:
        
        1. Inizialmente, il Seed Set S è vuoto.
        2. Ripeti il seguente passo k volte (dove k è la dimensione desiderata del Seed Set): 
        1. Seleziona casualmente un nodo iniziale all'interno del grafo. 
        2. Esegui un random walk nel grafo a partire dal nodo iniziale con un numero di step fissato, salvando i nodi visitati.
        3. Aggiungi l'ultimo nodo visitato al Seed Set.
        3. Restituisci il Seed Set S.
        
        Durante il random walk, i nodi vengono visitati in base alle connessioni nel grafo(vicini). L'obiettivo è selezionare i nodi che sono raggiungibili in modo casuale all'interno del grafo, consentendo di coprire diverse porzioni del grafo stesso.
        
        L'approccio del random walk può essere utile in situazioni in cui si desidera selezionare nodi che potrebbero essere influenti anche in parti del grafo che risultano meno connesse o meno evidenti del grafo.
        
        ```plaintext
        def random_walk(G, k, steps):
        S = [] # Seed Set inizialmente vuoto
        for _ in range(k): # Ripeti k volte, dove k è la dimensione del Seed Set
        node_id = G.GetRndNId() # Selezione casuale di un nodo iniziale
        visited = set() # Insieme dei nodi visitati durante il random walk
        for _ in range(steps): # Ripeti steps volte, dove steps è il numero di passi del random walk
        visited.add(node_id) # Aggiungi l'ID del nodo corrente all'insieme dei visitati
        
        node = G.GetNI(node_id)
        neighbors = [node.GetOutNId(e) for e in range(node.GetOutDeg())] # Ottieni gli ID dei nodi vicini
        if not neighbors:
        break # Se il nodo non ha vicini, termina il random walk
        
        node_id = random.choice(neighbors) # Scegli un ID di nodo vicino casuale come prossimo nodo
        
        S.append(node_id) # Aggiungi l'ultimo nodo visitato al Seed Set
        
        return S
        ```
        
        Dopo aver determinato il Seed Set S è necessaria la funzione di attivazione che va a calcolare il numero di nodi attivo alla fine del processo di diffusione.
        
        ```plaintext
        def activationFunction(G, S, edgePositivi, edgeNegativi, threshold):
        # definire Insieme degli infetti al tempo t e al tempo t-1
        # Ciclare finché infectedT!=infectedT1
        # Ciclare per ogni nodo non infetto
        # Per ogni nodo v se il numero di archi positivi con gli infetti - il numero di archi negativi con gli infetti è maggiore o uguale alla threshold allora è infetto
        
        infectedT = [] # Inizializzo l'insieme degli infetti al tempo t
        infectedT1 = S # Inizializzo l'insieme degli infetti con il seed set #Insieme degli infetti al tempo t-1
        notInfected = []
        for node in G.Nodes():
        if node.GetId() not in infectedT1:
        notInfected.append(node.GetId()) # Insieme dei nodi non infetti
        
        while (
        infectedT != infectedT1
        ): # Ciclo finché l'insieme degli infetti al tempo t è diverso dall'insieme degli infetti al tempo t-1
        infectedT = infectedT1
        for v in notInfected:
        positive = 0
        negative = 0
        node = G.GetNI(v)
        for i in range(node.GetOutDeg()): # Itera sugli archi uscenti
        neighbor_id = node.GetOutNId(i)
        if (v, neighbor_id) in edgePositivi or (
        neighbor_id,
        v,
        ) in edgePositivi: # Se l'arco è positivo
        if neighbor_id in infectedT1:
        positive += 1
        elif (v, neighbor_id) in edgeNegativi or (
        neighbor_id,
        v,
        ) in edgeNegativi: # Se l'arco è negativo
        if neighbor_id in infectedT1:
        negative += 1
        if positive - negative >= threshold:
        infectedT1.append(v)
        
        return infectedT1
        ```
        
        Sono state scelte come grandezza k del Seed Set `[12,25,50,100,200,300,400,500]` , per ognuno viene eseguito ciascuno dei tre algoritmi per determinare il Seed Set S, eseguendo poi la funzione di attivazione per definire il numero di nodi attivati.
        
        Tutto ciò viene ripetuto 10 volte per poi calcolare la media della size dell’insieme dei nodi attivati.
        
        ## **References**
        
        \[1\] https://arxiv.org/
        \[2\] https://snap.stanford.edu/data/ca-GrQc.html