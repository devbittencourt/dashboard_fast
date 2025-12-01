import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

result = []

try:
    # Coletar todos os dados de cadastro
    cadastrar_data = []
    
    for item in items:
        if 'json' in item and item['json']:
            item_data = item['json']
            cadastrar_data.append(item_data)
    
    # Criar DataFrame apenas com dados de cadastro
    df_cadastrar = pd.DataFrame(cadastrar_data) if cadastrar_data else pd.DataFrame()
    
    print(f"DEBUG - Total de cadastros recebidos: {len(df_cadastrar)}")
    
    # Se não há dados, retornar estrutura vazia
    if df_cadastrar.empty:
        print("DEBUG - Nenhum cadastro recebido")
        
        resultado_cadastrar = {
            'status': 'sucesso',
            'timestamp': datetime.now().isoformat(),
            'tipo': 'metricas_cadastrar',
            'metricas_resumo': {
                'total_cadastros': 0,
                'cadastros_hoje': 0,
                'cadastros_semana': 0,
                'taxa_cadastro_diaria': 0,
                'ultimo_cadastro': None,
                'tempo_medio_entre_cadastros': None,
                'taxa_crescimento': 0.0
            },
            'metricas_temporais': {
                'cadastros_ultima_hora': 0,
                'cadastros_ultimas_24h': 0,
                'cadastros_ultima_semana': 0,
                'cadastros_ultimo_mes': 0
            },
            'dados_graficos': {
                'cadastros_por_dia_30_dias': {'labels': [], 'data': []},
                'cadastros_por_hora': {'labels': [], 'data': []},
                'cadastros_por_dia_semana': {'labels': [], 'data': []}
            },
            'tendencia': {
                'status': 'estavel',
                'variacao': 0.0,
                'direcao': 'neutra'
            },
            'projecao': {
                'proxima_semana': 0,
                'proximo_mes': 0
            }
        }
        
        result.append({
            "json": resultado_cadastrar,
            "binary": {},
            "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
        })
        return result

    print(f"DEBUG - Colunas disponíveis nos cadastros: {df_cadastrar.columns.tolist()}")
    
    # DATAS PARA CÁLCULOS
    agora = datetime.now().replace(tzinfo=None)
    hoje = agora.date()
    uma_semana_atras = hoje - timedelta(days=7)
    um_mes_atras = hoje - timedelta(days=30)
    uma_hora_atras = agora - timedelta(hours=1)
    um_dia_atras = agora - timedelta(days=1)
    
    # PROCESSAR DATAS
    df_cadastrar_processed = df_cadastrar.copy()
    
    # Encontrar coluna de data
    date_column = None
    for col in ['created_at', 'timestamp', 'event_time']:
        if col in df_cadastrar.columns:
            date_column = col
            break
    
    if not date_column:
        print("DEBUG - Nenhuma coluna de data encontrada")
        for col in df_cadastrar.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_column = col
                break
    
    if date_column:
        df_cadastrar_processed['data_processada'] = pd.to_datetime(
            df_cadastrar_processed[date_column], errors='coerce'
        ).dt.tz_localize(None)
        df_cadastrar_validas = df_cadastrar_processed[df_cadastrar_processed['data_processada'].notna()]
    else:
        print("DEBUG - Criando timestamps fictícios")
        df_cadastrar_validas = df_cadastrar_processed.copy()
        start_time = datetime.now() - timedelta(days=30)
        df_cadastrar_validas['data_processada'] = [
            start_time + timedelta(hours=i) for i in range(len(df_cadastrar_validas))
        ]
    
    print(f"DEBUG - Cadastros válidos com data: {len(df_cadastrar_validas)}")
    
    # MÉTRICAS BÁSICAS
    total_cadastros = len(df_cadastrar_validas)
    
    # MÉTRICAS TEMPORAIS
    cadastros_hoje = len(df_cadastrar_validas[
        df_cadastrar_validas['data_processada'].dt.date == hoje
    ])
    
    cadastros_semana = len(df_cadastrar_validas[
        df_cadastrar_validas['data_processada'].dt.date >= uma_semana_atras
    ])
    
    cadastros_ultima_hora = len(df_cadastrar_validas[
        df_cadastrar_validas['data_processada'] >= uma_hora_atras
    ])
    
    cadastros_ultimas_24h = len(df_cadastrar_validas[
        df_cadastrar_validas['data_processada'] >= um_dia_atras
    ])
    
    cadastros_ultimo_mes = len(df_cadastrar_validas[
        df_cadastrar_validas['data_processada'].dt.date >= um_mes_atras
    ])
    
    # ÚLTIMO CADASTRO
    ultimo_cadastro = None
    if not df_cadastrar_validas.empty:
        ultimo_cadastro_dt = df_cadastrar_validas['data_processada'].max()
        ultimo_cadastro = ultimo_cadastro_dt.isoformat()
    
    # TAXA DE CADASTRO DIÁRIA (média dos últimos 7 dias)
    taxa_cadastro_diaria = 0
    if cadastros_semana > 0:
        ultimos_7_dias = df_cadastrar_validas[
            df_cadastrar_validas['data_processada'].dt.date >= uma_semana_atras
        ]
        if not ultimos_7_dias.empty:
            cadastros_por_dia = ultimos_7_dias.groupby(
                ultimos_7_dias['data_processada'].dt.date
            ).size()
            taxa_cadastro_diaria = round(float(cadastros_por_dia.mean()), 1)
    
    # TEMPO MÉDIO ENTRE CADASTROS
    tempo_medio_entre_cadastros = None
    if len(df_cadastrar_validas) > 1:
        df_cadastrar_sorted = df_cadastrar_validas.sort_values('data_processada')
        time_diffs = df_cadastrar_sorted['data_processada'].diff().dt.total_seconds().dropna()
        if len(time_diffs) > 0:
            tempo_medio_horas = time_diffs.mean() / 3600  # Converter para horas
            tempo_medio_entre_cadastros = round(float(tempo_medio_horas), 1)
    
    # PICO HORÁRIO DE CADASTROS
    pico_horario = None
    if not df_cadastrar_validas.empty:
        df_cadastrar_validas['hora'] = df_cadastrar_validas['data_processada'].dt.hour
        cadastros_por_hora = df_cadastrar_validas['hora'].value_counts()
        if not cadastros_por_hora.empty:
            hora_pico = cadastros_por_hora.idxmax()
            pico_horario = f"{hora_pico:02d}:00"
    
    # TAXA DE CRESCIMENTO
    taxa_crescimento = 0.0
    if cadastros_semana > 0:
        duas_semanas_atras = hoje - timedelta(days=14)
        semana_anterior = df_cadastrar_validas[
            (df_cadastrar_validas['data_processada'].dt.date >= duas_semanas_atras) &
            (df_cadastrar_validas['data_processada'].dt.date < uma_semana_atras)
        ]
        cadastros_semana_anterior = len(semana_anterior)
        
        semana_atual = df_cadastrar_validas[
            df_cadastrar_validas['data_processada'].dt.date >= uma_semana_atras
        ]
        cadastros_semana_atual = len(semana_atual)
        
        if cadastros_semana_anterior > 0:
            taxa_crescimento = round(
                ((cadastros_semana_atual - cadastros_semana_anterior) / cadastros_semana_anterior) * 100, 1
            )
    
    # PROJEÇÕES
    proxima_semana = 0
    proximo_mes = 0
    
    if taxa_cadastro_diaria > 0:
        proxima_semana = round(taxa_cadastro_diaria * 7)
        proximo_mes = round(taxa_cadastro_diaria * 30)
    
    # DADOS PARA GRÁFICOS - CADASTROS POR DIA (ÚLTIMOS 30 DIAS)
    cadastros_por_dia_30_dias_data = {'labels': [], 'data': []}
    if not df_cadastrar_validas.empty:
        try:
            trinta_dias_atras = hoje - timedelta(days=30)
            ultimos_30_dias = df_cadastrar_validas[
                df_cadastrar_validas['data_processada'].dt.date >= trinta_dias_atras
            ]
            
            # Criar range completo dos últimos 30 dias
            datas_completas = [hoje - timedelta(days=x) for x in range(29, -1, -1)]
            
            if not ultimos_30_dias.empty:
                # Agrupar por dia
                cadastros_dia = ultimos_30_dias.groupby(
                    ultimos_30_dias['data_processada'].dt.date
                ).size().sort_index()
                
                # Preencher dados para todos os dias
                for data in datas_completas:
                    label = data.strftime('%d/%m')
                    cadastros_por_dia_30_dias_data['labels'].append(label)
                    
                    cadastros_no_dia = cadastros_dia.get(data, 0)
                    cadastros_por_dia_30_dias_data['data'].append(int(cadastros_no_dia))
            else:
                # Preencher com zeros se não houver dados nos últimos 30 dias
                for data in datas_completas:
                    label = data.strftime('%d/%m')
                    cadastros_por_dia_30_dias_data['labels'].append(label)
                    cadastros_por_dia_30_dias_data['data'].append(0)
                    
        except Exception as e:
            print(f"Erro ao processar cadastros por dia (30 dias): {e}")
    
    # DADOS PARA GRÁFICOS - CADASTROS POR HORA
    cadastros_por_hora_data = {'labels': [], 'data': []}
    if not df_cadastrar_validas.empty:
        try:
            df_cadastrar_validas['hora'] = df_cadastrar_validas['data_processada'].dt.hour
            cadastros_hora = df_cadastrar_validas['hora'].value_counts().sort_index()
            
            # Preencher horas faltantes
            horas_completas = range(24)
            for hora in horas_completas:
                cadastros_por_hora_data['labels'].append(f"{hora:02d}:00")
                count = cadastros_hora.get(hora, 0)
                cadastros_por_hora_data['data'].append(int(count))
        except Exception as e:
            print(f"Erro ao processar cadastros por hora: {e}")
    
    # DADOS PARA GRÁFICOS - CADASTROS POR DIA DA SEMANA
    cadastros_por_dia_semana_data = {'labels': [], 'data': []}
    if not df_cadastrar_validas.empty:
        try:
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            df_cadastrar_validas['dia_semana'] = df_cadastrar_validas['data_processada'].dt.dayofweek
            cadastros_dia_semana = df_cadastrar_validas['dia_semana'].value_counts().sort_index()
            
            cadastros_por_dia_semana_data['labels'] = dias_semana
            cadastros_por_dia_semana_data['data'] = [
                int(cadastros_dia_semana.get(dia, 0)) for dia in range(7)
            ]
        except Exception as e:
            print(f"Erro ao processar cadastros por dia da semana: {e}")
    
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
    
    # MÉTRICAS RESUMO
    metricas_resumo = {
        'total_cadastros': int(total_cadastros),
        'cadastros_hoje': int(cadastros_hoje),
        'cadastros_semana': int(cadastros_semana),
        'taxa_cadastro_diaria': float(taxa_cadastro_diaria),
        'ultimo_cadastro': ultimo_cadastro,
        'tempo_medio_entre_cadastros': tempo_medio_entre_cadastros,
        'pico_horario': pico_horario,
        'taxa_crescimento': float(taxa_crescimento)
    }
    
    # MÉTRICAS TEMPORAIS DETALHADAS
    metricas_temporais = {
        'cadastros_ultima_hora': int(cadastros_ultima_hora),
        'cadastros_ultimas_24h': int(cadastros_ultimas_24h),
        'cadastros_ultima_semana': int(cadastros_semana),
        'cadastros_ultimo_mes': int(cadastros_ultimo_mes)
    }
    
    # DADOS PARA GRÁFICOS
    dados_graficos = {
        'cadastros_por_dia_30_dias': cadastros_por_dia_30_dias_data,
        'cadastros_por_hora': cadastros_por_hora_data,
        'cadastros_por_dia_semana': cadastros_por_dia_semana_data
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
    
    # RESULTADO FINAL - APENAS CADASTROS
    resultado_cadastrar = {
        'status': 'sucesso',
        'timestamp': datetime.now().isoformat(),
        'tipo': 'metricas_cadastrar',
        'metricas_resumo': metricas_resumo,
        'metricas_temporais': metricas_temporais,
        'dados_graficos': dados_graficos,
        'tendencia': tendencia,
        'projecao': projecao,
        'detalhes_processamento': {
            'registros_processados': len(df_cadastrar_validas),
            'periodo_analisado': {
                'inicio': df_cadastrar_validas['data_processada'].min().isoformat() if not df_cadastrar_validas.empty else None,
                'fim': df_cadastrar_validas['data_processada'].max().isoformat() if not df_cadastrar_validas.empty else None
            },
            'dias_com_cadastros': len([x for x in cadastros_por_dia_30_dias_data['data'] if x > 0])
        }
    }
    
    print(f"DEBUG - Processamento de cadastros concluído:")
    print(f"  Total de cadastros: {total_cadastros}")
    print(f"  Cadastros hoje: {cadastros_hoje}")
    print(f"  Último cadastro: {ultimo_cadastro}")
    print(f"  Taxa cadastro diária: {taxa_cadastro_diaria}")
    print(f"  Tempo médio entre cadastros: {tempo_medio_entre_cadastros} horas")
    
    result.append({
        "json": resultado_cadastrar,
        "binary": {},
        "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
    })

except Exception as e:
    print(f"DEBUG - Erro crítico no processamento de cadastros: {str(e)}")
    import traceback
    print(f"DEBUG - Traceback: {traceback.format_exc()}")
    
    error_info = {
        "status": "erro",
        "timestamp": datetime.now().isoformat(),
        "tipo": 'metricas_cadastrar',
        "error": str(e)
    }
    result.append({
        "json": error_info,
        "binary": {},
        "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
    })

return result
