# -*- coding: utf-8 -*-
"""
Módulo de animação para o simulador de resgate
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from typing import List, Dict, Tuple, Optional
import time
import os

from structures.node import Node
from structures.amostra_grafo import AmostraGrafo
from config import NUM_ANDARES, SALAS_POR_ANDAR


class AnimadorResgate:
    """Classe para animar a simulação de resgate."""
    
    def __init__(self, amostra: AmostraGrafo, largura=18, altura=12):
        self.amostra = amostra
        
        # Criar subplots - principal e legenda
        self.fig = plt.figure(figsize=(largura, altura))
        self.ax_main = plt.subplot2grid((4, 3), (0, 0), colspan=2, rowspan=4)
        self.ax_legend = plt.subplot2grid((4, 3), (0, 2), rowspan=2)
        self.ax_info = plt.subplot2grid((4, 3), (2, 2), rowspan=2)
        
        self.positions = self._calcular_posicoes()
        self.caminho_atual = []
        self.passo_atual = 0
        
        # Configurar plot principal
        plt.ion()  # Modo interativo
        self._configurar_plot_principal()
        self._configurar_legenda()
        self._configurar_informacoes()
    
    def _configurar_plot_principal(self):
        """Configura o plot principal."""
        self.ax_main.set_xlim(-1, SALAS_POR_ANDAR)
        self.ax_main.set_ylim(-1, NUM_ANDARES)
        self.ax_main.set_xlabel('Salas (1-12)', fontsize=12)
        self.ax_main.set_ylabel('Andares (1-7)', fontsize=12)
        self.ax_main.set_title('🔥 SIMULAÇÃO DE RESGATE EM PRÉDIO 🔥', fontsize=14, fontweight='bold')
        self.ax_main.grid(True, alpha=0.3)
        
        # Adicionar labels dos andares
        for andar in range(1, NUM_ANDARES + 1):
            y = NUM_ANDARES - andar
            self.ax_main.text(-0.5, y, f'A{andar}', ha='center', va='center', 
                            fontweight='bold', fontsize=10)
    
    def _configurar_legenda(self):
        """Configura a legenda visual."""
        self.ax_legend.set_xlim(0, 1)
        self.ax_legend.set_ylim(0, 1)
        self.ax_legend.axis('off')
        self.ax_legend.set_title('🗂️ LEGENDA', fontweight='bold', fontsize=12)
        
        # Elementos da legenda
        legenda_items = [
            ('🟢', 'Sala Livre'),
            ('🔴', 'Porta Bloqueada'),
            ('🟡', 'Corredor com Fumaça'),
            ('🟠', 'Escada Congestionada'),
            ('🔵', 'Posição Atual'),
            ('🎯', 'Destino (A7:S12)'),
            ('🚪', 'Entrada (A1:S1)'),
            ('━━', 'Caminho Percorrido')
        ]
        
        y_pos = 0.9
        for emoji, descricao in legenda_items:
            self.ax_legend.text(0.05, y_pos, f'{emoji} {descricao}', 
                              fontsize=10, va='center')
            y_pos -= 0.11
    
    def _configurar_informacoes(self):
        """Configura o painel de informações."""
        self.ax_info.set_xlim(0, 1)
        self.ax_info.set_ylim(0, 1)
        self.ax_info.axis('off')
        self.ax_info.set_title('📋 REGRAS DE RESGATE', fontweight='bold', fontsize=12)
        
        regras = [
            '🔥 CENÁRIO: Prédio em chamas',
            '',
            '📏 ESTRUTURA:',
            '• 7 andares, 12 salas/andar',
            '• Salas ímpares conectadas',
            '• Salas pares conectadas', 
            '• Corredor liga todas as salas',
            '• Escadas na sala 6',
            '',
            '⚠️ INCERTEZAS:',
            '• 15% portas bloqueadas',
            '• 30% corredores com fumaça',
            '• 20% escadas congestionadas',
            '',
            '🎯 OBJETIVO:',
            '• Sair de A1:S1 → A7:S12',
            '• Encontrar melhor rota'
        ]
        
        y_pos = 0.95
        for regra in regras:
            if regra.startswith('📏') or regra.startswith('⚠️') or regra.startswith('🎯'):
                fontweight = 'bold'
            else:
                fontweight = 'normal'
                
            self.ax_info.text(0.05, y_pos, regra, fontsize=9, va='top', 
                            fontweight=fontweight)
            y_pos -= 0.055
    
    def _calcular_posicoes(self) -> Dict[Node, Tuple[float, float]]:
        """Calcula posições 2D para os nós."""
        positions = {}
        for andar in range(1, NUM_ANDARES + 1):
            for sala in range(1, SALAS_POR_ANDAR + 1):
                node = Node(andar, sala)
                x = sala - 1
                y = NUM_ANDARES - andar  # Inverter para andar 1 ficar em baixo
                positions[node] = (x, y)
        return positions
    
    def _desenhar_base(self):
        """Desenha a estrutura base do prédio."""
        self.ax_main.clear()
        self.ax_main.set_xlim(-1, SALAS_POR_ANDAR)
        self.ax_main.set_ylim(-1, NUM_ANDARES)
        self.ax_main.set_xlabel('Salas (1-12)', fontsize=12)
        self.ax_main.set_ylabel('Andares (1-7)', fontsize=12)
        self.ax_main.set_title('🔥 SIMULAÇÃO DE RESGATE EM PRÉDIO 🔥', fontsize=14, fontweight='bold')
        self.ax_main.grid(True, alpha=0.3)
        
        # Adicionar labels dos andares
        for andar in range(1, NUM_ANDARES + 1):
            y = NUM_ANDARES - andar
            self.ax_main.text(-0.5, y, f'A{andar}', ha='center', va='center', 
                            fontweight='bold', fontsize=10)
        
        # Desenhar salas com diferentes cores e símbolos
        for node, (x, y) in self.positions.items():
            # Determinar cor e símbolo baseado no tipo de sala
            if node.andar == 1 and node.sala == 1:
                # Entrada
                self.ax_main.scatter(x, y, c='green', s=300, marker='s', 
                                   edgecolors='black', linewidths=2, label='Entrada')
                self.ax_main.text(x, y-0.3, '🚪', ha='center', va='center', fontsize=12)
            elif node.andar == NUM_ANDARES and node.sala == SALAS_POR_ANDAR:
                # Destino
                self.ax_main.scatter(x, y, c='red', s=300, marker='*', 
                                   edgecolors='black', linewidths=2, label='Destino')
                self.ax_main.text(x, y-0.3, '🎯', ha='center', va='center', fontsize=12)
            elif node.sala == 6:
                # Escadas
                self.ax_main.scatter(x, y, c='orange', s=250, marker='^', 
                                   edgecolors='black', linewidths=1)
                self.ax_main.text(x, y-0.3, '🪜', ha='center', va='center', fontsize=10)
            elif node.sala % 2 == 0:
                # Salas pares
                self.ax_main.scatter(x, y, c='lightblue', s=200, alpha=0.8, 
                                   edgecolors='navy', linewidths=1)
            else:
                # Salas ímpares
                self.ax_main.scatter(x, y, c='lightgreen', s=200, alpha=0.8, 
                                   edgecolors='darkgreen', linewidths=1)
            
            # Adicionar número da sala
            self.ax_main.text(x, y, str(node.sala), ha='center', va='center', 
                            fontsize=8, fontweight='bold')
        
        # Desenhar conexões com diferentes estilos baseados no tipo
        self._desenhar_conexoes()
    
    def _desenhar_conexoes(self):
        """Desenha as conexões entre salas com estilos diferentes."""
        # Desenhar conexões
        for node in self.amostra.adj:
            x1, y1 = self.positions[node]
            for vizinho, custo in self.amostra.adj[node]:
                if vizinho in self.positions:
                    x2, y2 = self.positions[vizinho]
                    
                    # Estilo da linha baseado no custo e tipo de conexão
                    if custo == 1.0:
                        cor_linha = 'green'
                        alpha = 0.6
                        linewidth = 1
                        linestyle = '-'
                    elif custo == 2.0:
                        cor_linha = 'orange'  # Escada congestionada
                        alpha = 0.8
                        linewidth = 2
                        linestyle = '--'
                    elif custo == 5.0:
                        cor_linha = 'red'  # Fumaça
                        alpha = 0.8
                        linewidth = 2
                        linestyle = ':'
                    else:
                        cor_linha = 'gray'
                        alpha = 0.4
                        linewidth = 1
                        linestyle = '-'
                    
                    # Desenhar apenas se não for muito próximo (evitar sobreposição)
                    if abs(x1-x2) + abs(y1-y2) <= 2:  # Conexões próximas apenas
                        self.ax_main.plot([x1, x2], [y1, y2], color=cor_linha, alpha=alpha, 
                                        linewidth=linewidth, linestyle=linestyle)
    
    def animar_caminho(self, caminho: List[Node], titulo: str = "Simulação de Resgate", delay: float = 1.0):
        """Anima um caminho específico."""
        self._desenhar_base()
        
        if not caminho:
            self.ax_main.text(SALAS_POR_ANDAR/2, NUM_ANDARES/2, '❌ CAMINHO NÃO ENCONTRADO!', 
                            ha='center', va='center', fontsize=16, color='red', 
                            fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow"))
            plt.tight_layout()
            plt.pause(3)
            return
        
        # Adicionar informações de progresso
        self.ax_main.text(SALAS_POR_ANDAR/2, NUM_ANDARES + 0.5, 
                        f'🚨 {titulo} - {len(caminho)} passos', 
                        ha='center', va='center', fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        plt.tight_layout()
        plt.pause(delay)
        
        # Animar cada passo do caminho
        for i, node in enumerate(caminho):
            x, y = self.positions[node]
            
            # Destacar posição atual
            self.ax_main.scatter(x, y, c='blue', s=400, marker='o', alpha=0.8, 
                               edgecolors='navy', linewidths=3, zorder=10)
            self.ax_main.text(x, y-0.5, '👤', ha='center', va='center', fontsize=16, zorder=11)
            
            # Desenhar rastro do caminho
            if i > 0:
                prev_node = caminho[i-1]
                x_prev, y_prev = self.positions[prev_node]
                self.ax_main.plot([x_prev, x], [y_prev, y], 'b-', linewidth=4, alpha=0.7, zorder=5)
                
                # Adicionar seta indicando direção
                dx, dy = x - x_prev, y - y_prev
                self.ax_main.annotate('', xy=(x, y), xytext=(x_prev, y_prev),
                                    arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            
            # Atualizar informações de progresso
            progresso = f'Passo {i+1}/{len(caminho)} - Atual: {node}'
            self.ax_main.text(SALAS_POR_ANDAR/2, -0.8, progresso, 
                            ha='center', va='center', fontsize=10, 
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
            
            plt.tight_layout()
            plt.pause(delay)
        
        # Marcar chegada ao destino
        destino = caminho[-1]
        x_dest, y_dest = self.positions[destino]
        self.ax_main.scatter(x_dest, y_dest, c='gold', s=500, marker='*', 
                           edgecolors='red', linewidths=3, zorder=12)
        self.ax_main.text(x_dest, y_dest-0.7, '🏁', ha='center', va='center', fontsize=20, zorder=13)
        
        self.ax_main.text(SALAS_POR_ANDAR/2, -0.8, 
                        f'✅ RESGATE CONCLUÍDO! Caminho: {len(caminho)} passos', 
                        ha='center', va='center', fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
        
        plt.tight_layout()
        plt.pause(delay * 2)
    
    def _calcular_custo_caminho(self, caminho: List[Node]) -> float:
        """Calcula o custo total de um caminho."""
        if len(caminho) <= 1:
            return 0.0
        
        custo_total = 0.0
        for i in range(len(caminho) - 1):
            atual = caminho[i]
            proximo = caminho[i + 1]
            
            # Buscar custo na adjacência
            for vizinho, custo in self.amostra.adj.get(atual, []):
                if vizinho == proximo:
                    custo_total += custo
                    break
        
        return custo_total
    
    def animar_comparacao(self, caminho_bfs: List[Node], caminho_dijkstra: List[Node], delay: float = 1.0):
        """Anima uma comparação entre BFS e Dijkstra."""
        # Primeira animação: BFS
        if caminho_bfs:
            self.animar_caminho(caminho_bfs, "🔍 BFS - Busca em Largura", delay)
            time.sleep(2)
        
        # Segunda animação: Dijkstra
        if caminho_dijkstra:
            self.animar_caminho(caminho_dijkstra, "⚡ Dijkstra - Menor Custo", delay)
            time.sleep(2)
        
        # Comparação final
        self._desenhar_comparacao_final(caminho_bfs, caminho_dijkstra)
    
    def _desenhar_comparacao_final(self, caminho_bfs: List[Node], caminho_dijkstra: List[Node]):
        """Desenha comparação final entre os dois algoritmos."""
        self._desenhar_base()
        
        if caminho_bfs:
            # Desenhar caminho BFS
            x_bfs = [self.positions[node][0] for node in caminho_bfs]
            y_bfs = [self.positions[node][1] for node in caminho_bfs]
            self.ax_main.plot(x_bfs, y_bfs, 'g-', linewidth=4, alpha=0.8, 
                            label=f'🔍 BFS ({len(caminho_bfs)} passos)')
        
        if caminho_dijkstra:
            # Desenhar caminho Dijkstra
            x_dij = [self.positions[node][0] for node in caminho_dijkstra]
            y_dij = [self.positions[node][1] for node in caminho_dijkstra]
            self.ax_main.plot(x_dij, y_dij, 'purple', linewidth=4, alpha=0.8, linestyle='--', 
                            label=f'⚡ Dijkstra ({len(caminho_dijkstra)} passos)')
        
        # Marcar origem e destino
        if caminho_bfs or caminho_dijkstra:
            caminho_ref = caminho_bfs if caminho_bfs else caminho_dijkstra
            origem = caminho_ref[0]
            destino = caminho_ref[-1]
            
            x_orig, y_orig = self.positions[origem]
            x_dest, y_dest = self.positions[destino]
            
            self.ax_main.scatter(x_orig, y_orig, c='blue', s=500, marker='s', 
                               label='🚪 Entrada', edgecolors='black', linewidths=2)
            self.ax_main.scatter(x_dest, y_dest, c='red', s=500, marker='*', 
                               label='🎯 Destino', edgecolors='black', linewidths=2)
        
        # Adicionar estatísticas
        stats_text = ""
        if caminho_bfs:
            custo_bfs = self._calcular_custo_caminho(caminho_bfs)
            stats_text += f"🔍 BFS: {len(caminho_bfs)} passos, custo {custo_bfs:.1f}\n"
        if caminho_dijkstra:
            custo_dij = self._calcular_custo_caminho(caminho_dijkstra)
            stats_text += f"⚡ Dijkstra: {len(caminho_dijkstra)} passos, custo {custo_dij:.1f}"
        
        self.ax_main.text(SALAS_POR_ANDAR/2, -1.2, stats_text, 
                        ha='center', va='center', fontsize=11, 
                        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow"))
        
        self.ax_main.legend(loc='upper right')
        plt.tight_layout()
        plt.pause(5)
    
    def salvar_frame(self, nome_arquivo: str):
        """Salva o frame atual."""
        plt.savefig(nome_arquivo, dpi=150, bbox_inches='tight')
        print(f"💾 Frame salvo: {nome_arquivo}")
    
    def fechar(self):
        """Fecha a animação."""
        plt.ioff()
        plt.close(self.fig)


def demo_animacao():
    """Demonstração da animação."""
    from structures.predio_grafo import PredioGrafo
    
    print("🎬 Iniciando demonstração da animação...")
    
    # Criar estrutura
    predio = PredioGrafo(NUM_ANDARES, SALAS_POR_ANDAR)
    amostra = AmostraGrafo(predio, seed=42)
    
    # Criar animador
    animador = AnimadorResgate(amostra)
    
    # Definir origem e destino
    origem = Node(1, 1)
    destino = Node(NUM_ANDARES, SALAS_POR_ANDAR)
    
    print(f"🎯 Origem: {origem}, Destino: {destino}")
    
    try:
        # Importar algoritmos
        from resgate_simulacao import bfs, dijkstra
        
        # Executar buscas
        print("🔍 Executando BFS...")
        caminho_bfs = bfs(origem, destino, amostra.adj)
        
        print("⚡ Executando Dijkstra...")
        custo_dij, caminho_dijkstra = dijkstra(origem, destino, amostra.adj)
        
        # Animar
        print("🎬 Iniciando animação...")
        animador.animar_comparacao(caminho_bfs, caminho_dijkstra, delay=0.8)
        
        # Salvar frame final
        animador.salvar_frame("resgate_comparacao.png")
        
        print("✅ Demonstração concluída!")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("Pressione Enter para fechar...")
        animador.fechar()


if __name__ == "__main__":
    demo_animacao()
