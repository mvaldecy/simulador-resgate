# -*- coding: utf-8 -*-
"""
Módulo contendo a definição da aresta do grafo
"""

from dataclasses import dataclass
from .node import Node


@dataclass
class Edge:
    """Aresta direcionada com custo (não-negativo) e tipo."""

    u: Node
    v: Node
    custo: float
    tipo: str  # 'porta_par', 'porta_impar', 'corredor', 'escada'
