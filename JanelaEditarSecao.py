from tkinter import Label, Button, Entry, LEFT,W, E

janelaAnalise = None

####################################################################################
#  GUI Para alterar as seÃ§Ãµes das barras.
####################################################################################
class JanelaEditarSecao:

    def __init__(self, master, barra, JanelaAnalise):
        self.master = master
        master.title('Editar Barra')
        self.master.geometry("300x150")
        self.master.minsize(500,175)
        self.master.resizable(0,0)

        global janelaAnalise
        janelaAnalise = JanelaAnalise

        barra_id = barra.id
        conjunto_barras = [barra]

        secao_inicio = barra.section_inicio # perfil da barra
        secao_final = barra.section_final # perfil da barra

        # default -> 'soldado'
        entry_state = 'normal'
        option_state = 'disabled'

        # apresenta a ID da barra
        self.label_barra_id = Label(self.master, text='Barra {}'.format(barra_id))
        self.label_barra_id.grid(row=2, column=1)
        
        # apresenta a seÃ§Ã£o atual
        self.label_section_atual = Label(self.master, text='Seção Inicial')
        self.label_section_atual.grid(row=1, column=4)
        self.label_section_atual_ = Label(self.master, text=secao_inicio)
        self.label_section_atual_.grid(row=2, column=4)

        # ENTRY's para alterar seÃ§Ã£o da barra
        r = 3
        self.labe1 = Label(self.master, text='d  [mm]= ', height=1)
        self.labe1.grid(row=r, column=3)
        self.entry_d_inicio = Entry(self.master, width=15, state=entry_state, justify="center")
        self.entry_d_inicio.insert(0, str(barra.section_inicio.d*1000))
        self.entry_d_inicio.grid(row=r, column=4)
        r += 1
        self.labe1 = Label(self.master, text='tw [mm]= ', height=1)
        self.labe1.grid(row=r, column=3)
        self.entry_tw_inicio = Entry(self.master, width=15, state=entry_state, justify="center")
        self.entry_tw_inicio.insert(0, str(barra.section_inicio.tw*1000))
        self.entry_tw_inicio.grid(row=r, column=4)
        r += 1
        self.labe1 = Label(self.master, text='bf [mm]= ', height=1)
        self.labe1.grid(row=r, column=3)
        self.entry_bf_inicio = Entry(self.master, width=15, state=entry_state, justify="center")
        self.entry_bf_inicio.insert(0, str(barra.section_inicio.bfs*1000))
        self.entry_bf_inicio.grid(row=r, column=4)
        r += 1
        self.labe1 = Label(self.master, text='tf [mm]= ', height=1)
        self.labe1.grid(row=r, column=3)
        self.entry_tf_inicio = Entry(self.master, width=15, state=entry_state, justify="center")
        self.entry_tf_inicio.insert(0, str(barra.section_inicio.tfs*1000))
        self.entry_tf_inicio.grid(row=r, column=4)
        r += 1

        # apresenta a seÃ§Ã£o atual
        self.label_section_final = Label(self.master, text='Seção Final')
        self.label_section_final.grid(row=1, column=6)
        self.label_section_final_ = Label(self.master, text=secao_final)
        self.label_section_final_.grid(row=2, column=6)

        # ENTRY's para alterar seÃ§Ã£o da barra
        r = 3
        self.labe1 = Label(self.master, text='d  [mm]= ', height=1)
        self.labe1.grid(row=r, column=5)
        self.entry_d_final = Entry(self.master, width=15, state=entry_state, justify="center")
        self.entry_d_final.insert(0, str(barra.section_final.d*1000))
        self.entry_d_final.grid(row=r, column=6)
        r += 1
        self.labe1 = Label(self.master, text='tw [mm]= ', height=1)
        self.labe1.grid(row=r, column=5)
        self.entry_tw_final = Entry(self.master, width=15, state=entry_state, justify="center")
        self.entry_tw_final.insert(0, str(barra.section_final.tw*1000))
        self.entry_tw_final.grid(row=r, column=6)
        r += 1
        self.labe1 = Label(self.master, text='bf [mm]= ', height=1)
        self.labe1.grid(row=r, column=5)
        self.entry_bf_final = Entry(self.master, width=15, state=entry_state, justify="center")
        self.entry_bf_final.insert(0, str(barra.section_final.bfs*1000))
        self.entry_bf_final.grid(row=r, column=6)
        r += 1
        self.labe1 = Label(self.master, text='tf [mm]= ', height=1)
        self.labe1.grid(row=r, column=5)
        self.entry_tf_final = Entry(self.master, width=15, state=entry_state, justify="center")
        self.entry_tf_final.insert(0, str(barra.section_final.tfs*1000))
        self.entry_tf_final.grid(row=r, column=6)
        r += 1
        
        r = 2
        self.labe1 = Label(self.master, text='kx = ', height=1)
        self.labe1.grid(row=r, column=9)
        self.entry_kx = Entry(self.master, width=5)
        self.entry_kx.insert(0, str(barra.kx))
        self.entry_kx.grid(row=r, column=10)
        r += 1
        self.labe1 = Label(self.master, text='ky = ', height=1)
        self.labe1.grid(row=r, column=9)
        self.entry_ky = Entry(self.master, width=5)
        self.entry_ky.insert(0, str(barra.ky))
        self.entry_ky.grid(row=r, column=10)

        self.button_ok = Button(self.master, text='Ok', command=lambda :self.modificar_barra(conjunto_barras))
        self.button_ok.grid(row=7, column = 1)

        # self.button_deletar = Button(self.master, text='Deletar Barra', command=lambda :self.deletar_barra(barra_id))
        # self.button_deletar.grid(row=7, column = 3)
    def modificar_barra(self, barras):
        print('modificar barras')
        global janelaAnalise

        for barra in barras:
            d = float(self.entry_d_inicio.get()) /1000.0
            tw = float(self.entry_tw_inicio.get()) /1000.0
            bf = float(self.entry_bf_inicio.get()) /1000.0
            tf = float(self.entry_tf_inicio.get()) /1000.0 
            
            kx = float(self.entry_kx.get())
            ky = float(self.entry_ky.get())

            dicionario_inicio = {'tipo': 'soldado',
                        'd': d,
                        'tw': tw,
                        'bf': bf,
                        'tf': tf,
                        'kx': kx,
                        'ky': ky,
                        }
            
            d = float(self.entry_d_final.get()) /1000.0
            tw = float(self.entry_tw_final.get()) /1000.0
            bf = float(self.entry_bf_final.get()) /1000.0
            tf = float(self.entry_tf_final.get()) /1000.0 

            dicionario_final = {'tipo': 'soldado',
                        'd': d,
                        'tw': tw,
                        'bf': bf,
                        'tf': tf,
                        'kx': kx,
                        'ky': ky,
                        }

            barra.set_section(dicionario_inicio, dicionario_final, kx, ky)


        janelaAnalise.portico.AnaliseMatricial()
        for barra in janelaAnalise.portico.lista_barras:
            barra.verificar_elu()
            barra.verificar_els()

        janelaAnalise.mostrar_barras()
  
        print('...')
        self.master.destroy()

