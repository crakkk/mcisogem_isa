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


class mcisogem_resil_convention(osv.osv):
	_name = "mcisogem.resil.convention"
	_description = "Historique de resiliation de convention"

	_columns = {
		'convention_id': fields.many2one('mcisogem.convention', 'Convention'),
		'date_debut_convention': fields.date('Date d\'éffet'),
		'date_fin_convention': fields.date('Date de résiliation')
	}

	_rec_name =  'convention_id'




	def create(self,cr,uid,vals,context=None):
		vals['id'] = context.get('id')
		vals['date_debut_convention'] = context.get('date_debut_convention')
		vals['convention_id'] = context.get('id')
			
		convention = self.pool.get('mcisogem.convention').search(cr,uid,[('id' , '=' , context.get('id'))])
		convention_data = self.pool.get('mcisogem.police').browse(cr, uid, convention)

		if vals['date_fin_convention'] != '1900-01-01' and vals['date_fin_convention'] < vals['date_debut_convention']:
			raise osv.except_osv('Attention !', "La date de résiliation ne doit pas être inférieure à la date d'éffet de la convention !")
		else:
			self.pool.get('mcisogem.convention').write(cr,uid,convention_data.ids,{'state':'resil' ,'date_fin_convention':vals['date_fin_convention']},context=context)
	




class mcisogem_bareme_stat_benef_temp(osv.osv):
	_name = "mcisogem.bareme.stat.benef.temp"
	_description = 'Statut du beneficiaire'
	
	_columns = {
		'delai': fields.integer('Delai', required=True),
		'cod_statut_benef':fields.many2one('mcisogem.stat.benef', 'Statut', readonly=True),
	}
	

class mcisogem_bareme_college_temp(osv.osv):
	_name = "mcisogem.bareme.college.temp"
	_description = 'Collège'
	
	_columns = {
	   'choix': fields.boolean('Choix'),
	   'code': fields.char('Code Collège', readonly=True),
	   'cod_college':fields.many2one('mcisogem.college', 'Collège', readonly=True),
	}
	
	def onchange_choix(self, cr, uid, ids, choix, context=None):
		cr.execute("update mcisogem_bareme_college_temp set choix=%s where id=%s", (choix, ids[0]))



class mcisogem_nomen_prest(osv.osv):
	_name = "mcisogem.nomen.prest"
	_description = 'Actes'
	
	
	
	_columns = {
		'libelle_court_acte': fields.char('Code', size=7, required=True),
		'code_fam_prest': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
		'name' : fields.char('Libellé de l\'acte', size=100, required=True),
		'cout_unit_nomen' : fields.integer('cout_unit_nomen'),
		'l_de_nomen' : fields.char('l_de_nomen', size=3),
		'mtt_lc_carmed' : fields.integer('mtt_lc_carmed'),
		'mtt_lc_hors_carmed' : fields.integer('mtt_lc_hors_carmed'),
		'ratio_th_nomen' : fields.integer('ratio_th_nomen'),
		'l_cle_nomen': fields.char('Lettre clé', size=5),
		'bl_nomen_envig' : fields.boolean('Soumis à entente préalable ?'),
		'entente_pre' : fields.boolean('Soumis à entente préalable ?'),
		'observation_nomen' : fields.text('Observation', size=65),
		'plf_prest_dft' : fields.integer('plf_prest_dft'),
		'ticm_dft' : fields.integer('ticm_dft'),
		'bl_ticm_tx_dft' : fields.integer('bl_ticm_tx_dft'),
		'prest_espece_dft' : fields.integer('prest_espece_dft'),
		'plf_an_prest_dft' : fields.integer('plf_an_prest_dft'),
		'max_act_an_dft' : fields.integer('max_act_an_dft'),
		'bl_envig_carmed' : fields.integer('bl_envig_carmed'),
		'code_sup' : fields.char('cod_sup', size=1),
		'view' : fields.boolean('')   , 
		'produit_police_id' : fields.many2one('mcisogem.produit.police' , ''),
		

	}
	
	_sql_constraints = [('unique_nomen_prest', 'unique(name)', "Cet acte existe déjà !"), ] 

	_defaults = {
		'bl_envig_carmed': 0,
		'max_act_an_dft' : 0,
		'plf_an_prest_dft' : 0,
		'prest_espece_dft' : 0,
		'bl_ticm_tx_dft' : 0,
		'ticm_dft' : 0,
		'plf_prest_dft' : 0,
		'ratio_th_nomen' : 0,
		'mtt_lc_hors_carmed' : 0,
		'mtt_lc_carmed' : 0,
		'cout_unit_nomen' : 0,
		'bl_nomen_envig': True,
		'view' : False
		
	}

	def create(self, cr, uid, vals, context=None):
		vals['view'] = True
		return super(mcisogem_nomen_prest, self).create(cr, uid, vals, context=context)



class mcisogem_bareme_acte_temp(osv.osv):
	_name = "mcisogem.bareme.acte.temp"
	_description = 'Famille d\'acte'

	TYPE_TM = [
		('F', 'Forfait'),
		('T', 'Taux (%)')
	]

	_columns = {
	  
	   'delai': fields.integer('Delai de carence(en Jrs)'),
	   'cod_acte':fields.many2one('mcisogem.nomen.prest',  'Acte', readonly=True),
	   'sous_acte': fields.many2one('mcisogem.sous.actes', 'Sous acte', readonly=True),
	   'bl_ticm_assure_tx': fields.selection(TYPE_TM, 'Type Ticket'),
	   'ticm_assure': fields.float('Ticket modérateur'),
	   'unite_temps_id': fields.many2one('mcisogem.unite.temps', "Périodicité de prescription", required=True),
	   'max_act_an_benef': fields.integer('Quantité'),
	   'plf_prest_assure': fields.integer('Plfd. Trans'),
	   'plafond_tick_mod': fields.float('Plfd. Periode'),
	   'plf_jour': fields.integer('Plfd. Jour'),
	   'plf_prest_fam': fields.integer('Plfd. Famille Assuré'),




	}
	
	def onchange_choix(self, cr, uid, ids, choix, context=None):
		cr.execute("update mcisogem_bareme_acte_temp set choix=%s where id=%s", (choix, ids[0]))













class mcisogem_college_temporaire(osv.osv):
	_name = "mcisogem.college.temporaire"

	_columns = {
		
		'name': fields.many2one('mcisogem.college','name','Collège'),
	}
		

class mcisogem_sexe(osv.osv):
	_name = "mcisogem.sexe"
	_description = 'sexe'
	
	_columns = {
		
	   'name':fields.char('Libellé'),
	   'code':fields.char('code')
	}


	_sql_constraints = [('unique_sexe', 'unique(name)', "Ce sexe existe déjà !"), ] 
	
class mcisogem_benef_college_temp(osv.osv):
	_name = "mcisogem.benef.college.temp"
	_description = 'College temporare'
	
	_columns = {
		
	   'name':fields.many2one('mcisogem.college', 'name', 'College'),
	   
	}

class mcisogem_quittancier_police_temp(osv.osv):
	_name = "mcisogem.quittancier.police.temp"
	_description = 'Police temporare'
	
	_columns = {        
	   'name':fields.many2one('mcisogem.police', 'name', 'Police'),       
	}

class mcisogem_typeavenant_temp(osv.osv):
	_name = "mcisogem.typeavenant.temp"
	_description = 'type avenant temporaire'
	
	_columns = {
		
	   'name':fields.many2one('mcisogem.type.avenant', 'name', 'Type avenant'),
	   
	}

class mcisogem_convention_temp(osv.osv):
	_name = "mcisogem.convention.temp"
	_description = 'Convention'
	_columns = {
		'code_convention': fields.many2one('mcisogem.convention', "Convention", required=True),
		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
		'code_tarif_convention_temp': fields.many2many('mcisogem.tarif.convention.temp',
									   'mcisogem_convention_temp_rel',
										'convention_temp_id',
										'code_convention',
										'Choix des actes', required=True),
		'date_effet_tarif': fields.date("Date d'effet", required=True),
		'date_resiliation_tarif': fields.date("Date de résiliation")
		
	}
	
	_defaults = {
		'date_resiliation_tarif': '1900-01-01'
	}


	
	def onchange_code_famille_tarif_convention(self, cr, uid, ids, code_famille, context=None):
		
		#Avant tout on vide la table temporaire des tarifs
		#Vidage des tables temporaires
		cr.execute("delete from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
		
		if not code_famille:
			return {'value': {'code_tarif_convention_temp': False}}
		if code_famille:
			result = []
			#Recuperation de la liste de tous les actes de la famille
			cr.execute("select * from mcisogem_nomen_prest where code_fam_prest=%s", (code_famille,))
			lesactes = cr.dictfetchall()
			if len(lesactes)>0:
			   #Insertion de la liste des actes dans la table mcisogem_tarif_convention_temp
			   #Parcours de la liste et enregistrement des données en base
			   for acte in lesactes:
				   cr.execute("insert into mcisogem_tarif_convention_temp (create_uid,choix,code_famille,code_acte,montant_brut_tarif, plafond_tarif, write_uid) values(%s, %s, %s, %s, %s, %s, %s)", (uid, False, code_famille, acte['id'], 0, 0, uid))
			   cr.execute("select * from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
			   lestarifstemp = cr.dictfetchall()
			   for tarif in lestarifstemp:
					result.append(tarif['id'])
			   return{'value': {'code_tarif_convention_temp': result}}
			else:
				return {'value': {'code_tarif_convention_temp': False}}


	def create(self, cr, uid, vals, context=None):
		
		#Recuperation des lignes qui ont été cochées dans la table mcisogem_tarif_convention_temp
		cr.execute("select * from mcisogem_tarif_convention_temp where write_uid=%s and choix=%s", (uid,True))
		lesactes = cr.dictfetchall()

		if len(lesactes) > 0:
			
			#Recuperation des valeurs par défaut
			utilisateur_data = self.pool.get('res.users').browse(cr, uid, uid, context=context)
			centre_gestion_data = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, utilisateur_data.code_gest.id, context=context)
			
			#Recuperation de la date du jour
			datedujour = time.strftime('%d-%m-%y %H:%M:%S',time.localtime())
			#Parcours de la liste des actes sélectionné
			for acte in lesactes:

				if not vals['date_resiliation_tarif']:
					vals['date_resiliation_tarif'] = '1900-01-01'
				cr.execute("""insert into mcisogem_tarif_convention 
				(create_uid, code_convention, cod_res_conv, code_acte, code_famille,  date_effet_tarif, write_uid, montant_brut_tarif, plafond_tarif, 
				 write_date, create_date, code_langue, date_resiliation_tarif)
				 values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
							(uid, vals['code_convention'], 0, acte['code_acte'], acte['code_famille'], vals['date_effet_tarif'], uid, acte['montant_brut_tarif'], acte['plafond_tarif'], datedujour, datedujour, centre_gestion_data.code_langue.code_langue, vals['date_resiliation_tarif']))
			#On vide la table des tarifs temporaires
			cr.execute("delete from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
			return 1
		else:
			raise osv.except_osv('Attention !', "Veillez sélectionner au moins un acte!")
			return True

class mcisogem_tarif_convention_temp(osv.osv):
	_name = "mcisogem.tarif.convention.temp"
	_description = 'Tarif convention'
	_columns = {
		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
		'choix': fields.boolean('Choix'),
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", required=True, readonly=True),
		'montant_brut_tarif': fields.integer('Montant brut tarif'),
		'plafond_tarif': fields.integer('Plafond', required=True),
}
