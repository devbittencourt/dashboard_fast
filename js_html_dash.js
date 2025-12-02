// Pegar todos os inputs
const inputs = $input.all();

// Coletar todos os dados JSON
let allData = [];
for (let i = 0; i < inputs.length; i++) {
  if (inputs[i] && inputs[i].json) {
    allData.push(inputs[i].json);
  }
}

// Organizar dados por tipo
const metricasHome = allData.find(d => d.tipo === 'metricas_home') || {};
const metricasCadastrar = allData.find(d => d.tipo === 'metricas_cadastrar') || {};
const metricasPublicar = allData.find(d => d.tipo === 'metricas_publicar') || {};
const metricasVagas = allData.find(d => d.tipo === 'metricas_vagas') || {};

// Função para formatar números
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

// Função para criar gráfico de barras em HTML/CSS
function createBarChart(labels, data, chartId, color = '#4f46e5') {
  const maxValue = Math.max(...data);
  const chartHeight = 200;
  
  let barsHtml = '';
  labels.forEach((label, index) => {
    const value = data[index];
    const height = maxValue > 0 ? (value / maxValue) * chartHeight : 0;
    const barWidth = 100 / labels.length;
    
    barsHtml += `
      <div class="bar-container" style="width: ${barWidth}%">
        <div class="bar" style="height: ${height}px; background-color: ${color}"></div>
        <div class="bar-label">${label}</div>
      </div>
    `;
  });
  
  return `
    <div class="chart-container" id="${chartId}">
      <div class="chart-bars" style="height: ${chartHeight}px">
        ${barsHtml}
      </div>
    </div>
  `;
}

// Função para criar gráfico de pizza em HTML/CSS
function createPieChart(labels, data, chartId) {
  const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'];
  const total = data.reduce((sum, value) => sum + value, 0);
  
  let cumulativePercent = 0;
  let slicesHtml = '';
  
  data.forEach((value, index) => {
    const percentage = total > 0 ? (value / total) * 100 : 0;
    const sliceRotation = cumulativePercent * 3.6;
    
    slicesHtml += `
      <div class="pie-slice" style="
        --percentage: ${percentage};
        --rotation: ${sliceRotation};
        --color: ${colors[index % colors.length]};
      ">
        <span class="slice-label">${labels[index]} (${value})</span>
      </div>
    `;
    
    cumulativePercent += percentage;
  });
  
  return `
    <div class="pie-chart" id="${chartId}">
      ${slicesHtml}
    </div>
  `;
}

// Criar HTML do dashboard
const html = `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Métricas - FastVagas</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        :root {
            --primary: #4f46e5;
            --primary-light: #e0e7ff;
            --secondary: #10b981;
            --secondary-light: #d1fae5;
            --warning: #f59e0b;
            --warning-light: #fef3c7;
            --danger: #ef4444;
            --danger-light: #fee2e2;
            --dark: #1f2937;
            --light: #f9fafb;
            --gray: #6b7280;
            --gray-light: #e5e7eb;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --radius: 8px;
        }
        
        body {
            background-color: #f3f4f6;
            color: var(--dark);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary) 0%, #6366f1 100%);
            color: white;
            padding: 25px 0;
            border-radius: var(--radius);
            margin-bottom: 30px;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }
        
        header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 30px 30px;
            opacity: 0.3;
        }
        
        .header-content {
            position: relative;
            z-index: 2;
            padding: 0 30px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .logo i {
            font-size: 2.5rem;
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 12px;
        }
        
        .logo h1 {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .timestamp {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.15);
            padding: 10px 15px;
            border-radius: var(--radius);
            width: fit-content;
            font-size: 0.9rem;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: var(--radius);
            padding: 25px;
            box-shadow: var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--gray-light);
        }
        
        .card-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--dark);
        }
        
        .card-title i {
            color: var(--primary);
        }
        
        .card-badge {
            background: var(--primary-light);
            color: var(--primary);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .stat-box {
            text-align: center;
            padding: 20px 15px;
            border-radius: var(--radius);
            background: var(--light);
            border: 1px solid var(--gray-light);
        }
        
        .stat-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: var(--gray);
        }
        
        .chart-container {
            margin-top: 20px;
            padding: 15px;
            background: var(--light);
            border-radius: var(--radius);
            border: 1px solid var(--gray-light);
        }
        
        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--dark);
        }
        
        .chart-bars {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            padding: 10px 0;
        }
        
        .bar-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100%;
        }
        
        .bar {
            width: 80%;
            border-radius: 4px 4px 0 0;
            transition: height 0.5s ease;
            min-height: 3px;
        }
        
        .bar-label {
            margin-top: 8px;
            font-size: 0.8rem;
            color: var(--gray);
            text-align: center;
            transform: rotate(-45deg);
            white-space: nowrap;
        }
        
        .pie-chart {
            width: 250px;
            height: 250px;
            border-radius: 50%;
            position: relative;
            margin: 0 auto;
            background: conic-gradient(
                from 0deg,
                var(--color-0, #4f46e5) 0% var(--percentage-0, 0%),
                var(--color-1, #10b981) 0% var(--percentage-1, 0%),
                var(--color-2, #f59e0b) 0% var(--percentage-2, 0%),
                var(--color-3, #ef4444) 0% var(--percentage-3, 0%),
                var(--color-4, #8b5cf6) 0% var(--percentage-4, 0%)
            );
        }
        
        .pie-slice {
            position: absolute;
            width: 100%;
            height: 100%;
            clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%);
        }
        
        .slice-label {
            position: absolute;
            left: 120%;
            top: 50%;
            transform: translateY(-50%);
            background: white;
            padding: 5px 10px;
            border-radius: 4px;
            box-shadow: var(--shadow);
            font-size: 0.85rem;
            white-space: nowrap;
        }
        
        .tendencia {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .tendencia.sucesso {
            background: var(--secondary-light);
            color: var(--secondary);
        }
        
        .tendencia.estavel {
            background: var(--warning-light);
            color: var(--warning);
        }
        
        .tendencia.alerta {
            background: var(--danger-light);
            color: var(--danger);
        }
        
        .table-container {
            overflow-x: auto;
            margin-top: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        th {
            background: var(--primary-light);
            color: var(--primary);
            font-weight: 600;
            text-align: left;
            padding: 15px;
            border-bottom: 2px solid var(--primary);
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid var(--gray-light);
        }
        
        tr:hover {
            background: var(--light);
        }
        
        .status-badge {
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .status-publicada {
            background: var(--secondary-light);
            color: var(--secondary);
        }
        
        .engajamento-alto {
            background: #10b98120;
            color: #10b981;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        .engajamento-normal {
            background: #f59e0b20;
            color: #f59e0b;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        .link-vaga {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        
        .link-vaga:hover {
            text-decoration: underline;
        }
        
        .highlight-box {
            background: linear-gradient(135deg, var(--primary-light) 0%, #e0e7ff 100%);
            border-left: 4px solid var(--primary);
            padding: 20px;
            border-radius: var(--radius);
            margin: 20px 0;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--gray-light);
            color: var(--dark);
        }
        
        .vacancy-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .vacancy-card {
            background: white;
            border-radius: var(--radius);
            padding: 20px;
            box-shadow: var(--shadow);
            border-top: 4px solid var(--primary);
        }
        
        .vacancy-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--dark);
        }
        
        .vacancy-company {
            color: var(--gray);
            font-size: 0.95rem;
            margin-bottom: 15px;
        }
        
        .vacancy-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--gray-light);
        }
        
        .stat-small {
            text-align: center;
        }
        
        .stat-small-value {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .stat-small-label {
            font-size: 0.8rem;
            color: var(--gray);
        }
        
        footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: var(--gray);
            font-size: 0.9rem;
            border-top: 1px solid var(--gray-light);
        }
        
        /* Novos estilos para gráficos de 30 dias */
        .charts-30-days {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }
        
        .chart-30-days-container {
            background: white;
            border-radius: var(--radius);
            padding: 25px;
            box-shadow: var(--shadow);
        }
        
        .chart-30-days-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--dark);
            padding-bottom: 15px;
            border-bottom: 2px solid var(--gray-light);
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .header-content {
                padding: 0 15px;
            }
            
            .logo h1 {
                font-size: 1.5rem;
            }
            
            .card {
                padding: 20px 15px;
            }
            
            .charts-30-days {
                grid-template-columns: 1fr;
            }
            
            .chart-30-days-container {
                padding: 20px 15px;
            }
            .bar-label-top {
                text-align: center;
                font-size: 0.8rem;
                color: var(--gray);
                margin-bottom: 8px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-chart-line"></i>
                    <div>
                        <h1>Dashboard FastVagas</h1>
                        <p class="subtitle">Análise completa de métricas e desempenho</p>
                    </div>
                </div>
                <div class="timestamp">
                    <i class="far fa-clock"></i>
                    <span>Última atualização: ${new Date().toLocaleString('pt-BR')}</span>
                </div>
            </div>
        </header>
        
        <div class="dashboard-grid">
            <!-- Card Visitas -->
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-home"></i>
                        Visitas
                    </h2>
                    <div class="tendencia ${metricasHome.tendencia?.status === 'estavel' ? 'estavel' : 'sucesso'}">
                        <i class="fas fa-${metricasHome.tendencia?.direcao === 'neutra' ? 'minus' : metricasHome.tendencia?.direcao === 'positiva' ? 'arrow-up' : 'arrow-down'}"></i>
                        ${metricasHome.tendencia?.status || 'N/A'}
                    </div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasHome.metricas_resumo?.total_visitas || 0)}</div>
                        <div class="stat-label">Total de Visitas</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasHome.metricas_resumo?.visitas_hoje || 0)}</div>
                        <div class="stat-label">Visitas Hoje</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasHome.metricas_temporais?.visitas_ultimas_24h || 0)}</div>
                        <div class="stat-label">Últimas 24h</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${metricasHome.metricas_resumo?.tempo_medio_sessao || 0}m</div>
                        <div class="stat-label">Tempo Médio</div>
                    </div>
                </div>
                
                  <div class="chart-container">
                    <div class="chart-title">Visitas por Hora do Dia</div>
                    ${metricasHome.dados_graficos?.visitas_por_hora ? (() => {
                        // Formatar labels: remover os minutos e manter apenas a hora
                        const originalLabels = metricasHome.dados_graficos.visitas_por_hora.labels;
                        const formattedLabels = originalLabels.map(label => {
                            // Extrair apenas a hora (parte antes dos :)
                            return label.split(':')[0];
                        });
                        
                        // Criar HTML personalizado para ter labels na parte superior
                        const maxValue = Math.max(...metricasHome.dados_graficos.visitas_por_hora.data);
                        const chartHeight = 200;
                        const data = metricasHome.dados_graficos.visitas_por_hora.data;
                        
                        let barsHtml = '';
                        formattedLabels.forEach((label, index) => {
                            const value = data[index];
                            const height = maxValue > 0 ? (value / maxValue) * chartHeight : 0;
                            const barWidth = 100 / formattedLabels.length;
                            
                            barsHtml += `
                                <div class="bar-container" style="width: ${barWidth}%">
                                    <div class="bar-label-top">${label}</div>
                                    <div class="bar" style="height: ${height}px; background-color: #4f46e5"></div>
                                </div>
                            `;
                        });
                        
                        return `
                            <div class="chart-bars" style="height: ${chartHeight}px; position: relative;">
                                ${barsHtml}
                            </div>
                            <style>
                                .bar-label-top {
                                    text-align: center;
                                    font-size: 0.8rem;
                                    color: var(--gray);
                                    margin-bottom: 8px;
                                    height: 20px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                }
                            </style>
                        `;
                    })() : '<p>Dados não disponíveis</p>'}
                </div>
            </div>
            
            <!-- Card Cadastros -->
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-user-plus"></i>
                        Cadastros
                    </h2>
                    <div class="tendencia ${metricasCadastrar.tendencia?.status === 'estavel' ? 'estavel' : 'sucesso'}">
                        <i class="fas fa-${metricasCadastrar.tendencia?.direcao === 'neutra' ? 'minus' : metricasCadastrar.tendencia?.direcao === 'positiva' ? 'arrow-up' : 'arrow-down'}"></i>
                        ${metricasCadastrar.tendencia?.status || 'N/A'}
                    </div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasCadastrar.metricas_resumo?.total_cadastros || 0)}</div>
                        <div class="stat-label">Total Cadastros</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasCadastrar.metricas_resumo?.cadastros_hoje || 0)}</div>
                        <div class="stat-label">Cadastros Hoje</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasCadastrar.metricas_temporais?.cadastros_ultimas_24h || 0)}</div>
                        <div class="stat-label">Últimas 24h</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${metricasCadastrar.projecao?.proxima_semana || 0}</div>
                        <div class="stat-label">Projeção Semana</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Cadastros por Dia da Semana</div>
                    ${metricasCadastrar.dados_graficos?.cadastros_por_dia_semana ? createBarChart(
                        metricasCadastrar.dados_graficos.cadastros_por_dia_semana.labels, 
                        metricasCadastrar.dados_graficos.cadastros_por_dia_semana.data,
                        'cadastros-dia-chart',
                        '#10b981'
                    ) : '<p>Dados não disponíveis</p>'}
                </div>
            </div>
            
            <!-- Card Publicações -->
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-newspaper"></i>
                        Publicações
                    </h2>
                    <div class="tendencia ${metricasPublicar.tendencia?.status === 'estavel' ? 'estavel' : 'sucesso'}">
                        <i class="fas fa-${metricasPublicar.tendencia?.direcao === 'neutra' ? 'minus' : metricasPublicar.tendencia?.direcao === 'positiva' ? 'arrow-up' : 'arrow-down'}"></i>
                        ${metricasPublicar.tendencia?.status || 'N/A'}
                    </div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasPublicar.metricas_resumo?.total_publicacoes || 0)}</div>
                        <div class="stat-label">Total Publicações</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasPublicar.metricas_resumo?.publicacoes_hoje || 0)}</div>
                        <div class="stat-label">Publicações Hoje</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${formatNumber(metricasPublicar.metricas_temporais?.publicacoes_ultima_semana || 0)}</div>
                        <div class="stat-label">Última Semana</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${metricasPublicar.projecao?.proximo_mes || 0}</div>
                        <div class="stat-label">Projeção Mês</div>
                    </div>
                </div>
                
                <div class="highlight-box">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <i class="fas fa-info-circle" style="font-size: 1.5rem; color: var(--primary);"></i>
                        <div>
                            <strong>Última publicação:</strong> ${metricasPublicar.metricas_resumo?.ultima_publicacao ? new Date(metricasPublicar.metricas_resumo.ultima_publicacao).toLocaleString('pt-BR') : 'N/A'}<br>
                            <strong>Tempo desde última:</strong> ${metricasPublicar.metricas_resumo?.tempo_desde_ultima_publicacao || 0} horas<br>
                            <strong>Frequência:</strong> ${metricasPublicar.estatisticas_avancadas?.frequencia_publicacao || 'N/A'}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- NOVA SEÇÃO: Gráficos dos Últimos 30 Dias -->
        <h2 class="section-title">
            <i class="fas fa-chart-area"></i>
            Análise dos Últimos 30 Dias
        </h2>
        
        <!-- Gráfico de Visitas - Linha inteira -->
        <div class="chart-30-days-container" style="margin-bottom: 25px;">
            <div class="chart-30-days-title">
                <i class="fas fa-home" style="color: #4f46e5;"></i>
                Visitas por 30 Dias
            </div>
            ${metricasHome.dados_graficos?.visitas_por_dia_30_dias ? (() => {
                const labels = metricasHome.dados_graficos.visitas_por_dia_30_dias.labels;
                const data = metricasHome.dados_graficos.visitas_por_dia_30_dias.data;
                const maxValue = Math.max(...data);
                const chartHeight = 200;
                
                let barsHtml = '';
                labels.forEach((label, index) => {
                    const value = data[index];
                    const height = maxValue > 0 ? (value / maxValue) * chartHeight : 0;
                    const barWidth = 100 / labels.length;
                    // Extrair apenas o dia (parte antes da /)
                    const dayOnly = label.split('/')[0];
                    
                    barsHtml += `
                        <div class="bar-container" style="width: ${barWidth}%">
                            <div class="bar-label-top">${dayOnly}</div>
                            <div class="bar" style="height: ${height}px; background-color: #4f46e5; position: relative;">
                                ${value > 0 ? `<div class="bar-value-bottom">${value}</div>` : ''}
                            </div>
                        </div>
                    `;
                });
                
                return `
                    <div class="chart-bars" style="height: ${chartHeight}px; position: relative;">
                        ${barsHtml}
                    </div>
                    <style>
                        .bar-value-bottom {
                            position: absolute;
                            bottom: -25px;
                            left: 50%;
                            transform: translateX(-50%);
                            font-size: 0.75rem;
                            font-weight: 600;
                            color: #4f46e5;
                            background: rgba(255, 255, 255, 0.9);
                            padding: 2px 5px;
                            border-radius: 3px;
                            white-space: nowrap;
                        }
                    </style>
                `;
            })() : '<p>Dados de visitas por 30 dias não disponíveis</p>'}
            <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: var(--radius);">
                <p style="margin: 0; font-size: 0.9rem; color: var(--gray);">
                    <strong>Total no período:</strong> ${formatNumber(metricasHome.metricas_resumo?.visitas_semana || 0)} visitas<br>
                    <strong>Média diária:</strong> ${formatNumber(Math.round((metricasHome.metricas_resumo?.visitas_semana || 0) / 30))} visitas/dia
                </p>
            </div>
        </div>
        
        <!-- Cadastros e Publicações - Gráfico combinado na linha abaixo -->
        <div class="chart-30-days-container">
            <div class="chart-30-days-title">
                <i class="fas fa-chart-bar"></i>
                Cadastros e Publicações por 30 Dias
            </div>
            ${metricasCadastrar.dados_graficos?.cadastros_por_dia_30_dias && metricasPublicar.dados_graficos?.publicacoes_por_dia_30_dias ? (() => {
                const labels = metricasCadastrar.dados_graficos.cadastros_por_dia_30_dias.labels;
                const cadastrosData = metricasCadastrar.dados_graficos.cadastros_por_dia_30_dias.data;
                const publicacoesData = metricasPublicar.dados_graficos.publicacoes_por_dia_30_dias.data;
                
                // Encontrar o valor máximo entre os dois conjuntos de dados
                const maxCadastro = Math.max(...cadastrosData);
                const maxPublicacao = Math.max(...publicacoesData);
                const maxValue = Math.max(maxCadastro, maxPublicacao, 1); // Mínimo 1 para evitar divisão por zero
                const chartHeight = 200;
                
                let barsHtml = '';
                labels.forEach((label, index) => {
                    const cadastroValue = cadastrosData[index];
                    const publicacaoValue = publicacoesData[index];
                    const barWidth = 100 / labels.length;
                    // Extrair apenas o dia (parte antes da /)
                    const dayOnly = label.split('/')[0];
                    
                    // Calcular alturas das barras
                    const cadastroHeight = maxValue > 0 ? (cadastroValue / maxValue) * chartHeight : 0;
                    const publicacaoHeight = maxValue > 0 ? (publicacaoValue / maxValue) * chartHeight : 0;
                    
                    barsHtml += `
                        <div style="width: ${barWidth}%; display: flex; flex-direction: column; align-items: center; height: ${chartHeight + 30}px;">
                            <div style="margin-bottom: 5px; font-size: 0.75rem; color: var(--gray); height: 20px; display: flex; align-items: center;">${dayOnly}</div>
                            <div style="display: flex; justify-content: center; gap: 2px; width: 100%; height: ${chartHeight}px; align-items: flex-start;">
                                <!-- Barra de Cadastros (verde) - COMEÇA DO TOPO -->
                                <div style="height: ${cadastroHeight}px; background-color: #10b981; width: 45%; position: relative; border-radius: 0 0 2px 2px; margin-top: 0;">
                                    ${cadastroValue > 0 ? `<div style="position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%); font-size: 0.7rem; font-weight: 600; color: #10b981; background: rgba(255, 255, 255, 0.9); padding: 1px 4px; border-radius: 2px; white-space: nowrap;">${cadastroValue}</div>` : ''}
                                </div>
                                <!-- Barra de Publicações (laranja) - COMEÇA DO TOPO -->
                                <div style="height: ${publicacaoHeight}px; background-color: #f59e0b; width: 45%; position: relative; border-radius: 0 0 2px 2px; margin-top: 0;">
                                    ${publicacaoValue > 0 ? `<div style="position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%); font-size: 0.7rem; font-weight: 600; color: #f59e0b; background: rgba(255, 255, 255, 0.9); padding: 1px 4px; border-radius: 2px; white-space: nowrap;">${publicacaoValue}</div>` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                return `
                    <div style="margin-top: 20px; margin-bottom: 20px;">
                        <!-- LEGENDA ACIMA DO GRÁFICO -->
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px; justify-content: center;">
                            <div style="display: flex; align-items: center; gap: 5px;">
                                <div style="width: 12px; height: 12px; background-color: #10b981; border-radius: 2px;"></div>
                                <span style="font-size: 0.85rem; color: var(--gray);">Cadastros</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 5px;">
                                <div style="width: 12px; height: 12px; background-color: #f59e0b; border-radius: 2px;"></div>
                                <span style="font-size: 0.85rem; color: var(--gray);">Publicações</span>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: flex-start; justify-content: space-between; height: ${chartHeight}px; padding: 0 5px;">
                            ${barsHtml}
                        </div>
                    </div>
                `;
            })() : '<p>Dados de cadastros e publicações por 30 dias não disponíveis</p>'}
            
            <!-- LINHA VAZIA ENTRE GRÁFICO E ESTATÍSTICAS -->
            <div style="height: 25px;"></div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 0;">
                <div style="padding: 10px; background: #f8f9fa; border-radius: var(--radius);">
                    <p style="margin: 0; font-size: 0.9rem; color: var(--gray);">
                        <strong>Cadastros</strong><br>
                        <strong>Total:</strong> ${formatNumber(metricasCadastrar.metricas_resumo?.cadastros_semana || 0)}<br>
                        <strong>Média diária:</strong> ${formatNumber(Math.round((metricasCadastrar.metricas_resumo?.cadastros_semana || 0) / 30))}
                    </p>
                </div>
                <div style="padding: 10px; background: #f8f9fa; border-radius: var(--radius);">
                    <p style="margin: 0; font-size: 0.9rem; color: var(--gray);">
                        <strong>Publicações</strong><br>
                        <strong>Total:</strong> ${formatNumber(metricasPublicar.metricas_resumo?.publicacoes_semana || 0)}<br>
                        <strong>Média diária:</strong> ${formatNumber(Math.round((metricasPublicar.metricas_resumo?.publicacoes_semana || 0) / 30))}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Seção Vagas -->
        <h2 class="section-title">
            <i class="fas fa-briefcase"></i>
            Análise de Vagas
        </h2>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">
                    <i class="fas fa-chart-bar"></i>
                    Métricas de Vagas
                </h2>
                <div class="card-badge">
                    ${metricasVagas.metricas_resumo?.total_vagas || 0} Vagas
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">${formatNumber(metricasVagas.metricas_resumo?.total_vagas || 0)}</div>
                    <div class="stat-label">Total de Vagas</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${formatNumber(metricasVagas.metricas_resumo?.total_visualizacoes || 0)}</div>
                    <div class="stat-label">Visualizações</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${formatNumber(metricasVagas.metricas_resumo?.total_cliques || 0)}</div>
                    <div class="stat-label">Cliques</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${metricasVagas.metricas_resumo?.ctr_medio || 0}%</div>
                    <div class="stat-label">CTR Médio</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 30px;">
                <div class="chart-container">
                    <div class="chart-title">Distribuição por Modalidade</div>
                    ${metricasVagas.dados_graficos?.modalidade_data ? createPieChart(
                        metricasVagas.dados_graficos.modalidade_data.labels,
                        metricasVagas.dados_graficos.modalidade_data.data,
                        'modalidade-chart'
                    ) : '<p>Dados não disponíveis</p>'}
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Distribuição por Faixa Salarial</div>
                    ${metricasVagas.dados_graficos?.salario_data ? createBarChart(
                        metricasVagas.dados_graficos.salario_data.labels,
                        metricasVagas.dados_graficos.salario_data.data,
                        'salario-chart',
                        '#8b5cf6'
                    ) : '<p>Dados não disponíveis</p>'}
                </div>
            </div>
        </div>
        
        <!-- Top Vagas com Alto Engajamento -->
        <h2 class="section-title" style="margin-top: 40px;">
            <i class="fas fa-fire"></i>
            Top Vagas com Alto Engajamento (${metricasVagas.metricas_resumo?.vagas_alto_engajamento || 0})
        </h2>
        
        <div class="vacancy-grid">
            ${metricasVagas.vagas_alto_engajamento_lista ? metricasVagas.vagas_alto_engajamento_lista.slice(0, 6).map(vaga => `
                <div class="vacancy-card">
                    <h3 class="vacancy-title">${vaga.titulo}</h3>
                    <div class="vacancy-company">
                        <i class="fas fa-building"></i> ${vaga.empresa}<br>
                        <i class="fas fa-map-marker-alt"></i> ${vaga.regiao}<br>
                        <i class="fas fa-${vaga.modalidade === 'Remoto' ? 'home' : 'building'}"></i> ${vaga.modalidade}
                    </div>
                    
                    ${vaga.salario_texto ? `<div><i class="fas fa-money-bill-wave"></i> ${vaga.salario_texto}</div>` : ''}
                    
                    <div class="vacancy-stats">
                        <div class="stat-small">
                            <div class="stat-small-value">${vaga.visualizacao}</div>
                            <div class="stat-small-label">Visualizações</div>
                        </div>
                        <div class="stat-small">
                            <div class="stat-small-value">${vaga.click_link}</div>
                            <div class="stat-small-label">Cliques</div>
                        </div>
                        <div class="stat-small">
                            <div class="stat-small-value">${vaga.ctr_individual}%</div>
                            <div class="stat-small-label">CTR</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <a href="${vaga.link_vaga}" target="_blank" class="link-vaga">
                            <i class="fas fa-external-link-alt"></i> Ver vaga
                        </a>
                        <span class="engajamento-alto" style="float: right;">Alto Engajamento</span>
                    </div>
                </div>
            `).join('') : '<p>Nenhuma vaga com alto engajamento encontrada</p>'}
        </div>
        
        <!-- Tabela Completa de Vagas -->
        <h2 class="section-title">
            <i class="fas fa-table"></i>
            Todas as Vagas (${metricasVagas.tabela_vagas_completa ? metricasVagas.tabela_vagas_completa.length : 0})
        </h2>
        
        <div class="card">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Título</th>
                            <th>Empresa</th>
                            <th>Local</th>
                            <th>Visualizações</th>
                            <th>Cliques</th>
                            <th>CTR</th>
                            <th>Engajamento</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${metricasVagas.tabela_vagas_completa ? metricasVagas.tabela_vagas_completa.slice(0, 10).map(vaga => `
                            <tr>
                                <td>${vaga.id}</td>
                                <td><strong>${vaga.titulo.substring(0, 50)}${vaga.titulo.length > 50 ? '...' : ''}</strong></td>
                                <td>${vaga.empresa.substring(0, 20)}${vaga.empresa.length > 20 ? '...' : ''}</td>
                                <td>${vaga.regiao.substring(0, 20)}${vaga.regiao.length > 20 ? '...' : ''}</td>
                                <td>${vaga.visualizacao}</td>
                                <td>${vaga.click_link}</td>
                                <td>${vaga.ctr_individual}%</td>
                                <td>
                                    <span class="${vaga.engajamento === 'Alto' ? 'engajamento-alto' : 'engajamento-normal'}">
                                        ${vaga.engajamento}
                                    </span>
                                </td>
                                <td>
                                    <a href="${vaga.link_vaga}" target="_blank" class="link-vaga">
                                        <i class="fas fa-external-link-alt"></i>
                                    </a>
                                </td>
                            </tr>
                        `).join('') : '<tr><td colspan="9" style="text-align: center;">Nenhuma vaga disponível</td></tr>'}
                    </tbody>
                </table>
                ${metricasVagas.tabela_vagas_completa && metricasVagas.tabela_vagas_completa.length > 10 ? 
                    `<p style="text-align: center; margin-top: 15px; color: var(--gray);">
                        Mostrando 10 de ${metricasVagas.tabela_vagas_completa.length} vagas
                    </p>` : ''
                }
            </div>
        </div>
        
        <!-- Informações de Processamento -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 40px;">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-cogs"></i>
                        Processamento
                    </h2>
                </div>
                <div style="padding: 15px;">
                    <p><strong>Período Analisado:</strong><br>
                    ${metricasHome.detalhes_processamento?.periodo_analisado?.inicio ? new Date(metricasHome.detalhes_processamento.periodo_analisado.inicio).toLocaleDateString('pt-BR') : 'N/A'} a 
                    ${metricasHome.detalhes_processamento?.periodo_analisado?.fim ? new Date(metricasHome.detalhes_processamento.periodo_analisado.fim).toLocaleDateString('pt-BR') : 'N/A'}</p>
                    
                    <p><strong>Registros Processados:</strong><br>
                    • Visitas: ${metricasHome.detalhes_processamento?.registros_processados || 0}<br>
                    • Cadastros: ${metricasCadastrar.detalhes_processamento?.registros_processados || 0}<br>
                    • Publicações: ${metricasPublicar.detalhes_processamento?.registros_processados || 0}<br>
                    • Vagas: ${metricasVagas.tabela_vagas_completa ? metricasVagas.tabela_vagas_completa.length : 0}</p>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-chart-pie"></i>
                        Resumo Geral
                    </h2>
                </div>
                <div style="padding: 15px;">
                    <p><strong>Status dos Serviços:</strong><br>
                    • Visitas: <span class="tendencia sucesso" style="display: inline-block; padding: 2px 8px;">${metricasHome.status || 'N/A'}</span><br>
                    • Cadastros: <span class="tendencia sucesso" style="display: inline-block; padding: 2px 8px;">${metricasCadastrar.status || 'N/A'}</span><br>
                    • Publicações: <span class="tendencia sucesso" style="display: inline-block; padding: 2px 8px;">${metricasPublicar.status || 'N/A'}</span><br>
                    • Vagas: <span class="tendencia sucesso" style="display: inline-block; padding: 2px 8px;">${metricasVagas.status || 'N/A'}</span></p>
                    
                    <p><strong>Picos de Atividade:</strong><br>
                    • Visitas: ${metricasHome.metricas_resumo?.pico_horario || 'N/A'}<br>
                    • Cadastros: ${metricasCadastrar.metricas_resumo?.pico_horario || 'N/A'}<br>
                    • Publicações: ${metricasPublicar.metricas_resumo?.pico_horario || 'N/A'}</p>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Dashboard gerado automaticamente • Dados atualizados em tempo real</p>
            <p>FastVagas Analytics • ${new Date().getFullYear()}</p>
        </footer>
    </div>
    
    <script>
        // Animar barras dos gráficos
        document.addEventListener('DOMContentLoaded', function() {
            // Animar barras ao carregar
            setTimeout(() => {
                const bars = document.querySelectorAll('.bar');
                bars.forEach(bar => {
                    const currentHeight = bar.style.height;
                    bar.style.height = '0px';
                    setTimeout(() => {
                        bar.style.height = currentHeight;
                    }, 100);
                });
            }, 500);
            
            // Adicionar tooltips às barras
            const barContainers = document.querySelectorAll('.bar-container');
            barContainers.forEach(container => {
                const bar = container.querySelector('.bar');
                const label = container.querySelector('.bar-label').textContent;
                const height = bar.style.height;
                const value = Math.round(parseInt(height) / 200 * 100); // Valor aproximado
                
                bar.title = \`\${label}: \${value}\`;
            });
        });
    </script>
</body>
</html>
`;

// Retornar o HTML
return [{ json: { html: html } }];
