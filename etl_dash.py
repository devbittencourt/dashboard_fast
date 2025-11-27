import pandas as pd
import numpy as np
from datetime import datetime
import re
import json

# Função para serializar dados com tratamento de valores não serializáveis
def safe_serialize(obj):
    if obj is None or pd.isna(obj):
        return None
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)

# Retornando array de dicionários
result = []

try:
    # Coletar todos os dados das vagas
    vagas_data = []
    for item in items:
        if 'json' in item and item['json']:
            # Limpar dados antes de adicionar
            cleaned_item = {}
            for key, value in item['json'].items():
                if value is None or (hasattr(value, '__class__') and 'JsNull' in str(value.__class__)):
                    cleaned_item[key] = None
                elif pd.isna(value):
                    cleaned_item[key] = None
                else:
                    cleaned_item[key] = value
            vagas_data.append(cleaned_item)
    
    # Criar DataFrame
    df_vagas = pd.DataFrame(vagas_data)
    
    # Preparar dados básicos
    df_vagas['visualizacao'] = pd.to_numeric(df_vagas['visualizacao'], errors='coerce').fillna(0).astype(int)
    df_vagas['click_link'] = pd.to_numeric(df_vagas['click_link'], errors='coerce').fillna(0).astype(int)
    df_vagas['ctr_individual'] = (df_vagas['click_link'] / df_vagas['visualizacao'] * 100).round(2)
    df_vagas['ctr_individual'] = df_vagas['ctr_individual'].replace([np.inf, -np.inf], 0).fillna(0)
    
    # TRATAMENTO DA REGIÃO: Remover números entre parênteses
    def limpar_regiao(regiao):
        if pd.isna(regiao) or regiao == '':
            return regiao
        # Remove padrões como "(1)", "(2)", "(10)" etc.
        regiao_limpa = re.sub(r'\s*\(\d+\)\s*$', '', str(regiao))
        return regiao_limpa.strip()
    
    # Aplicar a limpeza na coluna regiao (sobrescrevendo a original)
    if 'regiao' in df_vagas.columns:
        df_vagas['regiao'] = df_vagas['regiao'].apply(limpar_regiao)
    
    # Criar tabela completa de vagas (PRINCIPAL)
    tabela_vagas_completa = []
    if not df_vagas.empty:
        # Ordenar por visualização (desc) e depois por click_link (desc)
        df_ordenado = df_vagas.sort_values(['visualizacao', 'click_link'], ascending=[False, False])
        
        for _, vaga in df_ordenado.iterrows():
            link_vaga = f"https://fastvagas.vercel.app/}"
            
            # Garantir que todos os valores são serializáveis
            salario_numero = vaga.get('salario_numero')
            if salario_numero is None or pd.isna(salario_numero):
                salario_numero = None
            else:
                salario_numero = float(salario_numero)
            
            vaga_info = {
                'id': int(vaga['id']),
                'titulo': str(vaga['titulo']),
                'empresa': str(vaga.get('empresa', '')),
                'regiao': str(vaga.get('regiao', '')),
                'modalidade': str(vaga.get('modalidade', '')),
                'salario_numero': salario_numero,
                'salario_texto': str(vaga.get('salario_texto', '')),
                'visualizacao': int(vaga['visualizacao']),
                'click_link': int(vaga['click_link']),
                'ctr_individual': float(vaga['ctr_individual']),
                'link_vaga': link_vaga
            }
            tabela_vagas_completa.append(vaga_info)
    
    # Métricas resumidas básicas
    metricas_resumo = {
        'total_vagas': int(len(df_vagas)),
        'total_visualizacoes': int(df_vagas['visualizacao'].sum()),
        'total_cliques': int(df_vagas['click_link'].sum()),
        'ctr_medio': float(round(df_vagas['ctr_individual'].mean(), 2))
    }
    
    # Resultado principal
    resultado_principal = {
        'status': 'sucesso',
        'timestamp': datetime.now().isoformat(),
        'metricas_resumo': metricas_resumo,
        'tabela_vagas_completa': tabela_vagas_completa
    }
    
    # Converter para JSON seguro para HTML
    dados_json = json.dumps(resultado_principal, default=safe_serialize, ensure_ascii=False)
    
    # Gerar HTML completo com dados injetados
    html_completo = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard FastVagas</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}

        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}

        .dashboard {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
        }}

        .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }}

        .metric-label {{
            font-size: 1rem;
            opacity: 0.9;
        }}

        .charts-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        .chart-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .chart-card h3 {{
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }}

        .table-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .table-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}

        .table-header h2 {{
            color: #333;
        }}

        .search-box {{
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            width: 300px;
            font-size: 14px;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            text-align: left;
            cursor: pointer;
            user-select: none;
        }}

        th:hover {{
            background: linear-gradient(135deg, #5a6fd8, #6a4190);
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}

        tr:hover {{
            background-color: #f5f5f5;
        }}

        .ctr-high {{
            color: #28a745;
            font-weight: bold;
        }}

        .ctr-medium {{
            color: #ffc107;
            font-weight: bold;
        }}

        .ctr-low {{
            color: #dc3545;
            font-weight: bold;
        }}

        .link-vaga {{
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }}

        .link-vaga:hover {{
            text-decoration: underline;
        }}

        .salario {{
            font-weight: bold;
            color: #28a745;
        }}

        .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
            gap: 10px;
        }}

        .pagination button {{
            padding: 8px 16px;
            border: none;
            background: #667eea;
            color: white;
            border-radius: 5px;
            cursor: pointer;
        }}

        .pagination button:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}

        .pagination-info {{
            color: #666;
        }}

        .loading {{
            text-align: center;
            padding: 20px;
            color: #666;
        }}

        @media (max-width: 768px) {{
            .charts-container {{
                grid-template-columns: 1fr;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .search-box {{
                width: 100%;
                margin-top: 10px;
            }}
            
            .table-header {{
                flex-direction: column;
                align-items: stretch;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard FastVagas</h1>
            <p>Análise de performance das vagas em tempo real</p>
        </div>

        <div class="dashboard">
            <div class="metrics-grid" id="metricsGrid">
                <div class="loading">Carregando métricas...</div>
            </div>

            <div class="charts-container">
                <div class="chart-card">
                    <h3>Distribuição por Região (Top 5)</h3>
                    <canvas id="regionsChart"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Performance por Modalidade</h3>
                    <canvas id="modalidadeChart"></canvas>
                </div>
            </div>
        </div>

        <div class="table-container">
            <div class="table-header">
                <h2>📋 Tabela de Vagas</h2>
                <input type="text" id="searchInput" class="search-box" placeholder="🔍 Buscar por título, empresa ou região...">
            </div>
            
            <table id="vagasTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Título</th>
                        <th onclick="sortTable(1)">Empresa</th>
                        <th onclick="sortTable(2)">Região</th>
                        <th onclick="sortTable(3)">Salário</th>
                        <th onclick="sortTable(4)">Visualizações</th>
                        <th onclick="sortTable(5)">Cliques</th>
                        <th onclick="sortTable(6)">CTR</th>
                        <th>Link</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    <tr>
                        <td colspan="8" class="loading">Carregando dados das vagas...</td>
                    </tr>
                </tbody>
            </table>

            <div class="pagination">
                <button id="prevBtn" onclick="changePage(-1)">Anterior</button>
                <span class="pagination-info" id="pageInfo">Página 1 de 1</span>
                <button id="nextBtn" onclick="changePage(1)">Próxima</button>
            </div>
        </div>
    </div>

    <script>
        // Dados injetados diretamente do n8n
        const dados = {dados_json};
        
        // Variáveis globais
        let currentPage = 1;
        const itemsPerPage = 10;
        let currentData = [];
        let sortDirection = 1;
        let lastSortedColumn = -1;

        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Dados recebidos:', dados);
            if (dados && dados.status === 'sucesso') {{
                initializeDashboard();
                initializeTable();
                initializeCharts();
            }} else {{
                exibirErro('Erro ao carregar dados: ' + (dados?.error || 'Status inválido'));
            }}
        }});

        function exibirErro(mensagem) {{
            document.getElementById('metricsGrid').innerHTML = `
                <div class="metric-card" style="background: #dc3545;">
                    <div class="metric-label">Erro</div>
                    <div class="metric-value">!</div>
                    <div class="metric-label">${{mensagem}}</div>
                </div>
            `;
            
            document.getElementById('tableBody').innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; color: #dc3545;">${{mensagem}}</td>
                </tr>
            `;
        }}

        function initializeDashboard() {{
            if (!dados || !dados.metricas_resumo) {{
                exibirErro('Dados de métricas não disponíveis');
                return;
            }}
            
            const metrics = dados.metricas_resumo;
            const metricsGrid = document.getElementById('metricsGrid');
            
            metricsGrid.innerHTML = `
                <div class="metric-card">
                    <div class="metric-label">Total de Vagas</div>
                    <div class="metric-value">${{metrics.total_vagas}}</div>
                    <div class="metric-label">Vagas ativas</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Visualizações</div>
                    <div class="metric-value">${{metrics.total_visualizacoes}}</div>
                    <div class="metric-label">Total de views</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Cliques</div>
                    <div class="metric-value">${{metrics.total_cliques}}</div>
                    <div class="metric-label">Engajamento</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">CTR Médio</div>
                    <div class="metric-value">${{metrics.ctr_medio}}%</div>
                    <div class="metric-label">Taxa de conversão</div>
                </div>
            `;
        }}

        function initializeTable() {{
            if (!dados || !dados.tabela_vagas_completa) {{
                exibirErro('Dados das vagas não disponíveis');
                return;
            }}
            
            currentData = [...dados.tabela_vagas_completa];
            renderTable();
            
            // Configurar busca
            document.getElementById('searchInput').addEventListener('input', function(e) {{
                const searchTerm = e.target.value.toLowerCase();
                currentData = dados.tabela_vagas_completa.filter(vaga => 
                    vaga.titulo.toLowerCase().includes(searchTerm) ||
                    (vaga.empresa && vaga.empresa.toLowerCase().includes(searchTerm)) ||
                    vaga.regiao.toLowerCase().includes(searchTerm)
                );
                currentPage = 1;
                renderTable();
            }});
        }}

        function renderTable() {{
            const tableBody = document.getElementById('tableBody');
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const pageData = currentData.slice(startIndex, endIndex);
            
            if (pageData.length === 0) {{
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="8" style="text-align: center;">Nenhuma vaga encontrada</td>
                    </tr>
                `;
            }} else {{
                tableBody.innerHTML = pageData.map(vaga => {{
                    const salarioDisplay = vaga.salario_numero 
                        ? `R$ ${{vaga.salario_numero.toLocaleString('pt-BR')}}` 
                        : 'Não informado';
                    
                    return `
                    <tr>
                        <td>${{vaga.titulo}}</td>
                        <td>${{vaga.empresa || '-'}}</td>
                        <td>${{vaga.regiao}}</td>
                        <td class="salario">${{salarioDisplay}}</td>
                        <td>${{vaga.visualizacao}}</td>
                        <td>${{vaga.click_link}}</td>
                        <td class="${{getCTRClass(vaga.ctr_individual)}}">${{vaga.ctr_individual}}%</td>
                        <td><a href="${{vaga.link_vaga}}" target="_blank" class="link-vaga">Ver Vaga</a></td>
                    </tr>
                    `;
                }}).join('');
            }}
            
            updatePagination();
        }}

        function getCTRClass(ctr) {{
            if (ctr >= 50) return 'ctr-high';
            if (ctr >= 20) return 'ctr-medium';
            return 'ctr-low';
        }}

        function updatePagination() {{
            const totalPages = Math.ceil(currentData.length / itemsPerPage);
            document.getElementById('pageInfo').textContent = `Página ${{currentPage}} de ${{totalPages}}`;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = currentPage === totalPages || totalPages === 0;
        }}

        function changePage(direction) {{
            const totalPages = Math.ceil(currentData.length / itemsPerPage);
            currentPage += direction;
            
            if (currentPage < 1) currentPage = 1;
            if (currentPage > totalPages) currentPage = totalPages;
            
            renderTable();
        }}

        function sortTable(columnIndex) {{
            if (lastSortedColumn === columnIndex) {{
                sortDirection *= -1;
            }} else {{
                sortDirection = 1;
                lastSortedColumn = columnIndex;
            }}
            
            currentData.sort((a, b) => {{
                let valueA, valueB;
                
                switch(columnIndex) {{
                    case 0: valueA = a.titulo; valueB = b.titulo; break;
                    case 1: valueA = a.empresa || ''; valueB = b.empresa || ''; break;
                    case 2: valueA = a.regiao; valueB = b.regiao; break;
                    case 3: valueA = a.salario_numero || 0; valueB = b.salario_numero || 0; break;
                    case 4: valueA = a.visualizacao; valueB = b.visualizacao; break;
                    case 5: valueA = a.click_link; valueB = b.click_link; break;
                    case 6: valueA = a.ctr_individual; valueB = b.ctr_individual; break;
                    default: return 0;
                }}
                
                if (typeof valueA === 'string') {{
                    return sortDirection * valueA.localeCompare(valueB);
                }} else {{
                    return sortDirection * (valueA - valueB);
                }}
            }});
            
            currentPage = 1;
            renderTable();
        }}

        function initializeCharts() {{
            if (!dados || !dados.tabela_vagas_completa) {{
                return;
            }}
            
            // Gráfico de regiões (Top 5)
            const regionsData = getTopRegions(5);
            if (regionsData.labels.length > 0) {{
                new Chart(document.getElementById('regionsChart'), {{
                    type: 'bar',
                    data: {{
                        labels: regionsData.labels,
                        datasets: [{{
                            label: 'Visualizações',
                            data: regionsData.visualizacoes,
                            backgroundColor: 'rgba(102, 126, 234, 0.8)',
                            borderColor: 'rgba(102, 126, 234, 1)',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}

            // Gráfico de modalidade
            const modalidadeData = getModalidadeData();
            if (modalidadeData.labels.length > 0) {{
                new Chart(document.getElementById('modalidadeChart'), {{
                    type: 'doughnut',
                    data: {{
                        labels: modalidadeData.labels,
                        datasets: [{{
                            data: modalidadeData.data,
                            backgroundColor: [
                                'rgba(102, 126, 234, 0.8)',
                                'rgba(118, 75, 162, 0.8)',
                                'rgba(255, 99, 132, 0.8)',
                                'rgba(54, 162, 235, 0.8)',
                                'rgba(255, 206, 86, 0.8)'
                            ]
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});
            }}
        }}

        function getTopRegions(limit) {{
            const regionMap = {{}};
            dados.tabela_vagas_completa.forEach(vaga => {{
                if (vaga.regiao) {{
                    if (!regionMap[vaga.regiao]) {{
                        regionMap[vaga.regiao] = 0;
                    }}
                    regionMap[vaga.regiao] += vaga.visualizacao;
                }}
            }});
            
            const sortedRegions = Object.entries(regionMap)
                .sort((a, b) => b[1] - a[1])
                .slice(0, limit);
            
            return {{
                labels: sortedRegions.map(r => r[0]),
                visualizacoes: sortedRegions.map(r => r[1])
            }};
        }}

        function getModalidadeData() {{
            const modalidadeMap = {{}};
            dados.tabela_vagas_completa.forEach(vaga => {{
                const modalidade = vaga.modalidade || 'Não informado';
                if (!modalidadeMap[modalidade]) {{
                    modalidadeMap[modalidade] = 0;
                }}
                modalidadeMap[modalidade]++;
            }});
            
            return {{
                labels: Object.keys(modalidadeMap),
                data: Object.values(modalidadeMap)
            }};
        }}
    </script>
</body>
</html>'''

    result.append({
        "json": {"html": html_completo},
        "binary": {},
        "pairedItem": {"item": 0}
    })

except Exception as e:
    error_info = {
        "status": "erro",
        "timestamp": datetime.now().isoformat(),
        "error": str(e)
    }
    result.append({
        "json": error_info,
        "binary": {},
        "pairedItem": {"item": 0}
    })

return result
