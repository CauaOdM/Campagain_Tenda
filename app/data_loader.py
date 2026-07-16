import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def load_data(arquivo):
            # Lê a aba 'RESULTADOS' (header=1 pula a primeira linha vazia)
            df = pd.read_excel(arquivo, sheet_name="RESULTADOS", header=1)
            # Limpa espaços nos nomes das colunas
            df.columns = df.columns.str.strip()
            
            # Renomeia colunas para melhor exibição e manipulação
            df = df.rename(columns={
                'Rótulos de Linha': 'Campanha',
                'Soma de QTD_VENDA': 'Qtd Venda',
                'Soma de DISPARADOS': 'Disparados',
                'Soma de ENTREGUES': 'Entregues',
                'Média de TAXA_ENTREGA': 'Taxa de Entrega',
                'Soma de CLIQUES': 'Cliques',
                'Soma de QTDE_CLIENTE': 'Clientes',
                'VALOR_VENDA': 'Receita',
                'VALOR_DESCONTO': 'Desconto'
            })
            # Remove linhas vazias
            df = df.dropna(subset=['Campanha'])
            # CORREÇÃO: Remove a linha de "Total Geral" para que os valores dos KPIs fiquem exatos
            df = df[df['Campanha'] != 'Total Geral']
            
            return df