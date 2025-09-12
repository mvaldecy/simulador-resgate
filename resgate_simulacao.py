# -*- coding: utf-8 -*-
"""
Simulação do problema "Resgate em Prédio em Chamas"

- Modela o prédio como grafo com 7 andares e 12 salas por andar
- Aplica incertezas estocásticas nas arestas a cada execução
- Implementa BFS (não-informado) e Dijkstra (informado por custo)
- Permite rodar múltiplas simulações e comparar resultados

Autor: ChatGPT (para Bruno Ibiapina)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional
import math
import random
from collections import deque, defaultdict
import heapq

# -----------------------------
# Parâmetros do problema
# -----------------------------
NUM_ANDARES = 7
SALAS_POR_ANDAR = 12

# Custos base
CUSTO_LIVRE = 1.0
CUSTO_FUMACA = 5.0  # se houver fumaça no corredor

# Probabilidades de incerteza (por aresta por simulação)
P_PORTA_BLOQUEADA = 0.15         # portas entre pares e ímpares (horizontal "portas")
P_CORREDOR_FUMACA = 0.30         # corredor do andar pode ter fumaça entre quaisquer 2 salas
P_ESCADA_CONGESTIONADA = 0.20    # escada (vertical) dobra custo

# Semente para reprodutibilidade (ajuste/retire para aleatoriedade total)
SEMENTE = 42


@dataclass(frozen=True)
class Node:
    \"\"\"Um nó é identificado por (andar, sala).\"\"\"
    andar: int
    sala: int

    def __str__(self) -> str:
        return f\"A{self.andar}:S{self.sala}\"


@dataclass
class Edge:
    \"\"\"Aresta direcionada com custo (não-negativo) e tipo.\"\"\"
    u: Node
    v: Node
    custo: float
    tipo: str  # 'porta_par', 'porta_impar', 'corredor', 'escada'


class PredioGrafo:
    \"\"\"Gera a estrutura base (sem incerteza aplicada).\"\"\"
    def __init__(self, num_andares: int, salas_por_andar: int):
        self.num_andares = num_andares
        self.salas_por_andar = salas_por_andar
        self.nodes: List[Node] = [
            Node(a, s) for a in range(1, num_andares+1) for s in range(1, salas_por_andar+1)
        ]
        self.base_edges: List[Edge] = []
        self._construir_arestas_base()

    def _construir_arestas_base(self):
        # 1) Portas entre pares: 2<->4, 4<->6, ..., 10<->12
        for andar in range(1, self.num_andares+1):
            for s in range(2, self.salas_por_andar+1, 2):
                if s + 2 <= self.salas_por_andar:
                    a = Node(andar, s)
                    b = Node(andar, s+2)
                    self._add_bidirectional(a, b, CUSTO_LIVRE, \"porta_par\")

        # 2) Portas entre ímpares: 1<->3, 3<->5, ..., 9<->11
        for andar in range(1, self.num_andares+1):
            for s in range(1, self.salas_por_andar, 2):
                if s + 2 <= self.salas_por_andar:
                    a = Node(andar, s)
                    b = Node(andar, s+2)
                    self._add_bidirectional(a, b, CUSTO_LIVRE, \"porta_impar\")

        # 3) Corredor comum: conecta quaisquer duas salas do mesmo andar
        for andar in range(1, self.num_andares+1):
            salas = list(range(1, self.salas_por_andar+1))
            for i in range(len(salas)):
                for j in range(i+1, len(salas)):
                    a = Node(andar, salas[i])
                    b = Node(andar, salas[j])
                    self._add_bidirectional(a, b, CUSTO_LIVRE, \"corredor\")

        # 4) Escadas: sala 6 de cada andar conecta com sala 6 do andar superior
        for andar in range(1, self.num_andares):
            a = Node(andar, 6)
            b = Node(andar+1, 6)
            self._add_bidirectional(a, b, CUSTO_LIVRE, \"escada\")

    def _add_bidirectional(self, a: Node, b: Node, custo: float, tipo: str):
        self.base_edges.append(Edge(a, b, custo, tipo))
        self.base_edges.append(Edge(b, a, custo, tipo))


class AmostraGrafo:
    \"\"\"
    Um \"snapshot\" de uma simulação com incertezas aplicadas
    - remove portas bloqueadas
    - ajusta custo do corredor conforme fumaça
    - ajusta custo da escada conforme congestionamento
    \"\"\"
    def __init__(self, base: PredioGrafo, *, seed: Optional[int] = SEMENTE):
        self.base = base
        self.adj: Dict[Node, List[Tuple[Node, float]]] = defaultdict(list)
        # controle de semente por execução
        if seed is not None:
            random.seed(seed)
        self._amostrar_arestas()

    def _amostrar_arestas(self):
        for e in self.base.base_edges:
            # Decide o destino da aresta conforme tipo e incerteza
            if e.tipo in (\"porta_par\", \"porta_impar\"):
                # 15% de chance de ficar indisponível (aresta removida)
                if random.random() < P_PORTA_BLOQUEADA:
                    continue  # remove
                custo = CUSTO_LIVRE  # portas sem fumaça; custo fixo se existir
            elif e.tipo == \"corredor\":
                # 30% chance de fumaça, custo 5; senão custo 1
                custo = CUSTO_FUMACA if random.random() < P_CORREDOR_FUMACA else CUSTO_LIVRE
            elif e.tipo == \"escada\":
                # 20% chance de congestionamento, dobra custo
                custo = CUSTO_LIVRE * 2 if random.random() < P_ESCADA_CONGESTIONADA else CUSTO_LIVRE
            else:
                custo = e.custo

            self.adj[e.u].append((e.v, float(custo)))


# --------------------------------------
# Algoritmos de busca
# --------------------------------------
def bfs(origem: Node, destino: Node, adj: Dict[Node, List[Tuple[Node, float]]]) -> Optional[List[Node]]:
    \"\"\"Ignora custos; encontra qualquer caminho (se existir).\"\"\"
    fila = deque([origem])
    visitado = {origem: None}  # predecessor
    while fila:
        u = fila.popleft()
        if u == destino:
            # reconstrói caminho
            caminho = []
            x = u
            while x is not None:
                caminho.append(x)
                x = visitado[x]
            return list(reversed(caminho))
        for v, _ in adj.get(u, []):
            if v not in visitado:
                visitado[v] = u
                fila.append(v)
    return None


def dijkstra(origem: Node, destino: Node, adj: Dict[Node, List[Tuple[Node, float]]]) -> Tuple[float, Optional[List[Node]]]:
    \"\"\"Menor custo acumulado até destino. Retorna (custo, caminho).\"\"\"
    dist: Dict[Node, float] = defaultdict(lambda: math.inf)
    prev: Dict[Node, Optional[Node]] = {}
    dist[origem] = 0.0
    prev[origem] = None

    # desempate estável usando id(node) no heap
    heap = [(0.0, id(origem), origem)]
    while heap:
        d, _, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == destino:
            # reconstrói caminho
            caminho = []
            x = u
            while x is not None:
                caminho.append(x)
                x = prev[x]
            return dist[u], list(reversed(caminho))
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, id(v), v))

    return math.inf, None


# --------------------------------------
# Utilitários
# --------------------------------------
def caminho_custo(caminho: List[Node], adj: Dict[Node, List[Tuple[Node, float]]]) -> float:
    \"\"\"Calcula custo acumulado de um caminho (caso seja necessário verificar custo do BFS).\"\"\"
    if not caminho or len(caminho) == 1:
        return 0.0
    custo = 0.0
    # acelerar lookup de custo u->v
    adj_map = {u: {v: w for v, w in vizinhos} for u, vizinhos in adj.items()}
    for i in range(len(caminho)-1):
        u, v = caminho[i], caminho[i+1]
        w = adj_map.get(u, {}).get(v, math.inf)
        if math.isinf(w):
            return math.inf
        custo += w
    return custo


def simular(n_execucoes: int = 50, seed_inicial: Optional[int] = SEMENTE):
    \"\"\"Executa N simulações, variando a semente para incertezas a cada rodada.
    Retorna lista de dicionários com métricas por execução.
    \"\"\"
    base = PredioGrafo(NUM_ANDARES, SALAS_POR_ANDAR)
    origem = Node(1, 1)
    destino = Node(NUM_ANDARES, SALAS_POR_ANDAR)  # sala 12 do 7º andar

    resultados = []
    for i in range(n_execucoes):
        # varia a semente a cada rodada (se fornecida)
        seed_exec = (seed_inicial + i) if seed_inicial is not None else None
        amostra = AmostraGrafo(base, seed=seed_exec)

        # BFS (apenas alcançabilidade e um caminho qualquer)
        bfs_path = bfs(origem, destino, amostra.adj)
        bfs_sucesso = bfs_path is not None
        bfs_custo = caminho_custo(bfs_path, amostra.adj) if bfs_sucesso else math.inf

        # Dijkstra (caminho de menor custo)
        dj_custo, dj_path = dijkstra(origem, destino, amostra.adj)
        dj_sucesso = dj_path is not None and not math.isinf(dj_custo)

        resultados.append({
            \"execucao\": i+1,
            \"bfs_sucesso\": bfs_sucesso,
            \"bfs_custo\": None if not bfs_sucesso else bfs_custo,
            \"dijkstra_sucesso\": dj_sucesso,
            \"dijkstra_custo\": None if not dj_sucesso else dj_custo,
            \"bfs_passos\": None if not bfs_sucesso else len(bfs_path)-1,
            \"dijkstra_passos\": None if not dj_sucesso else len(dj_path)-1,
        })

    return resultados


def resumo(resultados: List[dict]) -> dict:
    \"\"\"Resumo estatístico simples sobre a lista de execuções.\"\"\"
    import statistics as stats
    def _mean(vals):
        vals = [v for v in vals if v is not None]
        return float(stats.mean(vals)) if vals else float('nan')

    bfs_sucessos = [1 if r[\"bfs_sucesso\"] else 0 for r in resultados]
    dj_sucessos = [1 if r[\"dijkstra_sucesso\"] else 0 for r in resultados]
    bfs_custos   = [r[\"bfs_custo\"] for r in resultados if r[\"bfs_custo\"] is not None]
    dj_custos    = [r[\"dijkstra_custo\"] for r in resultados if r[\"dijkstra_custo\"] is not None]
    bfs_passos   = [r[\"bfs_passos\"] for r in resultados if r[\"bfs_passos\"] is not None]
    dj_passos    = [r[\"dijkstra_passos\"] for r in resultados if r[\"dijkstra_passos\"] is not None]

    return {
        \"BFS_taxa_sucesso_%\": 100.0 * sum(bfs_sucessos) / len(resultados),
        \"Dijkstra_taxa_sucesso_%\": 100.0 * sum(dj_sucessos) / len(resultados),
        \"BFS_custo_medio\": _mean(bfs_custos),
        \"Dijkstra_custo_medio\": _mean(dj_custos),
        \"BFS_passos_medio\": _mean(bfs_passos),
        \"Dijkstra_passos_medio\": _mean(dj_passos),
    }


# --------------------------------------
# Execução direta
# --------------------------------------
if __name__ == \"__main__\":
    N = 100
    print(f\"Rodando {N} simulações...\")
    resultados = simular(n_execucoes=N)
    rsum = resumo(resultados)
    from pprint import pprint
    pprint(rsum)
