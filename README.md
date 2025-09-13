# Simulador de Resgate em Prédio em Chamas

Simulação de resgate em prédio de 7 andares com 12 salas por andar, implementando algoritmos de busca (BFS e Dijkstra) com incertezas estocásticas.

## 🚀 Como Executar

### Execução Principal (Simulação + Animação)

```bash
python3 resgate_simulacao.py
```

**Este é o arquivo principal que você deve executar!**

- Executa simulações completas de resgate
- Gera animação visual do processo
- Compara algoritmos BFS vs Dijkstra
- Salva resultados em arquivos

### Exemplos Didáticos

```bash
python3 exemplo_uso.py
```

- Demonstra uso das estruturas individualmente
- Mostra estatísticas do prédio
- Compara diferentes configurações

### Visualização Estática

```bash
python3 visualizacao.py
```

- Gera mapas estáticos do prédio
- Mostra estrutura sem animação

### Apenas Animação

```bash
python3 animacao.py
```

- Executa demonstração da animação
- Útil para testar visualização

## 📁 Estrutura do Projeto

```
simulador-resgate/
├── 🎯 resgate_simulacao.py    # ← ARQUIVO PRINCIPAL
├── 📖 exemplo_uso.py          # Exemplos didáticos
├── 📊 visualizacao.py         # Visualização estática
├── 🎬 animacao.py             # Sistema de animação
├── ⚙️ config.py               # Configurações
├── structures/                # Estruturas modulares
│   ├── __init__.py
│   ├── node.py               # Classe Node
│   ├── edge.py               # Classe Edge
│   ├── predio_grafo.py       # Estrutura do prédio
│   └── amostra_grafo.py      # Aplicação de incertezas
├── 📋 README.md              # Este arquivo
└── 📄 resgate.pdf            # Especificação original
```

## 🎮 Funcionalidades

### 🏢 Estrutura do Prédio

- **7 andares** × **12 salas** por andar
- **Salas ímpares conectadas**: 1↔3, 3↔5, 5↔7, 7↔9, 9↔11
- **Salas pares conectadas**: 2↔4, 4↔6, 6↔8, 8↔10, 10↔12
- **Corredor**: conecta todas as salas do mesmo andar
- **Escadas**: na sala 6, conectam andares adjacentes

### 🎲 Incertezas Estocásticas

- **15%** de chance de portas bloqueadas
- **30%** de chance de corredores com fumaça (custo ×5)
- **20%** de chance de escadas congestionadas (custo ×2)

### 🔍 Algoritmos Implementados

- **BFS**: Busca em largura (não-informado)
- **Dijkstra**: Busca de menor custo (informado)

### 🎬 Visualização

- **Animação em tempo real** do progresso da busca
- **Legenda interativa** com regras de resgate
- **Métricas em tempo real** (custo, passos, tempo)
- **Comparação visual** entre algoritmos

## 📊 Saídas do Programa

### Arquivos Gerados

- `mapa_predio.png` - Visualização estática da estrutura
- `animacao_resgate.gif` - Animação do processo de resgate
- `animacao_resgate.mp4` - Vídeo da simulação

### Dados Exibidos

```
=== Resultados das Simulações ===
Algoritmo: BFS
├─ Taxa de Sucesso: 95.0%
├─ Custo Médio: 12.3
├─ Passos Médios: 8.7
└─ Tempo Médio: 0.002s

Algoritmo: Dijkstra
├─ Taxa de Sucesso: 98.0%
├─ Custo Médio: 9.8
├─ Passos Médios: 9.2
└─ Tempo Médio: 0.005s
```

## ⚙️ Configurações

Edite o arquivo `config.py` para modificar parâmetros:

```python
# Estrutura do prédio
NUM_ANDARES = 7
SALAS_POR_ANDAR = 12

# Probabilidades de incerteza
P_PORTA_BLOQUEADA = 0.15      # 15%
P_CORREDOR_FUMACA = 0.30      # 30%
P_ESCADA_CONGESTIONADA = 0.20 # 20%

# Custos
CUSTO_LIVRE = 1.0
CUSTO_FUMACA = 5.0
CUSTO_ESCADA = 2.0
```

## 🛠️ Requisitos

```bash
pip install matplotlib numpy
```

## 🎯 Cenários de Teste

### Cenário 1: Resgate Simples

```bash
# Entrada: Andar 0, Sala 1
# Destino: Andar 6, Sala 12
python3 resgate_simulacao.py
```

### Cenário 2: Múltiplas Vítimas

```python
# Modificar resgate_simulacao.py
destinos = [Node(2, 5), Node(4, 8), Node(6, 12)]
```

## 🔬 Análise dos Resultados

O simulador permite comparar:

- **Eficiência**: Dijkstra encontra caminhos com menor custo
- **Simplicidade**: BFS é mais rápido computacionalmente
- **Robustez**: Como cada algoritmo lida com incertezas
- **Adaptabilidade**: Performance em diferentes cenários

## 📈 Extensões Possíveis

- [ ] Múltiplos socorristas simultâneos
- [ ] Diferentes tipos de vítimas (gravidade)
- [ ] Recursos limitados (oxigênio, equipamentos)
- [ ] Interface web interativa
- [ ] Integração com dados reais de emergência

---

**🚨 Para executar o simulador completo, rode:**

```bash
python3 resgate_simulacao.py
```

**💡 Para entender as estruturas, rode:**

```bash
python3 exemplo_uso.py
```
