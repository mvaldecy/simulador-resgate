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
		for andar in range(self.andares):
			for sala in range(self.salas):
				atual = Node(andar, sala)
				# Ligações horizontais
				if sala < self.salas - 1:
					vizinho = Node(andar, sala + 1)
					self.grafo[atual].append(Edge(vizinho, 'porta', 1))
					self.grafo[vizinho].append(Edge(atual, 'porta', 1))
				# Ligações verticais (escadas)
				if andar < self.andares - 1:
					vizinho = Node(andar + 1, sala)
					self.grafo[atual].append(Edge(vizinho, 'escada', 2))
					self.grafo[vizinho].append(Edge(atual, 'escada', 2))
	def vizinhos(self, node: Node):
		return self.grafo[node]

class AmostraGrafo:
	def __init__(self, base: PredioGrafo):
		self.andares = base.andares
		self.salas = base.salas
		self.grafo: Dict[Node, List[Edge]] = defaultdict(list)
		self._amostrar(base)
	def _amostrar(self, base: PredioGrafo):
		for node, edges in base.grafo.items():
			for edge in edges:
				novo = Edge(edge.destino, edge.tipo, edge.custo)
				# Incertezas
				if edge.tipo == 'porta':
					if random.random() < 0.15:
						novo.bloqueada = True
				if edge.tipo == 'porta' and not novo.bloqueada:
					if random.random() < 0.3:
						novo.fumaca = True
					if random.random() < 0.3:
						novo.fumaca_toxica = True
				if edge.tipo == 'escada':
					if random.random() < 0.2:
						novo.escada_congestionada = True
				self.grafo[node].append(novo)
	def vizinhos(self, node: Node):
		return self.grafo[node]

def bfs(grafo, inicio: Node, fim: Node):
	fila = deque([(inicio, [inicio])])
	visitados = set()
	while fila:
		atual, caminho = fila.popleft()
		if atual == fim:
			return caminho
		visitados.add(atual)
		for edge in grafo.vizinhos(atual):
			if edge.bloqueada:
				continue
			if edge.destino not in visitados:
				fila.append((edge.destino, caminho + [edge.destino]))
	return None

def dijkstra(grafo, inicio: Node, fim: Node):
	heap = [(0, inicio, [inicio])]
	visitados = set()
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

def caminho_custo(grafo, caminho):
	custo = 0
	for i in range(len(caminho) - 1):
		for edge in grafo.vizinhos(caminho[i]):
			if edge.destino == caminho[i+1]:
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

def simular(base, inicio, fim, algoritmo='dijkstra'):
	amostra = AmostraGrafo(base)
	if algoritmo == 'bfs':
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
		ax.plot(x, y, 's', color='lightgrey', markersize=120, zorder=1)
		ax.text(x, y, str(s+1), fontsize=16, ha='center', va='center', fontweight='bold', color='black', zorder=2)
	# Desenha o corredor
	for y in range(6):
		ax.plot(1, y, 's', color='white', markersize=120, zorder=0, alpha=0.01)
	ax.text(1, 2.5, 'CORREDOR', fontsize=12, ha='center', va='center', rotation=90, color='gray', zorder=0)
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
			cor = 'black'
			lw = 2
			label = ''
			if edge.tipo == 'porta' and edge.bloqueada:
				cor = 'red'
				lw = 3
				label = 'Porta bloqueada'
			elif edge.tipo == 'porta' and edge.fumaca_toxica:
				cor = 'purple'
				label = 'Fumaça tóxica'
			elif edge.tipo == 'porta' and edge.fumaca:
				cor = 'orange'
				label = 'Fumaça'
			elif edge.tipo == 'escada' and edge.escada_congestionada:
				cor = 'blue'
				lw = 3
				label = 'Escada congestionada'
			ax.plot([x1, x2], [y1, y2], color=cor, lw=lw, zorder=0)
	# Escada (sala 6)
	ax.plot(2, 0, marker=(3, 0, 0), color='black', markersize=40, zorder=3)
	ax.text(2.2, 0, 'ESCADA', fontsize=10, ha='left', va='center', color='black', zorder=3)
	# Status box
	status = ax.text(-0.5, -1.2, '', fontsize=12, va='top', ha='left', bbox=dict(facecolor='white', alpha=0.8))
	regras = ax.text(2.7, 5.5, resumo(), fontsize=10, va='top', ha='left', bbox=dict(facecolor='white', alpha=0.7))
	# Caminho
	caminho_coords = [(sala_pos[node.sala][0], sala_pos[node.sala][1]) for node in caminho] if caminho else []
	caminho_plot, = ax.plot([], [], 'o-', color='green', lw=6, markersize=18, zorder=4)
	# Início e fim
	ax.plot(sala_pos[inicio.sala][0], sala_pos[inicio.sala][1], 'o', color='blue', markersize=22, label='Início', zorder=5)
	ax.plot(sala_pos[fim.sala][0], sala_pos[fim.sala][1], 'o', color='red', markersize=22, label='Saída', zorder=5)
	ax.set_xlim(-1, 3.5)
	ax.set_ylim(-1.5, 6)
	ax.axis('off')
	ax.legend(loc='upper right')
	passos = []
	if caminho:
		for i, node in enumerate(caminho):
			msg = f"Passo {i+1}: Sala {node.sala+1}"
			if i > 0:
				prev = caminho[i-1]
				for edge in amostra.vizinhos(prev):
					if edge.destino == node:
						eventos = []
						if edge.tipo == 'porta' and edge.bloqueada:
							eventos.append('Porta bloqueada (15%)')
						if edge.tipo == 'porta' and edge.fumaca:
							eventos.append('Fumaça no corredor (30%, custo 5)')
						if edge.tipo == 'porta' and edge.fumaca_toxica:
							eventos.append('Fumaça tóxica (30%, custo dobrado)')
						if edge.tipo == 'escada' and edge.escada_congestionada:
							eventos.append('Escada congestionada (20%, custo dobrado)')
						if eventos:
							msg += ' | ' + ' | '.join(eventos)
			passos.append(msg)
	else:
		passos = ["Nenhum caminho disponível!"]
	def update(frame):
		if not caminho:
			status.set_text(passos[0])
			return caminho_plot,
		caminho_plot.set_data(*zip(*caminho_coords[:frame+1]))
		status.set_text(passos[frame])
		return caminho_plot, status
	ani = animation.FuncAnimation(fig, update, frames=len(passos), interval=1200, blit=True, repeat=False)
	plt.show()

# --------------------------------------
# Execução direta
# --------------------------------------

if __name__ == "__main__":
	base = PredioGrafo()
	inicio = Node(0, 0)
	fim = Node(0, 11)
	num_simulacoes = 10  # Altere para quantas execuções quiser
	resultados = []
	for i in range(num_simulacoes):
		print(f"\nSimulação {i+1}/{num_simulacoes}:")
		# Amostra única para ambos algoritmos
		amostra = AmostraGrafo(base)
		# Dijkstra
		caminho_dij, custo_dij = dijkstra(amostra, inicio, fim)
		# BFS
		caminho_bfs = bfs(amostra, inicio, fim)
		custo_bfs = caminho_custo(amostra, caminho_bfs) if caminho_bfs else float('inf')
		print(f"Dijkstra: {[str(n) for n in caminho_dij] if caminho_dij else 'Nenhum'} | Custo: {custo_dij if caminho_dij else 'Infinito'}")
		print(f"BFS: {[str(n) for n in caminho_bfs] if caminho_bfs else 'Nenhum'} | Custo: {custo_bfs if caminho_bfs else 'Infinito'}")
		resultados.append({
			'amostra': amostra,
			'caminho_dij': caminho_dij,
			'custo_dij': custo_dij,
			'caminho_bfs': caminho_bfs,
			'custo_bfs': custo_bfs
		})
		# Exibe animação apenas para a primeira simulação
		if i == 0:
			print("\nExibindo animação da primeira simulação (Dijkstra):")
			animar_caminho_detalhado(base, amostra, caminho_dij, inicio, fim, custo_dij)
	# Relatório comparativo
	print("\nResumo comparativo após", num_simulacoes, "execuções:")
	melhor_bfs = 0
	melhor_dij = 0
	empate = 0
	sem_caminho = 0
	for r in resultados:
		if not r['caminho_bfs'] and not r['caminho_dij']:
			sem_caminho += 1
		elif r['custo_bfs'] < r['custo_dij']:
			melhor_bfs += 1
		elif r['custo_dij'] < r['custo_bfs']:
			melhor_dij += 1
		else:
			empate += 1
	print(f"- BFS encontrou caminho mais curto em {melhor_bfs} execuções.")
	print(f"- Dijkstra encontrou caminho mais curto em {melhor_dij} execuções.")
	print(f"- Ambos empataram em {empate} execuções.")
	print(f"- Nenhum caminho possível em {sem_caminho} execuções.")
	print("\nObservação: Dijkstra sempre encontra o menor custo, mas BFS pode empatar se não houver custos diferenciados ou bloqueios relevantes.")
