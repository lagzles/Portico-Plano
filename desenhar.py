from dxfwrite import DXFEngine as dxf

def desenhar_portico(portico, filename):
    dwg = dxf.drawing(filename)

    for barra in portico.lista_barras:
        pi = [barra.ni.x*1, barra.ni.y*1]
        pf = [barra.nf.x*1, barra.nf.y*1]
        desenhar_linhas(dwg, pi, pf)
    
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


def desenhar_diagonais(dwg, ponto_i, ponto_f):
    line = dxf.line(start=ponto_i, end=ponto_f)
    line['layer'] = 'DIMENSIONS'
    line['color'] = '2'
    dwg.add(line)
    # dwg.save()

