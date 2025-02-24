import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages":["os","json","time"],"includes":["tkinter","customtkinter","PyPDF2"]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    

setup(
    name="PdfOrganizer",
    version="0.1",
    description="Organizador de pdfs por leitura",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)