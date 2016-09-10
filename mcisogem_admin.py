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
import tempfile
import base64
import ftplib

import logging
import os

_logger = logging.getLogger(__name__)


class mcisogem_langue(osv.osv):
	_name = "mcisogem.langue"
	_description = 'Langue'
	
	_columns = {
		'code_langue': fields.char('Code', size=10, required=True),
		'name': fields.char('Libellé', size=50, required=True),
		'ph_lib_langue': fields.char('PH Libellé', size=50, required=True),
	}
	_sql_constraints = [('unique_code_langue', 'unique(code_langue)', "Ce code existe déjà !"), ]

class mcisogem_role_user(osv.osv):
	_name = "mcisogem.role.user"
	
	_columns = {
		'name': fields.char('Libelle'),
		'type_user': fields.selection([('GESTIONNAIRE', 'Gestionnaire'), ('GRC', 'Relation client')], 'Groupe d\'utilisateur', required=True)
	}


class res_users(osv.osv):
	_name = "res.users"
	_inherit = "res.users"

	def random_with_N_digits(n):
		range_start = 10**(n-1)
		range_end = (10**n)-1
		return randint(range_start, range_end)

	def onchange_role(self, cr, uid, ids, mcisogem_role_user_id, context=None):
		if mcisogem_role_user_id:
			roles = self.pool.get('mcisogem.role.user').search(cr, uid, [('id', '=', mcisogem_role_user_id)])
			roles_data = self.pool.get('mcisogem.role.user').browse(cr,uid,roles)
			v = {}
			if roles_data:
				if roles_data.name == "GARANT":
					v = {'view3': True, 'view1': False, 'view2': False, 'view4': False, 'view5': False , 'view6': False}
				elif roles_data.name == "MEDECIN CME" or roles_data.name == "SECRETARIAT MEDICAL" or roles_data.name == "PRESTATAIRE" or roles_data.name == "PRESTATAIRE ET SECRETARIAT MEDICAL":
					v = {'view2': True, 'view3': False, 'view1': False, 'view4': False, 'view5': False , 'view6': False}
				elif roles_data.name == "SOUSCRIPTEUR":
					v = {'view4': True, 'view3': False, 'view2': False, 'view1': False, 'view5': False , 'view6': False}
				# elif roles_data.name == "PRESTATAIRE":
				# 	v = {'view1': True, 'view3': False, 'view2': False, 'view4': False, 'view5': False , 'view6': False}
				elif roles_data.name == "INTERMEDIAIRE":
					v = {'view1': False, 'view3': False, 'view2': False, 'view4': False, 'view5': True , 'view6': False}
				elif roles_data.name == "MEDECIN CONSEIL":
					v = {'view1': False, 'view3': False, 'view2': False, 'view4': False, 'view5': False , 'view6': True}
				else:
					v = {'view1': False, 'view3': False, 'view2': False, 'view4': False, 'view5': False , 'view6': False}			
			return{'value':v}

	_columns = {
		'type_user': fields.selection([('GESTIONNAIRE', 'Gestionnaire'), ('GRC', 'Relation client')], 'Groupe d\'utilisateur'),
		'mcisogem_role_user_id': fields.many2one('mcisogem.role.user', "Rôle"),
		'code_gest_id': fields.many2one('mcisogem.centre.gestion'),
		'centre_id': fields.many2one('mcisogem.centre', "Centre de soins"),
		'garant_id': fields.many2one('mcisogem.garant', "Gestionnaire"),
		'souscr_id': fields.many2one('mcisogem.souscripteur', "Souscripteur"),
		'prestat_id': fields.many2one('mcisogem.prestat', "Prestataire"),
		'intermediaire_id': fields.many2one('mcisogem.courtier', "Intermédiaire"),
		'praticien_id' :  fields.many2one('mcisogem.praticien', 'Medecin'),
		'view1' : fields.boolean(''),
		'view2' : fields.boolean(''),
		'view3' : fields.boolean(''),
		'view4' : fields.boolean(''),
		'view4' : fields.boolean(''),
		'view5' : fields.boolean(''),
		'view6' : fields.boolean(''),
		'code_gest': fields.char(''),
		'code_langue': fields.char('code_langue', size=10)
	}

	_defaults = {
		'code_gest': "CI",
		'view1' : False,
		'view2' : False,
		'view3' : False,
		'view4' : False,
		'view5' : False,
		'view6' : False,
	}

	def create(self, cr, uid, data, context=None):
		rep = super(res_users, self).create(cr, uid, data, context=context)

		users = self.pool.get('res.users').search(cr, uid, [('id', '=', rep)])
		user_data = self.pool.get('res.users').browse(cr, uid, users, context=context)

		roles = self.pool.get('mcisogem.role.user').search(cr, uid, [('id', '=', data['mcisogem_role_user_id'])])
		roles_data = self.pool.get('mcisogem.role.user').browse(cr, uid, roles, context=context)

		role_odoo = self.pool.get('res.groups').search(cr, uid, [('name', '=', roles_data.name)])
		role_odoo_data = self.pool.get('res.groups').browse(cr, uid, role_odoo)

		

		cr.execute('select uid from res_groups_users_rel where uid=%s and gid=%s', (rep, role_odoo_data.id))
		test = cr.fetchall()




		if role_odoo_data.name == "PRESTATION(VALIDATION DIRECTION)" or role_odoo_data.name == "PRESTATION(CREATION REGLEMENT)" or role_odoo_data.name == "PRESTATION(VALIDATION SAISIE)":

			g_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', "RESPONSABLE PRESTATION")])
			cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (g_id[0], rep))


		if role_odoo_data.name == "COMPTABILITE(VALIDATION REMBOURSEMENT)" or role_odoo_data.name == "COMPTABILITE(VALIDATION REGLEMENT)":

			g_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', "RESPONSABLE COMPTABLE")])
			cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (g_id[0], rep))


		if role_odoo_data.name == "PRESTATAIRE ET SECRETARIAT MEDICAL":

			g_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', "PRESTATAIRE")])
			cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (g_id[0], rep))

			g_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', "SECRETARIAT MEDICAL")])
			cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (g_id[0], rep))



		if not test:
			cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (role_odoo_data.id, rep))
			cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (3, rep))
			return rep
		else:
			return rep
		
	def write(self, cr, uid, ids, vals, context=None):
		# Recuperation des données
		rep = super(res_users, self).write(cr, uid, ids, vals, context=context)

		if 'mcisogem_role_user_id' in vals:
			

			roles = self.pool.get('mcisogem.role.user').search(cr, uid, [('id', '=', vals['mcisogem_role_user_id'])])
			roles_data = self.pool.get('mcisogem.role.user').browse(cr, uid, roles, context=context)

			role_odoo = self.pool.get('res.groups').search(cr, uid, [('name', '=', roles_data.name)])
			role_odoo_data = self.pool.get('res.groups').browse(cr, uid, role_odoo)

			cr.execute('select uid from res_groups_users_rel where uid=%s and gid=%s', (ids[0], role_odoo_data.id))
			test = cr.fetchall()


			# if test:
			# 	return True
			# else:
			cr.execute("delete from res_groups_users_rel where uid=%s and gid not in %s", (ids[0],(5,4,17)))

			if role_odoo_data.name == "PRESTATION(VALIDATION DIRECTION)" or role_odoo_data.name == "PRESTATION(CREATION REGLEMENT)" or role_odoo_data.name == "PRESTATION(VALIDATION SAISIE)":

				g_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', "RESPONSABLE PRESTATION")])
				cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (g_id[0], ids[0]))


			if role_odoo_data.name == "COMPTABILITE(VALIDATION REMBOURSEMENT)" or role_odoo_data.name == "COMPTABILITE(VALIDATION REGLEMENT)":

				g_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', "RESPONSABLE COMPTABLE")])
				cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (g_id[0], ids[0]))


			if role_odoo_data.name == "PRESTATAIRE ET SECRETARIAT MEDICAL":

				g_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', "PRESTATAIRE")])
				cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (g_id[0], ids[0]))

				g_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', "SECRETARIAT MEDICAL")])
				cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (g_id[0], ids[0]))



			cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (role_odoo_data.id, ids[0]))
			cr.execute("insert into res_groups_users_rel (gid,uid) values(%s, %s)", (3, ids[0]))
			return True

		return rep


			
class mcisogem_commune(osv.osv):
	_name = "mcisogem.commune"
	_description = 'Commune'
	
	_columns = {
		'code_commune': fields.char('Code', size=20, required=True),
		'code_ville': fields.many2one('mcisogem.ville', "Code de la ville", required=True),
		'name': fields.char('Libellé', size=150, required=True),
		'code_sup' : fields.char('cod_sup', size=1),
	}
	
	_sql_constraints = [('unique_commune', 'unique(name)', "Cette commune existe déjà !"), ]


	
class mcisogem_numero(osv.osv):
	_name = "mcisogem.numero"
	_description = 'Numéro'
	
	_columns = {
		'num_remb': fields.integer('Montant', size=18),
		'numero': fields.integer('Montant', size=18),
		'num_benef': fields.integer('Montant', size=18),
		'num_police': fields.integer('Montant', size=18),
		'num_prestexec': fields.char('Montant', size=18),
		'num_quittance': fields.integer('Montant', size=18),
		'num_centre': fields.integer('Montant', size=18),
		'num_regl_quittance': fields.integer('Montant', size=18),
		'num_regt': fields.integer('Montant', size=18),
		'num_regt_garant': fields.integer('Montant', size=18),
		'num_remb_garant': fields.integer('Montant', size=18),
		'num_court_souscr': fields.integer('Montant', size=18),
		'num_quittancier': fields.integer('Montant', size=18),
	}
	
class mcisogem_pays(osv.osv):
	_name = "mcisogem.pays"
	_description = 'Pays'

	_columns = {
		# 'name': fields.char('Libellé', size=50, required=True),
		'name': fields.many2one('res.country', 'Pays' ,  size=50, required=True),
		'code_pays': fields.char('Code', size=18, required=True),
		'zip_code' : fields.char('Code Zip' ,size=5, required=True)
	}

	_sql_constraints = [('unique_pays', 'unique(name)', "Ce pays existe déjà !"), ]
	

	def onchange_pays(self, cr, uid, ids, name):
		v = {}
		if name:
			pays = self.pool.get('res.country').search(cr, uid, [('id', '=', name)])
			pays_data = self.pool.get('res.country').browse(cr,uid,pays)
			v = {'code_pays': pays_data.code}
		return{'value':v}



class mcisogem_ville(osv.osv):
	_name = "mcisogem.ville"
	_description = 'Ville'
	
	_columns = {
		'code_ville': fields.char('Code', size=18, required=True),
		'name': fields.char('Libellé', size=50, required=True),
		'region_id': fields.many2one('mcisogem.region', 'Région'),
		'zone_geo_id': fields.many2one('mcisogem.zone', 'Zone géographique'),
		'code_postal': fields.integer('Code postal'),
	}
	_sql_constraints = [('unique_ville', 'unique(name)', "Cette ville existe déjà !"), ]

class mcisogem_district(osv.osv):
	_name = "mcisogem.district"
	_description = 'District'
	
	
	_columns = {
		'code_district': fields.char('Code', size=18, required=True),
		'name': fields.char('Libellé', size=50, required=True),
		'ville_id': fields.many2one('mcisogem.ville', 'Ville'),
	}

	_sql_constraints = [('unique_code_district', 'unique(code_district)', "Ce code existe déjà !"), ]


class mcisogem_zone(osv.osv):
	_name = "mcisogem.zone"
	_description = 'Zone géographique'
	
	_columns = {
		'code_zone_geo': fields.char('Code', size=10, required=True),
		'name': fields.char('Libellé', size=50, required=True),
	}

	_sql_constraints = [('unique_code_zone_geo', 'unique(code_zone_geo)', "Ce code existe déjà !"), ]
	


class mcisogem_regime(osv.osv):
	_name = "mcisogem.regime"
	_description = 'Type de remboursement'
	_columns = {
		'code_regime': fields.char('Code regime', size=10, required=True),
		'name': fields.char('Libelle regime', size=50),
	}
	_sql_constraints = [('unique_regime', 'unique(name)', "Ce régime existe déjà !"), ]


	
class mcisogem_concurent(osv.osv):
	_name = "mcisogem.concurent"
	_description = 'Concurents'
	
	_columns = {
		'code_concur': fields.char('Code', size=20, required=True),
		'name': fields.char('Libellé', size=150, required=True),
	}

	_sql_constraints = [('unique_concurrent', 'unique(name)', "Ce concurent existe déjà !"), ]


	
class mcisogem_unite_temps(osv.osv):
	_name = "mcisogem.unite.temps"
	_description = 'Unité de temps'
	
	_columns = {
		'code_unite_temps': fields.char('Code', size=1),
		'name': fields.char('Libellé', size=150, required=True),
		'nbre_jour': fields.integer('Nombre de jour'),
	}

	_sql_constraints = [('unique_unite_temps', 'unique(name)', "Cette unité de temps existe déjà !"), ]


class mcisogem_territoire(osv.osv):
	_name = "mcisogem.territoire"
	_description = 'Térritoire'
	
	_columns = {
		'code_territoire': fields.char('Code', size=30, required=True),
		'name': fields.char('Libellé', size=150, required=True),
		'pays_ids' : fields.many2many('mcisogem.pays' , 'mcisogem_territoire_rel' , 'code_pays' , 'code_territoire' , 'Pays')
	}
	_sql_constraints = [('unique_terr', 'unique(name)', "Cette territoire existe déjà !"), ]

	
class mcisogem_regroupe_territoire(osv.osv):
	_name = "mcisogem.regroupe.territoire"
	_description = 'Regroupe Térritoire'
		
	_columns = {
		'code_regroupe_territoire': fields.char('Code', size=30, required=True),
		'name': fields.char('Libellé', size=150, required=True),
		'code_sup': fields.char('Code sup'),
	}

	_sql_constraints = [('unique_regroup', 'unique(name)', "Ce regroupement de territoire existe déjà !"), ]


class mcisogem_region(osv.osv):
	_name = "mcisogem.region"
	_description = 'Region'
	
	_columns = {
		'code_region': fields.char('Code', size=10, required=True),
		'name': fields.char('Libellé', size=50, required=True),
		'pays_id': fields.many2one('mcisogem.pays', "Pays"),
		'zone_geo_id': fields.many2one('mcisogem.zone', "Zone géographique"),
	}
	
	_sql_constraints = [('unique_region', 'unique(name)', "Cette region existe déjà !"), ]

		
class mcisogem_banque(osv.osv):
	_name = "mcisogem.banque"
	_description = 'Banque'    
	
	_columns = {
		'code_banque': fields.char('Code de la banque', size=30, required=True),
		'name': fields.char('Libelle banque', size=100),
		'telephone1': fields.char('Tel', size=18),
		'fax': fields.char('Fax', size=18),
		'gestionnaire_banque': fields.char('Gestionnaire de la banque', size=20),
		'boite_postale': fields.char('Boite postale', size=50),
		'telephone2': fields.char('Tel portable', size=18),
		'adresse': fields.char('Adresse geographique', size=100),
		'date_cloture': fields.date("Date de cloture"),
		'cpta_banque': fields.char('Swift code', size=50),
	}
	
	_defaults = {
		'date_cloture': '1900-01-01',
	}
	_sql_constraints = [('unique_banque', 'unique(name)', "Cette banque existe déjà !"), ]



class mcisogem_centre_gestion(osv.osv):
	_name = "mcisogem.centre.gestion"
	_description = 'Centre de gestion'
	
	CENTRE = [('A','A') , ('B','B'), ('C','C'), ('D','D'), ('E','E'), ('F','F'), ('G','G'), 
	('H','H'), ('I','I'), ('J','J'), ('K','K'), ('L','L'), ('M','M'), ('N','N')
	, ('O','O'), ('P','P'), ('Q','Q'), ('R','R'), ('S','S'), ('T','T'), ('U','U'), 
	('V','V'), ('W','W'), ('X','X'),('Y','Y'), ('Z','Z')]
	_columns = {
		'name': fields.char('Libellé', size=50),
		'lettre_cle' : fields.selection(CENTRE),
		'code_centre': fields.char('Code', size=10, required=True),
		'langue_id': fields.many2one('mcisogem.langue', "Langue"),
		'pays_id': fields.many2one('mcisogem.pays', "Pays"),
		'territoire_id': fields.many2one('mcisogem.territoire', "Territoire"),
		'cod_sup': fields.boolean('Gestion par sous actes'),
		'avoir_ro' : fields.boolean('Régime obligatoire ?'),
		'type_cascade' : fields.selection([('D' , 'Direct') , ('I' , 'Indirect')] , 'Type Cascade') ,
		'ticket_m' : fields.integer('Ticket modérateur (%)'),
	}


class mcisogem_plage_type_garant(osv.osv):
  
	_name = "mcisogem.plage.type.garant"
	_description = 'Plage type garant'
	
	_columns = {
		'name': fields.char('Code plage', required=True),
		'code_type_garant': fields.many2one('mcisogem.type.garant', "Type de garant"),
		'debut_plage_type_garant': fields.integer('Début plage', required=True),
		'fin_plage_type_garant': fields.integer('Fin plage', required=True),
		'dernier_numero_attribue': fields.integer('Dernier Numéro attribué', readonly=True),
		'affichage': fields.integer('affichage',),
	}
	
	_defaults = {
		'dernier_numero_attribue' : 0,
		'affichage' : 0,
	}
	
	def create(self, cr, uid, vals, context=None):
		vals['dernier_numero_attribue'] = vals['debut_plage_type_garant']
		vals['affichage'] = 1
		return super(mcisogem_plage_type_garant, self).create(cr, uid, vals, context=context)
	
	def write(self, cr, uid, ids, vals, context=None):
		# Recuperation des données
		plage_type_data = self.pool.get('mcisogem.plage.type.garant').browse(cr, uid, ids, context=context)
		if vals['fin_plage_type_garant'] < plage_type_data.dernier_numero_attribue:
			raise osv.except_osv('Attention !', "La fin de la plage doit être supérieure ou égale au dernier numéro attribué pour cette plage !")
			return False
		else:
			return super(mcisogem_plage_type_garant, self).write(cr, uid, ids, vals, context=context) 



# statut_benef
class mcisogem_stat_benef(osv.osv):
	_name = "mcisogem.stat.benef"
	_description = 'Statut du bénéfficiaire'
	
	_columns = {
		'cod_statut_benef': fields.char('Code', required=True),
		'tm_stamp': fields.date('tm_stamp', readonly=True),
		'cod_lang':fields.many2one('mcisogem.langue', 'name', 'Langue'),
		'cod_sup': fields.integer('cod_sup'),
		'name': fields.char('Libellé'),
		'lbc_fam_statut': fields.char('lbc_fam_statut'),
		'produit_police_id' : fields.many2one('mcisogem.produit.police' , ''),
	}
	
	


	_sql_constraints = [('unique_stat_benef', 'unique(name)', "Ce Statut existe déjà !"), ]

	def create(self, cr, uid, vals, context=None):
		vals['cod_statut_benef'] = vals['cod_statut_benef'].upper()
		# vals['name'] = vals['name'].upper()
		vals['lbc_fam_statut'] = vals['cod_statut_benef']
		return super(mcisogem_stat_benef, self).create(cr, uid, vals, context=context)

# fam_statut

class mcisogem_fam_statut(osv.osv):
	_name = "mcisogem.fam.statut"
	_description = 'Famille de statut'

	_columns = {
		'lbc_fam_statut': fields.char('Libellé court', required=True),
		'lb_fam_statut': fields.char('Libellé', required=True),
		'code_sup': fields.integer('Code centre de gestion'),
	}
	
class mcisogem_nature_risque(osv.osv):
	_name = "mcisogem.nature.risque"
	_description = 'Nature risque'
	
	_columns = {
		'code_nature_risque': fields.char('Code', size=10, required=True),
		'name': fields.char('Libellé', size=150, required=True),
		'code_sup': fields.integer('Code centre de gestion'),
	}

	_sql_constraints = [('unique_nature_risque', 'unique(name)', "Cette nature risque existe déjà !"), ]


class mcisogem_plage_centre(osv.osv):
	
	_name = "mcisogem.plage.centre"
	_description = 'Plage centre'
	
	_columns = {
		'numero_plage_centre': fields.integer('Code plage', required=True),
		'code_centre' : fields.char('Code centre', size=50),
		'code_plage' : fields.integer('Début plage', size=50, required=True),
		'code_type_centre' : fields.many2one('mcisogem.type.centre', 'Type de centre', required=True),
		'dernier_numero' : fields.integer('Dernier numéro'),
	}
	
	_sql_constraints = [('unique_plage_centre', 'unique(numero_plage_centre,code_type_centre,code_plage)', "Cette plage de centre existe déjà !"), ]
  
	def create(self, cr, uid, vals, context=None):
		# Récuperation du type de centre
		type_centre_data = self.pool.get('mcisogem.type.centre').browse(cr, uid, vals['code_type_centre'], context=context)
		vals['code_centre'] = type_centre_data.code_type_centre2
		return super(mcisogem_plage_centre, self).create(cr, uid, vals, context=context)

	def write(self, cr, uid, ids, vals, context=None):
		# Récuperation du type de centre
		type_centre_data = self.pool.get('mcisogem.type.centre').browse(cr, uid, vals['code_type_centre'], context=context)
		# Ajout des valeurs par defauts
		vals['code_centre'] = type_centre_data.code_type_centre2
		return super(mcisogem_plage_centre, self).write(cr, uid, ids, vals, context=context) 



class mcisogem_plage_bon(osv.osv):
	_name = "mcisogem.plage.bon"
	_description = "Plage de bons attribues aux centres"

	_columns = {
		'centre_id' : fields.many2one('mcisogem.centre' , 'Centre', required=True),
		'debut' : fields.integer('Debut' , required=True),
		'fin' : fields.integer('Fin' , required=True),
	}

	_rec_name = 'centre_id'



	_sql_constraints = [('unique_plage_bon', 'unique(debut,fin)', "Cette plage est déjà attribuée!"), ]


	def create(self, cr, uid, vals, context=None):

		db = vals['debut']
		fn = vals['fin']

		if db > fn:
			raise osv.except_osv('Attention' , 'Le debut de la plage doit être supérieur à la fin !')


		bon_srch = self.pool.get('mcisogem.plage.bon').search(cr,uid,['&' , ('debut' , '<=' , db) , ('fin' , '>=' , fn)])
		
		if not bon_srch:

			bon_srch = self.pool.get('mcisogem.plage.bon').search(cr,uid,['&' , ('debut' , '<=' , db) , ('fin' , '>=' , db)])


			if not bon_srch:

				bon_srch = self.pool.get('mcisogem.plage.bon').search(cr,uid,['&' , ('debut' , '<=' , fn) , ('fin' , '>=' , fn)])

				if not bon_srch:

					bon_srch = self.pool.get('mcisogem.plage.bon').search(cr,uid,['&' , ('debut' , '>=' , db) , ('fin' , '<=' , fn)])



		if bon_srch:

			raise osv.except_osv('Attention' , 'Certains numéros de bons ont déjà été attribués')

		

		return super(mcisogem_plage_bon, self).create(cr, uid, vals, context=context)




# utilisateur_mobile

class mcisogem_utilisateur_mobile(osv.osv):
	_name = "mcisogem.utilisateur.mobile"
	_description = 'mobile users'

	_columns = {
		'matricule': fields.char('Matricule', required=True),
		'login': fields.char('Login', required=True),
		'mot_de_passe': fields.char('Mot de passe', required=True),
		'contact': fields.char('Contact'),
		'base': fields.selection([('WEB' , 'WEB') , ('LOURD' , 'Client lourd')] , 'Base de données')
	}

	_rec_name = 'matricule'

# pub_mobile

class mcisogem_pub_mobile(osv.osv):
    _name = "mcisogem.pub.mobile"
    _description = 'pub mobile'

    def binary2file(self, cr, uid, ids, binary_data, file_prefix="", file_suffix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(binary_data))
        f.close()
        os.close(fileno)
        return fname

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)


    _columns = {
        'titre': fields.char('Titre'),
        'contenu': fields.text('Contenu'),
        'attachments': fields.many2many('ir.attachment', string="Image de la Pub"),
        # 'image': fields.binary("Image",
        #                        help="This field holds the image used as image for the product, limited to 1024x1024px."),
        # 'image_medium': fields.function(_get_image, fnct_inv=_set_image,
        #                                 string="Medium-sized image", type="binary", multi="_get_image",
        #                                 store={
        #                                     'mcisogem.pub.mobile': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
        #                                 },
        #                                 help="Medium-sized image of the product. It is automatically " \
        #                                      "resized as a 128x128px image, with aspect ratio preserved, " \
        #                                      "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        # 'image_small': fields.function(_get_image, fnct_inv=_set_image,
        #                                string="Small-sized image", type="binary", multi="_get_image",
        #                                store={
        #                                    'mcisogem.pub.mobile': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
        #                                },
        #                                help="Small-sized image of the product. It is automatically " \
        #                                     "resized as a 64x64px image, with aspect ratio preserved. " \
        #                                     "Use this field anywhere a small image is required."),
        'Date': fields.date('Date'),

    }

    _rec_name = 'titre'

    def create(self, cr, uid, vals, context=None):
        ftp_server = "196.47.172.197"
        port = 22
        ftp_user = "apache"
        ftp_pwd = "smileci0901"
        ftp_source = "/webservice_app_mob/images/"

        pubid = super(mcisogem_pub_mobile, self).create(cr, uid, vals, context=context)
        cr.execute('select ir_attachment_id from ir_attachment_mcisogem_pub_mobile_rel where mcisogem_pub_mobile_id=%s', (pubid,))
        atta_brw = cr.fetchone()[0]

        attach_obj = self.pool.get('ir.attachment').browse(cr, uid, atta_brw, context=context)

        file = self.binary2file(
                    cr, uid, atta_brw, attach_obj.datas, "ftp", "")

        s = ftplib.FTP(ftp_server, port, ftp_user, ftp_pwd)
        f = open((file), 'rb')
        s.cwd(ftp_source)
        bin = attach_obj.datas_fname
        s.storbinary('STOR ' + (bin.replace('/', '_')), f)
        f.close()
        s.quit()

        return pubid







