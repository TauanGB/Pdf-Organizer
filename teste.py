import customtkinter as ctk
from tkinter import messagebox
from tkinter import Listbox
import json
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GerenciadorCategorias(ctk.CTkFrame):
	def __init__(self, parent):
		super().__init__(parent)
		
		# Componentes principais
		self.titulo = ctk.CTkLabel(self, text="Gerenciar Categorias e Subcategorias")  # Título
		self.label_categoria = ctk.CTkLabel(self, text="Categoria (Pasta):")  # LABEL CATEGORIA
		self.entrada_categoria = ctk.CTkEntry(self, width=200)  # ENTRY CATEGORIA
		self.label_subcategoria = ctk.CTkLabel(self, text="Subcategoria (PDF):")  # LABEL SUBCATEGORIA
		self.entrada_subcategoria = ctk.CTkEntry(self, width=200)  # ENTRY SUBCATEGORIA
		self.btn_add_categoria = ctk.CTkButton(self, text="+", command=self.adicionar_categoria, width=40)  # BT ADICIONAR CATEGORIA
		self.btn_add_subcategoria = ctk.CTkButton(self, text="+", command=self.adicionar_subcategoria, width=40)  # BT ADICIONAR SUBCATEGORIA
		self.btn_remover_categoria = ctk.CTkButton(self, text="-", command=self.remover_categoria, width=40)  # BT REMOVER CATEGORIA
		self.btn_remover_subcategoria = ctk.CTkButton(self, text="-", command=self.remover_subcategoria, width=40)  # BT REMOVER SUBCATEGORIA
		self.lista_categorias = Listbox(self, width=35, height=10, fg="black")  # LISTA DE CATEGORIAS
		self.lista_categorias.bind("<<ListboxSelect>>", self.mostrar_detalhes)  # Binding para exibir detalhes
		

		# Layout
		self.titulo.grid(row=0, column=1, columnspan=5, pady=10)  # TÍTULO
		self.label_categoria.grid(row=1, column=1, padx=10, pady=5, sticky="w")  # LABEL CATEGORIA
		self.entrada_categoria.grid(row=1, column=2, padx=10, pady=5)  # ENTRY CATEGORIA
		self.label_subcategoria.grid(row=2, column=1, padx=10, pady=5, sticky="w")  # LABEL SUBCATEGORIA
		self.entrada_subcategoria.grid(row=2, column=2, padx=10, pady=5)  # ENTRY SUBCATEGORIA
		self.btn_add_categoria.grid(row=1, column=5, padx=10, pady=10)  # BT ADICIONAR CATEGORIA
		self.btn_add_subcategoria.grid(row=2, column=5, padx=10, pady=10)  # BT ADICIONAR SUBCATEGORIA
		self.btn_remover_categoria.grid(row=1, column=6, padx=10, pady=10)  # BT REMOVER CATEGORIA
		self.btn_remover_subcategoria.grid(row=2, column=6, padx=10, pady=10)  # BT REMOVER SUBCATEGORIA
		self.lista_categorias.grid(row=3, column=1, columnspan=2, pady=10, sticky="nsew")  # LISTA CATEGORIAS

		# Frame adicional à direita
		self.frame_detalhes = FrameDetalhes(self)
		self.frame_detalhes.grid(row=0, rowspan=4, column=0, padx=20, pady=10, sticky="nsew")
		
		# Dicionário para armazenar as categorias e subcategorias
		self.categorias = {}
		self.carregar_dados()

	def carregar_dados(self):
		"""Carrega as categorias e subcategorias de um arquivo JSON, se existir."""
		if os.path.exists('estrutura.json'):
			with open('estrutura.json', 'r') as file:
				self.categorias = json.load(file)
			self.atualizar_lista()

	def salvar_dados(self):
		"""Salva as categorias e subcategorias em um arquivo JSON."""
		with open('estrutura.json', 'w') as file:
			json.dump(self.categorias, file, indent=4)

	def adicionar_categoria(self):
		nome_categoria = self.entrada_categoria.get()
		if nome_categoria:
			if nome_categoria not in self.categorias:
				self.categorias[nome_categoria] = {}  # Cada categoria contém um dicionário
				self.atualizar_lista()
				self.salvar_dados()
			else:
				messagebox.showwarning("Aviso", "Essa categoria já existe.")
		else:
			messagebox.showerror("Erro", "O nome da categoria não pode estar vazio.")

	def adicionar_subcategoria(self):
		nome_categoria = self.entrada_categoria.get()
		nome_subcategoria = self.entrada_subcategoria.get()
		if nome_categoria and nome_subcategoria:
			if nome_categoria in self.categorias:
				if nome_subcategoria not in self.categorias[nome_categoria]:
					self.categorias[nome_categoria][nome_subcategoria] = []
				self.atualizar_lista()
				self.salvar_dados()
				self.entrada_subcategoria.delete(0, "end")
			else:
				messagebox.showerror("Erro", "A categoria especificada não existe.")
		else:
			messagebox.showerror("Erro", "Os campos de categoria e subcategoria não podem estar vazios.")

	def remover_categoria(self):
		nome_categoria = self.entrada_categoria.get()
		if nome_categoria in self.categorias:
			del self.categorias[nome_categoria]
			self.atualizar_lista()
			self.salvar_dados()
			self.entrada_categoria.delete(0, "end")
			self.entrada_subcategoria.delete(0, "end")
		else:
			messagebox.showwarning("Aviso", "Categoria não encontrada.")

	def remover_subcategoria(self):
		nome_categoria = self.entrada_categoria.get()
		nome_subcategoria = self.entrada_subcategoria.get()
		if nome_categoria in self.categorias:
			if nome_subcategoria in self.categorias[nome_categoria]:
				del self.categorias[nome_categoria][nome_subcategoria]
				self.atualizar_lista()
				self.salvar_dados()
				self.entrada_subcategoria.delete(0, "end")
			else:
				messagebox.showwarning("Aviso", "Subcategoria não encontrada.")
		else:
			messagebox.showerror("Erro", "A categoria especificada não existe.")


	def atualizar_lista(self):
		"""Atualiza a exibição de categorias e subcategorias na listbox."""
		self.lista_categorias.delete(0, "end")
		for categoria, subcategorias in self.categorias.items():
			self.lista_categorias.insert("end", f"Categoria -- {categoria}")
			for sub, palavras_chave in subcategorias.items():
				self.lista_categorias.insert("end", f"  - {sub} ({len(palavras_chave)} palavras-chave)")

	def mostrar_detalhes(self, event):
		#FIXME arrumar, limpar antes de colocar outro
		"""Exibe detalhes da subcategoria selecionada no FrameDetalhes."""
		selection = self.lista_categorias.curselection()
		if selection:
			texto_selecionado = self.lista_categorias.get(selection[0])
			if "Categoria -- " in texto_selecionado:
				categoria = texto_selecionado.split(" -- ")[1]
				self.frame_detalhes.mostrar_detalhes(categoria, None, self.categorias)
			elif " - " in texto_selecionado:
				categoria = self.lista_categorias.get(selection[0] - 1).split(" -- ")[1]
				subcategoria = texto_selecionado.split(" - ")[1].split(" ")[0]
				self.frame_detalhes.mostrar_detalhes(categoria, subcategoria, self.categorias)

class FrameDetalhes(ctk.CTkFrame):
	#FIXME não ta adicionando palavra chave nem removendo
	def __init__(self, parent):
		super().__init__(parent)
		self.label_detalhes = ctk.CTkLabel(self, text="Detalhes da Subcategoria")
		self.lista_palavras_chave = Listbox(self)
		self.label_Palavra = ctk.CTkLabel(self, text='Palavra-chave',fg_color='transparent')
		self.entrada_palavra_chave = ctk.CTkEntry(self, width=180)
		self.btn_add_palavra = ctk.CTkButton(self, text="Adicionar", command=self.adicionar_palavra_chave,width=70)
		self.btn_remover_palavra = ctk.CTkButton(self, text="Remover", command=self.remover_palavra_chave,width=70)

		
		self.label_detalhes.grid(row=0,column=0,columnspan=2,padx=10, pady=2)
		self.lista_palavras_chave.grid(row=1,column=0,columnspan=2,padx=5,sticky='nswe')
		self.label_Palavra.grid(row=2,column=0,columnspan=2)
		self.entrada_palavra_chave.grid(row=3,column=0,columnspan=2,pady=5,padx=4)
		self.btn_add_palavra.grid(row=4,column=0,pady=2)
		self.btn_remover_palavra.grid(row=4,column=1,pady=2)

	def mostrar_detalhes(self, categoria, subcategoria, categorias_dict):
		self.categoria = categoria
		self.subcategoria = subcategoria
		self.categorias_dict = categorias_dict

		# Limpa a lista de palavras-chave antes de exibir novas
		self.lista_palavras_chave.delete(0, "end")
		if subcategoria:
			palavras_chave = categorias_dict[categoria][subcategoria]
			for palavra in palavras_chave:
				self.lista_palavras_chave.insert("end", palavra)

	def adicionar_palavra_chave(self):
		palavra_chave = self.entrada_palavra_chave.get()
		if palavra_chave and self.subcategoria:
			if palavra_chave not in self.categorias_dict[self.categoria][self.subcategoria]:
				self.categorias_dict[self.categoria][self.subcategoria].append(palavra_chave)
				self.lista_palavras_chave.insert("end", palavra_chave)
				self.master.salvar_dados()
				self.entrada_palavra_chave.delete(0, "end")
			else:
				messagebox.showwarning("Aviso", "Essa palavra-chave já existe.")

	def remover_palavra_chave(self):
		selecionado = self.lista_palavras_chave.curselection()
		if selecionado and self.subcategoria:
			palavra = self.lista_palavras_chave.get(selecionado)
			self.categorias_dict[self.categoria][self.subcategoria].remove(palavra)
			self.lista_palavras_chave.delete(selecionado)
			self.master.salvar_dados()
			

# Inicialização da janela principal
app = ctk.CTk()
app.title("Gerenciador de Categorias e Subcategorias")

# Frame da interface
frame = GerenciadorCategorias(app)
frame.pack(padx=20, pady=20)

app.mainloop()
