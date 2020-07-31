from tkinter import Tk
from tkinter import OptionMenu, Entry, Canvas, Checkbutton, LEFT,W, E,Y, RIGHT, Scrollbar
from tkinter import messagebox, Label, Button, Text, Frame, StringVar, IntVar, TOP, X
import os
import auxiliar
from Portico import *
from JanelaEditarSecao import *


class JanelaAnalisar:

    def __init__(self, master, portico):
        self.master = master
        master.title('Janela de Analise de Portico')
        self.master.geometry("760x650")
        self.master.minsize(760,600)
        self.master.resizable(0,0)
        self.portico = portico

        # Containers:
        #           Meio:
        #                   - Canvas com representaÃ§Ã£o da viga
        #           Inferior:
        #                   - Botões com barras 

        self.container_topo = Frame(self.master, width=700, height=30)
        self.container_topo.place(x=30, y=15)

        self.container_meio = Frame(self.master, width=700, height=50)        
        self.container_meio.place(x=30, y=50)

        self.container_inferior = Frame(self.master, width=700, height=450)        
        self.container_inferior.place(x=30, y=225)

        #################################################################################
        ####  Container Topo - Botões
        #################################################################################
        self.botao_completo = Button(self.container_topo,
                                    text='Completo',
                                    command=lambda : self.mostrar_barras())
        self.botao_completo.config(width=15)
        self.botao_completo.pack(side=LEFT)

        # self.botao_diagramas = Button(self.container_topo,
        #                             text='Diagramas',
        #                             command=lambda : self.mostrar_diagramas())
        # self.botao_diagramas.config(width=15)
        # self.botao_diagramas.pack(side=RIGHT)

        self.aaaaaaaa = Label(self.container_topo,
                                text="\t\t", height=1)
        self.aaaaaaaa.pack(side=LEFT)

        self.label_peso = Label(self.container_topo,
                                text=str(self.portico.SetarPeso()), height=1)
        self.label_peso.pack(side=LEFT)




        #################################################################################
        ####  Container Meio - Canvas
        #################################################################################

        self.canvas_portico = Canvas(self.container_meio, width=700,
                                    height=150, bd=1, highlightthickness=2, relief='ridge')
        self.canvas_portico.grid(row=4, column=1)

        ###########################################################################
        ### container Inferior
        ###########################################################################

        self.colour_schemes = [{"bg": "lightgrey", "fg": "black"}]
        # self.colour_schemes = [{"bg": "grey", "fg": "white"}]

        self.bars = []
        self.bars_canvas = Canvas(self.container_inferior, width=700, height=400)
        # self.bars_canvas = Canvas(self.master, width=700, height=450)
        self.bars_frame = Frame(self.bars_canvas)
        self.scrollbar = Scrollbar(self.bars_canvas, orient="vertical", command=self.bars_canvas.yview)

        self.bars_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.bars_canvas.grid(row=4, column=1)
        # self.bars_canvas.place(x=30, y=320)

        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas_frame = self.bars_canvas.create_window((0,0),
                                                            window=self.bars_frame,
                                                            anchor="n")
        
        self.master.bind_all("<MouseWheel>", self.mouse_scroll)
        self.master.bind_all("<Button-4>", self.mouse_scroll)
        self.master.bind_all("<Button-5>", self.mouse_scroll)
        self.master.bind("<Configure>", self.on_frame_configure)
        
        self.bars_canvas.bind("<Configure>", self.barr_width)

        self.mostrar_barras()

 


    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    
    
        
    

    def remove_bar(self):
        for bar in self.bars:
            bar.destroy()
        
        self.bars.clear()
    
                
    # Metodo que 'seta' as barras de mesmo tipo, para alimentar o canvas
    def mostrar_barras(self):
        # master = self.master

        self.remove_bar()
        self.bars = []
        self.canvas_cobertura()
        self.label_peso['text'] = ""
        peso = round(self.portico.SetarPeso(),2)
        self.label_peso['text'] = F" Peso do Pórtico (sem ligações): {peso} kg"

        cumeeira = self.portico.cumeeira
        barras_objetos = self.portico.lista_barras
        
        for b in barras_objetos:
            self.add_barr(b) # metodo para adicionar ao canvas

    # Metodo que cria o Label com as informaÃ§Ãµes da barra
    def add_barr(self, barra):
        if barra != None:
            # secao = stringSecaoBarra(barra)

            # Adiciona os Label's no Frame das barras (Frame dentro do canvas)
            tipo = barra.tipo
            barra_id = barra.id
            secao_inicio = barra.section_inicio
            ratio_inicio = round(barra.ratio_inicio_elu,2)
            ratio_momento_inicio = round(barra.ratio_mi,2)
            ratio_cortante_inicio = round(barra.ratio_vi,2)

            secao_final = barra.section_final
            ratio_final = round(barra.ratio_final_elu,2)
            ratio_momento_final = round(barra.ratio_mf,2)
            ratio_cortante_final = round(barra.ratio_vf,2)

            new_bar = Label(self.bars_frame,
                            text=F"""\t\t{tipo} - n: {barra_id} 
\t\t\t\tSeção Inicial da barra
\t\t\t{secao_inicio}  Combinado: {ratio_inicio}  | Momento: {ratio_momento_inicio}  | Cortante: {ratio_cortante_inicio} 
\t\t\t\tSeção Final da barra
\t\t\t{secao_final}  Combinado: {ratio_final}  | Momento: {ratio_momento_final}  | Cortante: {ratio_cortante_final} 
""", pady=1)
            new_bar.config(anchor=W, justify=LEFT, borderwidth=2, relief="ridge")
            self.set_bar_colour(len(self.bars), new_bar)
            elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)
            if elu > 1:
                new_bar.config(fg="red")
            elif elu > 0.7:
                new_bar.config(fg="blue")
            elif elu > 0.6:
                new_bar.config(fg="green")

            new_bar.bind("<Button-1>", lambda x: self.editar_barra(barra))
            new_bar.pack(side=TOP, fill=X)
            self.bars.append(new_bar)

    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    
    def editar_barra(self, barra):
        print('editar')
        root2 = Tk()
        editarSecao = JanelaEditarSecao(root2, barra, self)

    def mostrar_diagramas(self):
        print('diagramas')
    
    def canvas_cobertura(self):    
        lista_vaos, largura = self.pegar_vaos()
        
        if largura * 7 < 700:
            xi = 15 +(350 - largura/2*7)
            m = 7
        elif largura * 6 < 700:
            xi = 15 +(350 - largura/2*6)
            m = 6
        elif largura * 5 < 700:
            xi = 15 +(350 - largura/2*5)
            m = 5
        elif largura * 4 < 650:
            xi = 15 +(350 - largura/2*4)
            m = 4
        elif largura * 3 < 650:
            xi = 15 +(350 - largura/2*3)
            m = 3
        else:
            xi = 15 +(350 - largura/2*2)
            m = 2

        cumeeira = float(self.portico.cumeeira)
        pe_direito = float(self.portico.pe_direito)
        inclinacao = float(self.portico.inclinacao)
        influencia = float(self.portico.influencia)
        altura_minima = float(self.portico.altura_minima)

        pilar_metalico = self.portico.pilar_metalico

        can = self.canvas_portico
        can.delete('all')

        if len(lista_vaos)>0:
            for barra in self.portico.lista_barras:
                barra.verificar_elu()
                elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

                cor = "black"
                if elu > 1.0:
                    cor = "red"
                elif 0.8 < elu <= 1.0:
                    cor = "blue"
                elif 0.6 < elu <=0.8:
                    cor="green"

                if barra.tipo == 'viga':
                    pi = (xi+barra.ni.x*m, 100-barra.ni.y*m)
                    pf = (xi+barra.nf.x*m, 100-barra.nf.y*m)
                    can.create_line(pi,  pf,  fill=cor,width=1)

                    pii = (xi+barra.ni.x*m, 100-barra.ni.y*m - barra.section_inicio.d*m)
                    pff = (xi+barra.nf.x*m, 100-barra.nf.y*m - barra.section_final.d*m)
                    can.create_line(pii,  pff,  fill=cor,width=1)
                    can.create_line(pii,  pi,  fill=cor,width=1)
                    can.create_line(pff,  pf,  fill=cor,width=1)
                    
                    can.create_text(pi[0] + (pf[0]-pi[0])/2.0, pii[1]-8, font="Times 9",
                                    text=str(barra.id), fill=cor)
                elif barra.tipo == "coluna-externa":
                    pi = (xi+barra.ni.x*m - barra.section_inicio.d*m*0.5, 100-barra.ni.y*m)
                    pf = (xi+barra.nf.x*m - barra.section_final.d*m*0.5, 100-barra.nf.y*m)
                    can.create_line(pi,  pf,  fill=cor,width=1)

                    pi = (xi+barra.ni.x*m + barra.section_inicio.d*m*0.5, 100-barra.ni.y*m)
                    pf = (xi+barra.nf.x*m + barra.section_final.d*m*0.5, 100-barra.nf.y*m)
                    can.create_line(pi,  pf,  fill=cor,width=1)

                    can.create_text(pi[0]+1*m, 100-barra.nf.y*m/2, font="Times 9",
                                    text=str(barra.id), fill=cor)
                else:
                    pi = (xi-2+barra.ni.x*m, 100-barra.ni.y*m)
                    pf = (xi-2+barra.nf.x*m, 100-barra.nf.y*m)
                    can.create_line(pi,  pf,  fill=cor,width=1)

                    pi = (xi+2+barra.ni.x*m, 100-barra.ni.y*m)
                    pf = (xi+2+barra.nf.x*m, 100-barra.nf.y*m)
                    can.create_line(pi,  pf,  fill=cor,width=1)

                    can.create_text(pi[0]+1*m, 100-barra.nf.y*m/2, font="Times 9",
                                    text=str(barra.id), fill=cor)

        for base in self.portico.lista_bases:
            p1 = (xi+base.x*m, 100-base.y*m)
            if base.apoio =='engaste':
                # horizontais
                p1a =(p1[0]-10,p1[1])
                p1b =(p1[0]+10,p1[1])
                can.create_line(p1, p1a, fill="red", width=1)
                can.create_line(p1, p1b, fill="red", width=1)
                # diagonais
                p2a = (p1a[0]-5, p1a[1]+5)
                p2b = (p1b[0]-5, p1b[1]+5)
                p2 = (p1[0]-5, p1[1]+5)
                can.create_line(p1, p2, fill="red", width=1)
                can.create_line(p1a, p2a, fill="red", width=1)
                can.create_line(p1b, p2b, fill="red", width=1)
            elif base.apoio == 'rotulado' or base.apoio == 'bi-articulado':
                # diagonais
                p1a =(p1[0]-6,p1[1]+10)
                p1b =(p1[0]+6,p1[1]+10)
                can.create_line(p1, p1a, fill="red", width=1)
                can.create_line(p1, p1b, fill="red", width=1)
                # horizontal
                can.create_line(p1b, p1a, fill="red", width=1)
            elif base.apoio == 'simples':
                # diagonais
                p1a =(p1[0]-6,p1[1]+10)
                p1b =(p1[0]+6,p1[1]+10)
                can.create_line(p1, p1a, fill="red", width=1)
                can.create_line(p1, p1b, fill="red", width=1)
                # horizontal
                p2a = (p1a[0], p1a[1]+3)
                p2b = (p1b[0], p1b[1]+3)
                can.create_line(p1b, p1a, fill="red", width=1)
                can.create_line(p2b, p2a, fill="red", width=1)



    def pegar_vaos(self):
        lista_vaos = []
        largura = 0
        for vao in self.portico.lista_vaos:
            lista_vaos.append(float(vao))
            largura += float(vao)
        return lista_vaos, largura


####################################################################################
####################################################################################
####################################################################################
####################################################################################

    def recolour_bars(self):
        for index, barr in enumerate(self.bars):
            self.set_bar_colour(index, barr)


    def set_bar_colour(self, position, barr):
        my_scheme_choice = self.colour_schemes[0]
        barr.configure(bg=my_scheme_choice["bg"])
        barr.configure(fg=my_scheme_choice["fg"])


    def on_frame_configure(self, event=None):
        self.bars_canvas.configure(scrollregion=self.bars_canvas.bbox("all"))


    def barr_width(self, event):
        canvas_width = event.width
        self.bars_canvas.itemconfigure(self.canvas_frame, width=canvas_width)


    def mouse_scroll(self, event):
        if event.delta:
            self.bars_canvas.yview_scroll(-1*int(event.delta/120), "units")
        else:
            if event.num == 5:
                move = 1
            else:
                move = -1

            self.bars_canvas.yview_scroll(move, "units")
