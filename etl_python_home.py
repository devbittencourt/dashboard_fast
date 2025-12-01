import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

result = []

try:
    # Coletar todos os dados da Home
    home_data = []
    
    for item in items:
        if 'json' in item and item['json']:
            item_data = item['json']
            home_data.append(item_data)
    
    # Criar DataFrame apenas com dados da Home
    df_home = pd.DataFrame(home_data) if home_data else pd.DataFrame()
    
    print(f"DEBUG - Total de visitas à Home recebidas: {len(df_home)}")
    
    # Se não há dados, retornar estrutura vazia
    if df_home.empty:
        print("DEBUG - Nenhuma visita à Home recebida")
        
        resultado_home = {
            'status': 'sucesso',
            'timestamp': datetime.now().isoformat(),
            'tipo': 'metricas_home',
            'metricas_resumo': {
                'total_visitas': 0,
                'visitas_hoje': 0,
                'visitas_semana': 0,
                'taxa_visitas_diaria': 0,
                'tempo_medio_sessao': None,
                'pico_horario': None,
                'taxa_crescimento': 0.0
            },
            'metricas_temporais': {
                'visitas_ultima_hora': 0,
                'visitas_ultimas_24h': 0,
                'visitas_ultima_semana': 0,
                'visitas_ultimo_mes': 0
            },
            'dados_graficos': {
                'visitas_por_dia_30_dias': {'labels': [], 'data': []},
                'visitas_por_hora': {'labels': [], 'data': []},
                'visitas_por_dia_semana': {'labels': [], 'data': []}
            },
            'tendencia': {
                'status': 'estavel',
                'variacao': 0.0,
                'direcao': 'neutra'
            }
        }
        
        result.append({
            "json": resultado_home,
            "binary": {},
            "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
        })
        return result

    print(f"DEBUG - Colunas disponíveis na Home: {df_home.columns.tolist()}")
    
    # DATAS PARA CÁLCULOS - DEFINIR TODAS COM TIMEZONE UTC
    agora = datetime.now().replace(tzinfo=None)  # Remover timezone para comparação
    hoje = agora.date()
    uma_semana_atras = hoje - timedelta(days=7)
    um_mes_atras = hoje - timedelta(days=30)
    uma_hora_atras = agora - timedelta(hours=1)
    um_dia_atras = agora - timedelta(days=1)
    
    # PROCESSAR DATAS - CORREÇÃO DO TIMEZONE
    df_home_processed = df_home.copy()
    
    # Encontrar coluna de data (prioridade: created_at, timestamp)
    date_column = None
    for col in ['created_at', 'timestamp', 'event_time']:
        if col in df_home.columns:
            date_column = col
            break
    
    if not date_column:
        print("DEBUG - Nenhuma coluna de data encontrada")
        # Usar a primeira coluna que parece ser de data
        for col in df_home.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_column = col
                break
    
    if date_column:
        # Converter para datetime e REMOVER TIMEZONE para compatibilidade
        df_home_processed['data_processada'] = pd.to_datetime(
            df_home_processed[date_column], errors='coerce'
        ).dt.tz_localize(None)  # Remove timezone information
        
        df_home_validas = df_home_processed[df_home_processed['data_processada'].notna()]
    else:
        print("DEBUG - Criando timestamps fictícios baseados na ordem")
        df_home_validas = df_home_processed.copy()
        # Criar timestamps sequenciais baseados na ordem dos registros (sem timezone)
        start_time = datetime.now() - timedelta(days=30)
        df_home_validas['data_processada'] = [
            start_time + timedelta(hours=i) for i in range(len(df_home_validas))
        ]
    
    print(f"DEBUG - Registros válidos com data: {len(df_home_validas)}")
    if not df_home_validas.empty:
        print(f"DEBUG - Primeira data: {df_home_validas['data_processada'].min()}")
        print(f"DEBUG - Última data: {df_home_validas['data_processada'].max()}")
    
    # MÉTRICAS BÁSICAS
    total_visitas = len(df_home_validas)
    
    # MÉTRICAS TEMPORAIS - USAR DATAS SEM TIMEZONE
    visitas_hoje = len(df_home_validas[
        df_home_validas['data_processada'].dt.date == hoje
    ])
    
    visitas_semana = len(df_home_validas[
        df_home_validas['data_processada'].dt.date >= uma_semana_atras
    ])
    
    visitas_ultima_hora = len(df_home_validas[
        df_home_validas['data_processada'] >= uma_hora_atras
    ])
    
    visitas_ultimas_24h = len(df_home_validas[
        df_home_validas['data_processada'] >= um_dia_atras
    ])
    
    visitas_ultimo_mes = len(df_home_validas[
        df_home_validas['data_processada'].dt.date >= um_mes_atras
    ])
    
    # TAXA DE VISITAS DIÁRIA (média dos últimos 7 dias)
    taxa_visitas_diaria = 0
    if visitas_semana > 0:
        ultimos_7_dias = df_home_validas[
            df_home_validas['data_processada'].dt.date >= uma_semana_atras
        ]
        if not ultimos_7_dias.empty:
            visitas_por_dia = ultimos_7_dias.groupby(
                ultimos_7_dias['data_processada'].dt.date
            ).size()
            taxa_visitas_diaria = round(float(visitas_por_dia.mean()), 1)
    
    # TEMPO MÉDIO ENTRE SESSÕES
    tempo_medio_sessao = None
    if len(df_home_validas) > 1:
        df_home_sorted = df_home_validas.sort_values('data_processada')
        time_diffs = df_home_sorted['data_processada'].diff().dt.total_seconds().dropna()
        if len(time_diffs) > 0:
            tempo_medio_minutos = time_diffs.mean() / 60
            tempo_medio_sessao = round(float(tempo_medio_minutos), 1)
    
    # PICO HORÁRIO
    pico_horario = None
    if not df_home_validas.empty:
        df_home_validas['hora'] = df_home_validas['data_processada'].dt.hour
        visitas_por_hora = df_home_validas['hora'].value_counts()
        if not visitas_por_hora.empty:
            hora_pico = visitas_por_hora.idxmax()
            pico_horario = f"{hora_pico:02d}:00"
    
    # TAXA DE CRESCIMENTO (comparação semana anterior vs semana atual)
    taxa_crescimento = 0.0
    if visitas_semana > 0:
        duas_semanas_atras = hoje - timedelta(days=14)
        semana_anterior = df_home_validas[
            (df_home_validas['data_processada'].dt.date >= duas_semanas_atras) &
            (df_home_validas['data_processada'].dt.date < uma_semana_atras)
        ]
        visitas_semana_anterior = len(semana_anterior)
        
        semana_atual = df_home_validas[
            df_home_validas['data_processada'].dt.date >= uma_semana_atras
        ]
        visitas_semana_atual = len(semana_atual)
        
        if visitas_semana_anterior > 0:
            taxa_crescimento = round(
                ((visitas_semana_atual - visitas_semana_anterior) / visitas_semana_anterior) * 100, 1
            )
    
    # DADOS PARA GRÁFICOS - VISITAS POR DIA (ÚLTIMOS 30 DIAS)
    visitas_por_dia_30_dias_data = {'labels': [], 'data': []}
    if not df_home_validas.empty:
        try:
            # Últimos 30 dias
            trinta_dias_atras = hoje - timedelta(days=30)
            ultimos_30_dias = df_home_validas[
                df_home_validas['data_processada'].dt.date >= trinta_dias_atras
            ]
            
            if not ultimos_30_dias.empty:
                # Agrupar por dia
                visitas_dia = ultimos_30_dias.groupby(
                    ultimos_30_dias['data_processada'].dt.date
                ).size().sort_index()
                
                # Criar range completo dos últimos 30 dias
                datas_completas = [hoje - timedelta(days=x) for x in range(29, -1, -1)]
                
                # Preencher dados para todos os dias (mesmo os sem visitas)
                for data in datas_completas:
                    # Formatar label (DD/MM)
                    label = data.strftime('%d/%m')
                    visitas_por_dia_30_dias_data['labels'].append(label)
                    
                    # Buscar visitas do dia ou usar 0 se não houver
                    visitas_no_dia = visitas_dia.get(data, 0)
                    visitas_por_dia_30_dias_data['data'].append(int(visitas_no_dia))
                    
        except Exception as e:
            print(f"Erro ao processar visitas por dia (30 dias): {e}")
    
    # DADOS PARA GRÁFICOS - VISITAS POR HORA (CORRIGIDO)
    visitas_por_hora_data = {'labels': [], 'data': []}
    if not df_home_validas.empty:
        try:
            df_home_validas['hora'] = df_home_validas['data_processada'].dt.hour
            visitas_hora = df_home_validas['hora'].value_counts().sort_index()
            
            # Preencher horas faltantes - GARANTIR QUE SEJA NÚMEROS
            horas_completas = range(24)
            for hora in horas_completas:
                visitas_por_hora_data['labels'].append(f"{hora:02d}:00")
                count = visitas_hora.get(hora, 0)
                # Garantir que seja um número inteiro, não um dicionário
                visitas_por_hora_data['data'].append(int(count))
        except Exception as e:
            print(f"Erro ao processar visitas por hora: {e}")
    
    # DADOS PARA GRÁFICOS - VISITAS POR DIA DA SEMANA (CORRIGIDO)
    visitas_por_dia_semana_data = {'labels': [], 'data': []}
    if not df_home_validas.empty:
        try:
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            df_home_validas['dia_semana'] = df_home_validas['data_processada'].dt.dayofweek
            visitas_dia_semana = df_home_validas['dia_semana'].value_counts().sort_index()
            
            visitas_por_dia_semana_data['labels'] = dias_semana
            # Preencher dados para todos os dias da semana - GARANTIR NÚMEROS
            visitas_por_dia_semana_data['data'] = [
                int(visitas_dia_semana.get(dia, 0)) for dia in range(7)
            ]
        except Exception as e:
            print(f"Erro ao processar visitas por dia da semana: {e}")
        
    # ANÁLISE DE TENDÊNCIA
    status_tendencia = "estavel"
    direcao_tendencia = "neutra"
    
    if taxa_crescimento > 5:
        status_tendencia = "crescimento"
        direcao_tendencia = "positiva"
    elif taxa_crescimento < -5:
        status_tendencia = "queda"
        direcao_tendencia = "negativa"
    else:
        status_tendencia = "estavel"
        direcao_tendencia = "neutra"
    
    # MÉTRICAS RESUMO
    metricas_resumo = {
        'total_visitas': int(total_visitas),
        'visitas_hoje': int(visitas_hoje),
        'visitas_semana': int(visitas_semana),
        'taxa_visitas_diaria': float(taxa_visitas_diaria),
        'tempo_medio_sessao': tempo_medio_sessao,
        'pico_horario': pico_horario,
        'taxa_crescimento': float(taxa_crescimento)
    }
    
    # MÉTRICAS TEMPORAIS DETALHADAS
    metricas_temporais = {
        'visitas_ultima_hora': int(visitas_ultima_hora),
        'visitas_ultimas_24h': int(visitas_ultimas_24h),
        'visitas_ultima_semana': int(visitas_semana),
        'visitas_ultimo_mes': int(visitas_ultimo_mes)
    }
    
    # DADOS PARA GRÁFICOS
    dados_graficos = {
        'visitas_por_dia_30_dias': visitas_por_dia_30_dias_data,
        'visitas_por_hora': visitas_por_hora_data,
        'visitas_por_dia_semana': visitas_por_dia_semana_data
    }
    
    # ANÁLISE DE TENDÊNCIA
    tendencia = {
        'status': status_tendencia,
        'variacao': float(taxa_crescimento),
        'direcao': direcao_tendencia
    }
    
    # RESULTADO FINAL - APENAS HOME
    resultado_home = {
        'status': 'sucesso',
        'timestamp': datetime.now().isoformat(),
        'tipo': 'metricas_home',
        'metricas_resumo': metricas_resumo,
        'metricas_temporais': metricas_temporais,
        'dados_graficos': dados_graficos,
        'tendencia': tendencia,
        'detalhes_processamento': {
            'registros_processados': len(df_home_validas),
            'periodo_analisado': {
                'inicio': df_home_validas['data_processada'].min().isoformat() if not df_home_validas.empty else None,
                'fim': df_home_validas['data_processada'].max().isoformat() if not df_home_validas.empty else None
            },
            'dias_com_dados': len(visitas_por_dia_30_dias_data['data']) if visitas_por_dia_30_dias_data['data'] else 0
        }
    }
    
    print(f"DEBUG - Processamento da Home concluído:")
    print(f"  Total de visitas: {total_visitas}")
    print(f"  Visitas hoje: {visitas_hoje}")
    print(f"  Visitas última hora: {visitas_ultima_hora}")
    print(f"  Taxa crescimento: {taxa_crescimento}%")
    print(f"  Tempo médio entre sessões: {tempo_medio_sessao} min")
    print(f"  Dias analisados no gráfico: {len(visitas_por_dia_30_dias_data['labels'])}")
    
    result.append({
        "json": resultado_home,
        "binary": {},
        "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
    })

except Exception as e:
    print(f"DEBUG - Erro crítico no processamento da Home: {str(e)}")
    import traceback
    print(f"DEBUG - Traceback: {traceback.format_exc()}")
    
    error_info = {
        "status": "erro",
        "timestamp": datetime.now().isoformat(),
        "tipo": 'metricas_home',
        "error": str(e)
    }
    result.append({
        "json": error_info,
        "binary": {},
        "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
    })

return result
