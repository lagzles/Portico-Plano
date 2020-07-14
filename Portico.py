# -*- coding: utf-8 -*-
import Nos as ns
import Barras as br
import numpy as np
from metodos_numericos import *
from math import sin
import desenhar as dwg

# TODO metodo de verificação das barras em ELU e ELS
# TODO metodo de desenho para reações
# TODO metodo de desenho de corte

class Portico(object):
			
	def __init__(self, lista_vaos, pe_direito, cumeeira, inclinacao, influencia):
		# lista_vaos = [22]
		# pe_direito = 12.5
		# cumeeira = 22
		# inclinacao = 3.0 / 100.
		quantidade_porticos = 1
		self.lista_vaos = lista_vaos
		self.pe_direito = pe_direito
		self.inclinacao = inclinacao
		self.influencia = influencia
		self.cumeeira = cumeeira
		self.lista_nos = []
		self.lista_barras = []
		self.lista_vigas = []
		self.lista_colunas = []
		self.lista_bases = []
		self.gdl = 0

		self.carregamentos = []
		self.carregamentosELU = []
		self.carregamentosELS = []

		self.ap = []
		self.liv = []
		self.k = []
		self.ua = []

		print('vaos', lista_vaos)
		print('cumeeira', cumeeira)
		# print('inclinacao', inclinacao)

		self.GerarBarrasEPontos()
		self.GerarDesenhoDXF()


	def SetarCarregamentos(self, carregamentos):
		self.carregamentos = carregamentos
    		

	def AnaliseMatricial(self):
		print('#'*20)
		print()
		print('Fazendo analise\n')
		self.MontarMatrizRigidez()
		self.ua = {}
		oitao = sum(self.lista_vaos)
		for barra in self.lista_barras:
			barra.fboi = {}
			# barra.compressao = {}
			barra.normal = {}
			barra.cortante_inicio = {}
			barra.momento_inicio = {}
			barra.cortante_final = {}
			barra.momento_final = {}
		
		# carregamentos:  permanente, sobrecargas e vento
		for tipoCarr, carregamento in self.carregamentos:
			fa = np.zeros((len(self.liv)))
			fo = np.zeros((self.gdl))
			# fo1 = np.zeros((self.gdl))
			for barra in self.lista_barras:
				if barra.tipo == 'viga':
					yi = barra.ni.y
					yf = barra.nf.y
					if tipoCarr == 'pp':
						barra.set_peso()
						carr = - barra.peso_linear
					elif (yi-yf) < 0: # vigas da agua da esquerda
						carr = carregamento[0]
					else: # vigas da agua da direita
						carr = carregamento[1]

				elif barra.tipo == 'coluna-externa':
					colunaX = barra.ni.x
					if tipoCarr == 'pp':
						carr = 0
					elif colunaX == 0: # coluna externa da esquerda
						carr = carregamento[2]
					else: # coluna externa da direita
						carr = carregamento[3]

				else: # colunas internas
					carr = 0
				
				mz = (carr * (barra.comprimento() ** 2) ) / 12.
				fy = (carr * barra.comprimento() ) / 2.
				fx = 0*fy * round(sin(barra.theta),4)

				# esforços nodais no sistema local da barra
				fboi = np.zeros((6))
				fboi[0] = round(fx,2)
				fboi[1] = round(fy,2)
				fboi[2] = round(mz,2)
				fboi[3] = round(fx,2)
				fboi[4] = round(fy,2)
				fboi[5] = round(-mz,2)

				barra.fboi[tipoCarr] = fboi

				# foi = np.dot(np.dot(np.transpose(barra.ti), fboi), barra.ti)
				ti_transposta = np.transpose(barra.ti)
				foi = np.dot(ti_transposta, fboi)

				li_transposta = np.transpose(barra.li)
				fci = np.dot(li_transposta, foi)

				fo = fo + fci

			ap = self.ap
			liv = self.liv
			k = self.k

			# print(ka)
			foa = np.delete(fo, ap, axis=0)
			fca = fa - foa
			
			ka = np.delete(np.delete(k, ap, axis=0), ap, axis=1)
			kb = np.delete(np.delete(k, liv, axis=0), ap, axis=1)

			det = np.linalg.det(ka)
			
			if det == 0:
				print('Determinante de Ka = 0, matriz singular. Não pode')
				break
			ka_inv = np.linalg.inv(ka)


			# deslocamentos nós livres
			ua = np.dot(ka_inv, fca)
			fb = np.dot(kb, ua)

			self.ua[tipoCarr] = ua

			grausReacoes = len(fb)

			for barra in self.lista_barras:
				barra.esforcos_nodais(tipoCarr,[ua], liv, fo)

			for i in range(0,grausReacoes):
				grauApoio = ap[i]
				reacao = fb[i]

				for base in self.lista_bases:
					baseGdlX = base.gx - 1
					baseGdlY = base.gy - 1
					baseGdlZ = base.gz - 1
					# print(baseGdlX, gdlX)
					baseApoio = base.apoio
					if baseApoio == "engaste":
						if(baseGdlX == grauApoio):
							# base.rx = reacao
							base.rx[tipoCarr] = reacao + fo[baseGdlX]
						if(baseGdlY == grauApoio):
							# base.ry = reacao
							base.ry[tipoCarr] = reacao + fo[baseGdlY]
						if(baseGdlZ == grauApoio):
							# base.mz = reacao
							base.mz[tipoCarr] = reacao + fo[baseGdlZ]
					elif baseApoio == "bi-articulado":
						base.mz[tipoCarr] = 0.0 + fo[baseGdlZ]
						base.rx[tipoCarr] = 0.0 + fo[baseGdlX]
						if(baseGdlY == grauApoio):
    							# base.ry = reacao
							base.ry[tipoCarr] = reacao + fo[baseGdlY]

		print('\nReações de APOIO')
		print('Car	RX	RY	RMZ')
		for no in self.lista_bases:
			# print(base)
			no.printReacoes()
			print('#########################\n')
		print('\n')

	
	def MontarMatrizRigidez(self):
		# print('#'*20)
		# print()
		# print('Matriz de rigidez do portico')
		k = np.zeros((self.gdl, self.gdl))

		for barra in self.lista_barras:
			barra.set_gdl(self.gdl)
			k = k + barra.get_kci()
		
		liv = []
		ap = []
		for no in self.lista_nos:
			if no.apoio == False:
				liv = liv + [no.gx -1]
				liv = liv + [no.gy -1]
				liv = liv + [no.gz -1]

			else:
				if no.apoio == 'engaste':
					ap = ap + [no.gx -1]
					ap = ap + [no.gy -1]
					ap = ap + [no.gz -1]

				elif no.apoio == 'rotuladoInicial' or no.apoio == "rotuladoFinal":
					ap = ap + [no.gx - 1]
					ap = ap + [no.gy - 1]
					liv = liv + [no.gz - 1]

				elif no.apoio == 'bi-articulado':
					ap = ap + [no.gy - 1]
					liv = liv + [no.gx - 1]
					liv = liv + [no.gz - 1]

		self.liv = liv
		self.ap = ap
		self.k = k


	def GerarDesenhoDXF(self):
		barras = self.lista_barras
		dwg.desenhar_portico(self, 'portico.dxf')


	def GerarBarrasEPontos(self):
		n = len(self.lista_vaos)
		self.lista_colunas = []
		self.lista_vigas = []
		# numero de pilares
		np = n + 1

		# altura livre não eh altura abaixo da viga, isso esta errado
		altura_total = self.pe_direito
		cumeeira_alinhada = False
		inclinacao = self.inclinacao / 100.0

		# Pontos de cumeeira, abaixo e acima da viga, respectivamente
		h_cumeeira = altura_total + self.cumeeira * inclinacao

		# cota 'x' do ponto inicial até a cumeeira
		cumeeira = 0 + self.cumeeira
		largura = sum(self.lista_vaos) * 1

		########################################################################
		########################################################################
		cota = 0
		dx = 0

		oitao = 0
		for k in range(int(1)):
			pontos_base = []
			pontos_topo = []
			# incremento de distancia para cada portico
			pontos_base.append([0, 0])
			pontos_topo.append([0, altura_total]) ########3

			oitao = 0
			# loop que vai gradativamente definindo a largura do oitao
			# definindo os pontos de base e topo dos vãos
			for vao in self.lista_vaos:	
				oitao += vao
				# # caso a largura parcial do oitao seja menor que a dist. cumeeira
				if oitao < cumeeira:
					cota = altura_total + oitao*inclinacao
				
				elif oitao == cumeeira: # caso coincida com a posicao da cumeeira
					cota = h_cumeeira
					cumeeira_alinhada = True
					
				elif oitao > cumeeira: # caso o parcial do oitao seja maior que a cumeeira
					cota = h_cumeeira - (oitao - self.cumeeira)*inclinacao
					
				# caso a cumeeira esteja entre dois parciais do oitao
				if oitao > cumeeira > (oitao - vao):
					pontos_topo.append([self.cumeeira, h_cumeeira])
					# acrescenta o ponto de viga da cumeeira
				
				pontos_base.append([oitao, 0])
				pontos_topo.append([oitao, cota ])
				# após definido os pontos de cada parcial do oitao, se define os pontos das vigas

		# lançar nós e barras das vigas, no objeto Portico
		nof = None
		for p in range(len(pontos_topo)-1):
			pontoi = pontos_topo[p]
			pontof = pontos_topo[p+1]
			vao = pontof[0] - pontoi[0]
			cota = pontof[1]
			if p == 0:
				gdl = self.gdl
				noi = ns.Nos(pontoi[0], pontoi[1], gdl +1, gdl + 2, gdl + 3, False)
				self.gdl += 3
				self.lista_nos.append(noi)
			else:
				noi = nof

			nof = self.PontosIntermediariosDaViga(noi, vao, cota)


		# lançar nós das bases e barras das colunas, no objeto Portico
		for ponto in pontos_base:
			x = ponto[0]
			y = ponto[1]
			gdl = self.gdl
			
			coluna = 'coluna'
			pontoIndex = pontos_base.index(ponto)
			altura_alvenaria = 3

			# ponto inicial tera propriedade apoio diferente de False
			if pontoIndex == 0 or pontoIndex == (len(pontos_base)-1):
				# print('e')
				apoio = 'engaste'
				coluna = 'coluna-externa'
			else:
				# print('r')
				# apoio = 'rotuladoInicial'
				# apoio = 'rotuladoFinal'
				apoio = 'bi-articulado'

			gx = gdl + 1
			gy = gdl + 2
			gz = gdl + 3
			self.gdl += 3

			nob = ns.Nos(x, y, gx, gy, gz, apoio)
			self.lista_nos.append(nob)

			for no in self.lista_nos:
				if no.x == nob.x and no.y != 0:
					barraId = len(self.lista_barras)+1
					# no.apoio = 'topo'
					dy = abs(no.y - nob.y)
					if coluna == 'bi-articulado':
						kx = 1
						ky = 1
					else:
						kx = 1
						ky = altura_alvenaria / dy
					coluna = br.Barras(nob, no, barraId, kx, ky, coluna, self)
					self.lista_barras.append(coluna)
					self.lista_colunas.append(coluna)
					self.lista_bases.append(nob)


	def PontosIntermediariosDaViga(self, noi, vao, cota):
		# no2
		xb = noi.x
		yb = noi.y
		
		# no4
		xt = xb + vao
		yt = cota

		# divisão padrão do vão em 3 partes
		n = 3
		if (xt-xb) < 8.000: # caso tenha um 'vao' menor que 8m, não dividir
			n = 1
			# situacao mais comum quando cumeeira esta no meio do vao
		if n != 1:
			dx = (xt-xb) / n
			dy = (yt-yb) / n

			ptFim = None #ns.Nos(xb+dx, yb+dy, gdl+1, gdl+2, gdl+3, 0, 0, 0,False)
			# para divisao padrao do vao, em 3 partes
			for j in range(0, n):
				if j == 0:
					ptInicio = noi
				else:
					ptInicio = ptFim

				gdl = self.gdl
				ptFim = ns.Nos(xb+dx*(j+1), yb+dy*(j+1), gdl+1, gdl+2, gdl+3,False)
				self.gdl += 3
				
				barra_id = len(self.lista_barras) + 1
				barraIntermediaria = br.Barras(ptInicio, ptFim, barra_id, 1, 2.2/dx, 'viga', self)

				self.lista_barras.append(barraIntermediaria)
				self.lista_vigas.append(barraIntermediaria)
				self.lista_nos.append(ptFim)
				
		elif n == 1:
			ptInicio = noi
			gdl = self.gdl
			ptFim = ns.Nos(xt, yt, gdl+1, gdl+2, gdl+3, False)
			self.gdl += 3

			barra_id = len(self.lista_barras) + 1
			barraIntermediaria = br.Barras(ptInicio, ptFim, barra_id, 1, 2.2/vao, 'viga')

			self.lista_barras.append(barraIntermediaria)
			self.lista_vigas.append(barraIntermediaria)
			self.lista_nos.append(ptFim)

		return ptFim

	########################################################################33
	########################################################################33
	########################################################################33
	########################################################################33
	########################################################################33
	########################################################################33

	def verificar_vigas(self):
		lista_esp = [3.75, 4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		for barra in self.lista_vigas:
			print()
			barra.set_combinacoes_esforcos()
			barra.verificar()

			momento_maior = max(barra.elu_msdi, barra.elu_msdf)
			# section_mais_solicitada
			local = 'inicio'

			if momento_maior == barra.elu_msdi:
				local = 'inicio'
			else:
				local = 'final'

			dicionario_pesos = {}
			lista_pesos = []
			contador  = 0

			for tw in [3.75, 4.75, 6.35, 7.92]:
				for alma in lista_almas:
					for tf in lista_esp:
						for bf in lista_mesa:
							bool1 = tw < 6.0 and alma > 600
							bool2 = tf < 9.1 and bf > 200
							bool22 = tf < 6 and bf > 175
							bool3 = tw > 8.0 and alma < 1050
							bool4 = tf < tw or tf > 3*tw
							bool5 = bf > alma

							if contador > 30:
								break

							limitacoes = max([bool1, bool2, bool22, bool3, bool4, bool5])

							if not limitacoes:
								dicionario ={
									'd': alma/1000,
									'tw': tw/1000,
									'bf': bf/1000,
									'tf': tf/1000,
									'tipo': 'soldado'
								}
								
								barra.set_section_inicio(dicionario)
								barra.set_section_final(dicionario)
								barra.verificar()

								ratio = max(barra.ratio_inicio, barra.ratio_final)

								if ratio < 1.01:
									peso_linear = barra.section_inicio.set_peso_linear()
									dicionario_pesos[peso_linear] = dicionario
									lista_pesos.append(peso_linear)
									contador += 1

			menor_peso = min(lista_pesos)

			if local == 'inicio':
				barra.set_section_inicio(dicionario_pesos[menor_peso])
				barra.verificar_secao_inicio()
			else:
				barra.set_section_final(dicionario_pesos[menor_peso])
				barra.verificar_secao_final()

			dicionario = dicionario_pesos[menor_peso]

			d = dicionario['d']
			tw = dicionario['tw']
			bf = dicionario['bf']
			tf = dicionario['tf']

			for alma in lista_almas:
				dicionario ={
					'd': alma/1000,
					'tw': tw,
					'bf': bf,
					'tf': tf,
					'tipo': 'soldado'
				}
				if local == 'final':
					barra.set_section_inicio(dicionario)
					barra.verificar_secao_inicio()
					if barra.ratio_inicio < 1.01:
						break
				else:
					barra.set_section_final(dicionario)
					barra.verificar_secao_final()
					if barra.ratio_final < 1.01:
						break

		print()
		for viga in self.lista_vigas:
			print(viga.id, viga.comprimento())
			print(viga.section_inicio, viga.elu_msdi)
			print(viga.section_final, viga.elu_msdf)
			print('cortantes ',viga.elu_vsdi, viga.elu_vsdf)
			print('viga carregamento elu', viga.carregamento_elu)
			print('-')



