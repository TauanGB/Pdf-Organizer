#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar as mensagens melhoradas de salvamento
"""

import json
import os
import sys

# Adicionar o diretório atual ao path para importar as funções
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import (
    ler_clientes, 
    salvar_cliente, 
    verificar_cnpj_ja_existe
)

def testar_mensagens_melhoradas():
    """Testa as mensagens melhoradas de salvamento"""
    print("=== Testando Mensagens Melhoradas ===")
    
    # CNPJs de teste: alguns novos, alguns que já existem
    cnpjs_teste = [
        {
            'cnpj': '12345678000190',  # Novo
            'nome': 'EMPRESA NOVA 1 LTDA'
        },
        {
            'cnpj': '35709387000134',  # Já existe (DIDATA)
            'nome': 'DIDATA SISTEMAS E CONSULTORIA LTDA'
        },
        {
            'cnpj': '59959632000120',  # Já existe (PL INDUSTRIA)
            'nome': 'PL INDUSTRIA, COMERCIO E SERVICOS DE TRANSPORTES LTDA'
        },
        {
            'cnpj': '99999999000199',  # Novo
            'nome': 'EMPRESA NOVA 2 LTDA'
        },
        {
            'cnpj': '88888888000188',  # Novo
            'nome': 'EMPRESA NOVA 3 LTDA'
        }
    ]
    
    print(f"Testando {len(cnpjs_teste)} CNPJs...")
    
    salvos = 0
    ja_existem = 0
    erros = 0
    
    for i, dados in enumerate(cnpjs_teste):
        print(f"\nProcessando CNPJ {i+1}/{len(cnpjs_teste)}:")
        print(f"  CNPJ: {dados['cnpj']}")
        print(f"  Nome: {dados['nome']}")
        
        # Verificar se já existe
        if verificar_cnpj_ja_existe(dados['cnpj']):
            ja_existem += 1
            print(f"  ℹ Já existe no sistema")
        else:
            # Tentar salvar
            resultado = salvar_cliente(dados['cnpj'], dados['nome'])
            if resultado:
                salvos += 1
                print(f"  ✓ Salvo com sucesso")
            else:
                erros += 1
                print(f"  ✗ Falha no salvamento")
    
    print(f"\n=== Resultado Final ===")
    print(f"Salvos: {salvos}")
    print(f"Já existiam: {ja_existem}")
    print(f"Erros: {erros}")
    
    # Simular as mensagens que apareceriam na interface
    print(f"\n=== Mensagens que apareceriam na interface ===")
    if salvos > 0:
        print(f"✓ {salvos} CNPJ(s) salvo(s) com sucesso!")
    if ja_existem > 0:
        print(f"ℹ {ja_existem} CNPJ(s) já existiam no sistema e não foram duplicados.")
    if erros > 0:
        print(f"✗ {erros} CNPJ(s) não puderam ser salvos. Verifique os logs do console.")

def main():
    """Função principal"""
    print("TESTE DE MENSAGENS MELHORADAS")
    print("=" * 50)
    
    try:
        testar_mensagens_melhoradas()
        
        print("\n" + "=" * 50)
        print("TESTE CONCLUÍDO")
        
    except Exception as e:
        print(f"ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
