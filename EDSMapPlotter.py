
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
