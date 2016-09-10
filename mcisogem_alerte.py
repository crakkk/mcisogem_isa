# -*- coding:utf8 -*-
from pprint import pprint
import time
from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import osv
from datetime import datetime, timedelta
from openerp import tools
from openerp.tools.translate import _
import openerp
from dateutil.relativedelta import relativedelta
from dateutil import parser
import logging
_logger = logging.getLogger(__name__)



class mcisogem_alerte_quittance(osv.osv):
	_name = 'mcisogem.alerte.quittancier'
	_inherit = ['mail.thread','ir.needaction_mixin']
	_mail_post_access = 'read'


	def calcul_depassement(self, cr, uid, ids, field_name, arg, context=None):

		res = {}
		for alerte in self.pool.get('mcisogem.alerte.quittancier').browse(cr, uid, ids, context):
			
			dt_emi_quittance = datetime.strptime(str(alerte.dt_emi_quittance), "%Y-%m-%d")
			dt_today = datetime.strptime(str(time.strftime("%Y-%m-%d", time.localtime())), "%Y-%m-%d") 

			ecart = (dt_today - dt_emi_quittance).days

			res[alerte.id] = ecart

		return res


	_columns = {
		'quittance_id': fields.many2one('mcisogem.quittancier', 'Quittance'),
		'police_id' : fields.many2one('mcisogem.police' , 'Police'),
		'dt_emi_quittance' : fields.date('Date emission quittance'),
		'depassement': fields.function(calcul_depassement, type='integer', string='depassement (jrs)'),
	}

	_rec_name ="quittance_id"


	


	def quittance_en_alerte(self, cr , uid, context=None):
		les_quittances = self.pool.get('mcisogem.quittancier').search(cr,uid,[])

		for q in self.pool.get('mcisogem.quittancier').browse(cr,uid,les_quittances):
			dt_emis = datetime.strptime(str(q.dt_emi_quittance), "%Y-%m-%d") 
			dt_today = datetime.strptime(str(time.strftime("%Y-%m-%d", time.localtime())), "%Y-%m-%d") 
			ecart = (dt_today - dt_emis).days

			vals = {}
			vals['police_id'] = q.police_id.id
			vals['quittance_id'] = q.id
			vals['dt_emi_quittance'] = q.dt_emi_quittance

			print('***************************')
			print(vals)


			if ecart >= 7 and q.etat_paiement=='NP':

				s_id = self.pool.get('mcisogem.alerte.quittancier').search(cr,uid,[('id' , '=' , q.id)])

				if s_id :

					print('Cette alerte a déjà été enregistrée')

				else:

					########### envoi des notifications aux utilisateurs comptables
					msg = str("Cette quittance a été émise depuis " + str(ecart) + "jours et n'a pas encore été payée ")

					cr.execute("select id from res_groups where name='RESPONSABLE COMPTABLE'")
					groupe_ids = cr.dictfetchall()

					for groupe_id in groupe_ids:

						groupe_id = groupe_id['id']
						
						cr.execute('select uid from res_groups_users_rel  where gid=%s', (groupe_id,))

						user_ids = cr.fetchall()

						les_ids = []
						for u_id in user_ids:
							les_ids.append(u_id[0])

						res_users = self.pool['res.users']
						partner_ids = list(set(u.partner_id.id for u in res_users.browse(cr, uid, les_ids , context)))

						self.message_post(
							cr, uid, False,
							body=msg ,
							partner_ids=partner_ids,
							subtype='mail.mt_comment',
							subject="[ISA-WEB] - ALERTE NON PAIEMENT DE QUITTANCE",
							context=context
						)

					###################################################""

					self.pool.get('mcisogem.alerte.quittancier').create(cr,uid,vals,context)


class mcisogem_alerte_plafond(osv.osv):
	_name = 'mcisogem.alerte.plafond'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_mail_post_access = 'read'

	_columns = {
		'benef_id': fields.many2one('mcisogem.benef', 'Bénéficiaire'),
		'police_id' : fields.many2one('mcisogem.police' , 'Police'),
		'college_id' : fields.many2one('mcisogem.college' , 'Collège'),
		'acte_id' : fields.many2one('mcisogem.nomen.prest' , 'Acte'),
		'affection_id' : fields.many2one('mcisogem.affection' , 'affection'),
		'taux' : fields.float('Taux atteint'),
		'montant_atteint' : fields.integer('Montant atteint'),
		'montant_plafond' : fields.integer('plafond'),
	}

	_rec_name ="benef_id"


	


	def benef_en_alerte(self, cr , uid, context=None):
		# tools.drop_view_if_exists(cr, 'mcisogem_alerte_plafond')

		les_benefs = self.pool.get('mcisogem.benef').search(cr,uid,[])
		
		# je parcours chaque beneficiaire
		for benef in self.pool.get('mcisogem.benef').browse(cr,uid,les_benefs):

			polices = []


			# je recupere toutes polices du benef
			police_id = self.pool.get('mcisogem.benef').browse(cr,uid,benef.id).police_id
			polices.append(police_id)

			p = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr,uid,[('beneficiaire_id' , '=' , benef.id)] ,order='niveau ASC')

			if p:
				for police_id in self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr,uid,p):

					polices.append(police_id.police_id)


			# je parcours toutes les polices du benef à la recherche du plafond annuel défini
			for police in polices:

				college = None

				if police.type_regime == 'O' or police.type_regime == False:

					college = benef.college_id

				else:

					pol_comp_id = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr,uid,[('beneficiaire_id' , '=' , benef.id) , ('police_id' , '=' , police.id)])
					college = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr,uid,pol_comp_id).college_id


				histo_s = self.pool.get('mcisogem.histo.police').search(cr,uid,[('name' , '=' , police.name) , ('code_college' , '=' ,college.id)])
				histo_data  = self.pool.get('mcisogem.histo.police').browse(cr,uid,histo_s)


				actes = self.pool.get('mcisogem.nomen.prest').search(cr,uid,[])

				for acte in self.pool.get('mcisogem.nomen.prest').browse(cr,uid,actes):


					# prendre en compte les dates d 'effet des barèmes'
					if int(police.type_prime) == uid:

						bareme_s = self.pool.get('mcisogem.produit.police').search(cr,uid,[('police_id' , '=' , police.id) , ('acte_id' , '=' ,acte.id ) , ('college_id' , '=' , college.id) , ('statut_id' , '=' , benef.statut_benef.id)])

					else:

						bareme_s = self.pool.get('mcisogem.produit.police').search([('police_id' , '=' , police.id) , ('acte_id' , '=' ,acte.id ) , ('college_id' , '=' , college.id)])


					bareme_data =  self.pool.get('mcisogem.produit.police').browse(cr,uid,bareme_s)

					bsearch = self.pool.get('mcisogem.bareme').search(cr,uid,[('acte_id' , '=' , acte.id) , ('produit_id' , '=' , bareme_data.produit_id.id)])
					bdata = self.pool.get('mcisogem.bareme').browse(cr,uid,bsearch)
					

					periodicite_jr = bareme_data.unite_temps_id.nbre_jour
					
					mnt_prest = 0
					
					pf_periode = bdata.plf_an_prest

					if pf_periode > 0:
						
						
						les_prests_period = self.pool.get('mcisogem.prestation').search(cr,uid,[('acte_id' , '=' , acte.id) , 
								('date_prest' , '>=' , datetime.strptime(str(time.strftime("%Y-%m-%d", time.localtime())), '%Y-%m-%d') - timedelta(days=periodicite_jr)),
								('beneficiaire_id' , '=' , benef.id) ,
								('police_id' , '=' , police.id) , ('exercice_id' , '=' ,police.exercice_id.id )])

						

						# je fais le cumul des prestations de ce benef

						if les_prests_period:
							mnt_periode = 0
							for prest in self.pool.get('mcisogem.prestation').browse(cr,uid,les_prests_period):

								mnt_periode += prest.part_gest

								taux = (mnt_periode * 100) / pf_periode

								if taux >= 50:

									vals = {}
									vals['benef_id'] = benef.id
									vals['police_id'] = police.id
									vals['college_id'] = college.id
									vals['acte_id'] = acte.id
									vals['taux'] = taux
									vals['montant_plafond'] = pf_periode
									vals['montant_atteint'] = mnt_periode

									s_id = self.search(cr,uid,[('benef_id' , '=' , benef.id) , ('police_id' , '=' ,police.id) , ('college_id' , '=' ,college.id) , ('acte_id' , '=' ,acte.id)])

									if s_id:

										if self.browse(cr,uid,s_id).taux != taux:

											self.write(cr,uid,s_id[0],{'taux' : taux},context)

										else:
											break;
									else:


										########### envoi des notifications aux utilisateurs comptables
										msg = str("Le Bénéficiaire " + str(benef.nom) + " " + str(benef.prenom_benef) + " a atteint 50 '%'(ou plus) de son plafond périodique sur la police " + str(police.name))

										cr.execute("select id from res_groups where name='RESPONSABLE PRESTATION'")
										groupe_ids = cr.dictfetchall()

										for groupe_id in groupe_ids:

											groupe_id = groupe_id['id']
											
											cr.execute('select uid from res_groups_users_rel  where gid=%s', (groupe_id,))

											user_ids = cr.fetchall()

											les_ids = []
											for u_id in user_ids:
												les_ids.append(u_id[0])

											res_users = self.pool['res.users']
											partner_ids = list(set(u.partner_id.id for u in res_users.browse(cr, uid, les_ids , context)))

											self.message_post(
												cr, uid, False,
												body=msg ,
												partner_ids=partner_ids,
												subtype='mail.mt_comment',
												subject="[ISA-WEB] - ALERTE PLAFOND",
												context=context
												)

											###################################################""

										self.pool.get('mcisogem.alerte.plafond').create(cr,uid,vals,context)


				pf_affec = 0
				affections = self.pool.get('mcisogem.affec').search(cr,uid,[])

				for affection in self.pool.get('mcisogem.affec').browse(cr,uid,affections):

					plafond_affection = self.pool.get('mcisogem.plafond.affection').search(cr,uid,[('code_aff_id' , '=' , affection.id)])

					pf_affec = 0
					mnt_affec = 0

					for plf in self.pool.get('mcisogem.plafond.affection').browse(cr,uid,plafond_affection):
						if plf.tout_benef == True:
							pf_affec = plf.plafond

							break
						else:

							if plf.benef_id == benef_data.id:
								pf_affec = plf.plafond

								break

					if pf_affec > 0:

						les_prests_affec = self.pool.get('mcisogem.prestation').search(cr,uid,[('affection_id' , '=' , affection.id) , 
								('date_prest' , '>=' , datetime.strptime(str(time.strftime("%Y-%m-%d", time.localtime())), '%Y-%m-%d') - timedelta(days=periodicite_jr)),
								('beneficiaire_id' , '=' , benef.id) ,
								('police_id' , '=' , police.id) , ('exercice_id' , '=' ,police.exercice_id.id )])


						if les_prests_affec:

							for prest in self.pool.get('mcisogem.prestation').browse(cr,uid,les_prests_affec):

								mnt_affec += prest.part_gest

								taux = (mnt_affec * 100) / pf_affec

								if taux >= 50:

									vals = {}
									vals['benef_id'] = benef.id
									vals['police_id'] = police.id
									vals['college_id'] = college.id
									vals['affection_id'] = affection.id
									vals['taux'] = taux
									vals['montant_plafond'] = pf_affec
									vals['montant_atteint'] = mnt_affec

									s_id = self.search(cr,uid,[('benef_id' , '=' , benef.id) , ('police_id' , '=' ,police.id) , ('college_id' , '=' ,college.id) , ('affection_id' , '=' ,affection.id)])

									if s_id:

										if self.browse(cr,uid,s_id).taux != taux:

											self.write(cr,uid,s_id[0],{'taux' : taux},context)

										else:
											break
									else:


										########### envoi des notifications aux utilisateurs comptables
										msg = str("Le Bénéficiaire " + str(benef.nom) + " " + str(benef.prenom_benef) + " a atteint 50 '%'(ou plus) du plafond pour l'affection sur la police " + str(police.name))

										cr.execute("select id from res_groups where name='RESPONSABLE PRESTATION'")
										groupe_ids = cr.dictfetchall()

										for groupe_id in groupe_ids:

											groupe_id = groupe_id['id']
											
											cr.execute('select uid from res_groups_users_rel  where gid=%s', (groupe_id,))

											user_ids = cr.fetchall()

											les_ids = []
											for u_id in user_ids:
												les_ids.append(u_id[0])

											res_users = self.pool['res.users']
											partner_ids = list(set(u.partner_id.id for u in res_users.browse(cr, uid, les_ids , context)))

											self.message_post(
												cr, uid, False,
												body=msg ,
												partner_ids=partner_ids,
												subtype='mail.mt_comment',
												subject="[ISA-WEB] - ALERTE PLAFOND",
												context=context
												)

											###################################################""

										self.pool.get('mcisogem.alerte.plafond').create(cr,uid,vals,context)












