#!/usr/bin/env python3
"""
Script final para criar o executável Pdf-Organizer com ícone

IMPORTANTE: Este script foi configurado para mostrar o console
O console é essencial para o usuário saber que o servidor está rodando
e como acessar a interface web (http://localhost:5000)

Se quiser ocultar o console, adicione a flag --windowed ao comando PyInstaller
"""

import os
import sys
import subprocess
import platform

def verificar_requisitos():
    """Verifica se todos os requisitos estão atendidos"""
    print("🔍 Verificando requisitos...")
    
    # Verificar arquivos essenciais
    arquivos_essenciais = ["app.py", "icone.ico", "templates"]
    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo} encontrado")
        else:
            print(f"❌ {arquivo} não encontrado")
            return False
    
    # Verificar PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado")
        print("Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    return True

def limpar_builds():
    """Remove builds anteriores"""
    print("🧹 Limpando builds anteriores...")
    
    pastas_para_limpar = ["build", "dist", "__pycache__"]
    for pasta in pastas_para_limpar:
        if os.path.exists(pasta):
            try:
                import shutil
                shutil.rmtree(pasta)
                print(f"✅ {pasta} removida")
            except Exception as e:
                print(f"⚠️ Erro ao remover {pasta}: {e}")

def criar_executavel_final():
    """Cria o executável final com ícone"""
    print("🔨 Criando executável final...")
    
    # Comando PyInstaller otimizado
    # ATENÇÃO: Removida flag --windowed para que o console apareça
    # O console é importante para o usuário saber que o servidor está rodando
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=Pdf-Organizer",
        "--icon=icone.ico",
        "--add-data=templates;templates",
        "--add-data=trash-can.png;.",
        "--hidden-import=flask",
        "--hidden-import=PyPDF2",
        "--hidden-import=requests",
        "--hidden-import=tkinter",
        "--hidden-import=webbrowser",
        "--hidden-import=threading",
        "--hidden-import=sys",
        "--hidden-import=signal",
        "--exclude-module=testes",
        "--exclude-module=build",
        "--exclude-module=__pycache__",
        "--exclude-module=venv",
        "app.py"
    ]
    
    print(f"Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executável criado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar executável: {e}")
        print(f"Saída de erro: {e.stderr}")
        return False

def verificar_resultado():
    """Verifica se o executável foi criado corretamente"""
    print("🔍 Verificando resultado...")
    
    executavel_path = "dist/Pdf-Organizer.exe" if platform.system() == "Windows" else "dist/Pdf-Organizer"
    
    if os.path.exists(executavel_path):
        tamanho = os.path.getsize(executavel_path)
        print(f"✅ Executável criado: {executavel_path}")
        print(f"📏 Tamanho: {tamanho} bytes ({tamanho/1024/1024:.1f} MB)")
        
        if tamanho > 10000000:  # Mais de 10MB
            print("✅ Executável parece válido")
            return True
        else:
            print("⚠️ Executável muito pequeno, pode estar corrompido")
            return False
    else:
        print(f"❌ Executável não encontrado: {executavel_path}")
        return False

def mostrar_instrucoes_finais():
    """Mostra instruções finais"""
    print("\n🎉 EXECUTÁVEL CRIADO COM SUCESSO!")
    print("=" * 50)
    print("📁 Localização: dist/Pdf-Organizer.exe")
    print("🎨 Ícone aplicado: icone.ico")
    print("📏 Tamanho: ~17MB")
    print("🖥️ Console: Visível (importante para o usuário)")
    
    print("\n🧪 COMO TESTAR:")
    print("1. Vá para a pasta 'dist'")
    print("2. Execute 'Pdf-Organizer.exe'")
    print("3. Verifique se o console aparece com a mensagem do servidor")
    print("4. Verifique se o ícone aparece no explorador")
    print("5. Teste todas as funcionalidades")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Teste o executável completamente")
    print("2. Verifique se o ícone aparece corretamente")
    print("3. Distribua para os usuários finais")
    print("4. Crie um atalho na área de trabalho se necessário")

def main():
    """Função principal"""
    print("🚀 Criador de Executável Final - Pdf-Organizer")
    print("=" * 60)
    
    # Verificar requisitos
    if not verificar_requisitos():
        print("❌ Requisitos não atendidos!")
        return False
    
    # Limpar builds anteriores
    limpar_builds()
    
    # Criar executável final
    if not criar_executavel_final():
        return False
    
    # Verificar resultado
    if not verificar_resultado():
        return False
    
    # Mostrar instruções finais
    mostrar_instrucoes_finais()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
