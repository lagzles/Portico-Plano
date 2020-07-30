
################################################################################################
################################################################################################
################################################################################################

	def PegarColunasELU_ELS(self):
		# print('go!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_barras = self.lista_colunas# + self.lista_vigas

		lista_els = {}
		lista_elu = {}

		# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
		for barra in lista_barras:
			barra.verificar_elu()
			lista_els[barra.id] = []
			lista_elu[barra.id] = []
			dicionario_pesos = {}
			lista_pesos = []
			contador  = 0
		for tw in [3.75, 4.75, 6.35, 7.92]:
			# print('tw colunas elu els', tw)
			for alma in lista_almas:
				for tf in lista_esp:
					for bf in lista_mesa:
						bool0 = (tw < 4.0 and alma > 450)
						bool1 = tw < 6.0 and alma > 600
						bool9 = tw > 6.0 and alma < 500
						bool5 = tw > 7.0 and alma < 1050
						bool4 = False # tf < 6 and bf >= 150
						bool2 = tf < 9.1 and bf > 200
						bool3 = tf < 12 and bf > 250
						bool10 = alma >= 1050 and bf >= 200

						bool6 = tf < tw or tf > 3*tw
						bool7 = bf > alma
						bool8 = tf < 4

						limitacoes = max([bool0, bool1, bool2, bool3, bool4, bool5, bool6, bool7, bool8, bool9, bool10])

						if not limitacoes:
							dicionario ={
								'd': alma/1000,
								'tw': tw/1000,
								'bf': bf/1000,
								'tf': tf/1000,
								'tipo': 'soldado'
							}
							for barra in lista_barras:								
								barra.set_section_inicio(dicionario)
								barra.set_section_final(dicionario)
							
							self.AnaliseMatricial()

							for barra in lista_barras:								
								barra.verificar_elu()
								ratio_els = barra.verificar_els()
								ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

								if ratio_elu < 0.99 and ratio_els <= 1.0:
									lista_elu[barra.id].append(barra.section_inicio)
									barra.lista_elu.append(dicionario)
									contador += 1

		# segundo processo, dessas 30 secoes que atendem ELU, verificar quais atendem ELS
		# print('fim secao elu els')
		for barra in lista_barras:
			dicionario_pesos = {}
			lista_pesos = []
			dicionario = {
				'd': 1050.0 / 1000.0,
				'tw': 6.35 / 1000.0,
				'bf': 225.0 / 1000.0,
				'tf': 12.70 / 1000.0,
				'tipo': 'soldado'
			}
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

			for secao in barra.lista_elu:
				dicionario0 = {
					'd': secao['d'],
					'tw': secao['tw'],
					'bf': secao['bf'],
					'tf': secao['tf'],
					'tipo': 'soldado'
				}

				barra.set_section_inicio(dicionario0)
				barra.set_section_final(dicionario0)

				peso_linear = barra.section_inicio.set_peso_linear()
				lista_pesos.append(peso_linear)
				dicionario_pesos[peso_linear] = dicionario0


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



	def OtimizarColunasSemELS(self):
		# print('go!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_barras = self.lista_colunas# + self.lista_vigas

		# segundo processo, dessas 30 secoes que atendem ELU, verificar quais atendem ELS
		if self.pilar_metalico:
			for barra in lista_barras:
				dicionario_pesos = {}
				lista_pesos = []
				dicionario = {
					'd': 1050.0 / 1000.0,
					'tw': 6.35 / 1000.0,
					'bf': 225.0 / 1000.0,
					'tf': 12.70 / 1000.0,
					'tipo': 'soldado'
				}
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

				for secao in barra.lista_elu:
					dicionario0 = {
						'd': secao['d'],
						'tw': secao['tw'],
						'bf': secao['bf'],
						'tf': secao['tf'],
						'tipo': 'soldado'
					}

					barra.set_section_inicio(dicionario0)
					barra.set_section_final(dicionario0)
					barra.verificar_elu()
					
					ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)
					if ratio_elu < 0.99:
						peso_linear = barra.section_inicio.set_peso_linear()
						lista_pesos.append(peso_linear)
						dicionario_pesos[peso_linear] = dicionario0


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
					if (alma/1000.0) >= (d*0.85):
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

	def PegarVigasELU_ELS(self):
		# print('go vigas elu e els!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_barras =  self.lista_vigas

		lista_els = {}
		lista_elu = {}

		# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
		for barra in lista_barras:
			barra.verificar_elu()
			barra.lista_elu = []
		for tw in [3.75, 4.75, 6.35, 7.92]:
			# print('tw da viga elu els', tw)
			for alma in lista_almas:
				for tf in lista_esp:
					for bf in lista_mesa:
						bool0 = (tw < 4.0 and alma > 450) or (tw < 6.0 and tf > 6.5)
						bool1 = tw < 6.0 and alma > 600
						bool9 = tw > 6.0 and alma < 500
						bool5 = tw > 7.0 and alma < 1050
						bool4 =  tf < 6 and bf >= 150
						bool2 = tf < 9.1 and bf > 200
						bool3 = tf < 12 and bf > 250
						bool10 = alma >= 1050 and bf >= 200
						bool11 = alma < self.altura_minima

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
							for barra in lista_barras:								
								barra.set_section_inicio(dicionario)
								barra.set_section_final(dicionario)
							
							self.AnaliseMatricial()

							for barra in lista_barras:								
								barra.verificar_elu()
								ratio_els = barra.verificar_els()
								ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)

								if ratio_elu < 0.99 and ratio_els <= 1.0:
									# lista_elu[barra.id].append(barra.section_inicio)
									barra.lista_elu.append(dicionario)
									# contador += 1

		# segundo processo, dessas secoes que atendem ELU e ELS, pega a mais leve
		for barra in lista_barras:
			dicionario_pesos = {}
			lista_pesos = []
			dicionario = {
				'd': 1050.0 / 1000.0,
				'tw': 6.35 / 1000.0,
				'bf': 225.0 / 1000.0,
				'tf': 12.70 / 1000.0,
				'tipo': 'soldado'
			}
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

			for secao in barra.lista_elu:
				dicionario0 = {
					'd': secao['d'],
					'tw': secao['tw'],
					'bf': secao['bf'],
					'tf': secao['tf'],
					'tipo': 'soldado'
				}

				barra.set_section_inicio(dicionario0)
				barra.set_section_final(dicionario0)

				peso_linear = barra.section_inicio.set_peso_linear()
				lista_pesos.append(peso_linear)
				dicionario_pesos[peso_linear] = dicionario0


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
				if (alma/1000.0) >= (d*0.55) and alma < self.altura_minima:
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



	def OtimizarVigasSemELS(self):
		# print('go vigas sem els!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_barras = self.lista_colunas# + self.lista_vigas

		# segundo processo, dessas 30 secoes que atendem ELU, verificar quais atendem ELS
		for barra in lista_barras:
			dicionario_pesos = {}
			lista_pesos = []
			dicionario = {
				'd': 1050.0 / 1000.0,
				'tw': 6.35 / 1000.0,
				'bf': 225.0 / 1000.0,
				'tf': 12.70 / 1000.0,
				'tipo': 'soldado'
			}
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

			for secao in barra.lista_elu:
				dicionario0 = {
					'd': secao['d'],
					'tw': secao['tw'],
					'bf': secao['bf'],
					'tf': secao['tf'],
					'tipo': 'soldado'
				}

				barra.set_section_inicio(dicionario0)
				barra.set_section_final(dicionario0)
				barra.verificar_elu()
				
				ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)
				if ratio_elu < 0.99:
					peso_linear = barra.section_inicio.set_peso_linear()
					lista_pesos.append(peso_linear)
					dicionario_pesos[peso_linear] = dicionario0


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
				if (alma/1000.0) >= (d*0.75):
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





























#############################################################################
#############################################################################
#############################################################################

	def InerciaVigasELS(self):
		# print('go!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_barras = self.lista_vigas

		lista_els = {}
		lista_elu = {}
		for barra in lista_barras:
			barra.linercia_els = 0
			lista_els[barra.id] = []

		# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
		for tw in [3.75, 4.75, 6.35, 7.92]:
			for alma in lista_almas:
				for tf in lista_esp:
					for bf in lista_mesa:
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

						limitacoes = max([bool0, bool1, bool2, bool3, bool4, bool5, bool6, bool7, bool8, bool9, bool10])

						if not limitacoes:
							dicionario ={
								'd': alma/1000,
								'tw': tw/1000,
								'bf': bf/1000,
								'tf': tf/1000,
								'tipo': 'soldado'
							}

							for barra in lista_barras:
								barra.set_section_inicio(dicionario)
								barra.set_section_final(dicionario)

							self.AnaliseMatricial()

							for barra in lista_barras:
								ratio_els = barra.verificar_els()

								if ratio_els <= 0.99:
									barra.lista_els.append(barra.section_inicio)
									ix = barra.section_inicio.set_ix()
									# lista_els[barra.id].append(barra.section_inicio)
									lista_els[barra.id].append(ix)
				
		for barra in lista_barras:
			ix_minimo = 999.0
			for ix in lista_els[barra.id]:
				# ix = secao.set_ix()
				ix_minimo = min(ix, ix_minimo)
			barra.inercia_els = ix_minimo



	def OtimizarVigasComInerciaELS(self):
		# print('go!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_barras = self.lista_vigas # + self.lista_colunas
		lista_elu = {}

		# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
		for barra in lista_barras:
			# barra.set_combinacoes_esforcos()
			barra.verificar_elu()
			lista_elu[barra.id] = []

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

			dicionario_pesos = {}
			lista_pesos = []
			contador  = 0

			for tw in [3.75, 4.75, 6.35, 7.92]:
				for alma in lista_almas:
					for tf in lista_esp:
						for bf in lista_mesa:
							if contador > 100:
								break
							bool0 = (tw < 4.0 and alma > 450) or (tw < 6.0 and tf > 6.5)
							bool1 = tw < 6.0 and alma > 600
							bool9 = tw > 6.0 and alma < 500
							bool5 = tw > 8.0 and alma < 1050
							bool4 = tf < 6 and bf >= 150
							bool2 = tf < 9.1 and bf > 200
							bool3 = tf < 12 and bf > 250
							bool10 = alma >= 1050 and bf >= 200
							bool11 = alma < self.altura_minima

							bool6 = tf < tw or tf > 3*tw
							bool7 = bf > alma
							bool8 = tf < 4

							if barra.tipo == 'coluna':
								bool0 = (tw < 4.0 and alma > 450)
								bool6 = tf < tw or tf > 4*tw
								bool4 = False
								bool11 = False
							
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
								ix = barra.section_inicio.set_ix()

								if ratio_elu < 0.99 and ix >= barra.inercia_els:
									lista_elu[barra.id].append(dicionario)
									contador += 1

		#
		for barra in lista_barras:
			dicionario_pesos = {}
			lista_pesos = []
			dicionario = {
				'd': 1050.0 / 1000.0,
				'tw': 6.35 / 1000.0,
				'bf': 225.0 / 1000.0,
				'tf': 12.70 / 1000.0,
				'tipo': 'soldado'
			}
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


			for secao in lista_elu[barra.id]:
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
				if (alma/1000.0) >= (d*0.6) and alma < self.altura_minima:
					if local == 'final':
						barra.set_section_inicio(dicionario)
						barra.verificar_secao_inicio_elu()
						ix = barra.section_inicio.set_ix()
						if barra.ratio_inicio_elu < 0.99 and ix > barra.inercia_els:
							break
					else:
						barra.set_section_final(dicionario)
						barra.verificar_secao_final_elu()
						ix = barra.section_final.set_ix()
						if barra.ratio_final_elu < 0.99 and ix > barra.inercia_els:
							break







######################################################################################
######################################################################################


	def OtimizarVigasComInercia(self):
		# print('go!')
		lista_esp = [4.75, 6.35, 7.92, 9.52, 12.7, 15.88, 19.4]
		lista_almas = [400, 450,500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
		lista_mesa = [150, 175, 200, 225, 250, 275, 300, 330, 350]
		lista_barras = self.lista_vigas

		# primeiro processo:  achar 30 secoes por barra, que atendem ao ELU
		for barra in lista_barras:
			# barra.set_combinacoes_esforcos()
			barra.verificar_elu()

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

			dicionario_pesos = {}
			lista_pesos = []
			contador  = 0

			for tw in [3.75, 4.75, 6.35, 7.92]:
				for alma in lista_almas:
					for tf in lista_esp:
						for bf in lista_mesa:
							if contador > 100:
								break
							bool0 = (tw < 4.0 and alma > 450) or (tw < 6.0 and tf > 6.5)
							bool1 = tw < 6.0 and alma > 600
							bool9 = tw > 5.0 and alma < 600
							bool5 = tw > 6.0 and alma < 1050
							bool4 = tf < 6 and bf >= 150
							bool2 = tf < 9.1 and bf > 200
							bool3 = tf < 12 and bf > 250
							bool10 = alma >= 1050 and bf >= 200
							bool11 = alma < self.altura_minima

							bool6 = tf < tw or tf > 3*tw
							bool7 = bf > alma
							bool8 = tf < 4

							limitacoes = max([bool0, bool1, bool2, bool3, bool4, 
											bool5, bool6, bool7, bool8, bool9, 
											bool10,bool11])

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
									peso_linear = barra.section_inicio.set_peso_linear()
									lista_pesos.append(peso_linear)
									dicionario_pesos[peso_linear] = dicionario
									contador += 1

			if len(lista_pesos) >= 1:
				menor_peso = 500
				for peso in lista_pesos:
					menor_peso = min(menor_peso, peso)
				
				dicionario = dicionario_pesos[menor_peso]

				if barra.id == 1:
					a = 1
			
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
				if (alma/1000.0) >= (d*0.6) and alma < self.altura_minima:
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



