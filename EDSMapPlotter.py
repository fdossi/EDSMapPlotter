<<<<<<< HEAD
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, MULTIPLE, messagebox
from PIL import Image, ImageTk
import ctypes

# --- Configuração de High DPI (Melhora nitidez no Windows) ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# --- Tentativa de Importar Drag-and-Drop ---
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

# --- Função para Caminho de Recursos (Essencial para .exe) ---
def resource_path(relative_path):
    """Obtém caminho absoluto para recursos (imagens), funciona em dev e PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def gerar_eds_map(caminho_csv: str, pasta_saida: str, cmap_name: str = "viridis") -> bool:
    try:
        # Leitura robusta do CSV (sem cabeçalho)
        df = pd.read_csv(caminho_csv, header=None)
        df_numeric = df.apply(pd.to_numeric, errors="coerce")
        data = df_numeric.to_numpy(dtype=float)
        
        # Validação de dados
        if data.size == 0 or np.all(np.isnan(data)):
            print(f"Dados inválidos/vazios em: {caminho_csv}")
            return False

        # Extração inteligente do nome do elemento
        nome = os.path.basename(caminho_csv)
        n0 = os.path.splitext(nome)[0]
        parts = n0.split("_")
        
        if len(parts) > 1:
            elemento = parts[-1] # Pega o último termo após "_"
            prefix = "_".join(parts[:-1])
            out_name = f"{prefix}_edsmap_{elemento}.png"
        else:
            elemento = n0
            out_name = f"edsmap_{elemento}.png"
            
        path_salvar = os.path.join(pasta_saida, out_name)

        # Plotagem
        fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
        im = ax.imshow(data, cmap=cmap_name, origin='upper', interpolation='bilinear')
        ax.set_aspect('equal')
        ax.axis('off')

        ax.set_title(f"EDS-Map - {elemento}", fontsize=26, pad=16)

        cbar = fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)
        cbar.set_label("Intensidade", fontsize=22)
        cbar.ax.tick_params(labelsize=18)

        plt.tight_layout()
        fig.savefig(path_salvar, dpi=300, bbox_inches="tight")
        plt.close(fig) # Libera memória
        return True
    
    except Exception as e:
        print(f"Erro ao processar {caminho_csv}: {e}")
        return False

def main():
    # Definição dos Arquivos de Ícone
    ICON_PNG = resource_path("EDSMapPlotter_icon.png")
    ICON_ICO = resource_path("EDSMapPlotter_icon.ico")
    
    # Lista de cores do Matplotlib/Seaborn
    cmap_opcoes = ["Blues", "viridis", "magma", "inferno", "plasma", "cividis", 
                   "Greys", "Reds", "Greens", "Oranges", "Purples", "turbo", 
                   "Spectral", "coolwarm", "seismic", "jet"]

    # Inicializa Janela (com ou sem DnD)
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        messagebox.showinfo("Aviso", "Biblioteca Drag-and-Drop não encontrada.\nUse o botão 'Selecionar Arquivos'.")

    root.title("EDSMapPlotter v0.2.0")
    root.geometry("620x680")

    # Tenta carregar ícone da janela (.ico no Windows fica melhor)
    try:
        if os.name == 'nt' and os.path.exists(ICON_ICO):
            root.iconbitmap(ICON_ICO)
        elif os.path.exists(ICON_PNG):
            icon = tk.PhotoImage(file=ICON_PNG)
            root.iconphoto(False, icon)
    except Exception:
        pass

    # --- Interface Gráfica ---
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    # Logo no topo
    try:
        if os.path.exists(ICON_PNG):
            img = Image.open(ICON_PNG).resize((110, 110), Image.Resampling.LANCZOS)
            tklogo = ImageTk.PhotoImage(img)
            lbl_logo = tk.Label(main_frame, image=tklogo)
            lbl_logo.image = tklogo
            lbl_logo.pack(pady=(0, 15))
    except Exception:
        pass

    # Área de Lista
    tk.Label(main_frame, text="Arquivos CSV Selecionados:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
    
    list_frame = tk.Frame(main_frame)
    list_frame.pack(fill="x", pady=5)
    
    scrollbar = tk.Scrollbar(list_frame, orient="vertical")
    lista = tk.Listbox(list_frame, selectmode=MULTIPLE, height=8, yscrollcommand=scrollbar.set, bg="#f8f9fa", font=("Consolas", 9))
    scrollbar.config(command=lista.yview)
    
    scrollbar.pack(side="right", fill="y")
    lista.pack(side="left", fill="x", expand=True)

    # Lógica da Lista
    def add_files(filepaths):
        exist = set(lista.get(0, tk.END))
        count_new = 0
        for p in filepaths:
            # Remove chaves {} que o TkDnD às vezes coloca no Windows
            p = p.strip("{}") 
            if p not in exist and p.lower().endswith(".csv"):
                lista.insert(tk.END, p)
                count_new += 1
        lbl_status.config(text=f"{count_new} arquivos adicionados.", fg="#0056b3")

    def sel():
        paths = filedialog.askopenfilenames(filetypes=[("Arquivos CSV", "*.csv")])
        add_files(paths)

    def rem():
        sel_items = list(lista.curselection())
        for i in reversed(sel_items):
            lista.delete(i)
        lbl_status.config(text=f"{len(sel_items)} arquivos removidos.", fg="#dc3545")

    # Botões de Controle da Lista
    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(fill="x", pady=5)
    tk.Button(btn_frame, text="📂 Adicionar CSVs", command=sel, width=18).pack(side="left", padx=5)
    tk.Button(btn_frame, text="❌ Remover Seleção", command=rem, width=18).pack(side="right", padx=5)

    # Configuração de Saída
    tk.Label(main_frame, text="Salvar Imagens em:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(20,0))
    
    out_frame = tk.Frame(main_frame)
    out_frame.pack(fill="x", pady=5)
    out_entry = tk.Entry(out_frame)
    out_entry.pack(side="left", fill="x", expand=True)
    
    def sel_out():
        d = filedialog.askdirectory()
        if d:
            out_entry.delete(0, tk.END)
            out_entry.insert(0, d)
    
    tk.Button(out_frame, text="...", command=sel_out, width=4).pack(side="right", padx=5)

    # Seletor de Cores
    tk.Label(main_frame, text="Esquema de Cores (Colormap):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15,0))
    cmap_var = tk.StringVar(value="viridis")
    opt = tk.OptionMenu(main_frame, cmap_var, *cmap_opcoes)
    opt.config(width=25)
    opt.pack(anchor="w", pady=5)

    # Barra de Status
    lbl_status = tk.Label(main_frame, text="Pronto para iniciar.", bd=1, relief=tk.SUNKEN, anchor="w", fg="#666")
    lbl_status.pack(side="bottom", fill="x", pady=(20,0))

    # Processamento Principal
    def process():
        files = lista.get(0, tk.END)
        folder = out_entry.get().strip()
        
        if not files:
            messagebox.showwarning("Atenção", "Nenhum arquivo CSV foi selecionado.")
            return
        if not folder:
            messagebox.showwarning("Atenção", "Por favor, selecione a pasta onde as imagens serão salvas.")
            return
            
        os.makedirs(folder, exist_ok=True)
        lbl_status.config(text="Processando... Isso pode levar alguns segundos.", fg="#e67e22")
        root.update() # Atualiza a tela imediatamente
        
        sucessos = 0
        erros = 0
        
        for f in files:
            ok = gerar_eds_map(f, folder, cmap_var.get())
            if ok: sucessos += 1
            else: erros += 1
        
        lbl_status.config(text=f"Finalizado: {sucessos} mapas gerados com sucesso.", fg="#28a745")
        
        msg = f"Processamento concluído!\n\n✅ Sucessos: {sucessos}\n❌ Erros: {erros}\n\nImagens salvas em:\n{folder}"
        messagebox.showinfo("Relatório", msg)

    # Botão Gigante de Ação
    tk.Button(main_frame, text="GERAR MAPAS", command=process, bg="#28a745", fg="white", 
              font=("Segoe UI", 12, "bold"), height=2, cursor="hand2").pack(fill="x", pady=25)

    # Drag and Drop Bindings
    if HAS_DND:
        def drop(event):
            # O TkinterDnD pode retornar caminhos entre chaves {C:/caminho/com espaco}
            raw_data = event.data
            # Lógica simples para separar arquivos (funciona na maioria dos casos Windows)
            if raw_data.startswith("{") and "}" in raw_data:
                 # Regex ou split simples para extrair conteúdo entre chaves seria ideal, 
                 # mas o root.tk.splitlist geralmente resolve bem no Windows
                 paths = root.tk.splitlist(raw_data)
            else:
                 paths = raw_data.split()
            
            add_files(paths)

        lista.drop_target_register(DND_FILES)
        lista.dnd_bind('<<Drop>>', drop)

    root.mainloop()

if __name__ == "__main__":
    main()
=======

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog, MULTIPLE, messagebox
from PIL import Image, ImageTk

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    TkinterDnD = None
    DND_FILES = None

def gerar_eds_map(caminho_csv: str, pasta_saida: str, cmap_name: str = "Blues") -> None:
    try:
        df = pd.read_csv(caminho_csv, header=None)
        df_numeric = df.apply(pd.to_numeric, errors="coerce")
        data = df_numeric.to_numpy(dtype=float)
    except Exception as e:
        messagebox.showerror("Erro", str(e)); return
    if data.size==0 or np.all(np.isnan(data)):
        messagebox.showwarning("Aviso","Dados inválidos"); return

    nome = os.path.basename(caminho_csv)
    n0 = os.path.splitext(nome)[0]
    parts=n0.split("_")
    if len(parts)>1:
        elemento=parts[-1]; prefix="_".join(parts[:-1])
        out=f"{prefix}_edsmap_{elemento}.png"
    else:
        elemento=n0; out=f"edsmap_{elemento}.png"
    path=os.path.join(pasta_saida,out)

    fig,ax=plt.subplots(figsize=(8,6))
    hm=sns.heatmap(data, cmap=cmap_name, cbar_kws={"label":"Intensidade"}, xticklabels=False, yticklabels=False)
    ax.set_title(f"EDS-Map - {elemento}", fontsize=28)
    cb=hm.collections[0].colorbar
    cb.ax.tick_params(labelsize=18); cb.set_label("Intensidade", fontsize=22)
    plt.tight_layout(); fig.savefig(path,dpi=300,bbox_inches="tight"); plt.close(fig)

def main():
    ICON="EDSMapPlotter_icon.png"
    cmap_opcoes=["Blues","viridis","magma","inferno","plasma","cividis","Greys","Reds","Greens","Oranges","Purples","turbo","Spectral","coolwarm","seismic"]

    root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    root.title("EDSMapPlotter — Gerador de Mapas EDS")

    try:
        icon=tk.PhotoImage(file=ICON); root.iconphoto(False, icon)
    except: pass

    frame=tk.Frame(root,padx=10,pady=10); frame.pack(fill="both",expand=True)

    try:
        img = Image.open(ICON).resize((120,120))
        tklogo = ImageTk.PhotoImage(img)
        lbl=tk.Label(frame,image=tklogo); lbl.image=tklogo
        lbl.grid(row=0,column=0,columnspan=2,pady=(0,15))
    except: pass

    base_row=1
    tk.Label(frame,text="Arquivos CSV selecionados:").grid(row=base_row,column=0,sticky="w")
    lista=tk.Listbox(frame,selectmode=MULTIPLE,width=80,height=10)
    lista.grid(row=base_row+1,column=0,columnspan=2,pady=5)

    def sel():
        paths=filedialog.askopenfilenames(filetypes=[("CSV","*.csv")])
        exist=set(lista.get(0,tk.END))
        for p in paths:
            if p not in exist: lista.insert(tk.END,p)

    def rem():
        for i in reversed(lista.curselection()): lista.delete(i)

    tk.Label(frame,text="Pasta de saída:").grid(row=base_row+3,column=0,sticky="w")
    out=tk.Entry(frame,width=60); out.grid(row=base_row+4,column=0,pady=5,sticky="w")
    def sel_out():
        d=filedialog.askdirectory()
        if d: out.delete(0,tk.END); out.insert(0,d)

    tk.Label(frame,text="Mapa de cores:").grid(row=base_row+5,column=0,sticky="w")
    cmap=tk.StringVar(value=cmap_opcoes[0])
    tk.OptionMenu(frame,cmap,*cmap_opcoes).grid(row=base_row+6,column=0,pady=5,sticky="w")

    def process():
        files=lista.get(0,tk.END); folder=out.get().strip()
        if not files: messagebox.showwarning("Aviso","Nada selecionado"); return
        if not folder: messagebox.showwarning("Aviso","Selecione pasta"); return
        os.makedirs(folder,exist_ok=True)
        for f in files: gerar_eds_map(f,folder,cmap.get())
        messagebox.showinfo("Concluído","Processamento finalizado.")

    if TkinterDnD and DND_FILES:
        def drop(ev):
            items=root.splitlist(ev.data)
            exist=set(lista.get(0,tk.END))
            for p in items:
                if p.lower().endswith(".csv") and p not in exist:
                    lista.insert(tk.END,p)
        lista.drop_target_register(DND_FILES)
        lista.dnd_bind("<<Drop>>", drop)

    tk.Button(frame,text="Selecionar Arquivos",command=sel).grid(row=base_row+2,column=0,sticky="w")
    tk.Button(frame,text="Remover Selecionados",command=rem).grid(row=base_row+2,column=1,sticky="w")
    tk.Button(frame,text="Selecionar Pasta",command=sel_out).grid(row=base_row+4,column=1,sticky="w")
    tk.Button(frame,text="Processar Arquivos",command=process,bg="green",fg="white").grid(row=base_row+7,column=0,columnspan=2,pady=10)

    root.mainloop()

if __name__=="__main__":
    main()
>>>>>>> daca29debfbb140fca5b9c39c0406aa9b93e0d3c
