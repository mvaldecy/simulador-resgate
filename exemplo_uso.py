# -*- coding: utf-8 -*-
"""
Exemplo de uso das estruturas modularizadas do simulador de resgate
"""

from config import NUM_ANDARES, SALAS_POR_ANDAR, SEMENTE
from structures.node import Node
from structures.edge import Edge
from structures.predio_grafo import PredioGrafo
from structures.amostra_grafo import AmostraGrafo


def exemplo_basico():
    """Demonstra uso básico das estruturas."""
    print("=== Exemplo Básico das Estruturas ===")

    # 1. Criar um nó
    node1 = Node(1, 5)  # Andar 1, Sala 5
    print(f"Nó criado: {node1}")

    # 2. Criar uma aresta
    node2 = Node(1, 7)  # Andar 1, Sala 7
    edge = Edge(node1, node2, 1.0, "corredor")
    print(
        f"Aresta criada: {edge.u} -> {edge.v} (custo: {edge.custo}, tipo: {edge.tipo})"
    )

    # 3. Criar estrutura base do prédio
    predio = PredioGrafo(3, 6)  # 3 andares, 6 salas por andar
    print(
        f"Prédio criado com {len(predio.nodes)} nós e {len(predio.base_edges)} arestas"
    )

    # 4. Criar amostra com incertezas
    amostra = AmostraGrafo(predio, seed=42)
    print(f"Amostra criada com incertezas aplicadas")

    # 5. Verificar conectividade entre dois nós específicos
    origem = Node(1, 1)
    destino = Node(3, 6)

    if origem in amostra.adj and any(
        vizinho[0] == destino
        for vizinhos in amostra.adj.values()
        for vizinho in vizinhos
    ):
        print(f"Existe caminho direto ou indireto entre {origem} e {destino}")
    else:
        print(f"Verificando conectividade entre {origem} e {destino}...")

    # 6. Mostrar vizinhos de um nó específico
    if origem in amostra.adj:
        vizinhos = amostra.adj[origem]
        print(f"Vizinhos de {origem}: {len(vizinhos)} conexões")
        for vizinho, custo in vizinhos[:3]:  # Mostra apenas os 3 primeiros
            print(f"  -> {vizinho} (custo: {custo})")


def comparar_configuracoes():
    """Compara diferentes configurações de incerteza."""
    print("\n=== Comparação de Configurações ===")

    predio = PredioGrafo(NUM_ANDARES, SALAS_POR_ANDAR)

    # Simulação com diferentes sementes
    seeds = [42, 123, 999]

    for seed in seeds:
        amostra = AmostraGrafo(predio, seed=seed)
        total_arestas = sum(len(vizinhos) for vizinhos in amostra.adj.values())
        total_arestas_base = len(predio.base_edges)

        print(
            f"Semente {seed}: {total_arestas}/{total_arestas_base} arestas mantidas "
            f"({100*total_arestas/total_arestas_base:.1f}%)"
        )


def estatisticas_estrutura():
    """Mostra estatísticas da estrutura do prédio."""
    print("\n=== Estatísticas da Estrutura ===")

    predio = PredioGrafo(NUM_ANDARES, SALAS_POR_ANDAR)

    # Contar tipos de arestas
    tipos = {}
    for edge in predio.base_edges:
        tipos[edge.tipo] = tipos.get(edge.tipo, 0) + 1

    print(f"Total de nós: {len(predio.nodes)}")
    print(f"Total de arestas: {len(predio.base_edges)}")
    print("Distribuição por tipo:")
    for tipo, count in tipos.items():
        print(f"  {tipo}: {count} arestas")


if __name__ == "__main__":
    exemplo_basico()
    comparar_configuracoes()
    estatisticas_estrutura()
