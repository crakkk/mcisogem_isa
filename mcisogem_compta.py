# -*- coding:utf8 -*-
import time
from random import randint
from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import osv
from openerp import tools
from openerp.tools.translate import _
import openerp
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

from dateutil import parser
import logging

_logger = logging.getLogger(__name__)






class mcisogem_banque_commerciale(osv.osv):
	_name = "mcisogem.banque.commerciale"
	_description = 'Banque commerciale'






	_columns = {
		'code_banque': fields.char('Code', size=10, required=True),
		'name': fields.char('Libellé', required=True),
		'adresse': fields.char('Adresse'),
		'tel': fields.char('Téléphone'),
		'fax': fields.char('Fax'),
		'email': fields.char('E-mail'),
		'gestionnaire': fields.char('Gestionnaire'),
		'swift_code': fields.char('Swift code', required=True)
	}

class mcisogem_banque_reglement(osv.osv):
	_name = "mcisogem.banque.reglement"
	_description = 'Banque reglement'
	
	_columns = {
		'banque_com_id': fields.many2one('mcisogem.banque.commerciale', 'Banque commerciale', required=True),
		'name': fields.char('Code banque règlement', required=True),
		'num_cmpte': fields.char('N° compte bancaire', required=True),
		'banque_int': fields.char('Code banque interne', required=True),
		'code_journal': fields.char('Code journal'),
		'compte_treso': fields.char('Compte de trésorerie'),
		'date_clot': fields.date('Date de clôture'),
		'observ': fields.text('Observations')
	}

	def create(self, cr, uid, vals, context=None):
		vals['name'] = vals['name'].upper()
		vals['code_journal'] = vals['name'].upper()
		return super(mcisogem_banque_reglement, self).create(cr, uid, vals, context=context)



class mcisogem_centre_temp(osv.osv):
	_name = "mcisogem.centre.temp"
	
	_columns = {
		'centre_id': fields.many2one('mcisogem.centre', ''),
		'cpta_centre': fields.char(''),
		'compta_prestat_tiers': fields.char('')
	}

class mcisogem_prest_temp(osv.osv):
	_name = "mcisogem.prest.temp"
	
	_columns = {
		'prest_id': fields.many2one('mcisogem.prestation', ''),
		'centre_id' : fields.many2one('mcisogem.centre', '')
	}

class mcisogem_account_period(osv.osv):
	_name = "mcisogem.account.period"
	_description = "Période"
	_columns = {
		'name': fields.char('Libéllé', required=True),
		'code': fields.char('Code', size=12),
		'date_start': fields.date('Début', required=True, states={'done':[('readonly',True)]}),
		'date_stop': fields.date('Fin', required=True, states={'done':[('readonly',True)]}),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', required=True, states={'done':[('readonly',True)]}, select=True),
		'state': fields.selection([('draft','Ouvert'), ('done','Clôturé')], 'Status', readonly=True, copy=False)
	}
	_defaults = {
		'state': 'draft',
	}
	_order = "date_start asc"
	

	def _check_duration(self,cr,uid,ids,context=None):
		obj_period = self.browse(cr, uid, ids[0], context=context)
		if obj_period.date_stop < obj_period.date_start:
			return False
		return True

	def _check_year_limit(self,cr,uid,ids,context=None):
		for obj_period in self.browse(cr, uid, ids, context=context):
			if obj_period.exercice_id.date_fin < obj_period.date_stop or \
			   obj_period.exercice_id.date_fin < obj_period.date_start or \
			   obj_period.exercice_id.date_fin > obj_period.date_start or \
			   obj_period.exercice_id.date_fin > obj_period.date_stop:
				return False       
		return True

	_constraints = [
		(_check_duration, 'Erreur!\nLa durée de la période est invalide.', ['date_stop'])
	]


class mcisogem_ecriture_comptable(osv.osv):
	_name = "mcisogem.ecriture.comptable"
	_description = 'Ecriture comptable'

	def button_cancel(self, cr, uid, ids, context=None):
		result = self.browse(cr, uid, ids[0], context=context)
		result_table = self.pool.get('mcisogem.prestation').search(cr, uid, [('ecriture_id', '=', result.id)])
		prestat_data = self.pool.get('mcisogem.prestation').browse(cr, uid, result_table)
		for ind_presta in prestat_data: 
			self.pool.get('mcisogem.prestation').write(cr, uid, ind_presta.id, {'state':'VS'} , context=context)

		result_etat1 = self.pool.get('mcisogem.prestation.etat.sinistre.v').search(cr, uid, [('ecriture_id', '=', result.id)])
		if result_etat1:
			self.pool.get('mcisogem.prestation.etat.sinistre.v').unlink(cr, uid, result_etat1, context=context) 

		result_etat2 = self.pool.get('mcisogem.prestation.etat.sinistre.v2').search(cr, uid, [('ecriture_id', '=', result.id)])
		if result_etat2:
			self.pool.get('mcisogem.prestation.etat.sinistre.v2').unlink(cr, uid, result_etat2, context=context) 

		self.write(cr, uid, ids, {'state':'A','date_annulation' : time.strftime("%Y-%m-%d", time.localtime())}, context=context)

		vals = {}
		vals['type_ecriture'] = result.type_ecriture
		vals['mode_paiement'] = result.mode_paiement
		vals['state'] = "A"
		vals['num_piece_reglmt'] = result.type_ecriture
		vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
		vals['code_journal'] = result.code_journal
		vals['periode_id'] = result.periode_id.id
		vals['centre_id'] = result.centre_id.id
		vals['date_annulation'] = time.strftime("%Y-%m-%d", time.localtime())
		vals['garant_id'] = result.garant_id.id
		vals['banque_int'] = result.banque_int		
		vals['num_piece_reglmt'] = result.num_piece_reglmt
		vals['libelle_reglemt'] = result.libelle_reglemt
		vals['montant'] = - result.montant
		vals['sens'] = "C"
		vals['compte_gle'] = result.compte_gle
		vals['compte_tiers'] = result.compte_tiers
		vals['compte_compta_tp'] = result.compte_compta_tp
		vals['compte_compta_rd'] = result.compte_compta_rd
		rep = self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)

		vals['type_ecriture'] = result.type_ecriture
		vals['mode_paiement'] = result.mode_paiement
		vals['state'] = "A"
		vals['num_piece_reglmt'] = result.type_ecriture
		vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
		vals['code_journal'] = result.code_journal
		vals['periode_id'] = result.periode_id.id
		vals['centre_id'] = result.centre_id.id
		vals['date_annulation'] = time.strftime("%Y-%m-%d", time.localtime())
		vals['garant_id'] = result.garant_id.id
		vals['banque_int'] = result.banque_int		
		vals['num_piece_reglmt'] = result.num_piece_reglmt
		vals['libelle_reglemt'] = result.libelle_reglemt
		vals['montant'] = - result.montant
		vals['sens'] = "D"
		vals['compte_gle'] = result.compte_gle
		vals['compte_tiers'] = ""
		vals['compte_compta_tp'] = result.compte_compta_tp
		vals['compte_compta_rd'] = result.compte_compta_rd
		rep = self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)

		return True
	
	_columns = {
		'type_ecriture': fields.selection([('CONSTATATION', 'Constatation'), ('PAIEMENT', 'Paiement')], 'Type d\'écriture', readonly=True),
		'mode_paiement': fields.selection([('RD', 'Remboursement direct'), ('TP', 'Tiers payant')], 'Type d\'écriture'),
		'num_piece_reglmt': fields.char('N° pièce', readonly=True),
		'date_ecriture': fields.date('Date d\'écriture', readonly=True),
		'centre_id' : fields.many2one('mcisogem.centre' , 'Centre'),
		'garant_id' : fields.many2one('mcisogem.garant' , 'Garant'),

		'code_journal': fields.char('Code journal', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Période'),
		'date_annulation': fields.date('Date d\'annulation', readonly=True),

		'libelle_reglemt': fields.char('Libéllé', readonly=True),

		'montant': fields.integer('Montant', readonly=True),
		'sens': fields.selection([('C', 'C'), ('D', 'D')], 'Sens', readonly=True),
		'compte_gle': fields.char('Compte général', readonly=True),
		'compte_tiers': fields.char('Compte tiers', readonly=True),
		'prestation_ids' : fields.one2many('mcisogem.prestation','ecriture_id','Prestations'),

		'banque_int': fields.char('Code banque interne', readonly=True),

		'compte_compta_tp': fields.char('Compte Comptabilité TP', readonly=True),
		'compte_compta_rd': fields.char('Compte Comptabilité RD', readonly=True),
		'state': fields.selection([
			('V', "Validé"),
			('A', "Annuler"),
		], 'Statut' , readonly=True),
	}
	_rec_name = 'id'


class mcisogem_validation_compta_prestation_reglement(osv.osv):
	_name = 'mcisogem.validation.compta.prestation.reglement'

	_inherit = ['ir.needaction_mixin']

	_mail_post_access = 'read'

	def _get_regime(self, cr, uid, context=None):
		regime_tp = self.pool.get('mcisogem.regime').search(cr,uid,[('code_regime' , '=' , 'TP')])		
		regime_id = self.pool.get('mcisogem.regime').browse(cr,uid,regime_tp).id
		return regime_id


	_columns = {
		'mode_paiement': fields.many2one('mcisogem.regime', 'Type de remboursement'),
		'centre_ids' : fields.many2many('mcisogem.centre' , 'regl_centre_rel4' , 'id_g4' , 'id_c' , 'Centres'),
		'date_reglement' : fields.date('Date validation règlement'),
		'num_fact': fields.integer('N° Facture'),
		'medecin_ids' : fields.many2many('mcisogem.praticien' , 'regl_prat_rel4' , 'id_g' , 'id_m' , 'Prescripteurs'),
		'garant_ids' : fields.many2many('mcisogem.garant' , 'regl_garant_rel4' , 'id_g' , 'id_v' , 'Garants'),
		'periode_ids' : fields.many2many('mcisogem.account.period', 'regl_period_rel4' , 'id_g' , 'id_p' , 'Date Comptable'),
		'prestation_ids' : fields.many2many('mcisogem.prestation' ,'regl_prest_rel4', 'id_g' , 'id_p' , 'Prestations'),
		'affiche' : fields.boolean(''),
		
	}
	_defaults = {
		'affiche' : False,
		'mode_paiement' : _get_regime,
	}
	
	_rec_name = 'id'

	def onchange_pram(self, cr, uid, ids, mode_paiement,centre_ids,garant_ids,periode_ids,num_fact, context=None):        
		d = {}
		critere = []
		centres = centre_ids[0][2]
		garants = garant_ids[0][2]
		periodes = periode_ids[0][2]
		critere.append(('state' , '=' , 'VD'))

		if mode_paiement:
			critere.append(('mode_paiement' , '=' , self._get_regime(cr,uid,context)))

		if len(centres)>0:			
			critere.append(('centre_id' , '=' , centres))

		if num_fact:
			critere.append(('num_fact' , '=' , num_fact))

		if len(garants)>0:			
			critere.append(('garant_id' , 'in' , garants))

		if len(periodes)>0:			
			critere.append(('periode_id' , 'in' , periodes))

		d = {'prestation_ids': critere}
		p_ids = self.pool.get('mcisogem.prestation').search(cr, uid, critere)

		v = {}
		v = {'prestation_ids': p_ids}

		return {'domain': d, 'value': v, 'affiche': True}



	def _needaction_count(self , cr, uid,ids, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "RESPONSABLE COMPTABLE" or group_obj.name == "UTILISATEUR COMPTABLE":
					return self.pool.get('mcisogem.prestation').search_count(cr,uid,[('state' , 'in' , ['VD']), ('mode_paiement' , '=' , self._get_regime(cr,uid,context))])



	def create(self, cr, uid, data, context=None):
		prestations = data['prestation_ids'][0][2]
		cr.execute("delete from mcisogem_garant_temp where create_uid=%s", (uid,))
		sum_montant = 0
		les_prestation =[]

		for prest in prestations:
			
			self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'state':'VC' , 'date_reglement' : time.strftime("%Y-%m-%d")} , context=context)
			prestObj = self.pool.get('mcisogem.prestation').browse(cr,uid,prest)

			table = self.pool.get('mcisogem.ecriture.comptable').search(cr, uid, [('garant_id' , '=' , prestObj.garant_id.id),('date_ecriture' , '=' , time.strftime("%Y-%m-%d"))])
			ecri_data = self.pool.get('mcisogem.ecriture.comptable').browse(cr,uid,table)

			cr.execute('select num_piece_reglmt from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s', (prestObj.garant_id.id, time.strftime("%Y-%m-%d")))
			lesgroups = cr.dictfetchall()

			vals = {}

			if len(lesgroups) > 0:
				cr.execute('select num_piece_reglmt from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s', (prestObj.garant_id.id, time.strftime("%Y-%m-%d")))					
				test = cr.dictfetchall()[0]
				num = test['num_piece_reglmt']
			else:
				num = prestObj.id
			
			vals['type_ecriture'] = "CONSTATATION"
			vals['mode_paiement'] = "TP"
			vals['state'] = "V"
			vals['num_piece_reglmt'] = num
			vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
			vals['code_journal'] = "ODPR"
			vals['periode_id'] = prestObj.periode_id.id
			vals['banque_int'] = prestObj.garant_id.cpt_tp2		
			vals['garant_id'] = prestObj.garant_id.id

			vals['libelle_reglemt'] = prestObj.garant_id.name + " " + "du:" + prestObj.periode_id.code
			vals['montant'] = prestObj.part_gest
			vals['sens'] = "C"
			vals['compte_gle'] = prestObj.centre_id.cpta_centre
			vals['compte_tiers'] = prestObj.centre_id.compta_prestat_tiers
			vals['compte_compta_rd'] = ""

			id_ecriture = self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)

			sum_montant += prestObj.part_gest

			les_prestation.append(prest)

			self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'ecriture_id': id_ecriture} , context=context)

			
			nbre_garant = self.pool.get('mcisogem.garant.temp').search_count(cr,uid,[('garant_id' , '=' , prestObj.garant_id.id), ('create_uid' , '=' , uid)])	

			if nbre_garant == 0:
				cr.execute("insert into mcisogem_garant_temp (garant_id,create_uid) values(%s,%s)", (prestObj.garant_id.id, uid))


		rep = super(mcisogem_validation_compta_prestation_reglement , self).create(cr, uid, data, context=context)

		table_garant = self.pool.get('mcisogem.garant.temp').search(cr, uid, [('create_uid' , '=' , uid)])
		garant_data = self.pool.get('mcisogem.garant.temp').browse(cr,uid,table_garant)
		

		for garant in garant_data:
			
			cr.execute("select * from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s and mode_paiement=%s", (garant.garant_id.id, time.strftime("%Y-%m-%d"), 'TP'))
			test1 = cr.dictfetchall()

			if len(test1) > 0:
				vals = {}
				cr.execute("select * from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s and mode_paiement=%s", (garant.garant_id.id, time.strftime("%Y-%m-%d"), 'TP'))
				ecri2 = cr.dictfetchall()[0]

				cr.execute("select sum(montant) as montant_debit from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s and mode_paiement=%s", (garant.garant_id.id, time.strftime("%Y-%m-%d"), 'TP'))
				montant2 = cr.dictfetchall()[0]

				vals['type_ecriture'] = "CONSTATATION"
				vals['mode_paiement'] = "TP"
				vals['state'] = "V"
				vals['num_piece_reglmt'] = ecri2['num_piece_reglmt']
				vals['date_ecriture'] = ecri2['date_ecriture']
				vals['code_journal'] = ecri2['code_journal']
				vals['periode_id'] = ecri2['periode_id']
				vals['banque_int'] = ecri2['banque_int']		
				vals['garant_id'] = ecri2['garant_id']

				vals['libelle_reglemt'] = ecri2['libelle_reglemt']
				vals['montant'] = sum_montant
				vals['sens'] = "D"
				vals['compte_gle'] = garant.garant_id.cpt_tp
				# vals['compte_tiers'] = ""
				vals['compte_compta_tp'] = ecri2['compte_compta_rd']

				self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)
		return rep



class mcisogem_validation_compta_prestation_remb(osv.osv):
	_name = 'mcisogem.validation.compta.prestation.remb'

	_inherit = ['ir.needaction_mixin']

	_mail_post_access = 'read'

	def _get_regime(self, cr, uid, context=None):
		regime_tp = self.pool.get('mcisogem.regime').search(cr,uid,[('code_regime' , '=' , 'RD')])		
		regime_id = self.pool.get('mcisogem.regime').browse(cr,uid,regime_tp).id
		return regime_id


	_columns = {
		'mode_paiement': fields.many2one('mcisogem.regime', 'Type de remboursement', domain=[('code_regime', '=', ['RD'])]),
		'centre_ids' : fields.many2many('mcisogem.centre' , 'regl_centre_rel4' , 'id_g4' , 'id_c' , 'Centres'),
		'date_paiement_reglement' : fields.date('Date validation règlement'),
		'num_fact': fields.integer('N° Facture'),
		'date_paiement_remboursement' : fields.date('Date validation remboursement'),
		'medecin_ids' : fields.many2many('mcisogem.praticien' , 'regl_prat_rel4' , 'id_g' , 'id_m' , 'Prescripteurs'),
		'garant_ids' : fields.many2many('mcisogem.garant' , 'regl_garant_rel4' , 'id_g' , 'id_v' , 'Garants'),
		'periode_ids' : fields.many2many('mcisogem.account.period', 'regl_period_rel4' , 'id_g' , 'id_p' , 'Date Comptable'),
		'prestation_ids' : fields.many2many('mcisogem.prestation' ,'regl_prest_rel4', 'id_g' , 'id_p' , 'Prestations'),
		'affiche' : fields.boolean(''),
		
	}
	_defaults = {
		'affiche' : False,
		'mode_paiement' : _get_regime,
	}
	
	_rec_name = 'id'

	def onchange_pram(self, cr, uid, ids, mode_paiement,centre_ids,garant_ids,periode_ids,num_fact, context=None):        
		d = {}
		critere = []
		centres = centre_ids[0][2]
		garants = garant_ids[0][2]
		periodes = periode_ids[0][2]
		critere.append(('state' , '=' , 'VD'))

		if mode_paiement:
			critere.append(('mode_paiement' , '=' , self._get_regime(cr,uid,context)))

		if len(centres)>0:			
			critere.append(('centre_id' , '=' , centres))

		if num_fact:
			critere.append(('num_fact' , '=' , num_fact))

		if len(garants)>0:			
			critere.append(('garant_id' , 'in' , garants))

		if len(periodes)>0:			
			critere.append(('periode_id' , 'in' , periodes))

		d = {'prestation_ids' : critere}
		p_ids = self.pool.get('mcisogem.prestation').search(cr, uid, critere)

		v = {}
		v = {'prestation_ids': p_ids}

		return {'domain': d, 'value': v , 'affiche' : True}



	def _needaction_count(self , cr, uid,ids, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "RESPONSABLE COMPTABLE" or group_obj.name == "UTILISATEUR COMPTABLE":
					return self.pool.get('mcisogem.prestation').search_count(cr,uid,[('state' , 'in' , ['VD']), ('mode_paiement' , '=' , self._get_regime(cr,uid,context))])



	def create(self, cr, uid, data, context=None):
		prestations = data['prestation_ids'][0][2]
		cr.execute("delete from mcisogem_garant_temp where create_uid=%s", (uid,))
		sum_montant = 0

		for prest in prestations:
			self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'state':'VC' , 'date_remboursement' : time.strftime("%Y-%m-%d")} , context=context)
			prestObj = self.pool.get('mcisogem.prestation').browse(cr,uid,prest)

			cr.execute('select count(*) from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s', (prestObj.garant_id.id, time.strftime("%Y-%m-%d")))
			valid = cr.fetchone()[0]

			table = self.pool.get('mcisogem.ecriture.comptable').search(cr, uid, [('garant_id' , '=' , prestObj.garant_id.id),('date_ecriture' , '=' , time.strftime("%Y-%m-%d"))])
			ecri_data = self.pool.get('mcisogem.ecriture.comptable').browse(cr,uid,table)

			cr.execute('select num_piece_reglmt from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s', (prestObj.garant_id.id, time.strftime("%Y-%m-%d")))
			lesgroups = cr.dictfetchall()

			vals = {}

			if len(lesgroups) > 0:
				cr.execute('select num_piece_reglmt from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s', (prestObj.garant_id.id, time.strftime("%Y-%m-%d")))					
				test = cr.dictfetchall()[0]
				num = test['num_piece_reglmt']
			else:
				num = prestObj.id
				

			typeprest = "CONSTATATION"
			typetp = "RD"
			date = time.strftime("%Y-%m-%d", time.localtime())
			code_journal = "ODPR"
			periode_id = prestObj.periode_id.id
			banque_int = prestObj.garant_id.cpt_tp2		
			garant_id = prestObj.garant_id.id
			lib = prestObj.garant_id.name + " " + "du:" + prestObj.periode_id.code
			sens = "C"
			montant = prestObj.part_gest
			compte_gle = prestObj.centre_id.cpta_centre
			compte_tiers = prestObj.centre_id.compta_prestat_tiers
			compte_compta_rd = ""

			sum_montant += prestObj.part_gest

			cr.execute("insert into mcisogem_ecriture_comptable (type_ecriture,num_piece_reglmt,mode_paiement,date_ecriture,code_journal,periode_id,banque_int,garant_id,libelle_reglemt,sens,montant,compte_gle,compte_tiers,compte_compta_rd,state) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (typeprest, num,typetp,date,code_journal,periode_id,banque_int,garant_id,lib,sens,montant,compte_gle,compte_tiers,compte_compta_rd,'V'))

			nbre_garant = self.pool.get('mcisogem.garant.temp').search_count(cr,uid,[('garant_id' , '=' , prestObj.garant_id.id), ('create_uid' , '=' , uid)])	

			if nbre_garant == 0:
				cr.execute("insert into mcisogem_garant_temp (garant_id,create_uid) values(%s,%s)", (prestObj.garant_id.id, uid))


		rep = super(mcisogem_validation_compta_prestation_reglement , self).create(cr, uid, data, context=context)

		table_garant = self.pool.get('mcisogem.garant.temp').search(cr, uid, [('create_uid' , '=' , uid)])
		garant_data = self.pool.get('mcisogem.garant.temp').browse(cr,uid,table_garant)
		

		for garant in garant_data:
			
			cr.execute("select * from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s and mode_paiement=%s", (garant.garant_id.id, time.strftime("%Y-%m-%d"), 'RD'))
			test = cr.dictfetchall()

			if len(test) > 0:
				cr.execute("select * from mcisogem_ecriture_comptable where garant_id=%s and date_ecriture=%s and mode_paiement=%s", (garant.garant_id.id, time.strftime("%Y-%m-%d"), 'RD'))
				ecri = cr.dictfetchall()[0]

				vals = {}

				vals['type_ecriture'] = "CONSTATATION"
				vals['mode_paiement'] = "RD"
				vals['num_piece_reglmt'] = ecri['num_piece_reglmt']
				vals['date_ecriture'] = ecri['date_ecriture']
				vals['code_journal'] = ecri['code_journal']
				vals['periode_id'] = ecri['periode_id']
				vals['banque_int'] = ecri['banque_int']		
				vals['garant_id'] = ecri['garant_id']

				vals['libelle_reglemt'] = ecri['libelle_reglemt']
				vals['montant'] = sum_montant
				vals['sens'] = "D"
				vals['compte_gle'] = garant.garant_id.cpt_rd
				vals['compte_tiers'] = ""
				vals['compte_compta_rd'] = ecri['compte_compta_rd']

				self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)

		return rep


class mcisogem_paiement_sinistre(osv.osv):
	_name = 'mcisogem.paiement.sinistre'

	_inherit = ['ir.needaction_mixin']

	_mail_post_access = 'read'

	def button_recherche(self, cr, uid , ids, context=None):
		cr.execute("delete from mcisogem_centre_temp where create_uid=%s", (uid,))	
		cr.execute("delete from mcisogem_garant_temp where create_uid=%s", (uid,))	
		cr.execute("delete from mcisogem_prestation_recherche_temp where create_uid=%s", (uid,))
		cr.execute("delete from mcisogem_prestation_recherche_result where create_uid=%s", (uid,))	
		cr.execute("delete from mcisogem_prestation_recherche_result where state=%s", ('P',))
		cr.execute("delete from mcisogem_prestation_temp where create_uid=%s", (uid,))
		cr.execute("delete from mcisogem_prest_temp where create_uid=%s", (uid,))

		elem_table = self.search(cr,uid,[('id','=',ids)])
		elem_obj = self.browse(cr,uid,elem_table)

		if not elem_obj.prestation_ids:
			raise osv.except_osv('Attention !' , 'Vous devez ajouter au moins un sinistre avant de faire le regroupement.')
		for prest in elem_obj.prestation_ids:
			if prest.state == 'P':
				raise osv.except_osv('Attention !' , 'Un des sinistres que vous avez selectionner à  déjà été payer.')

		for prest in elem_obj.prestation_ids:
			cr.execute("insert into mcisogem_prest_temp (prest_id,create_uid) values(%s,%s)", (prest.id, uid))
			cr.execute("select * from mcisogem_centre_temp where centre_id=%s and create_uid=%s", (prest.centre_id.id, uid))
			lescentres = cr.dictfetchall()
			cr.execute("select * from mcisogem_garant_temp where garant_id=%s and create_uid=%s", (prest.garant_id.id, uid))
			lesgarants = cr.dictfetchall()

			if len(lescentres) == 0:
				cr.execute("insert into mcisogem_centre_temp (centre_id,create_uid) values(%s,%s)", (prest.centre_id.id, uid))
			if len(lesgarants) == 0:
				cr.execute("insert into mcisogem_garant_temp (garant_id,create_uid) values(%s,%s)", (prest.garant_id.id, uid))


		centre_table = self.pool.get('mcisogem.centre.temp').search(cr,uid,[('create_uid','=',uid)])
		centre_ids = self.pool.get('mcisogem.centre.temp').browse(cr,uid,centre_table)

		garant_table = self.pool.get('mcisogem.garant.temp').search(cr,uid,[('create_uid','=',uid)])
		garant_ids = self.pool.get('mcisogem.garant.temp').browse(cr,uid,garant_table)
		
		for centre in centre_ids:
			for garant in garant_ids:
				elem_table = self.search(cr,uid,[('id','=',ids)])
				elem_obj = self.browse(cr,uid,elem_table)
				montant_total = 0
				montant_exclu = 0 
				part_gest = 0
				nbre_prestat = 0
				for val in elem_obj.prestation_ids:
					if val.centre_id.id == centre.centre_id.id and val.garant_id.id == garant.garant_id.id:
						montant_total += val.montant_total
						montant_exclu += val.montant_exclu
						nbre_prestat += 1
				vals = {}
				
				vals['centre_id'] = centre.centre_id.id 
				vals['garant_id'] = garant.garant_id.id 
				vals['montant_exclus'] = montant_exclu
				vals['montant_total'] = montant_total
				vals['nbre_prestat'] = nbre_prestat		
				vals['banque_id'] = garant.garant_id.banque_id.id
				vals['code_journal'] = garant.garant_id.banque_id.code_journal
				vals['banque_int'] = garant.garant_id.cpt_tp2

				vals['compte_tiers_prestataire'] = centre.centre_id.compta_prestat_tiers
				vals['compte_gle_prestataire'] = centre.centre_id.cpta_centre
				vals['state'] = "VF"
				# vals['mode_paiement'] = elem_obj.mode_paiement.code_regime

				if self.pool.get('mcisogem.prestation').search_count(cr,uid,[('centre_id' , '=' ,centre.centre_id.id) , ('garant_id' , '=' , garant.garant_id.id)]) > 0:

					self.pool.get('mcisogem.prestation.temp').create(cr, uid, vals, context)

		cr.execute("select * from mcisogem_prestation_temp where create_uid=%s", (uid,))
		lesprestatemp = cr.dictfetchall()

		for pres in lesprestatemp:
			mode_paiement = self.browse(cr,uid,ids[0]).mode_paiement.code_regime
			cr.execute("insert into mcisogem_prestation_recherche_result (create_uid,mode_paiement,centre_id,garant_id,montant_exclus,montant_total,nbre_prestat,banque_id,code_journal,banque_int,compte_tiers_prestataire,compte_gle_prestataire,state,cod_prestation) values(%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (uid,mode_paiement, pres['centre_id'],pres['garant_id'],pres['montant_exclus'],pres['montant_total'],pres['nbre_prestat'],pres['banque_id'],pres['code_journal'],pres['banque_int'],pres['compte_tiers_prestataire'],pres['compte_gle_prestataire'],'VF',pres['id']))

		ctx = (context or {}).copy()
		# ctx['form_view_ref'] = 'view_mcisogem_prestation_recherche_temp_form'
		form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_mcisogem_prestation_recherche_temp_form')[1]

		return {
		  'name':'Paiement des factures',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.prestation.recherche.temp',
		  'views': [(form_id , 'form')],
		  'view_id':form_id,
		  'target':'current',
		  'domain' : [('result_ids.create_uid', '=', uid)],
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}

	def button_regroup(self, cr, uid , ids, context=None):
		cr.execute("delete from mcisogem_centre_temp where create_uid=%s", (uid,))	
		cr.execute("delete from mcisogem_garant_temp where create_uid=%s", (uid,))	
		cr.execute("delete from mcisogem_prestation_recherche_temp where create_uid=%s", (uid,))
		cr.execute("delete from mcisogem_prestation_recherche_result where create_uid=%s", (uid,))	
		cr.execute("delete from mcisogem_prestation_recherche_result where state=%s", ('P',))
		cr.execute("delete from mcisogem_prestation_temp where create_uid=%s", (uid,))
		cr.execute("delete from mcisogem_prest_temp where create_uid=%s", (uid,))

		elem_table = self.search(cr,uid,[('id','=',ids)])
		elem_obj = self.browse(cr,uid,elem_table)

		if not elem_obj.prestation_ids:
			raise osv.except_osv('Attention !' , 'Vous devez ajouter au moins un sinistre avant de faire le regroupement.')
		for prest in elem_obj.prestation_ids:
			if prest.state == 'P':
				raise osv.except_osv('Attention !' , 'Un des sinistres que vous avez selectionner à  déjà été payer.')

		for prest in elem_obj.prestation_ids:
			cr.execute("insert into mcisogem_prest_temp (prest_id,centre_id,create_uid) values(%s,%s,%s)", (prest.id,prest.centre_id.id, uid))
			cr.execute("select * from mcisogem_centre_temp where centre_id=%s and create_uid=%s", (prest.centre_id.id, uid))
			lescentres = cr.dictfetchall()
			cr.execute("select * from mcisogem_garant_temp where garant_id=%s and create_uid=%s", (prest.garant_id.id, uid))
			lesgarants = cr.dictfetchall()

			if len(lescentres) == 0:
				cr.execute("insert into mcisogem_centre_temp (centre_id,create_uid) values(%s,%s)", (prest.centre_id.id, uid))
			if len(lesgarants) == 0:
				cr.execute("insert into mcisogem_garant_temp (garant_id,create_uid) values(%s,%s)", (prest.garant_id.id, uid))


		centre_table = self.pool.get('mcisogem.centre.temp').search(cr,uid,[('create_uid','=',uid)])
		centre_ids = self.pool.get('mcisogem.centre.temp').browse(cr,uid,centre_table)

		garant_table = self.pool.get('mcisogem.garant.temp').search(cr,uid,[('create_uid','=',uid)])
		garant_ids = self.pool.get('mcisogem.garant.temp').browse(cr,uid,garant_table)
		
		for centre in centre_ids:
			for garant in garant_ids:
				elem_table = self.search(cr,uid,[('id','=',ids)])
				elem_obj = self.browse(cr,uid,elem_table)
				montant_total = 0
				montant_exclu = 0 
				part_gest = 0
				nbre_prestat = 0
				for val in elem_obj.prestation_ids:
					if val.centre_id.id == centre.centre_id.id and val.garant_id.id == garant.garant_id.id:
						montant_total += val.montant_total
						montant_exclu += val.montant_exclu
						nbre_prestat += 1
				vals = {}
				
				vals['centre_id'] = centre.centre_id.id 
				vals['garant_id'] = garant.garant_id.id 
				vals['montant_exclus'] = montant_exclu
				vals['montant_total'] = montant_total
				vals['nbre_prestat'] = nbre_prestat		
				vals['banque_id'] = garant.garant_id.banque_id.id
				vals['code_journal'] = garant.garant_id.banque_id.code_journal
				vals['banque_int'] = garant.garant_id.cpt_tp2

				vals['compte_tiers_prestataire'] = centre.centre_id.compta_prestat_tiers
				vals['compte_gle_prestataire'] = centre.centre_id.cpta_centre
				vals['state'] = "VF"
				# vals['mode_paiement'] = elem_obj.mode_paiement.code_regime
				if self.pool.get('mcisogem.prestation').search_count(cr,uid,[('centre_id' , '=' ,centre.centre_id.id) , ('garant_id' , '=' , garant.garant_id.id)]) > 0:

					self.pool.get('mcisogem.prestation.temp').create(cr, uid, vals, context)

		cr.execute("select * from mcisogem_prestation_temp where create_uid=%s", (uid,))
		lesprestatemp = cr.dictfetchall()

		for pres in lesprestatemp:
			mode_paiement = self.browse(cr,uid,ids[0]).mode_paiement.code_regime
			cr.execute("insert into mcisogem_prestation_recherche_result (create_uid,mode_paiement,centre_id,garant_id,montant_exclus,montant_total,nbre_prestat,banque_id,code_journal,banque_int,compte_tiers_prestataire,compte_gle_prestataire,state,cod_prestation) values(%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (uid,mode_paiement, pres['centre_id'],pres['garant_id'],pres['montant_exclus'],pres['montant_total'],pres['nbre_prestat'],pres['banque_id'],pres['code_journal'],pres['banque_int'],pres['compte_tiers_prestataire'],pres['compte_gle_prestataire'],'VF',pres['id']))

		ctx = (context or {}).copy()
		form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_mcisogem_prestation_recherche_virement_temp_form')[1]

		return {
		  'name':'Paiement des factures',
		  'view_type':'form',
		  'view_mode':'form',
		  # 'res_model':'mcisogem.prestation.recherche.virement.temp',
		  'res_model':'mcisogem.prestation.recherche.virement.temp',
		  'views': [(form_id , 'form')],
		  'view_id':form_id,
		  'target':'current',
		  'domain' : [('result_ids.create_uid', '=', uid)],
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}
		


	_columns = {
		'mode_paiement': fields.many2one('mcisogem.regime', 'Type de remboursement', domain=[('code_regime', 'in', ['TP', 'RD'])], required=True),
		'centre_ids' : fields.many2many('mcisogem.centre' , 'regl_centre_rel2' , 'id_g' , 'id_c' , 'Centres'),
		'date_reglement' : fields.date('Date validation règlement'),
		'date_remboursement' : fields.date('Date validation remboursement'),
		'medecin_ids' : fields.many2many('mcisogem.praticien' , 'regl_prat_rel2' , 'id_g' , 'id_m' , 'Prescripteurs'),
		'num_fact': fields.integer('N° Facture'),
		'garant_ids' : fields.many2many('mcisogem.garant' , 'regl_garant_rel2' , 'id_g' , 'id_v' , 'Garants'),
		'periode_ids' : fields.many2many('mcisogem.account.period', 'regl_period_rel2' , 'id_g' , 'id_p' , 'Date Comptable'),
		'prestation_ids' : fields.many2many('mcisogem.prestation' ,'regl_prest_rel2', 'id_g' , 'id_p' , 'Prestations')
		# 'prestation_ids' : fields.one2many('mcisogem.centre.temp','critere_id',''),		
	}
	
	_rec_name = 'mode_paiement'

	def onchange_pram(self, cr, uid, ids, mode_paiement,centre_ids,garant_ids,periode_ids,num_fact, context=None):        
		d = {}
		critere = []
		centres = centre_ids[0][2]
		garants = garant_ids[0][2]
		periodes = periode_ids[0][2]
		critere.append(('state' , '=' , 'VC'))

		if mode_paiement:

			critere.append(('mode_paiement' , '=' , mode_paiement))


		if len(centres)>0:
			
			critere.append(('centre_id' , '=' , centres))

		if num_fact:
			critere.append(('num_fact' , '=' , num_fact))

		if len(garants)>0:
			
			critere.append(('garant_id' , 'in' , garants))

		if len(periodes)>0:
			
			critere.append(('periode_id' , 'in' , periodes))


		d = {'prestation_ids': critere}
		p_ids = self.pool.get('mcisogem.prestation').search(cr, uid, critere)

		v = {}
		v = {'prestation_ids': p_ids}

		return {'domain': d, 'value': v}



	def _needaction_count(self , cr, uid,ids, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "RESPONSABLE COMPTABLE" or group_obj.name == "UTILISATEUR COMPTABLE":
					return self.pool.get('mcisogem.prestation').search_count(cr,uid,[('state' , 'in' , ['VC'])])



class mcisogem_prestation_temp(osv.osv):
	_name = 'mcisogem.prestation.temp'

	_columns = {

		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'), 
		'garant_id' : fields.many2one('mcisogem.garant' , 'Garant'),
		'montant_reclame' : fields.integer('Montant total réclamé', digits=(18, 0)),
		'montant_exclus' : fields.integer('Montant total exclus', digits=(18, 0)),
		'montant_total' : fields.integer('Montant total de règlement', digits=(18, 0)),

		'periode_id' : fields.many2one('mcisogem.account.period', 'Date comptable'),
   
		'nbre_prestat' : fields.integer('Nombre de prestation'),

		'num_cheque' : fields.char('N° Chèque'),

		'banque_id': fields.many2one('mcisogem.banque.reglement', 'Banque'),
		'code_journal': fields.char('Code journal'),
		'banque_int': fields.char('Code banque interne'),

		'compte_tiers_prestataire': fields.char('Compte tiers'),
		'compte_gle_prestataire': fields.char('Compte général'),

		'state': fields.selection([
			('SP', "Sinistre provisoire"),
			('V', "Validation des saisies"),
			('CRL', "Création des règlements"),
			('CRE', "Création des remboursements"),
			('VD', "Validation direction"),
			('VC', "Validation comptable"),
			('VF', "Validé"),
			('P', "Payé"),
		], 'Statut', readonly=True),
		'num_fact' : fields.char('N° Facture'),
		'mode_paiement' : fields.selection([
			('TP', "Tiers Payant"),
			('RD', "Remboursement direct"),
		], 'Mode de paiement')
	}
	_rec_name = "centre_id"


class mcisogem_garant_temp(osv.osv):
	_name = 'mcisogem.garant.temp'

	_columns = {
		'garant_id' : fields.many2one('mcisogem.garant','garant')		
	}


class mcisogem_garant_temp2(osv.osv):
	_name = 'mcisogem.garant.temp2'

	_columns = {
		'garant_id' : fields.many2one('mcisogem.garant','garant'),
		'critere1_id' : fields.many2one('mcisogem.recherche.etat.sinistre.c','critere'),	
		'garant_total' : fields.integer('Montant total'),
	}


class mcisogem_banquec_temp(osv.osv):
	_name = 'mcisogem.banquec.temp'

	_columns = {
		'banque_id' : fields.many2one('mcisogem.banque','garant'),
		'garant_id' : fields.many2one('mcisogem.garant','garant'),
		'critere2_id' : fields.many2one('mcisogem.recherche.etat.sinistre.c','critere'),	
		'banque_total' : fields.integer('Montant total'),	
	}


#######################PARAMETTRES CHEQUES#########################

class mcisogem_centre_c_temp(osv.osv):
	_name = 'mcisogem.centre.c.temp'

	_columns = {
		'centre_id' : fields.many2one('mcisogem.centre','centre'),
		'critere3_id' : fields.many2one('mcisogem.recherche.etat.sinistre.c','critere'),	
		'centre_total' : fields.integer('Montant total'),
	}


class mcisogem_garant_centre_temp(osv.osv):
	_name = 'mcisogem.garant.centre.temp'

	_columns = {
		'garant_id' : fields.many2one('mcisogem.garant','garant'),
		'centre_id' : fields.many2one('mcisogem.centre','centre'),
		'critere4_id' : fields.many2one('mcisogem.recherche.etat.sinistre.c','critere'),	
		'garant_total' : fields.integer('Montant total'),	
	}

###################################################################


class mcisogem_recherche_etat_sinistre_c(osv.osv):
	_name = 'mcisogem.recherche.etat.sinistre.c'

	_columns = {
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		'centre_ids' : fields.one2many('mcisogem.centre.c.temp', 'critere3_id'),
		'garant_id' : fields.many2one('mcisogem.garant', 'Garant'),
		'garant_ids' : fields.one2many('mcisogem.garant.centre.temp', 'critere4_id'),
		'garant_t_id' : fields.one2many('mcisogem.garant.temp2', 'critere1_id'),
		'periode_id' : fields.many2one('mcisogem.account.period','Date Comptable'),
		'banque_r_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement', required=True),
		'banque_c_id' : fields.many2one('mcisogem.banque','Banque '), 
		'banque_c_t_id' : fields.one2many('mcisogem.banquec.temp','critere2_id'), 
		'montant' : fields.integer('Date de valeur'),
		'mode_paiement' : fields.selection([
			('TP', "Tiers Payant"),
			('RD', "Remboursement direct"),
		], 'Mode de paiement'),
		'transfert_id' : fields.one2many('mcisogem.prestation.etat.sinistre.v.temp','critere_id',' '),
		'recherche' : fields.char('Recherche'),
		# 'periode_id' : fields.many2one('mcisogem.account.period' , 'Periode'),

		}

	_rec_name = 'id'
	_defaults = {
		'recherche': 'Recherche',
	
	}
	def create(self, cr, uid, vals, context=None):
		
		vals['aff_print'] = True
		# code_periode = time.strftime("%m/%Y", time.localtime())
		# periode_id = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',code_periode)])
		# periode_data = self.pool.get('mcisogem.account.period').browse(cr,uid,periode_id)
		# vals['periode_id'] = periode_data.id
 
		return super(mcisogem_recherche_etat_sinistre_c, self).create(cr,uid,vals,context)

	def print_recherche(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids, [], context=context)
		critere = self.browse(cr, uid, ids[0], context)

		nbr_sinistre = self.pool.get('mcisogem.prestation.etat.sinistre.v.temp').search_count(cr, uid, [('create_uid', '=', uid)])
		print('****nombre de bene recherche*****')
		print(nbr_sinistre)
		# raise osv.except_osv('Attention' ,'stop!')

		if (nbr_sinistre != 0 ):
			# return {
			# 		'type': 'ir.actions.report.xml',
			# 		'report_name': 'mcisogem_isa.report_sinistre_c_new',
			# 		'data': data,
			# }
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'mcisogem_isa.report_sinistre_c',
					'data': data,
			}
		else:
			raise osv.except_osv('Impossible' ,'aucun élement à imprimer!')

	def button_recherche(self, cr, uid , ids, context=None):

		critere = self.browse(cr, uid, ids[0])
		garant = critere.garant_id.id
		centre = critere.centre_id.id
		periode = critere.periode_id.id
		banque_r = critere.banque_r_id.id
		mode_paiement = critere.mode_paiement



		data = {}
		data['garant_id'] = garant
		data['centre_id'] = centre
		data['periode_id'] = periode
		data['banque_r_id'] = banque_r
		data['mode_paiement'] = mode_paiement
		
		self.pool.get('mcisogem.recherche.etat.sinistre.c').write(cr,uid,ids[0],data,context)
		
		requette = "SELECT id From mcisogem_prestation_etat_sinistre_v WHERE "

		if garant == False:
			requette += "1=1 "
		else:
			requette += "garant_id = {} ".format(garant)

		if centre == False:
			requette += "AND 1=1 "
		else : 
			if centre != "":
				requette += "AND centre_id = {} ".format(centre)

		if periode == False:
			requette += "AND 1=1 "
		else : 
			if periode != "":
				requette += "AND periode_id = {} ".format(periode)

		if banque_r == False:
			requette += "AND 1=1 "
		else : 
			if banque_r != "":
				requette += "AND banque_r_id = {} ".format(banque_r)

		if mode_paiement == False:
			requette += "AND 1=1 "
		else : 
			if mode_paiement != "":
				requette += "AND mode_paiement = '{}' ".format(mode_paiement)

		requette += "AND create_uid = '{}' ".format(uid)
			
		
		print('** la requette **')
		print(requette)
		print('** identifiant critere **')
		print(ids[0])
		#raise osv.except_osv('Attention' ,'Oups #TDC!')

		cr.execute('DELETE  FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s', (uid,))
		########### A
		cr.execute(requette)
		resultat_liste = cr.fetchall()
		print('**Lise des transferts recherchés**')
		print(resultat_liste)
		
		
		for ind_transf in resultat_liste:
			transferts = self.pool.get('mcisogem.prestation.etat.sinistre.v').browse(cr, uid, ind_transf, context)
			print(transferts.centre_id.name)
			data = {}
			
			data['centre_id'] = transferts.centre_id.id
			data['garant_id'] = transferts.garant_id.id
			data['periode_id'] = transferts.periode_id.id
			data['banque_r_id'] = transferts.banque_r_id.id
			data['banque_c_id'] = transferts.banque_c_id.id
			data['montant'] = transferts.montant
			data['mode_paiement'] = transferts.mode_paiement
			data['critere_id'] = ids[0]
			data['num_cheque'] = transferts.num_cheque

			self.pool.get('mcisogem.prestation.etat.sinistre.v.temp').create(cr, uid, data, context)

		cr.execute('DELETE  FROM mcisogem_garant_temp2 WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT garant_id FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s', (uid,))
		garant_liste = cr.fetchall()
		for ind_garant in garant_liste:
			cr.execute('SELECT  sum(montant) as total_garant FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s and garant_id =%s', (uid,ind_garant,))
			garant_total = cr.fetchone()[0]
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, ind_garant, context)
			data1 = {}
			data1['garant_id'] = garant.id
			data1['garant_total'] = garant_total
			data1['critere1_id'] = ids[0]
			self.pool.get('mcisogem.garant.temp2').create(cr, uid, data1, context)

		cr.execute('DELETE  FROM mcisogem_banquec_temp WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT garant_id FROM mcisogem_garant_temp2 WHERE create_uid = %s', (uid,))
		garant_liste = cr.fetchall()
		for ind_garant in garant_liste:
			cr.execute('SELECT DISTINCT banque_c_id FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s and garant_id =%s', (uid,ind_garant,))
			banque_c_liste = cr.fetchall()
			for ind_banque_c in banque_c_liste:
				cr.execute('SELECT  sum(montant) as total_bank_garant FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s and garant_id =%s and banque_c_id = %s', (uid,ind_garant,ind_banque_c,))
				banque_total = cr.fetchone()[0]
				banque = self.pool.get('mcisogem.banque').browse(cr, uid, ind_banque_c, context)
				data1 = {}
				data1['garant_id'] = ind_garant
				data1['banque_id'] = banque.id
				data1['banque_total'] = banque_total
				data1['critere2_id'] = ids[0]
				self.pool.get('mcisogem.banquec.temp').create(cr, uid, data1, context)


		#######################NEW PARAMETTRES#########################

		cr.execute('DELETE  FROM mcisogem_centre_c_temp WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT centre_id FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s', (uid,))
		centre_liste = cr.fetchall()
		for ind_centre in centre_liste:
			cr.execute('SELECT  sum(montant) as total_centre FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s and centre_id =%s', (uid,ind_centre,))
			centre_total = cr.fetchone()[0]
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, ind_centre, context)
			data1 = {}
			data1['centre_id'] = centre.id
			data1['centre_total'] = centre_total
			data1['critere3_id'] = ids[0]
			self.pool.get('mcisogem.centre.c.temp').create(cr, uid, data1, context)

		cr.execute('DELETE  FROM mcisogem_garant_centre_temp WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT centre_id FROM mcisogem_centre_c_temp WHERE create_uid = %s', (uid,))
		centre_liste = cr.fetchall()
		for ind_centre in centre_liste:
			cr.execute('SELECT DISTINCT garant_id FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s and centre_id =%s', (uid,ind_centre,))
			garant_liste = cr.fetchall()
			for ind_garant in garant_liste:
				cr.execute('SELECT  sum(montant) as total_garant FROM mcisogem_prestation_etat_sinistre_v_temp WHERE create_uid = %s and centre_id =%s and garant_id = %s', (uid,ind_centre,ind_garant,))
				garant_total = cr.fetchone()[0]
				garant = self.pool.get('mcisogem.garant').browse(cr, uid, ind_garant, context)
				data1 = {}
				data1['centre_id'] = ind_centre
				data1['garant_id'] = garant.id
				data1['garant_total'] = garant_total
				data1['critere4_id'] = ids[0]
				self.pool.get('mcisogem.garant.centre.temp').create(cr, uid, data1, context)


		###############################################################


class mcisogem_prestation_etat_sinistre_v_temp(osv.osv):
	_name = 'mcisogem.prestation.etat.sinistre.v.temp'

	_columns = {
		
		'critere_id': fields.many2one('mcisogem.recherche.etat.sinistre.c','critere'),
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		'garant_id' : fields.many2one('mcisogem.garant', 'Garant'),
		'periode_id' : fields.many2one('mcisogem.account.period','Date Comptable'),
		'banque_r_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement'),
		'banque_c_id' : fields.many2one('mcisogem.banque','Banque '), 
		'montant' : fields.integer('Montant'),
		'mode_paiement' : fields.char('Mode de paiement'),
		'num_cheque' : fields.char('Numero de chèque'),

		}

	_rec_name = 'id'



class mcisogem_prestation_etat_sinistre_v(osv.osv):
	_name = 'mcisogem.prestation.etat.sinistre.v'

	_columns = {
		
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		'garant_id' : fields.many2one('mcisogem.garant', 'Garant'),
		'periode_id' : fields.many2one('mcisogem.account.period','Date Comptable'),
		'banque_r_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement'),
		'banque_c_id' : fields.many2one('mcisogem.banque','Banque '), 
		'montant' : fields.integer('Montant'),
		'mode_paiement' : fields.char('Mode de paiement'),
		'ecriture_id' : fields.integer('Eciture comptable'),
		'num_cheque' : fields.char('Numero de chèque'),

		}

	_rec_name = 'id'


class mcisogem_recherche_etat_sinistre_v(osv.osv):
	_name = 'mcisogem.recherche.etat.sinistre.v'

	_columns = {
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		'garant_id' : fields.many2one('mcisogem.garant', 'Garant'),
		'garant_t_id' : fields.one2many('mcisogem.garant.temp2', 'critere1_id'),
		'periode_id' : fields.many2one('mcisogem.account.period','Date Comptable'),
		'banque_r_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement', required=True),
		'banque_c_id' : fields.many2one('mcisogem.banque','Banque '), 
		'banque_c_t_id' : fields.one2many('mcisogem.banquec.temp','critere2_id'), 
		'montant' : fields.integer('Date de valeur'),
		'mode_paiement' : fields.selection([
			('TP', "Tiers Payant"),
			('RD', "Remboursement direct"),
		], 'Mode de paiement'),
		'transfert_id' : fields.one2many('mcisogem.prestation.etat.sinistre.v2.temp','critere_id',' '),
		'recherche' : fields.char('Recherche'),

		}

	_rec_name = 'id'
	_defaults = {
		'recherche': 'Recherche',
	
	}
	def create(self, cr, uid, vals, context=None):
		
		vals['aff_print'] = True
 
		return super(mcisogem_recherche_etat_sinistre_v, self).create(cr,uid,vals,context)

	def print_recherche(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids, [], context=context)
		critere = self.browse(cr, uid, ids[0], context)

		nbr_sinistre = self.pool.get('mcisogem.prestation.etat.sinistre.v2.temp').search_count(cr, uid, [('create_uid', '=', uid)])
		print('****nombre de bene recherche*****')
		print(nbr_sinistre)
		# raise osv.except_osv('Attention' ,'stop!')

		if (nbr_sinistre != 0 ):
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'mcisogem_isa.report_sinistre_v',
					'data': data,
			}
		else:
			raise osv.except_osv('Impossible' ,'aucun élement à imprimer!')

	def button_recherche(self, cr, uid , ids, context=None):

		critere = self.browse(cr, uid, ids[0])
		garant = critere.garant_id.id
		centre = critere.centre_id.id
		periode = critere.periode_id.id
		banque_r = critere.banque_r_id.id
		mode_paiement = critere.mode_paiement



		data = {}
		data['garant_id'] = garant
		data['centre_id'] = centre
		data['periode_id'] = periode
		data['banque_r_id'] = banque_r
		data['mode_paiement'] = mode_paiement
		
		self.pool.get('mcisogem.recherche.etat.sinistre.v').write(cr,uid,ids[0],data,context)
		
		requette = "SELECT id From mcisogem_prestation_etat_sinistre_v2 WHERE "

		if garant == False:
			requette += "1=1 "
		else:
			requette += "garant_id = {} ".format(garant)

		if centre == False:
			requette += "AND 1=1 "
		else : 
			if centre != "":
				requette += "AND centre_id = {} ".format(centre)

		if periode == False:
			requette += "AND 1=1 "
		else : 
			if periode != "":
				requette += "AND periode_id = {} ".format(periode)

		if banque_r == False:
			requette += "AND 1=1 "
		else : 
			if banque_r != "":
				requette += "AND banque_r_id = {} ".format(banque_r)

		if mode_paiement == False:
			requette += "AND 1=1 "
		else : 
			if mode_paiement != "":
				requette += "AND mode_paiement = '{}' ".format(mode_paiement)

		requette += "AND create_uid = '{}' ".format(uid)
			
		
		print('** la requette **')
		print(requette)
		print('** identifiant critere **')
		print(ids[0])
		#raise osv.except_osv('Attention' ,'Oups #TDC!')

		cr.execute('DELETE  FROM mcisogem_prestation_etat_sinistre_v2_temp WHERE create_uid = %s', (uid,))
		########### A
		cr.execute(requette)
		resultat_liste = cr.fetchall()
		print('**Lise des transferts recherchés**')
		print(resultat_liste)
		
		
		for ind_transf in resultat_liste:
			transferts = self.pool.get('mcisogem.prestation.etat.sinistre.v2').browse(cr, uid, ind_transf, context)
			print(transferts.centre_id.name)
			data = {}
			
			data['centre_id'] = transferts.centre_id.id
			data['garant_id'] = transferts.garant_id.id
			data['periode_id'] = transferts.periode_id.id
			data['banque_r_id'] = transferts.banque_r_id.id
			data['banque_c_id'] = transferts.banque_c_id.id
			data['montant'] = transferts.montant
			data['mode_paiement'] = transferts.mode_paiement
			data['critere_id'] = ids[0]

			self.pool.get('mcisogem.prestation.etat.sinistre.v2.temp').create(cr, uid, data, context)

		cr.execute('DELETE  FROM mcisogem_garant_temp2 WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT garant_id FROM mcisogem_prestation_etat_sinistre_v2_temp WHERE create_uid = %s', (uid,))
		garant_liste = cr.fetchall()
		for ind_garant in garant_liste:
			cr.execute('SELECT  sum(montant) as total_garant FROM mcisogem_prestation_etat_sinistre_v2_temp WHERE create_uid = %s and garant_id =%s', (uid,ind_garant,))
			garant_total = cr.fetchone()[0]
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, ind_garant, context)
			data1 = {}
			data1['garant_id'] = garant.id
			data1['garant_total'] = garant_total
			data1['critere1_id'] = ids[0]
			self.pool.get('mcisogem.garant.temp2').create(cr, uid, data1, context)

		cr.execute('DELETE  FROM mcisogem_banquec_temp WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT garant_id FROM mcisogem_garant_temp2 WHERE create_uid = %s', (uid,))
		garant_liste = cr.fetchall()
		for ind_garant in garant_liste:
			cr.execute('SELECT DISTINCT banque_c_id FROM mcisogem_prestation_etat_sinistre_v2_temp WHERE create_uid = %s and garant_id =%s', (uid,ind_garant,))
			banque_c_liste = cr.fetchall()
			for ind_banque_c in banque_c_liste:
				cr.execute('SELECT  sum(montant) as total_bank_garant FROM mcisogem_prestation_etat_sinistre_v2_temp WHERE create_uid = %s and garant_id =%s and banque_c_id = %s', (uid,ind_garant,ind_banque_c,))
				banque_total = cr.fetchone()[0]
				banque = self.pool.get('mcisogem.banque').browse(cr, uid, ind_banque_c, context)
				data1 = {}
				data1['garant_id'] = ind_garant
				data1['banque_id'] = banque.id
				data1['banque_total'] = banque_total
				data1['critere2_id'] = ids[0]
				self.pool.get('mcisogem.banquec.temp').create(cr, uid, data1, context)


class mcisogem_prestation_etat_sinistre_v2_temp(osv.osv):
	_name = 'mcisogem.prestation.etat.sinistre.v2.temp'

	_columns = {
		
		'critere_id': fields.many2one('mcisogem.recherche.etat.sinistre.c','critere'),
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		'garant_id' : fields.many2one('mcisogem.garant', 'Garant'),
		'periode_id' : fields.many2one('mcisogem.account.period','Date Comptable'),
		'banque_r_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement'),
		'banque_c_id' : fields.many2one('mcisogem.banque','Banque '), 
		'montant' : fields.integer('Montant'),
		'mode_paiement' : fields.char('Mode de paiement'),
		'num_cheque' : fields.char('Numero de chèque'),

		}

	_rec_name = 'id'

class mcisogem_prestation_etat_sinistre_v2(osv.osv):
	_name = 'mcisogem.prestation.etat.sinistre.v2'

	_columns = {
		
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		'garant_id' : fields.many2one('mcisogem.garant', 'Garant'),
		'periode_id' : fields.many2one('mcisogem.account.period','Date Comptable'),
		'banque_r_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement'),
		'banque_c_id' : fields.many2one('mcisogem.banque','Banque '), 
		'montant' : fields.integer('Montant'),
		'mode_paiement' : fields.char('Mode de paiement'),
		'ecriture_id' : fields.integer('Eciture comptable'),
		'num_cheque' : fields.char('Numero de chèque'),

		}

	_rec_name = 'id'




class mcisogem_prestation_recherche_temp(osv.osv):
	_name = 'mcisogem.prestation.recherche.temp'

	def _compute_total(self):
	    for record in self:
	        record.nbre_chek = sum(line.value for line in record.result_ids)

	def _get_default_pet_ids(self, cr, uid, context=None):
	    return self.pool.get('mcisogem.prestation.recherche.result').search(cr, uid, [])

	def test(self,cr,uid,context):
		d = {}
		critere = []
		critere.append(('create_id' , '=' , uid))
		d = {'result_ids' : critere}
		return {'domain':d}

	def onchange_banque(self,cr,uid,context,banque_id):
		if banque_id:
			v = {}
			rech_ids = self.pool.get('mcisogem.banque.reglement').search(cr,uid,[('id' , '=' , banque_id)])
			banque_data = self.pool.get('mcisogem.banque.reglement').browse(cr,uid,rech_ids)
			v={'cod_journal':banque_data.code_journal,'treso':banque_data.compte_treso}
			return {'value':v}

	# def _get_utilisateur(self, cr,uid,context):		
	# 	return uid

	_columns = {
		'num_chek_debut': fields.integer('N° du 1er chèque', required=True),
		'num_chek_fin': fields.integer('Au', required=True),
		'banque_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement', required=True),
		'cod_journal': fields.char('Code journal'),
		'treso': fields.char('Compte de trésorerie'),
		'nbre_chek': fields.integer('Nombre de chèque'),
		'utilisateur': fields.integer(''),
		'result_ids':fields.many2many('mcisogem.prestation.recherche.result',
									   'mcisogem_prestation_recherche_result_rel',
										'mcisogem_prestation_id',
										'cod_prestation', 'Prestations', required=False)
		}

	_rec_name = 'id'

	_defaults = {
	    'result_ids': _get_default_pet_ids,
	    # 'utilisateur': _get_utilisateur
	}

	def create(self, cr, uid, data, context=None):

		temp_table = self.pool.get('mcisogem.prestation.recherche.result').search(cr,uid,[('create_uid','=',uid)])
		temp_ids = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,temp_table)
		num_chek_debut = data['num_chek_debut']
		num_chek_fin = data['num_chek_fin']

		for prest in temp_ids:
			if num_chek_fin < num_chek_debut:
				raise osv.except_osv('Attention !' , 'Le numéro de début de chèque doit être inférieur a celui de fin.')

			if num_chek_debut <= num_chek_fin:
				cr.execute("update mcisogem_prestation_recherche_result set num_cheque = %s, state =%s where centre_id = %s" , (num_chek_debut, "P",prest.centre_id.id))
				num_chek_debut += 1

		debut = data['num_chek_debut']
		fin = data['num_chek_fin']
		rech_ids = self.pool.get('mcisogem.banque.reglement').search(cr,uid,[('id' , '=' , data['banque_id'])])
		banque_data = self.pool.get('mcisogem.banque.reglement').browse(cr,uid,rech_ids)
		cod = banque_data.code_journal
		treso = banque_data.compte_treso
		for prest in temp_ids:
			vals = {}

			if debut <= fin:
				vals['type_ecriture'] = "PAIEMENT"
				vals['num_piece_reglmt'] = debut
				vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
				vals['code_journal'] = cod
				p_table = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',time.strftime("%m/%Y", time.localtime()))])
				p_ids = self.pool.get('mcisogem.account.period').browse(cr,uid,p_table)
				vals['periode_id'] = p_ids.id
				vals['banque_int'] = prest.garant_id.cpt_tp2
				vals['libelle_reglemt'] = "PCH:" + str(debut) + " " + prest.centre_id.name
				vals['sens'] = "C"
				vals['montant'] = prest.montant_total
				vals['compte_gle'] = treso
				vals['mode_paiement'] = "TP"
				vals['state'] = "V"

				ecri_id = self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)
				# self.pool.get('mcisogem.prestation').write(cr, uid, prest.id, {'ecriture_id': ecri_id} , context=context)
				cr.execute("select prest_id from mcisogem_prest_temp where centre_id = %s",(prest.centre_id.id,) )
				presta = cr.fetchall()
				print(presta)

				for ind_presta in presta:
					self.pool.get('mcisogem.prestation').write(cr, uid, ind_presta, {'ecriture_id': ecri_id} , context=context)
				
				vals = {}

				vals['type_ecriture'] = "PAIEMENT"
				vals['num_piece_reglmt'] = debut
				vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
				vals['code_journal'] = cod
				vals['periode_id'] = p_ids.id
				vals['banque_int'] = prest.garant_id.cpt_tp2
				vals['libelle_reglemt'] = "PCH:" + str(debut) + " " + prest.centre_id.name
				vals['montant'] = prest.montant_total
				vals['sens'] = "D"
				vals['compte_gle'] = prest.compte_gle_prestataire
				vals['compte_tiers'] = prest.compte_tiers_prestataire
				vals['mode_paiement'] = "TP"
				vals['state'] = "V"

				self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)
				debut += 1
			
		cr.execute("select * from mcisogem_prest_temp where create_uid=%s", (uid,))
		lesprestats = cr.dictfetchall()
		for pres in lesprestats:
			self.pool.get('mcisogem.prestation').write(cr, uid, pres['prest_id'], {'state':'P' , 'date_reglement' : time.strftime("%Y-%m-%d")} , context=context)
		data['cod_journal'] = cod
		data['treso'] = treso

		# CODE RAJOUTE DANS LE CREATE

		ind_resultat = self.pool.get('mcisogem.prestation.recherche.result').search(cr,uid,[('create_uid','=',uid)])
		result = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,ind_resultat)

		print('*****result_ids******')
		print(result)
		
		for prest in result:

			data1 = {}

			data1['centre_id'] = prest.centre_id.id
			data1['garant_id'] = prest.garant_id.id
			p_table = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',time.strftime("%m/%Y", time.localtime()))])
			p_ids = self.pool.get('mcisogem.account.period').browse(cr,uid,p_table)
			data1['periode_id'] = p_ids.id
			data1['banque_r_id'] = data['banque_id']
			data1['banque_c_id'] = prest.centre_id.banque_id.id
			data1['montant'] = prest.montant_total
			data1['mode_paiement'] = prest.mode_paiement
			data1['ecriture_id'] = ecri_id

			self.pool.get('mcisogem.prestation.etat.sinistre.v').create(cr, uid, data1, context)

		return super(mcisogem_prestation_recherche_temp , self).create(cr, uid, data, context=context)



class mcisogem_prestation_recherche_virement_temp(osv.osv):
	_name = 'mcisogem.prestation.recherche.virement.temp'

	def _compute_total(self):
	    for record in self:
	        record.nbre_chek = sum(line.value for line in record.result_ids)

	def _get_default_pet_ids(self, cr, uid, context=None):
	    return self.pool.get('mcisogem.prestation.recherche.result').search(cr, uid, [])

	def test(self,cr,uid,context):
		d = {}
		critere = []
		critere.append(('create_id' , '=' , uid))
		d = {'result_ids' : critere}
		return {'domain':d}

	def onchange_banque(self,cr,uid,context,banque_id):
		if banque_id:
			v = {}
			rech_ids = self.pool.get('mcisogem.banque.reglement').search(cr,uid,[('id' , '=' , banque_id)])
			banque_data = self.pool.get('mcisogem.banque.reglement').browse(cr,uid,rech_ids)
			v={'cod_journal':banque_data.code_journal,'treso':banque_data.compte_treso}
			return {'value':v}

	# def _get_utilisateur(self, cr,uid,context):		
	# 	return uid

	_columns = {
		'banque_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement', required=True),
		'cod_journal': fields.char('Code journal'),
		'treso': fields.char('Compte de trésorerie'),
		'nbre_chek': fields.integer('Nombre de chèque'),
		'utilisateur': fields.integer(''),
		'result_ids':fields.many2many('mcisogem.prestation.recherche.result',
									   'mcisogem_prestation_recherche_result_rel1',
										'mcisogem_prestation_id',
										'cod_prestation', 'Prestations', required=False)
		}

	_rec_name = 'id'

	_defaults = {
	    'result_ids': _get_default_pet_ids,
	    # 'utilisateur': _get_utilisateur
	}

	def create(self, cr, uid, data, context=None):

		temp_table = self.pool.get('mcisogem.prestation.recherche.result').search(cr,uid,[('create_uid','=',uid)])
		temp_ids = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,temp_table)
		
		rech_ids = self.pool.get('mcisogem.banque.reglement').search(cr,uid,[('id' , '=' , data['banque_id'])])
		banque_data = self.pool.get('mcisogem.banque.reglement').browse(cr,uid,rech_ids)
		cod = banque_data.code_journal
		treso = banque_data.compte_treso
		for prest in temp_ids:
			# cr.execute("select distinct num_piece_reglmt from mcisogem_ecriture_comptable order by num_piece_reglmt asc limit 1", )
			# piece = cr.fetchone()[0]
			piece_ids = self.pool.get('mcisogem.ecriture.comptable').search(cr,uid,[('id' , '!=' , 0)], limit = 1 , order='id asc')
			piece = self.pool.get('mcisogem.ecriture.comptable').browse(cr, uid, piece_ids, context).num_piece_reglmt
			print('** affiche piece**')
			print(piece)
			# print(piece[0])
			if (piece):
				# int(piece) += 1 
				# piece_new = str(piece)
				piece_new = str(int(piece) + 1)
			else:
				piece_new = 1

			vals = {}

			
			vals['type_ecriture'] = "PAIEMENT"
			vals['num_piece_reglmt'] = piece_new
			vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
			vals['code_journal'] = cod
			p_table = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',time.strftime("%m/%Y", time.localtime()))])
			p_ids = self.pool.get('mcisogem.account.period').browse(cr,uid,p_table)
			vals['periode_id'] = p_ids.id
			vals['banque_int'] = prest.garant_id.cpt_tp2
			vals['libelle_reglemt'] = "PCH:" + str(piece_new) + " " + prest.centre_id.name
			vals['sens'] = "C"
			vals['montant'] = prest.montant_total
			vals['compte_gle'] = treso
			vals['mode_paiement'] = "TP"
			vals['state'] = "V"

			ecri_id = self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)

			print('ecriture comptable')
			print(ecri_id)
			print(prest.id)

			# presta_ids = self.pool.get('mcisogem.prest.temp').search(cr, uid, [('centre_id', '=', prest.centre_id.id)])
			# presta = self.pool.get('mcisogem.prest.temp').browse(cr, uid, presta_ids, context).prest_id

			cr.execute("select prest_id from mcisogem_prest_temp where centre_id = %s",(prest.centre_id.id,) )
			presta = cr.fetchall()
			print(presta)

			for ind_presta in presta:
				self.pool.get('mcisogem.prestation').write(cr, uid, ind_presta, {'ecriture_id': ecri_id} , context=context)
			
			vals = {}

			vals['type_ecriture'] = "PAIEMENT"
			vals['num_piece_reglmt'] = piece_new
			vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
			vals['code_journal'] = cod
			vals['periode_id'] = p_ids.id
			vals['banque_int'] = prest.garant_id.cpt_tp2
			vals['libelle_reglemt'] = "PCH:" + str(piece_new) + " " + prest.centre_id.name
			vals['montant'] = prest.montant_total
			vals['sens'] = "D"
			vals['compte_gle'] = prest.compte_gle_prestataire
			vals['compte_tiers'] = prest.compte_tiers_prestataire
			vals['mode_paiement'] = "TP"
			vals['state'] = "V"

			self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)
			
		cr.execute("select * from mcisogem_prest_temp where create_uid=%s", (uid,))
		lesprestats = cr.dictfetchall()
		for pres in lesprestats:
			self.pool.get('mcisogem.prestation').write(cr, uid, pres['prest_id'], {'state':'P' , 'date_reglement' : time.strftime("%Y-%m-%d")} , context=context)
		data['cod_journal'] = cod
		data['treso'] = treso

		# # CODE RAJOUTE DANS LE CREATE

		ind_resultat = self.pool.get('mcisogem.prestation.recherche.result').search(cr,uid,[('create_uid','=',uid)])
		result = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,ind_resultat)

		print('*****result_ids******')
		print(result)
		
		for prest in result:

			data1 = {}

			data1['centre_id'] = prest.centre_id.id
			data1['garant_id'] = prest.garant_id.id
			p_table = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',time.strftime("%m/%Y", time.localtime()))])
			p_ids = self.pool.get('mcisogem.account.period').browse(cr,uid,p_table)
			data1['periode_id'] = p_ids.id
			data1['banque_r_id'] = data['banque_id']
			data1['banque_c_id'] = prest.centre_id.banque_id.id
			data1['montant'] = prest.montant_total
			data1['mode_paiement'] = prest.mode_paiement
			data1['ecriture_id'] = ecri_id

			self.pool.get('mcisogem.prestation.etat.sinistre.v2').create(cr, uid, data1, context)

		return super(mcisogem_prestation_recherche_virement_temp , self).create(cr, uid, data, context=context)


class mcisogem_prestation_recherche_result(osv.osv):
	_name = 'mcisogem.prestation.recherche.result'

	_columns = {
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		'garant_id' : fields.many2one('mcisogem.garant', 'Garant'),
		'beneficiaire_id' : fields.many2one('mcisogem.benef' , 'Bénéficiaire'),
		'cod_prestation':fields.many2one('mcisogem.prestation.temp', 'name', 'Prestations'), 
		'montant_exclus' : fields.integer('Montant total exclus', digits=(18, 0), readonly=True),
		'montant_total' : fields.integer('Montant total de règlement', digits=(18, 0), readonly=True),

		'periode_id' : fields.many2one('mcisogem.account.period', 'Date comptable'),
   
		'nbre_prestat' : fields.integer('Nombre de prestation'),

		'num_cheque' : fields.char('N° chèque'),

		'banque_id': fields.many2one('mcisogem.banque.reglement', 'Banque'),
		'code_journal': fields.char('Code journal'),
		'banque_int': fields.char('Code banque interne'),

		'compte_tiers_prestataire': fields.char('Compte tiers'),
		'compte_gle_prestataire': fields.char('Compte général'),

		'state': fields.selection([
			('SP', "Sinistre provisoire"),
			('V', "Validation des saisies"),
			('CRL', "Création des règlements"),
			('CRE', "Création des remboursements"),
			('VD', "Validation direction"),
			('VC', "Validation comptable"),
			('VF', "Validé"),
			('P', "Payé"),
		], 'Statut', readonly=True),
		'num_fact' : fields.char('N° de Facture'),
		'mode_paiement' : fields.selection([
			('TP', "Tiers Payant"),
			('RD', "Remboursement direct"),
		], 'Mode de paiement')
	}
	_rec_name = "garant_id"

# class mcisogem_prestation_recherche_result_a_valider_temp(osv.osv):
# 	_name = 'mcisogem.prestation.recherche.result.a.valider.temp'

# 	def button_to_valid(self, cr, uid, ids, context=None):
# 		result = self.browse(cr, uid, ids[0], context=context).id
# 		result_table = self.search(cr, uid, [('id', '=', result)])
# 		result_data = self.browse(cr, uid, result_table)
		
# 		ctx = (context or {}).copy()
# 		ctx['id'] = result
# 		ctx['result_prestations_ids'] = result_data.result_prestations_ids
# 		ctx['form_view_ref'] = 'view_mcisogem_validation_paiement_form'
		
# 		return {
# 		  'name':'Validation',
# 		  'view_type':'form',
# 		  'view_mode':'form',
# 		  'res_model':'mcisogem.prestation.recherche.result',
# 		  'view_id':False,
# 		  'target':'current',
# 		  'type':'ir.actions.act_window',
# 		  'domain':[('create_uid', '=', uid)],
# 		  'context':ctx,
# 		}

# 	_columns = {
# 		'nbre_ligne': fields.integer('Nombre de ligne'),
# 		'montant_total': fields.integer('Montant total'),
# 		'result_prestations_ids' : fields.one2many('mcisogem.prestation.recherche.result','result_id','Prestataires à payer', domain="[('create_uid', '=', uid)]")
# 	}




############## NEW REGLEMENT BANK ##############

class mcisogem_prestation_recherche_cheque_temp(osv.osv):
	_name = 'mcisogem.prestation.recherche.cheque.temp'

	def _compute_total(self):
	    for record in self:
	        record.nbre_chek = sum(line.value for line in record.result_ids)

	def _get_default_pet_ids(self, cr, uid, context=None):
	    return self.pool.get('mcisogem.prestation.recherche.result').search(cr, uid, [])

	def test(self,cr,uid,context):
		d = {}
		critere = []
		critere.append(('create_id' , '=' , uid))
		d = {'result_ids' : critere}
		return {'domain':d}

	def onchange_banque(self,cr,uid,context,banque_id):
		if banque_id:
			v = {}
			rech_ids = self.pool.get('mcisogem.banque.reglement').search(cr,uid,[('id' , '=' , banque_id)])
			banque_data = self.pool.get('mcisogem.banque.reglement').browse(cr,uid,rech_ids)
			v={'cod_journal':banque_data.code_journal,'treso':banque_data.compte_treso}
			return {'value':v}

	# def _get_utilisateur(self, cr,uid,context):		
	# 	return uid

	_columns = {
		'num_chek_debut': fields.integer('N° du 1er chèque', required=True),
		'num_chek_fin': fields.integer('Au'),
		'banque_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement', required=True),
		'cod_journal': fields.char('Code journal'),
		'treso': fields.char('Compte de trésorerie'),
		'nbre_chek': fields.integer('Nombre de chèque'),
		'utilisateur': fields.integer(''),
		'mode_paiement': fields.many2one('mcisogem.regime', 'Type de remboursement', domain=[('code_regime', 'in', ['TP', 'RD'])], required=True),
		'centre_ids' : fields.many2many('mcisogem.centre' , 'regl_centre_rel5' , 'id_g' , 'id_c' , 'Centres'),
		'date_reglement' : fields.date('Date validation règlement'),
		'date_remboursement' : fields.date('Date validation remboursement'),
		'medecin_ids' : fields.many2many('mcisogem.praticien' , 'regl_prat_rel5' , 'id_g' , 'id_m' , 'Prescripteurs'),
		'num_fact': fields.integer('N° Facture'),
		'garant_ids' : fields.many2many('mcisogem.garant' , 'regl_garant_rel5' , 'id_g' , 'id_v' , 'Garants'),
		'periode_ids' : fields.many2many('mcisogem.account.period', 'regl_period_rel5' , 'id_g' , 'id_p' , 'Date Comptable'),
		'result_ids':fields.many2many('mcisogem.prestation.recherche.result',
									   'mcisogem_prestation_recherche_result_rel5',
										'mcisogem_prestation_id',
										'cod_prestation', 'Prestations', required=False)
		}

	_rec_name = 'id'

	_defaults = {
	    # 'result_ids': _get_default_pet_ids,
	    # 'utilisateur': _get_utilisateur
	}
	def _needaction_count(self , cr, uid,ids, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "RESPONSABLE COMPTABLE" or group_obj.name == "UTILISATEUR COMPTABLE":
					return self.pool.get('mcisogem.prestation.recherche.result').search_count(cr,uid,[('state' , 'in' , ['VF'])])

	def onchange_pram(self, cr, uid, ids, mode_paiement,centre_ids,garant_ids,periode_ids,num_fact, context=None):        
		d = {}
		critere = []
		centres = centre_ids[0][2]
		garants = garant_ids[0][2]
		periodes = periode_ids[0][2]
		critere.append(('state' , '=' , 'VF'))

		# if mode_paiement:

		# 	critere.append(('mode_paiement' , '=' , mode_paiement))


		if len(centres)>0:
			
			critere.append(('centre_id' , '=' , centres))

		if num_fact:
			critere.append(('num_fact' , '=' , num_fact))

		if len(garants)>0:
			
			critere.append(('garant_id' , 'in' , garants))

		if len(periodes)>0:
			
			critere.append(('periode_id' , 'in' , periodes))

		d = {'result_ids' : critere}
			
		return {'domain' : d}

	def create(self, cr, uid, data, context=None):

		temp_table = self.pool.get('mcisogem.prestation.recherche.result').search(cr,uid,[('create_uid','=',uid)])
		temp_ids = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,temp_table)
		num_chek_debut = data['num_chek_debut']
		num_chek_fin = data['num_chek_fin']

		# for prest in temp_ids:
		for prest in data['result_ids'][0][2]:

			if num_chek_fin < num_chek_debut:
				raise osv.except_osv('Attention !' , 'Le numéro de début de chèque doit être inférieur a celui de fin.')

			if num_chek_debut <= num_chek_fin:
				regroupement_data = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,prest)
				cr.execute("update mcisogem_prestation_recherche_result set num_cheque = %s, state =%s where centre_id = %s" , (num_chek_debut, "P",regroupement_data.centre_id.id))
				num_chek_debut += 1

		debut = data['num_chek_debut']
		fin = data['num_chek_fin']
		rech_ids = self.pool.get('mcisogem.banque.reglement').search(cr,uid,[('id' , '=' , data['banque_id'])])
		banque_data = self.pool.get('mcisogem.banque.reglement').browse(cr,uid,rech_ids)
		cod = banque_data.code_journal
		treso = banque_data.compte_treso
		# for prest in temp_ids:
		for prest in data['result_ids'][0][2]:
			regroupement_data = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,prest)
			vals = {}

			if debut <= fin:
				vals['type_ecriture'] = "PAIEMENT"
				vals['num_piece_reglmt'] = debut
				vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
				vals['code_journal'] = cod
				p_table = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',time.strftime("%m/%Y", time.localtime()))])
				p_ids = self.pool.get('mcisogem.account.period').browse(cr,uid,p_table)
				vals['periode_id'] = p_ids.id
				vals['banque_int'] = regroupement_data.garant_id.cpt_tp2
				vals['libelle_reglemt'] = "PCH:" + str(debut) + " " + regroupement_data.centre_id.name
				vals['sens'] = "C"
				vals['montant'] = regroupement_data.montant_total
				vals['compte_gle'] = treso
				vals['mode_paiement'] = "TP"
				vals['state'] = "V"

				ecri_id = self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)

				# A REVOIR !!!!!!!!!!!!!
				#self.pool.get('mcisogem.prestation.recherche.result').write(cr, uid, prest.id, {'state':'P','num_cheque':} , context=context)

				# self.pool.get('mcisogem.prestation').write(cr, uid, prest.id, {'ecriture_id': ecri_id} , context=context)
				cr.execute("select prest_id from mcisogem_prest_temp where centre_id = %s",(regroupement_data.centre_id.id,) )
				presta = cr.fetchall()
				print(presta)

				for ind_presta in presta:
					self.pool.get('mcisogem.prestation').write(cr, uid, ind_presta, {'ecriture_id': ecri_id} , context=context)
				
				vals = {}

				vals['type_ecriture'] = "PAIEMENT"
				vals['num_piece_reglmt'] = debut
				vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
				vals['code_journal'] = cod
				vals['periode_id'] = p_ids.id
				vals['banque_int'] = regroupement_data.garant_id.cpt_tp2
				vals['libelle_reglemt'] = "PCH:" + str(debut) + " " + regroupement_data.centre_id.name
				vals['montant'] = regroupement_data.montant_total
				vals['sens'] = "D"
				vals['compte_gle'] = regroupement_data.compte_gle_prestataire
				vals['compte_tiers'] = regroupement_data.compte_tiers_prestataire
				vals['mode_paiement'] = "TP"
				vals['state'] = "V"

				self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)
				debut += 1
			
		cr.execute("select * from mcisogem_prest_temp where create_uid=%s", (uid,))
		lesprestats = cr.dictfetchall()
		for pres in lesprestats:
			self.pool.get('mcisogem.prestation').write(cr, uid, pres['prest_id'], {'state':'P' , 'date_reglement' : time.strftime("%Y-%m-%d")} , context=context)
		data['cod_journal'] = cod
		data['treso'] = treso

		# for prest in data['result_ids'][0][2]:
		# 	self.pool.get('mcisogem.prestation.recherche.result').write(cr, uid, prest.id, {'state':'P'} , context=context)

		# CODE RAJOUTE DANS LE CREATE

		ind_resultat = self.pool.get('mcisogem.prestation.recherche.result').search(cr,uid,[('create_uid','=',uid)])
		result = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,ind_resultat)

		print('*****result_ids******')
		print(result)

		result = data['result_ids'][0][2]
		
		for prest in result:
			regroupement_data = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,prest)

			data1 = {}

			data1['centre_id'] = regroupement_data.centre_id.id
			data1['garant_id'] = regroupement_data.garant_id.id
			p_table = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',time.strftime("%m/%Y", time.localtime()))])
			p_ids = self.pool.get('mcisogem.account.period').browse(cr,uid,p_table)
			data1['periode_id'] = p_ids.id
			data1['banque_r_id'] = data['banque_id']
			data1['banque_c_id'] = regroupement_data.centre_id.banque_id.id
			data1['montant'] = regroupement_data.montant_total
			data1['mode_paiement'] = 'TP'
			data1['ecriture_id'] = ecri_id
			data1['num_cheque'] = regroupement_data.num_cheque

			self.pool.get('mcisogem.prestation.etat.sinistre.v').create(cr, uid, data1, context)

		return super(mcisogem_prestation_recherche_cheque_temp , self).create(cr, uid, data, context=context)



class mcisogem_prestation_recherche_vire_temp(osv.osv):
	_name = 'mcisogem.prestation.recherche.vire.temp'

	def _compute_total(self):
	    for record in self:
	        record.nbre_chek = sum(line.value for line in record.result_ids)

	def _get_default_pet_ids(self, cr, uid, context=None):
	    return self.pool.get('mcisogem.prestation.recherche.result').search(cr, uid, [])

	def test(self,cr,uid,context):
		d = {}
		critere = []
		critere.append(('create_id' , '=' , uid))
		d = {'result_ids' : critere}
		return {'domain':d}

	def onchange_banque(self,cr,uid,context,banque_id):
		if banque_id:
			v = {}
			rech_ids = self.pool.get('mcisogem.banque.reglement').search(cr,uid,[('id' , '=' , banque_id)])
			banque_data = self.pool.get('mcisogem.banque.reglement').browse(cr,uid,rech_ids)
			v={'cod_journal':banque_data.code_journal,'treso':banque_data.compte_treso}
			return {'value':v}

	# def _get_utilisateur(self, cr,uid,context):		
	# 	return uid

	_columns = {
		'banque_id' : fields.many2one('mcisogem.banque.reglement','Banque de règlement', required=True),
		'cod_journal': fields.char('Code journal'),
		'treso': fields.char('Compte de trésorerie'),
		'nbre_chek': fields.integer('Nombre de chèque'),
		'utilisateur': fields.integer(''),
		'mode_paiement': fields.many2one('mcisogem.regime', 'Type de remboursement', domain=[('code_regime', 'in', ['TP', 'RD'])], required=True),
		'centre_ids' : fields.many2many('mcisogem.centre' , 'regl_centre_rel6' , 'id_g' , 'id_c' , 'Centres'),
		'date_reglement' : fields.date('Date validation règlement'),
		'date_remboursement' : fields.date('Date validation remboursement'),
		'medecin_ids' : fields.many2many('mcisogem.praticien' , 'regl_prat_rel4' , 'id_g' , 'id_m' , 'Prescripteurs'),
		'num_fact': fields.integer('N° Facture'),
		'garant_ids' : fields.many2many('mcisogem.garant' , 'regl_garant_rel4' , 'id_g' , 'id_v' , 'Garants'),
		'periode_ids' : fields.many2many('mcisogem.account.period', 'regl_period_rel4' , 'id_g' , 'id_p' , 'Date Comptable'),
		'result_ids':fields.many2many('mcisogem.prestation.recherche.result',
									   'mcisogem_prestation_recherche_result_rel4',
										'mcisogem_prestation_id',
										'cod_prestation', 'Prestations', required=False)
		}

	_rec_name = 'id'

	_defaults = {
	    # 'result_ids': _get_default_pet_ids,
	    # 'utilisateur': _get_utilisateur
	}

	def _needaction_count(self , cr, uid,ids, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "RESPONSABLE COMPTABLE" or group_obj.name == "UTILISATEUR COMPTABLE":
					return self.pool.get('mcisogem.prestation.recherche.result').search_count(cr,uid,[('state' , 'in' , ['VF'])])



	def onchange_pram(self, cr, uid, ids, mode_paiement,centre_ids,garant_ids,periode_ids,num_fact, context=None):        
		d = {}
		critere = []
		centres = centre_ids[0][2]
		garants = garant_ids[0][2]
		periodes = periode_ids[0][2]
		critere.append(('state' , '=' , 'VF'))

		# if mode_paiement:

		# 	critere.append(('mode_paiement' , '=' , mode_paiement))


		if len(centres)>0:
			
			critere.append(('centre_id' , '=' , centres))

		if num_fact:
			critere.append(('num_fact' , '=' , num_fact))

		if len(garants)>0:
			
			critere.append(('garant_id' , 'in' , garants))

		if len(periodes)>0:
			
			critere.append(('periode_id' , 'in' , periodes))

		d = {'result_ids' : critere}
			
		return {'domain' : d}

	def create(self, cr, uid, data, context=None):

		temp_table = self.pool.get('mcisogem.prestation.recherche.result').search(cr,uid,[('create_uid','=',uid)])
		temp_ids = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,temp_table)
		
		rech_ids = self.pool.get('mcisogem.banque.reglement').search(cr,uid,[('id' , '=' , data['banque_id'])])
		banque_data = self.pool.get('mcisogem.banque.reglement').browse(cr,uid,rech_ids)
		cod = banque_data.code_journal
		treso = banque_data.compte_treso
		for prest in data['result_ids'][0][2]:
			regroupement_data = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,prest)
		# for prest in temp_ids:
			# cr.execute("select distinct num_piece_reglmt from mcisogem_ecriture_comptable order by num_piece_reglmt asc limit 1", )
			# piece = cr.fetchone()[0]
			piece_ids = self.pool.get('mcisogem.ecriture.comptable').search(cr,uid,[('id' , '!=' , 0)], limit = 1 , order='id asc')
			piece = self.pool.get('mcisogem.ecriture.comptable').browse(cr, uid, piece_ids, context).num_piece_reglmt
			print('** affiche piece**')
			print(piece)
			# print(piece[0])
			if (piece):
				# int(piece) += 1 
				# piece_new = str(piece)
				piece_new = str(int(piece) + 1)
			else:
				piece_new = 1

			vals = {}

			
			vals['type_ecriture'] = "PAIEMENT"
			vals['num_piece_reglmt'] = piece_new
			vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
			vals['code_journal'] = cod
			p_table = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',time.strftime("%m/%Y", time.localtime()))])
			p_ids = self.pool.get('mcisogem.account.period').browse(cr,uid,p_table)
			vals['periode_id'] = p_ids.id
			vals['banque_int'] = regroupement_data.garant_id.cpt_tp2
			vals['libelle_reglemt'] = "PCH:" + str(piece_new) + " " + regroupement_data.centre_id.name
			vals['sens'] = "C"
			vals['montant'] = regroupement_data.montant_total
			vals['compte_gle'] = treso
			vals['mode_paiement'] = "TP"
			vals['state'] = "V"

			ecri_id = self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)

			print('ecriture comptable')
			print(ecri_id)
			print(regroupement_data.id)

			# presta_ids = self.pool.get('mcisogem.prest.temp').search(cr, uid, [('centre_id', '=', prest.centre_id.id)])
			# presta = self.pool.get('mcisogem.prest.temp').browse(cr, uid, presta_ids, context).prest_id

			cr.execute("select prest_id from mcisogem_prest_temp where centre_id = %s",(regroupement_data.centre_id.id,) )
			presta = cr.fetchall()
			print(presta)

			for ind_presta in presta:
				self.pool.get('mcisogem.prestation').write(cr, uid, ind_presta, {'ecriture_id': ecri_id} , context=context)
			
			vals = {}

			vals['type_ecriture'] = "PAIEMENT"
			vals['num_piece_reglmt'] = piece_new
			vals['date_ecriture'] = time.strftime("%Y-%m-%d", time.localtime())
			vals['code_journal'] = cod
			vals['periode_id'] = p_ids.id
			vals['banque_int'] = regroupement_data.garant_id.cpt_tp2
			vals['libelle_reglemt'] = "PCH:" + str(piece_new) + " " + regroupement_data.centre_id.name
			vals['montant'] = regroupement_data.montant_total
			vals['sens'] = "D"
			vals['compte_gle'] = regroupement_data.compte_gle_prestataire
			vals['compte_tiers'] = regroupement_data.compte_tiers_prestataire
			vals['mode_paiement'] = "TP"
			vals['state'] = "V"

			self.pool.get('mcisogem.ecriture.comptable').create(cr, uid, vals, context)
			
		cr.execute("select * from mcisogem_prest_temp where create_uid=%s", (uid,))
		lesprestats = cr.dictfetchall()
		for pres in lesprestats:
			self.pool.get('mcisogem.prestation').write(cr, uid, pres['prest_id'], {'state':'P' , 'date_reglement' : time.strftime("%Y-%m-%d")} , context=context)
		data['cod_journal'] = cod
		data['treso'] = treso

		for prest in data['result_ids'][0][2]:
			self.pool.get('mcisogem.prestation.recherche.result').write(cr, uid, prest, {'state':'P'} , context=context)

		# # CODE RAJOUTE DANS LE CREATE

		ind_resultat = self.pool.get('mcisogem.prestation.recherche.result').search(cr,uid,[('create_uid','=',uid)])
		result = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,ind_resultat)

		print('*****result_ids******')
		# print(result)
		result = data['result_ids'][0][2]

		
		
		for prest in result:
			print('*****HERE******')
			regroupement_data = self.pool.get('mcisogem.prestation.recherche.result').browse(cr,uid,prest)
			

			data1 = {}

			data1['centre_id'] = regroupement_data.centre_id.id
			data1['garant_id'] = regroupement_data.garant_id.id
			p_table = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',time.strftime("%m/%Y", time.localtime()))])
			p_ids = self.pool.get('mcisogem.account.period').browse(cr,uid,p_table)
			data1['periode_id'] = p_ids.id
			data1['banque_r_id'] = data['banque_id']
			data1['banque_c_id'] = regroupement_data.centre_id.banque_id.id
			data1['montant'] = regroupement_data.montant_total
			data1['mode_paiement'] = 'TP'
			data1['ecriture_id'] = ecri_id
			

			self.pool.get('mcisogem.prestation.etat.sinistre.v2').create(cr, uid, data1, context)


		return super(mcisogem_prestation_recherche_vire_temp , self).create(cr, uid, data, context=context)


