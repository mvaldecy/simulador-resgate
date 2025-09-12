# -*- coding: utf-8 -*-
"""
Módulo contendo a classe PredioGrafo que gera a estrutura base do prédio
"""

from typing import List
from .node import Node
from .edge import Edge

# Importa configurações
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CUSTO_LIVRE


class PredioGrafo:
    """Gera a estrutura base (sem incerteza aplicada)."""

    def __init__(self, num_andares: int, salas_por_andar: int):
        self.num_andares = num_andares
        self.salas_por_andar = salas_por_andar
        self.nodes: List[Node] = [
            Node(a, s)
            for a in range(1, num_andares + 1)
            for s in range(1, salas_por_andar + 1)
        ]
        self.base_edges: List[Edge] = []
        self._construir_arestas_base()

    def _construir_arestas_base(self):
        # 1) Portas entre pares: 2<->4, 4<->6, ..., 10<->12
        for andar in range(1, self.num_andares + 1):
            for s in range(2, self.salas_por_andar + 1, 2):
                if s + 2 <= self.salas_por_andar:
                    a = Node(andar, s)
                    b = Node(andar, s + 2)
                    self._add_bidirectional(a, b, CUSTO_LIVRE, "porta_par")

        # 2) Portas entre ímpares: 1<->3, 3<->5, ..., 9<->11
        for andar in range(1, self.num_andares + 1):
            for s in range(1, self.salas_por_andar, 2):
                if s + 2 <= self.salas_por_andar:
                    a = Node(andar, s)
                    b = Node(andar, s + 2)
                    self._add_bidirectional(a, b, CUSTO_LIVRE, "porta_impar")

        # 3) Corredor comum: conecta quaisquer duas salas do mesmo andar
        for andar in range(1, self.num_andares + 1):
            salas = list(range(1, self.salas_por_andar + 1))
            for i in range(len(salas)):
                for j in range(i + 1, len(salas)):
                    a = Node(andar, salas[i])
                    b = Node(andar, salas[j])
                    self._add_bidirectional(a, b, CUSTO_LIVRE, "corredor")

        # 4) Escadas: sala 6 de cada andar conecta com sala 6 do andar superior
        for andar in range(1, self.num_andares):
            a = Node(andar, 6)
            b = Node(andar + 1, 6)
            self._add_bidirectional(a, b, CUSTO_LIVRE, "escada")

    def _add_bidirectional(self, a: Node, b: Node, custo: float, tipo: str):
        self.base_edges.append(Edge(a, b, custo, tipo))
        self.base_edges.append(Edge(b, a, custo, tipo))
