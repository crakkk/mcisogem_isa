# -*- coding:utf8 -*-
import time

from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import osv
from datetime import datetime, timedelta
from openerp import tools
from openerp.tools.translate import _
import openerp
from datetime import datetime, timedelta, date
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
from math import *
import logging
_logger = logging.getLogger(__name__)


class mcisogem_quittancier_police_temp(osv.osv):
	_name = "mcisogem.quittancier.police.temp"
	_description = 'Police temporare'
	
	_columns = {        
	   'name':fields.many2one('mcisogem.police', 'name', 'Police'),       
	}



#----------------------------------------------------------
# Quittancier
#----------------------------------------------------------

class mcisogem_quittancier(osv.osv):
	_name = "mcisogem.quittancier"    
	_description = "Gestion du quittancier"


	TYPE_AVENANT = [
		('AI', 'Avenant Initial'),
		('AA', 'Avenant d\'Appel de prime'),
		('AB', 'Avenant de modification de Barèmes'),
		('AC', 'Avenant de modification de terme du Contrat'),
		('AJ', 'Avenant d\'Ajustement de prime'),
		('AP', 'Avenant de modification de Prime'),
		('AM', 'Avenant de Mouvement'),
	]

	def _get_cod_gest(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		return gest_obj.code_centre    
	
	def _get_cod_lang(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		return gest_obj.langue_id.name
	
	def _get_cod_gest_id(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))        
		cod_gest_id = cr.fetchone()[0]
		return cod_gest_id    

	_columns = {
		'detail_quittancier_ids': fields.one2many('mcisogem.detail.quittancier', 'mcisogem_quittancier_id', "Récapitulatif des mouvements d'incorporation", order="code_statut_benef"),

		'detail_quittancier_retrait_ids': fields.one2many('mcisogem.detail.quittancier.retrait', 'mcisogem_quittancier_id', "Récapitulatif des mouvements de retrait", order="code_statut_benef"),

		'dt_emi_quittance': fields.date('Date émission quittance'),
		#Garant
		'garant_id': fields.many2one('mcisogem.garant', "Garant", required=True),

		'quittance_id' : fields.many2one('mcisogem.quittancier' , 'Quittance à annuler'),
		#Type avenant
		'type_avenant_id':fields.many2one('mcisogem.type.avenant', "Type d\'avenant", required=True),
		# 'type_avenant_id':fields.selection(TYPE_AVENANT,'Type d\'avenant', required=True ),
		'avenan_libelle': fields.char(''),
		#Police
		'police_id': fields.many2one('mcisogem.police', "Police", required=True),
		'souscripteur_id': fields.many2one('mcisogem.souscripteur', 'Souscripteur', readonly=True),
		'courtier_id': fields.many2one('mcisogem.courtier', 'Intermédiaire', readonly=True),
		'date_effet_police': fields.date('Date effet police', readonly=True),
		'repartition_prime': fields.selection([('1', 'Mois'), ('2', 'Jour')], 'Repartition prime', readonly=True),
		'avenant':fields.integer('N° avenant police', readonly=True),
		'mnt_regl_prime_quittance': fields.float('Montant reclamé', digits=(18, 0)),  
		'cod_annul_quittance_calc': fields.boolean('Code annulation'), 
		'dt_annul_quittance_calc': fields.datetime('Date d’annulation de la quittance'),
		'mnt_quittance_emis': fields.float('Total prime nette', digits=(18, 0), readonly=True), 
		'calc_prime_quittance': fields.float('', digits=(1, 0)), 
		'prime_cal_quittance': fields.integer('Prime', required=True),
		'duree_exercice' : fields.integer('Durée de la police') , 
		'date_prochain_exercice' : fields.date('Date du prochain exercice'),
		'valide_quittance': fields.boolean('Code quittance valide'),
		#Exercice police
		'dt_emi_ave': fields.date('Exercice du', readonly=True),
		'dt_fin_ave': fields.date('Au', readonly=True),
		'periodicite_paiem': fields.many2one('mcisogem.unite.temps', 'Périodicité paiement prime' , readonly=True),
		'imputation_acc_courtier': fields.boolean('Accessoire Intermédiaire', readonly=True),
		'imputation_acc_cie': fields.boolean('Accessoire compagnie', readonly=True),
		'num_histo_prime': fields.integer('', readonly=True),
		'num_histo_pol': fields.integer('', readonly=True),       
		'mnt_glob0': fields.float('Montant TTC', digits=(18, 0), readonly=True), 
		'mnt_taxe_comm0': fields.float('TVA', digits=(18, 0), readonly=True),  
		'mnt_taxe_prime0': fields.float('Taxe d’enregistrement', digits=(18, 0), readonly=True),         
		'mnt_taxe': fields.float('  ', digits=(18, 2)),
		'mnt_TVA': fields.float('  ', digits=(18, 2)),
		'type_mnt_tva': fields.boolean('%'),
		'type_mnt_taxe': fields.boolean('%'),
		'tva_oui_non': fields.boolean('TVA'), 
		'cod_comptabilisation': fields.float('Code quittance valide', digits=(1, 0)),
		'dat_comptabilisation': fields.datetime(''),
		#Commissions
		'cout_d_acte': fields.float('Gestionnaire', digits=(18, 0), readonly=True), 
		'cout_d_acte_courtier': fields.float('Intermédiaire', digits=(18, 0), readonly=True),         
		'type_mnt_comxion_gest': fields.boolean('%'), 
		'type_mnt_comxion_courtier': fields.boolean('%'), 
		'mnt_comxion_gest': fields.float(' ', digits=(18, 2)), 
		'mnt_comxion_courtier': fields.float(' ', digits=(18, 2)), 
		'cout_d_acte0': fields.float('Total', digits=(18, 0), readonly=True),  
		#Accessoires
		'taxe_acc_nostro': fields.float('Gestionnaire', digits=(18, 0), readonly=True), 
		'taxe_acc_courtier': fields.float('Intermediare', digits=(18, 0), readonly=True), 
		'taxe_acc_assureur': fields.float('TVA', digits=(18, 0), readonly=True), 
		'type_mnt_accessoires_gest': fields.boolean('%'),
		'type_accessoires_courtier': fields.boolean('%'), 
		'type_accessoires_assureur': fields.boolean('%'),
		'mnt_accessoires_gest': fields.float(' ', digits=(18, 2)),
		'mnt_accessoires_courtier': fields.float(' ', digits=(18, 2)),
		'mnt_accessoires_assureur': fields.float(' ', digits=(18, 2)),
		'base': fields.float("Base", digits=(18, 0), readonly=True),    
		'cout_d_acte1': fields.float('Total', digits=(18, 0), readonly=True),

		'total_plus_access': fields.float('Montant prime HT + Accessoires', digits=(18, 0), readonly=True),
		'prime_annuel': fields.float('Prime Annuelle', digits=(18, 0), readonly=True),
		'num_quittance_interne_police': fields.integer('Numero avenant police', readonly=True),
		'objet_particulier': fields.text('Objet particulier', size=20),
		#Nature risque
		'nature_risque_id':fields.many2one('mcisogem.nature.risque', "Nature risque"),
		'prime_sida': fields.float('Prime sida', digits=(18, 0), readonly=True), 
		'prime_tot_sans_sida': fields.float('Prime Nette', digits=(18, 0), readonly=True),          
		'num_quittance_annulee': fields.float('Numero de la quittance à annuler', digits=(18, 0)),
		'mnt_glob1': fields.float('  ', digits=(18, 0)),
		'prime_tot_rest': fields.float('  ', digits=(18, 0)),
		'prctge_apprime': fields.float('  ', digits=(18, 0)),
		'cout_d_acte_assur': fields.float('  ', digits=(18, 0)), 
		'deb_periode': fields.date('Période du', required=True),
		'fin_periode': fields.date('Date fin', required=True),
		'exoneration' : fields.float('Exoneration'),
		'affiche': fields.boolean(''),
		'etat_paiement': fields.selection([
			('P', "Payé"),
			('NP', "Non Payé"),
		], 'Etat de paiement', required=True, readonly=True),

		'date_paiement' : fields.date('Date de paiement'),
		'state': fields.selection([
			('draft', "Nouveau"),
			('sent', "Calculer"),
			('done', "Valider"),
			('cancel', "Annuler"),
		], 'Statut', required=True, readonly=True),
		'show_gestionnaire' : fields.boolean(),
		'show_garant' : fields.boolean(),
		'show_intermediaire' : fields.boolean(),
		'show_taxe' : fields.boolean(),
		'show_taxe_enreg' : fields.boolean(),
		'show_exoneration' : fields.boolean(),

	}
	_rec_name = 'type_avenant_id'

	_defaults = {
		'affiche': False,
		'state': 'draft',
		'dt_emi_quittance': time.strftime("%Y-%m-%d", time.localtime()),
		'mnt_regl_prime_quittance': 0,
		'cod_annul_quittance_calc': False,
		'calc_prime_quittance': 0,
		'prime_cal_quittance': 0,
		'prime_cal_quittance': 0,
		'cod_comptabilisation': 0,
		'dat_comptabilisation': '1900-01-01 00:00:00',
		'dat_comptabilisation': '1900-01-01 00:00:00',
		'dat_comptabilisation': '',
		'cout_d_acte_assur': 0,
		'dt_annul_quittance_calc': '1900-01-01 00:00:00',
		'type_avenant_id' : 1,
		'etat_paiement' : 'NP',
		'show_exoneration' : False,
		'show_taxe_enreg' : False,
		'show_taxe' : False,
		'show_intermediaire' : False,
		'show_garant' : False,
		'show_gestionnaire' : False,


	}


	def payer(self, cr, uid, ids, context=None):

		return super(mcisogem_quittancier, self).write(cr, uid, ids, {'etat_paiement':'P' , 'date_paiement' : time.strftime("%Y-%m-%d", time.localtime())}, context=context)

	def annuler_paiement(self, cr, uid, ids, context=None):
		return super(mcisogem_quittancier, self).write(cr, uid, ids, {'etat_paiement':'NP' , 'date_paiement' :None}, context=context)
		


	def print_quittance(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids, [], context=context)

		return {
				'type': 'ir.actions.report.xml',
				'report_name': 'mcisogem_isa.report_quittancier_all',
				'data': data,
		}


	def onchange_garant(self, cr, uid, ids, garant_id, context=None):        
		if not garant_id:
			return False
		else:

			cr.execute("delete from mcisogem_quittancier_police_temp where create_uid=%s", (uid,))
			cr.execute("select id from mcisogem_police where garant_id=%s and state=%s", (garant_id, 'draft',))
			lespolicesgarant = cr.dictfetchall()
			

			for col in lespolicesgarant:
				cr.execute("insert into mcisogem_quittancier_police_temp (create_uid,name) values(%s, %s)", (uid, col['id'],))

	def onchange_quittance(self, cr, uid, ids, quittance_id, context=None):  

		vals = {}
		valeurs = self.browse(cr,uid,quittance_id)

		vals['prime_tot_sans_sida'] = valeurs.prime_tot_sans_sida
		vals['prime_sida'] = valeurs.prime_sida
		vals['taxe_acc_nostro'] = valeurs.taxe_acc_nostro
		vals['taxe_acc_assureur'] = valeurs.taxe_acc_assureur
		vals['taxe_acc_courtier'] = valeurs.taxe_acc_courtier

		vals['cout_d_acte1'] = valeurs.cout_d_acte1
		vals['cout_d_acte'] = valeurs.cout_d_acte
		vals['cout_d_acte0'] = valeurs.cout_d_acte0
		vals['cout_d_acte_assur'] = valeurs.cout_d_acte_assur
		vals['cout_d_acte_courtier'] = valeurs.cout_d_acte_courtier

		vals['type_accessoires_courtier'] = valeurs.type_accessoires_courtier
		vals['type_mnt_taxe'] = valeurs.type_mnt_taxe
		vals['type_accessoires_assureur'] = valeurs.type_accessoires_assureur
		vals['type_mnt_accessoires_gest'] = valeurs.type_mnt_accessoires_gest
		vals['type_mnt_comxion_courtier'] = valeurs.type_mnt_comxion_courtier
		vals['type_mnt_comxion_gest'] = valeurs.type_mnt_comxion_gest

		vals['total_plus_access'] = valeurs.total_plus_access
		vals['mnt_taxe_prime0'] = valeurs.mnt_taxe_prime0
		vals['mnt_quittance_emis']= valeurs.mnt_quittance_emis
		vals['mnt_glob0'] = valeurs.mnt_glob0
		vals['objet_particulier'] = valeurs.objet_particulier

		vals['mnt_taxe_prime0'] = valeurs.mnt_taxe_prime0
		vals['mnt_taxe'] = valeurs.mnt_taxe
		vals['mnt_accessoires_gest'] = valeurs.mnt_accessoires_assureur
		vals['mnt_accessoires_assureur'] = valeurs.mnt_accessoires_assureur
		vals['mnt_TVA'] = valeurs.mnt_TVA
		vals['mnt_glob1'] = valeurs.mnt_glob1
		vals['mnt_comxion_gest'] = valeurs.mnt_comxion_gest
		vals['mnt_comxion_courtier'] = valeurs.mnt_comxion_courtier
		vals['mnt_accessoires_courtier'] = valeurs.mnt_accessoires_courtier

		vals['souscripteur_id'] = valeurs.souscripteur_id
		vals['police_id'] = valeurs.police_id
		vals['courtier_id'] = valeurs.courtier_id
		vals['dt_emi_ave'] = valeurs.dt_emi_ave
		vals['dt_fin_ave'] = valeurs.dt_fin_ave
		vals['date_effet_police'] = valeurs.date_effet_police
		vals['deb_periode'] = valeurs.deb_periode
		vals['fin_periode'] = valeurs.fin_periode
		vals['affiche'] = True
		vals['repartition_prime'] = valeurs.repartition_prime
		vals['periodicite_paiem'] = valeurs.periodicite_paiem
		vals['imputation_acc_courtier'] = valeurs.imputation_acc_courtier
		vals['imputation_acc_cie'] = valeurs.imputation_acc_cie

		return {'value' : vals}

	def onchange_type_avenan(self, cr, uid, ids, type_avenant_id, context=None): 
		if not type_avenant_id:
			return False
		else:
			search_avenant = self.pool.get('mcisogem.type.avenant').search(cr,uid,[('id' , '=' , type_avenant_id)])
			avenant_data = self.pool.get('mcisogem.type.avenant').browse(cr,uid,search_avenant)
			
			return {'value': {'objet_particulier': avenant_data.code_type_avenant, 'avenan_libelle': avenant_data.code_type_avenant , 'type_avenant_id' : type_avenant_id}}


	def onchange_intermediaire(self, cr, uid, ids, courtier_id, context=None):        
		if not courtier_id:

			return False
		else:

			search_intermed = self.pool.get('mcisogem.courtier').search(cr,uid,[('id' , '=' , courtier_id)])
			intermed_data = self.pool.get('mcisogem.courtier').browse(cr,uid,search_intermed)
			return {'value': {'type_mnt_comxion_courtier': True, 'mnt_comxion_courtier': intermed_data.taux_commission}}


	def onchange_police(self, cr, uid, ids, police_id, type_avenant_id, context=None):
		vals = {}

		if not police_id:
			return False

		if not type_avenant_id:
			return False

		if police_id != False and type_avenant_id != False:

			code_avenant = self.pool.get('mcisogem.type.avenant').browse(cr,uid,type_avenant_id).code_type_avenant


			avenant_search = self.pool.get('mcisogem.type.avenant').search(cr,uid,[('code_type_avenant' , '=' , 'AS')])
			avenant_fact = self.pool.get('mcisogem.type.avenant').browse(cr,uid,avenant_search).id



			data = self.details_police(cr,uid,police_id)
			prime_assure = 0
			prime_sida = 0
			somme_prime = 0


			nbre_ave = self.pool.get('mcisogem.avenant').search_count(cr,uid,[('police_id' , '=' , police_id) , ('type_avenant_id' , '=' , type_avenant_id) , ('state' , '=' , 'valid')])
			if nbre_ave == 0:
				raise osv.except_osv('Attention' , "Vous devez d'abord créé un avenant de ce type sur la police")


			if code_avenant == 'ARS':

				if self.check_etat_police(cr,uid,police_id) != 'resil':
					raise osv.except_osv('Attention' , 'Cette police n\' a pas été résiliée')

				
				prime_assure = 0
				prime_sida = 0

				dt_fin_police = data['dt_resil_pol']
				dt_fin_police = datetime.strptime(str(dt_fin_police), '%Y-%m-%d')
				dt_fin_exercice = data['dt_fin_ave']
				dt_fin_exercice = datetime.strptime(str(dt_fin_exercice), '%Y-%m-%d')

				cr.execute("select distinct college_id from mcisogem_benef where police_id=%s", (police_id,))
				lescolleges = cr.dictfetchall()     

				for college in lescolleges:
					college_search = self.pool.get('mcisogem.college').search(cr,uid,[('id' , '=' , college['college_id'] )])
					college_data = self.pool.get('mcisogem.college').browse(cr,uid,college_search)

					cr.execute("select distinct statut_benef from mcisogem_benef where police_id =%s and college_id=%s and dt_effet <= %s", (police_id, college['college_id'] ,dt_fin_police))

					lesstatuts = cr.dictfetchall()

					

					#On parcours les statut de bénéficiaire
					for statut in lesstatuts:

						cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id=%s order by id DESC", (college['college_id'], police_id, statut['statut_benef']))
						lesprimes = cr.dictfetchall()

						prime = lesprimes[0]

						dt_effet_prime = prime['dt_eff_mod_prime']
						dt_effet_prime = datetime.strptime(str(dt_effet_prime), '%Y-%m-%d')
						

						cr.execute("select  * from mcisogem_benef where statut != 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s", 
							(police_id, statut['statut_benef'] , college['college_id'], dt_fin_police))
						lesbenefs = cr.dictfetchall() 

						cr.execute("select  * from mcisogem_benef where statut = 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s and date_exclusion > %s", 
							(police_id, statut['statut_benef'] , college['college_id'], dt_fin_police ,dt_fin_police))
						lesbenefs_r = cr.dictfetchall() 

	

						nbre_mois = relativedelta(dt_fin_exercice, dt_fin_police).months

						prime_assure += (prime['prim_assure'] * nbre_mois ) / 12.0
						prime_sida += (prime['prime_sida'] * nbre_mois ) / 12.0

						for benef in lesbenefs_r:

							dt_fin_benef = datetime.strptime(str(benef['date_exclusion']), "%Y-%m-%d %H:%M:%S")

							if dt_fin_benef > dt_fin_police:
								dt_fin_police = dt_fin_benef


							nbre_mois = relativedelta(dt_fin_exercice, dt_fin_police).months

							prime_assure += round((prime['prim_assure'] * nbre_mois ) / 12.0)
							prime_sida += round((prime['prime_sida'] * nbre_mois ) / 12.0)

					prime_assure = round(prime_assure)
					prime_sida = round(prime_sida)


				prime_assure = -prime_assure
				prime_sida = -prime_sida			
				somme_prime = prime_assure + prime_sida


				

				return {'value': {'souscripteur_id': data.souscripteur_id['id'], 'courtier_id': data.courtier_id['id'],
					'dt_emi_ave': data.dt_emi_ave, 'dt_fin_ave': data.dt_fin_exercice,
					'date_effet_police': data.dt_effet, 'deb_periode': data.dt_deb_exercice,
					'fin_periode': data.dt_fin_exercice, 'affiche': True, 'repartition_prime': data.repartition_prime, 
					'periodicite_paiem': data.periodicite_paiem['id'], 'imputation_acc_courtier': data.imputation_acc_courtier,
					'imputation_acc_cie': data.imputation_acc_cie , 'prime_tot_sans_sida' : prime_assure , 'prime_sida' : prime_sida , 'mnt_quittance_emis' : somme_prime , 'base' : somme_prime , 'show_exoneration' : data.taxe_exon , 'show_intermediaire' : data.imputation_acc_courtier , 'show_taxe' : data.tva_oui_non , 'show_gestionnaire' : data.imputation_acc_gestionnaire , 'show_garant' : data.imputation_acc_cie , 'show_taxe_enreg' : data.taxe_enreg}}

			if code_avenant == 'AS':
				return {'value': {'souscripteur_id': data.souscripteur_id['id'], 'courtier_id': data.courtier_id['id'],
						'dt_emi_ave': data.dt_emi_ave, 'dt_fin_ave': data.dt_fin_exercice,
						'date_effet_police': data.dt_effet, 'deb_periode': data.dt_deb_exercice,
						'fin_periode': data.dt_fin_exercice, 'affiche': True, 'repartition_prime': data.repartition_prime, 
						'periodicite_paiem': data.periodicite_paiem['id'], 'imputation_acc_courtier': data.imputation_acc_courtier,
						'imputation_acc_cie': data.imputation_acc_cie , 'show_exoneration' : data.taxe_exon , 'show_intermediaire' : data.imputation_acc_courtier , 'show_taxe' : data.tva_oui_non , 'show_gestionnaire' : data.imputation_acc_gestionnaire , 'show_garant' : data.imputation_acc_cie , 'show_taxe_enreg' : data.taxe_enreg}}

			# Avenant Initial
			if code_avenant == 'AI':

				# je recupere tous les benef actifs de la  police
				les_benef_search = self.pool.get('mcisogem.benef').search(cr,uid,[('police_id','=',police_id) , ('statut' , '!=' , 'R')])
				les_benef_police = self.pool.get('mcisogem.benef').browse(cr,uid,les_benef_search)

				for benef in les_benef_police:

					statut_benef = benef.statut_benef.id
					college_benef = benef.college_id.id

					l_histo_prime_search = self.pool.get('mcisogem.histo.prime').search(cr,uid,[('police_id','=',police_id) , ('statut_benef_id' , '=' , statut_benef) , ('college_id' , '=' , college_benef)])
				
					for l_histo_prime_data in self.pool.get('mcisogem.histo.prime').browse(cr,uid,l_histo_prime_search):

						prime_assure += l_histo_prime_data.prim_assure
						prime_sida += l_histo_prime_data.prime_sida



				cr.execute('select repartition_prime from mcisogem_police where id=%s', (police_id,)) 
				mode_repar_prime = cr.fetchone()[0]

				exercice_search = self.pool.get('mcisogem.exercice.police').search(cr,uid, [('state' , '=' , 'actif') , ('police_id' , '=' , police_id)])
				exercice_data = self.pool.get('mcisogem.exercice.police').browse(cr,uid,exercice_search)

				if self.pool.get('mcisogem.exercice.police').search_count(cr,uid, [('state' , '=' , 'actif'), ('police_id' , '=' , police_id)]) == 0:
					raise osv.except_osv('Attention' , "Cette police ne possède pas d'exercice actif")


				dt_deb_exercice = exercice_data.date_debut_exercice
				dt_fin_exercice = exercice_data.date_fin_exercice

				deb = datetime.strptime(str(dt_deb_exercice), '%Y-%m-%d')
				fin = datetime.strptime(str(dt_fin_exercice), '%Y-%m-%d')


				nbre_mois_exercice = relativedelta(fin, deb)
				nbre_jour_exercice = nbre_mois_exercice.days
				nbre_mois_exercice = nbre_mois_exercice.months
				mois_a_acourir = nbre_mois_exercice + 1
				jours_a_acourir = nbre_jour_exercice

				

				if data.typ_prime == 1:

					if int(mode_repar_prime) == 1:

						prime_assure = (prime_assure * mois_a_acourir) / 12.0
						prime_sida = (prime_sida * mois_a_acourir) / 12.0
						somme_prime = prime_assure + prime_sida

					else:
						
						prime_assure = (prime_assure * jours_a_acourir) / 365
						prime_sida = (prime_sida * jours_a_acourir) / 365
						somme_prime = prime_assure + prime_sida
							
				return {'value': {'souscripteur_id': data.souscripteur_id['id'], 'courtier_id': data.courtier_id['id'],
						'dt_emi_ave': data.dt_emi_ave, 'dt_fin_ave': data.dt_fin_exercice,
						'date_effet_police': data.dt_effet, 'deb_periode': data.dt_deb_exercice,
						'fin_periode': data.dt_fin_exercice, 'affiche': True, 'repartition_prime': data.repartition_prime, 
						'periodicite_paiem': data.periodicite_paiem['id'], 'imputation_acc_courtier': data.imputation_acc_courtier,
						'imputation_acc_cie': data.imputation_acc_cie , 'prime_tot_sans_sida' : prime_assure , 'prime_sida' : prime_sida , 'mnt_quittance_emis' : somme_prime , 'show_exoneration' : data.taxe_exon , 'show_intermediaire' : data.imputation_acc_courtier , 'show_taxe' : data.tva_oui_non , 'show_gestionnaire' : data.imputation_acc_gestionnaire , 'show_garant' : data.imputation_acc_cie , 'show_taxe_enreg' : data.taxe_enreg}}

			# Avenant d'appel de prime'
			if code_avenant == 'AA':
				# je recupere tous les benef actifs de la  police
				les_benef_search = self.pool.get('mcisogem.benef').search(cr,uid,[('police_id','=',police_id)])
				les_benef_police = self.pool.get('mcisogem.benef').browse(cr,uid,les_benef_search)

				for benef in les_benef_police:

					statut_benef = benef.statut_benef.id
					l_histo_prime_search = self.pool.get('mcisogem.histo.prime').search(cr,uid,[('police_id','=',police_id) , ('statut_benef_id' , '=' , statut_benef)])
				
					for l_histo_prime_data in self.pool.get('mcisogem.histo.prime').browse(cr,uid,l_histo_prime_search):

						prime_assure += l_histo_prime_data.prim_assure
						prime_sida += l_histo_prime_data.prime_sida


				cr.execute('select repartition_prime from mcisogem_police where id=%s', (police_id,)) 
				mode_repar_prime = cr.fetchone()[0]

				exercice_search = self.pool.get('mcisogem.exercice.police').search(cr,uid, [('state' , '=' , 'actif') , ('police_id' , '=' , police_id)])
				exercice_data = self.pool.get('mcisogem.exercice.police').browse(cr,uid,exercice_search)

				if self.pool.get('mcisogem.exercice.police').search_count(cr,uid, [('state' , '=' , 'actif'), ('police_id' , '=' , police_id)]) == 0:
					raise osv.except_osv('Attention' , "Cette police ne possède pas d'exercice actif")


				dt_deb_exercice = exercice_data.date_debut_exercice
				dt_fin_exercice = exercice_data.date_fin_exercice

				deb = datetime.strptime(str(dt_deb_exercice), '%Y-%m-%d')
				fin = datetime.strptime(str(dt_fin_exercice), '%Y-%m-%d')


				nbre_mois_exercice = relativedelta(fin, deb)
				nbre_jour_exercice = nbre_mois_exercice.days
				nbre_mois_exercice = nbre_mois_exercice.months
				mois_a_acourir = nbre_mois_exercice + 1
				jours_a_acourir = nbre_jour_exercice

				

				if data.typ_prime == 1:

					if int(mode_repar_prime) == 1:

						prime_assure = (prime_assure * mois_a_acourir) / 12.0
						prime_sida = (prime_sida * mois_a_acourir) / 12.0
						somme_prime = prime_assure + prime_sida

					else:
						
						prime_assure = (prime_assure * jours_a_acourir) / 365
						prime_sida = (prime_sida * jours_a_acourir) / 365
						somme_prime = prime_assure + prime_sida
							

				return {'value': {'souscripteur_id': data.souscripteur_id['id'], 'courtier_id': data.courtier_id['id'],
						'dt_emi_ave': data.dt_emi_ave, 'dt_fin_ave': data.dt_fin_exercice,
						'date_effet_police': data.dt_effet, 'deb_periode': data.dt_deb_exercice,
						'fin_periode': data.dt_fin_exercice, 'affiche': True, 'repartition_prime': data.repartition_prime, 
						'periodicite_paiem': data.periodicite_paiem['id'], 'imputation_acc_courtier': data.imputation_acc_courtier,
						'imputation_acc_cie': data.imputation_acc_cie , 'prime_tot_sans_sida' : prime_assure , 'prime_sida' : prime_sida , 'mnt_quittance_emis' : somme_prime , 'show_exoneration' : data.taxe_exon , 'show_intermediaire' : data.imputation_acc_courtier , 'show_taxe' : data.tva_oui_non , 'show_gestionnaire' : data.imputation_acc_gestionnaire , 'show_garant' : data.imputation_acc_cie , 'show_taxe_enreg' : data.taxe_enreg}}

			# Avenant de modification de barème
			if code_avenant == 'AB':
				prime_assure = 0
				prime_sida = 0

				cr.execute("select distinct college_id from mcisogem_benef where police_id=%s", (police_id,))
				lescolleges = cr.dictfetchall()     


				for college in lescolleges:


					college_search = self.pool.get('mcisogem.college').search(cr,uid,[('id' , '=' , college['college_id'] )])
					college_data = self.pool.get('mcisogem.college').browse(cr,uid,college_search)

					cr.execute("select distinct statut_benef from mcisogem_benef where police_id =%s and college_id=%s", (police_id, college['college_id']))
					lesstatuts = cr.dictfetchall()

					#On parcours les statut de bénéficiaire
					for statut in lesstatuts:

						cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id=%s order by id DESC LIMIT 2", (college['college_id'], police_id, statut['statut_benef'],))
						lesprimes = cr.dictfetchall()
						
						prime_1 = 0
						prime_1_sida = 0

						prime_2 = 0
						prime_2_sida = 0

						if len(lesprimes) > 1:

							prime_1 = lesprimes[0]['prim_assure']
							prime_1_sida = lesprimes[0]['prime_sida']

							prime_2 = lesprimes[1]['prim_assure']
							prime_2_sida = lesprimes[0]['prime_sida']

						diff_prime = prime_1 - prime_2
						diff_prime_sida = prime_2_sida - prime_1_sida

						prime = lesprimes[0]
							
						dt_fin_prime = prime['dt_echea_pol']
						dt_effet_prime = prime['dt_eff_mod_prime']

						dt_fin_prime = datetime.strptime(str(dt_fin_prime), '%Y-%m-%d')
						dt_effet_prime = datetime.strptime(str(dt_effet_prime), '%Y-%m-%d')


						cr.execute("select  * from mcisogem_benef where statut != 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s", (police_id, statut['statut_benef'] , college['college_id'], dt_fin_prime))
						lesbenefs = cr.dictfetchall()


						cr.execute("select  * from mcisogem_benef where statut = 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s and date_exclusion between %s and %s", (police_id, statut['statut_benef'] , college['college_id'], dt_fin_prime , dt_effet_prime ,dt_fin_prime))
						lesbenefs_r = cr.dictfetchall()

						for benef in lesbenefs:
							
							dt_effet_benef = datetime.strptime(str(benef['dt_effet']), '%Y-%m-%d')
							
							if dt_effet_benef < dt_effet_prime:
								dt_effet_benef = dt_effet_prime

							nbre_mois = relativedelta(dt_fin_prime, dt_effet_benef).months + 1
							
							prime_assure += (diff_prime * nbre_mois ) / 12.0
							prime_sida += (diff_prime_sida * nbre_mois ) / 12.0

						for benef in lesbenefs_r:

							dt_fin_benef = dt_fin_prime
							
							if benef['date_exclusion']:
								dt_fin_benef = datetime.strptime(str(benef['date_exclusion']), "%Y-%m-%d %H:%M:%S")

							
							dt_effet_benef = datetime.strptime(str(benef['dt_effet']), '%Y-%m-%d')


							if dt_effet_benef < dt_effet_prime:
								dt_effet_benef = dt_effet_prime


							if dt_fin_benef < dt_fin_prime:
								dt_fin_prime = dt_fin_benef


							nbre_mois = relativedelta(dt_fin_prime, dt_effet_benef).months + 1

							prime_assure += (diff_prime * nbre_mois ) / 12.0
							prime_sida += (diff_prime_sida * nbre_mois ) / 12.0
						
					prime_assure = round(prime_assure)
					prime_sida = round(prime_sida)

				somme_prime = prime_assure + prime_sida

				return {'value': {'souscripteur_id': data.souscripteur_id['id'], 'courtier_id': data.courtier_id['id'],
					'dt_emi_ave': data.dt_emi_ave, 'dt_fin_ave': data.dt_fin_exercice,
					'date_effet_police': data.dt_effet, 'deb_periode': data.dt_deb_exercice,
					'fin_periode': data.dt_fin_exercice, 'affiche': True, 'repartition_prime': data.repartition_prime, 
					'periodicite_paiem': data.periodicite_paiem['id'], 'imputation_acc_courtier': data.imputation_acc_courtier,
					'imputation_acc_cie': data.imputation_acc_cie , 'prime_tot_sans_sida' : prime_assure , 'prime_sida' : prime_sida , 'mnt_quittance_emis' : somme_prime , 'show_exoneration' : data.taxe_exon , 'show_intermediaire' : data.imputation_acc_courtier , 'show_taxe' : data.tva_oui_non , 'show_gestionnaire' : data.imputation_acc_gestionnaire , 'show_garant' : data.imputation_acc_cie , 'show_taxe_enreg' : data.taxe_enreg}}

			#Avenant de Mouvement
			if code_avenant == 'AM':
				prime_assure = 0
				prime_sida = 0
				prime_assure_r = 0
				prime_sida_r = 0
				cr.execute("select distinct college_id from mcisogem_benef where police_id=%s", (police_id,))
				lescolleges = cr.dictfetchall()     


				for college in lescolleges:
					college_search = self.pool.get('mcisogem.college').search(cr,uid,[('id' , '=' , college['college_id'] )])
					college_data = self.pool.get('mcisogem.college').browse(cr,uid,college_search)

					cr.execute("select distinct statut_benef from mcisogem_benef where police_id=%s and college_id=%s and valide_quittance != 2", (police_id, college['college_id']))
					lesstatuts = cr.dictfetchall()


					#On parcours les statut de bénéficiaire
					for statut in lesstatuts:

						cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id=%s order by id ASC", (college['college_id'], police_id, statut['statut_benef'],))
						lesprimes = cr.dictfetchall()
						
						for prime in lesprimes:
							dt_fin_prime = prime['dt_echea_pol']
							dt_effet_prime = prime['dt_eff_mod_prime']


							dt_fin_prime = datetime.strptime(str(dt_fin_prime), '%Y-%m-%d')
							dt_effet_prime = datetime.strptime(str(dt_effet_prime), '%Y-%m-%d')

							cr.execute("select  * from mcisogem_benef where police_id=%s and statut_benef=%s and college_id=%s and creat_incorpo = %s and dt_effet <= %s and valide_quittance != %s", (police_id, statut['statut_benef'] , college['college_id'], 'I', dt_fin_prime , 2))

							lesbenefs = cr.dictfetchall()

							
							for benef in lesbenefs:

								dt_effet_benef = datetime.strptime(str(benef['dt_effet']), '%Y-%m-%d')

								if dt_effet_benef < dt_effet_prime:
									dt_effet_benef = dt_effet_prime


								nbre_mois = relativedelta(dt_fin_prime, dt_effet_benef).months + 1
								prime_assure += (prime['prim_assure'] * nbre_mois ) / 12.0
								prime_sida += (prime['prime_sida'] * nbre_mois ) / 12.0

								
							prime_assure = round(prime_assure)
							prime_sida = round(prime_sida)

							# cr.execute("select  * from mcisogem_benef where statut = 'R' and police_id=%s and valide_quittance != 2 and statut_benef=%s and college_id=%s and dt_effet <= %s and date_exclusion between %s and %s", (police_id, statut['statut_benef'] , college['college_id'], dt_fin_prime , dt_effet_prime , dt_fin_prime))
							# lesbenefs = cr.dictfetchall()

							
							# for benef in lesbenefs:

							# 	dt_excl_benef = datetime.strptime(str(benef['date_exclusion']), "%Y-%m-%d %H:%M:%S")
							# 	dt_excl_benef = dt_excl_benef.date()

							# 	nbre_mois = relativedelta(dt_fin_prime, dt_excl_benef).months

							# 	prime_assure_r += (prime['prim_assure'] * nbre_mois ) / 12.0
							# 	prime_sida_r += (prime['prime_sida'] * nbre_mois ) / 12.0


							cr.execute("select  * from mcisogem_benef where statut = 'R' and police_id=%s and valide_quittance = 0 and statut_benef=%s and college_id=%s", (police_id, statut['statut_benef'] , college['college_id']))
							lesbenefs = cr.dictfetchall()

							for benef in lesbenefs:

								dt_excl_benef = datetime.strptime(str(benef['date_exclusion']), "%Y-%m-%d %H:%M:%S")
								dt_excl_benef = dt_excl_benef.date()

								if dt_excl_benef < dt_effet_prime.date():
									dt_excl_benef = dt_effet_prime
									nbre_mois = relativedelta(dt_fin_prime, dt_excl_benef).months + 1
								else:

									nbre_mois = relativedelta(dt_fin_prime, dt_excl_benef).months


								prime_assure_r += (prime['prim_assure'] * nbre_mois ) / 12.0
								prime_sida_r += (prime['prime_sida'] * nbre_mois ) / 12.0


						prime_assure_r = round(prime_assure_r)
						prime_sida_r = round(prime_sida_r)

						prime_assure = prime_assure - prime_assure_r
						prime_sida = prime_sida - prime_sida_r

				somme_prime = prime_assure + prime_sida

				return {'value': {'souscripteur_id': data.souscripteur_id['id'], 'courtier_id': data.courtier_id['id'],
					'dt_emi_ave': data.dt_emi_ave, 'dt_fin_ave': data.dt_fin_exercice,
					'date_effet_police': data.dt_effet, 'deb_periode': data.dt_deb_exercice,
					'fin_periode': data.dt_fin_exercice, 'affiche': True, 'repartition_prime': data.repartition_prime, 
					'periodicite_paiem': data.periodicite_paiem['id'], 'imputation_acc_courtier': data.imputation_acc_courtier,
					'imputation_acc_cie': data.imputation_acc_cie , 'prime_tot_sans_sida' : prime_assure , 'prime_sida' : prime_sida , 'mnt_quittance_emis' : somme_prime , 'show_exoneration' : data.taxe_exon , 'show_intermediaire' : data.imputation_acc_courtier , 'show_taxe' : data.tva_oui_non , 'show_gestionnaire' : data.imputation_acc_gestionnaire , 'show_garant' : data.imputation_acc_cie , 'show_taxe_enreg' : data.taxe_enreg}}

			if code_avenant == 'AR':
				nbre_avenant_fact = self.pool.get('mcisogem.quittancier').search_count(cr,uid,[('police_id' , '=' , police_id) , ('type_avenant_id' , '=' , avenant_fact)])

				if nbre_avenant_fact == 0:
					raise osv.except_osv('Attention' , 'Aucun Avenant de facturation n\'a été émis pour cette police')

				prime_assure = 0
				prime_sida = 0

				cr.execute("select distinct college_id from mcisogem_benef where police_id=%s", (police_id,))
				lescolleges = cr.dictfetchall()     

				for college in lescolleges:
					college_search = self.pool.get('mcisogem.college').search(cr,uid,[('id' , '=' , college['college_id'] )])
					college_data = self.pool.get('mcisogem.college').browse(cr,uid,college_search)

					cr.execute("select distinct statut_benef from mcisogem_benef where police_id =%s and college_id=%s", (police_id, college['college_id']))
					lesstatuts = cr.dictfetchall()

					premiere_prime_assur  = 0
					premiere_prime_sida  = 0

					#On parcours les statut de bénéficiaire
					for statut in lesstatuts:

						cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id=%s order by id ASC", (college['college_id'], police_id, statut['statut_benef'],))
						lesprimes = cr.dictfetchall()
						
						for prime in lesprimes:
							dt_fin_prime = prime['dt_echea_pol']
							dt_effet_prime = prime['dt_eff_mod_prime']

							dt_fin_prime = datetime.strptime(str(dt_fin_prime), '%Y-%m-%d')
							dt_effet_prime = datetime.strptime(str(dt_effet_prime), '%Y-%m-%d')


							cr.execute("select  * from mcisogem_benef where police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s", (police_id, statut['statut_benef'] , college['college_id'], dt_fin_prime))
							lesbenefs = cr.dictfetchall()


							for benef in lesbenefs:
								dt_fin_prime = prime['dt_echea_pol']
								dt_effet_prime = prime['dt_eff_mod_prime']

								dt_fin_prime = datetime.strptime(str(dt_fin_prime), '%Y-%m-%d')
								dt_effet_prime = datetime.strptime(str(dt_effet_prime), '%Y-%m-%d')

								dt_effet_benef = datetime.strptime(str(benef['dt_effet']), '%Y-%m-%d')
								dt_fin_benef = dt_fin_prime

								if benef['statut'] == 'R':
									dt_fin_benef = datetime.strptime(str(benef['date_exclusion']), '%Y-%m-%d %H:%M:%S').date()
									dt_fin_prime = dt_fin_benef

								if dt_effet_benef < dt_effet_prime:
									dt_effet_benef = dt_effet_prime

								nbre_mois = relativedelta(dt_fin_prime, dt_effet_benef).months + 1
								
								prime_assure += (prime['prim_assure'] * nbre_mois ) / 12.0
								prime_sida += (prime['prime_sida'] * nbre_mois ) / 12.0

						prime_assure = round(prime_assure)
						prime_sida = round(prime_sida)

				prime_reste = 0
				prime_sida_reste = 0
				somme_reste = 0

				les_avenants_fact = self.pool.get('mcisogem.quittancier').search(cr,uid,[('police_id' , '=' , police_id) , ('type_avenant_id' , '=' , avenant_fact)])

				for les_avenants_fact_data in self.pool.get('mcisogem.quittancier').browse(cr,uid,les_avenants_fact):
					prime_reste += les_avenants_fact_data.prime_tot_sans_sida
					prime_sida_reste += les_avenants_fact_data.prime_sida

				# somme_reste = prime_reste + prime_sida_reste

				prime_assure = prime_assure - prime_reste
				prime_sida = prime_sida - prime_sida_reste

				somme_prime = prime_assure + prime_sida

				return {'value': {'souscripteur_id': data.souscripteur_id['id'], 'courtier_id': data.courtier_id['id'],
					'dt_emi_ave': data.dt_emi_ave, 'dt_fin_ave': data.dt_fin_exercice,
					'date_effet_police': data.dt_effet, 'deb_periode': data.dt_deb_exercice,
					'fin_periode': data.dt_fin_exercice, 'affiche': True, 'repartition_prime': data.repartition_prime, 
					'periodicite_paiem': data.periodicite_paiem['id'], 'imputation_acc_courtier': data.imputation_acc_courtier,
					'imputation_acc_cie': data.imputation_acc_cie , 'prime_tot_sans_sida' : prime_assure , 'prime_sida' : prime_sida , 'mnt_quittance_emis' : somme_prime , 'show_exoneration' : data.taxe_exon , 'show_intermediaire' : data.imputation_acc_courtier , 'show_taxe' : data.tva_oui_non , 'show_gestionnaire' : data.imputation_acc_gestionnaire , 'show_garant' : data.imputation_acc_cie , 'show_taxe_enreg' : data.taxe_enreg}}


	def check_etat_police(self,cr,uid, police_id):
		# cette fonction retourne l'état de la police qu'on lui passe en paramètre 
		police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
		police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)
		return police_data.state


	def details_police(self,cr,uid, police_id):
		# cette fonction retourne les détails sur une police  donnée
		police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
		police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)

		return police_data


	def button_to_edit(self, cr, uid, ids, vals, context=None):
		return super(mcisogem_quittancier, self).write(cr, uid, ids, vals, context=context)


	def create(self, cr, uid, data, context=None):        

		statut_police = self.check_etat_police(cr,uid,data['police_id'])
		police_data = self.details_police(cr,uid,data['police_id'])



		if police_data.imputation_acc_cie == False:
			data['type_accessoires_assureur'] = False


			data['mnt_accessoires_assureur'] = 0
			# data['mnt_accessoires_courtier'] = 0



		if police_data.imputation_acc_courtier == False:
			data['type_accessoires_courtier'] = False

			# data['mnt_accessoires_assureur'] = 0
			data['mnt_accessoires_courtier'] = 0



		if police_data.imputation_acc_gestionnaire == False:
			data['type_mnt_accessoires_gest'] = False
			data['mnt_accessoires_gest'] = 0



		# if police_data.tva_oui_non == False:


		if police_data.taxe_enreg == False:
			data['type_mnt_taxe'] = False
			data['mnt_taxe'] = 0


		if police_data.taxe_exon == False:
			data['exoneration'] = 0




		#on verifie s'il existe des bénéficiaires dans la police
		nbre_benef = self.pool.get('mcisogem.benef').search_count(cr,uid,[('police_id' , '=' , data['police_id'])])

		if nbre_benef == 0:
			raise osv.except_osv('Attention' , "Il n'existe aucun bénéficiaire(s) dans cette police")

		#Vérifier si la police est acive
		nbre_ave = self.pool.get('mcisogem.avenant').search_count(cr,uid,[('police_id' , '=' , data['police_id']) , ('type_avenant_id' , '=' , data['type_avenant_id']) , ('state' , '=' , 'valid')])


		if nbre_ave == 0:
			raise osv.except_osv('Attention' , "Vous devez d'abord créé un avenant de ce type sur la police")


		#Vérifier si la période est incluse dans l'exercice de la police 
		cr.execute('select repartition_prime from mcisogem_police where id=%s', (data['police_id'],)) 
		mode_repar_prime = cr.fetchone()[0]


		exercice_search = self.pool.get('mcisogem.exercice.police').search(cr,uid, [('state' , '=' , 'actif') , ('police_id' , '=' , data['police_id'])])
		exercice_data = self.pool.get('mcisogem.exercice.police').browse(cr,uid,exercice_search)

		if self.pool.get('mcisogem.exercice.police').search(cr,uid, [('state' , '=' , 'actif') , ('police_id' , '=' , data['police_id'])]) == 0:
			raise osv.except_osv('Attention' , "Cette police ne possède pas d'exercice actif")

			
		dt_deb_exercice = exercice_data.date_debut_exercice
		dt_fin_exercice = exercice_data.date_fin_exercice

		obj_pol_data = self.pool.get('mcisogem.police').browse(cr, uid, data['police_id'], context=context)
		deb = datetime.strptime(str(dt_deb_exercice), '%Y-%m-%d')
		fin = datetime.strptime(str(dt_fin_exercice), '%Y-%m-%d')


		nbre_mois_exercice = relativedelta(fin, deb)
		nbre_jour_exercice = nbre_mois_exercice.days
		nbre_mois_exercice = nbre_mois_exercice.months

		avenant_search = self.pool.get('mcisogem.type.avenant').search(cr,uid,[('id' , '=' , data['type_avenant_id'])])
		code_avenant = self.pool.get('mcisogem.type.avenant').browse(cr,uid,avenant_search).code_type_avenant

		code_avenant_quittance =  self.pool.get('mcisogem.quittancier').search_count(cr, uid, [('police_id', '=', data['police_id']) , ('avenan_libelle' , '=' , 'AI')])
		
		data['state'] = 'sent'

		

		pol = self.pool.get('mcisogem.police').search(cr,uid,[('id' , '=' , data['police_id'])])

		pol_data = self.pool.get('mcisogem.police').browse(cr,uid,pol)


		data['souscripteur_id'] = pol_data.souscripteur_id['id'] 
		data['courtier_id'] = pol_data.courtier_id['id']    
		data['dt_emi_ave'] = pol_data.dt_emi_ave      
		data['dt_fin_ave'] = pol_data.dt_fin_ave   
		data['dt_effet'] = pol_data.dt_effet
		data['date_effet_police'] =  pol_data.dt_effet
		data['repartition_prime'] = pol_data.repartition_prime    
		data['periodicite_paiem'] = pol_data.periodicite_paiem['id']
		data['imputation_acc_courtier'] =pol_data.imputation_acc_courtier  
		data['imputation_acc_cie'] = pol_data.imputation_acc_cie
		data['duree_exercice'] = nbre_mois_exercice + 1

		ave = self.pool.get('mcisogem.avenant').search(cr,uid,[('type_avenant_id' , '=' , data['type_avenant_id']) , ('police_id' , '=' , data['police_id'])])

		data['avenant'] = self.pool.get('mcisogem.avenant').browse(cr,uid,ave).num_ave_interne_police

		mois_a_acourir = nbre_mois_exercice + 1
		jours_a_acourir = nbre_jour_exercice


		if code_avenant == 'ANN':

			if statut_police !='draft':
				raise osv.except_osv('Attention !', "La police sélectionnée n'est pas active !")


			valeurs = self.browse(cr,uid,data['quittance_id'])

			data['prime_tot_sans_sida'] = - (valeurs.prime_tot_sans_sida)
			data['prime_sida'] = - (valeurs.prime_sida)
			data['taxe_acc_nostro'] = - (valeurs.taxe_acc_nostro)
			data['taxe_acc_assureur'] = - valeurs.taxe_acc_assureur
			data['taxe_acc_courtier'] = - valeurs.taxe_acc_courtier

			data['cout_d_acte1'] = - valeurs.cout_d_acte1
			data['cout_d_acte0'] = - valeurs.cout_d_acte0
			data['cout_d_acte_assur'] = - valeurs.cout_d_acte_assur
			data['cout_d_acte_courtier'] = - valeurs.cout_d_acte_courtier

			data['type_accessoires_courtier'] = valeurs.type_accessoires_courtier
			data['type_mnt_taxe'] = valeurs.type_mnt_taxe
			data['type_accessoires_assureur'] = valeurs.type_accessoires_assureur
			data['type_mnt_accessoires_gest'] = valeurs.type_mnt_accessoires_gest
			data['type_mnt_comxion_courtier'] = valeurs.type_mnt_comxion_courtier
			data['type_mnt_comxion_gest'] = valeurs.type_mnt_comxion_gest

			data['total_plus_access'] = - valeurs.total_plus_access
			data['mnt_taxe_prime0'] = - valeurs.mnt_taxe_prime0
			data['mnt_quittance_emis']= - valeurs.mnt_quittance_emis
			data['mnt_glob0'] = - valeurs.mnt_glob0
			data['objet_particulier'] = valeurs.objet_particulier

			data['mnt_taxe_prime0'] = - valeurs.mnt_taxe_prime0
			data['mnt_accessoires_gest'] = - valeurs.mnt_accessoires_gest
			data['mnt_accessoires_assureur'] = - valeurs.mnt_accessoires_assureur
			data['mnt_TVA'] = - valeurs.mnt_TVA
			data['mnt_glob1'] = - valeurs.mnt_glob1
			data['mnt_comxion_gest'] = - valeurs.mnt_comxion_gest
			data['mnt_comxion_courtier'] = - valeurs.mnt_comxion_courtier
			data['mnt_accessoires_courtier'] = - valeurs.mnt_accessoires_courtier

			return super(mcisogem_quittancier, self).create(cr, uid, data, context=context)

		if code_avenant == 'AS':

			if statut_police !='draft':
				raise osv.except_osv('Attention !', "La police sélectionnée n'est pas active !")

			data['mnt_quittance_emis'] = data['prime_tot_sans_sida']  + data['prime_sida'] 
			
			prime_net_total = data['prime_tot_sans_sida']
			prime_net_SIDA =  data['prime_sida']

			total_prime_net = data['mnt_quittance_emis']
			prime_net_SIDA_total = data['mnt_quittance_emis']
			
			data['base'] = data['mnt_quittance_emis']

			if code_avenant_quittance == 0:
				raise osv.except_osv('Attention' , "Aucune quittance de type <Avenant Initial> n'a été émise pour cette police")
				
			if code_avenant_quittance > 0:

				quittance_id = super(mcisogem_quittancier, self).create(cr, uid, data, context=context)

				quittance_data = self.browse(cr, uid, quittance_id, context=context)


				#On vérifie le type d'accessoire gestionnaire - Forfait ou pourcentage
				if data['type_mnt_accessoires_gest'] == True:
					mnt_accessoires_gest = round((total_prime_net * data['mnt_accessoires_gest']) / 100)
				else:
					mnt_accessoires_gest = data['mnt_accessoires_gest']	


				# accessoire intermediaire
				if data['type_accessoires_courtier'] == True:
					mnt_accessoires_interme = round((mnt_accessoires_gest * data['mnt_accessoires_courtier']) / 100)
				else:
					mnt_accessoires_interme = data['mnt_accessoires_courtier']



				#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
				if data['type_accessoires_assureur'] == True:
					mnt_accessoires_assureur = round((mnt_accessoires_gest * data['mnt_accessoires_assureur']) / 100)
				else:
					mnt_accessoires_assureur = data['mnt_accessoires_assureur']

				total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur

				#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
				if data['type_mnt_comxion_gest'] == True:
					mnt_comxion_gest = round((total_prime_net * data['mnt_comxion_gest']) / 100)
				else:
					mnt_comxion_gest = data['mnt_comxion_gest']


				#On vérifie le type de commission du courtier - Forfait ou pourcentage
				if data['type_mnt_comxion_courtier'] == True:
					mnt_comxion_courtier = round((total_prime_net * data['mnt_comxion_courtier']) / 100)
				else:
					mnt_comxion_courtier = data['mnt_comxion_courtier']


				total_commission = mnt_comxion_courtier + mnt_comxion_gest

				#On vérifie le type de montant taxe - Forfait ou pourcentage
				if data['type_mnt_taxe'] == True:
					taux_taxe = round((total_prime_net * data['mnt_taxe']) / 100)
				else:
					taux_taxe = data['mnt_taxe']

				montant_hc_plus_access = total_prime_net + total_accessoires 

				if data['type_mnt_taxe'] == True:
					taxe_enregistrement = round((montant_hc_plus_access * data['mnt_taxe']) / 100)
				else:
					taxe_enregistrement = data['mnt_taxe']


				montant_ttc = montant_hc_plus_access+ taxe_enregistrement

				cr.execute('update mcisogem_quittancier set prime_tot_sans_sida=%s, prime_sida=%s , mnt_quittance_emis = %s , taxe_acc_nostro = %s , taxe_acc_courtier = %s , taxe_acc_assureur =%s ,cout_d_acte1=%s , cout_d_acte=%s , cout_d_acte_courtier = %s , cout_d_acte0 = %s, mnt_taxe_prime0 = %s , mnt_glob0=%s , total_plus_access=%s , base=%s where id = %s' , (prime_net_total ,prime_net_SIDA,total_prime_net,mnt_accessoires_gest,mnt_accessoires_interme, mnt_accessoires_assureur ,total_accessoires,mnt_comxion_gest,mnt_comxion_courtier,total_commission,taxe_enregistrement,montant_ttc,montant_hc_plus_access,total_prime_net,quittance_id ))


				return quittance_id

		if code_avenant == 'ARS':

			if self.check_etat_police(cr,uid,data['police_id'] ) != 'resil':
				raise osv.except_osv('Attention' , 'Cette police n\' a pas été résiliée')


			les_valeurs  = self.onchange_police(cr, uid,  0 , data['police_id'] , data['type_avenant_id'])['value']

			total_prime_net = les_valeurs['mnt_quittance_emis']	
			type_prime = self.details_police(cr,uid,data['police_id']).type_prime
			prime_net_total = les_valeurs['prime_tot_sans_sida']
			prime_net_SIDA =  les_valeurs['prime_sida'] 
			prime_net_SIDA_total = les_valeurs['mnt_quittance_emis']


			if code_avenant_quittance > 0:

				quittance_id = super(mcisogem_quittancier, self).create(cr, uid, data, context=context)

				quittance_data = self.browse(cr, uid, quittance_id, context=context)
			

				#Vérifier si police par statut bénéficiaire
				if type_prime == '1':

						
					#On vérifie le type d'accessoire gestionnaire - Forfait ou pourcentage
					if data['type_mnt_accessoires_gest'] == True:
						mnt_accessoires_gest = round((total_prime_net * data['mnt_accessoires_gest']) / 100)
					else:
						mnt_accessoires_gest = data['mnt_accessoires_gest']	

					# accessoire intermediaire
					if data['type_accessoires_courtier'] == True:
						mnt_accessoires_interme = round((mnt_accessoires_gest * data['mnt_accessoires_courtier']) / 100)
					else:
						mnt_accessoires_interme = data['mnt_accessoires_courtier']


					#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
					if data['type_accessoires_assureur'] == True:
						mnt_accessoires_assureur = round((mnt_accessoires_gest * data['mnt_accessoires_assureur']) / 100)
					else:
						mnt_accessoires_assureur = data['mnt_accessoires_assureur']



					total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur



					#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
					if data['type_mnt_comxion_gest'] == True:
						mnt_comxion_gest = round((total_prime_net * data['mnt_comxion_gest']) / 100)
					else:
						mnt_comxion_gest = data['mnt_comxion_gest']


					#On vérifie le type de commission du courtier - Forfait ou pourcentage
					if data['type_mnt_comxion_courtier'] == True:
						mnt_comxion_courtier = round((total_prime_net * data['mnt_comxion_courtier']) / 100)
					else:
						mnt_comxion_courtier = data['mnt_comxion_courtier']


					total_commission = mnt_comxion_courtier + mnt_comxion_gest

					#On vérifie le type de montant taxe - Forfait ou pourcentage
					if data['type_mnt_taxe'] == True:
						taux_taxe = round((total_prime_net * data['mnt_taxe']) / 100)
					else:
						taux_taxe = data['mnt_taxe']

					montant_hc_plus_access = total_prime_net + total_accessoires 

					if data['type_mnt_taxe'] == True:
						taxe_enregistrement = round((montant_hc_plus_access * data['mnt_taxe']) / 100)
					else:
						taxe_enregistrement = data['mnt_taxe']


					montant_ttc = montant_hc_plus_access+ taxe_enregistrement

					
					cr.execute('update mcisogem_quittancier set prime_tot_sans_sida=%s, prime_sida=%s , mnt_quittance_emis = %s , taxe_acc_nostro = %s , taxe_acc_courtier = %s , taxe_acc_assureur =%s ,cout_d_acte1=%s , cout_d_acte=%s , cout_d_acte_courtier = %s , cout_d_acte0 = %s, mnt_taxe_prime0 = %s , mnt_glob0=%s , total_plus_access=%s , base=%s where id = %s' , (prime_net_total ,prime_net_SIDA,total_prime_net,mnt_accessoires_gest,mnt_accessoires_interme, mnt_accessoires_assureur ,total_accessoires,mnt_comxion_gest,mnt_comxion_courtier,total_commission,taxe_enregistrement,montant_ttc,montant_hc_plus_access,total_prime_net,quittance_id ))

					cr.execute("select distinct college_id from mcisogem_benef where police_id=%s", (data['police_id'],))
					lescolleges = cr.dictfetchall()
					prime_net_total = 0
					prime_net_SIDA_total = 0

					#On parcours les colleges
					for college in lescolleges:

						college_search = self.pool.get('mcisogem.college').search(cr,uid,[('id' , '=' , college['college_id'])])

						college_data = self.pool.get('mcisogem.college').browse(cr,uid,college_search)


						cr.execute("select distinct statut_benef from mcisogem_benef where police_id =%s and college_id=%s", (data['police_id'], college['college_id']))

						lesstatuts = cr.dictfetchall()


						#On parcours les statuts de bénéficiaire
						for statut in lesstatuts:

							prime_statut_assure = 0
							prime_statut_assure_sida = 0
							prime_statut_assure_r = 0
							prime_statut_assure_sida_r = 0

							statut_data = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut['statut_benef'])

							cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id = %s ORDER BY id ASC", (college['college_id'], data['police_id'] , statut['statut_benef']))

							#on parcours toutes les primes qui ont été définies pour le statut en cours
							lesprimes = cr.dictfetchall()


							for prime in lesprimes:

								dt_fin_prime = datetime.strptime(str(prime['dt_echea_pol']), '%Y-%m-%d')

								dt_effet_prime = datetime.strptime(str(prime['dt_eff_mod_prime']), '%Y-%m-%d')

								# on parcours les bénéficiaires incorporés concernés par la prime en cours

								cr.execute("select  * from mcisogem_benef where statut != 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s", (data['police_id'], statut['statut_benef'] , college['college_id'], dt_fin_prime))


								lesbenefs = cr.dictfetchall()
								nbre_benef_incorpo = len(lesbenefs)

								# on parcours les bénéficiaires incorporés concernés par la prime en cours

								cr.execute("select  * from mcisogem_benef where statut = 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s", (data['police_id'], statut['statut_benef'] , college['college_id'], dt_fin_prime))

								lesbenefs_retire = cr.dictfetchall()
								nbre_benef_retrait = len(lesbenefs_retire)


								prime_assure = 0
								prime_sida = 0

								prime_assure_r = 0
								prime_sida_r = 0

								for benef in lesbenefs:

									dt_effet_benef = datetime.strptime(str(benef['dt_effet']), '%Y-%m-%d')

									dt_fin_exercice = datetime.strptime(str(quittance_data.deb_periode), '%Y-%m-%d')
									dt_deb_exercice = datetime.strptime(str(quittance_data.fin_periode), '%Y-%m-%d')


									nbre_mois = relativedelta(dt_fin_exercice, dt_deb_exercice).months + 1

									nbre_mois_benef = relativedelta(dt_fin_prime, dt_effet_benef).months + 1

									prime_assure += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
									prime_sida += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

									prime_statut_assure += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
									prime_statut_assure_sida += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

								for benef_r in lesbenefs_retire:

									dt_effet_benef = datetime.strptime(str(benef_r['dt_effet']), '%Y-%m-%d')
									dt_retrait_benef = datetime.strptime(str(benef_r['date_exclusion']), '%Y-%m-%d %H:%M:%S')
									dt_fin_exercice = datetime.strptime(str(quittance_data.deb_periode), '%Y-%m-%d')
									dt_deb_exercice = datetime.strptime(str(quittance_data.fin_periode), '%Y-%m-%d')
									nbre_mois = relativedelta(dt_fin_exercice, dt_deb_exercice).months + 1

									nbre_mois_benef = relativedelta(dt_fin_exercice, dt_retrait_benef).months

									prime_assure_r += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
									prime_sida_r += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

									prime_statut_assure_r += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
									prime_statut_assure_sida_r += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

							if nbre_benef_incorpo > 0:

								cr.execute("insert into mcisogem_detail_quittancier (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot ) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
									(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',nbre_benef_incorpo,nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime_statut_assure,prime_statut_assure_sida,prime_statut_assure_sida + prime_statut_assure,prime_statut_assure_sida)
								)

							if nbre_benef_retrait > 0:

								cr.execute("insert into mcisogem_detail_quittancier_retrait (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
									(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',nbre_benef_retrait,nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime_statut_assure_r,prime_statut_assure_sida_r,prime_statut_assure_r + prime_statut_assure_sida_r,prime_statut_assure_sida_r)
								)



					return quittance_id


			else:
				raise osv.except_osv('Attention' , 'Aucun avenant Initial n\' a été calculé pour cette police')

		if code_avenant == 'AB':

			if statut_police !='draft':
				raise osv.except_osv('Attention !', "La police sélectionnée n'est pas active !")


			les_valeurs  = self.onchange_police(cr, uid,  0 , data['police_id'] , data['type_avenant_id'])['value']

			total_prime_net = les_valeurs['mnt_quittance_emis']	
			type_prime = self.details_police(cr,uid,data['police_id']).type_prime
			prime_net_total = les_valeurs['prime_tot_sans_sida']
			prime_net_SIDA =  les_valeurs['prime_sida'] 
			prime_net_SIDA_total = les_valeurs['mnt_quittance_emis']

			if code_avenant_quittance > 0:

				quittance_id = super(mcisogem_quittancier, self).create(cr, uid, data, context=context)

				quittance_data = self.browse(cr, uid, quittance_id, context=context)
			

				#Vérifier si police par statut bénéficiaire
				if type_prime == '1':

						
					#On vérifie le type d'accessoire gestionnaire - Forfait ou pourcentage
					if data['type_mnt_accessoires_gest'] == True:
						mnt_accessoires_gest = round((total_prime_net * data['mnt_accessoires_gest']) / 100)
					else:
						mnt_accessoires_gest = data['mnt_accessoires_gest']	


					# accessoire intermediaire
					if data['type_accessoires_courtier'] == True:
						mnt_accessoires_interme = round((mnt_accessoires_gest * data['mnt_accessoires_courtier']) / 100)
					else:
						mnt_accessoires_interme = data['mnt_accessoires_courtier']



					#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
					if data['type_accessoires_assureur'] == True:
						mnt_accessoires_assureur = round((mnt_accessoires_gest * data['mnt_accessoires_assureur']) / 100)
					else:
						mnt_accessoires_assureur = data['mnt_accessoires_assureur']



					total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur



					#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
					if data['type_mnt_comxion_gest'] == True:
						mnt_comxion_gest = round((total_prime_net * data['mnt_comxion_gest']) / 100)
					else:
						mnt_comxion_gest = data['mnt_comxion_gest']


					#On vérifie le type de commission du courtier - Forfait ou pourcentage
					if data['type_mnt_comxion_courtier'] == True:
						mnt_comxion_courtier = round((total_prime_net * data['mnt_comxion_courtier']) / 100)
					else:
						mnt_comxion_courtier = data['mnt_comxion_courtier']


					total_commission = mnt_comxion_courtier + mnt_comxion_gest

					#On vérifie le type de montant taxe - Forfait ou pourcentage
					if data['type_mnt_taxe'] == True:
						taux_taxe = round((total_prime_net * data['mnt_taxe']) / 100)
					else:
						taux_taxe = data['mnt_taxe']

					montant_hc_plus_access = total_prime_net + total_accessoires 

					if data['type_mnt_taxe'] == True:
						taxe_enregistrement = round((montant_hc_plus_access * data['mnt_taxe']) / 100)
					else:
						taxe_enregistrement = data['mnt_taxe']


					montant_ttc = montant_hc_plus_access+ taxe_enregistrement

					
					cr.execute('update mcisogem_quittancier set prime_tot_sans_sida=%s, prime_sida=%s , mnt_quittance_emis = %s , taxe_acc_nostro = %s , taxe_acc_courtier = %s , taxe_acc_assureur =%s ,cout_d_acte1=%s , cout_d_acte=%s , cout_d_acte_courtier = %s , cout_d_acte0 = %s, mnt_taxe_prime0 = %s , mnt_glob0=%s , total_plus_access=%s , base=%s where id = %s' , (prime_net_total ,prime_net_SIDA,total_prime_net,mnt_accessoires_gest,mnt_accessoires_interme, mnt_accessoires_assureur ,total_accessoires,mnt_comxion_gest,mnt_comxion_courtier,total_commission,taxe_enregistrement,montant_ttc,montant_hc_plus_access,total_prime_net,quittance_id ))


					return quittance_id

		if code_avenant == 'AM':

			if statut_police !='draft':
				raise osv.except_osv('Attention !', "La police sélectionnée n'est pas active !")


			les_valeurs  = self.onchange_police(cr, uid,  0 , data['police_id'] , data['type_avenant_id'])['value']
			total_prime_net = les_valeurs['mnt_quittance_emis']	
			type_prime = self.details_police(cr,uid,data['police_id']).type_prime
			prime_net_total = les_valeurs['prime_tot_sans_sida']
			prime_net_SIDA =  les_valeurs['prime_sida'] 
			prime_net_SIDA_total = les_valeurs['mnt_quittance_emis']

			if code_avenant_quittance > 0:

				quittance_id = super(mcisogem_quittancier, self).create(cr, uid, data, context=context)

				quittance_data = self.browse(cr, uid, quittance_id, context=context)


				#Vérifier si police par statut bénéficiaire
				if type_prime == '1':

						
					#On vérifie le type d'accessoire gestionnaire - Forfait ou pourcentage
					if data['type_mnt_accessoires_gest'] == True:
						mnt_accessoires_gest = round((total_prime_net * data['mnt_accessoires_gest']) / 100)
					else:
						mnt_accessoires_gest = data['mnt_accessoires_gest']	


					# accessoire intermediaire
					if data['type_accessoires_courtier'] == True:
						mnt_accessoires_interme = round((mnt_accessoires_gest * data['mnt_accessoires_courtier']) / 100)
					else:
						mnt_accessoires_interme = data['mnt_accessoires_courtier']



					#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
					if data['type_accessoires_assureur'] == True:
						mnt_accessoires_assureur = round((mnt_accessoires_gest * data['mnt_accessoires_assureur']) / 100)
					else:
						mnt_accessoires_assureur = data['mnt_accessoires_assureur']



					total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur



					#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
					if data['type_mnt_comxion_gest'] == True:
						mnt_comxion_gest = round((total_prime_net * data['mnt_comxion_gest']) / 100)
					else:
						mnt_comxion_gest = data['mnt_comxion_gest']


					#On vérifie le type de commission du courtier - Forfait ou pourcentage
					if data['type_mnt_comxion_courtier'] == True:
						mnt_comxion_courtier = round((total_prime_net * data['mnt_comxion_courtier']) / 100)
					else:
						mnt_comxion_courtier = data['mnt_comxion_courtier']


					total_commission = mnt_comxion_courtier + mnt_comxion_gest

					#On vérifie le type de montant taxe - Forfait ou pourcentage
					if data['type_mnt_taxe'] == True:
						taux_taxe = round((total_prime_net * data['mnt_taxe']) / 100)
					else:
						taux_taxe = data['mnt_taxe']

					montant_hc_plus_access = total_prime_net + total_accessoires 

					if data['type_mnt_taxe'] == True:
						taxe_enregistrement = round((montant_hc_plus_access * data['mnt_taxe']) / 100)
					else:
						taxe_enregistrement = data['mnt_taxe']

					montant_ttc = montant_hc_plus_access+ taxe_enregistrement

					cr.execute('update mcisogem_quittancier set prime_tot_sans_sida=%s, prime_sida=%s , mnt_quittance_emis = %s , taxe_acc_nostro = %s , taxe_acc_courtier = %s , taxe_acc_assureur =%s ,cout_d_acte1=%s , cout_d_acte=%s , cout_d_acte_courtier = %s , cout_d_acte0 = %s, mnt_taxe_prime0 = %s , mnt_glob0=%s , total_plus_access=%s , base=%s where id = %s' , (prime_net_total ,prime_net_SIDA,total_prime_net,mnt_accessoires_gest,mnt_accessoires_interme, mnt_accessoires_assureur ,total_accessoires,mnt_comxion_gest,mnt_comxion_courtier,total_commission,taxe_enregistrement,montant_ttc,montant_hc_plus_access,total_prime_net,quittance_id ))



					cr.execute("select distinct college_id from mcisogem_benef where police_id=%s", (data['police_id'],))
					lescolleges = cr.dictfetchall()
					prime_net_total = 0
					prime_net_SIDA_total = 0

					#On parcours les colleges
					for college in lescolleges:

						college_search = self.pool.get('mcisogem.college').search(cr,uid,[('id' , '=' , college['college_id'])])

						college_data = self.pool.get('mcisogem.college').browse(cr,uid,college_search)


						cr.execute("select distinct statut_benef from mcisogem_benef where police_id =%s and college_id=%s", (data['police_id'], college['college_id']))

						lesstatuts = cr.dictfetchall()


						#On parcours les statuts de bénéficiaire
						for statut in lesstatuts:
							prime_statut_assure = 0
							prime_statut_assure_sida = 0
							prime_statut_assure_r = 0
							prime_statut_assure_sida_r = 0

							statut_data = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut['statut_benef'])

							cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id = %s ORDER BY id ASC", (college['college_id'], data['police_id'] , statut['statut_benef']))

							#on parcours toutes les primes qui ont été définies pour le statut en cours
							lesprimes = cr.dictfetchall()

							nbre_benef_incorpo = 0
							nbre_benef_retrait = 0

							for prime in lesprimes:

								dt_fin_prime = datetime.strptime(str(prime['dt_echea_pol']), '%Y-%m-%d')

								dt_effet_prime = datetime.strptime(str(prime['dt_eff_mod_prime']), '%Y-%m-%d')

								# on parcours les bénéficiaires incorporés concernés par la prime en cours

								cr.execute("select  * from mcisogem_benef where statut != 'R' and police_id=%s and statut_benef=%s and college_id=%s and creat_incorpo = %s and dt_effet <= %s and valide_quittance != %s", (data['police_id'], statut['statut_benef'] , college['college_id'], 'I', dt_fin_prime , 2))


								lesbenefs = cr.dictfetchall()

								if len(lesbenefs) > 0:
									nbre_benef_incorpo = len(lesbenefs)

								# on parcours les bénéficiaires retirés concernés par la prime en cours
								cr.execute("select  * from mcisogem_benef where statut = 'R' and police_id=%s and valide_quittance = 0 and statut_benef=%s and college_id=%s", (data['police_id'], statut['statut_benef'] , college['college_id']))

								# cr.execute("select  * from mcisogem_benef where statut = 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s", (data['police_id'], statut['statut_benef'] , college['college_id'], dt_fin_prime))

								lesbenefs_retire = cr.dictfetchall()

								if len(lesbenefs_retire) > 0:
									nbre_benef_retrait = len(lesbenefs_retire)



								prime_assure = 0
								prime_sida = 0

								prime_assure_r = 0
								prime_sida_r = 0

								for benef in lesbenefs:

									dt_effet_benef = datetime.strptime(str(benef['dt_effet']), '%Y-%m-%d')
									dt_fin_exercice = datetime.strptime(str(quittance_data.deb_periode), '%Y-%m-%d')
									dt_deb_exercice = datetime.strptime(str(quittance_data.fin_periode), '%Y-%m-%d')
									nbre_mois = relativedelta(dt_fin_exercice, dt_deb_exercice).months + 1

									nbre_mois_benef = relativedelta(dt_fin_prime, dt_effet_benef).months + 1

									prime_assure += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
									prime_sida += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

									prime_statut_assure += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
									prime_statut_assure_sida += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

									cr.execute("update mcisogem_benef set valide_quittance=%s where id=%s", (2, benef['id']))

								for benef_r in lesbenefs_retire:

									dt_effet_benef = datetime.strptime(str(benef_r['dt_effet']), '%Y-%m-%d')
									dt_retrait_benef = datetime.strptime(str(benef_r['date_exclusion']), '%Y-%m-%d %H:%M:%S')
									dt_fin_exercice = datetime.strptime(str(quittance_data.deb_periode), '%Y-%m-%d')
									dt_deb_exercice = datetime.strptime(str(quittance_data.fin_periode), '%Y-%m-%d')
									nbre_mois = relativedelta(dt_fin_exercice, dt_deb_exercice).months + 1

									nbre_mois_benef = relativedelta(dt_fin_exercice, dt_retrait_benef).months

									prime_assure_r += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
									prime_sida_r += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

									prime_statut_assure_r += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
									prime_statut_assure_sida_r += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)


									cr.execute("update mcisogem_benef set valide_quittance=%s where id=%s", (2, benef_r['id']))

							if nbre_benef_incorpo > 0:

								cr.execute("insert into mcisogem_detail_quittancier (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot ) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
									(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',nbre_benef_incorpo,nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime_statut_assure,prime_statut_assure_sida,prime_statut_assure_sida + prime_statut_assure,prime_statut_assure_sida)
								)

							if nbre_benef_retrait > 0:
								
								cr.execute("insert into mcisogem_detail_quittancier_retrait (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
									(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',nbre_benef_retrait,nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime_statut_assure_r,prime_statut_assure_sida_r,prime_statut_assure_r + prime_statut_assure_sida_r,prime_statut_assure_sida_r)
								)
											
					return quittance_id

		if code_avenant == 'AI':

			data['deb_periode'] = dt_deb_exercice
			data['fin_periode'] = dt_fin_exercice  


			if statut_police !='draft':
				raise osv.except_osv('Attention !', "La police sélectionnée n'est pas active !")


			les_benef_search = self.pool.get('mcisogem.benef').search(cr,uid,[('police_id','=',data['police_id']) , ('statut' , '!=' , 'R')])
			les_benef_police = self.pool.get('mcisogem.benef').browse(cr,uid,les_benef_search)
			total_prime_net = 0
			

			les_valeurs  = self.onchange_police(cr, uid,  0 , data['police_id'] , data['type_avenant_id'])['value']

			total_prime_net = les_valeurs['mnt_quittance_emis']

			
				
			type_prime = self.details_police(cr,uid,data['police_id']).type_prime
			
			nbre_benef = self.pool.get('mcisogem.benef').search_count(cr,uid,[('police_id','=',data['police_id']) , ('statut' , '!=' , 'R')])

			prime_net_total = les_valeurs['prime_tot_sans_sida']
			prime_net_SIDA =  les_valeurs['prime_sida'] 
			prime_net_SIDA_total = les_valeurs['mnt_quittance_emis']



			#Vérifier si une quittance de type AI n'a pas déjà été émise
			if code_avenant_quittance == 0:
				
				quittance_id = super(mcisogem_quittancier, self).create(cr, uid, data, context=context)

				quittance_data = self.browse(cr, uid, quittance_id, context=context)

				#Vérifier si police par statut bénéficiaire
				if type_prime == '1':

						
					#On vérifie le type d'accessoire gestionnaire - Forfait ou pourcentage
					if data['type_mnt_accessoires_gest'] == True:
						mnt_accessoires_gest = round((total_prime_net * data['mnt_accessoires_gest']) / 100)
					else:
						mnt_accessoires_gest = data['mnt_accessoires_gest']	


					# accessoire intermediaire
					if data['type_accessoires_courtier'] == True:
						mnt_accessoires_interme = round((mnt_accessoires_gest * data['mnt_accessoires_courtier']) / 100)
					else:
						mnt_accessoires_interme = data['mnt_accessoires_courtier']



					#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
					if data['type_accessoires_assureur'] == True:
						mnt_accessoires_assureur = round((mnt_accessoires_gest * data['mnt_accessoires_assureur']) / 100)
					else:
						mnt_accessoires_assureur = data['mnt_accessoires_assureur']



					total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur



					#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
					if data['type_mnt_comxion_gest'] == True:
						mnt_comxion_gest = round((total_prime_net * data['mnt_comxion_gest']) / 100)
					else:
						mnt_comxion_gest = data['mnt_comxion_gest']


					#On vérifie le type de commission du courtier - Forfait ou pourcentage
					if data['type_mnt_comxion_courtier'] == True:
						mnt_comxion_courtier = round((total_prime_net * data['mnt_comxion_courtier']) / 100)
					else:
						mnt_comxion_courtier = data['mnt_comxion_courtier']


					

					total_commission = mnt_comxion_courtier + mnt_comxion_gest

					#On vérifie le type de montant taxe - Forfait ou pourcentage
					if data['type_mnt_taxe'] == True:
						taux_taxe = round((total_prime_net * data['mnt_taxe']) / 100)
					else:
						taux_taxe = data['mnt_taxe']

					montant_hc_plus_access = total_prime_net + total_accessoires 

					if data['type_mnt_taxe'] == True:
						taxe_enregistrement = round((montant_hc_plus_access * data['mnt_taxe']) / 100)
					else:
						taxe_enregistrement = data['mnt_taxe']


					montant_ttc = montant_hc_plus_access+ taxe_enregistrement

					cr.execute('update mcisogem_quittancier set prime_tot_sans_sida=%s, prime_sida=%s , mnt_quittance_emis = %s , taxe_acc_nostro = %s , taxe_acc_courtier = %s , taxe_acc_assureur =%s ,cout_d_acte1=%s , cout_d_acte=%s , cout_d_acte_courtier = %s , cout_d_acte0 = %s, mnt_taxe_prime0 = %s , mnt_glob0=%s , total_plus_access=%s , base=%s where id = %s' , (prime_net_total ,prime_net_SIDA,total_prime_net,mnt_accessoires_gest,mnt_accessoires_interme, mnt_accessoires_assureur ,total_accessoires,mnt_comxion_gest,mnt_comxion_courtier,total_commission,taxe_enregistrement,montant_ttc,montant_hc_plus_access,total_prime_net,quittance_id ))
					
				
					cr.execute("select distinct college_id from mcisogem_benef where statut != %s and valide_quittance = %s and police_id=%s", ('R', 0 , data['police_id'],))
					lescolleges = cr.dictfetchall()     
					prime_net_total = 0   
					prime_net_SIDA_total = 0                         

					#On parcours les colleges
					for college in lescolleges:

						college_data = self.pool.get('mcisogem.college').browse(cr,uid,college['college_id'])

						cr.execute("select distinct statut_benef from mcisogem_benef where statut != %s and valide_quittance = %s and police_id =%s and college_id=%s", ('R', 0 , data['police_id'], college['college_id']))
						lesstatuts = cr.dictfetchall()


						#On parcours les statuts de bénéficiaire
						for statut in lesstatuts:

							statut_data = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut['statut_benef'])

							# nbre de beneficiaire incorporés
							nbre_benef_incorpo = self.pool.get('mcisogem.benef').search_count(cr,uid,[('statut_benef' , '=' , statut['statut_benef']) , ('statut' , '!=' , 'R') , ('college_id' , '=' ,college['college_id'] ) , ('police_id' , '=' ,data['police_id'] )])


							cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id = %s ORDER BY id ASC", (college['college_id'], data['police_id'] , statut['statut_benef']))

							#on parcours toutes les primes qui ont été définies pour le statut en cours
							lesprimes = cr.dictfetchall()
							lesbenefs = None
							for prime in lesprimes:

								dt_fin_prime = datetime.strptime(str(prime['dt_echea_pol']), '%Y-%m-%d')

								dt_effet_prime = datetime.strptime(str(prime['dt_eff_mod_prime']), '%Y-%m-%d')

								# on parcours les bénéficiaires incorporés concernés par la prime en cours

								cr.execute("select  * from mcisogem_benef where statut !=%s and valide_quittance = %s and police_id = %s and college_id=%s and creat_incorpo = %s and statut_benef=%s and dt_effet < %s", ('R', 0 , data['police_id'],college['college_id'], 'C',statut_data.id , dt_fin_prime))

								lesbenefs = cr.dictfetchall()


								# on parcours les bénéficiaires incorporés concernés par la prime en cours

								cr.execute("select  * from mcisogem_benef where statut !=%s and valide_quittance > %s and police_id = %s and college_id=%s and creat_incorpo = %s and statut_benef=%s and dt_effet < %s", ('R', 0 , data['police_id'],college['college_id'], 'C',statut_data.id , dt_fin_prime))

								lesbenefs_retire = cr.dictfetchall()

								prime_A = 0
								prime_A_SIDA = 0

								for benef in lesbenefs:
									prime_A += prime['prim_assure']
									prime_A_SIDA += prime['prime_sida']

									dt_effet_benef = datetime.strptime(str(benef['dt_effet']), '%Y-%m-%d')
									dt_fin_exercice = datetime.strptime(str(quittance_data.deb_periode), '%Y-%m-%d')
									dt_deb_exercice = datetime.strptime(str(quittance_data.fin_periode), '%Y-%m-%d')
									nbre_mois = relativedelta(dt_fin_exercice, dt_deb_exercice).months + 1

							if nbre_benef_incorpo > 0 and lesbenefs:

								cr.execute("insert into mcisogem_detail_quittancier (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot ) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
									(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',nbre_benef_incorpo,nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime_A,prime['prime_sida'],prime_A + prime_A_SIDA,prime_A_SIDA)
								)


					return quittance_id

				


			else:
				raise osv.except_osv('Attention !', "Une quittance a déjà été calculée avec le type d'avemant AI pour cette police!")
				return False

		if code_avenant =='AA': 

			if statut_police !='draft':
				raise osv.except_osv('Attention !', "La police sélectionnée n'est pas active !")


			les_benef_search = self.pool.get('mcisogem.benef').search(cr,uid,[('police_id','=',data['police_id'])])
			les_benef_police = self.pool.get('mcisogem.benef').browse(cr,uid,les_benef_search)
			total_prime_net = 0
				
			les_valeurs  = self.onchange_police(cr, uid,  0 , data['police_id'] , data['type_avenant_id'])['value']

			total_prime_net = les_valeurs['mnt_quittance_emis']
				
			type_prime = self.details_police(cr,uid,data['police_id']).type_prime
			
			nbre_benef = self.pool.get('mcisogem.benef').search_count(cr,uid,[('police_id','=',data['police_id'])])

			prime_net_total = les_valeurs['prime_tot_sans_sida']
			prime_net_SIDA =  les_valeurs['prime_sida'] 
			prime_net_SIDA_total = les_valeurs['mnt_quittance_emis']


			#Vérifier si une quittance de type AI a déjà été émise
			if code_avenant_quittance > 0:

				quittance_id = super(mcisogem_quittancier, self).create(cr, uid, data, context=context)

				quittance_data = self.browse(cr, uid, quittance_id, context=context)
			

				#Vérifier si police par statut bénéficiaire
				if type_prime == '1':

						
					#On vérifie le type d'accessoire gestionnaire - Forfait ou pourcentage
					if data['type_mnt_accessoires_gest'] == True:
						mnt_accessoires_gest = round((total_prime_net * data['mnt_accessoires_gest']) / 100)
					else:
						mnt_accessoires_gest = data['mnt_accessoires_gest']	


					# accessoire intermediaire
					if data['type_accessoires_courtier'] == True:
						mnt_accessoires_interme = round((mnt_accessoires_gest * data['mnt_accessoires_courtier']) / 100)
					else:
						mnt_accessoires_interme = data['mnt_accessoires_courtier']



					#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
					if data['type_accessoires_assureur'] == True:
						mnt_accessoires_assureur = round((mnt_accessoires_gest * data['mnt_accessoires_assureur']) / 100)
					else:
						mnt_accessoires_assureur = data['mnt_accessoires_assureur']



					total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur



					#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
					if data['type_mnt_comxion_gest'] == True:
						mnt_comxion_gest = round((total_prime_net * data['mnt_comxion_gest']) / 100)
					else:
						mnt_comxion_gest = data['mnt_comxion_gest']


					#On vérifie le type de commission du courtier - Forfait ou pourcentage
					if data['type_mnt_comxion_courtier'] == True:
						mnt_comxion_courtier = round((total_prime_net * data['mnt_comxion_courtier']) / 100)
					else:
						mnt_comxion_courtier = data['mnt_comxion_courtier']


					total_commission = mnt_comxion_courtier + mnt_comxion_gest

					#On vérifie le type de montant taxe - Forfait ou pourcentage
					if data['type_mnt_taxe'] == True:
						taux_taxe = round((total_prime_net * data['mnt_taxe']) / 100)
					else:
						taux_taxe = data['mnt_taxe']

					montant_hc_plus_access = total_prime_net + total_accessoires 

					if data['type_mnt_taxe'] == True:
						taxe_enregistrement = round((montant_hc_plus_access * data['mnt_taxe']) / 100)
					else:
						taxe_enregistrement = data['mnt_taxe']


					montant_ttc = montant_hc_plus_access+ taxe_enregistrement

					cr.execute('update mcisogem_quittancier set prime_tot_sans_sida=%s, prime_sida=%s , mnt_quittance_emis = %s , taxe_acc_nostro = %s , taxe_acc_courtier = %s , taxe_acc_assureur =%s ,cout_d_acte1=%s , cout_d_acte=%s , cout_d_acte_courtier = %s , cout_d_acte0 = %s, mnt_taxe_prime0 = %s , mnt_glob0=%s , total_plus_access=%s , base=%s where id = %s' , (prime_net_total ,prime_net_SIDA,total_prime_net,mnt_accessoires_gest,mnt_accessoires_interme, mnt_accessoires_assureur ,total_accessoires,mnt_comxion_gest,mnt_comxion_courtier,total_commission,taxe_enregistrement,montant_ttc,montant_hc_plus_access,total_prime_net,quittance_id ))
									

					cr.execute("select distinct college_id from mcisogem_benef where valide_quittance > %s and police_id=%s", (0 , data['police_id'],))
					lescolleges = cr.dictfetchall()     
					prime_net_total = 0   
					prime_net_SIDA_total = 0                         


					#On parcours les colleges
					for college in lescolleges:

						
						
						college_search = self.pool.get('mcisogem.college').search(cr,uid,[('id' , '=' , college['college_id'] )])
						college_data = self.pool.get('mcisogem.college').browse(cr,uid,college_search)

						cr.execute("select distinct statut_benef from mcisogem_benef where valide_quittance > %s and police_id =%s and college_id=%s", (0 , data['police_id'], college['college_id']))
						lesstatuts = cr.dictfetchall()


						#On parcours les statut de bénéficiaire
						for statut in lesstatuts:
							cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id=%s ORDER BY dt_eff_mod_prime DESC limit 1", (college['college_id'], data['police_id'], statut['statut_benef'],))
							lesprimes = cr.dictfetchall()[0]


							statut_search = self.pool.get('mcisogem.stat.benef').search(cr,uid,[('id' , '=' , statut['statut_benef'] )])
							statut_data = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut_search)
							

							if statut['statut_benef'] == 1: 
								cr.execute("select  * from mcisogem_benef where valide_quittance > %s and police_id=%s and statut_benef=%s and college_id=%s and creat_incorpo = %s", (0 , data['police_id'], 1 , college['college_id'], 'C',))
								lesbenefs = cr.dictfetchall()



								prime_A = lesprimes['prim_assure'] * len(lesbenefs)
								prime_A_SIDA = lesprimes['prime_sida'] * len(lesbenefs)

								les_donnees = {}

								cr.execute("insert into mcisogem_detail_quittancier (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot ) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
										(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',len(lesbenefs),nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime['prim_assure'],prime['prime_sida'],prime_A + prime_A_SIDA,prime_A_SIDA)
									)


							else:
								if statut['statut_benef'] == 3:
									cr.execute("select distinct * from mcisogem_benef where valide_quittance > %s and police_id=%s and statut_benef=%s and college_id=%s and creat_incorpo = %s", (0 , data['police_id'], 3 , college['college_id'], 'C',))
									lesbenefs = cr.dictfetchall()                                              
									prime_C = lesprimes['prim_assure'] * len(lesbenefs)
									prime_C_SIDA = lesprimes['prime_sida'] * len(lesbenefs)

									cr.execute("insert into mcisogem_detail_quittancier (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot ) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
										(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',len(lesbenefs),nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime['prim_assure'],prime['prime_sida'],prime_C + prime_C_SIDA,prime_C_SIDA)
									)

								else:
									cr.execute("select * from mcisogem_benef where valide_quittance > %s and police_id=%s and statut_benef=%s and college_id=%s and creat_incorpo = %s", (0 , data['police_id'], 2 , college['college_id'], 'C',))
									lesbenefs = cr.dictfetchall()                                              
									prime_E = lesprimes['prim_assure'] * len(lesbenefs)
									prime_E_SIDA = lesprimes['prime_sida'] * len(lesbenefs)

									cr.execute("insert into mcisogem_detail_quittancier (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot ) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
										(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',len(lesbenefs),nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime['prim_assure'],prime['prime_sida'],prime_E + prime_E_SIDA,prime_E_SIDA)
									)



						les_benef_search = self.pool.get('mcisogem.benef').search(cr,uid,[('police_id','=',data['police_id'])])
						les_benef_police = self.pool.get('mcisogem.benef').browse(cr,uid,les_benef_search)

						for benef in lesbenefs:
								cr.execute("update mcisogem_histo_benef set valide_quittance=%s where id=%s", (2, benef['id']))


					
					for benef in les_benef_police:
						cr.execute("update mcisogem_benef set valide_quittance=%s where id=%s", (2, benef.id))		

							
					return quittance_id

				#Si police par tranche d'age
				else:
					cr.execute("select distinct college_id from mcisogem_histo_benef where st_retr_excl!=%s and police_id=%s", ('R', data['police_id'],))
					lescolleges = cr.dictfetchall()      
					prime_net_total = 0    
					prime_net_SIDA_total = 0                         

					#On parcours les colleges
					for college in lescolleges:
						cr.execute("select distinct code_tranche_age from mcisogem_histo_prime where college_id=%s and police_id=%s", (college['college_id'], data['police_id'],))
						lesstrancheage = cr.dictfetchall()
						prime_net_total_temp = 0
						prime_net_SIDA_total_temp = 0 
								
						#On parcours les tranches d'age de bénéficiaire
						for trancheage in lesstrancheage:
							obj_tranche_age_data = self.pool.get('mcisogem.tranche.age').browse(cr, uid, trancheage, context=context)
							cr.execute("select distinct * from mcisogem_histo_prime where  police_id=%s and college_id=%s code_tranche_age=%s", ( data['police_id'], college, trancheage,))
							lesprimes = cr.dictfetchall()
							cr.execute("select distinct * from mcisogem_histo_benef where st_retr_excl!=%s and valide_quittance in %s and police_id=%s and cod_statut_benef=%s and college_id=%s st_creat_incorpo in %s id_tran_age=%s", ('R', (1,2), data['police_id'], 'E', college, ('C'), trancheage,))
							lesbenefs = cr.dictfetchall()

							prime_tranche = lesprimes['prim_assure'] * len(lesbenefs)
							prime_tranche_SIDA = lesprimes['Prime_sida'] * len(lesbenefs)

							#On additionne les primes par tranche d'age
							prime_net_total_temp += prime_tranche
							prime_net_SIDA_total_temp += prime_tranche_SIDA

							cr.execute("""INSERT INTO mcisogem_detail_quittancier (mcisogem_quittancier_id, college, date_effet_police,
							effectif_det, nbre_jour_mois_det, nbre_jour_mois_exercice, type_jour_mois_det, prime_indivuel, prime_indivuel_sida, prime_indivuel_tot, 
							prime_indivuel_sida_tot, st_creat_incorpo, deb_tran_age, fin_tran_age)
							VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
							, (quittance_id, college, quittance_data.date_effet_police, len(lesbenefs), mois_a_acourir, nbre_mois_exercice, 
							quittance_data.repartition_prime, lesprimes['prim_assure'], lesprimes['Prime_sida'], prime_tranche, prime_tranche_SIDA, obj_tranche_age_data.debut_tranche, obj_tranche_age_data.fin_tranche))

							

						#On additionne les primes par collège
						prime_net_total += prime_net_total_temp
						prime_net_SIDA_total += prime_net_SIDA_total_temp

				#Vérifier si mode de répartition de prime au mois          
				if mode_repar_prime == 1:
					mois_a_acourir = datetime.strptime(obj_pol_data.dt_fin_exercice , '%Y-%m-%d').month - datetime.strptime(obj_pol_data.dt_effet , '%Y-%m-%d').month

					prime_net_total = (prime_net_total * mois_a_acourir) / 12.0
					prime_net_SIDA = (prime_net_SIDA * mois_a_acourir) / 12.0
					total_prime_net = prime_net_total + prime_net_SIDA

				else:

					print(datetime.strptime(obj_pol_data.dt_fin_exercice , '%Y-%m-%d').day)

					jours_a_acourir = datetime.strptime(obj_pol_data.dt_fin_exercice , '%Y-%m-%d').day - datetime.strptime(obj_pol_data.dt_effet , '%Y-%m-%d').day
					prime_net_total = (prime_net_total * jours_a_acourir) / 365
					prime_net_SIDA = (prime_net_SIDA * jours_a_acourir) / 365
					total_prime_net = prime_net_total + prime_net_SIDA
				
					
				#On vérifie le type d'accessoire gestionnaire - Forfait ou pourcentage
				if data['type_mnt_accessoires_gest'] == True:
					mnt_accessoires_gest = (total_prime_net * data['mnt_accessoires_gest']) / 100
				else:
					mnt_accessoires_gest = data['mnt_accessoires_gest']

				#On vérifie type d'accessoire courtier - Forfait ou pourcentage
				if data['type_mnt_comxion_courtier'] == True:
					mnt_accessoires_courtier = (mnt_accessoires_gest * data['mnt_accessoires_courtier']) / 100
				else:
					mnt_accessoires_courtier = data['mnt_accessoires_courtier']

				#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
				if data['type_accessoires_assureur'] == True:
					mnt_accessoires_assureur = (mnt_accessoires_gest * data['mnt_accessoires_assureur']) / 100
				else:
					mnt_accessoires_assureur = data['mnt_accessoires_assureur']

				total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur

				#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
				if data['type_mnt_comxion_gest'] == True:
					mnt_comxion_gest = round((total_prime_net * data['mnt_comxion_gest']) / 100)
				else:
					mnt_comxion_gest = data['mnt_comxion_gest']

				#On vérifie le type de commission du courtier - Forfait ou pourcentage
				if data['type_mnt_comxion_courtier'] == True:
					mnt_comxion_courtier = (total_prime_net * data['type_mnt_comxion_courtier']) / 100
				else:
					mnt_comxion_courtier = data['type_mnt_comxion_courtier']

				total_commission = mnt_accessoires_gest + mnt_accessoires_interme

				#On vérifie le type de montant taxe - Forfait ou pourcentage
				if data['type_mnt_taxe'] == True:
					taux_taxe = round((total_prime_net * data['mnt_taxe']) / 100)
				else:
					taux_taxe = data['mnt_taxe']

				taxe_enregistrement = (total_prime_net + total_accessoires) * taux_taxe

				montant_ttc = total_prime_net + total_accessoires + taxe_enregistrement

				montant_hc_plus_access = total_prime_net + total_accessoires 

				cr.execute('update mcisogem_quittancier set prime_tot_sans_sida=%s, prime_sida=%s , mnt_quittance_emis = %s , mnt_accessoires_gest = %s , mnt_accessoires_courtier = %s , mnt_accessoires_assureur =%s ,cout_d_acte1=%s , cout_d_acte=%s , cout_d_acte_courtier=%s , cout_d_acte0 = %s, mnt_taxe_prime0 = %s , mnt_glob0=%s , total_plus_access=%s , base=%s where id = %s' , (prime_net_total ,prime_net_SIDA,total_prime_net,mnt_accessoires_gest,mnt_accessoires_interme, mnt_accessoires_assureur ,total_accessoires,mnt_comxion_gest,mnt_comxion_courtier,total_commission,taxe_enregistrement,montant_ttc,montant_hc_plus_access,mnt_accessoires_gest,quittance_id ))


				return quittance_id

			else:
				raise osv.except_osv('Attention !', "Une quittance avec le type d'avemant AI doit être émise pour cette police!")
				return False

		if code_avenant == 'AR':

			if statut_police !='draft':
				raise osv.except_osv('Attention !', "La police sélectionnée n'est pas active !")


			avenant_search = self.pool.get('mcisogem.type.avenant').search(cr,uid,[('code_type_avenant' , '=' , 'AS')])
			avenant_fact = self.pool.get('mcisogem.type.avenant').browse(cr,uid,avenant_search).id
			nbre_avenant_fact = self.pool.get('mcisogem.quittancier').search_count(cr,uid,[('police_id' , '=' , data['police_id']) , ('type_avenant_id' , '=' , avenant_fact)])


			if nbre_avenant_fact == 0:
				raise osv.except_osv('Attention' , 'Aucun Avenant de facturation n\'a été émis pour cette police')

			les_valeurs  = self.onchange_police(cr, uid,  0 , data['police_id'] , data['type_avenant_id'])['value']

			total_prime_net = les_valeurs['mnt_quittance_emis']	
			type_prime = self.details_police(cr,uid,data['police_id']).type_prime
			prime_net_total = les_valeurs['prime_tot_sans_sida']
			prime_net_SIDA =  les_valeurs['prime_sida'] 
			prime_net_SIDA_total = les_valeurs['mnt_quittance_emis']

			if code_avenant_quittance > 0:

				quittance_id = super(mcisogem_quittancier, self).create(cr, uid, data, context=context)

				quittance_data = self.browse(cr, uid, quittance_id, context=context)
			

				#Vérifier si police par statut bénéficiaire
				if type_prime == '1':

						
					#On vérifie le type d'accessoire gestionnaire - Forfait ou pourcentage
					if data['type_mnt_accessoires_gest'] == True:
						mnt_accessoires_gest = round((total_prime_net * data['mnt_accessoires_gest']) / 100)
					else:
						mnt_accessoires_gest = data['mnt_accessoires_gest']	


					# accessoire intermediaire
					if data['type_accessoires_courtier'] == True:
						mnt_accessoires_interme = round((mnt_accessoires_gest * data['mnt_accessoires_courtier']) / 100)
					else:
						mnt_accessoires_interme = data['mnt_accessoires_courtier']



					#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
					if data['type_accessoires_assureur'] == True:
						mnt_accessoires_assureur = round((mnt_accessoires_gest * data['mnt_accessoires_assureur']) / 100)
					else:
						mnt_accessoires_assureur = data['mnt_accessoires_assureur']



					total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur



					#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
					if data['type_mnt_comxion_gest'] == True:
						mnt_comxion_gest = round((total_prime_net * data['mnt_comxion_gest']) / 100)
					else:
						mnt_comxion_gest = data['mnt_comxion_gest']


					#On vérifie le type de commission du courtier - Forfait ou pourcentage
					if data['type_mnt_comxion_courtier'] == True:
						mnt_comxion_courtier = round((total_prime_net * data['mnt_comxion_courtier']) / 100)
					else:
						mnt_comxion_courtier = data['mnt_comxion_courtier']


					total_commission = mnt_comxion_courtier + mnt_comxion_gest

					#On vérifie le type de montant taxe - Forfait ou pourcentage
					if data['type_mnt_taxe'] == True:
						taux_taxe = round((total_prime_net * data['mnt_taxe']) / 100)
					else:
						taux_taxe = data['mnt_taxe']

					montant_hc_plus_access = total_prime_net + total_accessoires 

					if data['type_mnt_taxe'] == True:
						taxe_enregistrement = round((montant_hc_plus_access * data['mnt_taxe']) / 100)
					else:
						taxe_enregistrement = data['mnt_taxe']


					montant_ttc = montant_hc_plus_access+ taxe_enregistrement

					
					cr.execute('update mcisogem_quittancier set prime_tot_sans_sida=%s, prime_sida=%s , mnt_quittance_emis = %s , taxe_acc_nostro = %s , taxe_acc_courtier = %s , taxe_acc_assureur =%s ,cout_d_acte1=%s , cout_d_acte=%s , cout_d_acte_courtier = %s , cout_d_acte0 = %s, mnt_taxe_prime0 = %s , mnt_glob0=%s , total_plus_access=%s , base=%s where id = %s' , (prime_net_total ,prime_net_SIDA,total_prime_net,mnt_accessoires_gest,mnt_accessoires_interme, mnt_accessoires_assureur ,total_accessoires,mnt_comxion_gest,mnt_comxion_courtier,total_commission,taxe_enregistrement,montant_ttc,montant_hc_plus_access,total_prime_net,quittance_id ))


					cr.execute("select distinct college_id from mcisogem_benef where police_id=%s", (data['police_id'],))
					lescolleges = cr.dictfetchall()     
					prime_net_total = 0   
					prime_net_SIDA_total = 0                         

					#On parcours les colleges
					for college in lescolleges:

						college_data = self.pool.get('mcisogem.college').browse(cr,uid,college['college_id'])

						cr.execute("select distinct statut_benef from mcisogem_benef where police_id =%s and college_id=%s", (data['police_id'], college['college_id']))
						lesstatuts = cr.dictfetchall()


						#On parcours les statuts de bénéficiaire
						for statut in lesstatuts:

							prime_statut_assure = 0
							prime_statut_assure_sida = 0
							prime_statut_assure_r = 0
							prime_statut_assure_sida_r = 0

							statut_data = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut['statut_benef'])

							cr.execute("select  * from mcisogem_histo_prime where college_id=%s and police_id=%s and statut_benef_id = %s ORDER BY id DESC LIMIT 1", (college['college_id'], data['police_id'] , statut['statut_benef']))

							#on parcours toutes les primes qui ont été définies pour le statut en cours
							lesprimes = cr.dictfetchall()

							prime = lesprimes[0]

							dt_fin_prime = datetime.strptime(str(prime['dt_echea_pol']), '%Y-%m-%d')

							dt_effet_prime = datetime.strptime(str(prime['dt_eff_mod_prime']), '%Y-%m-%d')

							# on parcours les bénéficiaires incorporés concernés par la prime en cours

							cr.execute("select  * from mcisogem_benef where statut != 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s", (data['police_id'], statut['statut_benef'] , college['college_id'], dt_fin_prime))


							lesbenefs = cr.dictfetchall()
							nbre_benef_incorpo = len(lesbenefs)

							# on parcours les bénéficiaires incorporés concernés par la prime en cours

							cr.execute("select  * from mcisogem_benef where statut = 'R' and police_id=%s and statut_benef=%s and college_id=%s and dt_effet <= %s", (data['police_id'], statut['statut_benef'] , college['college_id'], dt_fin_prime))

							lesbenefs_retire = cr.dictfetchall()
							nbre_benef_retrait = len(lesbenefs_retire)


							prime_assure = 0
							prime_sida = 0

							prime_assure_r = 0
							prime_sida_r = 0

							for benef in lesbenefs:

								dt_effet_benef = datetime.strptime(str(benef['dt_effet']), '%Y-%m-%d')
								dt_fin_exercice = datetime.strptime(str(quittance_data.deb_periode), '%Y-%m-%d')
								dt_deb_exercice = datetime.strptime(str(quittance_data.fin_periode), '%Y-%m-%d')
								nbre_mois = relativedelta(dt_fin_exercice, dt_deb_exercice).months + 1

								nbre_mois_benef = relativedelta(dt_fin_prime, dt_effet_benef).months + 1

								prime_assure += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
								prime_sida += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

								prime_statut_assure += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
								prime_statut_assure_sida += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

							for benef_r in lesbenefs_retire:

								dt_effet_benef = datetime.strptime(str(benef_r['dt_effet']), '%Y-%m-%d')
								dt_retrait_benef = datetime.strptime(str(benef_r['date_exclusion']), '%Y-%m-%d %H:%M:%S')
								dt_fin_exercice = datetime.strptime(str(quittance_data.deb_periode), '%Y-%m-%d')
								dt_deb_exercice = datetime.strptime(str(quittance_data.fin_periode), '%Y-%m-%d')
								nbre_mois = relativedelta(dt_fin_exercice, dt_deb_exercice).months + 1

								nbre_mois_benef = relativedelta(dt_fin_exercice, dt_retrait_benef).months

								prime_assure_r += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
								prime_sida_r += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

								prime_statut_assure_r += round((prime['prim_assure'] * nbre_mois_benef ) / 12.0)
								prime_statut_assure_sida_r += round((prime['prime_sida'] * nbre_mois_benef ) / 12.0)

							if nbre_benef_incorpo > 0:

								cr.execute("insert into mcisogem_detail_quittancier (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot ) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
									(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',nbre_benef_incorpo,nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime_statut_assure,prime_statut_assure_sida,prime_statut_assure_sida + prime_statut_assure,prime_statut_assure_sida)
								)

							if nbre_benef_retrait > 0:

								cr.execute("insert into mcisogem_detail_quittancier_retrait (mcisogem_quittancier_id ,college,code_statut_benef,st_creat_incorpo,effectif_det,nbre_jour_mois_det,nbre_jour_mois_exercice,type_jour_mois_det,prime_indivuel,prime_indivuel_sida,prime_indivuel_tot,prime_indivuel_sida_tot) values(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)", 
									(quittance_id,college_data.code_college,statut_data.lbc_fam_statut,'C',nbre_benef_retrait,nbre_mois,nbre_mois,quittance_data.repartition_prime[0],prime_statut_assure_r,prime_statut_assure_sida_r,prime_statut_assure_r + prime_statut_assure_sida_r,prime_statut_assure_sida_r)
								)





					return quittance_id



	def button_to_valider(self, cr, uid, ids, context=None):
		return super(mcisogem_quittancier, self).write(cr, uid, ids, {'state':'done'}, context=context) 

	def button_to_cancel(self, cr, uid, ids, context=None):
		return super(mcisogem_quittancier, self).write(cr, uid, ids, {'state':'sent'}, context=context) 
		return True 


	def write(self, cr, uid, ids, data , context=None):

		if type(ids)== 'int':
			# c'est la creation qui continue
			return super(mcisogem_quittancier, self).write(cr, uid, ids, data, context=context)
		else:


			vals = {}
			old_datas = self.browse(cr,uid,ids)
			vals['type_mnt_accessoires_gest'] = old_datas.type_mnt_accessoires_gest
			vals['type_accessoires_courtier'] = old_datas.type_accessoires_courtier
			vals['type_accessoires_assureur'] = old_datas.type_accessoires_assureur
			vals['type_mnt_comxion_gest'] = old_datas.type_mnt_comxion_gest
			vals['type_mnt_comxion_courtier'] = old_datas.type_mnt_comxion_courtier
			vals['type_mnt_taxe'] = old_datas.type_mnt_taxe

			vals['mnt_accessoires_gest'] = old_datas.mnt_accessoires_gest
			vals['mnt_accessoires_courtier'] = old_datas.mnt_accessoires_courtier
			vals['mnt_accessoires_assureur'] = old_datas.mnt_accessoires_assureur
			vals['mnt_comxion_gest'] = old_datas.mnt_comxion_gest
			vals['mnt_comxion_courtier'] = old_datas.mnt_comxion_courtier
			
			vals['mnt_taxe'] = old_datas.mnt_taxe
			vals['mnt_glob0'] = old_datas.mnt_glob0
			vals['mnt_quittance_emis'] = old_datas.mnt_quittance_emis

			
			total_prime_net = old_datas.mnt_quittance_emis

			if 'type_mnt_accessoires_gest' in data:
				vals['type_mnt_accessoires_gest'] = data['type_mnt_accessoires_gest']

			if 'type_accessoires_courtier' in data:
				vals['type_accessoires_courtier'] = data['type_accessoires_courtier']

			if 'type_accessoires_assureur' in data:
				vals['type_accessoires_assureur'] = data['type_accessoires_assureur']

			if 'type_mnt_comxion_gest' in data:
				vals['type_mnt_comxion_gest'] = data['type_mnt_comxion_gest']

			if 'type_mnt_comxion_courtier' in data:
				vals['type_mnt_comxion_courtier'] = data['type_mnt_comxion_courtier']

			if 'type_mnt_taxe' in data:
				vals['type_mnt_taxe'] = data['type_mnt_taxe']


			if 'mnt_accessoires_gest' in data:
				vals['mnt_accessoires_gest'] = data['mnt_accessoires_gest']

			if 'mnt_accessoires_courtier' in data:
				vals['mnt_accessoires_courtier'] = data['mnt_accessoires_courtier']

			if 'mnt_accessoires_assureur' in data:
				vals['mnt_accessoires_assureur'] = data['mnt_accessoires_assureur']

			if 'mnt_comxion_courtier' in data:
				vals['mnt_comxion_courtier'] = data['mnt_comxion_courtier']

			if 'mnt_comxion_gest' in data:
				vals['mnt_comxion_gest'] = data['mnt_comxion_gest']

			if 'mnt_comxion_gest' in data:
				vals['mnt_comxion_gest'] = data['mnt_comxion_gest']

			if 'mnt_taxe' in data:
				vals['mnt_taxe'] = data['mnt_taxe']


			if vals['type_mnt_accessoires_gest'] == True:
				mnt_accessoires_gest = round((total_prime_net * vals['mnt_accessoires_gest']) / 100)
			else:
				mnt_accessoires_gest = vals['mnt_accessoires_gest']

			# accessoire intermediaire
			if vals['type_accessoires_courtier'] == True:
				mnt_accessoires_interme = round((mnt_accessoires_gest * vals['mnt_accessoires_courtier']) / 100)
			else:
				mnt_accessoires_interme = vals['mnt_accessoires_courtier']



			if 'deb_periode' in data:
				vals['deb_periode'] = data['deb_periode']

			if 'fin_periode' in data:
				vals['fin_periode'] = data['fin_periode']

				
			#On vérifie le type d'accessoire compagnie - Forfait ou pourcentage
			if vals['type_accessoires_assureur']== True:
				mnt_accessoires_assureur = round((mnt_accessoires_gest * vals['mnt_accessoires_assureur']) / 100)
			else:
				mnt_accessoires_assureur = vals['mnt_accessoires_assureur']


			total_accessoires = mnt_accessoires_gest + mnt_accessoires_interme + mnt_accessoires_assureur

			#On vérifie le type de commission du gestionnaire - Forfait ou pourcentage
			if vals['type_mnt_comxion_gest'] == True:
				mnt_comxion_gest = round((total_prime_net * vals['mnt_comxion_gest']) / 100)
			else:
				mnt_comxion_gest = vals['mnt_comxion_gest']


			#On vérifie le type de commission du courtier - Forfait ou pourcentage
			if vals['type_mnt_comxion_courtier'] == True:
				mnt_comxion_courtier = round((total_prime_net * vals['mnt_comxion_courtier']) / 100)
			else:
				mnt_comxion_courtier = vals['mnt_comxion_courtier']


			total_commission = mnt_comxion_courtier + mnt_comxion_gest


			#On vérifie le type de montant taxe - Forfait ou pourcentage
			if vals['type_mnt_taxe'] == True:
				taux_taxe = round((total_prime_net * vals['mnt_taxe']) / 100)
			else:
				taux_taxe = vals['mnt_taxe']

			montant_hc_plus_access = total_prime_net + total_accessoires

			if vals['type_mnt_taxe'] == True:
				taxe_enregistrement = round((montant_hc_plus_access * vals['mnt_taxe']) / 100)
			else:
				taxe_enregistrement = vals['mnt_taxe']

			montant_ttc = montant_hc_plus_access+ taxe_enregistrement

			# vals['dt_emi_quittance'] = time.strftime("%Y-%m-%d", time.localtime())

			if 'dt_emi_quittance' in data:

				vals['dt_emi_quittance'] = data['dt_emi_quittance']


			if 'nature_risque_id' in data:

				vals['nature_risque_id'] = data['nature_risque_id']


			vals['taxe_acc_nostro'] = mnt_accessoires_gest
			vals['taxe_acc_assureur'] = mnt_accessoires_assureur
			vals['taxe_acc_courtier'] = mnt_accessoires_interme
			vals['cout_d_acte'] = mnt_comxion_gest
			vals['cout_d_acte_courtier'] = mnt_comxion_courtier
			vals['cout_d_acte0'] = total_commission
			vals['cout_d_acte1'] = total_accessoires
			vals['total_plus_access'] = montant_hc_plus_access
			vals['mnt_taxe_prime0'] = taxe_enregistrement
			vals['mnt_glob0'] = montant_ttc

			return super(mcisogem_quittancier, self).write(cr, uid, ids, vals, context=context)

		



#----------------------------------------------------------
# Détail quittancier
#----------------------------------------------------------

class mcisogem_detail_quittancier(osv.osv):
	"""Table pour le détail du quittancier"""
	_name = "mcisogem.detail.quittancier"    
	_description = "Gestion du quittancier"

	def _get_cod_gest(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		return gest_obj.code_centre
	
	
	def _get_cod_lang(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		return gest_obj.langue_id.name
	
	def _get_cod_gest_id(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))        
		cod_gest_id = cr.fetchone()[0]
		return cod_gest_id
	

	_columns = {   
		'mcisogem_quittancier_id': fields.many2one('mcisogem.quittancier',"Quittancier"),
		'college': fields.char('College'),
		'code_statut_benef': fields.char('Statut'),
		'date_effet_police': fields.date('Date effet de l’exercice'),
		'effectif_det': fields.float('Effectif', digits=(18, 0)),  
		'nbre_jour_mois_det': fields.float('Jour/Mois', digits=(18, 0)),  
		'nbre_jour_mois_exercice': fields.float('Nombre Jour/Mois', digits=(18, 0)),  
		'type_jour_mois_det': fields.float('Type', digits=(1, 0)),  
		'prime_indivuel': fields.float('Prime', digits=(18, 0)),
		'prime_indivuel_sida': fields.float('Prime SIDA', digits=(18, 0)),

		'prime_indivuel_tot': fields.float('Total Prime', digits=(18, 2)),
		'prime_indivuel_sida_tot': fields.float('Total Prime sida', digits=(18, 2)),

		'st_creat_incorpo': fields.char('Création/Incorporation'),

		'dt_sortie_benef': fields.date('Date de sortie de la police'),

		'deb_tran_age': fields.integer('Début tranche d\'âge'),  
		'fin_tran_age': fields.integer('Fin tranche d\'âge'), 

		'ident_centre': fields.many2one('mcisogem.centre.gestion', "Centre de gestion"),
		'code_gest': fields.char('libelle_gest', size=10),
		'code_langue': fields.char('code_langue', size=10),
	}
	
	_defaults = {         
		'code_gest': _get_cod_gest,
		'ident_centre': _get_cod_gest_id,
		'code_langue': _get_cod_lang,
	}

	_order = 'code_statut_benef ASC'


class mcisogem_detail_quittancier_retrait(osv.osv):
	"""Table pour le détail du quittancier des retraits"""
	_name = "mcisogem.detail.quittancier.retrait"    
	_description = "Gestion du quittancier"

	def _get_cod_gest(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		return gest_obj.code_centre
	
	
	def _get_cod_lang(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		return gest_obj.langue_id.name
	
	def _get_cod_gest_id(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))        
		cod_gest_id = cr.fetchone()[0]
		return cod_gest_id
	

	_columns = {   
		'mcisogem_quittancier_id': fields.many2one('mcisogem.quittancier',"Quittancier"),
		'college': fields.char('College'),
		'code_statut_benef': fields.char('Statut'),
		'date_effet_police': fields.date('Date effet de l’exercice'),
		'effectif_det': fields.float('Effectif', digits=(18, 0)),  
		'nbre_jour_mois_det': fields.float('Jour/Mois', digits=(18, 0)),  
		'nbre_jour_mois_exercice': fields.float('Nombre Jour/Mois', digits=(18, 0)),  
		'type_jour_mois_det': fields.float('Type', digits=(1, 0)),  
		'prime_indivuel': fields.float('Prime', digits=(18, 0)),
		'prime_indivuel_sida': fields.float('Prime SIDA', digits=(18, 0)),

		'prime_indivuel_tot': fields.float('Total Prime', digits=(18, 2)),
		'prime_indivuel_sida_tot': fields.float('Total Prime sida', digits=(18, 2)),

		'st_creat_incorpo': fields.char('Création/Incorporation'),

		'dt_sortie_benef': fields.date('Date de sortie de la police'),

		'deb_tran_age': fields.integer('Début tranche d\'âge'),  
		'fin_tran_age': fields.integer('Fin tranche d\'âge'), 

		'ident_centre': fields.many2one('mcisogem.centre.gestion', "Centre de gestion"),
		'code_gest': fields.char('libelle_gest', size=10),
		'code_langue': fields.char('code_langue', size=10),
	}
	
	_defaults = {         
		'code_gest': _get_cod_gest,
		'ident_centre': _get_cod_gest_id,
		'code_langue': _get_cod_lang,
	}

	_order = 'code_statut_benef ASC'