# Organizador de PDFs

Sistema inteligente para organização automática de PDFs baseado em CNPJs e estruturas personalizadas.

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

- Python 3.8+
- Dependências listadas em `requirements.txt`

## 🛠️ Instalação

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

## 🧪 Teste Rápido

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
└── teste_organizacao.py  # Script de teste
```

## 🎯 Características Técnicas

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

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
