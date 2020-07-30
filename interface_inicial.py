from tkinter import Tk
from tkinter import messagebox, Label, Button, Text, Frame, StringVar, IntVar, OptionMenu, Entry, Canvas, Checkbutton, LEFT,W, E
import os
import auxiliar
from Portico import *
 




class JanelaInicial:

    def __init__(self, master):
        self.master = master
        master.title('Programa Estimativo de Porticos')
        self.master.geometry("760x460")
        self.master.minsize(760,460)
        self.master.resizable(0,0)

        # Containers:
        #           Esquerdo:
        #                   - Entrys para valores de vÃ£o
        #                   - Entry para valor da cumeeira
        #           Direito:
        #                   - valor de carregamentos
        #                   - areas de influencia
        #           Direito_extremo:
        #                   - Canvas com apresentaÃ§Ã£o da geometria
        #           Meio:
        #                   - Canvas com representaÃ§Ã£o da viga

        self.container_esquerdo = Frame(self.master)
        self.container_esquerdo.place(x=30, y=15)
        
        # container com valores geometricos, vinculos e carregamentos
        self.container_direito = Frame(self.master)
        self.container_direito.place(x=430, y=15)

        self.container_meio = Frame(self.master, width=700, height=300)        
        self.container_meio.place(x=30, y=215)

        self.container_inferior = Frame(self.master, width=700, height=300)        
        self.container_inferior.place(x=30, y=415)

        ###########################################################################
        ###########################################################################

        self.pilar_metalico = IntVar()
        self.pilar_metalico.set(0)

        ###########################################################################
        ###########################################################################
 
        linha = 2
        coluna = 1
        largura = 8
        self.text_largura_inf = self.InserirLabelEEntry('Distancia entre Vigas =',
                                                        '[m]', linha,coluna,largura,10.0,
                                                        self.container_direito)

        self.label_vazio4 = Label(self.container_direito, text='\t', height=1)
        self.label_vazio4.grid(row=4, column=1)

        linha = 5
        self.text_cp = self.InserirLabelEEntry('Carga Permanente =',
                                                '[kg/m2]', linha,coluna,largura,18.0,
                                                self.container_direito)

        linha = 6
        self.text_cp = self.InserirLabelEEntry('Sobrecarga Norma =',
                                                '[kg/m2]', linha,coluna,largura,25.0,
                                                self.container_direito)

        linha = 7
        self.text_su = self.InserirLabelEEntry('Sobrecarga Utilidade =',
                                                '[kg/m2]', linha, coluna, largura, 15.0,
                                                self.container_direito)

        linha = 8
        self.text_cv = self.InserirLabelEEntry('Sobrecarga Vento =',
                                                '[kg/m2]', linha, coluna, largura, 75.0,
                                                self.container_direito)
        

        #################################################################################
        ####  Container Meio - Canvas
        #################################################################################

        self.canvas_portico = Canvas(self.container_meio, width=700,
                                    height=150, bd=1, highlightthickness=2, relief='ridge')
        self.canvas_portico.grid(row=4, column=1)

        ###########################################################################
        ### container esquerdo
        ###########################################################################
 
        linha = 2
        coluna = 1
        largura = 20
        texto0 = "Vãos ="
        texto1 = "Inclinação Cobertura ="
        texto2 = "Posição da Cumeeira  ="
        texto3 = "Pé direito ="
        texto4 = "Altura Minima ="
        self.text_vaos = self.InserirLabelEEntry(texto0,
                                                '[m]', linha,coluna,largura,"25 25 25 25",
                                                self.container_esquerdo
                                                )
        self.text_vaos.bind("<FocusOut>", lambda x: self.canvas_cobertura())

        linha = 4
        largura = 20
        self.text_inclinacao = self.InserirLabelEEntry(texto1,
                                                        '[%]', linha,coluna,largura, "3.0",
                                                        self.container_esquerdo)
        self.text_inclinacao.bind("<FocusOut>", lambda x: self.canvas_cobertura())

        linha = 5
        self.text_cumeeira = self.InserirLabelEEntry(texto2,
                                                    '[m]', linha,coluna,largura, "50.0",
                                                    self.container_esquerdo)
        self.text_cumeeira.bind("<FocusOut>", lambda x: self.canvas_cobertura())

        linha += 1
        self.text_pe_direito = self.InserirLabelEEntry(texto3,
                                                    '[m]', linha,coluna,largura, "9.5",
                                                    self.container_esquerdo)
        self.text_pe_direito.bind("<FocusOut>", lambda x: self.canvas_cobertura())
                                                    
        linha += 1
        self.text_altura_minima = self.InserirLabelEEntry(texto4,
                                                    '[mm]', linha, coluna,largura, 0.0,
                                                    self.container_esquerdo)

        linha += 1
        
        self.check_pilar_metalico = Checkbutton(self.container_esquerdo,
                                    text="Pilar Metálico (?)",
                                    variable=self.pilar_metalico)
        self.check_pilar_metalico.grid(row=linha, column=1, sticky=W)

        self.label_vazio4 = Label(self.container_direito, text='\t', height=1)
        # self.label_vazio4.grid(row=4, column=1)
        self.label_vazio4.grid(row=4, column=1, sticky=W)

        self.canvas_cobertura()

        self.button_analisar = Button(self.container_inferior, text="Analisar Pórtico", command=self.analisar_portico)
        self.button_analisar.config(width=48)
        self.button_analisar.pack(side=LEFT)

        self.button_otimizar = Button(self.container_inferior, text="Otimizar Pórtico", command=self.otimizar_portico)
        self.button_otimizar.config(width=48)
        self.button_otimizar.pack(side=LEFT)


    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    def analisar_portico(self):
        print('Analisar')
        lista_vaos, largura = self.pegar_vaos()

        cumeeira = float(self.text_cumeeira.get())
        pe_direito = float(self.text_pe_direito.get())
        inclinacao = float(self.text_inclinacao.get())
        influencia = float(self.text_largura_inf.get())

        pilar_metalico = True
        if self.pilar_metalico == 0:
            pilar_metalico = False



    def otimizar_portico(self):
        print('Otimizar')
    
    def pegar_vaos(self):
        lista_vaos1 = self.text_vaos.get().split(" ")
        lista_vaos = []
        largura = 0
        for vao in lista_vaos1:
            if len(vao) != 0:
                lista_vaos.append(float(vao))
                largura += float(vao)
        return lista_vaos, largura
        
    def canvas_cobertura(self):    
        lista_vaos, largura = self.pegar_vaos()
        
        if largura * 5 < 650:
            xi = 30 +(350 - largura/2*5)
            m = 5
        elif largura * 4 < 650:
            xi = 30 +(350 - largura/2*4)
            m = 4
        elif largura * 3 < 650:
            xi = 30 +(350 - largura/2*3)
            m = 3
        else:
            xi = 30 +(350 - largura/2*2)
            m = 2

        cumeeira = float(self.text_cumeeira.get())
        pe_direito = float(self.text_pe_direito.get())
        inclinacao = float(self.text_inclinacao.get())

        pilar_metalico = True
        if self.pilar_metalico == 0:
            pilar_metalico = False

        portico_canvas = Portico(lista_vaos, pe_direito, cumeeira, inclinacao, 10, 0, pilar_metalico)
        can = self.canvas_portico

        can.delete('all')

        if len(lista_vaos)>0:
            for barra in portico_canvas.lista_barras:
                pi = (xi+barra.ni.x*m, 100-barra.ni.y*m)
                pf = (xi+barra.nf.x*m, 100-barra.nf.y*m)
                can.create_line(pi,  pf,  fill="black",width=3)

            # cota do pÃo direito
            primeira_coluna = portico_canvas.lista_colunas[0]
            p1 = (xi-30+primeira_coluna.ni.x*m, 100-primeira_coluna.ni.y*m)
            p2 = (xi-30+primeira_coluna.nf.x*m, 100-primeira_coluna.nf.y*m)  
            p1a = (p1[0]+15, p1[1])
            p1b = (p1[0]-5,  p1[1])
            p2a = (p2[0]+15, p2[1])
            p2b = (p2[0]-5,  p2[1])
            can.create_line(p1,  p2,  fill="blue",width=1)
            can.create_line(p1a, p1b, fill="blue",width=1)
            can.create_line(p2a, p2b, fill="blue",width=1)
            can.create_text(xi-40, (p1[1]+p2[1])/2.0, font="Times 9", text=self.text_pe_direito.get(), fill="blue")

            # cota da cumeeira
            p1 = (xi, p2[1]-25)
            p5 = (xi+(cumeeira)*m, p2[1]-25)
            
            p1a = (xi, p2[1]-5)
            p1b = (xi, p2[1]-35)
            p5a = (xi+(cumeeira)*m, p2[1]-20)
            p5b = (xi+(cumeeira)*m, p2[1]-35)
            
            can.create_line(p1,  p5,  fill="blue",width=1)
            can.create_line(p1a,  p1b,  fill="blue",width=1)
            can.create_line(p5a,  p5b,  fill="blue",width=1)
            can.create_text(xi+(cumeeira*3)*0.5, p2[1]-35, font="Times 9",
                            text="cumeeira", fill="blue")

        # cota dos vaos
        oitao = 0
        for vao in lista_vaos:
            p1 = (xi+oitao*m, 120)
            oitao += vao
            p2 = (xi+oitao*m, 120)

            p1a = (p1[0], p1[1]-10)
            p1b = (p1[0], p1[1]+5)
            
            p2a = (p2[0], p2[1]-10)
            p2b = (p2[0], p2[1]+5)

            can.create_line(p1,  p2,  fill="blue",width=1)
            can.create_line(p1a,  p1b,  fill="blue",width=1)        
            can.create_line(p2a,  p2b,  fill="blue",width=1)

            x = p1[0] + (p2[0] - p1[0])/2.0

            can.create_text(x, 130, font="Times 9",
                        text=str(vao), fill="blue")



    def InserirLabelEEntry(self, nome, unidade, linha, coluna, largura, valor_default, container):
        label_cp = Label(container, text=nome, height=1, anchor=E, justify=LEFT)
        # label_cp.grid(row=linha, column=coluna)
        label_cp.grid(row=linha, column=coluna, sticky=W)

        label_cp = Label(container, text=unidade, height=1, anchor=E, justify=LEFT)
        label_cp.grid(row=linha, column=(coluna+2), sticky=W)
        
        text_entry = Entry(container, width=largura, justify='center')
        if type(valor_default) == type("string"):
            text_entry.insert(0, valor_default)

        elif type(valor_default) == StringVar:
            text_entry.config(textvariable=valor_default)
            # text_entry.insert(0, valor_default.get())

        else:
            text_entry.insert(0, str(round(float(valor_default),1)))

        text_entry.grid(row=linha, column=(coluna+1), sticky=W)

        return text_entry


root = Tk()

interface = JanelaInicial(root)

# auxiliar.CentralizarJanela(interface)

root.mainloop()

x = input("nao tenho certeza pq isso")