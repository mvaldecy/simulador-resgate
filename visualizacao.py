# -*- coding: utf-8 -*-
"""
Módulo de visualização gráfica para o simulador de resgate
"""

import matplotlib
matplotlib.use('Agg')  # Backend sem display para salvar arquivos
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from typing import List, Dict, Tuple, Optional
from structures.node import Node
from structures.predio_grafo import PredioGrafo
from structures.amostra_grafo import AmostraGrafo
from config import NUM_ANDARES, SALAS_POR_ANDAR

class VisualizadorPredio:
    """Visualiza a estrutura do prédio e simulações de resgate."""
    
    def __init__(self, predio: PredioGrafo, figsize=(14, 10)):
        self.predio = predio
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.node_positions = self._calcular_posicoes_nodes()
        self.setup_plot()
        
    def _calcular_posicoes_nodes(self) -> Dict[Node, Tuple[float, float]]:
        """Calcula posições x,y para cada nó do grafo."""
        positions = {}
        
        # Layout: salas lado a lado, andares empilhados
        sala_width = 1.0
        andar_height = 1.5
        
        for node in self.predio.nodes:
            x = (node.sala - 1) * sala_width
            y = (node.andar - 1) * andar_height
            positions[node] = (x, y)
            
        return positions
    
    def setup_plot(self):
        """Configura o plot básico."""
        self.ax.set_xlim(-0.5, SALAS_POR_ANDAR - 0.5)
        self.ax.set_ylim(-0.5, NUM_ANDARES * 1.5)
        self.ax.set_aspect('equal')
        self.ax.set_title('Simulador de Resgate - Estrutura do Prédio', fontsize=16, fontweight='bold')
        self.ax.set_xlabel('Salas', fontsize=12)
        self.ax.set_ylabel('Andares', fontsize=12)
        
        # Grid
        self.ax.grid(True, alpha=0.3)
        
        # Labels dos andares
        for andar in range(1, NUM_ANDARES + 1):
            self.ax.text(-1, (andar - 1) * 1.5, f'Andar {andar}', 
                        ha='center', va='center', fontweight='bold')
        
        # Labels das salas
        for sala in range(1, SALAS_POR_ANDAR + 1):
            self.ax.text(sala - 1, -1, f'S{sala}', 
                        ha='center', va='center', fontweight='bold')
    
    def desenhar_estrutura_base(self):
        """Desenha a estrutura base do prédio."""
        self.ax.clear()
        self.setup_plot()
        
        # Desenhar nós (salas)
        for node in self.predio.nodes:
            x, y = self.node_positions[node]
            
            # Cor diferente para salas pares e ímpares
            color = 'lightblue' if node.sala % 2 == 0 else 'lightcoral'
            
            # Destacar sala 6 (escadas)
            if node.sala == 6:
                color = 'gold'
                
            circle = plt.Circle((x, y), 0.15, color=color, ec='black', linewidth=2)
            self.ax.add_patch(circle)
            
            # Label do nó
            self.ax.text(x, y, f'{node.sala}', ha='center', va='center', 
                        fontweight='bold', fontsize=8)
        
        # Desenhar arestas
        self._desenhar_arestas_base()
        
        # Legenda
        self._adicionar_legenda_base()
        
        plt.tight_layout()
        return self.fig
    
    def _desenhar_arestas_base(self):
        """Desenha as arestas da estrutura base."""
        for edge in self.predio.base_edges:
            x1, y1 = self.node_positions[edge.u]
            x2, y2 = self.node_positions[edge.v]
            
            # Cores e estilos por tipo de aresta
            if edge.tipo == 'porta_par':
                color, linestyle, alpha = 'blue', '-', 0.7
            elif edge.tipo == 'porta_impar':
                color, linestyle, alpha = 'red', '-', 0.7
            elif edge.tipo == 'escada':
                color, linestyle, alpha = 'orange', '-', 1.0
                linewidth = 3
            else:  # corredor
                color, linestyle, alpha = 'gray', ':', 0.3
                
            linewidth = 3 if edge.tipo == 'escada' else 1
            
            self.ax.plot([x1, x2], [y1, y2], color=color, linestyle=linestyle, 
                        alpha=alpha, linewidth=linewidth)
    
    def _adicionar_legenda_base(self):
        """Adiciona legenda para a estrutura base."""
        legend_elements = [
            plt.Line2D([0], [0], color='blue', lw=2, label='Portas Pares'),
            plt.Line2D([0], [0], color='red', lw=2, label='Portas Ímpares'),
            plt.Line2D([0], [0], color='orange', lw=3, label='Escadas'),
            plt.Line2D([0], [0], color='gray', lw=1, linestyle=':', label='Corredores'),
            plt.scatter([], [], c='lightblue', s=100, label='Salas Pares'),
            plt.scatter([], [], c='lightcoral', s=100, label='Salas Ímpares'),
            plt.scatter([], [], c='gold', s=100, label='Escadas (Sala 6)')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
    
    def visualizar_amostra(self, amostra: AmostraGrafo, seed: Optional[int] = None):
        """Visualiza uma amostra com incertezas aplicadas."""
        self.ax.clear()
        self.setup_plot()
        
        # Título com informação da semente
        title = 'Simulador de Resgate - Amostra com Incertezas'
        if seed is not None:
            title += f' (Semente: {seed})'
        self.ax.set_title(title, fontsize=16, fontweight='bold')
        
        # Desenhar nós
        for node in self.predio.nodes:
            x, y = self.node_positions[node]
            
            # Verificar se o nó tem conexões na amostra
            has_connections = node in amostra.adj and len(amostra.adj[node]) > 0
            
            if has_connections:
                color = 'lightblue' if node.sala % 2 == 0 else 'lightcoral'
                if node.sala == 6:
                    color = 'gold'
                alpha = 1.0
            else:
                color = 'gray'
                alpha = 0.3
                
            circle = plt.Circle((x, y), 0.15, color=color, alpha=alpha, 
                              ec='black', linewidth=1)
            self.ax.add_patch(circle)
            
            self.ax.text(x, y, f'{node.sala}', ha='center', va='center', 
                        fontweight='bold', fontsize=8)
        
        # Desenhar arestas da amostra
        self._desenhar_arestas_amostra(amostra)
        
        # Legenda para amostra
        self._adicionar_legenda_amostra()
        
        plt.tight_layout()
        return self.fig
    
    def _desenhar_arestas_amostra(self, amostra: AmostraGrafo):
        """Desenha as arestas da amostra com incertezas."""
        # Mapear arestas da amostra para tipos originais
        edge_map = {}
        for edge in self.predio.base_edges:
            key = (edge.u, edge.v)
            edge_map[key] = edge.tipo
        
        for u, vizinhos in amostra.adj.items():
            for v, custo in vizinhos:
                x1, y1 = self.node_positions[u]
                x2, y2 = self.node_positions[v]
                
                # Determinar tipo da aresta original
                edge_type = edge_map.get((u, v), 'corredor')
                
                # Cor baseada no custo e tipo
                if edge_type == 'escada':
                    color = 'darkorange' if custo > 1.0 else 'orange'
                    linewidth = 3
                elif custo >= 5.0:  # Fumaça
                    color = 'red'
                    linewidth = 2
                elif edge_type == 'porta_par':
                    color = 'blue'
                    linewidth = 1
                elif edge_type == 'porta_impar':
                    color = 'red'
                    linewidth = 1
                else:  # corredor normal
                    color = 'green'
                    linewidth = 1
                
                self.ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, alpha=0.7)
    
    def _adicionar_legenda_amostra(self):
        """Adiciona legenda para a amostra."""
        legend_elements = [
            plt.Line2D([0], [0], color='blue', lw=2, label='Portas Pares (Livres)'),
            plt.Line2D([0], [0], color='red', lw=2, label='Portas Ímpares/Fumaça'),
            plt.Line2D([0], [0], color='orange', lw=3, label='Escadas (Livre)'),
            plt.Line2D([0], [0], color='darkorange', lw=3, label='Escadas (Congestionada)'),
            plt.Line2D([0], [0], color='green', lw=1, label='Corredor (Livre)'),
            plt.Line2D([0], [0], color='gray', lw=1, label='Bloqueado/Inacessível')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
    
    def visualizar_caminho(self, amostra: AmostraGrafo, caminho: List[Node], 
                          titulo: str = "Caminho Encontrado", seed: Optional[int] = None):
        """Visualiza um caminho específico sobre a amostra."""
        # Primeiro desenha a amostra
        self.visualizar_amostra(amostra, seed)
        
        # Atualizar título
        self.ax.set_title(titulo, fontsize=16, fontweight='bold')
        
        if not caminho:
            self.ax.text(SALAS_POR_ANDAR/2, NUM_ANDARES*1.5/2, 'CAMINHO NÃO ENCONTRADO', 
                        ha='center', va='center', fontsize=20, color='red', 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))
            return self.fig
        
        # Destacar nós do caminho
        for i, node in enumerate(caminho):
            x, y = self.node_positions[node]
            
            if i == 0:  # Origem
                color, label = 'lime', 'INÍCIO'
                circle = plt.Circle((x, y), 0.2, color=color, ec='darkgreen', linewidth=3)
            elif i == len(caminho) - 1:  # Destino
                color, label = 'red', 'FIM'
                circle = plt.Circle((x, y), 0.2, color=color, ec='darkred', linewidth=3)
            else:  # Caminho intermediário
                color, label = 'yellow', ''
                circle = plt.Circle((x, y), 0.18, color=color, ec='orange', linewidth=2)
            
            self.ax.add_patch(circle)
            
            if label:
                self.ax.text(x, y-0.4, label, ha='center', va='center', 
                           fontweight='bold', fontsize=8)
        
        # Desenhar caminho
        for i in range(len(caminho) - 1):
            x1, y1 = self.node_positions[caminho[i]]
            x2, y2 = self.node_positions[caminho[i + 1]]
            
            self.ax.plot([x1, x2], [y1, y2], color='purple', linewidth=4, 
                        alpha=0.8, zorder=10)
            
            # Seta indicando direção
            dx, dy = x2 - x1, y2 - y1
            if abs(dx) > 0.1 or abs(dy) > 0.1:  # Só desenha seta se não for muito pequena
                self.ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                               arrowprops=dict(arrowstyle='->', color='purple', 
                                             lw=2, alpha=0.8), zorder=10)
        
        # Informações do caminho
        custo_total = self._calcular_custo_caminho(amostra, caminho)
        info_text = f'Passos: {len(caminho)-1}\nCusto Total: {custo_total:.1f}'
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes, 
                    va='top', ha='left', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
        
        plt.tight_layout()
        return self.fig
    
    def _calcular_custo_caminho(self, amostra: AmostraGrafo, caminho: List[Node]) -> float:
        """Calcula o custo total de um caminho."""
        if len(caminho) <= 1:
            return 0.0
        
        custo_total = 0.0
        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            
            # Buscar custo na adjacência
            if u in amostra.adj:
                for vizinho, custo in amostra.adj[u]:
                    if vizinho == v:
                        custo_total += custo
                        break
                else:
                    return float('inf')  # Caminho inválido
            else:
                return float('inf')  # Nó sem saída
        
        return custo_total
    
    def comparar_algoritmos(self, amostra: AmostraGrafo, caminho_bfs: List[Node], 
                           caminho_dijkstra: List[Node], seed: Optional[int] = None):
        """Compara visualmente os resultados de BFS e Dijkstra."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Configurar ambos os subplots
        for ax in [ax1, ax2]:
            ax.set_xlim(-0.5, SALAS_POR_ANDAR - 0.5)
            ax.set_ylim(-0.5, NUM_ANDARES * 1.5)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
        
        # BFS
        ax1.set_title('BFS (Busca em Largura)', fontsize=14, fontweight='bold')
        self._desenhar_comparacao(ax1, amostra, caminho_bfs, 'blue')
        
        # Dijkstra
        ax2.set_title('Dijkstra (Menor Custo)', fontsize=14, fontweight='bold')
        self._desenhar_comparacao(ax2, amostra, caminho_dijkstra, 'red')
        
        plt.tight_layout()
        return fig
    
    def _desenhar_comparacao(self, ax, amostra: AmostraGrafo, caminho: List[Node], cor_caminho: str):
        """Desenha um subplot para comparação de algoritmos."""
        # Desenhar nós
        for node in self.predio.nodes:
            x, y = self.node_positions[node]
            color = 'lightblue' if node.sala % 2 == 0 else 'lightcoral'
            if node.sala == 6:
                color = 'gold'
                
            circle = plt.Circle((x, y), 0.12, color=color, ec='black', linewidth=1)
            ax.add_patch(circle)
            ax.text(x, y, f'{node.sala}', ha='center', va='center', fontsize=6)
        
        # Desenhar arestas da amostra (simplificado)
        for u, vizinhos in amostra.adj.items():
            for v, custo in vizinhos:
                x1, y1 = self.node_positions[u]
                x2, y2 = self.node_positions[v]
                ax.plot([x1, x2], [y1, y2], color='gray', linewidth=0.5, alpha=0.3)
        
        # Desenhar caminho
        if caminho:
            for i in range(len(caminho) - 1):
                x1, y1 = self.node_positions[caminho[i]]
                x2, y2 = self.node_positions[caminho[i + 1]]
                ax.plot([x1, x2], [y1, y2], color=cor_caminho, linewidth=3, alpha=0.8)
            
            # Marcar início e fim
            x_inicio, y_inicio = self.node_positions[caminho[0]]
            x_fim, y_fim = self.node_positions[caminho[-1]]
            
            ax.scatter(x_inicio, y_inicio, c='green', s=200, marker='o', 
                      edgecolors='darkgreen', linewidth=2, zorder=10)
            ax.scatter(x_fim, y_fim, c='red', s=200, marker='s', 
                      edgecolors='darkred', linewidth=2, zorder=10)
            
            # Informações
            custo = self._calcular_custo_caminho(amostra, caminho)
            info = f'Passos: {len(caminho)-1}\nCusto: {custo:.1f}'
            ax.text(0.02, 0.98, info, transform=ax.transAxes, va='top', ha='left',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        else:
            ax.text(SALAS_POR_ANDAR/2, NUM_ANDARES*1.5/2, 'SEM CAMINHO', 
                   ha='center', va='center', fontsize=16, color='red')

def demonstracao_visualizacao():
    """Função de demonstração da visualização."""
    from structures.predio_grafo import PredioGrafo
    from structures.amostra_grafo import AmostraGrafo
    from config import NUM_ANDARES, SALAS_POR_ANDAR, SEMENTE
    
    # Criar estruturas
    predio = PredioGrafo(NUM_ANDARES, SALAS_POR_ANDAR)
    amostra = AmostraGrafo(predio, seed=SEMENTE)
    
    # Criar visualizador
    vis = VisualizadorPredio(predio)
    
    # 1. Estrutura base
    print("Gerando visualização da estrutura base...")
    fig1 = vis.desenhar_estrutura_base()
    fig1.savefig('estrutura_base.png', dpi=300, bbox_inches='tight')
    print("✅ Salvo: estrutura_base.png")
    
    # 2. Amostra com incertezas
    print("Gerando visualização da amostra...")
    fig2 = vis.visualizar_amostra(amostra, SEMENTE)
    fig2.savefig('amostra_incertezas.png', dpi=300, bbox_inches='tight')
    print("✅ Salvo: amostra_incertezas.png")
    
    plt.close('all')  # Fechar figuras para liberar memória
    print("🎨 Visualizações geradas com sucesso!")

if __name__ == "__main__":
    demonstracao_visualizacao()
