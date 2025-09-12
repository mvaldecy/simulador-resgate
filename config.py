# -*- coding: utf-8 -*-
"""
Configurações globais do simulador de resgate
"""

# -----------------------------
# Parâmetros do problema
# -----------------------------
NUM_ANDARES = 7
SALAS_POR_ANDAR = 12

# Custos base
CUSTO_LIVRE = 1.0
CUSTO_FUMACA = 5.0  # se houver fumaça no corredor

# Probabilidades de incerteza (por aresta por simulação)
P_PORTA_BLOQUEADA = 0.15  # portas entre pares e ímpares (horizontal "portas")
P_CORREDOR_FUMACA = 0.30  # corredor do andar pode ter fumaça entre quaisquer 2 salas
P_ESCADA_CONGESTIONADA = 0.20  # escada (vertical) dobra custo

# Semente para reprodutibilidade (ajuste/retire para aleatoriedade total)
SEMENTE = 42
