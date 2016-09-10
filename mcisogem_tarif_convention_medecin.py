# -*- coding:utf8 -*-
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



class mcisogem_tarif_convention_medecin(osv.osv):
	_name = "mcisogem.tarif.convention.medecin"
	_description = 'Tarif convention medecin'

	def _get_medecin_ids(self, cr, ids, code_centre, arg, context=None):
		res = {}
		if not code_centre:
			return False
		else:
		# Recuperation des medecins
			pratic_obj = self.pool.get('mcisogem.praticien')
			medecin_ids = self.search(cr, uid , 'mcisogem.agr.prestat', [('code_centre', '=', code_centre)])
			for record in self.pool.get('mcisogem.agr.prestat').browse(cr, uid, medecin_ids, context=context):
				pratic_ids = []
				praticien = pratic_obj.browse(cr, uid, pratic_obj.search(cr, uid, [('id', '=', record.praticien_rel_id)]), context=context)
				if praticien:
					praticien_ids = pratic_obj.search(cr, uid, [('id', '=', [praticien[0].id])])
					for b in pratic_obj.browse(cr, uid, praticien_ids, context=context):
						pratic_ids.append(b.libelle_court_prestat)
				res[r.id] = pratic_ids
			return res

	_columns = {
		'code_centre': fields.many2one('mcisogem.centre', "Centre", required=True),
		'code_medecin_id': fields.many2one('mcisogem.medecin.temp', "Medecin", required=True),
		'code_medecin': fields.char(''),
		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", ),
		'montant_brut_tarif': fields.integer('Montant brut tarif', ),
		'plafond_tarif': fields.integer('Plafond', ),
		'affichage' : fields.integer('affichage', required=False),
		'code_tarif_convention_medecin_temp': fields.many2many('mcisogem.tarif.convention.medecin.temp',
									   'mcisogem_convention_medecin_temp_rel',
										'convention_medecin_temp_id',
										'code_convention_medecin',
										'Choix des actes', required=False),
		'date_effet_tarif': fields.date("Date d'effet", required=True),
		'date_resiliation_tarif': fields.date("Date de résiliation"),
		'code_langue': fields.char('code_langue', size=10),
		'code_gest': fields.many2one('mcisogem.centre.gestion', "Centre de gestion"),
		'code_sup' : fields.char('cod_sup', size=1),
		'ident_centre': fields.char('Centre de gestion'),

	}
	_defaults = {
		'date_resiliation_tarif': '1900-01-01',
		'affichage': 0
	}

	_rec_name = 'code_medecin_id'

	_sql_constraints = [('unique_tarif', 'unique(code_acte,code_centre,code_medecin_id)', "Ce tarif existe déjà pour cet acte !"), ] 



	def onchange_code_famille_tarif_convention_medecin(self, cr, uid, ids, code_famille, context=None):
		
		# Avant tout on vide la table temporaire des tarifs convention medecin
		# Vidage des tables temporaires
		cr.execute("delete from mcisogem_tarif_convention_medecin_temp where write_uid=%s", (uid,))
		
		if not code_famille:
			return {'value': {'code_tarif_convention_medecin_temp': False}}
		if code_famille:
			data = []
			# Recuperation de la liste de tous les actes de la famille
			cr.execute("select * from mcisogem_nomen_prest where code_fam_prest=%s", (code_famille,))
			lesactes = cr.dictfetchall()
			if len(lesactes) > 0:
			# Insertion de la liste des actes dans la table mcisogem_tarif_convention_medecin_temp
			# Parcours de la liste et enregistrement des donn�es en base
				for acte in lesactes:
					cr.execute("insert into mcisogem_tarif_convention_medecin_temp (create_uid,choix_conv,code_famille,code_acte,montant_brut_tarif,plafond_tarifconv, write_uid) values(%s, %s, %s, %s, %s, %s, %s)", (uid, False, code_famille, acte['id'], 0, 0, uid))
					cr.execute("select * from mcisogem_tarif_convention_medecin_temp where write_uid=%s", (uid,))
					lestarifstemp = cr.dictfetchall()
				for tarif in lestarifstemp:
						data.append(tarif['id'])
				return{'value': {'code_tarif_convention_medecin_temp': data}}
			else:
				return {'value': {'code_tarif_convention_medecin_temp': False}}
					

	def onchange_code_centre(self, cr, uid, ids, code_centre, context=None):
		
		# Avant tout on vide la table temporaire des tarifs convention medecin
		# Vidage des tables temporaires
		cr.execute("delete from mcisogem_medecin_temp where write_uid=%s", (uid,))		
		if not code_centre:
			return False 
		if code_centre:
			data = []
			# Recuperation de la liste de tous les actes de la famille
			cr.execute("select * from mcisogem_praticien a LEFT JOIN praticien_rel b ON (b.libelle_court_prestat = a.id) LEFT JOIN mcisogem_agr_prestat c ON (c.id = b.praticien_rel_id) where c.code_centre=%s", (code_centre,))
			lesmedecins = cr.dictfetchall()
			if len(lesmedecins) > 0:
			# Insertion de la liste des actes dans la table mcisogem_tarif_convention_medecin_temp
			# Parcours de la liste et enregistrement des donn�es en base
				for medecin in lesmedecins:
					cr.execute("insert into mcisogem_medecin_temp (libelle_court_prestat,nom_prenoms_prestat, write_uid) values(%s, %s, %s)", (medecin['libelle_court_prestat'], medecin['nom_prenoms_prestat'], uid))
					cr.execute("select * from mcisogem_medecin_temp where write_uid=%s", (uid,))
					lesmedecinstemp = cr.dictfetchall()
				for med in lesmedecinstemp:
						data.append(med['id'])
				return {'domain':{'codemedecin_id':[('id','in',data)]}}
			else:
				return {'value': {'code_medecin_id': False}}

	def onchange_medecin(self, cr, uid, ids, code_medecin_id, context=None):
		v = {}
		if code_medecin_id:
			med = self.pool.get('mcisogem.medecin.temp').search(cr, uid, [('id', '=', code_medecin_id)])
			med_data = self.pool.get('mcisogem.medecin.temp').browse(cr,uid,med)
			v = {'code_medecin': med_data.libelle_court_prestat}
		return{'value':v}
		
			
			
	def create(self, cr, uid, vals, context=None):

		dernier_id = 0
		# Recuperation de la date du jour
		
  
	  # Recuperation des lignes qui ont été cochées dans la table mcisogem_tarif_convention_temp
		cr.execute("select * from mcisogem_tarif_convention_medecin_temp where write_uid=%s and choix_conv=%s", (uid, True))
		lesactes = cr.dictfetchall()
		if len(lesactes) > 0:
		  
		  # Recuperation des valeurs par défaut
		  #utilisateur_data = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		  #centre_gestion_data = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, utilisateur_data.code_gest_id.id, context=context)
		  
		  # Parcours de la liste des actes sélectionné
		  for acte in lesactes:
			   
				  data = {}
				  data['create_uid'] = uid      
				  data['code_centre'] = vals['code_centre']      
				  data['code_medecin_id'] = vals['code_medecin_id']   
				  data['code_acte'] = acte['code_acte']    
				  data['code_famille'] = acte['code_famille']      
				  data['date_effet_tarif'] = vals['date_effet_tarif']  
					
				  data['write_uid'] = uid      
				  data['montant_brut_tarif'] = acte['montant_brut_tarif'] 
				  data['plafond_tarif'] = acte['plafond_tarifconv']       
				  data['affichage'] = 1
				  
				  dernier_id = super(mcisogem_tarif_convention_medecin, self).create(cr, uid, data, context=context)
		  cr.execute("delete from mcisogem_tarif_convention_medecin_temp where write_uid=%s", (uid,))
		  return dernier_id
		else:
		  raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un acte!")
		  return 0
		

mcisogem_tarif_convention_medecin()



class mcisogem_tarif_convention_medecin_temp(osv.osv):
	_name = "mcisogem.tarif.convention.medecin.temp"
	_description = 'Tarif convention temporaire'
	_columns = {
		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte"),
		'choix_conv': fields.boolean('Choix'),
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte" ,readonly=True),
		'montant_brut_tarif': fields.integer('Montant brut tarif',),
		'plafond_tarifconv': fields.integer('plafond'),
}
	
mcisogem_tarif_convention_medecin_temp()   


class mcisogem_medecin_temp(osv.osv):
	_name = "mcisogem.medecin.temp"
	_description = 'Tarif convention temporaire'
	_columns = {
		'libelle_court_prestat': fields.char('Code'),
		'nom_prenoms_prestat': fields.char('Nom & prénoms')
	}
	_rec_name = 'nom_prenoms_prestat'
	
mcisogem_medecin_temp() 
  
	
