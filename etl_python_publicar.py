import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

result = []

try:
    # Coletar todos os dados de publicação
    publicar_data = []
    
    for item in items:
        if 'json' in item and item['json']:
            item_data = item['json']
            publicar_data.append(item_data)
    
    # Criar DataFrame apenas com dados de publicação
    df_publicar = pd.DataFrame(publicar_data) if publicar_data else pd.DataFrame()
    
    print(f"DEBUG - Total de publicações recebidas: {len(df_publicar)}")
    
    # Se não há dados, retornar estrutura vazia
    if df_publicar.empty:
        print("DEBUG - Nenhuma publicação recebida")
        
        resultado_publicar = {
            'status': 'sucesso',
            'timestamp': datetime.now().isoformat(),
            'tipo': 'metricas_publicar',
            'metricas_resumo': {
                'total_publicacoes': 0,
                'publicacoes_hoje': 0,
                'publicacoes_semana': 0,
                'taxa_publicacao_diaria': 0,
                'ultima_publicacao': None,
                'tempo_desde_ultima_publicacao': None,
                'tempo_medio_entre_publicacoes': None,
                'taxa_crescimento': 0.0
            },
            'metricas_temporais': {
                'publicacoes_ultima_hora': 0,
                'publicacoes_ultimas_24h': 0,
                'publicacoes_ultima_semana': 0,
                'publicacoes_ultimo_mes': 0
            },
            'dados_graficos': {
                'publicacoes_por_dia_30_dias': {'labels': [], 'data': []},
                'publicacoes_por_hora': {'labels': [], 'data': []},
                'publicacoes_por_dia_semana': {'labels': [], 'data': []}
            },
            'tendencia': {
                'status': 'estavel',
                'variacao': 0.0,
                'direcao': 'neutra'
            },
            'projecao': {
                'proxima_semana': 0,
                'proximo_mes': 0
            },
            'estatisticas_avancadas': {
                'frequencia_publicacao': 'baixa',
                'consistencia': 'irregular',
                'velocidade_crescimento': 'estavel'
            }
        }
        
        result.append({
            "json": resultado_publicar,
            "binary": {},
            "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
        })
        return result

    print(f"DEBUG - Colunas disponíveis nas publicações: {df_publicar.columns.tolist()}")
    
    # DATAS PARA CÁLCULOS
    agora = datetime.now().replace(tzinfo=None)
    hoje = agora.date()
    uma_semana_atras = hoje - timedelta(days=7)
    um_mes_atras = hoje - timedelta(days=30)
    uma_hora_atras = agora - timedelta(hours=1)
    um_dia_atras = agora - timedelta(days=1)
    
    # PROCESSAR DATAS
    df_publicar_processed = df_publicar.copy()
    
    # Encontrar coluna de data
    date_column = None
    for col in ['created_at', 'timestamp', 'event_time']:
        if col in df_publicar.columns:
            date_column = col
            break
    
    if not date_column:
        print("DEBUG - Nenhuma coluna de data encontrada")
        for col in df_publicar.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_column = col
                break
    
    if date_column:
        df_publicar_processed['data_processada'] = pd.to_datetime(
            df_publicar_processed[date_column], errors='coerce'
        ).dt.tz_localize(None)
        df_publicar_validas = df_publicar_processed[df_publicar_processed['data_processada'].notna()]
    else:
        print("DEBUG - Criando timestamps fictícios")
        df_publicar_validas = df_publicar_processed.copy()
        start_time = datetime.now() - timedelta(days=30)
        df_publicar_validas['data_processada'] = [
            start_time + timedelta(hours=i) for i in range(len(df_publicar_validas))
        ]
    
    print(f"DEBUG - Publicações válidas com data: {len(df_publicar_validas)}")
    
    # MÉTRICAS BÁSICAS
    total_publicacoes = len(df_publicar_validas)
    
    # MÉTRICAS TEMPORAIS
    publicacoes_hoje = len(df_publicar_validas[
        df_publicar_validas['data_processada'].dt.date == hoje
    ])
    
    publicacoes_semana = len(df_publicar_validas[
        df_publicar_validas['data_processada'].dt.date >= uma_semana_atras
    ])
    
    publicacoes_ultima_hora = len(df_publicar_validas[
        df_publicar_validas['data_processada'] >= uma_hora_atras
    ])
    
    publicacoes_ultimas_24h = len(df_publicar_validas[
        df_publicar_validas['data_processada'] >= um_dia_atras
    ])
    
    publicacoes_ultimo_mes = len(df_publicar_validas[
        df_publicar_validas['data_processada'].dt.date >= um_mes_atras
    ])
    
    # ÚLTIMA PUBLICAÇÃO
    ultima_publicacao = None
    tempo_desde_ultima_publicacao = None
    
    if not df_publicar_validas.empty:
        ultima_publicacao_dt = df_publicar_validas['data_processada'].max()
        ultima_publicacao = ultima_publicacao_dt.isoformat()
        
        # Calcular tempo desde a última publicação
        tempo_desde_ultima_publicacao = round((agora - ultima_publicacao_dt).total_seconds() / 3600, 1)  # em horas
    
    # TAXA DE PUBLICAÇÃO DIÁRIA (média dos últimos 7 dias)
    taxa_publicacao_diaria = 0
    if publicacoes_semana > 0:
        ultimos_7_dias = df_publicar_validas[
            df_publicar_validas['data_processada'].dt.date >= uma_semana_atras
        ]
        if not ultimos_7_dias.empty:
            publicacoes_por_dia = ultimos_7_dias.groupby(
                ultimos_7_dias['data_processada'].dt.date
            ).size()
            taxa_publicacao_diaria = round(float(publicacoes_por_dia.mean()), 1)
    
    # TEMPO MÉDIO ENTRE PUBLICAÇÕES
    tempo_medio_entre_publicacoes = None
    if len(df_publicar_validas) > 1:
        df_publicar_sorted = df_publicar_validas.sort_values('data_processada')
        time_diffs = df_publicar_sorted['data_processada'].diff().dt.total_seconds().dropna()
        if len(time_diffs) > 0:
            tempo_medio_dias = time_diffs.mean() / 86400  # Converter para dias
            tempo_medio_entre_publicacoes = round(float(tempo_medio_dias), 1)
    
    # PICO HORÁRIO DE PUBLICAÇÕES
    pico_horario = None
    if not df_publicar_validas.empty:
        df_publicar_validas['hora'] = df_publicar_validas['data_processada'].dt.hour
        publicacoes_por_hora = df_publicar_validas['hora'].value_counts()
        if not publicacoes_por_hora.empty:
            hora_pico = publicacoes_por_hora.idxmax()
            pico_horario = f"{hora_pico:02d}:00"
    
    # TAXA DE CRESCIMENTO
    taxa_crescimento = 0.0
    if publicacoes_semana > 0:
        duas_semanas_atras = hoje - timedelta(days=14)
        semana_anterior = df_publicar_validas[
            (df_publicar_validas['data_processada'].dt.date >= duas_semanas_atras) &
            (df_publicar_validas['data_processada'].dt.date < uma_semana_atras)
        ]
        publicacoes_semana_anterior = len(semana_anterior)
        
        semana_atual = df_publicar_validas[
            df_publicar_validas['data_processada'].dt.date >= uma_semana_atras
        ]
        publicacoes_semana_atual = len(semana_atual)
        
        if publicacoes_semana_anterior > 0:
            taxa_crescimento = round(
                ((publicacoes_semana_atual - publicacoes_semana_anterior) / publicacoes_semana_anterior) * 100, 1
            )
    
    # PROJEÇÕES
    proxima_semana = 0
    proximo_mes = 0
    
    if taxa_publicacao_diaria > 0:
        proxima_semana = round(taxa_publicacao_diaria * 7)
        proximo_mes = round(taxa_publicacao_diaria * 30)
    
    # DADOS PARA GRÁFICOS - PUBLICAÇÕES POR DIA (ÚLTIMOS 30 DIAS)
    publicacoes_por_dia_30_dias_data = {'labels': [], 'data': []}
    if not df_publicar_validas.empty:
        try:
            trinta_dias_atras = hoje - timedelta(days=30)
            ultimos_30_dias = df_publicar_validas[
                df_publicar_validas['data_processada'].dt.date >= trinta_dias_atras
            ]
            
            # Criar range completo dos últimos 30 dias
            datas_completas = [hoje - timedelta(days=x) for x in range(29, -1, -1)]
            
            if not ultimos_30_dias.empty:
                # Agrupar por dia
                publicacoes_dia = ultimos_30_dias.groupby(
                    ultimos_30_dias['data_processada'].dt.date
                ).size().sort_index()
                
                # Preencher dados para todos os dias
                for data in datas_completas:
                    label = data.strftime('%d/%m')
                    publicacoes_por_dia_30_dias_data['labels'].append(label)
                    
                    publicacoes_no_dia = publicacoes_dia.get(data, 0)
                    publicacoes_por_dia_30_dias_data['data'].append(int(publicacoes_no_dia))
            else:
                # Preencher com zeros se não houver dados nos últimos 30 dias
                for data in datas_completas:
                    label = data.strftime('%d/%m')
                    publicacoes_por_dia_30_dias_data['labels'].append(label)
                    publicacoes_por_dia_30_dias_data['data'].append(0)
                    
        except Exception as e:
            print(f"Erro ao processar publicações por dia (30 dias): {e}")
    
    # DADOS PARA GRÁFICOS - PUBLICAÇÕES POR HORA
    publicacoes_por_hora_data = {'labels': [], 'data': []}
    if not df_publicar_validas.empty:
        try:
            df_publicar_validas['hora'] = df_publicar_validas['data_processada'].dt.hour
            publicacoes_hora = df_publicar_validas['hora'].value_counts().sort_index()
            
            # Preencher horas faltantes
            horas_completas = range(24)
            for hora in horas_completas:
                publicacoes_por_hora_data['labels'].append(f"{hora:02d}:00")
                count = publicacoes_hora.get(hora, 0)
                publicacoes_por_hora_data['data'].append(int(count))
        except Exception as e:
            print(f"Erro ao processar publicações por hora: {e}")
    
    # DADOS PARA GRÁFICOS - PUBLICAÇÕES POR DIA DA SEMANA
    publicacoes_por_dia_semana_data = {'labels': [], 'data': []}
    if not df_publicar_validas.empty:
        try:
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            df_publicar_validas['dia_semana'] = df_publicar_validas['data_processada'].dt.dayofweek
            publicacoes_dia_semana = df_publicar_validas['dia_semana'].value_counts().sort_index()
            
            publicacoes_por_dia_semana_data['labels'] = dias_semana
            publicacoes_por_dia_semana_data['data'] = [
                int(publicacoes_dia_semana.get(dia, 0)) for dia in range(7)
            ]
        except Exception as e:
            print(f"Erro ao processar publicações por dia da semana: {e}")
    
    # ANÁLISE DE TENDÊNCIA
    status_tendencia = "estavel"
    direcao_tendencia = "neutra"
    
    if taxa_crescimento > 10:
        status_tendencia = "crescimento"
        direcao_tendencia = "positiva"
    elif taxa_crescimento < -10:
        status_tendencia = "queda"
        direcao_tendencia = "negativa"
    else:
        status_tendencia = "estavel"
        direcao_tendencia = "neutra"
    
    # ESTATÍSTICAS AVANÇADAS
    frequencia_publicacao = "baixa"
    if taxa_publicacao_diaria >= 5:
        frequencia_publicacao = "alta"
    elif taxa_publicacao_diaria >= 2:
        frequencia_publicacao = "media"
    else:
        frequencia_publicacao = "baixa"
    
    consistencia = "irregular"
    if total_publicacoes >= 10 and tempo_medio_entre_publicacoes and tempo_medio_entre_publicacoes <= 7:
        consistencia = "regular"
    
    velocidade_crescimento = "estavel"
    if taxa_crescimento > 20:
        velocidade_crescimento = "rapida"
    elif taxa_crescimento < -20:
        velocidade_crescimento = "lenta"
    
    # MÉTRICAS RESUMO
    metricas_resumo = {
        'total_publicacoes': int(total_publicacoes),
        'publicacoes_hoje': int(publicacoes_hoje),
        'publicacoes_semana': int(publicacoes_semana),
        'taxa_publicacao_diaria': float(taxa_publicacao_diaria),
        'ultima_publicacao': ultima_publicacao,
        'tempo_desde_ultima_publicacao': tempo_desde_ultima_publicacao,
        'tempo_medio_entre_publicacoes': tempo_medio_entre_publicacoes,
        'pico_horario': pico_horario,
        'taxa_crescimento': float(taxa_crescimento)
    }
    
    # MÉTRICAS TEMPORAIS DETALHADAS
    metricas_temporais = {
        'publicacoes_ultima_hora': int(publicacoes_ultima_hora),
        'publicacoes_ultimas_24h': int(publicacoes_ultimas_24h),
        'publicacoes_ultima_semana': int(publicacoes_semana),
        'publicacoes_ultimo_mes': int(publicacoes_ultimo_mes)
    }
    
    # DADOS PARA GRÁFICOS
    dados_graficos = {
        'publicacoes_por_dia_30_dias': publicacoes_por_dia_30_dias_data,
        'publicacoes_por_hora': publicacoes_por_hora_data,
        'publicacoes_por_dia_semana': publicacoes_por_dia_semana_data
    }
    
    # ANÁLISE DE TENDÊNCIA
    tendencia = {
        'status': status_tendencia,
        'variacao': float(taxa_crescimento),
        'direcao': direcao_tendencia
    }
    
    # PROJEÇÕES
    projecao = {
        'proxima_semana': int(proxima_semana),
        'proximo_mes': int(proximo_mes)
    }
    
    # ESTATÍSTICAS AVANÇADAS
    estatisticas_avancadas = {
        'frequencia_publicacao': frequencia_publicacao,
        'consistencia': consistencia,
        'velocidade_crescimento': velocidade_crescimento
    }
    
    # RESULTADO FINAL - APENAS PUBLICAÇÕES
    resultado_publicar = {
        'status': 'sucesso',
        'timestamp': datetime.now().isoformat(),
        'tipo': 'metricas_publicar',
        'metricas_resumo': metricas_resumo,
        'metricas_temporais': metricas_temporais,
        'dados_graficos': dados_graficos,
        'tendencia': tendencia,
        'projecao': projecao,
        'estatisticas_avancadas': estatisticas_avancadas,
        'detalhes_processamento': {
            'registros_processados': len(df_publicar_validas),
            'periodo_analisado': {
                'inicio': df_publicar_validas['data_processada'].min().isoformat() if not df_publicar_validas.empty else None,
                'fim': df_publicar_validas['data_processada'].max().isoformat() if not df_publicar_validas.empty else None
            },
            'dias_com_publicacoes': len([x for x in publicacoes_por_dia_30_dias_data['data'] if x > 0])
        }
    }
    
    print(f"DEBUG - Processamento de publicações concluído:")
    print(f"  Total de publicações: {total_publicacoes}")
    print(f"  Última publicação: {ultima_publicacao}")
    print(f"  Tempo desde última publicação: {tempo_desde_ultima_publicacao} horas")
    print(f"  Taxa publicação diária: {taxa_publicacao_diaria}")
    
    result.append({
        "json": resultado_publicar,
        "binary": {},
        "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
    })

except Exception as e:
    print(f"DEBUG - Erro crítico no processamento de publicações: {str(e)}")
    import traceback
    print(f"DEBUG - Traceback: {traceback.format_exc()}")
    
    error_info = {
        "status": "erro",
        "timestamp": datetime.now().isoformat(),
        "tipo": 'metricas_publicar',
        "error": str(e)
    }
    result.append({
        "json": error_info,
        "binary": {},
        "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
    })

return result
