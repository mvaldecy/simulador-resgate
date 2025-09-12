# -*- coding: utf-8 -*-
"""
Módulo contendo a definição do nó do grafo
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    """Um nó é identificado por (andar, sala)."""

    andar: int
    sala: int

    def __str__(self) -> str:
        return f"A{self.andar}:S{self.sala}"
