class Grafo:
    def __init__(self):
        self.lista_ady = {}
        self.capacidades = {}
        self.originales = set()

    def agregar_vertice(self, v):
        if v not in self.lista_ady:
            self.lista_ady[v] = []

    def agregar_arista(self, u, v, cap):
        self.agregar_vertice(u)
        self.agregar_vertice(v)
        self.lista_ady[u].append(v)
        self.lista_ady[v].append(u)
        self.capacidades[(u, v)] = cap
        self.capacidades[(v, u)] = 0
        self.originales.add((u, v))

    def bfs(self, s, t, padres):
        visitados = {v: False for v in self.lista_ady}
        cola = [s]
        visitados[s] = True

        while cola:
            u = cola.pop(0)
            for vecino in self.lista_ady[u]:
                capacidad_restante = self.capacidades[(u, vecino)]
                if not visitados[vecino] and capacidad_restante > 0:
                    cola.append(vecino)
                    visitados[vecino] = True
                    padres[vecino] = u
                    if vecino == t:
                        return True
        return visitados[t]
    
    def edmonds_karp(self, fuente, sumidero):
        padres = {}
        flujo_max = 0
        while self.bfs(fuente, sumidero, padres):
            flujo_camino = float("inf")
            
            aux = sumidero
            while aux != fuente:
                flujo_camino = min(flujo_camino, self.capacidades[(padres[aux], aux)])
                aux = padres[aux]
            
            aux = sumidero
            while aux != fuente:
                self.capacidades[(padres[aux], aux)] -= flujo_camino
                self.capacidades[(aux, padres[aux])] += flujo_camino
                aux = padres[aux]
            
            flujo_max += flujo_camino
        return flujo_max


def dfs_descomponer_flujo(g, actual, sumidero, visitados=None):
    """Rastrea un camino de flujo positivo desde una banda hasta la plataforma."""
    if visitados is None:
        visitados = set()
    
    if actual == sumidero:
        return [actual]
    
    visitados.add(actual)
    
    for vecino in g.lista_ady[actual]:
        # solo sigue aristas originales por donde haya pasado flujo (cap de retorno > 0)
        if (actual, vecino) in g.originales and g.capacidades[(vecino, actual)] > 0 and vecino not in visitados:
            camino = dfs_descomponer_flujo(g, vecino, sumidero, visitados)
            if camino:
                return [actual] + camino
    return None

def modelar_grafo(g, bandas, servidores, plataformas, banda_servidor, servidor_plataforma, fuente, sumidero):
    total_espectadores = 0
    
    # nodos fuente, sumidero y servidores
    for id_banda, bx in bandas:
        g.agregar_arista(fuente, id_banda, bx)
        total_espectadores += bx
        
    for id_servidor, sx in servidores:
        g.agregar_arista(f"{id_servidor}_in", f"{id_servidor}_out", sx)
        
    for id_plataforma, px in plataformas:
        g.agregar_arista(id_plataforma, sumidero, px)
        
    # Contratos
    for id_banda, id_servidor in banda_servidor:
        g.agregar_arista(id_banda, f"{id_servidor}_in", float('inf'))
        
    for id_servidor, id_plataforma in servidor_plataforma:
        g.agregar_arista(f"{id_servidor}_out", id_plataforma, float('inf'))
        
    return total_espectadores


def descomponer_flujos(g, bandas, sumidero):
    asignacion_dict = {}
    
    for id_banda, _ in bandas:
        while True:
            camino = dfs_descomponer_flujo(g, id_banda, sumidero)
            if not camino:
                break 
            
            # Identificar el cuello de botella del camino y descontarlo
            flujo_camino = min(g.capacidades[(v, u)] for u, v in zip(camino[:-1], camino[1:]))
            
            for u, v in zip(camino[:-1], camino[1:]):
                g.capacidades[(v, u)] -= flujo_camino
                
            plataforma = camino[-2]
            clave = (id_banda, plataforma)
            asignacion_dict[clave] = asignacion_dict.get(clave, 0) + flujo_camino

    return [(b, p, cant) for (b, p), cant in asignacion_dict.items()]


def main(bandas, servidores, plataformas, banda_servidor, servidor_plataforma):
    g = Grafo()
    fuente = "s"
    sumidero = "t"
    
    total_espectadores = modelar_grafo(g, bandas, servidores, plataformas, banda_servidor, servidor_plataforma, fuente, sumidero)
    
    flujo_max = g.edmonds_karp(fuente, sumidero)
    
    asignacion = descomponer_flujos(g, bandas, sumidero)
    
    posible = (flujo_max == total_espectadores)
    
    return (posible, flujo_max, asignacion)