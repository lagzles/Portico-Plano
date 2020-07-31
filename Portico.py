# -*- coding: utf-8 -*-
import Nos as ns
import Barras as br
import numpy as np
# from metodos_numericos import *
from math import sin
import desenhar as dwg

# TODO metodo de desenho para reações
# TODO metodo de desenho de corte

class Portico(object):
			
	def __init__(self, lista_vaos, pe_direito, cumeeira, inclinacao,
				influencia, altura_minima, pilar_metalico):
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
		self.altura_minima = altura_minima
		self.pilar_metalico = pilar_metalico
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
		# self.GerarDesenhoDXF()

	def SetarPeso(self):
		peso = 0
		for barra in self.lista_barras:
			peso += barra.set_peso()
		
		self.peso = peso
		return peso

	def SetarCarregamentos(self, carregamentos):
		self.carregamentos = carregamentos
    		

	def AnaliseMatricial(self):
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
					if tipoCarr == 'pp': # vigas da agua da esquerda
						barra.set_peso()
						carr = - barra.peso_linear

					elif (yi-yf) < 0: # vigas da agua da esquerda
						carr = carregamento[0]
					else: # vigas da agua da direita
						carr = carregamento[1]

				elif barra.tipo == 'coluna-externa':
					colunaX = barra.ni.x
					if colunaX == 0: # coluna externa da esquerda
						carr = carregamento[2]
					else: # coluna externa da direita
						carr = carregamento[3]

				else: # colunas internas
					carr = 0
				
				# aplicação do peso proprio nos pilares é feita de forma diferente
				# do que para carregamentos de vento
				if tipoCarr == 'pp' and barra.tipo != 'viga':
					barra.set_peso()
					carr = - barra.peso_linear
					mz = 0
					fy = 0
					fx = (carr * barra.comprimento() ) / 2.
				else:
					mz = (carr * (barra.comprimento() ** 2) ) / 12.
					fy = (carr * barra.comprimento() ) / 2.
					fx = 0

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

		for barra in self.lista_barras:
			barra.set_combinacoes_esforcos()
			barra.set_deformacoes_combinadas()
		
	
	def MontarMatrizRigidez(self):
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

				elif  no.apoio == 'rotulado':
					ap = ap + [no.gy - 1]
					ap = ap + [no.gx - 1]
					liv = liv + [no.gz - 1]

				elif no.apoio == 'bi-articulado' or no.apoio == 'simples':
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
				
				if self.pilar_metalico: # apoio para solução pilar metalico, na cota 0
					pontos_base.append([oitao, 0])
				else:# apoio para solução pilar concreto, no ponto da viga
					pontos_base.append([oitao, cota])
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
			# caso o portico seja pilar metalico.
			if self.pilar_metalico:
				gdl = self.gdl
				
				coluna = 'coluna'
				pontoIndex = pontos_base.index(ponto)
				altura_alvenaria = 3

				# ponto inicial tera propriedade apoio diferente de False
				if pontoIndex == 0 or pontoIndex == (len(pontos_base)-1):
					apoio = 'engaste'
					coluna = 'coluna-externa'
				else:
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
						if coluna == 'coluna':
							kx = 1
							ky = 1
						else:
							kx = 1
							ky = altura_alvenaria / dy
						coluna = br.Barras(nob, no, barraId, kx, ky, coluna, self)
						self.lista_barras.append(coluna)
						self.lista_colunas.append(coluna)
						self.lista_bases.append(nob)
			else: # pilar de concreto
				for no in self.lista_nos:
					if no.x == 0:
						no.apoio = 'rotulado'
						self.lista_bases.append(no)
					elif no.x == ponto[0]:
						no.apoio = 'simples'
						self.lista_bases.append(no)


	def PontosIntermediariosDaViga(self, noi, vao, cota):
		# no2
		xb = noi.x
		yb = noi.y
		
		# no4
		xt = xb + vao
		yt = cota

		# divisão padrão do vão em 3 partes
		n = 4
		if (xt-xb) < 6.000: # caso tenha um 'vao' menor que 6m, não dividir
			n = 1
			# situacao mais comum quando cumeeira esta no meio do vao
		elif (xt - xb) <= 10.0:
			n = 2
		elif 10 < (xt - xb) <= 22.0:
			n = 3	
		elif 22 < (xt - xb) < 30.0:
			n = 4	

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
			barraIntermediaria = br.Barras(ptInicio, ptFim, barra_id, 1, 2.2/vao, 'viga', self)

			self.lista_barras.append(barraIntermediaria)
			self.lista_vigas.append(barraIntermediaria)
			self.lista_nos.append(ptFim)

		return ptFim

	########################################################################33
	########################################################################33
	########################################################################33
	########################################################################33
	########################################################################33
################################################################################################
################################################################################################
################################################################################################

	def LocalDeMaiorMomento(self, barra):
		momento_maior = max(abs(barra.elu_msdi), abs(barra.elu_msdf))
		# section_mais_solicitada
		local = 'inicio'

		x_do_momento_maximo, momento_maximo = barra.x_do_momento_maximo()

		if momento_maior == abs(barra.elu_msdi):
			local = 'inicio'
			if 0 <= x_do_momento_maximo <= barra.comprimento():
				barra.elu_msdi = momento_maximo
				momento_maior = abs(momento_maximo)
			# barra.elu_msdi = momento_maior
		else:
			local = 'final'
			if 0 <= x_do_momento_maximo <= barra.comprimento():
				barra.elu_msdf = momento_maximo
				momento_maior = abs(momento_maximo)
			# barra.elu_msdf = momento_maior
		
		return local, momento_maior


	#################################################################################################################
	#################################################################################################################
	#################################################################################################################

	def OtimizarColunas(self):
		# print('go!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_barras = self.lista_colunas# + self.lista_vigas

		lista_els = {}
		lista_elu = {}

		# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
		if self.pilar_metalico:
			for barra in lista_barras:
				# barra.set_combinacoes_esforcos()
				barra.verificar_elu()
				lista_els[barra.id] = []
				lista_elu[barra.id] = []

				local, momento_maior = self.LocalDeMaiorMomento(barra)

				dicionario_pesos = {}
				lista_pesos = []
				contador  = 0

				for tw in [3.75, 4.75, 6.35, 7.92]:
					for tf in lista_esp:
						for alma in lista_almas:
							for bf in lista_mesa:
								if contador > 30:
									break
								bool0 = (tw < 4.0 and alma > 450) or (tw < 6.0 and tf > 6.5)
								bool1 = tw < 6.0 and alma > 600
								bool9 = tw > 6.0 and alma < 500
								bool5 = tw > 8.0 and alma < 1050
								bool4 = tf < 6 and bf >= 150
								bool2 = tf < 9.1 and bf > 200
								bool3 = tf < 12 and bf > 250
								bool10 = alma >= 1050 and bf >= 200

								bool6 = tf < tw or tf > 3*tw
								bool7 = bf > alma
								bool8 = tf < 4

								if barra.tipo == 'coluna':
									bool0 = (tw < 4.0 and alma > 450)
									bool6 = tf < tw or tf > 4*tw
									bool4 = False

								limitacoes = max([bool0, bool1, bool2, bool3, bool4, bool5, bool6, bool7, bool8, bool9, bool10])

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
									barra.verificar_elu()
									ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

									if ratio_elu < 0.99:
										lista_elu[barra.id].append(dicionario)
										contador += 1

			# segundo processo, dessas 30 secoes que atendem ELU, verificar quais atendem ELS
			for barra in lista_barras:
				dicionario_pesos = {}
				lista_els[barra.id] = []
				lista_pesos = []
				dicionario = {
					'd': 1050.0 / 1000.0,
					'tw': 6.35 / 1000.0,
					'bf': 225.0 / 1000.0,
					'tf': 12.70 / 1000.0,
					'tipo': 'soldado'
				}
				
				local, momento_maior = self.LocalDeMaiorMomento(barra)

				for secao in lista_elu[barra.id]:
					dicionario = {
						'd': secao['d'],
						'tw': secao['tw'],
						'bf': secao['bf'],
						'tf': secao['tf'],
						'tipo': 'soldado'
					}

					barra.set_section_inicio(dicionario)
					barra.set_section_final(dicionario)

					# self.AnaliseMatricial()
					ratio_els = barra.verificar_els()
					# self.LocalDeMaiorMomento(barra)

					if ratio_els < 1.0:
						lista_els[barra.id].append(secao)

				# if len(lista_els[barra.id]) > 0:
				if len(lista_elu[barra.id]) > 0:
					for secao in lista_els[barra.id]:
						dicionario = {
							'd': secao['d'],
							'tw': secao['tw'],
							'bf': secao['bf'],
							'tf': secao['tf'],
							'tipo': 'soldado'
						}

						barra.set_section_inicio(dicionario)
						peso_linear = barra.section_inicio.set_peso_linear()
						lista_pesos.append(peso_linear)
						dicionario_pesos[peso_linear] = dicionario
					
				if len(lista_pesos) >= 1:
					menor_peso = 500
					for peso in lista_pesos:
						menor_peso = min(menor_peso, peso)
					
					dicionario = dicionario_pesos[menor_peso]
				
				barra.set_section_inicio(dicionario)
				barra.set_section_final(dicionario)
				barra.verificar_elu()
							
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
					if (alma/1000.0) >= (d*0.65):
						if local == 'final':
							barra.set_section_inicio(dicionario)
							barra.verificar_secao_inicio_elu()
							if barra.ratio_inicio_elu < 0.99:
								break
						else:
							barra.set_section_final(dicionario)
							barra.verificar_secao_final_elu()
							if barra.ratio_final_elu < 0.99:
								break

################################################################################################
################################################################################################

#####################################################################################
######################################################################################
######################################################################################


	def OtimizarVigas(self):
		# print('go!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_apoios_cumeeira = [0.0,self.cumeeira]
		oitao = 0
		for vao in self.lista_vaos:
			oitao += vao
			lista_apoios_cumeeira.append(oitao)

		lista_barras = self.lista_vigas

		lista_els = {}
		lista_elu = {}

		# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
		for barra in lista_barras:
			# barra.set_combinacoes_esforcos()
			barra.verificar_elu()
			lista_els[barra.id] = []
			lista_elu[barra.id] = []


			local, momento_maior = self.LocalDeMaiorMomento(barra)

			dicionario_pesos = {}
			lista_pesos = []
			contador  = 0

			for tw in [3.75, 4.75, 6.35, 7.92]:
				for tf in lista_esp:
					for alma in lista_almas:
						for bf in lista_mesa:
							if contador > 50:
								break
							bool0 = (tw < 4.0 and alma > 450) or (tw < 6.0 and tf > 6.5)
							bool1 = tw < 6.0 and alma > 600
							bool9 = tw > 6.0 and alma < 500
							bool5 = tw > 8.0 and alma < 1050
							bool4 = tf < 6 and bf >= 150
							bool2 = tf < 9.1 and bf > 200
							bool3 = tf < 12 and bf > 250
							bool10 = alma >= 1050 and bf >= 200
							bool11 = alma < self.altura_minima and (barra.ni.x in lista_apoios_cumeeira or barra.nf.x in lista_apoios_cumeeira)

							bool6 = tf < tw or tf > 3*tw
							bool7 = bf > alma
							bool8 = tf < 4

							limitacoes = max([bool0, bool1, bool2, bool3, bool4,
											 bool5, bool6, bool7, bool8, bool9, 
											 bool10, bool11])

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
								barra.verificar_elu()
								ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

								if ratio_elu < 0.9:
									lista_elu[barra.id].append(dicionario)
									contador += 1

		# segundo processo, dessas 30 secoes que atendem ELU, verificar quais atendem ELS
		for barra in lista_barras:
			dicionario_pesos = {}
			lista_els[barra.id] = []
			lista_pesos = []
			dicionario = {
				'd': 1050.0 / 1000.0,
				'tw': 6.35 / 1000.0,
				'bf': 225.0 / 1000.0,
				'tf': 12.70 / 1000.0,
				'tipo': 'soldado'
			}

			local, momento_maior = self.LocalDeMaiorMomento(barra)

			for secao in lista_elu[barra.id]:
				dicionario = secao # {

				barra.set_section_inicio(dicionario)
				barra.set_section_final(dicionario)

				self.AnaliseMatricial()
				ratio_els = barra.verificar_els()
				self.LocalDeMaiorMomento(barra)

				if ratio_els < 0.95:
					lista_els[barra.id].append(dicionario)

			if len(lista_els[barra.id]) > 0:
			# if len(lista_els[barra.id]) > 0:
				for secao in lista_els[barra.id]:
					dicionario = secao # {

					barra.set_section_inicio(dicionario)

					peso_linear = barra.section_inicio.set_peso_linear()
					lista_pesos.append(peso_linear)
					dicionario_pesos[peso_linear] = dicionario
				
			if len(lista_pesos) >= 1:
				menor_peso = 500
				for peso in lista_pesos:
					menor_peso = min(menor_peso, peso)
				
				dicionario = dicionario_pesos[menor_peso]
			
			barra.set_section_inicio(dicionario)
			barra.set_section_final(dicionario)
			barra.verificar_elu()
    					
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
				condicao_viga = True
				if (alma/1000.0) >= (d*0.7):# and alma < self.altura_minima:
					if local == 'final':
						if (barra.ni.x in lista_apoios_cumeeira):
							condicao_viga = alma >= self.altura_minima
						else:
							condicao_viga = True

						if condicao_viga:
							barra.set_section_inicio(dicionario)
							barra.verificar_secao_inicio_elu()
							if barra.ratio_inicio_elu < 0.9:
								break
					else:
						if (barra.nf.x in lista_apoios_cumeeira):
							condicao_viga = alma >= self.altura_minima
						else:
							condicao_viga = True

						if condicao_viga:
							barra.set_section_final(dicionario)
							barra.verificar_secao_final_elu()
							if barra.ratio_final_elu < 0.9:
								break


















	########################################################################33

	def OtimizarBarras(self):
		# print('go!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_apoios_cumeeira = [0.0,self.cumeeira]
		oitao = 0
		for vao in self.lista_vaos:
			oitao += vao
			lista_apoios_cumeeira.append(oitao)

		if self.pilar_metalico:
			lista_barras = self.lista_vigas + self.lista_colunas
		else:
			lista_barras = self.lista_vigas
    			
		lista_els = {}
		lista_elu = {}

		# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
		for barra in lista_barras:
			# barra.set_combinacoes_esforcos()
			barra.verificar_elu()
			lista_els[barra.id] = []
			lista_elu[barra.id] = []

			local, momento_maior = self.LocalDeMaiorMomento(barra)

			dicionario_pesos = {}
			lista_pesos = []
			contador  = 0

			for tw in [3.75, 4.75, 6.35, 7.92]:
				for alma in lista_almas:
					for tf in lista_esp:
						for bf in lista_mesa:
							if contador > 50:
								break
							bool0 = (tw < 4.0 and alma > 450) or (tw < 6.0 and tf > 6.5)
							bool1 = tw < 6.0 and alma > 600
							bool9 = tw > 6.0 and alma < 500
							bool5 = tw > 8.0 and alma < 1050
							bool4 = tf < 6 and bf >= 150
							bool2 = tf < 9.1 and bf > 200
							bool3 = tf < 12 and bf > 250
							bool10 = alma >= 1050 and bf >= 200
							bool11 = alma < self.altura_minima and (barra.ni.x in lista_apoios_cumeeira or barra.nf.x in lista_apoios_cumeeira)

							bool6 = tf < tw or tf > 3*tw
							bool7 = bf > alma
							bool8 = tf < 4

							if barra.tipo == 'coluna':
								bool0 = (tw < 4.0 and alma > 450)
								bool6 = tf < tw or tf > 4*tw
								bool4 = False

							limitacoes = max([bool0, bool1, bool2, bool3, bool4,
											bool5, bool6, bool7, bool8, bool9,
											bool10, bool11])

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
								barra.verificar_elu()
								ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

								if ratio_elu < 0.99:
									lista_elu[barra.id].append(dicionario)
									contador += 1

		# segundo processo, dessas 30 secoes que atendem ELU, verificar quais atendem ELS
		for barra in lista_barras:
			dicionario_pesos = {}
			lista_els[barra.id] = []
			lista_pesos = []
			dicionario = {
				'd': 1050.0 / 1000.0,
				'tw': 6.35 / 1000.0,
				'bf': 225.0 / 1000.0,
				'tf': 12.70 / 1000.0,
				'tipo': 'soldado'
			}

			local, momento_maior = self.LocalDeMaiorMomento(barra)

			for secao in lista_elu[barra.id]:
				dicionario = {
					'd': secao['d'],
					'tw': secao['tw'],
					'bf': secao['bf'],
					'tf': secao['tf'],
					'tipo': 'soldado'
				}

				barra.set_section_inicio(dicionario)
				barra.set_section_final(dicionario)

				self.AnaliseMatricial()
				ratio_els = barra.verificar_els()
				self.LocalDeMaiorMomento(barra)

				if ratio_els < 1.0:
					lista_els[barra.id].append(secao)

			if len(lista_els[barra.id]) > 0:
				for secao in lista_els[barra.id]:
					dicionario = {
						'd': secao['d'],
						'tw': secao['tw'],
						'bf': secao['bf'],
						'tf': secao['tf'],
						'tipo': 'soldado'
					}
					barra.set_section_inicio(dicionario)
					barra.set_section_final(dicionario)
					barra.verificar_elu()
					ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

					if ratio_elu < 1.00:
						peso_linear = barra.section_inicio.set_peso_linear()
						lista_pesos.append(peso_linear)
						dicionario_pesos[peso_linear] = dicionario
				
			if len(lista_pesos) >= 1:
				menor_peso = 500
				for peso in lista_pesos:
					menor_peso = min(menor_peso, peso)
				
				dicionario = dicionario_pesos[menor_peso]
			
			barra.set_section_inicio(dicionario)
			barra.set_section_final(dicionario)
			barra.verificar_elu()
    					
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
				condicao_viga = True
				if alma/1000.0 >= d * 0.6:
					if local == 'final':
						if barra.tipo == 'viga':
							if (barra.ni.x in lista_apoios_cumeeira):
								condicao_viga = alma >= self.altura_minima
							else:
								condicao_viga = True

						if condicao_viga:
							barra.set_section_inicio(dicionario)
							barra.verificar_secao_inicio_elu()
							if barra.ratio_inicio_elu < 0.99:
								break
					else:
						if barra.tipo == 'viga':
							if (barra.nf.x in lista_apoios_cumeeira):
								condicao_viga = alma >= self.altura_minima
							else:
								condicao_viga = True

						if condicao_viga:
							barra.set_section_final(dicionario)
							barra.verificar_secao_final_elu()
							if barra.ratio_final_elu < 0.99:
								break


#############################################################################
#############################################################################
#############################################################################






















	# def PegarVigasELU_ELS(self):
	# 	# print('go vigas elu e els!')
	# 	lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
	# 	lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
	# 	lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
	# 	lista_barras =  self.lista_vigas

	# 	lista_apoios_cumeeira = [0.0,self.cumeeira]
	# 	oitao = 0
	# 	for vao in self.lista_vaos:
	# 		oitao += vao
	# 		lista_apoios_cumeeira.append(oitao)

	# 	lista_els = {}
	# 	lista_elu = {}

	# 	# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
	# 	for barra in lista_barras:
	# 		barra.verificar_elu()
	# 		barra.lista_elu = []
	# 	for tw in [3.75, 4.75, 6.35, 7.92]:
	# 		# print('tw da viga elu els', tw)
	# 		for tf in lista_esp:
	# 			for alma in lista_almas:
	# 				for bf in lista_mesa:
	# 					bool0 = (tw < 4.0 and alma > 450) or (tw < 6.0 and tf > 6.5)
	# 					bool1 = tw < 6.0 and alma > 600
	# 					bool9 = tw > 6.0 and alma < 500
	# 					bool5 = tw > 7.0 and alma < 1050
	# 					bool4 =  tf < 6 and bf >= 150
	# 					bool2 = tf < 9.1 and bf > 200
	# 					bool3 = tf < 12 and bf > 250
	# 					bool10 = alma >= 1050 and bf >= 200
	# 					bool11 = alma < self.altura_minima

	# 					bool6 = tf < tw or tf > 3*tw
	# 					bool7 = bf > alma
	# 					bool8 = tf < 4

	# 					limitacoes = max([bool0, bool1, bool2, bool3, bool4,
	# 					 				bool5, bool6, bool7, bool8, bool9,
	# 									bool10, bool11])

	# 					if not limitacoes:
	# 						dicionario ={
	# 							'd': alma/1000,
	# 							'tw': tw/1000,
	# 							'bf': bf/1000,
	# 							'tf': tf/1000,
	# 							'tipo': 'soldado'
	# 						}
	# 						for barra in lista_barras:								
	# 							barra.set_section_inicio(dicionario)
	# 							barra.set_section_final(dicionario)
							
	# 						self.AnaliseMatricial()

	# 						local, momento_maior = self.LocalDeMaiorMomento(barra)

	# 						for barra in lista_barras:								
	# 							barra.verificar_elu()
	# 							ratio_els = barra.verificar_els()
	# 							ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

	# 							if ratio_elu < 0.9 and ratio_els <= 0.9:
	# 								barra.lista_elu.append(dicionario)

	# 	# segundo processo, dessas secoes que atendem ELU e ELS, pega a mais leve
	# 	for barra in lista_barras:
	# 		dicionario_pesos = {}
	# 		lista_pesos = []
	# 		dicionario = {
	# 			'd': 1050.0 / 1000.0,
	# 			'tw': 6.35 / 1000.0,
	# 			'bf': 225.0 / 1000.0,
	# 			'tf': 12.70 / 1000.0,
	# 			'tipo': 'soldado'
	# 		}

	# 		for secao in barra.lista_elu:
	# 			dicionario0 = {
	# 				'd': secao['d'],
	# 				'tw': secao['tw'],
	# 				'bf': secao['bf'],
	# 				'tf': secao['tf'],
	# 				'tipo': 'soldado'
	# 			}
					
	# 			self.AnaliseMatricial()
	# 			local, momento_maior = self.LocalDeMaiorMomento(barra)

	# 			barra.set_section_inicio(dicionario0)
	# 			barra.set_section_final(dicionario0)

	# 			barra.verificar_elu()
	# 			ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

	# 			if ratio_elu < 0.9:
	# 				peso_linear = barra.section_inicio.set_peso_linear()
	# 				lista_pesos.append(peso_linear)
	# 				dicionario_pesos[peso_linear] = dicionario0


	# 		if len(lista_pesos) >= 1:
	# 			menor_peso = 500
	# 			for peso in lista_pesos:
	# 				menor_peso = min(menor_peso, peso)
				
	# 			dicionario = dicionario_pesos[menor_peso]
			
	# 		barra.set_section_inicio(dicionario)
	# 		barra.set_section_final(dicionario)
	# 		barra.verificar_elu()
    					
	# 		d = dicionario['d']
	# 		tw = dicionario['tw']
	# 		bf = dicionario['bf']
	# 		tf = dicionario['tf']

	# 		for alma in lista_almas:
	# 			dicionario ={
	# 				'd': alma/1000,
	# 				'tw': tw,
	# 				'bf': bf,
	# 				'tf': tf,
	# 				'tipo': 'soldado'
	# 			}
	# 			condicao_viga = True
	# 			if (alma/1000.0) >= (d*0.7):# and alma < self.altura_minima:
	# 				if local == 'final':
	# 					if (barra.ni.x in lista_apoios_cumeeira):
	# 						condicao_viga = alma >= self.altura_minima
	# 					else:
	# 						condicao_viga = True

	# 					if condicao_viga:
	# 						barra.set_section_inicio(dicionario)
	# 						barra.verificar_secao_inicio_elu()
	# 						if barra.ratio_inicio_elu < 0.8:
	# 							break
	# 				else:
	# 					if (barra.nf.x in lista_apoios_cumeeira):
	# 						condicao_viga = alma >= self.altura_minima
	# 					else:
	# 						condicao_viga = True

	# 					if condicao_viga:
	# 						barra.set_section_final(dicionario)
	# 						barra.verificar_secao_final_elu()
	# 						if barra.ratio_final_elu < 0.8:
	# 							break


