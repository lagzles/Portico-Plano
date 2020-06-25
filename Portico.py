# -*- coding: utf-8 -*-
import Nos as ns
import Barras as br
import numpy as np
from math import sin
import desenhar as dwg


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
		self.lista_bases = []
		self.gdl = 0

		self.carregamentos = []
		self.carregamentosELU = []
		self.carregamentosELS = []

		self.ap = []
		self.liv = []
		self.k = []

		print('vaos', lista_vaos)
		print('cumeeira', cumeeira)
		# print('inclinacao', inclinacao)

		self.GerarBarrasEPontos()
		self.DefinirGDL()
		self.GerarDesenhoDXF()


	def SetarCarregamentos(self, carregamentos):
		self.carregamentos = carregamentos
		for carr in carregamentos:
			if carr[0] == 'ultimo':
				self.carregamentosELU.append(carr[1])
			else:
				self.carregamentosELS.append(carr[1])
    		

	def AnaliseMatricial(self):
		print('#'*20)
		print()
		print('Fazendo analise\n')
		self.MontarMatrizRigidez()

		for carregamento in self.carregamentosELU:
			# carregamentos nodais equivalentes de cada barra
			carr = carregamento
			fa = np.zeros((len(self.liv)))
			fo = np.zeros((self.gdl))
			fo1 = np.zeros((self.gdl))

			# print('gdl  /  ap  /  liv  /  k  ')
			# print(self.gdl, len(self.ap), len(self.liv), self.k.shape)

			contador = 0
			contador2 = 0
			for barra in self.lista_barras:
				if barra.tipo == 'viga':
					mz = (carr * (barra.comprimento() ** 2) ) / 12.
					fy = (carr * barra.lb) / 2.
					fx = fy * round(sin(barra.theta),4)

					fo1[barra.ni.gx-1] += fx
					fo1[barra.ni.gy-1] += fy
					fo1[barra.ni.gz-1] += mz
					fo1[barra.nf.gx-1] += fx
					fo1[barra.nf.gy-1] += fy
					fo1[barra.nf.gz-1] += - mz
					
					fboi = np.zeros((6))
					fboi[0] = round(fx,2)
					fboi[1] = round(fy,2)
					fboi[2] = round(mz,2)
					fboi[3] = round(fx,2)
					fboi[4] = round(fy,2)
					fboi[5] = round(-mz,2)

					barra.fboi = fboi
					# foi = np.dot(np.dot(np.transpose(barra.ti), fboi), barra.ti)
					foi = np.dot(np.transpose(barra.ti), fboi)

					fci = np.dot(np.transpose(barra.li), foi)

					fo = fo + fci
					contador += fy * 2
					contador2 += 1

			fo = fo1

			ap = self.ap
			liv = self.liv
			k = self.k

			# print(ka)
			foa = np.delete(fo, ap, axis=0)
			fca = fa - foa
			
			ka = np.delete(np.delete(k, ap, axis=0), ap, axis=1)
			kb = np.delete(np.delete(k, liv, axis=0), ap, axis=1)

			det = np.linalg.det(ka)
			for no in self.lista_nos:
				print('nó', no, [no.x, no.y], no.apoio)
			for barra in self.lista_barras:
				print('barra',barra.id, [barra.ni.x, barra.ni.y], barra.ni.apoio, [barra.nf.x, barra.nf.y], barra.nf.apoio)

			if det == 0:
				print('Determinante de Ka = 0, matriz singular. Não pode')
				break
			ka_inv = np.linalg.inv(ka)

			# deslocamentos nós livres
			ua = np.dot(ka_inv, (fa - foa))
			fb = np.dot(kb, ua)

			grausReacoes = len(fb)

			for barra in self.lista_barras:
				barra.esforcos_nodais([ua], liv)

			for i in range(0,grausReacoes):
				grauApoio = ap[i]
				reacao = fb[i]

				for base in self.lista_bases:
					baseGdlX = base.gx - 1
					baseGdlY = base.gy - 1
					baseGdlZ = base.gz - 1
					# print(baseGdlX, gdlX)

					if(baseGdlX == grauApoio):
						base.rx = reacao
					if(baseGdlY == grauApoio):
						base.ry = reacao
					if(baseGdlZ == grauApoio):
						base.mz = reacao

			print('\nReações de APOIO')
			print('X	Y	MZ')
			somaVerticais = 0
			for base in self.lista_bases:
				# print(base)
				base.printReacoes()
				somaVerticais += base.ry
			
			# for base in self.lista_bases:
			# 	print(base.x, base.y)

			# print('\nsoma de Reacoes verticais', round(somaVerticais,2))
			# print('soma de esforços verticais ',round(contador,2))

			# print('Esforços nodais das barras')
			# for barra in self.lista_barras:
			# 	print(barra.id,[[barra.ni.x, barra.ni.y], [barra.nf.x, barra.nf.y]] , barra.fbi)

	
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

				elif no.apoio == 'rotuladoInicial' or no.apoio == "rotuladoFinal":#if no.apoio == 'bi-articulado':
					ap = ap + [no.gx - 1]
					ap = ap + [no.gy - 1]
					# ap = ap + [no.gz - 1]
					# liv = liv + [no.gx - 1]
					liv = liv + [no.gz - 1]

				elif no.apoio == 'bi-articulado':
					ap = ap + [no.gx - 1]
					ap = ap + [no.gy - 1]
					# liv = liv + [no.gx - 1]
					liv = liv + [no.gz - 1]
					# ap = ap + [no.gz - 1]

				# else:#if no.apoio == 'bi-articulado':
				# 	ap = ap + [no.gx - 1]
				# 	ap = ap + [no.gy - 1]
				# 	ap = ap + [no.gz - 1]
				# 	# liv = liv + [no.gx - 1]
				# 	# liv = liv + [no.gz - 1]
		
		self.liv = liv
		self.ap = ap
		self.k = k

		# print('liv',liv)
		# print('ap',ap)


	def GerarDesenhoDXF(self):
		barras = self.lista_barras
		dwg.desenhar_portico(self, 'portico.dxf')


	def DefinirGDL(self):
		numeroNos = len(self.lista_nos)
		# print('gdls')
		# print(numeroNos*3, self.gdl)
		maiorGdl = 0


	def GerarBarrasEPontos(self):
		# # numero de vaos
		# print('#'*20)
		# print()
		# print('Barras e Pontos')

		n = len(self.lista_vaos)
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
			# salvar cota do lado direito do galpao
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
			
			pontoIndex = pontos_base.index(ponto)

			# ponto inicial tera propriedade apoio diferente de False
			if pontoIndex == 0 or pontoIndex == (len(pontos_base)-1):
				# print('e')
				apoio = 'engaste'
			else:
				# print('r')
				# apoio = 'rotuladoInicial'
				# apoio = 'rotuladoFinal'
				apoio = 'bi-articulado'
				# apoio = 'engaste'

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
					coluna = br.Barras(nob, no, barraId, 1, 1, 'coluna')
					self.lista_barras.append(coluna)
					self.lista_bases.append(nob)
		

	def PontosIntermediariosDaViga(self, noi, vao, cota):
		# no2
		xb = noi.x
		yb = noi.y
		
		# no4
		xt = xb + vao
		yt = cota

		# divisão padrão do vão em 3 partes
		n = 1#3
		if (xt-xb) < 8.000: # caso tenha um 'vao' menor que 8m, não dividir
			n = 1
			# situacao mais comum quando cumeeira esta no meio do vao
		if n != 1:
			dx = (xt-xb) / n
			dy = (yt-yb) / n

			# gdl = self.gdl
			ptFim = None #ns.Nos(xb+dx, yb+dy, gdl+1, gdl+2, gdl+3, 0, 0, 0,False)
			# self.gdl += 3
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
				barraIntermediaria = br.Barras(ptInicio, ptFim, barra_id, n , n, 'viga')

				self.lista_barras.append(barraIntermediaria)
				self.lista_nos.append(ptFim)
				
		elif n == 1:
			ptInicio = noi
			gdl = self.gdl
			ptFim = ns.Nos(xt, yt, gdl+1, gdl+2, gdl+3, False)
			self.gdl += 3

			barra_id = len(self.lista_barras) + 1
			barraIntermediaria = br.Barras(ptInicio, ptFim, barra_id, n , n, 'viga')

			self.lista_barras.append(barraIntermediaria)
			self.lista_nos.append(ptFim)

		return ptFim

