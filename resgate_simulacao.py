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

# Mantém apenas um import de cada
import matplotlib.pyplot as plt
from matplotlib import animation


# --------------------------------------
# Definições de classes e funções
# --------------------------------------

from dataclasses import dataclass
from typing import Dict, List
import math
import random
from collections import deque, defaultdict
import heapq
import matplotlib.pyplot as plt
from matplotlib import animation


@dataclass
class Node:
    andar: int
    sala: int

    def __hash__(self):
        return hash((self.andar, self.sala))

    def __str__(self):
        return f"A{self.andar}-S{self.sala}"

    def __lt__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return (self.andar, self.sala) < (other.andar, other.sala)


@dataclass
class Edge:
    destino: Node
    tipo: str
    custo: float
    bloqueada: bool = False
    fumaca: bool = False
    fumaca_toxica: bool = False
    escada_congestionada: bool = False


class PredioGrafo:
    def __init__(self, andares=7, salas=12):
        self.andares = andares
        self.salas = salas
        self.grafo: Dict[Node, List[Edge]] = defaultdict(list)
        self._criar_grafo()

    def _criar_grafo(self):
        """
        Cria a estrutura do prédio conforme especificação:
        - Salas ímpares conectadas: 1↔3, 3↔5, 5↔7, 7↔9, 9↔11
        - Salas pares conectadas: 2↔4, 4↔6, 6↔8, 8↔10, 10↔12
        - Corredor conecta todas as salas do mesmo andar
        - Escadas na sala 6 conectam andares adjacentes
        """
        for andar in range(self.andares):
            # 1. Conectar salas ímpares adjacentes (1-3, 3-5, 5-7, 7-9, 9-11)
            for sala in range(1, self.salas, 2):  # 1, 3, 5, 7, 9, 11
                if sala + 2 <= self.salas:  # Se existe próxima sala ímpar
                    atual = Node(andar, sala - 1)  # Converte para índice 0
                    vizinho = Node(andar, sala + 1)  # Próxima sala ímpar (índice 0)
                    self._adicionar_conexao_bidirecional(atual, vizinho, "porta_impar")
            
            # 2. Conectar salas pares adjacentes (2-4, 4-6, 6-8, 8-10, 10-12)
            for sala in range(2, self.salas + 1, 2):  # 2, 4, 6, 8, 10, 12
                if sala + 2 <= self.salas:  # Se existe próxima sala par
                    atual = Node(andar, sala - 1)  # Converte para índice 0
                    vizinho = Node(andar, sala + 1)  # Próxima sala par (índice 0)
                    self._adicionar_conexao_bidirecional(atual, vizinho, "porta_par")
            
            # 3. Corredor conecta todas as salas do mesmo andar
            for sala1 in range(self.salas):
                for sala2 in range(sala1 + 1, self.salas):
                    node1 = Node(andar, sala1)
                    node2 = Node(andar, sala2)
                    self._adicionar_conexao_bidirecional(node1, node2, "corredor")
            
            # 4. Escadas conectam sala 6 (índice 5) entre andares adjacentes
            if andar < self.andares - 1:
                atual = Node(andar, 5)  # Sala 6 (índice 5)
                acima = Node(andar + 1, 5)  # Sala 6 do andar superior
                self._adicionar_conexao_bidirecional(atual, acima, "escada")

    def _adicionar_conexao_bidirecional(self, node1: Node, node2: Node, tipo: str):
        """Adiciona conexão bidirecional entre dois nós"""
        custo_base = 1.0 if tipo != "escada" else 2.0
        self.grafo[node1].append(Edge(node2, tipo, custo_base))
        self.grafo[node2].append(Edge(node1, tipo, custo_base))

    def vizinhos(self, node: Node):
        return self.grafo[node]


class AmostraGrafo:
    def __init__(self, base: PredioGrafo):
        self.andares = base.andares
        self.salas = base.salas
        self.grafo: Dict[Node, List[Edge]] = defaultdict(list)
        self._amostrar(base)

    def _amostrar(self, base: PredioGrafo):
        """
        Aplica incertezas estocásticas conforme especificação:
        - 15% de portas (pares/ímpares) bloqueadas
        - 30% de corredores com fumaça (custo passa a 5)
        - 20% de escadas congestionadas (custo dobra)
        """
        for node, edges in base.grafo.items():
            for edge in edges:
                novo = Edge(edge.destino, edge.tipo, edge.custo)
                
                # Aplicar incertezas baseadas no tipo de conexão
                if edge.tipo in ["porta_par", "porta_impar"]:
                    # 15% de chance de porta estar bloqueada
                    if random.random() < 0.15:
                        novo.bloqueada = True
                
                elif edge.tipo == "corredor":
                    # 30% de chance de ter fumaça (custo passa a 5)
                    if random.random() < 0.30:
                        novo.fumaca = True
                        novo.custo = 5.0
                
                elif edge.tipo == "escada":
                    # 20% de chance de congestionamento (dobra custo)
                    if random.random() < 0.20:
                        novo.escada_congestionada = True
                        novo.custo = edge.custo * 2
                
                self.grafo[node].append(novo)

    def vizinhos(self, node: Node):
        return self.grafo[node]


def bfs(origem: Node, destino: Node, adj: Dict[Node, List[Tuple[Node, float]]]) -> Optional[List[Node]]:
    """Ignora custos; encontra qualquer caminho (se existir)."""
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
    """Menor custo acumulado até destino. Retorna (custo, caminho)."""
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
    while heap:
        custo, atual, caminho = heapq.heappop(heap)
        if atual == fim:
            return caminho, custo
        if atual in visitados:
            continue
        visitados.add(atual)
        for edge in grafo.vizinhos(atual):
            if edge.bloqueada:
                continue
            novo_custo = custo + edge.custo
            heapq.heappush(heap, (novo_custo, edge.destino, caminho + [edge.destino]))
    return None, math.inf


def encontrar_caminho_visitando_todas_salas(grafo, entrada: Node):
    """
    Encontra um caminho que visita todas as salas do prédio começando da entrada.
    Retorna o caminho completo e o custo total.
    """
    todas_salas = set()
    for andar in range(grafo.andares):
        for sala in range(grafo.salas):
            todas_salas.add(Node(andar, sala))
    
    return dfs_visitar_todas(grafo, entrada, todas_salas, [entrada], set([entrada]))


def dfs_visitar_todas(grafo, atual: Node, restantes: set, caminho: list, visitados: set):
    """DFS para visitar todas as salas"""
    if not restantes:
        return caminho, calcular_custo_caminho(grafo, caminho)
    
    for edge in grafo.vizinhos(atual):
        if edge.bloqueada or edge.destino in visitados:
            continue
            
        novo_caminho = caminho + [edge.destino]
        novo_visitados = visitados | {edge.destino}
        novas_restantes = restantes - {edge.destino}
        
        resultado = dfs_visitar_todas(grafo, edge.destino, novas_restantes, 
                                     novo_caminho, novo_visitados)
        if resultado[0]:  # Se encontrou solução
            return resultado
    
    return None, math.inf


def resgate_completo(grafo):
    """
    Simula o cenário completo de resgate:
    1. Visita todas as salas do prédio
    2. Vai da entrada até a sala 12 do último andar
    """
    entrada = Node(0, 0)  # Sala 1 do 1º andar (índice 0,0)
    destino_final = Node(grafo.andares - 1, grafo.salas - 1)  # Sala 12 do último andar
    
    print(f"Iniciando resgate na {entrada} (Sala 1, Andar 1)")
    print(f"Destino final: {destino_final} (Sala 12, Andar {grafo.andares})")
    
    # Fase 1: Visitar todas as salas
    print("\n=== FASE 1: Visitando todas as salas ===")
    caminho_completo, custo_visita = encontrar_caminho_visitando_todas_salas(grafo, entrada)
    
    if caminho_completo:
        print(f"✅ Todas as salas visitadas!")
        print(f"Salas visitadas: {len(caminho_completo)}")
        print(f"Custo total da visita: {custo_visita}")
        ultima_posicao = caminho_completo[-1]
    else:
        print("❌ Não foi possível visitar todas as salas")
        return None, math.inf
    
    # Fase 2: Ir para o destino final
    print(f"\n=== FASE 2: Indo para o destino final ===")
    print(f"Da posição {ultima_posicao} para {destino_final}")
    
    caminho_final, custo_final = dijkstra(grafo, ultima_posicao, destino_final)
    
    if caminho_final:
        print(f"✅ Destino alcançado!")
        print(f"Passos finais: {len(caminho_final)}")
        print(f"Custo final: {custo_final}")
        
        # Combinar caminhos
        caminho_total = caminho_completo + caminho_final[1:]  # Remove duplicata
        custo_total = custo_visita + custo_final
        
        return caminho_total, custo_total
    else:
        print("❌ Não foi possível alcançar o destino final")
        return None, math.inf


def calcular_custo_caminho(grafo, caminho):
    """Calcula o custo total de um caminho"""
    if len(caminho) <= 1:
        return 0
    
    custo_total = 0
    for i in range(len(caminho) - 1):
        atual = caminho[i]
        proximo = caminho[i + 1]
        
        # Encontra a aresta correspondente
        for edge in grafo.vizinhos(atual):
            if edge.destino == proximo and not edge.bloqueada:
                custo_total += edge.custo
                break
        else:
            return math.inf  # Caminho inválido
    
    return custo_total


def caminho_custo(grafo, caminho):
    custo = 0
    for i in range(len(caminho) - 1):
        for edge in grafo.vizinhos(caminho[i]):
            if edge.destino == caminho[i + 1]:
                custo += edge.custo
                break
    return custo


def resumo():
    return (
        "Regras do Resgate:\n"
        "- Prédio com 7 andares, 12 salas por andar.\n"
        "- Entrada: Sala 1 do 1º andar. Saída: Sala 12 do 7º andar.\n"
        "- Salas pares conectadas entre si (2↔4, 4↔6, ...).\n"
        "- Salas ímpares conectadas entre si (1↔3, 3↔5, ...).\n"
        "- Todas as salas conectadas por corredor comum no andar.\n"
        "- Escada na sala 6 conecta todos os andares.\n"
        "- Incertezas:\n"
        "   * Portas bloqueadas (15%)\n"
        "   * Corredor com fumaça (30%, custo 5)\n"
        "   * Fumaça tóxica (30%, dobra o custo do corredor)\n"
        "   * Escada congestionada (20%, dobra o custo)\n"
        "- Objetivo: resgatar vítimas e sair pelo menor caminho possível.\n"
    )


def simular(base, inicio, fim, algoritmo="dijkstra"):
    amostra = AmostraGrafo(base)
    if algoritmo == "bfs":
        caminho = bfs(amostra, inicio, fim)
        custo = caminho_custo(amostra, caminho) if caminho else math.inf
    else:
        caminho, custo = dijkstra(amostra, inicio, fim)
    return amostra, caminho, custo


def animar_caminho_detalhado(base, amostra, caminho, inicio, fim, custo):
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.title("Resgate em Prédio em Chamas - Andar 1 (Exemplo de Layout)", fontsize=15)
    # Layout das salas conforme a planta (6 à esquerda, 6 à direita, corredor central)
    sala_pos = {}
    for s in range(12):
        if s < 6:
            x, y = 0, 5 - s
        else:
            x, y = 2, 11 - s
        sala_pos[s] = (x, y)
    # Desenha as salas
    for s in range(12):
        x, y = sala_pos[s]
        ax.plot(x, y, "s", color="lightgrey", markersize=120, zorder=1)
        ax.text(
            x,
            y,
            str(s + 1),
            fontsize=16,
            ha="center",
            va="center",
            fontweight="bold",
            color="black",
            zorder=2,
        )
    # Desenha o corredor
    for y in range(6):
        ax.plot(1, y, "s", color="white", markersize=120, zorder=0, alpha=0.01)
    ax.text(
        1,
        2.5,
        "CORREDOR",
        fontsize=12,
        ha="center",
        va="center",
        rotation=90,
        color="gray",
        zorder=0,
    )
    # Desenha arestas
    for node, edges in amostra.grafo.items():
        andar = node.andar
        sala = node.sala
        if andar != 0:
            continue  # Só desenha o andar térreo para visualização
        x1, y1 = sala_pos[sala]
        for edge in edges:
            if edge.destino.andar != 0:
                continue
            x2, y2 = sala_pos[edge.destino.sala]
            cor = "black"
            lw = 2
            label = ""
            if edge.tipo == "porta" and edge.bloqueada:
                cor = "red"
                lw = 3
                label = "Porta bloqueada"
            elif edge.tipo == "porta" and edge.fumaca_toxica:
                cor = "purple"
                label = "Fumaça tóxica"
            elif edge.tipo == "porta" and edge.fumaca:
                cor = "orange"
                label = "Fumaça"
            elif edge.tipo == "escada" and edge.escada_congestionada:
                cor = "blue"
                lw = 3
                label = "Escada congestionada"
            ax.plot([x1, x2], [y1, y2], color=cor, lw=lw, zorder=0)
    # Escada (sala 6)
    ax.plot(2, 0, marker=(3, 0, 0), color="black", markersize=40, zorder=3)
    ax.text(
        2.2, 0, "ESCADA", fontsize=10, ha="left", va="center", color="black", zorder=3
    )
    # Status box
    status = ax.text(
        -0.5,
        -1.2,
        "",
        fontsize=12,
        va="top",
        ha="left",
        bbox=dict(facecolor="white", alpha=0.8),
    )
    regras = ax.text(
        2.7,
        5.5,
        resumo(),
        fontsize=10,
        va="top",
        ha="left",
        bbox=dict(facecolor="white", alpha=0.7),
    )
    # Caminho
    caminho_coords = (
        [(sala_pos[node.sala][0], sala_pos[node.sala][1]) for node in caminho]
        if caminho
        else []
    )
    (caminho_plot,) = ax.plot(
        [], [], "o-", color="green", lw=6, markersize=18, zorder=4
    )
    # Início e fim
    ax.plot(
        sala_pos[inicio.sala][0],
        sala_pos[inicio.sala][1],
        "o",
        color="blue",
        markersize=22,
        label="Início",
        zorder=5,
    )
    ax.plot(
        sala_pos[fim.sala][0],
        sala_pos[fim.sala][1],
        "o",
        color="red",
        markersize=22,
        label="Saída",
        zorder=5,
    )
    ax.set_xlim(-1, 3.5)
    ax.set_ylim(-1.5, 6)
    ax.axis("off")
    ax.legend(loc="upper right")
    passos = []
    if caminho:
        for i, node in enumerate(caminho):
            msg = f"Passo {i+1}: Sala {node.sala+1}"
            if i > 0:
                prev = caminho[i - 1]
                for edge in amostra.vizinhos(prev):
                    if edge.destino == node:
                        eventos = []
                        if edge.tipo == "porta" and edge.bloqueada:
                            eventos.append("Porta bloqueada (15%)")
                        if edge.tipo == "porta" and edge.fumaca:
                            eventos.append("Fumaça no corredor (30%, custo 5)")
                        if edge.tipo == "porta" and edge.fumaca_toxica:
                            eventos.append("Fumaça tóxica (30%, custo dobrado)")
                        if edge.tipo == "escada" and edge.escada_congestionada:
                            eventos.append("Escada congestionada (20%, custo dobrado)")
                        if eventos:
                            msg += " | " + " | ".join(eventos)
            passos.append(msg)
    else:
        passos = ["Nenhum caminho disponível!"]

    def update(frame):
        if not caminho:
            status.set_text(passos[0])
            return (caminho_plot,)
        caminho_plot.set_data(*zip(*caminho_coords[: frame + 1]))
        status.set_text(passos[frame])
        return caminho_plot, status

    ani = animation.FuncAnimation(
        fig, update, frames=len(passos), interval=1200, blit=True, repeat=False
    )
    plt.show()


# --------------------------------------
# Execução direta
# --------------------------------------

if __name__ == "__main__":
    print("=== SIMULADOR DE RESGATE EM PRÉDIO ===")
    print("Cenário: Busca de caminho de resgate com animação")
    
    # Importar animação
    try:
        from animacao import AnimadorResgate
        ANIMACAO_DISPONIVEL = True
        print("✅ Animação disponível!")
    except ImportError as e:
        print(f"⚠️ Animação não disponível: {e}")
        print("Instale matplotlib com: pip install matplotlib")
        ANIMACAO_DISPONIVEL = False
    
    # Importar visualização estática
    try:
        from visualizacao import VisualizadorPredio
        VISUALIZACAO_DISPONIVEL = True
        print("✅ Visualização gráfica disponível!")
    except ImportError as e:
        print(f"⚠️ Visualização não disponível: {e}")
        VISUALIZACAO_DISPONIVEL = False
    
    # Configuração
    print(f"Prédio: {NUM_ANDARES} andares, {SALAS_POR_ANDAR} salas por andar")
    print(f"Total de salas: {NUM_ANDARES * SALAS_POR_ANDAR}")
    
    # Criar estruturas
    base = PredioGrafo(NUM_ANDARES, SALAS_POR_ANDAR)
    amostra = AmostraGrafo(base, seed=42)
    
    # Definir cenário de resgate
    origem = Node(1, 1)  # Entrada do prédio
    destino = Node(NUM_ANDARES, SALAS_POR_ANDAR)  # Sala 12 do último andar
    
    print(f"\n🎯 Cenário de Resgate:")
    print(f"Origem: {origem} (entrada do prédio)")
    print(f"Destino: {destino} (sala de escape)")
    
    # Visualizações estáticas
    if VISUALIZACAO_DISPONIVEL:
        print("\n🎨 Gerando visualizações estáticas...")
        vis = VisualizadorPredio()
        
        # Estrutura base
        fig1 = vis.visualizar_estrutura_base(base)
        fig1.savefig('estrutura_base.png', dpi=300, bbox_inches='tight')
        print("💾 Salvo: estrutura_base.png")
        
        # Amostra com incertezas
        fig2 = vis.visualizar_amostra(amostra)
        fig2.savefig('amostra_incertezas.png', dpi=300, bbox_inches='tight')
        print("💾 Salvo: amostra_incertezas.png")
    
    # Executar algoritmos de busca
    print("\n🔍 Executando algoritmos de busca...")
    
    # BFS
    print("🔍 BFS - Busca em Largura...")
    caminho_bfs = bfs(origem, destino, amostra.adj)
    if caminho_bfs:
        custo_bfs = caminho_custo(caminho_bfs, amostra.adj)
        print(f"✅ BFS encontrou caminho: {len(caminho_bfs)} passos, custo {custo_bfs:.1f}")
    else:
        print("❌ BFS não encontrou caminho")
    
    # Dijkstra
    print("⚡ Dijkstra - Menor Custo...")
    custo_dijkstra, caminho_dijkstra = dijkstra(origem, destino, amostra.adj)
    if caminho_dijkstra:
        print(f"✅ Dijkstra encontrou caminho: {len(caminho_dijkstra)} passos, custo {custo_dijkstra:.1f}")
    else:
        print("❌ Dijkstra não encontrou caminho")
    
    # Comparação
    if caminho_bfs and caminho_dijkstra:
        print(f"\n📊 Comparação:")
        print(f"BFS:      {len(caminho_bfs)} passos, custo {custo_bfs:.1f}")
        print(f"Dijkstra: {len(caminho_dijkstra)} passos, custo {custo_dijkstra:.1f}")
        diferenca_custo = custo_bfs - custo_dijkstra
        if diferenca_custo > 0:
            print(f"💡 Dijkstra economizou {diferenca_custo:.1f} pontos de custo!")
    
    # Animação
    if ANIMACAO_DISPONIVEL:
        print(f"\n🎬 Iniciando animação...")
        resposta = input("Deseja ver a animação? (s/n): ").lower().strip()
        
        if resposta in ['s', 'sim', 'y', 'yes', '']:
            print("🎬 Carregando animação...")
            animador = AnimadorResgate(amostra, largura=16, altura=10)
            
            try:
                if caminho_bfs or caminho_dijkstra:
                    print("🎬 Animando comparação entre algoritmos...")
                    animador.animar_comparacao(caminho_bfs, caminho_dijkstra, delay=0.8)
                else:
                    print("❌ Nenhum caminho encontrado para animar")
                
                # Salvar frames finais
                animador.salvar_frame('simulacao_final.png')
                
            except Exception as e:
                print(f"❌ Erro na animação: {e}")
            finally:
                animador.fechar()
                print("🎬 Animação finalizada")
        else:
            print("⏭️ Animação pulada")
    
    # Simulações estatísticas
    print(f"\n📈 Executando simulações estatísticas...")
    resultados = simular(n_execucoes=50)
    estatisticas = resumo(resultados)
    
    print("\n📊 Resultados Estatísticos:")
    for chave, valor in estatisticas.items():
        if isinstance(valor, float):
            print(f"{chave}: {valor:.2f}")
        else:
            print(f"{chave}: {valor}")
    
    print("\n✅ Simulação concluída!")
