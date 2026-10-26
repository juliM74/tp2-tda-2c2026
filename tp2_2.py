from collections import deque


class Grafo:
    def __init__(self):
        self.lista_ady = {}
        self.capacidades = {}
        self.originales = set()
        self.cap_original = {}

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
        self.cap_original[(u, v)] = cap

    def bfs(self, s, t, padres):
        visitados = {v: False for v in self.lista_ady}
        cola = deque([s])
        visitados[s] = True

        while cola:
            u = cola.popleft()
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


def dfs_descomponer_flujo(g, actual, sumidero, flujo_retorno, visitados):
    if actual == sumidero:
        return [actual]
    visitados.add(actual)

    for vecino in g.lista_ady[actual]:
        if (
            (actual, vecino) in g.originales
            and flujo_retorno.get((vecino, actual), 0) > 0
            and vecino not in visitados
        ):
            camino = dfs_descomponer_flujo(
                g, vecino, sumidero, flujo_retorno, visitados
            )
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
    flujo_retorno = dict(g.capacidades)
    asignacion_dict = {}

    for id_banda, _ in bandas:
        while True:
            camino = dfs_descomponer_flujo(
                g, id_banda, sumidero, flujo_retorno, set()
            )
            if not camino:
                break

            flujo_camino = min(
                flujo_retorno[(v, u)] for u, v in zip(camino[:-1], camino[1:])
            )
            for u, v in zip(camino[:-1], camino[1:]):
                flujo_retorno[(v, u)] -= flujo_camino

            plataforma = camino[-2]
            clave = (id_banda, plataforma)
            asignacion_dict[clave] = asignacion_dict.get(clave, 0) + flujo_camino

    return [(b, p, cant) for (b, p), cant in asignacion_dict.items()]


def cancelar_camino(g, origen, destino, cantidad):
    padres = {}
    visitados = {v: False for v in g.lista_ady}
    cola = deque([origen])
    visitados[origen] = True

    while cola:
        u = cola.popleft()
        if u == destino:
            break
        for vecino in g.lista_ady[u]:
            if not visitados[vecino] and g.capacidades[(u, vecino)] > 0:
                visitados[vecino] = True
                padres[vecino] = u
                cola.append(vecino)

    if destino not in padres:
        return 0

    cuello = cantidad
    actual = destino
    while actual != origen:
        anterior = padres[actual]
        cuello = min(cuello, g.capacidades[(anterior, actual)])
        actual = anterior

    actual = destino
    while actual != origen:
        anterior = padres[actual]
        g.capacidades[(anterior, actual)] -= cuello
        g.capacidades[(actual, anterior)] += cuello
        actual = anterior
    return cuello


ESTADO = {
    "grafo": None,
    "fuente": "s",
    "sumidero": "t",
    "flujo_max": 0,
    "total_espectadores": 0,
    "bandas": [],
}


def main(bandas, servidores, plataformas, banda_servidor, servidor_plataforma):
    global ESTADO
    g = Grafo()
    fuente = "s"
    sumidero = "t"

    total_espectadores = modelar_grafo(
        g,
        bandas,
        servidores,
        plataformas,
        banda_servidor,
        servidor_plataforma,
        fuente,
        sumidero,
    )
    flujo_max = g.edmonds_karp(fuente, sumidero)
    asignacion = descomponer_flujos(g, bandas, sumidero)
    posible = (flujo_max == total_espectadores)

    ESTADO.update(
        grafo=g,
        fuente=fuente,
        sumidero=sumidero,
        flujo_max=flujo_max,
        total_espectadores=total_espectadores,
        bandas=bandas,
    )
    return (posible, flujo_max, asignacion)


def actualizar_servidor(id_servidor, nueva_capacidad):
    g = ESTADO["grafo"]
    fuente = ESTADO["fuente"]
    sumidero = ESTADO["sumidero"]

    if g is None:
        raise RuntimeError("Debe ejecutarse main antes de actualizar_servidor")
    if nueva_capacidad < 0:
        raise ValueError("La capacidad no puede ser negativa")

    u = f"{id_servidor}_in"
    v = f"{id_servidor}_out"
    if (u, v) not in g.cap_original:
        raise ValueError(f"Servidor inexistente: {id_servidor}")
    
    capacidad_anterior = g.cap_original[(u, v)]
    flujo_actual = g.capacidades[(v, u)]
    g.cap_original[(u, v)] = nueva_capacidad

    if nueva_capacidad >= capacidad_anterior:
        g.capacidades[(u, v)] += (nueva_capacidad - capacidad_anterior)
        ESTADO["flujo_max"] += g.edmonds_karp(fuente, sumidero)

    elif flujo_actual > nueva_capacidad:
        exceso = flujo_actual - nueva_capacidad
        
        restante_fuente = exceso
        while restante_fuente > 0:
            c = cancelar_camino(g, u, fuente, restante_fuente)
            if c == 0:
                break
            restante_fuente -= c

        restante_sumidero = exceso
        while restante_sumidero > 0:
            c = cancelar_camino(g, sumidero, v, restante_sumidero)
            if c == 0:
                break
            restante_sumidero -= c

        g.capacidades[(u, v)] = 0
        g.capacidades[(v, u)] = nueva_capacidad
        ESTADO["flujo_max"] -= exceso

        ESTADO["flujo_max"] += g.edmonds_karp(fuente, sumidero)

    else:
        g.capacidades[(u, v)] -= (capacidad_anterior - nueva_capacidad)

    posible = ESTADO["flujo_max"] == ESTADO["total_espectadores"]
    asignacion = descomponer_flujos(g, ESTADO["bandas"], ESTADO["sumidero"])
    return (posible, ESTADO["flujo_max"], asignacion)