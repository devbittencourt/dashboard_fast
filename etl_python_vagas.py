import pandas as pd
import numpy as np
from datetime import datetime
import re
import json

result = []

try:
    # Coletar todos os dados de vagas
    vagas_data = []
    
    for item in items:
        if 'json' in item and item['json']:
            item_data = item['json']
            
            # Verificar se é uma vaga (tem título e empresa)
            if ('titulo' in item_data and 'empresa' in item_data and 
                item_data['titulo'] and item_data['empresa']):
                vagas_data.append(item_data)
    
    # Criar DataFrame apenas com vagas
    df_vagas = pd.DataFrame(vagas_data) if vagas_data else pd.DataFrame()
    
    print(f"DEBUG - Total de vagas recebidas: {len(df_vagas)}")
    
    # Se não há vagas, retornar estrutura vazia
    if df_vagas.empty:
        print("DEBUG - Nenhuma vaga recebida para processamento")
        
        resultado_vagas = {
            'status': 'sucesso',
            'timestamp': datetime.now().isoformat(),
            'tipo': 'metricas_vagas',
            'metricas_resumo': {
                'total_vagas': 0,
                'total_visualizacoes': 0,
                'total_cliques': 0,
                'ctr_medio': 0.0,
                'vagas_alto_engajamento': 0,
                'vagas_com_visualizacao': 0,
                'taxa_engajamento': 0.0
            },
            'metricas_temporais': {
                'vagas_hoje': 0,
                'vagas_semana': 0,
                'taxa_cadastro_diario': 0
            },
            'dados_graficos': {
                'regions_data': {'labels': [], 'visualizacoes': []},
                'modalidade_data': {'labels': [], 'data': []},
                'salario_data': {'labels': [], 'data': []}
            },
            'tabela_vagas_completa': [],
            'vagas_alto_engajamento_lista': []
        }
        
        result.append({
            "json": resultado_vagas,
            "binary": {},
            "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
        })
        return result

    print(f"DEBUG - Colunas disponíveis nas vagas: {df_vagas.columns.tolist()}")
    
    # DATAS PARA CÁLCULOS
    hoje = datetime.now().date()
    uma_semana_atras = hoje - pd.Timedelta(days=7)
    
    # MÉTRICAS BÁSICAS
    total_vagas = len(df_vagas)
    
    # Garantir que as colunas numéricas existam e converter
    if 'visualizacao' not in df_vagas.columns:
        df_vagas['visualizacao'] = 0
    if 'click_link' not in df_vagas.columns:
        df_vagas['click_link'] = 0
    
    df_vagas['visualizacao'] = pd.to_numeric(df_vagas['visualizacao'], errors='coerce').fillna(0).astype(int)
    df_vagas['click_link'] = pd.to_numeric(df_vagas['click_link'], errors='coerce').fillna(0).astype(int)
    
    # Calcular métricas de performance
    total_visualizacoes = int(df_vagas['visualizacao'].sum())
    total_cliques = int(df_vagas['click_link'].sum())
    
    # Calcular CTR individual para cada vaga
    df_vagas['ctr_individual'] = 0.0
    mask_visualizacoes = df_vagas['visualizacao'] > 0
    df_vagas.loc[mask_visualizacoes, 'ctr_individual'] = (
        df_vagas.loc[mask_visualizacoes, 'click_link'] / 
        df_vagas.loc[mask_visualizacoes, 'visualizacao'] * 100
    ).round(2)
    
    # Métricas de engajamento
    vagas_com_visualizacao = len(df_vagas[df_vagas['visualizacao'] > 0])
    vagas_alto_engajamento = len(df_vagas[df_vagas['ctr_individual'] > 20])
    
    # CTR médio (apenas para vagas com visualizações)
    ctr_medio = float(round(df_vagas.loc[mask_visualizacoes, 'ctr_individual'].mean(), 2)) if mask_visualizacoes.any() else 0.0
    
    # Taxa de engajamento geral
    taxa_engajamento = round((vagas_com_visualizacao / total_vagas * 100), 2) if total_vagas > 0 else 0.0
    
    # MÉTRICAS TEMPORAIS
    vagas_hoje = 0
    vagas_semana = 0
    taxa_cadastro_diario = 0
    
    # Processar datas das vagas
    if 'data_criacao' in df_vagas.columns:
        try:
            df_vagas['data_criacao_dt'] = pd.to_datetime(df_vagas['data_criacao'], errors='coerce')
            df_vagas_validas = df_vagas[df_vagas['data_criacao_dt'].notna()]
            
            if not df_vagas_validas.empty:
                vagas_hoje = len(df_vagas_validas[df_vagas_validas['data_criacao_dt'].dt.date == hoje])
                vagas_semana = len(df_vagas_validas[df_vagas_validas['data_criacao_dt'].dt.date >= uma_semana_atras])
                
                # Taxa de cadastro diário (últimos 7 dias)
                ultimos_7_dias = df_vagas_validas[df_vagas_validas['data_criacao_dt'].dt.date >= uma_semana_atras]
                if not ultimos_7_dias.empty:
                    vagas_por_dia = ultimos_7_dias.groupby(ultimos_7_dias['data_criacao_dt'].dt.date).size()
                    taxa_cadastro_diario = round(float(vagas_por_dia.mean()), 1)
        except Exception as e:
            print(f"Erro no processamento de datas: {e}")
    
    # DADOS PARA GRÁFICOS - REGIÕES
    regions_data = {'labels': [], 'visualizacoes': []}
    if 'regiao' in df_vagas.columns:
        try:
            # Limpar dados de região
            def limpar_regiao(regiao):
                if pd.isna(regiao) or regiao == '' or regiao is None:
                    return 'Não informado'
                regiao_str = str(regiao)
                # Remover números entre parênteses no final
                regiao_limpa = re.sub(r'\s*\(\d+\)\s*$', '', regiao_str)
                return regiao_limpa.strip()
            
            df_vagas['regiao_limpa'] = df_vagas['regiao'].apply(limpar_regiao)
            
            # Agrupar por região
            regiao_stats = df_vagas.groupby('regiao_limpa').agg({
                'visualizacao': 'sum',
                'id': 'count'
            }).rename(columns={'id': 'quantidade'})
            
            # Ordenar por visualizações e pegar top 10
            regiao_stats = regiao_stats.sort_values('visualizacao', ascending=False).head(10)
            
            regions_data['labels'] = regiao_stats.index.tolist()
            regions_data['visualizacoes'] = regiao_stats['visualizacao'].astype(int).tolist()
            
        except Exception as e:
            print(f"Erro ao processar dados de região: {e}")
    
    # DADOS PARA GRÁFICOS - MODALIDADE
    modalidade_data = {'labels': [], 'data': []}
    if 'modalidade' in df_vagas.columns:
        try:
            modalidade_stats = df_vagas['modalidade'].value_counts()
            modalidade_data['labels'] = modalidade_stats.index.tolist()
            modalidade_data['data'] = modalidade_stats.values.tolist()
        except Exception as e:
            print(f"Erro ao processar dados de modalidade: {e}")
    
    # DADOS PARA GRÁFICOS - SALÁRIO
    salario_data = {'labels': [], 'data': []}
    if 'salario_numero' in df_vagas.columns:
        try:
            # Criar faixas salariais
            df_vagas['salario_numero'] = pd.to_numeric(df_vagas['salario_numero'], errors='coerce')
            df_salario_valido = df_vagas[df_vagas['salario_numero'].notna()]
            
            if not df_salario_valido.empty:
                bins = [0, 2000, 4000, 6000, 8000, 10000, 15000, 20000, float('inf')]
                labels = ['Até 2k', '2k-4k', '4k-6k', '6k-8k', '8k-10k', '10k-15k', '15k-20k', 'Acima 20k']
                
                df_salario_valido['faixa_salarial'] = pd.cut(df_salario_valido['salario_numero'], bins=bins, labels=labels, right=False)
                salario_stats = df_salario_valido['faixa_salarial'].value_counts().sort_index()
                
                salario_data['labels'] = salario_stats.index.tolist()
                salario_data['data'] = salario_stats.values.tolist()
                
        except Exception as e:
            print(f"Erro ao processar dados de salário: {e}")
    
    # TABELA COMPLETA DE VAGAS
    tabela_vagas_completa = []
    vagas_alto_engajamento_lista = []
    
    # Ordenar vagas por visualizações (mais populares primeiro)
    df_vagas_ordenado = df_vagas.sort_values(['visualizacao', 'click_link'], ascending=[False, False])
    
    for _, vaga in df_vagas_ordenado.iterrows():
        try:
            # Processar dados da vaga
            id_vaga = int(vaga['id']) if pd.notna(vaga.get('id')) else 0
            titulo = str(vaga.get('titulo', 'Sem título'))
            empresa = str(vaga.get('empresa', ''))
            regiao = str(vaga.get('regiao', ''))
            modalidade = str(vaga.get('modalidade', ''))
            
            # Processar salário
            salario_numero = vaga.get('salario_numero')
            if salario_numero is None or pd.isna(salario_numero):
                salario_numero = None
            else:
                salario_numero = float(salario_numero)
            
            salario_texto = str(vaga.get('salario_texto', ''))
            visualizacao = int(vaga.get('visualizacao', 0))
            click_link = int(vaga.get('click_link', 0))
            ctr_individual = float(vaga.get('ctr_individual', 0))
            
            # Status da vaga
            status_vaga = "Publicada" if visualizacao > 0 else "Cadastrada"
            data_criacao = str(vaga.get('data_criacao', ''))
            
            # Link da vaga
            link_vaga = f"https://fastvagas.vercel.app/" if id_vaga > 0 else "#"
            
            vaga_info = {
                'id': id_vaga,
                'titulo': titulo,
                'empresa': empresa,
                'regiao': regiao,
                'modalidade': modalidade,
                'salario_numero': salario_numero,
                'salario_texto': salario_texto,
                'visualizacao': visualizacao,
                'click_link': click_link,
                'ctr_individual': ctr_individual,
                'link_vaga': link_vaga,
                'status': status_vaga,
                'data_criacao': data_criacao,
                'engajamento': 'Alto' if ctr_individual > 20 else 'Normal'
            }
            
            tabela_vagas_completa.append(vaga_info)
            
            # Adicionar à lista de alto engajamento se aplicável
            if ctr_individual > 20 and visualizacao > 0:
                vagas_alto_engajamento_lista.append(vaga_info)
                
        except Exception as e:
            print(f"Erro ao processar vaga individual: {e}")
            continue
    
    # MÉTRICAS RESUMO
    metricas_resumo = {
        'total_vagas': int(total_vagas),
        'total_visualizacoes': total_visualizacoes,
        'total_cliques': total_cliques,
        'ctr_medio': ctr_medio,
        'vagas_alto_engajamento': vagas_alto_engajamento,
        'vagas_com_visualizacao': vagas_com_visualizacao,
        'taxa_engajamento': taxa_engajamento
    }
    
    # MÉTRICAS TEMPORAIS
    metricas_temporais = {
        'vagas_hoje': int(vagas_hoje),
        'vagas_semana': int(vagas_semana),
        'taxa_cadastro_diario': float(taxa_cadastro_diario)
    }
    
    # DADOS PARA GRÁFICOS
    dados_graficos = {
        'regions_data': regions_data,
        'modalidade_data': modalidade_data,
        'salario_data': salario_data
    }
    
    # RESULTADO FINAL - APENAS VAGAS
    resultado_vagas = {
        'status': 'sucesso',
        'timestamp': datetime.now().isoformat(),
        'tipo': 'metricas_vagas',
        'metricas_resumo': metricas_resumo,
        'metricas_temporais': metricas_temporais,
        'dados_graficos': dados_graficos,
        'tabela_vagas_completa': tabela_vagas_completa,
        'vagas_alto_engajamento_lista': vagas_alto_engajamento_lista
    }
    
    print(f"DEBUG - Processamento de vagas concluído:")
    print(f"  Total de vagas: {total_vagas}")
    print(f"  Visualizações totais: {total_visualizacoes}")
    print(f"  Vagas com alto engajamento: {vagas_alto_engajamento}")
    print(f"  CTR médio: {ctr_medio}%")
    
    result.append({
        "json": resultado_vagas,
        "binary": {},
        "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
    })

except Exception as e:
    print(f"DEBUG - Erro crítico no processamento de vagas: {str(e)}")
    import traceback
    print(f"DEBUG - Traceback: {traceback.format_exc()}")
    
    error_info = {
        "status": "erro",
        "timestamp": datetime.now().isoformat(),
        "tipo": 'metricas_vagas',
        "error": str(e)
    }
    result.append({
        "json": error_info,
        "binary": {},
        "pairedItem": items[0].get("pairedItem", {"item": 0}) if items else {"item": 0}
    })

return result
