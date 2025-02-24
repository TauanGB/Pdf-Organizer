import customtkinter 
from customtkinter import CTkImage
from PIL import Image
from tkinter import END, Listbox,Menu
from tkinter.filedialog import askdirectory
from tkinter import messagebox
import PyPDF2
import os
import json
from time import strftime

class Client_Label:
	def __init__(self ,master,frame , Nome, CadPessoa):
		self.master = master
		self.Nome = Nome
		self.CadPessoa = CadPessoa
		self.FramePai = frame
		self._Fundo = customtkinter.CTkFrame(frame,fg_color='gray')
		self._Lixeira = customtkinter.CTkButton(self._Fundo,text='X',width=25,command=self.Deletar)
		self._Editar = customtkinter.CTkButton(self._Fundo,text='Editar',width=50,command=self.Editar)
		self._Label = customtkinter.CTkLabel(self._Fundo, text=f'{CadPessoa} - {Nome}',wraplength=350, fg_color='transparent')

		self._Fundo.pack(side='top',fill='x',pady=(2,2),padx=(5,5))
		self._Lixeira.pack(side="left",pady=(4,4),padx=(5,1))
		self._Editar.pack(side="left",pady=(4,4),padx=(1,5))
		self._Label.pack(side="left",fill="x")
	
	def Deletar(self):
		#Apagando da lista do frameword
		self._Fundo.pack_forget()
		#Apagando da lista de clientes do banco temporario
		self.master.Clientes.pop(self.CadPessoa)

		#Salvando em banco permanente
		self.master.SalvarEmBancoClientes()

	def Editar(self):
		self.master.Bt_voltar_Cadastro.configure(state='disabled')
		self.master.Bt_AddAlterar.configure(text="Alterar",fg_color='red')

		self.master.EntryRSaCadastro.delete(0,"end")
		self.master.EntryRSaCadastro.insert(0,self.Nome)
		self.master.EntryCNPJCadastro.delete(0,"end")
		self.master.EntryCNPJCadastro.insert(0,self.CadPessoa)
		self.Deletar()

class GerenciadorCategorias(customtkinter.CTkFrame):
	def __init__(self, parent, voltarMenu_callback):
		super().__init__(parent)
		
		self.voltar_menu = voltarMenu_callback
		self.create_widgets()

	def create_widgets(self):
		# Componentes principais
		self.titulo = customtkinter.CTkLabel(self, text="ESTRUTURA DE PASTAS\nselecione para apagar")  # Título
		self.lista_Estrutura = Listbox(self, width=40, fg="black")  # LISTA DE CATEGORIAS
		self.lista_Estrutura.bind("<<ListboxSelect>>", self.mostrar_detalhes)  # Binding para exibir detalhes
	
		self.btn_voltar = customtkinter.CTkButton(self, text="Voltar", command=self.retornar_menu)#BT PRA SALVAR AND VOLTAR
		
		self.Diretorio_Principal = ''#STRING COPM NOME DO DIRETORIO INICIAL 
		self.alterar_diretorio = customtkinter.CTkButton(self, text="Alterar Diretorio Matriz", command=self.Select_Diretorio)
		
		self.remove_icone = CTkImage(light_image=Image.open("trash-can.png"))
		self.remover = customtkinter.CTkButton(self,text='',image=self.remove_icone,width=15,fg_color="white", state="disabled",command=self.remover_item)
		self.adicionar_pasta = customtkinter.CTkButton(self, text="Add Pasta", command=self.PastaTop)
		self.adicionar_pdf = customtkinter.CTkButton(self, text="Add Pdf", command=self.PastaPdf)

		self.rowconfigure(1,weight=1)

		# Layout
		self.titulo.grid(row=0, column= 0, pady=5,padx=5,sticky="ns")  # TÍTULO
		self.lista_Estrutura.grid(row=1,rowspan=3, column= 0,padx=5,pady=5, sticky="ns")  # LISTA CATEGORIA
		# Frame adicional à direita
		self.frame_detalhes = self.FrameDetalhes(self)
		self.frame_detalhes.grid(row=0,rowspan=2, column=2,columnspan=4, padx=20, pady=10, sticky="nsew")

		self.remover.grid(row=2, column= 1, padx=5, pady=5)
		self.alterar_diretorio.grid(row=2, column= 2, padx=5, pady=5, sticky="nsew")
		self.adicionar_pasta.grid(row=2, column= 3, padx=5, pady=5, sticky="nsew")
		self.adicionar_pdf.grid(row=3, column= 2, padx=5, pady=5, sticky="nsew")
		self.btn_voltar.grid(row=3, column=3,padx=5,pady=5)
		
		# Dicionário para armazenar as categorias e subcategorias
		self.categorias = {}
		self.carregar_dados()
		self.TopLevel_pasta = None
		self.TopLevel_pdf = None

	def PastaTop(self):
		if self.TopLevel_pasta is None or not self.TopLevel_pasta.winfo_exists():
			self.TopLevel_pasta = self.TopLevel_Pasta(self)

		self.TopLevel_pasta.focus()
		self.master.iconify()
	
	def PastaPdf(self):
		if self.TopLevel_pdf is None or not self.TopLevel_pdf.winfo_exists():
			self.TopLevel_pdf = self.TopLevel_Pdf(self)

		self.TopLevel_pdf.focus()
		self.master.iconify()

	def Select_Diretorio(self):
		self.Diretorio_Principal = askdirectory()
		self.salvar_dados()
		self.atualizar_lista()

	def retornar_menu(self):
		self.salvar_dados()
		self.voltar_menu()

	def carregar_dados(self):
		if os.path.exists('estrutura.json'):
			with open('estrutura.json', 'r') as file:
				self.categorias,self.Diretorio_Principal = json.load(file)
			self.atualizar_lista()

	def salvar_dados(self):
		"""Salva as categorias e subcategorias em um arquivo JSON."""
		with open('estrutura.json', 'w') as file:
			json.dump([self.categorias,self.Diretorio_Principal], file, indent=4)

	#OBSOLETOS-----------------------------------------------------------------------
	def adicionar_categoria(self,nome_categoria, nome_categoriaPai = None):
		self.master.focus()
		if nome_categoria != "":
			if nome_categoriaPai == 'EMPRESA':
				if nome_categoria not in self.categorias:
					self.categorias[nome_categoria] = {}  # Cada categoria contém um dicionário
					self.atualizar_lista()
					self.salvar_dados()
					self.carregar_dados()
				else:
					messagebox.showwarning("Aviso", "Essa categoria já existe.")
			else:
				if nome_categoria not in self.categorias[nome_categoriaPai].keys():
					self.categorias[nome_categoriaPai][nome_categoria] = {}# Cada categoria contém um dicionário
					self.atualizar_lista()
					self.salvar_dados()
					self.carregar_dados()
				else:
					messagebox.showwarning("Aviso", "Essa subcategoria já existe.")
		else:
			messagebox.showerror("Erro", "O nome da categoria não pode estar vazio.")

	def adicionar_subcategoria(self,pastaPai,nome_pdf,palavraChave1,palavraChave2,palavraChave3):
		if pastaPai and nome_pdf:
			if pastaPai == "EMPRESA":
				if nome_pdf not in self.categorias.keys():
					self.categorias[nome_pdf] = [palavraChave1,palavraChave2,palavraChave3]
					self.atualizar_lista()
					self.salvar_dados()
					self.carregar_dados()
				else:
					messagebox.showerror("Erro", "Esse Tipo de Pdf Ja existe.")
			elif pastaPai in self.categorias.keys():
				#verifica se existe a pasta pai referente
				if nome_pdf not in self.categorias[pastaPai].keys():
					#verifica se o tipo de pdf n ja existe
					self.categorias[pastaPai][nome_pdf] = [palavraChave1,palavraChave2,palavraChave3]
					self.atualizar_lista()
					self.salvar_dados()
					self.carregar_dados()
				else:
					messagebox.showerror("Erro", "Esse Tipo de Pdf Ja existe.")
			elif pastaPai not in self.categorias:#verifica se existe como subpasta
				pastaAcima,pastaPai = [i.strip() for i in pastaPai.split(" - ")]
				if nome_pdf not in self.categorias[pastaAcima].keys():
					self.categorias[pastaAcima][pastaPai][nome_pdf] = [palavraChave1,palavraChave2,palavraChave3]
					self.atualizar_lista()
					self.salvar_dados()
					self.carregar_dados()
				else:
					messagebox.showerror("Erro", "Esse Tipo de Pdf Ja existe.")

			else:
				messagebox.showerror("Erro", "Chama Tauan.")
		else:
			messagebox.showerror("Erro", "Os campos de Pasta e Pdf não podem estar vazios.")

	def remover_item(self):
		selection = self.lista_Estrutura.curselection()
		item = self.lista_Estrutura.get(selection[0]).split('-')[-1]
		if item in self.categorias.keys():
			self.frame_detalhes.desabilitarLista()
			del self.categorias[item]
			self.atualizar_lista()
			self.salvar_dados()
		else:
			for pasta in self.categorias.keys():
				if type(self.categorias[pasta]) == list:
					continue
				elif item in self.categorias[pasta].keys():
					self.frame_detalhes.desabilitarLista()
					del self.categorias[pasta][item]
					self.atualizar_lista()
					self.salvar_dados()
					return
				
				else:
					for subpasta in self.categorias[pasta].keys():
						if type(self.categorias[pasta][subpasta]) == list:
							continue
						elif type(self.categorias[pasta][subpasta]) == dict:
							if item in self.categorias[pasta][subpasta].keys():
								self.frame_detalhes.desabilitarLista()
								del self.categorias[pasta][subpasta][item]
								self.atualizar_lista()
								self.salvar_dados()
								return
								
							else:
								continue
					
	# FIM DOS OBSOLETOS-----------------------------------------------------------------------

	def atualizar_lista(self):
		"""Atualiza a exibição de categorias e subcategorias na listbox."""
		self.lista_Estrutura.delete(0, "end")
		self.lista_Estrutura.insert("end", f"Diretorio Matriz : {(self.Diretorio_Principal).split("/")[-1]}")
		self.lista_Estrutura.insert("end", f"EMPRESA")
		for categoria, subcategorias in self.categorias.items():
			if type(subcategorias) == dict:
				self.lista_Estrutura.insert("end", f" |--PASTA--{categoria}")
				for sub, sub_item in subcategorias.items():
					if type(sub_item) == list:
						self.lista_Estrutura.insert("end", f" |    |--PDF--{sub}")
					elif type(sub_item) == dict:
						self.lista_Estrutura.insert("end", f" |    |--SUBPASTA--{sub}")
						for subniv_pdf, subnivel_item in sub_item.items():
							if type(subnivel_item) == list:
								self.lista_Estrutura.insert("end", f" |    |    |--PDF--{subniv_pdf}")
							else:
								messagebox.showerror("Rapaz","Chama Tauan que tem algo errado ai")
			elif type(subcategorias) == list:
				self.lista_Estrutura.insert("end", f" |--PDF--{categoria}")
			
			else:
				messagebox.showerror("Rapaz","Chama Tauan que tem algo errado ai")
						
	def mostrar_detalhes(self, event):
		"""Exibe detalhes da subcategoria selecionada no FrameDetalhes."""
		selection = self.lista_Estrutura.curselection()
		if selection:
			texto_selecionado = self.lista_Estrutura.get(selection[0])
			##RECONHECER CATEGORIA PARA TER DIRETORIO DO PDF EM QUESTAO E EXIBIR
			if "PDF" in texto_selecionado:
				self.remover.configure(fg_color='red',state='normal')
				pdf = texto_selecionado.split("--")[-1]
				if pdf in self.categorias.keys():
					#VERIFICANDO SE N ESTA EM PASTA ALGUMA
					categoria = None
				else:
					for pasta in self.categorias.keys():
						if type(self.categorias[pasta]) == list:
							continue
						elif pdf in self.categorias[pasta].keys():
							categoria = pasta
							break
						for subpasta in self.categorias[pasta]:
							if type(self.categorias[pasta][subpasta]) == dict:
								if pdf in self.categorias[pasta][subpasta].keys():
									categoria = [pasta,subpasta]
								break
				self.frame_detalhes.habilitarLista()
				self.frame_detalhes.mostrar_detalhes(categoria, pdf, self.categorias)
			elif "PASTA" in texto_selecionado or "SUBPASTA" in texto_selecionado:
				self.frame_detalhes.desabilitarLista()
				self.remover.configure(fg_color='red',state='normal')
			else:
				self.frame_detalhes.desabilitarLista()
				self.remover.configure(fg_color='white',state='disabled')

	class FrameDetalhes(customtkinter.CTkFrame):
		def __init__(self, parent):
			super().__init__(parent)

			self.create_widgets()

		def create_widgets(self):
			self.label_detalhes = customtkinter.CTkLabel(self, text="Palavras-chave Para reconhecimento de pdf")
			self.lista_palavras_chave = Listbox(self)
			self.label_Palavra = customtkinter.CTkLabel(self, text='Palavra-chave',fg_color='transparent')
			self.entrada_palavra_chave = customtkinter.CTkEntry(self, width=180)
			self.btn_add_palavra = customtkinter.CTkButton(self, text="Adicionar", command=self.adicionar_palavra_chave,width=70)
			self.btn_remover_palavra = customtkinter.CTkButton(self, text="Remover", command=self.
			remover_palavra_chave,width=70)
			
			self.lista_palavras_chave.bind("<<ListboxSelect>>", self.editar_palavra)
			
			self.label_detalhes.grid(row=0,column=0,columnspan=2,padx=10, pady=2)
			self.lista_palavras_chave.grid(row=1,column=0,columnspan=2,padx=5,sticky='nswe')
			self.label_Palavra.grid(row=2,column=0,columnspan=2)
			self.entrada_palavra_chave.grid(row=3,column=0,columnspan=2,pady=5,padx=4)
			self.btn_add_palavra.grid(row=4,column=0,pady=2)
			self.btn_remover_palavra.grid(row=4,column=1,pady=2)

		def desabilitarLista(self):
			self.lista_palavras_chave.configure(state="disabled",background='#B5B5B5')
		
		def habilitarLista(self):
			self.lista_palavras_chave.configure(state="normal",background='#FFFFFF')

		def mostrar_detalhes(self, pasta, pdf, categorias_dict):
			self.Pasta = pasta
			self.Pdf = pdf
			self.categorias_dict = categorias_dict

			# Limpa a lista de palavras-chave antes de exibir novas
			self.lista_palavras_chave.delete(0, "end")
			if self.Pasta == None:
				palavras_chave = categorias_dict[pdf]
				for palavra in palavras_chave:
					self.lista_palavras_chave.insert("end", palavra)

			elif type(self.Pasta) == str:
				palavras_chave = categorias_dict[pasta][pdf]
				for palavra in palavras_chave:
					self.lista_palavras_chave.insert("end", palavra)
			elif type(self.Pasta) == list:
				palavras_chave = categorias_dict[pasta[0]][pasta[1]][pdf]
				for palavra in palavras_chave:
					self.lista_palavras_chave.insert("end", palavra)

		def editar_palavra(self,event):
			selecao_cursor = self.lista_palavras_chave.curselection()

			if len(selecao_cursor) >0:
				self.entrada_palavra_chave.delete(0, "end")

				self.entrada_palavra_chave.insert("end",self.lista_palavras_chave.get(selecao_cursor[0]))

		def adicionar_palavra_chave(self):
			palavra_chave = self.entrada_palavra_chave.get().upper()
			if palavra_chave and self.Pdf:
				if palavra_chave not in self.categorias_dict[self.Pasta][self.Pdf]:
					self.categorias_dict[self.Pasta][self.Pdf].append(palavra_chave)
					
					self.lista_palavras_chave.insert("end", palavra_chave)
					self.master.salvar_dados()
					self.entrada_palavra_chave.delete(0, "end")
				else:
					messagebox.showwarning("Aviso", "Essa palavra-chave já existe.")
				self.master.atualizar_lista()

		def remover_palavra_chave(self):
			selecionado = self.lista_palavras_chave.curselection()
			if selecionado and self.Pdf:
				palavra = self.lista_palavras_chave.get(selecionado)
				self.categorias_dict[self.Pasta][self.Pdf].remove(palavra)
				self.lista_palavras_chave.delete(selecionado)
				self.master.salvar_dados()
				self.master.atualizar_lista()

	class TopLevel_Pasta(customtkinter.CTkToplevel):
		def __init__(self, master):
			super().__init__(master)
			self.Pasta_create_widgets()

		def Pasta_create_widgets(self) :
			self.label_TituloCategoria = customtkinter.CTkLabel(self, text='Nome Da Pasta')
			self.entry_TituloCategoria = customtkinter.CTkEntry(self,placeholder_text='Titulo')
			self.label_Aviso = customtkinter.CTkLabel(self, text=' Caso a pasta seja uma subpasta, selecione a \n pasta pai abaixo', anchor="e",justify="left")
			self.optionmenu_Value = customtkinter.StringVar(value='EMPRESA')
			self.optionmenu_PastaPai = customtkinter.CTkOptionMenu(self,values=list([x for x in self.master.categorias.keys() if type(self.master.categorias[x]) == dict]),variable=self.
			optionmenu_Value)
			self.label_PastaPai = customtkinter.CTkLabel(self, text='Pasta Pai')
			self.Button_confirm =  customtkinter.CTkButton(self,text='Adicionar',command=self.Pasta_Adicionar)

			self.label_TituloCategoria.grid(row=0,column=0,sticky='w',padx=(5,2),pady=2)
			self.entry_TituloCategoria.grid(row=0,column=1,padx=2,pady=2)
			self.label_PastaPai.grid(row=2,column=0,sticky='w',padx=(5,2),pady=2)
			self.optionmenu_PastaPai.grid(row=2,column=1,padx=2,pady=2)
			self.label_Aviso.grid(row=1,column=0,columnspan=2,padx=2,sticky="NSEW",pady=2)
			self.Button_confirm.grid(row=3,column=1,padx=2,pady=5)

		def Pasta_Adicionar(self):
			self.master.adicionar_categoria(self.entry_TituloCategoria.get(),self.optionmenu_Value.get())
			self.destroy()
			pass
			#apenas adicionar pasta -old categoria- logo uma entry e um botao de voltar e outro de adicionar
	
	class TopLevel_Pdf(customtkinter.CTkToplevel):
		def __init__(self, master):
			super().__init__(master)
			self.Pasta_create_widgets()

		def Pasta_create_widgets(self) :
			self.label_TituloCategoria = customtkinter.CTkLabel(self, text='Tipo do pdf')
			self.entry_TituloCategoria = customtkinter.CTkEntry(self,placeholder_text='Tipo')
			self.label_Aviso = customtkinter.CTkLabel(self, text='Necessita no minimo 3 palavra chave e selecione a pasta em que ficara o pdf',anchor="e")
			self.label_PalavraChave = customtkinter.CTkLabel(self, text='Palavras chaves',anchor="e")
			self.entry_PalavraChave_1 = customtkinter.CTkEntry(self,placeholder_text='Palavra Chave 1')
			self.entry_PalavraChave_2 = customtkinter.CTkEntry(self,placeholder_text='Palavra Chave 2')
			self.entry_PalavraChave_3 = customtkinter.CTkEntry(self,placeholder_text='Palavra Chave 3')

			##for para pegar todas as pastas
			Subclasses = []
			for chave in self.master.categorias.keys():
				Subclasses += [f"{chave} - {item}" for item in self.master.categorias[chave] if type(self.master.categorias[chave][item]) == dict]

			self.optionmenu_Value = customtkinter.StringVar(value="EMPRESA")
			self.optionmenu_PastaPai = customtkinter.CTkOptionMenu(self,values=list(self.master.categorias.keys())+ Subclasses,variable=self.
			optionmenu_Value)
			self.label_PastaPai = customtkinter.CTkLabel(self, text='Pasta Pai')
			self.Button_confirm =  customtkinter.CTkButton(self,text='Adicionar',command=self.Pasta_Adicionar)

			self.label_TituloCategoria.grid(row=0,column=0,sticky='w',padx=(5,2),pady=2)
			self.entry_TituloCategoria.grid(row=0,column=1,padx=2,pady=2)
			self.label_PastaPai.grid(row=0,column=2,sticky='w',padx=2,pady=2)	 
			self.optionmenu_PastaPai.grid(row=0,column=3,padx=2,pady=2)
			self.label_Aviso.grid(row=1,column=0,columnspan=3,padx=(5,2),sticky="NSEW",pady=2)
			self.label_PalavraChave.grid(row=2,column=0,padx=(5,2),pady=2,sticky='w')
			self.entry_PalavraChave_1.grid(row=2,column=1,padx=2,pady=2)
			self.entry_PalavraChave_2.grid(row=2,column=2,padx=2,pady=2)
			self.entry_PalavraChave_3.grid(row=2,column=3,padx=2,pady=2)
			self.Button_confirm.grid(row=3,column=3,padx=2,pady=5)

		def Pasta_Adicionar(self):
			if self.entry_PalavraChave_1.get() != '' and self.entry_PalavraChave_2.get() != '' and self.entry_PalavraChave_3.get() != '':
				self.master.adicionar_subcategoria(self.optionmenu_Value.get(),self.entry_TituloCategoria.get(),self.entry_PalavraChave_1.get(),self.entry_PalavraChave_2.get(),self.entry_PalavraChave_3.get())
				self.destroy()
			else:
				messagebox.showerror('Alerta','Coloque as tres palavras chaves')
			
			#apenas adicionar pasta -old categoria- logo uma entry e um botao de voltar e outro de adicionar

class MenuPrincipal(customtkinter.CTkFrame):
	def __init__(self, master, abrir_cadastro_callback, abrir_historico_callback, abrir_estruturacao_callback):
		super().__init__(master)
		self.abrir_cadastro_callback = abrir_cadastro_callback
		self.abrir_historico_callback = abrir_historico_callback
		self.abrir_Estruturacao_callback = abrir_estruturacao_callback
		self.dados_tmp = {}
		self.Historico = {}

		if os.path.isfile('Historico.json'):
			with open('Historico.json', 'r', encoding='utf-8') as arq:
				self.Historico = json.load(arq)
				arq.close()
		else:
			self.Historico = {f"{strftime("%m/%Y")}": ["Exemplo Historico"]}
			with open('Historico.json', 'w', encoding='utf-8') as arq:
				json.dump(self.Historico, arq)
		

		self.create_widgets()

	

	def create_widgets(self):

		self.leftFrameMenu = customtkinter.CTkFrame(self, corner_radius=0)
		self.rightFrameMenu = customtkinter.CTkFrame(self)
		
		self.leftFrameMenu.grid(row=0, sticky="N")
		self.rightFrameMenu.grid(row=0, column=1)
		
		# Botões do menu
		self.Bt_cadastro = customtkinter.CTkButton(self.leftFrameMenu, text="Cadastro", command=self.abrir_cadastro_callback)
		self.Bt_historico = customtkinter.CTkButton(self.leftFrameMenu, text="Histórico", command=self.abrir_historico_callback)
		self.Bt_Estruturacao = customtkinter.CTkButton(self.leftFrameMenu, text="Estruturação", command=self.abrir_Estruturacao_callback,fg_color="#3AABA3")
		self.Bt_organizar = customtkinter.CTkButton(self.leftFrameMenu, text="Organizar", command=self.organizar,fg_color="green")
		self.Bt_desfazer = customtkinter.CTkButton(self.leftFrameMenu, text="Desfazer", command=self.desfazer,fg_color="#FF0A00",state="disabled")
		
		self.Bt_cadastro.grid(row=0, padx=10, pady=10)
		self.Bt_historico.grid(row=1, padx=10, pady=10)
		self.Bt_Estruturacao.grid(row=2, padx=10, pady=10)
		self.Bt_organizar.grid(row=3, padx=10, pady=10)
		self.Bt_desfazer.grid(row=4, padx=10, pady=10)

		self.Bt_desfazer.grid_remove()

		# Listbox e barra de progresso
		self.progressbar = customtkinter.CTkProgressBar(self.rightFrameMenu, progress_color="#0ACF00", orientation='horizontal',mode="determinate")
		self.progressbar.set(0.0)
		self.listbox = Listbox(self.rightFrameMenu, width=150, height=15)
		
		
		self.progressbar.pack(padx=10, pady=10,fill='x', expand=1)
		self.listbox.pack(padx=10, pady=10)

	def desfazer(self):
		self.progressbar.set(0)
		for arq,dados in self.dados_tmp.items():
			self.progressbar.set((1/len(self.dados_tmp.keys())+self.progressbar.get()))

			if os.path.exists(f"{dados[0]}"):
				os.rename(dados[1],f"{dados[0]}/{arq}")
			else:
				os.makedirs(dados[0])
				os.rename(dados[1],f"{dados[0]}/{arq}")
				
			self.listbox.insert(END,f"{arq} Retornado a para {dados[0]}/{arq}")
			if strftime("%m/%Y") in self.Historico.keys():
				self.Historico[strftime("%m/%Y")].append(f"Dia {strftime("%d")} {arq} Retornado para {dados[0]}/{arq}")
			else:
				self.Historico[strftime("%m/%Y")] = [f"Dia {strftime("%d")} {arq} Retornado para {dados[0]}/{arq}"]

			self.master.update()
			self.master.update_idletasks()
		self.Bt_desfazer.grid_remove()
		self.salvar_dados_historico()

	def salvar_dados_historico(self):
		with open('Historico.json', 'w', encoding='utf-8') as arq:
			json.dump(self.Historico, arq)
			arq.close()

	def listarPdfs(self):
		estrutura_tmp = {}
		for item_1 in self.estrutura.keys():
			if type(self.estrutura[item_1]) == list:
				estrutura_tmp[item_1] = self.estrutura[item_1]
			else:
				for item_2 in self.estrutura[item_1].keys():
					if type(self.estrutura[item_1][item_2]) == list:
						estrutura_tmp[item_2] = self.estrutura[item_1][item_2]
					else:
						for item_3 in self.estrutura[item_1][item_2].keys():
							if type(self.estrutura[item_1][item_2][item_3]) == list:
								estrutura_tmp[item_3] = self.estrutura[item_1][item_2][item_3]
		return estrutura_tmp
	
	def getDirPdf(self,dirTypeDoc):
		dirPdf = None
		if dirTypeDoc in self.estrutura.keys():
				dirPdf = None
		else:
			for pasta in self.estrutura.keys():
				if type(self.estrutura[pasta]) == list:
					continue
				elif dirTypeDoc in self.estrutura[pasta].keys():
					dirPdf = pasta
					break
				for subpasta in self.estrutura[pasta]:
					if type(self.estrutura[pasta][subpasta]) == dict:
						if dirTypeDoc in self.estrutura[pasta][subpasta].keys():
							dirPdf = f"{pasta}/{subpasta}"
						break
		return dirPdf

	def VerificarDuplicidade(self,caminho_destino,arq,diretorio,caminho_origem):
		#VERIFICA SE N JA EXISTE ALGUM ARQUIVO IGUAL
		if os.path.exists(f"{caminho_destino}/{arq}"):
			numero = 1
			novo_nome = f"{numero}-{arq}"
			
			# Gera um nome disponível sem renomear ainda
			while os.path.exists(f"{caminho_destino}/{arq}"):
				numero += 1
				novo_nome = f"{numero}-{arq}"

			novo_caminho = f"{diretorio}/{novo_nome}"
			os.rename(caminho_origem, novo_caminho)
			return [novo_nome,novo_caminho]
		
		return [arq,caminho_origem]

	def organizar(self):
		self.Diretorio = askdirectory()
		self.PdfProcessados = {}
		self.PdfNaoReconhecidos = {}

		if self.Diretorio != "":
			tmparquivos = [f for f in os.listdir(self.Diretorio) if os.path.isfile(os.path.join(self.Diretorio, f))]
			arquivos = [f for f in tmparquivos if ".pdf" in f]
			print(arquivos)
			if len(arquivos) != 0:
				# Loop para percorrer diretórios e subdiretórios
				if os.path.exists('estrutura.json'):
					with open('estrutura.json', 'r') as file:
						self.estrutura,self.Diretorio_Principal = json.load(file)	
				else:
					messagebox.showwarning("Alerta","Antes de prosseguir crie a estrutura")
					return
				if not os.path.exists(self.Diretorio_Principal):
					messagebox.showerror("Erro","Diretorio principal foi excluido")

				if os.path.isfile('Clientes.json'):
					with open('Clientes.json', 'r', encoding='utf-8') as arq:
						self.clientes = json.load(arq)
				else:
					messagebox.showwarning("Alerta","Antes de prosseguir cadastre os clientes")
					return
				#ETAPA 1-----------------------------------------
				for arq in arquivos:
					tmpDiretorio = self.Diretorio + "/" + arq
					print(f"Analisando PDF: {tmpDiretorio}")

					self.progressbar.set((0.5/len(arquivos)+self.progressbar.get()))
					self.master.update()
					self.master.update_idletasks()

					#ETAPA 2-----------------------------------------
					# Tentar abrir e ler o PDF
					try:
						with open(tmpDiretorio, "rb") as pdf_file:
							pdf_reader = PyPDF2.PdfReader(pdf_file)
							infoday = pdf_reader.metadata['/CreationDate'].split(":")[1]
							infoday,infoano = f'{infoday[4:6]}',f'{infoday[0:4]}'


							texto = pdf_reader.pages[0].extract_text()
							pdf_file.close()
					except Exception as e:
						self.PdfNaoReconhecidos[arq] = {"Cliente":"","Doc Type":""}
						print(f"Erro ao processar o arquivo {arq}: {e}")
						continue
							
								
						# Identificar o cliente baseado no nome e cadastro unico
					cliente_identificado = ''
					for cad_pessoa, nome in self.clientes.items():
						if cad_pessoa in texto or nome in texto:
							cliente_identificado = nome
							print(f"Cliente identificado: {nome}")
							break
						elif cad_pessoa[0:10] in texto:
							cliente_identificado = nome
							print(f"Cliente identificado: {nome}")
							break

					# CRIANDO UM SEGUNDO DICIONARIO PARA RODAR OS DADOS SOMENTE COM OS PDF'S
					self.new_estrutura = self.listarPdfs()


					for tipo, keywords in self.new_estrutura.items():
						if any(keyword.lower() in texto.lower() for keyword in keywords):
							tipo_documento_identificado = tipo
							print(f"Tipo de documento identificado: {tipo}")
							break
					
					
					# Exibir o resultado da análise
					if cliente_identificado != '' and tipo_documento_identificado != '':
						print(f"Arquivo '{arq}' pertence ao cliente '{cliente_identificado}' e é do tipo '{tipo_documento_identificado}'")
						self.PdfProcessados[arq] = {"Cliente":cliente_identificado,"Doc Type":tipo_documento_identificado}
					elif tipo_documento_identificado == '':
						print(f"Arquivo '{arq}' pertence ao cliente '{cliente_identificado}', mas tipo de documento não identificado.")
						self.PdfNaoReconhecidos[arq] = {"Cliente":cliente_identificado,"Doc Type":""}
					else:
						print(f"Cliente não identificado para o arquivo '{arq}'.")
						self.PdfNaoReconhecidos[arq] = {"Cliente":"","Doc Type":tipo_documento_identificado}
				#ETAPA 3-----------------------------------------
				print("\033[H\033[2J")
				for chave in self.PdfProcessados:
					print(chave)
					print(self.PdfProcessados[chave])
				
				#ETAPA 4-----------------------------------------
				## Leitura Feita arquivos marcados
				if len(self.PdfNaoReconhecidos.keys()) >= 1:
					TextoTmp = "Os Seguintes Arquivos não foram reconhecidos devido a não reconhecimento de: "
					for arq in self.PdfNaoReconhecidos.keys():
						if self.PdfNaoReconhecidos[arq]["Cliente"] == "" and self.PdfNaoReconhecidos[arq]["Doc Type"] == "":
							TextoTmp = TextoTmp + f"\n{arq} - Tipo do arquivo , Cliente"

						elif self.PdfNaoReconhecidos[arq]["Cliente"] == "":
							TextoTmp = TextoTmp + f"\n{arq} - Cliente"

						elif self.PdfNaoReconhecidos[arq]["Doc Type"] == "":
							TextoTmp = TextoTmp + f"\n{arq} - Tipo do arquivo"

						else:
							TextoTmp = TextoTmp + f"\n{arq} - Erro no sistema"

					TextoTmp = TextoTmp+"\n\n\nDeseja Continuar?"
					Resposta = messagebox.askquestion("Atenção",TextoTmp)
					print(Resposta)

					if Resposta == "no":
						return

				#ETAPA 5-----------------------------------------
				##self.progressbar.configure(max=len(arquivos/2))
				##INICIO DA 2º contagem
				for arq in self.PdfProcessados.keys():
					self.progressbar.set((0.5/len(self.PdfProcessados.keys())+self.progressbar.get()))
					self.master.update()
					self.master.update_idletasks()


					dirTypeDoc = self.PdfProcessados[arq]["Doc Type"]
					dirClient = self.PdfProcessados[arq]["Cliente"]

					#IDENTIFICIANDO LOCAL DO ARQUIVO NA ESTRUTURA
					tmpdirreferente = self.getDirPdf(dirTypeDoc)

					##--------------------------------------------------------------------------------
					if tmpdirreferente == None:
						caminho_destino = f"{self.Diretorio_Principal}/{dirClient}/{dirTypeDoc}/{infoano}/{infoday}"
					else:
						caminho_destino = f"{self.Diretorio_Principal}/{dirClient}/{tmpdirreferente}/{dirTypeDoc}/{infoano}/{infoday}"
					caminho_origem = f"{self.Diretorio}/{arq}"

					arq,caminho_origem = self.VerificarDuplicidade(caminho_destino,arq,self.Diretorio,caminho_origem)


					#-------------------TROCA DE LOCAL DE ARQUIVOS-----------------------
					if os.path.exists(f"{caminho_destino}"):
						os.rename(self.Diretorio + "/" + arq,f"{caminho_destino}/{arq}")
					else:
						os.makedirs(f"{caminho_destino}")
						os.rename(self.Diretorio + "/" + arq,f"{caminho_destino}/{arq}")
					#-------------------TROCA DE LOCAL DE ARQUIVOS-----------------------
						
					self.listbox.insert(END,f"{arq} Transferido para {self.Diretorio_Principal + "/" + arq}")

					if strftime("%m/%Y") in self.Historico.keys():
						self.Historico[strftime("%m/%Y")].append(f"Dia {strftime("%d")} {arq} Transferido para {self.Diretorio_Principal + "/" + arq}")
					else:
						self.Historico[strftime("%m/%Y")] = [f"Dia {strftime("%d")} {arq} Transferido para {self.Diretorio_Principal + "/" + arq}"]
				##--------------------------------------------------------------------------------


					#salvando dados para "desfazer"
					self.dados_tmp[arq] = [f"{self.Diretorio}",f"{caminho_destino}/{arq}"]
					self.master.update()
					self.master.update_idletasks()
				self.Bt_desfazer.configure(state='normal')
				self.Bt_desfazer.grid(row=4, padx=10, pady=10)
				self.salvar_dados_historico()
				
			else:
				messagebox.showerror("Erro","Não há pdf's no diretorio selecionado")
		else:
				messagebox.showerror("Erro","Selecione o diretorio corretamente")

class Cadastro(customtkinter.CTkFrame):
	def __init__(self, master, voltar_callback):
		super().__init__(master)
		self.voltar_callback = voltar_callback
		self.create_widgets()
		self.carregar_dados()
	
	def carregar_dados(self):
		if os.path.isfile('Clientes.json'):
			with open('Clientes.json', 'r', encoding='utf-8') as arq:
				self.Clientes = json.load(arq)
		else:
			with open('Clientes.json', 'w', encoding='utf-8') as arq:
				self.Clientes = {"12.345.678/0001-23": "CLIENTE EXEMPLO"}
				json.dump(self.Clientes,arq)
			return

	def create_widgets(self):
		self.leftFrameCadastro = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
		self.rightFrameCadastro = customtkinter.CTkScrollableFrame(self, width=450, height=300)

		self.EntryFrameCadastro = customtkinter.CTkFrame(self.leftFrameCadastro, fg_color='#6B6B6B')
		self.LabelRS = customtkinter.CTkLabel(self.EntryFrameCadastro, text='Razão social')
		self.EntryRSaCadastro = customtkinter.CTkEntry(self.EntryFrameCadastro, width=300)
		self.LabelCNPJ = customtkinter.CTkLabel(self.EntryFrameCadastro, text='CNPJ-CPF')
		self.EntryCNPJCadastro = customtkinter.CTkEntry(self.EntryFrameCadastro, width=300,validate='key',validatecommand=(self.master.register(self.ValidEntrys), '%P'))
		self.Bt_AddAlterar = customtkinter.CTkButton(self.EntryFrameCadastro, text="Cadastrar", command=self.ModfCadastCliente, fg_color='green')
		self.Bt_voltar_Cadastro = customtkinter.CTkButton(self.leftFrameCadastro, text="Voltar", command=self.voltar_callback)

		self.EntryCNPJCadastro.bind("<KeyRelease>",self.AplicarCracteresESpeciaisEntry)

		self.leftFrameCadastro.pack(fill='y', side='left', expand=1, padx=10, pady=10)
		self.rightFrameCadastro.pack(padx=10, pady=10)
		self.EntryFrameCadastro.pack(side='top', fill='x', padx=5, pady=5)
		
		self.LabelRS.grid(row=0, column=0, padx=5, pady=(10, 2.5), sticky="w")
		self.EntryRSaCadastro.grid(row=0, column=1)
		self.LabelCNPJ.grid(row=1, column=0, padx=5, sticky="w")
		self.EntryCNPJCadastro.grid(row=1, column=1)	
		self.Bt_AddAlterar.grid(row=2, column=3, pady=5, padx=50)
		self.Bt_voltar_Cadastro.pack(anchor="w", side="bottom", padx=10, pady=10)

	def ModfCadastCliente(self):
		TmpNome = (self.EntryRSaCadastro.get()).upper().strip()
		TmpNumeroIdentificacao = (self.EntryCNPJCadastro.get()).strip()
		TmpNumero = self.EntryCNPJCadastro.get().replace(".", "").replace("-", "").replace("/", "")
		self.AplicarCracteresESpeciaisEntry(None)
		if self.Bt_voltar_Cadastro._state == 'disabled':
			self.Bt_voltar_Cadastro.configure(state='normal')
			self.Bt_AddAlterar.configure(text="Cadastrar",fg_color='green')

		if len(TmpNumero) == 14 or len(TmpNumero) == 11 :
			if TmpNumeroIdentificacao not in self.Clientes.keys():
				self.EntryRSaCadastro.delete(0,"end")
				self.EntryCNPJCadastro.delete(0,"end")
				#criando label na lista
				Client_Label(self,self.rightFrameCadastro,TmpNome,TmpNumeroIdentificacao)
				#Escrevendo no banco temporario
				self.Clientes[TmpNumeroIdentificacao] = TmpNome

				#Escrevendo no banco permanente
				self.SalvarEmBancoClientes()
			else:
				messagebox.showwarning("Alerta","Este Cnpj ja esta cadastrado")
		else:
			messagebox.showwarning("Alerta","Numeração de Cadastro incorreta, insira um CNPJ ou CPF")

	def SalvarEmBancoClientes(self):
		#Salvando permanentemente em Banco de dados de Clientes
		with open('Clientes.json','w',encoding='utf-8') as arq:
			json.dump(self.Clientes,arq)
			arq.close()
		
	def ListarClientes(self):
		#Mostrar todos os clientes
		if self.rightFrameCadastro.winfo_children().__len__() == 0:
			for Cliente in list(self.Clientes.keys()):
				Client_Label(self,self.rightFrameCadastro,self.Clientes[Cliente],Cliente)
			pass

	def ValidEntrys(self,new_value):##Validando entrada de numeros no entry do historico
		new_value = new_value.replace(".", "").replace("-", "").replace("/", "")
		if new_value.isdigit() or new_value == '':
			#Caso esteja na entry do CNPJ-CPF 
			if new_value.__len__() <= 14:
				return True
			else:
				return False
		else:
			return False
		
	def AplicarCracteresESpeciaisEntry(self,event):
		new_value = self.EntryCNPJCadastro.get().replace(".", "").replace("-", "").replace("/", "")

		if new_value.__len__() == 14: 
			self.EntryCNPJCadastro.delete(0,self.EntryCNPJCadastro.get().__len__())
			self.EntryCNPJCadastro.insert(0,f"{new_value[0:2]}.{new_value[2:5]}.{new_value[5:8]}/{new_value[8:12]}-{new_value[12:15]}")
		elif new_value.__len__() == 11:
			self.EntryCNPJCadastro.delete(0,self.EntryCNPJCadastro.get().__len__())
			self.EntryCNPJCadastro.insert(0,f"{new_value[0:3]}.{new_value[3:6]}.{new_value[6:9]}-{new_value[9:11]}")

		elif new_value.__len__() == 9 or new_value.__len__() == 12 or new_value.__len__() == 13 :
			self.EntryCNPJCadastro.delete(0,self.EntryCNPJCadastro.get().__len__())
			self.EntryCNPJCadastro.insert(0,new_value)
		else:
			pass
	# end def

class Historico(customtkinter.CTkFrame):
	def __init__(self, master, voltar_callback):
		super().__init__(master)
		self.voltar_callback = voltar_callback
		self.Historico = {}
		self.create_widgets()

		self.carregar_dados()
		if strftime("%m/%Y") in self.Historico.keys():
			for i in self.Historico[strftime("%m/%Y")]:
				self.listbox_Historico.insert(END,i)

	def create_widgets(self):
		self.leftFrameHisto = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
		self.rightFrameHisto = customtkinter.CTkFrame(self)

		self.EntryFrameHisto = customtkinter.CTkFrame(self.leftFrameHisto, fg_color='#6B6B6B')
		
		self.LabelDt = customtkinter.CTkLabel(self.EntryFrameHisto, text='Data', anchor='center')
		self.LabelMes = customtkinter.CTkLabel(self.EntryFrameHisto, text='Mês')
		self.EntryMesHistorico = customtkinter.CTkEntry(self.EntryFrameHisto, width=45,validate='key',validatecommand=(self.master.register(self.ValidEntrys), '%P'))
		self.LabelAno = customtkinter.CTkLabel(self.EntryFrameHisto, text='Ano')
		self.EntryAnoHistorico = customtkinter.CTkEntry(self.EntryFrameHisto, width=45,validate='key',validatecommand=(self.master.register(self.ValidEntrys), '%P'))
		self.Bt_Pesquisar = customtkinter.CTkButton(self.EntryFrameHisto, text="Pesquisar",command=self.Pesq_Historico)
		self.Bt_voltar_Historico = customtkinter.CTkButton(self.leftFrameHisto, text="Voltar", command=self.voltar_callback)
		self.listbox_Historico = Listbox(self.rightFrameHisto, width=200, height=40)

		self.leftFrameHisto.pack(fill='y', side='left', expand=1, padx=10, pady=10)
		self.rightFrameHisto.pack(padx=10, pady=10)
		self.EntryFrameHisto.pack(side='top', fill='x', padx=5, pady=5, ipadx=5)
		
		self.LabelDt.pack()
		self.Bt_Pesquisar.pack(pady=5, side='bottom')
		self.LabelMes.pack(padx=5, side="left")
		self.EntryMesHistorico.pack(side="left")
		self.LabelAno.pack(padx=5, side="left")
		self.EntryAnoHistorico.pack(side="left")
		
		self.Bt_voltar_Historico.pack(side="bottom", padx=10, pady=10)
		self.listbox_Historico.pack()

	def Pesq_Historico(self):
		self.listbox_Historico.delete(0,END)
		if f"{self.EntryMesHistorico.get()}/{self.EntryAnoHistorico.get()}" in self.Historico.keys():
			for i in self.Historico[f"{self.EntryMesHistorico.get()}/{self.EntryAnoHistorico.get()}"]:
				self.listbox_Historico.insert(END,i)
		else:
			self.listbox_Historico.insert(END,"DATA NÃO ENCONTRADA")


	def carregar_dados(self):
		if os.path.isfile('Historico.json'):
			with open('Historico.json', 'r', encoding='utf-8') as arq:
				self.Historico = json.load(arq)
				arq.close()
		else:
			self.Historico = {f"{strftime("%m/%Y")}": ["Exemplo Historico"]}
			with open('Historico.json', 'w', encoding='utf-8') as arq:
				json.dump(self.Historico, arq)

	def ValidEntrys(self,new_value):
		if new_value.isdigit():
			match (self.master.focus_get().master):
				#switch em python 
				case self.EntryMesHistorico:
					#Caso esteja na entry do Mes 
					if int(new_value) <= 12:
						return True
					else:
						return False
					
				case self.EntryAnoHistorico:
					#Caso esteja na entry do Ano 
					if int(new_value) <= int(strftime("%Y")):
						return True
					else:
						return False
					
				case _:
					return True
				
		elif new_value == '':
			return True
		else:
			return False

class App:
	def __init__(self):
		self.janela = customtkinter.CTk()
		self.janela.title("Organizador de Diretórios")
		self.janela.resizable(False, False)

		'''#Criando barra de menu
		self.menuBar = Menu(self.janela)
		self.toolsMenuBar = Menu(self.menuBar,tearoff=False,)
		self.menuBar.add_cascade(label="Importar",menu=self.toolsMenuBar)
		self.toolsMenuBar.add_command(label="Auto Reconhecer Pdf",command=self.Ferramenta_AutoReconhecerPdf)
		self.toolsMenuBar.add_command(label="Estrutura",command=self.Ferramenta_Estrutura)
		self.janela.config(menu=self.menuBar)'''


		self.frame_menu_principal = MenuPrincipal(self.janela, self.abrir_cadastro, self.abrir_historico,self.abrir_estruturacao)
		self.frame_cadastro = Cadastro(self.janela, self.voltar_menu)
		self.frame_historico = Historico(self.janela, self.voltar_menu)
		self.frame_estrutura = GerenciadorCategorias(self.janela, self.voltar_menu)

		self.frame_menu_principal.pack()

	def Ferramenta_Estrutura(self):
		messagebox.showinfo("Aviso", "Selecione o diretorio ja existente com a estrutura de arquivos criada.")
		Diretorio = askdirectory()
		self.estrutura_final = {}
		pastas_encontradas = []
		pdfs_encontrados = []

		if Diretorio != "":
			self.estrutura_final = self.mapear_pastas_e_pdfs(Diretorio)
			print(self.estrutura_final)

		else:
			messagebox.showerror("Error", "Selecione o diretorio ja existente com a estrutura de arquivos criada.")

		
		if messagebox.askyesno("Alerta", "Sera apagado a estrutura existente, e sera criada uma nova") != True:
			return

		#Retirando Dado de diretorio matriz da estrutura
		if os.path.isfile('estrutura.json'):
			with open('estrutura.json', 'r') as file:
				self.categorias,self.Diretorio_Principal = json.load(file)
		else:
			self.Diretorio_Principal = ''

		"""Salva as categorias e subcategorias em um arquivo JSON."""
		with open('estrutura.json', 'w') as file:
			json.dump([self.categorias,self.Diretorio_Principal], file, indent=4)
		
	def mapear_pastas_e_pdfs(self,diretorio):
		def explorar_pasta(caminho):
			estrutura = {}
			for item in os.listdir(caminho):
				caminho_completo = os.path.join(caminho, item)
				if os.path.isdir(caminho_completo):# Se for uma pasta
					estrutura[item] = explorar_pasta(caminho_completo)# Chamada recursiva

			return estrutura
		return explorar_pasta(diretorio)
	
	def encontrar_pdfs(self,diretorio):
		pdfs_encontrados = []

		for raiz, _, arquivos in os.walk(diretorio):
			for arquivo in arquivos:
				if arquivo.lower().endswith(".pdf"):
					caminho_completo = os.path.join(raiz, arquivo)
					pdfs_encontrados.append(caminho_completo)

		return pdfs_encontrados
	
	def extrair_texto_pdfs_pypdf(self,lista_pdfs):
		pdfs_texto = {}

		for pdf in lista_pdfs:
			try:
				with open(pdf, "rb") as arquivo_pdf:
					leitor = PyPDF2.PdfReader(arquivo_pdf)
					texto_completo = ""

					for pagina in leitor.pages:
						texto_completo += pagina.extract_text() + " "

					# Quebrar o texto em uma lista de palavras
					palavras = texto_completo.split()

					# Adicionar ao dicionário
					pdfs_texto[pdf.split("\\")[-1]] = palavras

			except Exception as e:
				print(f"Erro ao processar {pdf}: {e}")

		return pdfs_texto
	
	def encontrar_palavras_exclusivas(self,dicionario_pdfs):
		# Passo 1: Criar um dicionário invertido {palavra: [pdfs onde aparece]}
		palavras_em_pdfs = {}

		for pdf, palavras in dicionario_pdfs.items():
			for palavra in set(palavras):  # Usamos 'set' para evitar duplicatas
				if palavra not in palavras_em_pdfs:
					palavras_em_pdfs[palavra] = []
				palavras_em_pdfs[palavra].append(pdf)

		# Passo 2: Remover palavras que aparecem em mais de um PDF
		palavras_exclusivas = {
			palavra: pdfs[0] for palavra, pdfs in palavras_em_pdfs.items() if len(pdfs) == 1
		}

		# Passo 3: Construir um novo dicionário com apenas palavras exclusivas
		dicionario_filtrado = {pdf: [] for pdf in dicionario_pdfs}

		for palavra, pdf in palavras_exclusivas.items():
			dicionario_filtrado[pdf].append(palavra)

		return dicionario_filtrado


	def Ferramenta_AutoReconhecerPdf(self):
		Diretorio = askdirectory()
		
		pdfs = self.encontrar_pdfs(Diretorio)

		dicio_pdfs = self.extrair_texto_pdfs_pypdf(pdfs)

		dicionario_final = self.encontrar_palavras_exclusivas(dicio_pdfs)

		# Exibir resultado
		for pdf, palavras in dicionario_final.items():
			print(f"\n📂 {pdf}")
			print(f"🔑 Palavras-chave: {palavras}")

	def abrir_cadastro(self):
		self.janela.config(menu="")
		
		self.frame_menu_principal.pack_forget()
		self.frame_cadastro.pack()
		self.frame_cadastro.ListarClientes()
		
	def abrir_historico(self):
		self.janela.config(menu="")
		
		self.frame_menu_principal.pack_forget()
		self.frame_historico.pack()

	def abrir_estruturacao(self):
		self.janela.config(menu="")
		
		self.frame_menu_principal.pack_forget()
		self.frame_estrutura.pack()
		pass


	def voltar_menu(self):
		self.frame_cadastro.pack_forget()
		self.frame_historico.pack_forget()
		self.frame_estrutura.pack_forget()
		self.frame_menu_principal.pack()
		'''self.janela.config(menu=self.menuBar)'''

if __name__ == "__main__":
	app = App()
	app.janela.mainloop()
