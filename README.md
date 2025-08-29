# Organizador de PDFs

Sistema inteligente para organização automática de PDFs baseado em CNPJs e estruturas personalizadas.

[![Download](https://img.shields.io/badge/Download-Executável-brightgreen)](https://github.com/seu-usuario/Pdf-Organizer/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🚀 Funcionalidades Principais

### 1. **Organização Automática de PDFs** ⭐ (Função Principal)
- **Upload múltiplo** de arquivos PDF
- **Análise automática** de CNPJs nos documentos
- **Identificação inteligente** do tipo de documento
- **Movimentação automática** para pastas corretas
- **Interface visual** com progresso em tempo real
- **Logs detalhados** do processamento

### 2. **Auto Reconhecimento de CNPJs**
- **Extração automática**: Identifica CNPJs válidos em PDFs
- **Validação completa**: Verifica dígitos verificadores dos CNPJs
- **Interface intuitiva**: Upload múltiplo de PDFs e análise visual
- **Edição de nomes**: Permite editar nomes das empresas encontradas
- **Seleção flexível**: Escolha quais CNPJs salvar

### 3. **Gestão de Estruturas**
- **Cadastro de CNPJs**: Adicione empresas manualmente
- **Estruturação de pastas**: Organize documentos por categorias
- **Palavras-chave**: Defina critérios para classificação automática
- **Pasta matriz**: Configure diretório base para organização

## 📋 Pré-requisitos

### Para Usuários do Executável
- **Windows**: Windows 7 ou superior
- **Linux**: Distribuições baseadas em Ubuntu/Debian
- **macOS**: macOS 10.12 ou superior
- **Navegador**: Chrome, Firefox, Safari ou Edge

### Para Desenvolvedores
- Python 3.8+
- Dependências listadas em `requirements.txt`

## 📥 Downloads

### Versões Disponíveis

| Plataforma | Arquivo | Tamanho | Download |
|------------|---------|---------|----------|
| Windows | `Pdf-Organizer.exe` | ~50MB | [Download](https://github.com/seu-usuario/Pdf-Organizer/releases/latest/download/Pdf-Organizer.exe) |
| Linux | `Pdf-Organizer` | ~45MB | [Download](https://github.com/seu-usuario/Pdf-Organizer/releases/latest/download/Pdf-Organizer) |
| macOS | `Pdf-Organizer` | ~45MB | [Download](https://github.com/seu-usuario/Pdf-Organizer/releases/latest/download/Pdf-Organizer-mac) |

### 📋 Notas de Release

- **v1.0.0**: Versão inicial com funcionalidades básicas
- **v1.1.0**: Melhorias na interface e correções de bugs
- **v1.2.0**: Adicionado suporte a múltiplos CNPJs

## 🛠️ Instalação

### Opção 1: Executável (Recomendado para Usuários Finais)

1. **Baixe a versão executável** mais recente na seção [Releases](https://github.com/seu-usuario/Pdf-Organizer/releases)
2. **Execute o arquivo** `Pdf-Organizer.exe` (Windows) ou `Pdf-Organizer` (Linux/Mac)
3. **Acesse no navegador**: `http://localhost:5000`

### Opção 2: Código Fonte (Para Desenvolvedores)

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd Pdf-Organizer
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python app.py
```

4. Acesse no navegador: `http://localhost:5000`

**Opções de execução:**
- `python app.py` - Abre o navegador automaticamente
- `python app.py --no-browser` - Não abre o navegador automaticamente

## 🎯 Como Usar - Organização de PDFs

### Passo 1: Configurar a Estrutura
1. Acesse "Cadastro de Dados"
2. Configure a pasta matriz (onde os PDFs serão organizados)
3. Adicione pastas e tipos de documentos com palavras-chave
4. Cadastre os CNPJs das empresas

### Passo 2: Organizar PDFs
1. Clique em "Organizar PDFs" (botão principal verde)
2. Selecione os arquivos PDF para processar
3. Clique em "Analisar PDFs"
4. Revise os resultados da análise
5. Clique em "Organizar PDFs" para mover os arquivos

## 🚪 Como Encerrar o Aplicativo

### Método 1: Botão Sair (Recomendado)
1. Clique no botão **"Sair"** na página principal
2. Confirme a ação no diálogo
3. O aplicativo será encerrado automaticamente

### Método 2: Tecla de Atalho
- Pressione **ESC** em qualquer página para sair rapidamente

### Método 3: Terminal/Console
- Pressione **Ctrl+C** no terminal onde o aplicativo está rodando

### Método 4: Executável
- Feche a janela do navegador
- O aplicativo será encerrado automaticamente após alguns segundos

## 🧪 Teste Rápido

### Para Usuários do Executável
O software já vem com dados de exemplo integrados. Basta executar o aplicativo e usar a funcionalidade de teste.

### Para Desenvolvedores
Para testar a funcionalidade com dados de exemplo:

```bash
cd testes
python teste_organizacao.py
```

Isso criará:
- Estrutura de teste com pastas e palavras-chave
- Clientes de teste com CNPJs válidos
- PDFs de teste para demonstração

**Nota:** Todos os arquivos de teste estão organizados na pasta `testes/`. Consulte o `README.md` dentro desta pasta para mais detalhes sobre os testes disponíveis.

## 📖 Como Usar - Outras Funcionalidades

### Auto Reconhecimento de CNPJs

1. **Acesse a página de cadastro** e clique em "Auto Reconhecer CNPJs"
2. **Faça upload dos PDFs** que deseja analisar
3. **Revise os CNPJs encontrados** na tabela
4. **Edite os nomes das empresas** conforme necessário
5. **Selecione quais CNPJs salvar** usando os checkboxes
6. **Clique em "Salvar CNPJs Selecionados"**

### Gestão de Estruturas

1. **Cadastre CNPJs** na seção "Cadastro de CNPJs"
2. **Configure estruturas** para organização dos documentos
3. **Defina pasta matriz** onde os PDFs estão localizados
4. **Organize PDFs** automaticamente baseado nas regras

## 🔧 Tecnologias Utilizadas

- **Flask**: Framework web
- **PyPDF2**: Processamento de PDFs
- **ReportLab**: Geração de PDFs de teste
- **Bootstrap 5**: Interface responsiva
- **JavaScript**: Interatividade da interface
- **Font Awesome**: Ícones
- **PyInstaller**: Empacotamento para versão executável

## 📁 Estrutura de Arquivos

```
Pdf-Organizer/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências
├── templates/            # Templates HTML
│   ├── index.html        # Página inicial
│   ├── organizar_pdfs.html # Interface de organização
│   └── ...
├── Clientes.json         # CNPJs cadastrados
├── estrutura.json        # Estruturas de organização
├── Historico.json        # Histórico de operações
├── icone.ico             # Ícone do aplicativo
├── trash-can.png         # Ícone alternativo
├── testes/               # Arquivos de teste (não incluídos no executável)
├── build/                # Arquivos de build (gerados automaticamente)
├── main.spec             # Configuração PyInstaller
├── OrganizePDF.spec      # Configuração alternativa PyInstaller
└── setup.py              # Configuração cx_Freeze
```

## 🎯 Características Técnicas

### Versão Executável
- **Aplicação standalone**: Não requer instalação de Python
- **Interface web integrada**: Servidor web embutido
- **Dados persistentes**: Configurações salvas localmente
- **Multiplataforma**: Windows, Linux e macOS
- **Auto-inicialização**: Abre navegador automaticamente

### Organização Automática
- **Análise inteligente**: Identifica tipos de PDF por CNPJ e palavras-chave
- **Movimentação segura**: Cria diretórios automaticamente
- **Progresso visual**: Barra de progresso e logs em tempo real
- **Tratamento de erros**: Feedback detalhado sobre problemas

### Validação de CNPJ
- Algoritmo oficial de validação com dígitos verificadores
- Reconhece CNPJs formatados (XX.XXX.XXX/XXXX-XX) ou sem formatação
- Filtra apenas CNPJs válidos

### Processamento de PDFs
- Extração de texto completo dos documentos
- Análise de contexto ao redor dos CNPJs
- Suporte a múltiplos arquivos simultâneos

### Interface Responsiva
- Design moderno com Bootstrap 5
- Funcionalidades interativas com JavaScript
- Feedback visual em tempo real
- Ícones intuitivos com Font Awesome
- Encerramento elegante do aplicativo

### Console Limpo e Profissional
- **Interface limpa**: Console mostra apenas informações essenciais para o usuário
- **Sem logs técnicos**: Logs de debug e requisições HTTP suprimidos
- **Mensagem clara**: Indica que é o servidor e como acessar a interface web
- **Configurável**: Código de supressão de logs pode ser facilmente comentado para debug

## 🚀 Criando o Executável

### Para Desenvolvedores

#### Opção 1: Script Automático (Recomendado)

Use o script de build incluído:

```bash
python build_executable.py
```

Este script:
- Verifica se o PyInstaller está instalado
- Instala automaticamente se necessário
- Cria o executável com todas as configurações corretas
- Exclui arquivos de teste e desenvolvimento

#### Opção 2: Comando Manual

1. **Instale o PyInstaller**:
```bash
pip install pyinstaller
```

2. **Crie o executável**:
```bash
# Windows
pyinstaller --onefile --windowed --name "Pdf-Organizer" app.py

# Linux/Mac
pyinstaller --onefile --name "Pdf-Organizer" app.py
```

3. **O executável será criado** na pasta `dist/`

### Configurações PyInstaller

O projeto inclui arquivos de configuração:
- `main.spec` - Configuração principal com ícone
- `OrganizePDF.spec` - Configuração alternativa com ícone

Para usar uma configuração específica:
```bash
pyinstaller main.spec
```

### Ícone do Aplicativo

O projeto inclui um ícone personalizado:
- **`icone.ico`** - Ícone do aplicativo (Windows)
- **`trash-can.png`** - Ícone alternativo

O ícone será aplicado automaticamente ao executável quando disponível.

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 🖥️ Console Limpo e Profissional

### Características do Console
O aplicativo foi configurado para mostrar um console limpo e profissional, sem logs técnicos desnecessários que possam confundir o usuário final.

**O que o console mostra:**
```
============================================================
PDF ORGANIZER - SERVIDOR
============================================================
Este console é apenas o servidor do Pdf-Organizer.
Abra o seguinte site para interagir com o sistema:

    http://localhost:5000

Caso feche este console, você deverá abrir o aplicativo novamente.
============================================================
 * Debug mode: off
```

**O que foi suprimido:**
- Logs de requisições HTTP (Werkzeug)
- Mensagens de debug técnicas
- Logs de processamento de PDFs
- Mensagens de erro detalhadas

### Para Desenvolvedores - Habilitando Logs
Se precisar debugar problemas de rede ou ver logs técnicos, edite o arquivo `app.py` e comente a linha:

```python
# ATENÇÃO: Este código suprime os logs do Werkzeug para manter o console limpo
# Se precisar debugar problemas de rede, comente esta linha
logging.getLogger("werkzeug").setLevel(logging.ERROR)
```

**Para habilitar logs completos:**
```python
# logging.getLogger("werkzeug").setLevel(logging.ERROR)
```

## 🔧 Troubleshooting

### Problemas Comuns com o Executável

#### O executável não abre
- **Windows**: Verifique se o antivírus não está bloqueando
- **Linux**: Execute `chmod +x Pdf-Organizer` para dar permissão
- **macOS**: Clique com botão direito → "Abrir" para contornar Gatekeeper

#### Erro de porta em uso
- Feche outras instâncias do aplicativo
- Reinicie o computador se necessário
- Use `netstat -ano | findstr :5000` (Windows) para verificar

#### Navegador não abre automaticamente
- Acesse manualmente: `http://localhost:5000`
- Verifique se o firewall não está bloqueando

#### Problemas com PDFs
- Verifique se os PDFs não estão corrompidos
- Certifique-se de que os PDFs contêm texto (não são apenas imagens)
- Use PDFs com CNPJs válidos

### Suporte

Para problemas não listados acima:
1. Verifique as [Issues](https://github.com/seu-usuario/Pdf-Organizer/issues)
2. Abra uma nova issue com detalhes do problema
3. Inclua logs de erro se disponíveis

## 📄 Licença

Este projeto está sob a licença MIT.
