# -*- coding: utf-8 -*-
"""
Módulo contendo a classe AmostraGrafo que aplica incertezas estocásticas
"""

from typing import Dict, Tuple, List, Optional
import random
from collections import defaultdict
from .node import Node
from .predio_grafo import PredioGrafo

# Importa configurações
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    CUSTO_LIVRE,
    CUSTO_FUMACA,
    P_PORTA_BLOQUEADA,
    P_CORREDOR_FUMACA,
    P_ESCADA_CONGESTIONADA,
    SEMENTE,
)


class AmostraGrafo:
    """
    Um "snapshot" de uma simulação com incertezas aplicadas
    - remove portas bloqueadas
    - ajusta custo do corredor conforme fumaça
    - ajusta custo da escada conforme congestionamento
    """

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
            if e.tipo in ("porta_par", "porta_impar"):
                # 15% de chance de ficar indisponível (aresta removida)
                if random.random() < P_PORTA_BLOQUEADA:
                    continue  # remove
                custo = CUSTO_LIVRE  # portas sem fumaça; custo fixo se existir
            elif e.tipo == "corredor":
                # 30% chance de fumaça, custo 5; senão custo 1
                custo = (
                    CUSTO_FUMACA if random.random() < P_CORREDOR_FUMACA else CUSTO_LIVRE
                )
            elif e.tipo == "escada":
                # 20% chance de congestionamento, dobra custo
                custo = (
                    CUSTO_LIVRE * 2
                    if random.random() < P_ESCADA_CONGESTIONADA
                    else CUSTO_LIVRE
                )
            else:
                custo = e.custo

            self.adj[e.u].append((e.v, float(custo)))
