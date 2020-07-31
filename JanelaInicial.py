from tkinter import Tk
from tkinter import messagebox, Label, Button, Text, Frame, StringVar, IntVar, OptionMenu, Entry, Canvas, Checkbutton, LEFT,W, E
import os
import auxiliar
from Portico import *
from JanelaAnalisar import *

import time
 

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
        self.pilar_metalico.set(1)
        
        self.duas_aguas = IntVar()
        self.duas_aguas.set(1)

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
        self.text_sc = self.InserirLabelEEntry('Sobrecarga Norma =',
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
                                                '[m]', linha,coluna,largura,"25 25",
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
                                                    '[m]', linha,coluna,largura, "25.0",
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
                                    variable=self.pilar_metalico,
                                    command=self.canvas_cobertura)
        self.check_pilar_metalico.grid(row=linha, column=1, sticky=W)
        self.check_pilar_metalico.bind("<FocusOut>", lambda x: self.canvas_cobertura())

        
        linha += 1
        self.check_duas_aguas = Checkbutton(self.container_esquerdo,
                                    text="Duas Aguas (?)",
                                    variable=self.duas_aguas,
                                    command=self.canvas_cobertura)
        self.check_duas_aguas.grid(row=linha, column=1, sticky=W)
        self.check_duas_aguas.bind("<FocusOut>", lambda x: self.canvas_cobertura())

        self.label_vazio4 = Label(self.container_direito, text='\t', height=1)
        # self.label_vazio4.grid(row=4, column=1)
        self.label_vazio4.grid(row=4, column=1, sticky=W)

        self.canvas_cobertura()

        self.button_analisar = Button(self.container_inferior, text="Analisar Pórtico", command=self.analisar_portico)
        self.button_analisar.config(width=32)
        self.button_analisar.pack(side=LEFT)

        self.button_otimizar = Button(self.container_inferior, text="1 Verificação Pórtico", command=lambda :self.otimizar_portico(1))
        self.button_otimizar.config(width=32)
        self.button_otimizar.pack(side=LEFT)

        self.button_otimizar = Button(self.container_inferior, text="10 Verificações Pórtico", command=lambda :self.otimizar_portico(10))
        self.button_otimizar.config(width=32)
        self.button_otimizar.pack(side=LEFT)


    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    def pegar_vaos(self):
        lista_vaos1 = self.text_vaos.get().split(" ")
        lista_vaos = []
        largura = 0
        for vao in lista_vaos1:
            if len(vao) != 0:
                lista_vaos.append(float(vao))
                largura += float(vao)
        return lista_vaos, largura
    #####################################################################################################
    #####################################################################################################
    #####################################################################################################
    def analisar_portico(self):
        print('Analisar')
        lista_vaos, largura = self.pegar_vaos()

        duas_aguas = self.duas_aguas.get()
        if duas_aguas == 1:
            cumeeira = float(self.text_cumeeira.get())
        else:
            cumeeira = largura
        pe_direito = float(self.text_pe_direito.get())
        inclinacao = float(self.text_inclinacao.get())
        influencia = float(self.text_largura_inf.get())
        altura_minima = float(self.text_altura_minima.get())

        pilar_metalico = True
        if self.pilar_metalico.get() == 0:
            pilar_metalico = False
        
        print("Criando Portico")
        portico = Portico(lista_vaos, pe_direito, cumeeira, inclinacao, influencia, altura_minima, pilar_metalico)

        print("Criando Carregamentos")
        carregamentos = self.FazerCarregamentosParaPortico()

        portico.SetarCarregamentos(carregamentos)

        print("Começando Pré-Analise")
        portico.AnaliseMatricial()
        
        root2 = Tk()
        janelaAnalisar = JanelaAnalisar(root2, portico)



    def otimizar_portico(self, iteracoes):
        print('Otimizar')
        lista_vaos, largura = self.pegar_vaos()

        duas_aguas = self.duas_aguas.get()
        if duas_aguas == 1:
            cumeeira = float(self.text_cumeeira.get())
        else:
            cumeeira = largura
        pe_direito = float(self.text_pe_direito.get())
        inclinacao = float(self.text_inclinacao.get())
        influencia = float(self.text_largura_inf.get())
        altura_minima = float(self.text_altura_minima.get())

        pilar_metalico = True
        if self.pilar_metalico.get() == 0:
            pilar_metalico = False
        
        print("Criando Portico")
        portico = Portico(lista_vaos, pe_direito, cumeeira, inclinacao, influencia, altura_minima, pilar_metalico)

        print("Criando Carregamentos")
        carregamentos = self.FazerCarregamentosParaPortico()

        portico.SetarCarregamentos(carregamentos)

        messagebox.showinfo("AVISO AOS INTERESSADOS", """
O programa fara uma pré-verificação das vigas e pilares do pórtico. Esta verificação pode levar alguns de segundos até 1, ou 2 minutos dependendo da quantidade de vãos do pórtico.
O tempo estimado de analise é de 21 segundos para cada vão por iteração.

A analise começara assim que pressionares 'OK'""")

        print("Começando Pré-Analise")
        agora = time.time()
        portico.AnaliseMatricial()
        portico.OtimizarColunas()
        portico.OtimizarVigas()
        
        iterr = 0
        peso_i = 0
        peso_f = portico.SetarPeso()
        while ((peso_f != peso_i) and iterr < iteracoes): ##iterr < 9:# (peso_f != peso_i): ##
            peso_i = peso_f

            portico.AnaliseMatricial()
            portico.OtimizarColunas()
            portico.OtimizarVigas()
            portico.AnaliseMatricial()
            for barra in portico.lista_barras:
                barra.verificar_elu()
                barra.verificar_els()

            iterr += 1
            peso_f = portico.SetarPeso()
        print(time.time() - agora, 'segundos de analise')
        root2 = Tk()
        janelaAnalisar = JanelaAnalisar(root2, portico)
    
        
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

        duas_aguas = self.duas_aguas.get()
        if duas_aguas == 1:
            cumeeira = float(self.text_cumeeira.get())
        else:
            cumeeira = largura
        pe_direito = float(self.text_pe_direito.get())
        inclinacao = float(self.text_inclinacao.get())

        pilar_metalico = True
        if self.pilar_metalico.get() == 0:
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
            if pilar_metalico:
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
            else:
                p2 = (xi-30, 100-pe_direito*m)

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

            # horizontal
            can.create_line(p1,  p2,  fill="blue",width=1)
            # vertical esquerda
            can.create_line(p1a,  p1b,  fill="blue",width=1)
            # vertical direita
            can.create_line(p2a,  p2b,  fill="blue",width=1)

            x = p1[0] + (p2[0] - p1[0])/2.0

            can.create_text(x, 130, font="Times 9",
                        text=str(vao), fill="blue")
        
        for base in portico_canvas.lista_bases:
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


    

    def FazerCarregamentosParaPortico(self):
        cp = float(self.text_cp.get())
        sc = float(self.text_sc.get())
        su = float(self.text_su.get())
        cv = float(self.text_cv.get())
        
        if self.duas_aguas.get() == 1:
            duas_aguas = True
        else:
            duas_aguas = False

        influencia = float(self.text_largura_inf.get())
        if influencia > 14.0:
            influencia_fechamento = influencia/2.0
        else:
            influencia_fechamento = influencia

        cp_linear = cp * influencia 
        sc_linear = sc * influencia
        su_linear = su * influencia
        cv_linear = cv * influencia
        cv_fechamento = cv * influencia_fechamento


        carregamentos = []
        # carregamento = [tipo, [vertical agua esquerda, vertical agua direita, horizontal esquerda, horizontal direita]]
        carr0 = ['pp',   [  0,  0,  0,  0]] # valores serão setados na analise
        carr1 = ['cp',   [- cp_linear, -cp_linear,   0,  0]]
        carr2 = ['sc',   [-sc_linear, -sc_linear,   0,  0]]
        carr3 = ['su',   [-su_linear, -su_linear,   0,  0]]

        if duas_aguas:
            # carregamento de vento para cobertura 2 aguas
            carr4 = ['cv 0',      [ cv_linear,  cv_linear, cv_fechamento, -cv_fechamento]]
            carr5 = ['cv 90 i',   [ 0.53*cv_linear,  0.10*cv_linear, -1.00*cv_fechamento, -0.20*cv_fechamento]] # >
            carr6 = ['cv 90 ii',  [ 1.03*cv_linear,  0.60*cv_linear, -0.50*cv_fechamento, -0.70*cv_fechamento]] # >>
            carr7 = ['cv 270 i',  [ 0.10*cv_linear,  0.53*cv_linear, +0.20*cv_fechamento, +1.00*cv_fechamento]] # <
            carr8 = ['cv 270 ii', [ 0.60*cv_linear,  1.03*cv_linear, +0.70*cv_fechamento, +0.50*cv_fechamento]] # <<

        else:
            # carregamento de vento para cobertura 1 agua
            carr4 = ['cv 0',      [ 1.20*cv_linear,  1.20*cv_linear, cv_fechamento, -cv_fechamento]]
            carr5 = ['cv 90 i',   [ 0.70*cv_linear,  0.70*cv_linear, -1.00*cv_fechamento, -0.20*cv_fechamento]] # >
            carr6 = ['cv 90 ii',  [ 1.20*cv_linear,  1.20*cv_linear, -0.50*cv_fechamento, -0.70*cv_fechamento]] # >>
            carr7 = ['cv 270 i',  [ 0.70*cv_linear,  0.70*cv_linear, +0.20*cv_fechamento, +1.00*cv_fechamento]] # <
            carr8 = ['cv 270 ii', [ 1.20*cv_linear,  1.20*cv_linear, +0.70*cv_fechamento, +0.50*cv_fechamento]] # <<

        carregamentos.append(carr0)
        carregamentos.append(carr1)
        carregamentos.append(carr2)
        carregamentos.append(carr3)
        carregamentos.append(carr4)
        carregamentos.append(carr5)
        carregamentos.append(carr6)
        carregamentos.append(carr7)
        carregamentos.append(carr8)

        return carregamentos




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

    
