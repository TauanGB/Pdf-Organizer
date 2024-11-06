import customtkinter
from tkinter import Listbox
from tkinter.filedialog import askdirectory
from tkinter import messagebox
import PyPDF2 as PdfReader
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

class MenuPrincipal(customtkinter.CTkFrame):
	def __init__(self, master, abrir_cadastro_callback, abrir_historico_callback, organizar_callback):
		super().__init__(master)
		self.abrir_cadastro_callback = abrir_cadastro_callback
		self.abrir_historico_callback = abrir_historico_callback
		self.organizar_callback = organizar_callback
		self.create_widgets()

	def create_widgets(self):
		self.leftFrameMenu = customtkinter.CTkFrame(self, corner_radius=0)
		self.rightFrameMenu = customtkinter.CTkFrame(self)
		
		self.leftFrameMenu.grid(row=0, sticky="N")
		self.rightFrameMenu.grid(row=0, column=1)
		
		# Botões do menu
		self.Bt_cadastro = customtkinter.CTkButton(self.leftFrameMenu, text="Cadastro", command=self.abrir_cadastro_callback)
		self.Bt_historico = customtkinter.CTkButton(self.leftFrameMenu, text="Histórico", command=self.abrir_historico_callback)
		self.Bt_organizar = customtkinter.CTkButton(self.leftFrameMenu, text="Organizar", command=self.organizar_callback)
		
		self.Bt_cadastro.grid(row=0, padx=10, pady=10)
		self.Bt_historico.grid(row=1, padx=10, pady=10)
		self.Bt_organizar.grid(row=2, padx=10, pady=10)

		# Listbox e barra de progresso
		self.progressbar = customtkinter.CTkProgressBar(self.rightFrameMenu, progress_color="#0ACF00", orientation='horizontal', width=350)
		self.listbox = Listbox(self.rightFrameMenu, width=60, height=15)
		
		self.progressbar.pack(padx=10, pady=10, expand=1)
		self.listbox.pack(padx=10, pady=10)

class Cadastro(customtkinter.CTkFrame):
	def __init__(self, master, voltar_callback, Clientes):
		super().__init__(master)
		self.Clientes = Clientes
		self.voltar_callback = voltar_callback
		self.create_widgets()

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
		self.create_widgets()
		print(master.title())

	def create_widgets(self):
		self.leftFrameHisto = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
		self.rightFrameHisto = customtkinter.CTkFrame(self)

		self.EntryFrameHisto = customtkinter.CTkFrame(self.leftFrameHisto, fg_color='#6B6B6B')
		self.LabelDt = customtkinter.CTkLabel(self.EntryFrameHisto, text='Data', anchor='center')
		self.LabelDia = customtkinter.CTkLabel(self.EntryFrameHisto, text='Dia')
		self.EntryDiaHistorico = customtkinter.CTkEntry(self.EntryFrameHisto, width=45)
		self.LabelMes = customtkinter.CTkLabel(self.EntryFrameHisto, text='Mês')
		self.EntryMesHistorico = customtkinter.CTkEntry(self.EntryFrameHisto, width=45)
		self.LabelAno = customtkinter.CTkLabel(self.EntryFrameHisto, text='Ano')
		self.EntryAnoHistorico = customtkinter.CTkEntry(self.EntryFrameHisto, width=45)
		self.Bt_Pesquisar = customtkinter.CTkButton(self.EntryFrameHisto, text="Pesquisar")
		self.Bt_voltar_Historico = customtkinter.CTkButton(self.leftFrameHisto, text="Voltar", command=self.voltar_callback)
		self.listbox_Historico = Listbox(self.rightFrameHisto, width=60, height=15)

		self.leftFrameHisto.pack(fill='y', side='left', expand=1, padx=10, pady=10)
		self.rightFrameHisto.pack(padx=10, pady=10)
		self.EntryFrameHisto.pack(side='top', fill='x', padx=5, pady=5, ipadx=5)
		
		self.LabelDt.pack()
		self.Bt_Pesquisar.pack(pady=5, side='bottom')
		self.LabelDia.pack(padx=5, side="left")
		self.EntryDiaHistorico.pack(side="left")
		self.LabelMes.pack(padx=5, side="left")
		self.EntryMesHistorico.pack(side="left")
		self.LabelAno.pack(padx=5, side="left")
		self.EntryAnoHistorico.pack(side="left")
		
		self.Bt_voltar_Historico.pack(side="bottom", padx=10, pady=10)
		self.listbox_Historico.pack()

class App:
	def __init__(self):
		self.janela = customtkinter.CTk()
		self.janela.title("Organizador de Diretórios")
		self.janela.resizable(False, False)

		if os.path.isfile('Clientes.json'):
			with open('Clientes.json', 'r', encoding='utf-8') as arq:
				self.Clientes = json.load(arq)
		else:
			self.Clientes = {"CNPJ Exemplo": "Cliente Exemplo"}
			with open('Clientes.json', 'w', encoding='utf-8') as arq:
				json.dump(self.Clientes, arq)

		self.frame_menu_principal = MenuPrincipal(self.janela, self.abrir_cadastro, self.abrir_historico, self.organizar)
		self.frame_cadastro = Cadastro(self.janela, self.voltar_menu,self.Clientes)
		self.frame_historico = Historico(self.janela, self.voltar_menu)

		self.frame_menu_principal.pack()


	def abrir_cadastro(self):
		self.frame_menu_principal.pack_forget()
		self.frame_cadastro.pack()
		self.frame_cadastro.ListarClientes()
		

	def abrir_historico(self):
		self.frame_menu_principal.pack_forget()
		self.frame_historico.pack()

	def organizar(self):
		#TODO adicionar função principal
		self.Diretorio = askdirectory()
		if not self.Diretorio:
			return

	def voltar_menu(self):
		self.frame_cadastro.pack_forget()
		self.frame_historico.pack_forget()
		self.frame_menu_principal.pack()

if __name__ == "__main__":
	app = App()
	app.janela.mainloop()
