from dxfwrite import DXFEngine as dxf

def desenhar_portico(portico, filename):
    dwg = dxf.drawing(filename)

    for barra in portico.lista_barras:
        pi = [barra.ni.x*100, barra.ni.y*100]
        pf = [barra.nf.x*100, barra.nf.y*100]
        desenhar_linhas(dwg, pi, pf)

        adicionar_texto(dwg, pi, barra.ni.id, 20, 0)
        adicionar_texto(dwg, pf, barra.nf.id, 20, 0)

        pm = [(barra.ni.x + barra.nf.x)/2*100, (barra.ni.y + barra.nf.y)/2*100]
        adicionar_texto(dwg, pm, barra.id, 40, 45)

    
    if dwg != None:
        dwg.save()
    

def desenhar_linhas(dwg, ponto_i, ponto_f):
    line = dxf.line(start=ponto_i, end=ponto_f)
    line['layer'] = 'DIMENSIONS'
    line['color'] = '5'
    dwg.add(line)
    # dwg.save()


def desenhar_banzos(dwg, ponto_i, ponto_f):
    line = dxf.line(start=ponto_i, end=ponto_f)
    line['layer'] = 'DIMENSIONS'
    line['color'] = '4'
    dwg.add(line)
    # dwg.save()


def desenhar_montantes(dwg, ponto_i, ponto_f):
    line = dxf.line(start=ponto_i, end=ponto_f)
    line['layer'] = 'DIMENSIONS'
    line['color'] = '3'
    dwg.add(line)
    # dwg.save()


def adicionar_texto(dwg, ponto, texto, altura, rotacao):
    pc = (ponto[0], ponto[1])
    textDwg = dxf.text(texto, pc, height=altura, rotation=rotacao)
    dwg.add(textDwg)



def desenhar_diagonais(dwg, ponto_i, ponto_f):
    line = dxf.line(start=ponto_i, end=ponto_f)
    line['layer'] = 'DIMENSIONS'
    line['color'] = '2'
    dwg.add(line)
    # dwg.save()

