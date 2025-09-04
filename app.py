from flask import Flask, render_template, redirect, url_for, jsonify, request, flash
import os
import threading
import webbrowser
import time
import json
import re
from datetime import datetime
from werkzeug.utils import secure_filename
import PyPDF2
import io
import requests
import tkinter as tk
from tkinter import filedialog
import subprocess
import platform
import logging
# ATENÇÃO: Este código suprime os logs do Werkzeug para manter o console limpo
# Se precisar debugar problemas de rede, comente esta linha
logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

progress = 0
logs = []

CLIENTES_JSON = 'Clientes.json'
ESTRUTURA_JSON = 'estrutura.json'
HISTORICO_JSON = 'Historico.json'
DESFAZER_TEMP_JSON = 'desfazer_temp.json'


def abrir_navegador():
    """Abre o navegador após um pequeno delay para garantir que o servidor esteja rodando"""
    time.sleep(2)  # Aumentar o delay para garantir que o servidor esteja pronto
    try:
        webbrowser.open('http://localhost:5000')
    except Exception as e:
        pass  # Silenciar erros de navegador

def ler_clientes():
    """Lê clientes do arquivo JSON filtrando entradas inválidas"""
    if os.path.exists(CLIENTES_JSON):
        try:
            with open(CLIENTES_JSON, 'r', encoding='utf-8') as f:
                clientes = json.load(f)
                # Se for lista de dicts, converte para {cnpj: nome}
                if isinstance(clientes, list):
                    return {c['cnpj']: c['nome'] for c in clientes if isinstance(c, dict) and 'cnpj' in c and 'nome' in c and c['cnpj'].strip()}
                # Se for dict, filtra entradas inválidas
                elif isinstance(clientes, dict):
                    # Filtrar entradas com CNPJ vazio ou inválido
                    clientes_validos = {}
                    for cnpj, nome in clientes.items():
                        if cnpj and cnpj.strip() and nome and nome.strip():
                            clientes_validos[cnpj] = nome
                    return clientes_validos
        except Exception as e:
            print(f"Erro ao ler arquivo de clientes: {e}")
            return {}
    return {}

def verificar_cnpj_ja_existe(cnpj):
    """Verifica se um CNPJ já existe no arquivo de clientes"""
    try:
        # Normalizar o CNPJ para comparação
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        
        if os.path.exists(CLIENTES_JSON):
            with open(CLIENTES_JSON, 'r', encoding='utf-8') as f:
                clientes = json.load(f)
                if isinstance(clientes, dict):
                    # Verificar se o CNPJ já existe (em qualquer formato)
                    for cnpj_existente in clientes.keys():
                        cnpj_existente_limpo = re.sub(r'[^0-9]', '', cnpj_existente)
                        if cnpj_existente_limpo == cnpj_limpo:
                            return True
        return False
    except Exception as e:
        print(f"Erro ao verificar se CNPJ existe: {e}")
        return False

def salvar_cliente(cnpj, nome):
    """Salva um cliente no arquivo JSON com tratamento de erros melhorado"""
    try:
        # Normalizar o CNPJ para o formato padrão (com formatação)
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj_limpo) == 14:
            cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        else:
            print(f"CNPJ inválido (não tem 14 dígitos): {cnpj}")
            return False
        
        clientes = {}
        if os.path.exists(CLIENTES_JSON):
            try:
                with open(CLIENTES_JSON, 'r', encoding='utf-8') as f:
                    clientes = json.load(f)
                    if not isinstance(clientes, dict):
                        clientes = {}
            except Exception as e:
                print(f"Erro ao ler arquivo de clientes: {e}")
                clientes = {}
        else:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(CLIENTES_JSON) if os.path.dirname(CLIENTES_JSON) else '.', exist_ok=True)
            with open(CLIENTES_JSON, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        # Verificar se o CNPJ já existe (em qualquer formato)
        cnpj_ja_existe = False
        for cnpj_existente in clientes.keys():
            cnpj_existente_limpo = re.sub(r'[^0-9]', '', cnpj_existente)
            if cnpj_existente_limpo == cnpj_limpo:
                cnpj_ja_existe = True
                print(f"CNPJ {cnpj_formatado} já existe no arquivo como {cnpj_existente} com nome: {clientes[cnpj_existente]}")
                break
        
        if cnpj_ja_existe:
            return False
        
        # Validar nome
        if not nome or not nome.strip():
            print(f"Nome vazio ou inválido para CNPJ {cnpj_formatado}: '{nome}'")
            return False
        
        # Salvar o cliente no formato padronizado
        clientes[cnpj_formatado] = nome
        try:
            with open(CLIENTES_JSON, 'w', encoding='utf-8') as f:
                json.dump(clientes, f, ensure_ascii=False, indent=2)
            print(f"Cliente salvo com sucesso: {cnpj_formatado} - {nome}")
            return True
        except Exception as e:
            print(f"Erro ao salvar cliente {cnpj_formatado}: {e}")
            return False
    except Exception as e:
        print(f"Erro geral ao salvar cliente {cnpj}: {e}")
        return False

def remover_cliente(cnpj):
    """Remove um cliente do arquivo JSON"""
    if os.path.exists(CLIENTES_JSON):
        try:
            with open(CLIENTES_JSON, 'r', encoding='utf-8') as f:
                clientes = json.load(f)
                if isinstance(clientes, dict) and cnpj in clientes:
                    del clientes[cnpj]
                    with open(CLIENTES_JSON, 'w', encoding='utf-8') as f:
                        json.dump(clientes, f, ensure_ascii=False, indent=2)
                    return True
                else:
                    return False
        except Exception as e:
            return False
    else:
        return False

def ler_estrutura():
    if os.path.exists(ESTRUTURA_JSON):
        with open(ESTRUTURA_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Retornar a estrutura completa (lista com estrutura modelo e pasta matriz)
            return data
    return []

def ler_estrutura_modelo():
    """Retorna apenas a estrutura modelo (primeiro item da lista)"""
    estrutura_completa = ler_estrutura()
    if isinstance(estrutura_completa, list) and len(estrutura_completa) > 0:
        return estrutura_completa[0]
    return {}

def salvar_estrutura(nome, tipo_pasta='raiz', pasta_pai=None):
    # Mantém compatibilidade com formato [categorias, diretorio]
    if os.path.exists(ESTRUTURA_JSON):
        with open(ESTRUTURA_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            categorias = data[0]
            diretorio = data[1] if len(data) > 1 else ''
        else:
            categorias = data
            diretorio = ''
    else:
        categorias = {}
        diretorio = ''
    
    if nome:
        if tipo_pasta == 'subpasta' and pasta_pai and pasta_pai.strip():
            # Se for subpasta, adiciona à pasta pai
            if pasta_pai not in categorias:
                categorias[pasta_pai] = {}
            categorias[pasta_pai][nome] = []
        else:
            # Se for pasta raiz, cria uma nova pasta vazia
            if nome not in categorias:
                categorias[nome] = {}
    
    with open(ESTRUTURA_JSON, 'w', encoding='utf-8') as f:
        json.dump([categorias, diretorio], f, ensure_ascii=False, indent=2)

def ler_matriz():
    if os.path.exists(ESTRUTURA_JSON):
        with open(ESTRUTURA_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 1:
                return data[1]
            else:
                # Se o arquivo está no formato antigo (apenas dicionário), 
                # não há diretório raiz configurado
                return ''
    return ''

def salvar_matriz(caminho):
    # Atualiza o segundo item da lista em estrutura.json
    if os.path.exists(ESTRUTURA_JSON):
        with open(ESTRUTURA_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            categorias = data[0]
        else:
            categorias = data
        data = [categorias, caminho]
    else:
        data = [{}, caminho]
    with open(ESTRUTURA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def abrir_explorador_windows():
    """Abre o explorador de arquivos do Windows e retorna o diretório selecionado"""
    try:
        # Abrir o explorador do Windows diretamente
        diretorio_inicial = os.path.expanduser("~")
        os.startfile(diretorio_inicial)
        
        # Como não podemos capturar o resultado diretamente, vamos retornar None
        # e deixar o usuário inserir manualmente
        return None
        
    except Exception as e:
        return None

def validar_cnpj(cnpj):
    """Valida se um CNPJ é válido usando o algoritmo de validação"""
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula os dígitos verificadores
    multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Primeiro dígito verificador
    soma = 0
    for i in range(12):
        soma += int(cnpj[i]) * multiplicadores1[i]
    
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    # Segundo dígito verificador
    soma = 0
    for i in range(13):
        soma += int(cnpj[i]) * multiplicadores2[i]
    
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    # Verifica se os dígitos verificadores estão corretos
    return int(cnpj[12]) == digito1 and int(cnpj[13]) == digito2

def extrair_cnpjs_do_texto(texto, nome_arquivo):
    """Extrai CNPJs válidos de um texto"""
    cnpjs_encontrados = []
    
    # Padrão para encontrar CNPJs (14 dígitos com ou sem formatação)
    padrao_cnpj = r'\b\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}\b'
    
    # Encontra todas as ocorrências
    matches = re.finditer(padrao_cnpj, texto)
    
    for match in matches:
        cnpj_encontrado = match.group()
        
        # Obtém contexto (50 caracteres antes e depois)
        inicio = max(0, match.start() - 50)
        fim = min(len(texto), match.end() + 50)
        contexto = texto[inicio:fim].strip()
        
        # Formata CNPJ para exibição (padrão XX.XXX.XXX/0001-XX)
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj_encontrado)
        cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        
        cnpjs_encontrados.append({
            'cnpj': cnpj_formatado,
            'contexto': contexto,
            'arquivo': nome_arquivo,
            'nome_sugerido': f"Empresa {len(cnpjs_encontrados) + 1}",
            'repeticoes': 1,  # Inicialmente 1, será calculado depois
            'repeticoes_mesmo_contexto': 1  # Inicialmente 1, será calculado depois
        })
    
    return cnpjs_encontrados

def processar_pdf(pdf_file):
    """Processa um arquivo PDF e extrai CNPJs"""
    try:
        # Verificar se o arquivo é válido
        if not pdf_file or not pdf_file.filename:
            return []
            
        # Resetar a posição do cursor do arquivo para o início
        pdf_file.seek(0)
        
        # Verificar se o arquivo tem conteúdo
        conteudo = pdf_file.read()
        if not conteudo:
            return []
            
        # Resetar novamente para o início
        pdf_file.seek(0)
        
        # Lê o arquivo PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(conteudo))
        
        if len(pdf_reader.pages) == 0:
            return []
        
        texto_completo = ""
        for pagina in pdf_reader.pages:
            try:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + " "
            except Exception as e:
                continue
        
        if not texto_completo.strip():
            return []
        
        # Extrai CNPJs do texto
        cnpjs = extrair_cnpjs_do_texto(texto_completo, pdf_file.filename)
        
        return cnpjs
    except Exception as e:
        return []

def buscar_dados_empresa(cnpj_limpo):
    """Busca dados da empresa na Brasil API com tratamento de erros melhorado"""
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
        print(f"Buscando dados para CNPJ: {cnpj_limpo}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            nome_empresa = dados.get('razao_social', 'Nome não encontrado')
            print(f"Dados encontrados para {cnpj_limpo}: {nome_empresa}")
            return {
                'nome': nome_empresa,
                'nome_fantasia': dados.get('nome_fantasia', ''),
                'situacao': dados.get('situacao_cadastral', ''),
                'data_abertura': dados.get('data_inicio_atividade', ''),
                'tipo': dados.get('tipo', ''),
                'porte': dados.get('porte', ''),
                'natureza_juridica': dados.get('natureza_juridica', ''),
                'capital_social': dados.get('capital_social', ''),
                'endereco': {
                    'logradouro': dados.get('logradouro', ''),
                    'numero': dados.get('numero', ''),
                    'complemento': dados.get('complemento', ''),
                    'bairro': dados.get('bairro', ''),
                    'municipio': dados.get('municipio', ''),
                    'uf': dados.get('uf', ''),
                    'cep': dados.get('cep', '')
                }
            }
        else:
            print(f"Erro na API para CNPJ {cnpj_limpo}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao buscar dados para CNPJ {cnpj_limpo}: {e}")
        return None

def calcular_repeticoes_cnpjs(cnpjs_encontrados):
    """Remove duplicatas e calcula repetições por arquivo e contexto"""
    # Dicionário para agrupar CNPJs únicos
    cnpjs_unicos = {}
    
    for cnpj in cnpjs_encontrados:
        cnpj_formatado = cnpj['cnpj']
        
        if cnpj_formatado not in cnpjs_unicos:
            # Primeira ocorrência do CNPJ
            cnpjs_unicos[cnpj_formatado] = {
                'cnpj': cnpj['cnpj'],
                'nome_sugerido': cnpj['nome_sugerido'],
                'arquivos': [cnpj['arquivo']],
                'contextos': [cnpj['contexto']],
                'repeticoes': 1,  # Conta arquivos diferentes
                'repeticoes_mesmo_contexto': 1  # Conta contextos únicos
            }
        else:
            # CNPJ já existe, adiciona arquivo se for diferente
            if cnpj['arquivo'] not in cnpjs_unicos[cnpj_formatado]['arquivos']:
                cnpjs_unicos[cnpj_formatado]['arquivos'].append(cnpj['arquivo'])
                cnpjs_unicos[cnpj_formatado]['repeticoes'] += 1
            
            # Adiciona contexto se for diferente
            contexto_similar = False
            for contexto_existente in cnpjs_unicos[cnpj_formatado]['contextos']:
                if cnpj['contexto'][:50] == contexto_existente[:50]:
                    contexto_similar = True
                    break
            
            if not contexto_similar:
                cnpjs_unicos[cnpj_formatado]['contextos'].append(cnpj['contexto'])
                cnpjs_unicos[cnpj_formatado]['repeticoes_mesmo_contexto'] += 1
    
    # Converte de volta para lista
    resultado = []
    for cnpj_formatado, dados in cnpjs_unicos.items():
        # Busca dados da empresa na API (usa CNPJ sem formatação para a API)
        cnpj_limpo_api = re.sub(r'[^0-9]', '', cnpj_formatado)
        dados_empresa = buscar_dados_empresa(cnpj_limpo_api)
        nome_empresa = dados_empresa['nome'] if dados_empresa else dados['nome_sugerido']
        
        # Usa o primeiro contexto como principal
        resultado.append({
            'cnpj': dados['cnpj'],
            'cnpj_limpo': cnpj_limpo_api,  # CNPJ sem formatação para uso no template
            'nome_sugerido': nome_empresa,
            'arquivo': ', '.join(dados['arquivos']),  # Lista todos os arquivos
            'contexto': dados['contextos'][0],  # Primeiro contexto
            'contextos_completos': dados['contextos'],  # Todos os contextos
            'arquivos_completos': dados['arquivos'],  # Todos os arquivos
            'repeticoes': dados['repeticoes'],
            'repeticoes_mesmo_contexto': dados['repeticoes_mesmo_contexto'],
            'dados_empresa': dados_empresa
        })
    
    return resultado

def estrutura_para_tree(estrutura):
    # Converte o dicionário de estrutura em uma lista de nós para a tree
    tree = []
    for nome, valor in estrutura.items():
        if isinstance(valor, dict):
            # É uma pasta que contém PDFs ou subpastas
            filhos = []
            for pdf_nome, palavras in valor.items():
                if isinstance(palavras, list):
                    # É um PDF com lista de palavras-chave
                    filhos.append({
                        'nome': pdf_nome,
                        'tipo': 'pdf',
                        'palavras': ', '.join(palavras),
                        'filhos': []
                    })
                elif isinstance(palavras, dict):
                    # É uma subpasta com seus próprios PDFs
                    subfilhos = []
                    for sub_pdf_nome, sub_palavras in palavras.items():
                        if isinstance(sub_palavras, list):
                            subfilhos.append({
                                'nome': sub_pdf_nome,
                                'tipo': 'pdf',
                                'palavras': ', '.join(sub_palavras),
                                'filhos': []
                            })
                        else:
                            subfilhos.append({
                                'nome': sub_pdf_nome,
                                'tipo': 'pdf',
                                'palavras': str(sub_palavras),
                                'filhos': []
                            })
                    filhos.append({
                        'nome': pdf_nome,
                        'tipo': 'pasta',
                        'filhos': subfilhos
                    })
                elif not palavras:
                    # É uma subpasta vazia
                    filhos.append({
                        'nome': pdf_nome,
                        'tipo': 'pasta',
                        'filhos': []
                    })
                else:
                    # É um valor simples (tratado como PDF)
                    filhos.append({
                        'nome': pdf_nome,
                        'tipo': 'pdf',
                        'palavras': str(palavras),
                        'filhos': []
                    })
            tree.append({
                'nome': nome,
                'tipo': 'pasta',
                'filhos': filhos
            })
        elif isinstance(valor, list):
            # É um PDF no nível raiz (sem pasta)
            tree.append({
                'nome': nome, 
                'tipo': 'pdf',
                'palavras': ', '.join(valor), 
                'filhos': []
            })
        else:
            tree.append({
                'nome': nome, 
                'tipo': 'pasta',
                'filhos': []
            })
    return tree

def analisar_estrutura_diretorio(diretorio):
    """Analisa a estrutura de um diretório e retorna apenas as pastas"""
    estrutura = []
    
    def processar_diretorio(caminho, nivel=0):
        """Processa recursivamente um diretório, considerando apenas pastas"""
        try:
            itens = os.listdir(caminho)
            pastas = []
            
            for item in itens:
                item_path = os.path.join(caminho, item)
                
                if os.path.isdir(item_path):
                    # É uma pasta
                    pastas.append({
                        'nome': item,
                        'tipo': 'pasta',
                        'caminho': item_path,
                        'palavras_chave': '',  # Será preenchido pelo usuário
                        'filhos': processar_diretorio(item_path, nivel + 1)
                    })
            
            # Retorna apenas pastas
            return pastas
            
        except PermissionError:
            return []
        except Exception as e:
            return []
    
    # Processa o diretório raiz
    estrutura = processar_diretorio(diretorio)
    
    return {
        'raiz': diretorio,
        'estrutura': estrutura,
        'total_pastas': contar_pastas(estrutura)
    }

def contar_pastas(estrutura):
    """Conta o total de pastas na estrutura"""
    total = 0
    for item in estrutura:
        if item['tipo'] == 'pasta':
            total += 1
            total += contar_pastas(item['filhos'])
    return total

def contar_pdfs(estrutura):
    """Conta o total de PDFs na estrutura"""
    total = 0
    for item in estrutura:
        if item['tipo'] == 'pdf':
            total += 1
        else:
            total += contar_pdfs(item['filhos'])
    return total

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return jsonify({'progress': progress, 'logs': logs})

@app.route('/cadastro_estrutura', methods=['GET', 'POST'])
def cadastro_estrutura():
    if request.method == 'POST':
        if 'add_cnpj' in request.form:
            cnpj = request.form.get('cnpj', '').strip()
            nome = request.form.get('nome', '').strip()
            if cnpj and nome:
                salvar_cliente(cnpj, nome)
        elif 'cnpj_remover' in request.form:
            cnpj_remover = request.form.get('cnpj_remover', '').strip()
            if cnpj_remover:
                sucesso = remover_cliente(cnpj_remover)
                if sucesso:
                    flash(f'CNPJ {cnpj_remover} removido com sucesso!', 'success')
                else:
                    flash(f'Falha ao remover CNPJ {cnpj_remover}', 'error')
        elif 'add_estrutura' in request.form:
            estrutura_nome = request.form.get('estrutura', '').strip()
            tipo_pasta = request.form.get('tipo_pasta', 'raiz')
            pasta_pai = request.form.get('pasta_pai', '').strip()
            if estrutura_nome:
                salvar_estrutura(estrutura_nome, tipo_pasta, pasta_pai)
        elif 'add_matriz' in request.form:
            matriz = request.form.get('matriz', '').strip()
            if matriz:
                salvar_matriz(matriz)
        return redirect(url_for('cadastro_estrutura'))

    cnpjs = ler_clientes()
    estrutura = ler_estrutura()
    # Extrair apenas as categorias (primeiro item da lista) para a função estrutura_para_tree
    categorias = estrutura[0] if isinstance(estrutura, list) and len(estrutura) > 0 else {}
    estruturas_tree = estrutura_para_tree(categorias)
    matriz = ler_matriz()
    # Gerar lista de pastas cadastradas (apenas as chaves do dicionário que são as pastas)
    pastas = [nome for nome, valor in categorias.items() if isinstance(valor, dict)]
    return render_template('cadastro_estrutura.html', cnpjs=cnpjs, estruturas_tree=estruturas_tree, matriz=matriz, pastas=pastas)

@app.route('/selecionar_diretorio', methods=['POST'])
def selecionar_diretorio():
    """Abre diálogo para selecionar diretório"""
    try:
        # Tentar com tkinter
        try:
            # Criar janela tkinter básica
            root = tk.Tk()
            
            # Configuração para garantir que apareça
            root.withdraw()  # Ocultar janela principal
            root.attributes('-topmost', True)  # Manter no topo
            
            # Abrir diálogo de seleção de diretório
            diretorio = filedialog.askdirectory(
                title="Selecionar Pasta Matriz",
                initialdir=os.path.expanduser("~")
            )
            
            # Destruir a janela tkinter
            try:
                root.quit()
                root.destroy()
            except:
                pass
            
            # Processar o resultado
            if diretorio:
                # Salvar o diretório selecionado
                salvar_matriz(diretorio)
                return jsonify({'success': True, 'diretorio': diretorio})
            else:
                return jsonify({'success': False, 'message': 'Nenhum diretório selecionado'})
                
        except Exception as e:
            # Se tkinter falhar, tentar método alternativo para Windows
            if platform.system() == 'Windows':
                try:
                    # Abrir o explorador do Windows
                    abrir_explorador_windows()
                    return jsonify({
                        'success': False, 
                        'message': 'Explorador do Windows foi aberto. Copie o caminho da pasta desejada e cole no campo de texto acima.'
                    })
                except Exception as win_error:
                    return jsonify({'success': False, 'message': f'Erro ao abrir explorador: {str(win_error)}. Use o campo de texto para inserir o caminho manualmente.'})
            else:
                return jsonify({'success': False, 'message': f'Tkinter não está disponível: {str(e)}. Use o campo de texto para inserir o caminho manualmente.'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao selecionar diretório: {str(e)}'})

@app.route('/selecionar_diretorio_estrutura', methods=['POST'])
def selecionar_diretorio_estrutura():
    """Abre diálogo para selecionar diretório para análise de estrutura"""
    try:
        # Tentar com tkinter
        try:
            # Criar janela tkinter básica
            root = tk.Tk()
            
            # Configuração para garantir que apareça
            root.withdraw()  # Ocultar janela principal
            root.attributes('-topmost', True)  # Manter no topo
            
            # Abrir diálogo de seleção de diretório
            diretorio = filedialog.askdirectory(
                title="Selecionar Diretório para Análise de Estrutura",
                initialdir=os.path.expanduser("~")
            )
            
            # Destruir a janela tkinter
            try:
                root.quit()
                root.destroy()
            except:
                pass
            
            # Processar o resultado
            if diretorio:
                return jsonify({'success': True, 'diretorio': diretorio})
            else:
                return jsonify({'success': False, 'message': 'Nenhum diretório selecionado'})
                
        except Exception as e:
            # Se tkinter falhar, tentar método alternativo para Windows
            if platform.system() == 'Windows':
                try:
                    # Abrir o explorador do Windows
                    abrir_explorador_windows()
                    return jsonify({
                        'success': False, 
                        'message': 'Explorador do Windows foi aberto. Copie o caminho da pasta desejada e cole no campo de texto acima.'
                    })
                except Exception as win_error:
                    return jsonify({'success': False, 'message': f'Erro ao abrir explorador: {str(win_error)}. Use o campo de texto para inserir o caminho manualmente.'})
            else:
                return jsonify({'success': False, 'message': f'Tkinter não está disponível: {str(e)}. Use o campo de texto para inserir o caminho manualmente.'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao selecionar diretório: {str(e)}'})

@app.route('/salvar_matriz_manual', methods=['POST'])
def salvar_matriz_manual():
    """Salva a matriz inserida manualmente"""
    try:
        data = request.get_json()
        matriz = data.get('matriz', '').strip()
        
        if not matriz:
            return jsonify({'success': False, 'message': 'Caminho não fornecido'})
        
        # Verificar se o diretório existe
        if not os.path.exists(matriz):
            return jsonify({'success': False, 'message': 'Diretório não encontrado'})
        
        # Salvar o diretório
        salvar_matriz(matriz)
        return jsonify({'success': True, 'message': 'Pasta matriz salva com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao salvar pasta: {str(e)}'})

@app.route('/organizar_pdfs')
def organizar_pdfs():
    return render_template('organizar_pdfs.html')

@app.route('/analisar_cnpjs', methods=['GET', 'POST'])
def analisar_cnpjs():
    if request.method == 'POST':
        if 'pdfs' in request.files:
            # Processar upload de PDFs
            arquivos = request.files.getlist('pdfs')
            cnpjs_encontrados = []
            
            for arquivo in arquivos:
                if arquivo.filename and arquivo.filename.lower().endswith('.pdf'):
                    cnpjs_pdf = processar_pdf(arquivo)
                    cnpjs_encontrados.extend(cnpjs_pdf)
            
            # Calcular repetições de cada CNPJ
            cnpjs_com_repeticoes = calcular_repeticoes_cnpjs(cnpjs_encontrados)
            
            return render_template('analisar_cnpjs.html', cnpjs_encontrados=cnpjs_com_repeticoes)
        
        elif 'salvar_cnpjs' in request.form:
            # Salvar CNPJs selecionados
            cnpjs_selecionados = request.form.getlist('cnpjs_selecionados')
            print(f"Total de CNPJs selecionados para salvar: {len(cnpjs_selecionados)}")
            
            salvos = 0
            ja_existem = 0
            erros = 0
            detalhes_erros = []
            detalhes_ja_existem = []
            
            for i, cnpj_formatado in enumerate(cnpjs_selecionados):
                print(f"Processando CNPJ {i+1}/{len(cnpjs_selecionados)}: {cnpj_formatado}")
                
                nome = request.form.get(f'nome_{cnpj_formatado}', '').strip()
                print(f"  Nome encontrado: '{nome}'")
                
                if nome:
                    # CNPJ já está formatado, salvar diretamente
                    resultado = salvar_cliente(cnpj_formatado, nome)
                    if resultado:
                        salvos += 1
                        print(f"  ✓ Salvo com sucesso")
                    else:
                        # Verificar se é porque já existe ou se é erro real
                        if verificar_cnpj_ja_existe(cnpj_formatado):
                            ja_existem += 1
                            detalhes_ja_existem.append(f"CNPJ {cnpj_formatado}: já existe no sistema")
                            print(f"  ℹ Já existe no sistema")
                        else:
                            erros += 1
                            detalhes_erros.append(f"CNPJ {cnpj_formatado}: falha no salvamento")
                            print(f"  ✗ Falha no salvamento")
                else:
                    erros += 1
                    detalhes_erros.append(f"CNPJ {cnpj_formatado}: nome vazio")
                    print(f"  ✗ Nome vazio")
            
            print(f"Resultado final: {salvos} salvos, {ja_existem} já existiam, {erros} erros")
            
            # Mostrar mensagem de resultado
            if salvos > 0:
                flash(f'{salvos} CNPJ(s) salvo(s) com sucesso!', 'success')
            if ja_existem > 0:
                flash(f'{ja_existem} CNPJ(s) já existiam no sistema e não foram duplicados.', 'info')
            if erros > 0:
                flash(f'{erros} CNPJ(s) não puderam ser salvos. Verifique os logs do console.', 'error')
                print("Detalhes dos erros:")
                for erro in detalhes_erros:
                    print(f"  - {erro}")
            
            return redirect(url_for('cadastro_estrutura'))
    
    return render_template('analisar_cnpjs.html', cnpjs_encontrados=[])

@app.route('/reconhecer_estrutura', methods=['GET', 'POST'])
def reconhecer_estrutura():
    if request.method == 'POST':
        if 'diretorio' in request.form:
            diretorio = request.form.get('diretorio', '').strip()
            if diretorio:
                # Com a File System Access API, recebemos apenas o nome do diretório
                # Vamos tentar encontrar o diretório no sistema
                diretorio_encontrado = None
                
                # Primeiro, verificar se é um caminho válido
                if os.path.exists(diretorio):
                    diretorio_encontrado = diretorio
                else:
                    # Tentar encontrar o diretório em locais comuns
                    locais_comuns = [
                        os.path.expanduser("~/Documents"),
                        os.path.expanduser("~/Desktop"),
                        os.path.expanduser("~/Downloads"),
                        os.getcwd(),  # Diretório atual
                    ]
                    
                    for local in locais_comuns:
                        caminho_teste = os.path.join(local, diretorio)
                        if os.path.exists(caminho_teste):
                            diretorio_encontrado = caminho_teste
                            break
                
                if diretorio_encontrado:
                    # Analisar estrutura do diretório
                    estrutura_encontrada = analisar_estrutura_diretorio(diretorio_encontrado)
                    return render_template('reconhecer_estrutura.html', 
                                        estrutura_encontrada=estrutura_encontrada,
                                        diretorio_analisado=diretorio_encontrado)
                else:
                    flash(f'Diretório "{diretorio}" não encontrado! Verifique se o diretório existe e está acessível.', 'error')
            else:
                flash('Nenhum diretório selecionado!', 'error')
    
    return render_template('reconhecer_estrutura.html', estrutura_encontrada=None, diretorio_analisado=None)

@app.route('/configurar_palavras_chave', methods=['GET', 'POST'])
def configurar_palavras_chave():
    if request.method == 'POST':
        # Receber dados do formulário
        estrutura_data = request.form.get('estrutura_data')
        diretorio_raiz = request.form.get('diretorio_raiz')
        
        if estrutura_data and diretorio_raiz:
            # Processar tipos de PDF enviados
            tipos_pdf = {}
            for key, value in request.form.items():
                if key.startswith('tipo_nome_') or key.startswith('tipo_palavras_'):
                    tipos_pdf[key] = value.strip()
            
            # Salvar estrutura com tipos de PDF
            salvar_estrutura_com_palavras_chave(diretorio_raiz, estrutura_data, tipos_pdf)
            
            flash('Estrutura configurada com sucesso!', 'success')
            return redirect(url_for('cadastro_estrutura'))
    
    # GET: renderizar a página com dados do sessionStorage (serão carregados via JavaScript)
    return render_template('configurar_palavras_chave.html')

@app.route('/adicionar_tipos_pdf', methods=['GET', 'POST'])
def adicionar_tipos_pdf():
    if request.method == 'POST':
        # Processar dados do formulário
        estrutura_data = request.form.get('estrutura_data', '')
        diretorio_raiz = request.form.get('diretorio_raiz', '')
        palavras_chave = {}
        
        # Coletar todos os campos de tipos de PDF (normais e adicionais)
        for key, value in request.form.items():
            if (key.startswith('tipo_nome_') or 
                key.startswith('tipo_palavras_') or 
                key.startswith('tipo_adicional_nome_') or 
                key.startswith('tipo_adicional_palavras_')):
                palavras_chave[key] = value.strip()
        
        if estrutura_data and diretorio_raiz:
            try:
                # Salvar estrutura com tipos de PDF
                salvar_estrutura_com_palavras_chave(diretorio_raiz, estrutura_data, palavras_chave)
                
                flash('Tipos de PDF adicionados com sucesso!', 'success')
                return redirect(url_for('cadastro_estrutura'))
            except Exception as e:
                flash(f'Erro ao salvar tipos de PDF: {str(e)}', 'error')
                return redirect(url_for('adicionar_tipos_pdf'))
        else:
            flash('Dados insuficientes para salvar. Verifique se a estrutura e diretório estão configurados.', 'error')
            return redirect(url_for('adicionar_tipos_pdf'))
    
    # GET: renderizar a página com dados da estrutura atual
    estrutura = ler_estrutura()
    matriz = ler_matriz()
    
    # Converter estrutura para formato compatível com a página de configuração
    estrutura_para_configuracao = []
    
    def converter_estrutura(estrutura_dict, caminho_base=''):
        for nome, valor in estrutura_dict.items():
            if isinstance(valor, dict):
                # É uma pasta
                caminho_atual = f"{caminho_base}/{nome}" if caminho_base else nome
                item = {
                    'nome': nome,
                    'tipo': 'pasta',
                    'caminho': caminho_atual,
                    'filhos': []
                }
                
                # Processar subpastas e PDFs
                for sub_nome, sub_valor in valor.items():
                    if isinstance(sub_valor, list):
                        # É um PDF
                        item['filhos'].append({
                            'nome': sub_nome,
                            'tipo': 'pdf',
                            'caminho': f"{caminho_atual}/{sub_nome}",
                            'palavras_chave': ', '.join(sub_valor)
                        })
                    elif isinstance(sub_valor, dict):
                        # É uma subpasta
                        sub_item = {
                            'nome': sub_nome,
                            'tipo': 'pasta',
                            'caminho': f"{caminho_atual}/{sub_nome}",
                            'filhos': []
                        }
                        
                        # Processar PDFs na subpasta
                        for pdf_nome, pdf_palavras in sub_valor.items():
                            if isinstance(pdf_palavras, list):
                                sub_item['filhos'].append({
                                    'nome': pdf_nome,
                                    'tipo': 'pdf',
                                    'caminho': f"{caminho_atual}/{sub_nome}/{pdf_nome}",
                                    'palavras_chave': ', '.join(pdf_palavras)
                                })
                        
                        item['filhos'].append(sub_item)
                
                estrutura_para_configuracao.append(item)
            elif isinstance(valor, list):
                # É um PDF no nível raiz
                estrutura_para_configuracao.append({
                    'nome': nome,
                    'tipo': 'pdf',
                    'caminho': nome,
                    'palavras_chave': ', '.join(valor)
                })
    
    converter_estrutura(estrutura)
    
    return render_template('adicionar_tipos_pdf.html', 
                         estrutura_data=estrutura_para_configuracao,
                         diretorio_raiz=matriz)

@app.route('/excluir_itens_estrutura', methods=['POST'])
def excluir_itens_estrutura():
    try:
        dados = request.get_json()
        itens_para_excluir = dados.get('itens_para_excluir', [])
        
        # Carregar estrutura atual
        estrutura = ler_estrutura()
        
        # Função recursiva para remover itens aninhados
        def remover_item_recursivo(estrutura_dict, nome_item, caminho_item):
            """Remove um item da estrutura, incluindo subitens"""
            # Se o item está no nível raiz
            if nome_item in estrutura_dict:
                del estrutura_dict[nome_item]
                return True
            
            # Procurar em subpastas
            for pasta_nome, pasta_conteudo in list(estrutura_dict.items()):
                if isinstance(pasta_conteudo, dict):
                    # Se encontrou o item nesta pasta
                    if nome_item in pasta_conteudo:
                        del pasta_conteudo[nome_item]
                        return True
                    
                    # Procurar recursivamente em subpastas
                    if remover_item_recursivo(pasta_conteudo, nome_item, caminho_item):
                        return True
            
            return False
        
        # Processar exclusões
        itens_removidos = 0
        for item in itens_para_excluir:
            nome = item.get('nome')
            caminho = item.get('caminho')
            
            if remover_item_recursivo(estrutura, nome, caminho):
                itens_removidos += 1
        
        # Salvar estrutura atualizada
        # Verificar se o arquivo existe, se não existir, criar com estrutura vazia
        if not os.path.exists(ESTRUTURA_JSON):
            with open(ESTRUTURA_JSON, 'w', encoding='utf-8') as f:
                json.dump([{}, ''], f, ensure_ascii=False, indent=2)
        
        with open(ESTRUTURA_JSON, 'w', encoding='utf-8') as f:
            json.dump(estrutura, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'{itens_removidos} item(s) excluído(s) com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def salvar_estrutura_com_palavras_chave(diretorio_raiz, estrutura_data, palavras_chave):
    """Salva a estrutura com os tipos de PDF configurados"""
    try:
        # Processar dados da estrutura
        import json
        
        # Carregar estrutura existente
        estrutura_existente = ler_estrutura()
        
        # Parse do JSON da estrutura do formulário
        estrutura_form = json.loads(estrutura_data)
        
        # Usar a estrutura existente como base (primeiro item da lista)
        if isinstance(estrutura_existente, list) and len(estrutura_existente) > 0:
            estrutura_para_salvar = estrutura_existente[0].copy()
        else:
            estrutura_para_salvar = {}
        
        def processar_tipos_pdf_novos(estrutura_atual):
            """Processa apenas os novos tipos de PDF sem sobrescrever a estrutura existente"""
            for item in estrutura_atual:
                if item['tipo'] == 'pasta':
                    # Usar o caminho como ID, mas substituir caracteres problemáticos
                    pasta_id = item['caminho'].replace('/', '_').replace('\\', '_')
                    
                    # Processar tipos de PDF para esta pasta
                    tipos_pdf = {}
                    for key, value in palavras_chave.items():
                        if key.startswith(f'tipo_nome_{pasta_id}_'):
                            tipo_id = key.replace(f'tipo_nome_{pasta_id}_', '')
                            nome_tipo = value.strip()
                            palavras_tipo = palavras_chave.get(f'tipo_palavras_{pasta_id}_{tipo_id}', '').strip()
                            
                            if nome_tipo and palavras_tipo:
                                tipos_pdf[nome_tipo] = [p.strip() for p in palavras_tipo.split(',') if p.strip()]
                    
                    # Adicionar novos tipos à pasta existente (se existir)
                    if item['nome'] in estrutura_para_salvar:
                        if tipos_pdf:
                            estrutura_para_salvar[item['nome']].update(tipos_pdf)
                    else:
                        # Se a pasta não existe, criar com os novos tipos
                        if tipos_pdf:
                            estrutura_para_salvar[item['nome']] = tipos_pdf
                        else:
                            estrutura_para_salvar[item['nome']] = {}
                    
                    # Processar subpastas recursivamente
                    if item['filhos']:
                        processar_tipos_pdf_novos(item['filhos'])
        
        # Processar apenas os novos tipos de PDF
        processar_tipos_pdf_novos(estrutura_form)
        
        # Processar tipos de PDF da pasta raiz (se existirem)
        tipos_pdf_raiz = {}
        for key, value in palavras_chave.items():
            if key.startswith('tipo_nome_raiz_'):
                tipo_id = key.replace('tipo_nome_raiz_', '')
                nome_tipo = value.strip()
                palavras_tipo = palavras_chave.get(f'tipo_palavras_raiz_{tipo_id}', '').strip()
                
                if nome_tipo and palavras_tipo:
                    tipos_pdf_raiz[nome_tipo] = [p.strip() for p in palavras_tipo.split(',') if p.strip()]
        
        # Processar tipos de PDF adicionais
        tipos_pdf_adicionais = {}
        for key, value in palavras_chave.items():
            if key.startswith('tipo_adicional_nome_'):
                # Extrair pasta_id e tipo_id da chave
                partes = key.split('_')
                if len(partes) >= 4:
                    pasta_id = '_'.join(partes[2:-1])  # Junta todas as partes exceto as primeiras e a última
                    tipo_id = partes[-1]
                    nome_tipo = value.strip()
                    palavras_tipo = palavras_chave.get(f'tipo_adicional_palavras_{pasta_id}_{tipo_id}', '').strip()
                    
                    if nome_tipo and palavras_tipo:
                        if pasta_id == 'raiz':
                            # Adicionar à pasta raiz
                            tipos_pdf_raiz[nome_tipo] = [p.strip() for p in palavras_tipo.split(',') if p.strip()]
                        else:
                            # Adicionar à pasta específica
                            if pasta_id not in tipos_pdf_adicionais:
                                tipos_pdf_adicionais[pasta_id] = {}
                            tipos_pdf_adicionais[pasta_id][nome_tipo] = [p.strip() for p in palavras_tipo.split(',') if p.strip()]
        
        # Adicionar tipos da pasta raiz diretamente na estrutura final
        if tipos_pdf_raiz:
            estrutura_para_salvar.update(tipos_pdf_raiz)
        
        # Adicionar tipos adicionais às pastas específicas
        for pasta_id, tipos in tipos_pdf_adicionais.items():
            # Encontrar a pasta correspondente na estrutura
            pasta_encontrada = False
            for item in estrutura_form:
                if item['caminho'].replace('/', '_').replace('\\', '_') == pasta_id:
                    # Adicionar tipos a esta pasta
                    if item['nome'] not in estrutura_para_salvar:
                        estrutura_para_salvar[item['nome']] = {}
                    estrutura_para_salvar[item['nome']].update(tipos)
                    pasta_encontrada = True
                    break
                
                # Procurar em subpastas
                if item['filhos']:
                    for filho in item['filhos']:
                        if filho['caminho'].replace('/', '_').replace('\\', '_') == pasta_id:
                            if item['nome'] not in estrutura_para_salvar:
                                estrutura_para_salvar[item['nome']] = {}
                            if filho['nome'] not in estrutura_para_salvar[item['nome']]:
                                estrutura_para_salvar[item['nome']][filho['nome']] = {}
                            estrutura_para_salvar[item['nome']][filho['nome']].update(tipos)
                            pasta_encontrada = True
                            break
                    if pasta_encontrada:
                        break
        
        # Salvar no arquivo JSON no formato [estrutura_modelo, diretorio_matriz]
        # Verificar se o arquivo existe, se não existir, criar com estrutura vazia
        if not os.path.exists(ESTRUTURA_JSON):
            with open(ESTRUTURA_JSON, 'w', encoding='utf-8') as f:
                json.dump([{}, ''], f, ensure_ascii=False, indent=2)
        
        with open(ESTRUTURA_JSON, 'w', encoding='utf-8') as f:
            json.dump([estrutura_para_salvar, diretorio_raiz], f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        raise e

def ler_historico():
    """Lê o histórico de movimentação de arquivos"""
    try:
        if os.path.exists(HISTORICO_JSON):
            with open(HISTORICO_JSON, 'r', encoding='utf-8') as f:
                historico = json.load(f)
                return historico
        else:
            return {}
    except Exception as e:
        return {}

def salvar_historico(historico):
    """Salva o histórico de movimentação de arquivos"""
    try:
        # Verificar se o arquivo existe, se não existir, criar com estrutura vazia
        if not os.path.exists(HISTORICO_JSON):
            with open(HISTORICO_JSON, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        with open(HISTORICO_JSON, 'w', encoding='utf-8') as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise e

def adicionar_ao_historico(arquivo_original, destino, descricao="", operacao="transferido"):
    """Adiciona uma operação ao histórico com dados estruturados"""
    from datetime import datetime
    
    historico = ler_historico()
    mes_ano = datetime.now().strftime("%m/%Y")
    
    if mes_ano not in historico:
        historico[mes_ano] = []
    
    # Criar registro estruturado
    registro = {
        "dia": datetime.now().strftime("%d"),
        "mes_ano": mes_ano,
        "arquivo": os.path.basename(arquivo_original),
        "local_antigo": arquivo_original,
        "novo_local": destino,
        "operacao": operacao,
        "descricao": descricao,
        "timestamp": datetime.now().isoformat()
    }
    
    historico[mes_ano].append(registro)
    salvar_historico(historico)
    
    return registro

def salvar_dados_desfazer(operacoes):
    """Salva dados temporários para desfazer operações"""
    try:
        dados_desfazer = {
            "timestamp": datetime.now().isoformat(),
            "operacoes": operacoes
        }
        
        # Verificar se o arquivo existe, se não existir, criar diretório se necessário
        diretorio = os.path.dirname(DESFAZER_TEMP_JSON)
        if diretorio and not os.path.exists(diretorio):
            os.makedirs(diretorio, exist_ok=True)
        
        with open(DESFAZER_TEMP_JSON, 'w', encoding='utf-8') as f:
            json.dump(dados_desfazer, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        return False

def ler_dados_desfazer():
    """Lê dados temporários para desfazer operações"""
    try:
        if os.path.exists(DESFAZER_TEMP_JSON):
            with open(DESFAZER_TEMP_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        return None

def limpar_dados_desfazer():
    """Remove dados temporários de desfazer"""
    try:
        if os.path.exists(DESFAZER_TEMP_JSON):
            os.remove(DESFAZER_TEMP_JSON)
        return True
    except Exception as e:
        return False

def mover_arquivo_com_historico(arquivo_origem, arquivo_destino, descricao=""):
    """Move um arquivo e registra no histórico"""
    try:
        # Criar diretório de destino se não existir
        os.makedirs(os.path.dirname(arquivo_destino), exist_ok=True)
        
        # Mover o arquivo
        import shutil
        shutil.move(arquivo_origem, arquivo_destino)
        
        # Registrar no histórico
        registro = adicionar_ao_historico(arquivo_origem, arquivo_destino, descricao, "transferido")
        
        return True, registro
    except Exception as e:
        return False, str(e)

def converter_historico_antigo():
    """Converte histórico antigo (texto) para novo formato (estruturado)"""
    try:
        historico = ler_historico()
        convertidos = 0
        
        for mes_ano in historico.keys():
            operacoes_mes = historico[mes_ano]
            operacoes_convertidas = []
            
            for operacao in operacoes_mes:
                if isinstance(operacao, str):
                    # Converter operação antiga (texto) para nova estrutura
                    if "Transferido para" in operacao:
                        partes = operacao.split(" Transferido para ")
                        if len(partes) == 2:
                            # Extrair informações do texto antigo
                            info_parte = partes[0].split(" ", 2)  # "Dia XX arquivo.pdf"
                            if len(info_parte) >= 3:
                                dia = info_parte[1]
                                arquivo = info_parte[2]
                                destino = partes[1]
                                
                                # Criar nova estrutura
                                nova_operacao = {
                                    "dia": dia,
                                    "mes_ano": mes_ano,
                                    "arquivo": arquivo,
                                    "local_antigo": f"uploads/{arquivo}",  # Assumindo que veio de uploads
                                    "novo_local": destino,
                                    "operacao": "transferido",
                                    "descricao": "Migrado do formato antigo",
                                    "timestamp": datetime.now().isoformat()
                                }
                                operacoes_convertidas.append(nova_operacao)
                                convertidos += 1
                            else:
                                # Manter operação antiga se não conseguir converter
                                operacoes_convertidas.append(operacao)
                        else:
                            operacoes_convertidas.append(operacao)
                    else:
                        operacoes_convertidas.append(operacao)
                else:
                    # Já está no novo formato
                    operacoes_convertidas.append(operacao)
            
            historico[mes_ano] = operacoes_convertidas
        
        if convertidos > 0:
            salvar_historico(historico)
        
        return convertidos
        
    except Exception as e:
        return 0

def limpar_historico_invalido():
    """Remove operações do histórico onde os arquivos não existem mais"""
    try:
        historico = ler_historico()
        operacoes_removidas = 0
        
        for mes_ano in list(historico.keys()):
            operacoes_mes = historico[mes_ano]
            operacoes_para_remover = []
            
            for operacao in operacoes_mes:
                # Verificar se é uma operação de transferência (estrutura antiga ou nova)
                if isinstance(operacao, dict):
                    # Nova estrutura
                    if operacao.get('operacao') == 'transferido':
                        destino_atual = operacao.get('novo_local', '')
                        if destino_atual and not os.path.exists(destino_atual):
                            operacoes_para_remover.append(operacao)
                else:
                    # Estrutura antiga (texto)
                    if "Transferido para" in operacao:
                        partes = operacao.split(" Transferido para ")
                        if len(partes) == 2:
                            destino_atual = partes[1]
                            if not os.path.exists(destino_atual):
                                operacoes_para_remover.append(operacao)
            
            # Remover operações inválidas
            for operacao in operacoes_para_remover:
                operacoes_mes.remove(operacao)
                operacoes_removidas += 1
            
            # Se não há mais operações no mês, remover o mês
            if not operacoes_mes:
                del historico[mes_ano]
        
        if operacoes_removidas > 0:
            salvar_historico(historico)
        
        return operacoes_removidas
        
    except Exception as e:
        raise e

def desfazer_ultima_operacao():
    """Desfaz a última operação de movimentação usando dados temporários"""
    try:
        # Ler dados temporários de desfazer
        dados_desfazer = ler_dados_desfazer()
        
        if not dados_desfazer or not dados_desfazer.get('operacoes'):
            return False, "Nenhuma operação recente encontrada para desfazer"
        
        operacoes = dados_desfazer['operacoes']
        arquivos_desfeitos = 0
        erros = 0
        
        for operacao in operacoes:
            try:
                arquivo_origem = operacao['local_antigo']
                arquivo_destino = operacao['novo_local']
                nome_arquivo = operacao['arquivo']
                
                # Verificar se o arquivo ainda está no destino
                if os.path.exists(arquivo_destino):
                    # Mover de volta para a origem
                    import shutil
                    shutil.move(arquivo_destino, arquivo_origem)
                    
                    # Registrar no histórico
                    adicionar_ao_historico(arquivo_destino, arquivo_origem, 
                                         f"Desfeito: {operacao.get('descricao', '')}", "desfeito")
                    
                    arquivos_desfeitos += 1
                else:
                    erros += 1
                    
            except Exception as e:
                erros += 1
        
        # Limpar dados temporários após desfazer
        limpar_dados_desfazer()
        
        if arquivos_desfeitos > 0:
            return True, f"{arquivos_desfeitos} arquivo(s) desfeito(s) com sucesso. {erros} erro(s)."
        else:
            return False, f"Nenhum arquivo foi desfeito. {erros} erro(s)."
            
    except Exception as e:
        return False, f"Erro ao desfazer operação: {str(e)}"

def nome_cliente_para_pasta(nome_cliente):
    """Converte o nome do cliente em um nome de pasta válido"""
    try:
        if not nome_cliente:
            return "cliente_desconhecido"
        
        # Remover caracteres especiais e substituir espaços por underscores
        nome_limpo = re.sub(r'[^\w\s-]', '', nome_cliente)
        nome_limpo = re.sub(r'[-\s]+', '_', nome_limpo)
        nome_limpo = nome_limpo.strip('_')
        
        # Limitar o tamanho da pasta
        if len(nome_limpo) > 50:
            nome_limpo = nome_limpo[:50]
        
        return nome_limpo if nome_limpo else "cliente_desconhecido"
        
    except Exception as e:
        return "cliente_desconhecido"

def identificar_cliente_por_cnpj(cnpj_formatado, clientes):
    """Identifica o cliente baseado no CNPJ formatado"""
    try:
        # Compara diretamente com os CNPJs cadastrados (que já estão formatados)
        nome_cliente = clientes.get(cnpj_formatado, '')
        return nome_cliente if nome_cliente else None
        
    except Exception as e:
        return None

def identificar_tipo_dentro_pasta_cliente(arquivo, estrutura, nome_cliente):
    """Identifica o tipo de PDF dentro da estrutura modelo para criar a pasta do cliente"""
    try:
        # Verificar se o arquivo é válido
        if not arquivo or not arquivo.filename:
            return None, None
            
        # Resetar a posição do cursor do arquivo para o início
        arquivo.seek(0)
        
        # Verificar se o arquivo tem conteúdo
        conteudo = arquivo.read()
        if not conteudo:
            return None, None
            
        # Resetar novamente para o início
        arquivo.seek(0)
        
        # Extrair texto do PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(conteudo))
        
        if len(pdf_reader.pages) == 0:
            return None, None
            
        texto_completo = ""
        for pagina in pdf_reader.pages:
            try:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + " "
            except Exception as e:
                continue
        
        if not texto_completo.strip():
            return None, None
            
        texto_completo = texto_completo.lower()
        
        # NOVA LÓGICA: A estrutura modelo define as categorias principais e subcategorias
        # Não precisamos mais procurar por pastas que correspondam ao cliente
        # Apenas analisamos o conteúdo do PDF para determinar a categoria
        
        melhor_categoria = None
        melhor_subcategoria = None
        melhor_score = 0
        
        # Percorrer a estrutura modelo (primeiro item da lista)
        if isinstance(estrutura, list) and len(estrutura) > 0:
            estrutura_modelo = estrutura[0]  # Primeiro item é a estrutura modelo
            
            for categoria_principal, subcategorias in estrutura_modelo.items():
                if isinstance(subcategorias, dict):
                    for subcategoria, palavras_chave in subcategorias.items():
                        if isinstance(palavras_chave, list):
                            score = 0
                            for palavra in palavras_chave:
                                if palavra.lower() in texto_completo:
                                    score += 1
                            
                            if score > melhor_score:
                                melhor_score = score
                                melhor_categoria = categoria_principal
                                melhor_subcategoria = subcategoria
        else:
            # Fallback: se estrutura não for lista, usar diretamente
            for categoria_principal, subcategorias in estrutura.items():
                if isinstance(subcategorias, dict):
                    for subcategoria, palavras_chave in subcategorias.items():
                        if isinstance(palavras_chave, list):
                            score = 0
                            for palavra in palavras_chave:
                                if palavra.lower() in texto_completo:
                                    score += 1
                            
                            if score > melhor_score:
                                melhor_score = score
                                melhor_categoria = categoria_principal
                                melhor_subcategoria = subcategoria
        
        # Retorna a categoria e subcategoria se tiver pelo menos 1 palavra-chave
        if melhor_score > 0:
            return melhor_categoria, melhor_subcategoria
        
        return None, None
        
    except Exception as e:
        return None, None

def identificar_tipo_pdf_por_palavras_chave(arquivo, estrutura):
    """Identifica o tipo de PDF baseado em palavras-chave no conteúdo"""
    try:
        # Verificar se o arquivo é válido
        if not arquivo or not arquivo.filename:
            return None
            
        # Resetar a posição do cursor do arquivo para o início
        arquivo.seek(0)
        
        # Verificar se o arquivo tem conteúdo
        conteudo = arquivo.read()
        if not conteudo:
            return None
            
        # Resetar novamente para o início
        arquivo.seek(0)
        
        # Extrair texto do PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(conteudo))
        
        if len(pdf_reader.pages) == 0:
            return None
            
        texto_completo = ""
        for pagina in pdf_reader.pages:
            try:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + " "
            except Exception as e:
                continue
        
        if not texto_completo.strip():
            return None
            
        texto_completo = texto_completo.lower()
        
        # Buscar na estrutura por palavras-chave que correspondam ao texto
        melhor_match = None
        melhor_score = 0
        
        # Usar a estrutura modelo (primeiro item da lista)
        if isinstance(estrutura, list) and len(estrutura) > 0:
            estrutura_modelo = estrutura[0]
        else:
            estrutura_modelo = estrutura
        
        for pasta_nome, pasta_conteudo in estrutura_modelo.items():
            if isinstance(pasta_conteudo, dict):
                for pdf_nome, palavras_chave in pasta_conteudo.items():
                    if isinstance(palavras_chave, list):
                        score = 0
                        for palavra in palavras_chave:
                            if palavra.lower() in texto_completo:
                                score += 1
                        
                        if score > melhor_score:
                            melhor_score = score
                            melhor_match = pasta_nome
        
        # Retorna o melhor match se tiver pelo menos 1 palavra-chave
        return melhor_match if melhor_score > 0 else None
        
    except Exception as e:
        return None

@app.route('/analisar_pdfs_organizar', methods=['POST'])
def analisar_pdfs_organizar():
    """Analisa PDFs para organização baseada em CNPJs e estrutura matriz"""
    global progress, logs
    progress = 0
    logs = []
    
    try:
        if 'pdfs' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'})
        
        arquivos = request.files.getlist('pdfs')
        if not arquivos or all(arquivo.filename == '' for arquivo in arquivos):
            return jsonify({'success': False, 'message': 'Nenhum arquivo PDF selecionado'})
        
        # Carregar dados necessários
        clientes = ler_clientes()
        estrutura = ler_estrutura()
        matriz = ler_matriz()
        
        if not matriz:
            return jsonify({'success': False, 'message': 'Pasta matriz não configurada. Configure primeiro na seção de Cadastro de Dados.'})
        
        # Verificar se a estrutura modelo existe
        if not estrutura or (isinstance(estrutura, list) and len(estrutura) == 0):
            return jsonify({'success': False, 'message': 'Estrutura modelo não configurada. Configure primeiro na seção de Estrutura.'})
        
        # Criar pasta de uploads se não existir
        pasta_uploads = os.path.join(os.getcwd(), "uploads")
        os.makedirs(pasta_uploads, exist_ok=True)
        
        logs.append(f"Iniciando análise de {len(arquivos)} PDFs...")
        progress = 10
        
        resultados = []
        total_pdfs = len(arquivos)
        pdfs_identificados = 0
        pdfs_nao_identificados = 0
        total_cnpjs = 0
        
        for i, arquivo in enumerate(arquivos):
            if arquivo.filename and arquivo.filename.lower().endswith('.pdf'):
                logs.append(f"Analisando {arquivo.filename}...")
                
                # Salvar arquivo na pasta uploads
                nome_arquivo = secure_filename(arquivo.filename)
                caminho_arquivo = os.path.join(pasta_uploads, nome_arquivo)
                arquivo.save(caminho_arquivo)
                
                # Processar PDF
                cnpjs_pdf = processar_pdf(arquivo)
                total_cnpjs += len(cnpjs_pdf)
                
                # Identificar cliente e tipo de PDF baseado nos CNPJs
                cliente_identificado = None
                tipo_identificado = None
                destino = None
                cnpj_encontrado = False
                
                # PRIMEIRO: Verificar se há CNPJs no PDF (OBRIGATÓRIO)
                if cnpjs_pdf:
                    cnpj_encontrado = True
                    logs.append(f"✓ CNPJ(s) encontrado(s) em {arquivo.filename}")
                    
                    # SEGUNDO: Tentar identificar cliente por CNPJ cadastrado
                    # NOVA LÓGICA: Se houver múltiplos CNPJs conhecidos, usar o SEGUNDO
                    cnpjs_cadastrados = []
                    
                    # Primeiro, coletar todos os CNPJs cadastrados
                    for cnpj_info in cnpjs_pdf:
                        cnpj_formatado = cnpj_info['cnpj']
                        cliente = identificar_cliente_por_cnpj(cnpj_formatado, clientes)
                        if cliente:
                            cnpjs_cadastrados.append({
                                'cnpj': cnpj_formatado,
                                'cliente': cliente,
                                'posicao': len(cnpjs_cadastrados) + 1
                            })
                    
                    # Decidir qual CNPJ usar baseado na quantidade encontrada
                    if len(cnpjs_cadastrados) == 0:
                        logs.append(f"✗ Nenhum CNPJ cadastrado encontrado")
                    elif len(cnpjs_cadastrados) == 1:
                        # Se só há um CNPJ cadastrado, usar ele
                        cnpj_selecionado = cnpjs_cadastrados[0]
                        cliente_identificado = cnpj_selecionado['cliente']
                        logs.append(f"✓ Cliente identificado (único): {cliente_identificado} (CNPJ #{cnpj_selecionado['posicao']})")
                    else:
                        # Se há múltiplos CNPJs cadastrados, usar o SEGUNDO
                        if len(cnpjs_cadastrados) >= 2:
                            cnpj_selecionado = cnpjs_cadastrados[1]  # Segundo CNPJ (índice 1)
                            cliente_identificado = cnpj_selecionado['cliente']
                            logs.append(f"✓ Cliente identificado (segundo de {len(cnpjs_cadastrados)}): {cliente_identificado} (CNPJ #{cnpj_selecionado['posicao']})")
                        else:
                            # Fallback: usar o primeiro se não houver segundo
                            cnpj_selecionado = cnpjs_cadastrados[0]
                            cliente_identificado = cnpj_selecionado['cliente']
                            logs.append(f"✓ Cliente identificado (fallback): {cliente_identificado} (CNPJ #{cnpj_selecionado['posicao']})")
                    
                    # Se identificou um cliente, tentar determinar o tipo
                    if cliente_identificado:
                        # TERCEIRO: Identificar o tipo de PDF baseado na estrutura modelo
                        categoria_principal, subcategoria = identificar_tipo_dentro_pasta_cliente(arquivo, estrutura, cliente_identificado)
                        
                        if categoria_principal and subcategoria:
                            # NOVA LÓGICA: Criar estrutura de pastas: Matriz/Cliente/Categoria/Subcategoria
                            pasta_cliente = nome_cliente_para_pasta(cliente_identificado)
                            tipo_identificado = f"{categoria_principal}/{subcategoria}"
                            destino = os.path.join(matriz, pasta_cliente, categoria_principal, subcategoria)
                            logs.append(f"✓ Tipo identificado: {tipo_identificado}")
                        else:
                            logs.append(f"✗ Tipo não determinado pela estrutura modelo")
                else:
                    logs.append(f"✗ Nenhum CNPJ encontrado em {arquivo.filename} - arquivo não será movido")
                
                # Só é identificado se TEM CNPJ, CLIENTE identificado E TIPO determinado
                identificado = cnpj_encontrado and cliente_identificado and tipo_identificado is not None
                if identificado:
                    pdfs_identificados += 1
                    logs.append(f"✓ {arquivo.filename} identificado - Cliente: {cliente_identificado}, Tipo: {tipo_identificado}")
                else:
                    pdfs_nao_identificados += 1
                    if not cnpj_encontrado:
                        logs.append(f"✗ {arquivo.filename} não identificado - nenhum CNPJ encontrado")
                    elif not cliente_identificado:
                        logs.append(f"✗ {arquivo.filename} não identificado - CNPJ não cadastrado")
                    else:
                        logs.append(f"✗ {arquivo.filename} não identificado - tipo não determinado dentro da pasta do cliente")
                
                # Adicionar informação sobre qual CNPJ foi selecionado
                cnpj_selecionado_info = None
                if 'cnpj_selecionado' in locals():
                    cnpj_selecionado_info = {
                        'cnpj': cnpj_selecionado['cnpj'],
                        'posicao': cnpj_selecionado['posicao'],
                        'total_cnpjs_cadastrados': len(cnpjs_cadastrados) if 'cnpjs_cadastrados' in locals() else 0
                    }
                
                resultados.append({
                    'nome': arquivo.filename,
                    'cnpjs': [cnpj['cnpj'] for cnpj in cnpjs_pdf],
                    'identificado': identificado,
                    'cliente': cliente_identificado,
                    'tipo': tipo_identificado,
                    'destino': destino,
                    'cnpj_selecionado': cnpj_selecionado_info
                })
                
                progress = 10 + ((i + 1) / total_pdfs) * 80
        
        logs.append("Análise concluída!")
        progress = 100
        
        return jsonify({
            'success': True,
            'results': resultados,
            'total_pdfs': total_pdfs,
            'pdfs_identificados': pdfs_identificados,
            'pdfs_nao_identificados': pdfs_nao_identificados,
            'total_cnpjs': total_cnpjs
        })
        
    except Exception as e:
        logs.append(f"Erro na análise: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro durante a análise: {str(e)}'})

@app.route('/status_organizacao')
def status_organizacao():
    """Retorna o status atual da organização"""
    return jsonify({'progress': progress, 'logs': logs})

@app.route('/organizar_pdfs_executar', methods=['POST'])
def organizar_pdfs_executar():
    """Executa a organização dos PDFs baseado nos resultados da análise"""
    global progress, logs
    progress = 0
    logs = []
    
    try:
        data = request.get_json()
        resultados = data.get('results', [])
        
        if not resultados:
            return jsonify({'success': False, 'message': 'Nenhum resultado de análise fornecido'})
        
        logs.append("Iniciando organização dos PDFs...")
        progress = 10
        
        movidos = 0
        erros = 0
        operacoes_realizadas = []  # Lista para armazenar operações para desfazer
        
        # Criar pasta de uploads se não existir
        pasta_uploads = os.path.join(os.getcwd(), "uploads")
        os.makedirs(pasta_uploads, exist_ok=True)
        
        for i, resultado in enumerate(resultados):
            # Verificar se o arquivo tem CNPJs (OBRIGATÓRIO)
            if not resultado.get('cnpjs') or len(resultado['cnpjs']) == 0:
                logs.append(f"✗ {resultado['nome']} não organizado - nenhum CNPJ encontrado")
                continue
            
            # Verificar se foi identificado, tem cliente e tem destino
            if resultado['identificado'] and resultado.get('cliente') and resultado['destino']:
                try:
                    # Criar diretório de destino se não existir
                    os.makedirs(resultado['destino'], exist_ok=True)
                    
                    # Nome do arquivo seguro
                    nome_arquivo = secure_filename(resultado['nome'])
                    caminho_destino = os.path.join(resultado['destino'], nome_arquivo)
                    
                    # Tentar encontrar o arquivo na pasta de uploads
                    arquivo_origem = os.path.join(pasta_uploads, nome_arquivo)
                    
                    if os.path.exists(arquivo_origem):
                        # Mover o arquivo real
                        descricao = f"Cliente: {resultado['cliente']}, Tipo: {resultado['tipo']}"
                        sucesso, registro = mover_arquivo_com_historico(arquivo_origem, caminho_destino, descricao)
                        if sucesso:
                            movidos += 1
                            logs.append(f"✓ {nome_arquivo} movido para {resultado['destino']}")
                            
                            # Adicionar à lista de operações para desfazer
                            operacoes_realizadas.append({
                                'arquivo': nome_arquivo,
                                'local_antigo': arquivo_origem,
                                'novo_local': caminho_destino,
                                'descricao': descricao
                            })
                        else:
                            erros += 1
                            logs.append(f"✗ Erro ao mover {resultado['nome']}: {registro}")
                    else:
                        # Se não encontrar o arquivo, criar um arquivo de exemplo
                        with open(caminho_destino, 'w') as f:
                            f.write(f"Arquivo organizado: {resultado['nome']}\nCliente: {resultado['cliente']}\nTipo: {resultado['tipo']}")
                        
                        # Registrar no histórico
                        descricao = f"Cliente: {resultado['cliente']}, Tipo: {resultado['tipo']}"
                        adicionar_ao_historico(resultado['nome'], caminho_destino, descricao, "transferido")
                        
                        movidos += 1
                        logs.append(f"✓ {nome_arquivo} organizado para {resultado['destino']}")
                        
                        # Adicionar à lista de operações para desfazer
                        operacoes_realizadas.append({
                            'arquivo': nome_arquivo,
                            'local_antigo': arquivo_origem,
                            'novo_local': caminho_destino,
                            'descricao': descricao
                        })
                    
                except Exception as e:
                    erros += 1
                    logs.append(f"✗ Erro ao organizar {resultado['nome']}: {str(e)}")
            else:
                if not resultado.get('cnpjs') or len(resultado['cnpjs']) == 0:
                    logs.append(f"✗ {resultado['nome']} não organizado - nenhum CNPJ encontrado")
                elif not resultado.get('cliente'):
                    logs.append(f"✗ {resultado['nome']} não organizado - CNPJ não cadastrado")
                else:
                    logs.append(f"✗ {resultado['nome']} não organizado - tipo não determinado pela estrutura modelo")
            
            progress = 10 + ((i + 1) / len(resultados)) * 80
        
        logs.append("Organização concluída!")
        progress = 100
        
        # Salvar dados temporários para desfazer se houve operações realizadas
        if operacoes_realizadas:
            salvar_dados_desfazer(operacoes_realizadas)
        
        return jsonify({
            'success': True,
            'movidos': movidos,
            'erros': erros,
            'message': f'Organização concluída. {movidos} PDFs movidos, {erros} erros.'
        })
        
    except Exception as e:
        logs.append(f"Erro na organização: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro durante a organização: {str(e)}'})

@app.route('/desfazer_ultima_operacao', methods=['POST'])
def desfazer_ultima_operacao_route():
    """Rota para desfazer a última operação de movimentação"""
    try:
        sucesso, mensagem = desfazer_ultima_operacao()
        return jsonify({
            'success': sucesso,
            'message': mensagem
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao desfazer operação: {str(e)}'
        })

@app.route('/limpar_historico_invalido', methods=['POST'])
def limpar_historico_invalido_route():
    """Rota para limpar operações inválidas do histórico"""
    try:
        operacoes_removidas = limpar_historico_invalido()
        
        if operacoes_removidas > 0:
            return jsonify({
                'success': True,
                'message': f'{operacoes_removidas} operações inválidas removidas do histórico'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Nenhuma operação inválida encontrada no histórico'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao limpar histórico: {str(e)}'
        })

@app.route('/converter_historico_antigo', methods=['POST'])
def converter_historico_antigo_route():
    """Rota para converter histórico antigo para novo formato"""
    try:
        operacoes_convertidas = converter_historico_antigo()
        
        if operacoes_convertidas > 0:
            return jsonify({
                'success': True,
                'message': f'{operacoes_convertidas} operações convertidas do formato antigo'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Nenhuma operação antiga encontrada para converter'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao converter histórico: {str(e)}'
        })

@app.route('/visualizar_historico')
def visualizar_historico():
    """Rota para visualizar o histórico de operações"""
    try:
        historico = ler_historico()
        return render_template('visualizar_historico.html', historico=historico)
    except Exception as e:
        return render_template('visualizar_historico.html', historico={}, erro=str(e))

@app.route('/sair', methods=['POST'])
def sair_aplicacao():
    """Encerra o aplicativo de forma segura"""
    try:
        # Função para encerrar o servidor em uma thread separada
        def shutdown_server():
            time.sleep(1)  # Pequeno delay para permitir resposta ao cliente
            
            # Tentar encerrar de forma mais elegante primeiro
            try:
                import signal
                import sys
                # Enviar sinal de encerramento
                os.kill(os.getpid(), signal.SIGTERM)
            except:
                # Se falhar, usar método mais direto
                os._exit(0)
        
        # Iniciar thread para encerrar o servidor
        threading.Thread(target=shutdown_server, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': 'Aplicação será encerrada em alguns segundos...'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao encerrar aplicação: {str(e)}'
        })

@app.route('/buscar_cnpj_api', methods=['POST'])
def buscar_cnpj_api():
    """Busca dados de um CNPJ na API externa"""
    try:
        data = request.get_json()
        cnpj = data.get('cnpj', '').strip()
        
        if not cnpj:
            return jsonify({'success': False, 'message': 'CNPJ não fornecido'})
        
        # Usar a função existente para buscar dados da empresa
        dados_empresa = buscar_dados_empresa(cnpj)
        
        if dados_empresa and dados_empresa.get('nome'):
            return jsonify({
                'success': True,
                'nome': dados_empresa['nome'],
                'cnpj': dados_empresa.get('cnpj', cnpj),
                'email': dados_empresa.get('email', ''),
                'telefone': dados_empresa.get('telefone', ''),
                'logradouro': dados_empresa.get('logradouro', ''),
                'numero': dados_empresa.get('numero', ''),
                'complemento': dados_empresa.get('complemento', ''),
                'bairro': dados_empresa.get('bairro', ''),
                'municipio': dados_empresa.get('municipio', ''),
                'uf': dados_empresa.get('uf', ''),
                'cep': dados_empresa.get('cep', '')
            })
        else:
            return jsonify({'success': False, 'message': 'CNPJ não encontrado na API'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar CNPJ: {str(e)}'})

def signal_handler(signum, frame):
    """Handler para capturar sinais de encerramento"""
    print("\nEncerrando aplicação...")
    os._exit(0)

if __name__ == '__main__':
    # Configurar handler de sinal para encerramento elegante
    import signal
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Sinal de encerramento
    
    # Verificar se deve abrir o navegador automaticamente
    import sys
    abrir_browser = True
    
    # Se o argumento --no-browser for passado, não abrir o navegador
    if '--no-browser' in sys.argv:
        abrir_browser = False
    
    if abrir_browser:
        threading.Thread(target=abrir_navegador).start()
    
    # Mensagem simples para o usuário
    print("=" * 60)
    print("PDF ORGANIZER - SERVIDOR")
    print("=" * 60)
    print("Este console é apenas o servidor do Pdf-Organizer.")
    print("Abra o seguinte site para interagir com o sistema:")
    print("")
    print("    http://localhost:5000")
    print("")
    print("Caso feche este console, você deverá abrir o aplicativo novamente.")
    print("=" * 60)
    
    try:
        #app.run(debug=False, use_reloader=False)
        app.run(debug=True, use_reloader=False)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
