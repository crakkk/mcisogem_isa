# -*- coding: utf8 -*-
import time
from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import osv
from datetime import datetime
from openerp import tools
from openerp.tools.translate import _
import openerp
from dateutil.relativedelta import relativedelta
from dateutil import parser
import logging
_logger = logging.getLogger(__name__)


# creer les classes presentation et dci

class mcisogem_presentation(osv.osv):
	_name = 'mcisogem.presentation'
	_columns = {
		'name' : fields.char('Libellé' , required=True),
	}

class mcisogem_dci(osv.osv):
	_name = 'mcisogem.dci'
	_columns = {
		'name' : fields.char('Libellé' , required=True),
	}


class mcisogem_medicament(osv.osv):
	_name = 'mcisogem.medicament'
	_columns = {
		'code_medicament':fields.char('Code' , required=True),
		'acte_id' : fields.many2one('mcisogem.nomen.prest' , 'Famille' , required=True),
		'name' : fields.char('Nom commercial' , required=True),
		'presentation_id' : fields.many2one('mcisogem.presentation' , 'Présentation'),
		'dci_id' : fields.many2one('mcisogem.dci' , 'Dci'),

		't' : fields.char('T'),
	}


	def chargement(self, cr, uid,t,context=None):
		
		f_id = self.pool.get('mcisogem.fam.prest').search(cr,uid,[('libelle_court_famille' , '=' , 'PHAR')])

		if not f_id:
			f_id = self.pool.get('mcisogem.fam.prest').search(cr,uid,[('libelle_court_famille' , '=' , 'FAR')])

			if not f_id:
				f_id = self.pool.get('mcisogem.fam.prest').search(cr,uid,[('libelle_court_famille' , '=' , 'PH')])
		

		if f_id:

			acte_ids = self.pool.get('mcisogem.nomen.prest').search(cr,uid,[('code_fam_prest' , '=' , f_id)])


			return {'domain' : {'acte_id' : [('id' , 'in' , acte_ids)] } }
			

class mcisogem_type_centre(osv.osv):
	_name = "mcisogem.type.centre"
	_description = 'Type de centre'
	
	_columns = {
		'name': fields.char('Libellé', size=50, required=True),
		'code_type_reserve' : fields.boolean('Type reservé'),
		'code_sup' : fields.char('cod_sup', size=1),
		'Nbre_ctr' : fields.integer('Nbre_ctr'),
		'code_type_centre2' : fields.char('Lettre', size=50, required=True),
		'view': fields.boolean('')              
	}
	
	_sql_constraints = [('unique_type_centre', 'unique(name)', "Ce type de centre existe déjà !"), ]

	_defaults = {
		'Nbre_ctr':0,
		'code_type_reserve': True,
		'view': False
	}

	def create(self, cr, uid, data, context=None):
		data['name'] = (data['name']).upper()
		data['code_type_centre2'] = (data['code_type_centre2']).upper()
		return super(mcisogem_type_centre, self).create(cr, uid, data, context=context)


class mcisogem_centre(osv.osv): 
	_name = "mcisogem.centre"
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_description = 'Centre'

	def _get_zip(self, cr, uid, context=None):
		cr.execute('select pays_id from mcisogem_centre_gestion')        
		centre_pays_id = cr.fetchone()[0]
		pays_table = self.pool.get('mcisogem.pays').search(cr, uid, [('id', '=', centre_pays_id)])
		pays_obj = self.pool.get('mcisogem.pays').browse(cr, uid, pays_table, context=context)
		return "+" + str(pays_obj.zip_code)


	def button_to_done(self, cr, uid, ids, data, context=None):
		table = self.search(cr, uid, [('id', '=', ids)])
		table_obj = self.browse(cr, uid, table, context=context)
		if not table_obj.cpta_centre or not table_obj.numero_guichet_centre or not table_obj.numero_compte_centre or not table_obj.numero_banque_centre or not table_obj.cle_rib_centre or not table_obj.compta_prestat_tiers or not table_obj.regl_centre_prestat or not table_obj.mode_paiement_centre or not table_obj.mode_paiement_centre:
			e_mess = "Veuillez renseigner les informations comptable avant la validation"
			raise osv.except_osv(_('Attention !'), _(e_mess))
		else:
			return self.write(cr, uid, ids, {'state' : 'finish'}, context=context)
		 
	
	def button_to_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'done'}, context=context)
		return True

	def _get_group(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		group_id = cr.fetchone()[0]
		group_obj = self.pool.get('res.groups').browse(cr, uid, group_id, context=context)
		if group_obj.name == 'Financial Manager':
			return True
		else:
			return False

		# def _is_compta(self, cr, uid, ids, field_name, arg, context=None):
	#   cr.execute('select res_groups_users_rel.gid from res_groups_users_rel, res_groups where res_groups_users_rel.gid = res_groups.id and res_groups_users_rel.uid=%s and  res_groups.name in %s', (uid,('RESPONSABLE COMPTABLE','UTILISATEUR COMPTABLE')))
	#   lesgroups = cr.dictfetchall()

	#   print('#####################################""')
	#   print(len(lesgroups) )

	#   if len(lesgroups) == 0:
	#       return False
	#   else:
	#       return False
	
	_columns = {
		'code_centre': fields.char('Code du centre', readonly=True),
		'code_type_centre': fields.many2one('mcisogem.type.centre', "Type de centre", required=True),
		'code_ville': fields.many2one('mcisogem.ville', "Ville", required=True),
		'code_district': fields.many2one('mcisogem.district', "District"),
			'name' : fields.char('Libellé du centre', required=True, read=['mcisogem_isa.group_comptabilite_manager'],),
		'plage_bon_ids' : fields.one2many('mcisogem.plage.bon' ,'centre_id',  'Plages de bons'),
		'adresse_centre' : fields.char('Adresse géographique'),
		'code_bp_centre' : fields.char('Code BP', size=20),
		'bp_centre' : fields.char('Boite postale', size=20),
		'tel_centre1' : fields.char('Téléphone 1', size=150),
		'tel_centre2' : fields.char('Téléphone 2', size=150),
		'tel_resp_hh' : fields.char('Contact reponsable', size=20),
		'fax_centre' : fields.char('Fax', size=20),
		'observation_centre' : fields.text('Observations', size=65),
		'regl_centre_prestat' : fields.selection([('CE', 'Centre'), ('PR', 'Prescripteur'), ('SE', 'Service'), ('AU', 'Autre ordre')], 'Paiement à l\'ordre de'),
		'mode_paiement_centre' : fields.selection([('LC', 'Chèque'), ('ES', 'Espèce'), ('VI', 'Virement bancaire'), ('AU', 'Autre')], 'Mode de paiement'),
		'regl_centre_prestat_autre' : fields.char('Intitulé de l\'ordre'),
		'mode_paiement_centre_autre' : fields.char('Intitulé du mode de paiement'),
		'numero_guichet_centre' : fields.char('N° Guichet', size=20),
		'numero_banque_centre' : fields.char('N° Banque', size=20),
		'numero_compte_centre' : fields.char('N° Compte', size=20),
		'cle_rib_centre' : fields.char('Clé RIB', size=20),
		'autre_ordre_centre' : fields.char('Autre ordre', size=65),
		'cpta_centre' : fields.char('Compte général', size=20),
		'code_sup' : fields.char('cod_sup', size=1),
		'email_centre' : fields.char('Email', size=50),
		'show_chp': fields.boolean(''),
		'correspondant' : fields.char('Correspondant', size=150),
		'responsable' : fields.char('Responsable', size=150, required=True),
		'capital' : fields.integer('Capital'),
		'code_territoire': fields.many2one('mcisogem.pays', "Pays", required=True),
		'code_commune': fields.many2one('mcisogem.commune', "Commune"),
		'privilege' : fields.selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')], 'Privilège'),
		'activer' : fields.boolean('Actif'),
		'compta_prestat_tiers' : fields.char('Compte tiers', size=50),
		'code_externe' : fields.char('Code externe', size=50),
		'view' : fields.boolean(''),
		'banque_id' : fields.many2one('mcisogem.banque', 'Banque'),
		'longitude' : fields.float('Longitude'),
		'latitude' : fields.float('Latitude'),
	
		'state': fields.selection([
			('draft', "Nouveau"),
			('done', "Informations Comptable"),
			('finish', "Terminer"),
		], 'Status', readonly=True)
	}
	_defaults = {
		'view': False,
		'privilege': '0',
		'activer': True,
		'state': 'draft',
		'tel_centre1': _get_zip,
		'tel_centre2': _get_zip,
		'show_chp' : _get_group
	}
	 
	_sql_constraints = [('unique_code', 'unique(name, code_centre)', "Ce souscripteur existe déjà !"), ]

	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "RESPONSABLE COMPTABLE" or group_obj.name == "UTILISATEUR COMPTABLE":
					return [('state', '=', 'done')]
			return False
		else:
			return False
	   
	_sql_constraints = [('unique_centre', 'unique(name)', "Ce centre existe déjà !"), ]


	def onchange_code_ville_centre(self, cr, uid, ids, code_ville, context=None):
			return {'value': {'code_commune' : False}}
	
	def onchange_regl_centre_prestat(self, cr, uid, ids, nom, context=None):
		if not nom:
			return {'value': {'autre_ordre_centre' : False}}
		if nom:
			return {'value': {'autre_ordre_centre' : nom}}

	
	def create(self, cr, uid, vals, context=None):
		# Géneration du code du centre 
		vals['view'] = True
		vals['state'] = 'done'
		
		vals['name'] = (vals['name']).upper()
		phone = vals['tel_centre1']
		vals['tel_centre1'] = phone[0:4] + " " + phone[4:6] + " " + phone[6:8] + " " + phone[8:10] + " " + phone[10:12]

		phone = vals['tel_centre2']
		vals['tel_centre2'] = phone[0:4] + " " + phone[4:6] + " " + phone[6:8] + " " + phone[8:10] + " " + phone[10:12]
		rep =  super(mcisogem_centre, self).create(cr, uid, vals, context=context)

		########### envoi des notifications a la comptabilité
		msg = str("Un nouveau centre a été créer. Merci de renseigner ses informations comptable")

		cr.execute("select id from res_groups where name='RESPONSABLE COMPTABLE' or name='UTILISATEUR COMPTABLE'")
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
				subject="Informations comptable centre",
				context=context
				)

			###################################################
		
		# type_centre = self.pool.get('mcisogem.type.centre').search(cr,uid,[('id' , '=' , vals['code_type_centre'])])
		# type_centre_data = self.pool.get('mcisogem.type.centre').browse(cr, uid, type_centre)
		# cr.execute('select code_centre from mcisogem_centre_gestion')
		# cg_code = cr.fetchone()[0]

		# if len(str(rep)) == 7:
		# 	increment = "0" + str(rep)
		# if len(str(rep)) == 6:
		# 	increment = "00" + str(rep)
		# if len(str(rep)) == 5:
		# 	increment = "000" + str(rep)
		# elif len(str(rep)) == 4:
		# 	increment = "0000" + str(rep)
		# elif len(str(rep)) == 3:
		# 	increment = "00000" + str(rep)
		# elif len(str(rep)) == 2:
		# 	increment = "000000" + str(rep)
		# elif len(str(rep)) == 1:
		# 	increment = "0000000" + str(rep)
		# else:
		# 	increment = str(rep)

		# if len(str(type_centre_data.id)) == 1:
		# 	idtyp = "0" + str(type_centre_data.id)
		# else:
		# 	idtyp = str(type_centre_data.id)

		# code_centre = cg_code + idtyp + increment
		# self.pool.get('mcisogem.centre').write(cr,uid,rep,{'code_centre':code_centre},context=context)
		# return rep


		type_centre = self.pool.get('mcisogem.type.centre').search(cr,uid,[('id' , '=' , vals['code_type_centre'])])
		type_centre_data = self.pool.get('mcisogem.type.centre').browse(cr, uid, type_centre)

		# CODE CENTRE DE GESTION

		cr.execute('select code_centre from mcisogem_centre_gestion')
		cg_code = cr.fetchone()[0]

		# PAYS CENTRE DE GESTION

		centre_gestion_ids = self.pool.get('mcisogem.centre.gestion').search(cr,uid,[('code_centre' , '=' , cg_code)])
		centre_gestions = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, centre_gestion_ids)
		code_pays = centre_gestions.pays_id.code_pays

		# INCREMENTATION

		# if len(str(rep)) == 7:
		# 	increment = "0" + str(rep)
		# if len(str(rep)) == 6:
		# 	increment = "00" + str(rep)
		# if len(str(rep)) == 5:
		# 	increment = "000" + str(rep)
		# elif len(str(rep)) == 4:
		# 	increment = "0000" + str(rep)
		# elif len(str(rep)) == 3:
		# 	increment = "00000" + str(rep)
		# elif len(str(rep)) == 2:
		# 	increment = "000000" + str(rep)
		# elif len(str(rep)) == 1:
		# 	increment = "0000000" + str(rep)
		# else:
		# 	increment = str(rep)

		if len(str(rep)) == 4:
			increment = "" + str(rep)
		elif len(str(rep)) == 3:
			increment = "0" + str(rep)
		elif len(str(rep)) == 2:
			increment = "00" + str(rep)
		elif len(str(rep)) == 1:
			increment = "000" + str(rep)
		else:
			increment = str(rep)


		# INCREMENTATION

		# if len(str(type_centre_data.id)) == 1:
		# 	idtyp = "0" + str(type_centre_data.id)
		# else:
		# 	idtyp = str(type_centre_data.id)

		#########################

		if type_centre_data.name == 'CLINIQUE':
			idtyp =  "03"
		elif type_centre_data.name == 'PHARMACIE':
			idtyp =  "12"
		elif type_centre_data.name == 'CABINET DENTAIRE':
			idtyp =  "08"
		elif type_centre_data.name == 'CABINET DENTAIRE':
			idtyp =  "08"
		elif type_centre_data.name == "CENTRE MEDICAL D'ENTREPRISE":
			idtyp =  "05"
		elif type_centre_data.name == "OPTIQUE MEDICAL":
			idtyp =  "11"
		elif type_centre_data.name == "HOPITAL PUBLIC":
			idtyp =  "06"
		elif type_centre_data.name == "HOPITAL CONFESSIONNEL":
			idtyp =  "07"
		elif type_centre_data.name == "CENTRE DE RADIOLOGIE MEDICALE":
			idtyp =  "10"
		elif type_centre_data.name == "LABORATOIRE D'ANALYSES MEDICALES":
			idtyp =  "09" 
		elif type_centre_data.name == "POLYCLINIQUE":
			idtyp =  "04"
		else:
			idtyp =  "00"




		code_centre = code_pays + cg_code + idtyp + increment
		self.pool.get('mcisogem.centre').write(cr,uid,rep,{'code_centre':code_centre},context=context)
		return rep


class mcisogem_fam_activite(osv.osv):
	
	_name = "mcisogem.fam.activite"
	_description = 'Famille d\'activité'
	
	_sql_constraints = [('unique_fam_activite', 'unique(code_activite,code_fam_prest)', "Cette famille d'activité existe déjà !"), ] 
	
	_columns = {
		'code_activite': fields.char('Code de l\'activite', size=10, required=True),
		'code_fam_prest': fields.integer('Code famille', required=True),
		'code_sup' : fields.char('cod_sup', size=1) 
}


class mcisogem_fam_prest(osv.osv):
	_name = "mcisogem.fam.prest"
	_description = 'Famille d\'actes'
	
	_columns = {
		'libelle_court_famille' : fields.char('Code', size=10, required=True),
		'name' : fields.char('Libellé', size=60, required=True),
		'observation_famille' : fields.text('Observation', size=65),
		'type_liasse' : fields.char('type_liasse', size=1),
		'code_sup' : fields.char('cod_sup', size=1),
		'type_fam_act' : fields.integer('type_fam_act'),
		'view' : fields.boolean(''),  
	}
	_defaults = {
		'type_fam_act': 0,
		'view' : False
	}
	_sql_constraints = [('unique_code', 'unique(libelle_court_famille, name)', "Cette famille d'acte existe déjà !"), ]
  
	def create(self, cr, uid, vals, context=None):
		vals['view'] = True
		return super(mcisogem_fam_prest, self).create(cr, uid, vals, context=context)


class mcisogem_acte_entente_preal(osv.osv):
	_name = "mcisogem.acte.entente.prealable"
	_description = 'Actes soumis à entente préalable'
	
	_sql_constraints = [('unique_nomen_prest', 'unique(code_langue,code_famille)', "Cette famille d'activité figure déjà dans la liste des actes soumis à entente préalable, veuillez la modifier si vous désirez ajouter ou rétirer des actes !"), ] 
	
	_columns = {
		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
		'acte_ids': fields.many2many('mcisogem.nomen.prest',
									   'mcisogem_acte_rel',
										'acte_entente_prealable_id',
										'code_acte',
										'Actes soumis à entente préalable'),
	}
	_rec_name = 'code_famille'

	def onchange_code_famille_entente(self, cr, uid, ids, code_famille, context=None):
		if not code_famille:
			return {'value': {'code_famille' : False}}
		else:
			# Vérifions si le code famille existe bien en base de données
			cr.execute('select id from mcisogem_acte_entente_prealable where code_famille=%s', (code_famille,))        
			lesactessoumis = cr.dictfetchall()
			if len(lesactessoumis) > 0 :
				raise osv.except_osv('Attention !', "Cette famille d'acte comporte des actes soumis à entente, veuillez procéder à leur modification !")
				return {'value': {'code_famille' : False}}
			else:
				return {'value': {'code_famille' : code_famille}}

	def onchange_code_famille_entente(self, cr, uid, ids, code_famille, context=None):
		if not code_famille:
			return {'value': {'code_famille' : False}}
		else:
			# Vérifions si le code famille existe bien en base de données
			cr.execute('select id from mcisogem_acte_entente_prealable where code_famille=%s', (code_famille,))        
			lesactessoumis = cr.dictfetchall()
			if len(lesactessoumis) > 0 :
				raise osv.except_osv('Attention !', "Cette famille d'acte comporte des actes soumis à entente, veuillez procéder à leur modification !")
				return {'value': {'code_famille' : False}}
			else:
				return {'value': {'code_famille' : code_famille}}

class mcisogem_convention_unique(osv.osv):
	_name = "mcisogem.convention.unique"
	_description = 'Convention unique'
	
	_columns = {
		'libelle': fields.char('Libellé')
	}
	_rec_name = 'libelle'

class mcisogem_convention(osv.osv):
	_name = "mcisogem.convention"
	_description = 'Convention'
	
	_columns = {
		# 'lib': fields.char('Libellé', required=True),
		'date_debut_convention': fields.date('Date d\'effet', required=True),
		'date_fin_convention': fields.date('Date de résiliation', readonly=True),
		'code_default_acte_temp': fields.many2many('mcisogem.default.acte.temp',
									   'mcisogem_conv_acte_temp_rel',
										'acte_temp_id',
										'id',
										'Actes', required=False),
		'type_tarif' : fields.selection([('CLN', 'Clinique'), ('DENT', 'Cabinet Dentaire')],'Type de tarif', required=False),
		'description_convention': fields.text('Description', size=30),
		'montant_plafond_tarif': fields.integer('Plafond'),
		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte", readonly=True),
		'code_conv': fields.many2one('mcisogem.convention.unique', "Convention", required=True, ondelete='cascade'),
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", required=False),
		'view': fields.boolean(''),
		'state': fields.selection([
			('draft', "Actif"),
			('resil', "Résilier"),
		], 'Status', readonly=True)

	}
	
	_defaults = {
		'view': False,
		'state': 'draft'
	}
	_rec_name = 'code_conv'

	# _sql_constraints = [('unique_code', 'unique(lib, date_debut_convention)', "Cette convention existe déjà !"), ]

	# def create(self, cr, uid, vals, context=None):
	#   vals['view'] = True
	#   vals['name'] = (vals['name']).upper()
	#   return super(mcisogem_convention, self).create(cr, uid, vals, context=context)

	def create(self, cr, uid, vals, context=None):

	  dernier_id = 0
	  cr.execute("select * from mcisogem_convention where code_conv=%s and type_tarif=%s", (vals['code_conv'], vals['type_tarif'],))
	  lesconv = cr.dictfetchall()

	  if len(lesconv) > 0:
		  raise osv.except_osv('Attention !', "Cette convention à déjà des plafonds pour les actes du type sélectionné.")

		# Recuperation de la date du jour
	  datedujour = time.strftime('%d-%m-%y %H:%M:%S', time.localtime())
  
	  # Recuperation des lignes qui ont été cochées dans la table mcisogem_tarif_convention_temp
	  cr.execute("select * from mcisogem_default_acte_temp where write_uid=%s and montant_brut_tarif !=%s", (uid, 0))
	  lesactes = cr.dictfetchall()
	  cr.execute("select * from mcisogem_default_acte_temp where write_uid=%s and montant_brut_tarif !=%s", (uid, 0))
	  lesactesdefbon = cr.dictfetchall()

	  cr.execute("select * from mcisogem_default_acte_temp where write_uid=%s and montant_brut_tarif =%s", (uid, 0))
	  lesactesdef = cr.dictfetchall()

	  

	  data2 = {}

	  if len(lesactesdef) == 0:     
		  # Parcours de la liste des actes sélectionné

		  for acte in lesactes:
							   
			  data = {}
			  data['view'] = True
			  data['type_tarif'] = vals['type_tarif']   
			  data['code_acte'] = acte['code_acte']    
			  data['code_famille'] = acte['code_famille']  

			  data['date_debut_convention'] = vals['date_debut_convention']      
			  data['description_convention'] = vals['description_convention']     

			  data['montant_plafond_tarif'] = acte['montant_brut_tarif'] 

			  data['write_date'] = datedujour      
			  data['create_date'] = datedujour 
			  data['state'] = 'draft'  
			  data['code_conv'] = vals['code_conv'] 

			  dernier_id = super(mcisogem_convention, self).create(cr, uid, data, context=context)
			  
			  # On vide la table des tarifs temporaires
			  cr.execute("delete from mcisogem_default_acte_temp where write_uid=%s", (uid,))

		  return dernier_id
	  else:
		  raise osv.except_osv(_('Attention!'),_('Vous devez obligatoirement renseigner tous les plafonds des actes principaux de la convention'))
		  return 0

	def button_resilier_convention(self, cr, uid, ids, context=None):

		convention = self.browse(cr, uid, ids[0], context=context).id
		convention_table = self.search(cr, uid, [('id', '=', convention)])

		convention_data = self.browse(cr, uid, convention_table)
		
		ctx = (context or {}).copy()
		ctx['id'] = convention
		ctx['date_debut_convention'] = convention_data.date_debut_convention
		ctx['form_view_ref'] = 'view_mcisogem_convention_resilier_form'
		
		return {
		  'name':'Resiliation',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.resil.convention',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}


	def onchange_conv(self, cr, uid, ids, code_convention, context=None):
		if not code_convention:
			return False
		else:
			table = self.pool.get('mcisogem.convention')
			conv_table = table.search(cr, uid, [('id', '=', code_convention)])
			conv_data = table.browse(cr, uid, conv_table)


	def button_to_reactive(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'draft', 'date_fin_convention':'1900-01-01', 'date_debut_convention': time.strftime('%d-%m-%y', time.localtime())}, context=context)


	# def onchange_typetarif(self, cr, uid, ids, type_tarif, context=None):
		
	#   # Avant tout on vide la table temporaire des tarifs
	#   # Vidage des tables temporaires
		
	#   if not type_tarif:
	#       return {'value': {'code_default_acte_temp': False}}
	#   if type_tarif:
	#       data = []


	#       # cr.execute("select * from mcisogem_tarif_convention where type_tarif=%s", (type_tarif,))
	#       # lesconv = cr.dictfetchall()

	#       # if len(lesconv) > 0:
	#       #   return {'value': {'code_default_acte_temp': False}}

	#       # Recuperation de la liste de tous les actes de la famille
	#       if type_tarif == 'CLN':
	#           les_actes = self.pool.get('mcisogem.nomen.prest').search(cr,uid,['|' , ('libelle_court_acte' , 'in' , ['C','CS','AMI','FHHM']) , ('l_cle_nomen' , 'in' , ['B','Z','KC','KE'])])
	#       else:
	#           les_actes = self.pool.get('mcisogem.nomen.prest').search(cr,uid,['|' , ('libelle_court_acte' , 'in' , ['D' , 'DDC']) , ('l_cle_nomen' , 'in' , ['Z', 'D'])])


	#       return{'domain': {'code_default_acte_temp': [('code_acte' , 'in' , les_actes)]}}

	def onchange_typetarif(self, cr, uid, ids, type_tarif, context=None):
		
		# Avant tout on vide la table temporaire des tarifs
		# Vidage des tables temporaires
		cr.execute("delete from mcisogem_default_acte_temp where write_uid=%s", (uid,))
		
		if not type_tarif:
			return {'value': {'code_default_acte_temp': False}}

		data = []
		# lesconv = cr.dictfetchall()

		# Recuperation de la liste de tous les actes de la famille
		if type_tarif == 'CLN':
			cr.execute("select * from mcisogem_nomen_prest where libelle_court_acte in %s or l_cle_nomen in %s order by name asc", (('C','CS','AMI','FHHM'),('B','Z','KC','KE')))
			lesactes = cr.dictfetchall()
		else:
			cr.execute("select * from mcisogem_nomen_prest where libelle_court_acte in %s or l_cle_nomen in %s order by name asc", (('D' , 'DDC'),('Z', 'D')))
			lesactes = cr.dictfetchall()
		
		if len(lesactes) > 0:
		   # Insertion de la liste des actes dans la table mcisogem_tarif_convention_temp
		   # Parcours de la liste et enregistrement des données en base
		   for acte in lesactes:
			   cr.execute("insert into mcisogem_default_acte_temp (create_uid,code_famille,code_acte,lettre_cle,montant_brut_tarif, write_uid) values(%s, %s, %s, %s, %s, %s)", (uid, acte['code_fam_prest'], acte['id'], acte['l_cle_nomen'], 0, uid))
			   cr.execute("select * from mcisogem_default_acte_temp where write_uid=%s", (uid,))
			   lestarifstemp = cr.dictfetchall()
		   for tarif in lestarifstemp:
				data.append(tarif['id'])
		   return{'value': {'code_default_acte_temp': data}}

		else:
		 	
		   return{'value': {'code_default_acte_temp': None}}

		# if type_tarif:
		#     data = []
			# cr.execute("select * from mcisogem_convention where type_tarif=%s", (type_tarif,))
			# lesconv = cr.dictfetchall()

			# if len(lesconv) > 0:
			#     return {'value': {'code_default_acte_temp': False}}

		#     # Recuperation de la liste de tous les actes de la famille
		#     if type_tarif == 'CLN':
		#         cr.execute("select * from mcisogem_nomen_prest where libelle_court_acte in %s or l_cle_nomen in %s order by name asc", (('C','CS','AMI','FHHM'),('B','Z','KC','KE')))
		#         lesactes = cr.dictfetchall()
		#     else:
		#         cr.execute("select * from mcisogem_nomen_prest where libelle_court_acte in %s or l_cle_nomen in %s order by name asc", (('D' , 'DDC'),('Z', 'D')))
		#         lesactes = cr.dictfetchall()
			
		#     if len(lesactes) > 0:
		#        # Insertion de la liste des actes dans la table mcisogem_tarif_convention_temp
		#        # Parcours de la liste et enregistrement des données en base
		#        for acte in lesactes:
		#            cr.execute("insert into mcisogem_default_acte_temp (create_uid,code_famille,code_acte,lettre_cle,montant_brut_tarif, write_uid) values(%s, %s, %s, %s, %s, %s)", (uid, acte['code_fam_prest'], acte['id'], acte['l_cle_nomen'], 0, uid))
		#            cr.execute("select * from mcisogem_default_acte_temp where write_uid=%s", (uid,))
		#            lestarifstemp = cr.dictfetchall()
		#        for tarif in lestarifstemp:
		#             data.append(tarif['id'])
		#        return{'value': {'code_default_acte_temp': data}}
		#     else:
		#         return {'value': {'code_default_acte_temp': False}}



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


class mcisogem_spec_med(osv.osv):
	_name = "mcisogem.spec.med"
	_description = 'Spécialités'
	
	_columns = {
		'libelle_court_spec': fields.char('Libellé court', required=True),
		'name': fields.char('Libellé', required=True),
		'bl_prescr_autoris': fields.boolean('Prescription autorisée'),
		'code_sup' : fields.char('cod_sup', size=1),
		'Nbre_ctr': fields.integer('Nbre_ctr'),
		'code_specialite_reserve': fields.boolean('Spécialité reservée')
	}
	
	_sql_constraints = [('unique_spec_med', 'unique(libelle_court_spec)', "Cette spécialité existe déjà !"), ]

	_defaults = {
		'Nbre_ctr': 0,
	}

	def create(self, cr, uid, data, context=None):
		data['name'] = (data['name']).upper()
		data['libelle_court_spec'] = (data['libelle_court_spec']).upper()
		return super(mcisogem_spec_med, self).create(cr, uid, data, context=context)
	
mcisogem_spec_med()


class mcisogem_prestat(osv.osv):
	_name = "mcisogem.prestat"
	_description = 'Prestataire'
	
	_columns = {
		'libelle_court_prestat': fields.char('Libellé court', size=10, required=False),
		'code_ville': fields.many2one('mcisogem.ville', "Ville", required=True),
		'code_specialite': fields.many2one('mcisogem.spec.med', "Spécialité", required=True),
		'nom_prestat': fields.char('Nom', size=100, required=True),
		'prenoms_prestat': fields.char('Prenoms', size=100, required=True),
		'adresse_prestat': fields.char('Adresse', size=60),
		'code_bp_prestat': fields.char('Code postale', size=20),
		'bp_prestat': fields.char('Boite postale', size=20),
		'tel_prestat': fields.char('Boite postale', size=20),
		'tel1_prestat': fields.char('Boite postale', size=20),
		'fax_prestat': fields.char('Fax', size=20),
		'pc_gratuit_prestat': fields.char('pc_gratuit_prestat', size=20),
		'observation_prestat': fields.text('Observation', size=60),
		'regl_centre_prestat' : fields.selection([('C', 'Centre'), ('P', 'Prestataire'), ('A', 'Autre ordre')], 'Paiement à l\'ordre de '),
		'mode_paiement_prestat' : fields.selection([('LC', 'Chèque'), ('ES', 'Espèce'), ('VI', 'Virement bancaire'), ('AU', 'Autre')], 'Mode de paiement'),
		'numero_banque_prestat': fields.char('No banque', size=20),
		'numero_guichet_prestat': fields.char('No guichet', size=20),
		'numero_compte_prestat': fields.char('No Compte', size=20),
		'cle_rib_prestat': fields.char('Clé rib', size=20),
		'cpta_prestat': fields.char('Compte général', size=20),
		'code_sup' : fields.char('cod_sup', size=1),
		'email_prestat' : fields.char('Email', size=50),
		'correspondant_prestat' : fields.char('Correspondant', size=150),
		'responsable_prestat' : fields.char('Responsable', size=150),
		'capital' : fields.integer('capital'),
		'code_territoire': fields.many2one('mcisogem.territoire', "Térritoire", required=True),
		'code_commune': fields.many2one('mcisogem.commune', "Commune"),
		'numero_ordre_prestat' : fields.char('Numero ordre', size=30),
		'code_journal' : fields.char('code_journal', size=20),
		'compta_prestat_tiers' : fields.char('Compte tiers', size=50),
		'privilege' : fields.selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')], 'Privilège'),
		'activer' : fields.boolean('Activé'),
		'autre_ordre_prestat' : fields.char('Autre ordre', size=100),
		'view': fields.boolean('')

	}

	_sql_constraints = [('unique_prestataire', 'unique(libelle_court_prestat)', "Ce Prestataire existe déjà !"), ]

	_defaults = {
		'pc_gratuit_prestat': 0,
		'capital': 0,
		'view': False
	}
	_rec_name = 'libelle_court_prestat'


	def onchange_code_ville_prestat(self, cr, uid, ids, code_ville, context=None):
			return {'value': {'code_commune' : False}}
	
	def onchange_regl_centre_prestat(self, cr, uid, ids, nom, context=None):
		if not nom:
			return {'value': {'autre_ordre_prestat' : False}}
		if nom:
			return {'value': {'autre_ordre_prestat' : nom}}

	
	
	def create(self, cr, uid, vals, context=None):
		specialite_data = self.pool.get('mcisogem.spec.med').browse(cr, uid, vals['code_specialite'], context=context)
		vals['nom_prestat'] = specialite_data.name
		vals['view'] = True
		# cr.execute("update mcisogem_plage_centre set dernier_numero=%s where id=%s", (dernier_num, plage_centre_data.id))
		return super(mcisogem_prestat, self).create(cr, uid, vals, context=context)
mcisogem_prestat()


class mcisogem_praticien(osv.osv):
	_name = "mcisogem.praticien"
	_inherit = ['ir.needaction_mixin']
	_description = 'Praticien'

	def button_to_done(self, cr, uid, ids, data, context=None):
		table = self.search(cr, uid, [('id', '=', ids)])
		table_obj = self.browse(cr, uid, table, context=context)
		if not table_obj.cpta_prestat or not table_obj.compta_prestat_tiers or not table_obj.mode_paiement_prestat or not table_obj.cle_rib_prestat or not table_obj.numero_guichet_prestat or not table_obj.numero_compte_prestat or not table_obj.numero_banque_prestat:
			e_mess = "Veuillez renseigner les informations comptable avant la validation"
			raise osv.except_osv(_('Attention !'), _(e_mess))
		else:
			self.write(cr, uid, ids, {'state' : 'finish'}, context=context)
		return True

	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "RESPONSABLE COMPTABLE" or group_obj.name == "UTILISATEUR COMPTABLE":
					return [('state', '=', 'done')]
			return False
		else:
			return False
	
	_columns = {
		'libelle_court_prestat': fields.char('Libellé court', readonly=True),
		'code_specialite': fields.many2one('mcisogem.spec.med', "Spécialité", required=True),
		'nom_prestat': fields.char('Nom', size=100, required=True),
		'prenoms_prestat': fields.char('Prenoms', size=100, required=True),
		'adresse_prestat': fields.char('Adresse', size=60),
		'nom_prenoms_prestat': fields.char('Nom & prénoms'),
		'code_bp_prestat': fields.char('Code postale', size=20),
		'bp_prestat': fields.char('Boite postale', size=20),
		'tel1_prestat': fields.char('Téléphone 1'),
		'tel2_prestat': fields.char('Téléphone 2', size=20),
		'pc_gratuit_prestat': fields.char('pc_gratuit_prestat', size=20),
		'observation_prestat': fields.text('Observation', size=60),
		'regl_centre_prestat' : fields.selection([('C', 'Centre'), ('P', 'Prestataire'), ('A', 'Autre ordre')], 'Paiement à l\'ordre de '),
		'mode_paiement_prestat' : fields.selection([('LC', 'Chèque'), ('ES', 'Espèce'), ('VI', 'Virement bancaire'), ('AU', 'Autre')], 'Mode de paiement'),
		'numero_banque_prestat': fields.char('No banque', size=20),
		'numero_guichet_prestat': fields.char('No guichet', size=20),
		'numero_compte_prestat': fields.char('No Compte', size=20),
		'cle_rib_prestat': fields.char('Clé rib', size=20),
		'cpta_prestat': fields.char('Compte général', size=20),
		'code_sup' : fields.char('cod_sup', size=1),
		'email_prestat' : fields.char('Email', size=50),
		'correspondant_prestat' : fields.char('Correspondant', size=150),
		'responsable_prestat' : fields.char('Responsable', size=150),
		'capital' : fields.integer('capital'),
		'code_commune': fields.many2one('mcisogem.commune', "Commune"),
		'numero_ordre_prestat' : fields.char('Numero ordre', size=30),
		'code_journal' : fields.char('code_journal', size=20),
		'compta_prestat_tiers' : fields.char('Compte tiers', size=50),
		'privilege' : fields.selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')], 'Privilège'),
		'activer' : fields.boolean('Actif'),
		'autre_ordre_prestat' : fields.char('Autre ordre', size=100),
		'view': fields.boolean(''),
		'paiement_ordre' : fields.char('Paiement à l\'ordre'),
		'show_chp': fields.boolean(''),
		'code_externe' : fields.char('Code externe'),
		'state': fields.selection([
			('draft', "Nouveau"),
			('sent', "Comptabilité"),
			('done', "Informations Comptable"),
			('cancel', "Annuler"),
			('finish', "Terminer"),
		], 'Status', required=True, readonly=True)
	}

	_defaults = {
		'pc_gratuit_prestat': 0,
		'capital': 0,
		'state': 'draft',
		'view': False
	}
	
	_sql_constraints = [('unique_prestataire', 'unique(libelle_court_prestat,nom_prestat,prenoms_prestat)', "Ce Prestataire existe déjà !"), ]

	_rec_name = 'libelle_court_prestat'

	def onchange_code_ville_praticien(self, cr, uid, ids, code_ville, context=None):
			return {'value': {'code_commune' : False}}
	
	def create(self, cr, uid, vals, context=None):
		vals['view'] = True
		vals['state'] = 'done'
		
		vals['nom_prestat'] = (vals['nom_prestat']).upper()
		vals['prenoms_prestat'] = (vals['prenoms_prestat']).upper()
		vals['nom_prenoms_prestat'] = vals['nom_prestat'] + " " + vals['prenoms_prestat']
		rep = super(mcisogem_praticien, self).create(cr, uid, vals, context=context)
		praticien = self.pool.get('mcisogem.praticien').search(cr,uid,[('id' , '=' , rep)])
		praticien_data = self.pool.get('mcisogem.praticien').browse(cr, uid, praticien)

		# NOM ET PRENOM

		nom = praticien_data.nom_prestat
		prenom = praticien_data.prenoms_prestat
		# SPECIALITE

		spe = praticien_data.code_specialite.libelle_court_spec
		# CODE CENTRE DE GESTION

		cr.execute('select code_centre from mcisogem_centre_gestion')
		cg_code = cr.fetchone()[0]

		# PAYS CENTRE DE GESTION

		centre_gestion_ids = self.pool.get('mcisogem.centre.gestion').search(cr,uid,[('code_centre' , '=' , cg_code)])
		centre_gestions = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, centre_gestion_ids)
		code_pays = centre_gestions.pays_id.code_pays

		
		if len(str(rep)) == 4:
			increment = "" + str(rep)
		elif len(str(rep)) == 3:
			increment = "0" + str(rep)
		elif len(str(rep)) == 2:
			increment = "00" + str(rep)
		elif len(str(rep)) == 1:
			increment = "000" + str(rep)
		else:
			increment = str(rep)

		# code = cg_code[0:2] + spe[0:2] + nom[0:1] + prenom[0:1] + increment
		code = code_pays[0:2] + cg_code[0:2] + spe[0:2] + nom[0:1] + prenom[0:1] + increment
		self.pool.get('mcisogem.praticien').write(cr,uid,rep,{'libelle_court_prestat':code},context=context)

		return rep


class mcisogem_type_aff(osv.osv):
	_name = "mcisogem.type.aff"
	_description = 'Type affection'
	
	_columns = {
		'code_type_affection': fields.integer('Code famille', required=True),
		'libelle_court_affection': fields.char('Libellé court', size=10, required=True),
		'name': fields.char('Libellé', size=30, required=True),
		'code_sup' : fields.char('cod_sup', size=1),
	}

	_sql_constraints = [('unique_type_aff', 'unique(name)', "Ce type d'affection existe déjà !"), ]
	
	
	
mcisogem_type_aff()

class mcisogem_affec(osv.osv):
	_name = "mcisogem.affec"
	_description = 'Affection'
	
	_columns = {
		'sous_chapitre_id': fields.many2one('mcisogem.sous.chapitre.affection', "Sous Chapitre", required=True),
		'lbc_affection': fields.char('Libellé', size=100, required=True),
		'code_affection': fields.char('Code', size=30, required=True),
		'activer' : fields.boolean('Actif'),
		'view': fields.boolean('')
	}
	
	_defaults = {
		'activer' : True,
		'view': False
	}


	_sql_constraints = [('unique_aff', 'unique(name)', "Cette affection existe déjà !"), ]


	_rec_name = 'lbc_affection'

	def create(self, cr, uid, vals, context=None):
		vals['view'] = True
		vals['lbc_affection'] = (vals['lbc_affection']).upper()
		vals['code_affection'] = (vals['code_affection']).upper()
		return super(mcisogem_affec, self).create(cr, uid, vals, context=context)



class mcisogem_liste_dent(osv.osv):
	_name = "mcisogem.liste.dent"
	_description = 'Liste dents'
	
	_columns = {
		'prestation_id' : fields.many2one('mcisogem.prestation'),
		'name': fields.integer('Numéro de dent', required=True),
		'enf_ad' : fields.selection([('ADULTE', 'Adulte'), ('ENFANT', 'Enfant')], 'Nature', required=True),
		'machoire': fields.selection([('MACHOIRE SUPERIEURE', 'Machoire supérieure'), ('MACHOIRE INFERIEURE', 'Machoire inférieure')], 'Machoire', required=True),
		'semi_arcade' : fields.selection([('SEMI-ARCADE INFERIEURE GAUCHE', 'Semi-arcade inférieure gauche'), ('SEMI-ARCADE SUPERIEURE GAUCHE', 'Semi-arcade supérieure gauche'), ('SEMI-ARCADE INFERIEURE DROITE', 'Semi-arcade inférieure droite'), ('SEMI-ARCADE SUPERIEURE DROITE', 'Semi-arcade supérieure droite')], 'Semi-arcade', required=True),
		'type_dent' : fields.selection([('INCISIVES', 'Incisives'), ('CANINES', 'Canines'), ('PREMOLAIRES', 'Prémolaires'), ('MOLAIRES', 'Molaires'), ('DENTS DE SAGESSE', 'Dents de sagesse')], 'Types de dent', required=True)
	}
	
mcisogem_liste_dent()


class mcisogem_acte_absence_dents(osv.osv):
	_name = "mcisogem.acte.absence.dents"
	_description = 'Acte d\'extraction de dents'
	_columns = {
		'libelle_court_acte': fields.char('Libellé court', size=10, required=True),
		'name': fields.char('Libellé', size=150, required=True),
		'code_ext_dent' : fields.boolean('Code d\'extraction')
}
	
mcisogem_acte_absence_dents()


class mcisogem_sous_actes(osv.osv):
	_name = "mcisogem.sous.actes"
	_description = 'Sous Actes'
	_columns = {
		'libelle_court_sous_acte': fields.char('Libellé court', size=20, required=True),
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", required=True),
		'code_famille_acte': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
		'name': fields.char('Libellé', size=100, required=True),
		'cout_unit_nomen': fields.integer('cout_unit_nomen'),
		'mtt_lc_carmed': fields.integer('mtt_lc_carmed'),
		'mtt_lc_hors_carmed': fields.integer('mtt_lc_hors_carmed'),
		'ratio_th_nomen': fields.integer('ratio_th_nomen'),
		'bl_nomen_envig': fields.boolean('Soumis à entente préalable ?'),
		'l_cle_nomen': fields.char('Lettre clé', size=5),
		'observation_nomen': fields.text('Observation'),
		'plf_prest_dft': fields.integer('plf_prest_dft'),
		'ticm_dft': fields.integer('ticm_dft'),
		'bl_ticm_tx_dft': fields.integer('bl_ticm_tx_dft'),
		'prest_espece_dft': fields.integer('prest_espece_dft'),
		'plf_an_prest_dft': fields.integer('plf_an_prest_dft'),
		'max_act_an_dft': fields.integer('max_act_an_dft'),
		'qte_cg': fields.integer('Coefficient'),
		'code_sup' : fields.char('cod_sup', size=1),
		'view' : fields.boolean('')
	}
	
	_sql_constraints = [('unique_sous_acte', 'unique(name)', "Ce sous acte existe déjà !"), ]

	_defaults = {
		'view': False
	}

	def create(self, cr, uid, vals, context=None):
		vals['view'] = True
		return super(mcisogem_sous_actes, self).create(cr, uid, vals, context=context)
	
mcisogem_sous_actes()

class mcisogem_sous_actes_centre(osv.osv):
	_name = "mcisogem.sous.actes.centre"
	_description = 'Sous Actes Centre'
	_columns = {
		'code_centre': fields.many2one('mcisogem.centre', 'Centre', required=True),
		'code_sous_acte': fields.many2one('mcisogem.sous.actes', 'Sous actes', required=True),
		'lbc_sous_acte_interne' : fields.char('Libellé court sous acte interne', size=10, required=True),
		'code_acte': fields.many2one('mcisogem.nomen.prest', 'Actes', required=True),
		'code_fam_prest': fields.many2one('mcisogem.fam.prest', 'Famille d\'acte', required=True),
		'lb_nomen_prest' : fields.char('Libellé acte', size=100, required=True),
		'l_cle_nomen': fields.char('l_cle_nomen', size=3, required=False),
		'mnt_sous_acte': fields.integer('Montant', required=False),
		'sous_acte_autorise': fields.integer('sous_acte_autorise', required=False),
		'dt_deb_souacte': fields.date('Date d\'effet', required=True),
		'dt_fin_souacte': fields.date('15Date de résiliation', required=True),
		'qte_cg' : fields.char('qte_cg', size=50, required=False),
	}
mcisogem_sous_actes_centre()


class mcisogem_default_acte_temp(osv.osv):
	_name = "mcisogem.default.acte.temp"
	_description = 'Actes par defaut des tarifs de convention'

	_columns = {
	
		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte", readonly=True),
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", readonly=True),
		'lettre_cle': fields.char('', readonly=True),
		'code_convention': fields.many2one('mcisogem.convention.unique', "Convention"),
		'montant_brut_tarif': fields.integer('Plafond', required=False),
	
	}

mcisogem_default_acte_temp()


class mcisogem_tarif_convention_med_temp(osv.osv):
	_name = "mcisogem.tarif.convention.med.temp"
	_description = 'Tarif convention medicament Temp'
	_columns = {
		'code_medicament' : fields.char('Code'),
		'medicament_id': fields.many2one('mcisogem.medicament', "Médicament"),
		'presentation_id': fields.many2one('mcisogem.presentation', "Présentation"),
		'dci_id': fields.many2one('mcisogem.dci', "DCI"),
		'montant_brut_tarif': fields.integer('Montant brut'),
}



class mcisogem_tarif_convention(osv.osv):
	_name = "mcisogem.tarif.convention"
	_description = 'Tarif convention'
	_columns = {
		'code_convention': fields.many2one('mcisogem.convention.unique', "Convention", required=True),

		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte"),
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", required=False),
		'medicament_id': fields.many2one('mcisogem.medicament', "Médicament", required=False),


		'montant_brut_tarif': fields.integer('Montant brut tarif'),

		'montant_plafond_tarif': fields.integer('Plafond', readonly=True),

		'date_effet_tarif': fields.date("Date d'effet", required=True),

		'date_resiliation_tarif': fields.date("Date de résiliation", readonly=True),

		'cod_res_conv': fields.integer('cod_res_conv'),

		'code_sup' : fields.char('cod_sup', size=1),

		'affichage' : fields.integer('affichage', required=False),


		'code_tarif_convention_temp': fields.many2many('mcisogem.tarif.convention.temp',
									   'mcisogem_convention_temp_rel',
										'convention_temp_id',
										'code_convention',
										'Actes', required=False),

		'code_tarif_convention_med_temp': fields.many2many('mcisogem.tarif.convention.med.temp',
									   'mcisogem_convention_med_temp_rel',
										'convention_temp_id',
										'code_convention',
										'Médicaments', required=False),

		
		'type_plafond' : fields.selection([
			('acte', "Acte"),
			('med', "Médicaments"),
		], 'Type tarif') ,


		'state': fields.selection([
			('draft', "Actif"),
			('resil', "Résilier"),
		], 'Statut', readonly=True)
	}
	
	_defaults = {
		'affichage': 0  ,
		'date_resiliation_tarif' : '1900-01-01',
		'state': 'draft' , 
		'type_plafond' : 'acte',
	}


	def onchange_acte(self, cr, uid, ids, code_acte, context=None):

		if code_acte:

			cr.execute('delete from mcisogem_tarif_convention_med_temp where create_uid = %s' , (uid , ))

			med_ids = self.pool.get('mcisogem.medicament').search(cr,uid,[('acte_id' , '=' , code_acte)])

			for med_id in med_ids:
				med = self.pool.get('mcisogem.medicament').browse(cr,uid,med_id)

				cr.execute('insert into mcisogem_tarif_convention_med_temp(code_medicament , medicament_id ,dci_id , presentation_id ,  montant_brut_tarif , create_uid) values(%s , %s , %s , %s , %s , %s)'  , (med.code_medicament , med.id , med.dci_id.id , med.presentation_id.id ,  0 , uid,))


	_rec_name = 'code_convention'    

	_sql_constraints = [('unique_tarif_convention', 'unique(code_acte,code_convention,state,type_tarif)', "Ce tarif convention existe déjà !"), ]


	def onchange_code_famille_tarif_convention(self, cr, uid, ids, code_famille, context=None):
		
		# Avant tout on vide la table temporaire des tarifs
		# Vidage des tables temporaires
		cr.execute("delete from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
		if not code_famille:
			return {'value': {'code_tarif_convention_temp': False}}
		if code_famille:
			data = []
			# Recuperation de la liste de tous les actes de la famille
			# cr.execute("select * from mcisogem_nomen_prest where code_fam_prest=%s and libelle_court_acte not in %s and l_cle_nomen not in %s order by name asc", (code_famille,('AMI','FHHM'),('B','Z','KC','KE')))
			
			cr.execute("select * from mcisogem_nomen_prest where code_fam_prest=%s order by name asc", (code_famille , ))
			lesactes = cr.dictfetchall()
			if len(lesactes) > 0:
				# Insertion de la liste des actes dans la table mcisogem_tarif_convention_temp
				# Parcours de la liste et enregistrement des données en base
				for acte in lesactes:
					cr.execute("insert into mcisogem_tarif_convention_temp (create_uid,code_famille,code_acte,montant_brut_tarif,plafond_tarif, write_uid) values(%s, %s, %s, %s, %s, %s)", (uid, code_famille, acte['id'], 0,0,uid))
					cr.execute("select * from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
					lestarifstemp = cr.dictfetchall()
					for tarif in lestarifstemp:
						data.append(tarif['id'])
				return{'value': {'code_tarif_convention_temp': data}}
			else:
				return {'value': {'code_tarif_convention_temp': False}}




	def button_resilier_tarif_convention(self, cr, uid, ids, context=None):

		tarif_convention = self.browse(cr, uid, ids[0], context=context).id
		tarif_convention_table = self.search(cr, uid, [('id', '=', tarif_convention)])

		tarif_convention_data = self.browse(cr, uid, tarif_convention_table)
		
		ctx = (context or {}).copy()
		ctx['id'] = tarif_convention
		ctx['date_effet_tarif'] = tarif_convention_data.date_effet_tarif
		ctx['form_view_ref'] = 'view_mcisogem_tarif_convention_resilier_form'
		
		return {
		  'name':'Resiliation tarif de convention',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.resil.tarif.convention',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}

	def button_to_reactive(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'draft', 'date_resiliation_tarif':'1900-01-01', 'date_effet_tarif': time.strftime('%d-%m-%y', time.localtime())}, context=context)
	
	def create(self, cr, uid, vals, context=None):
		

		dernier_id = 0
		# Recuperation de la date du jour
		datedujour = time.strftime('%d-%m-%y %H:%M:%S', time.localtime())
		

		plafond = 0

		if vals['type_plafond'] == 'acte':

			for dt in vals['code_tarif_convention_temp'][0][2]:

				acte = self.pool.get('mcisogem.tarif.convention.temp').browse(cr,uid,dt)

				data = {}
				data['create_uid'] = uid      
				data['code_convention'] = vals['code_convention']  
				data['cod_res_conv'] = 0      
				data['code_acte'] = acte.code_acte.id   
				data['code_famille'] = acte.code_famille.id      
				data['date_effet_tarif'] = vals['date_effet_tarif']      
				data['write_uid'] = uid      
				data['montant_brut_tarif'] = acte.montant_brut_tarif 
				data['montant_plafond_tarif'] = plafond       
				data['write_date'] = datedujour      
				data['create_date'] = datedujour     
				data['date_resiliation_tarif'] = '1900-01-01'    
				data['affichage'] = 1


				sch = self.pool.get('mcisogem.tarif.convention').search(cr,uid,[('code_convention' , '=' , vals['code_convention']) , ('code_acte' , '=' , acte.code_acte.id)])
				
				if sch:
					raise osv.except_osv('Attention' , "Certains éléments que vous essayez de créer existent déjà !")

				dernier_id = super(mcisogem_tarif_convention, self).create(cr, uid, data, context=context)

			cr.execute("delete from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
			return dernier_id
			


	def write(self, cr, uid, ids, vals, context=None):
		return super(mcisogem_tarif_convention, self).write(cr, uid, ids, vals, context=context)


class mcisogem_prestation_medicament(osv.osv):
	_name = 'mcisogem.prestation.medicament'
	_columns = {
		'acte_id' : fields.many2one('mcisogem.nomen.prest' , 'Famille'),
		'code_medicament':fields.integer('Code'),
		'name' : fields.char('Libelle'),
		'ordo_ids':fields.one2many('mcisogem.prestation.ordornance','medicament_ids','Ordornance'),
	}

class mcisogem_resil_tarif_convention(osv.osv):
	_name = "mcisogem.resil.tarif.convention"
	_description = "Historique de resiliation de tarif convention"

	_columns = {
		'convention_id': fields.many2one('mcisogem.convention', 'Convention'),
		'date_effet_tarif': fields.date('Date d\'éffet'),
		'date_resiliation_tarif': fields.date('Date de résiliation')
	}

	_rec_name =  'convention_id'

	def create(self,cr,uid,vals,context=None):
		vals['id'] = context.get('id')
		vals['date_effet_tarif'] = context.get('date_effet_tarif')
		vals['convention_id'] = context.get('id')
			
		tarif_convention = self.pool.get('mcisogem.tarif.convention').search(cr,uid,[('id' , '=' , context.get('id'))])
		tarif_convention_data = self.pool.get('mcisogem.tarif.convention').browse(cr, uid, tarif_convention)

		if vals['date_resiliation_tarif'] != '1900-01-01' and vals['date_resiliation_tarif'] < vals['date_effet_tarif']:
			raise osv.except_osv('Attention !', "La date de résiliation ne doit pas être inférieure à la date d'éffet de la convention !")
		else:
			self.pool.get('mcisogem.tarif.convention').write(cr,uid,tarif_convention_data.ids,{'state':'resil' ,'date_resiliation_tarif':vals['date_resiliation_tarif']},context=context)
			return super(mcisogem_resil_tarif_convention , self).create(cr,uid,vals,context)


class mcisogem_tarif_convention_centre_temp(osv.osv):
	_name = "mcisogem.tarif.convention.centre.temp"
	_description = 'Tarif convention Centre Temp'
	_columns = {
		'choix': fields.boolean('Choix'),
		'code_centre': fields.many2one('mcisogem.centre', "Centre", readonly=True),
		'libelle_court_centre': fields.char('Code Centre', readonly=True),
}
	
mcisogem_tarif_convention_centre_temp()


class mcisogem_tarif_convention_centre(osv.osv):
	_name = "mcisogem.tarif.convention.centre"
	_description = 'Tarif convention centre'
	_columns = {
		'code_convention': fields.many2one('mcisogem.convention', "Convention", required=False),
		'code_centre': fields.many2one('mcisogem.centre', "Centre", required=False),
		'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d\'acte", required=False),
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", required=False),
		'montant_brut_tarif': fields.integer('Montant brut tarif', required=False),
		'montant_plafond_tarif': fields.integer('Montant brut tarif', required=False),
		'date_effet_tarif': fields.datetime("Date d'effet", required=True),
		'date_resiliation_tarif': fields.datetime("Date de résiliation"),
		'cod_res_conv': fields.integer('cod_res_conv'),
		'code_sup' : fields.char('cod_sup', size=1),
		'affichage' : fields.integer('affichage', required=False),
		'affichage_tab_centre' : fields.integer('affichage_tab_centre', required=False),
		'affichage_tab_acte' : fields.integer('affichage_tab_acte', required=False),
		'affichage_famille' : fields.integer('affichage_famille', required=False),
		'affichage_convention' : fields.integer('affichage_convention', required=False),
		'affichage_centre' : fields.integer('affichage_convention', required=False),
		'actions': fields.selection([('1', 'Association Centre - Convention'), ('2', 'Ajouter ou remplacer un acte dans la convention d\'un centre')], 'Quelle action souhaitez-vous mener ?'),
		'code_tarif_convention_temp': fields.many2many('mcisogem.tarif.convention.temp',
									   'mcisogem_convention_acte_temp_rel',
										'convention_acte_temp_id',
										'code_convention_acte_temp',
										'Choix des actes', required=False),
		'code_tarif_convention_centre_temp': fields.many2many('mcisogem.tarif.convention.centre.temp',
									   'mcisogem_convention_centre_temp_rel',
										'convention_centre_temp_id',
										'code_convention_centre_temp',
										'Choix des centres', required=False),
}
	
	_defaults = {
			  'affichage_tab_centre':0,
			  'affichage_tab_acte':0,
			  'affichage_convention':0,
			  'affichage_famille':0,
			  'affichage_centre':0,
			  'affichage':0,
			  'date_resiliation_tarif' :'1900-01-01 00:00:00',
}    

	_sql_constraints = [('unique_tarif_convention_centre', 'unique(code_acte,code_centre,date_effet_tarif,cod_res_conv)', "Ce tarif centre existe déjà !"), ]


	def onchange_actions(self, cr, uid, ids, actions, context=None):
		
		if not actions:
			return {'value' : {'actions' :  False}}
		else:
			data = []
			if actions == '1':
				 # Recuperation de la liste des centre qui n'ont pas de convention
				# vidage de la table temporaire
				cr.execute("delete from mcisogem_tarif_convention_centre_temp where write_uid=%s", (uid,))
				# Recuperation de la liste de tous les centres
				cr.execute("select * from mcisogem_centre order by name")
				lescentres = cr.dictfetchall()
				if len(lescentres) > 0:
				   # Parcours des centres et insertion des données dans la table temporaire
				   for centre in lescentres:
						cr.execute("""insert into mcisogem_tarif_convention_centre_temp (create_uid,choix,code_centre,libelle_court_centre,write_uid)
						values(%s,%s,%s,%s,%s)""", (uid, False, centre['id'], centre['code_centre'], uid))
				   # Recuperation des centres enregistrés en base temporaires
				   cr.execute('select * from mcisogem_tarif_convention_centre_temp where write_uid=%s', (uid,))
				   lescentrestemp = cr.dictfetchall()
				   for ctemp in lescentrestemp:
					   data.append(ctemp['id'])
				   return {'value': {'code_tarif_convention_centre_temp': data, 'affichage_tab_centre': 1, 'affichage_tab_acte': 0,
								   'affichage_convention':1, 'affichage_centre': 0, 'affichage_famille' : 0  }}
				else:
					raise osv.except_osv('Attention !', "Veuillez enregistrer au moins un centre !")
					return {'value': {'affichage_tab_centre': 1, 'affichage_tab_acte': 0}}
			else:
				cr.execute("delete from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
				return {'value': {'affichage_tab_centre': 0, 'affichage_tab_acte': 1, 'code_tarif_convention_temp': [], 'code_famille': False,
								  'affichage_convention' :0, 'affichage_famille':1, 'affichage_centre' : 1}}
	

	def onchange_code_famille(self, cr, uid, ids, code_famille, context=None):

		# Avant tout on vide la table temporaire des tarifs
		# Vidage des tables temporaires
		cr.execute("delete from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
		
		if not code_famille:
			return {'value': {'code_tarif_convention_temp': False}}
		if code_famille:
			data = []
			# Recuperation de la liste de tous les actes de la famille
			cr.execute("select * from mcisogem_nomen_prest where code_fam_prest=%s", (code_famille,))
			lesactes = cr.dictfetchall()
			if len(lesactes) > 0:
			   # Insertion de la liste des actes dans la table mcisogem_tarif_convention_temp
			   # Parcours de la liste et enregistrement des données en base
			   for acte in lesactes:
				   cr.execute("insert into mcisogem_tarif_convention_temp (create_uid,choix,code_famille,code_acte,montant_brut_tarif, write_uid) values(%s, %s, %s, %s, %s, %s)", (uid, False, code_famille, acte['id'], 0, uid))
			   cr.execute("select * from mcisogem_tarif_convention_temp where write_uid=%s", (uid,))
			   lestarifstemp = cr.dictfetchall()
			   for tarif in lestarifstemp:
					data.append(tarif['id'])
			   return{'value': {'code_tarif_convention_temp': data}}
			else:
				raise osv.except_osv('Attention !', "Cette famille ne comporte aucun acte !")
				return {'value': {'code_tarif_convention_temp': False}}

			
	def create(self, cr, uid, vals, context=None):
		
		if not vals['date_resiliation_tarif']:
			vals['date_resiliation_tarif'] = '1900-01-01 00:00:00'
		
		# Recuperation de la date du jour
		dernier_id = 0
		datedujour = time.strftime('%d-%m-%y %H:%M:%S', time.localtime())
		print'------------------------'
		print datedujour
		
		if not vals['actions']:
			raise osv.except_osv('Attention !', "Veuillez sélectionner une action !")
			return False
		else:
			utilisateur_data = self.pool.get('res.users').browse(cr, uid, uid, context=context)
			centre_gestion_data = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, utilisateur_data.code_gest_id.id, context=context)
			
			# Cas ou actions = 1 - Association centre - convention
			if vals['actions'] == '1':
				# Test pour voir s'il a bien sélectionné une convention
				if not vals['code_convention']:
					raise osv.except_osv('Attention !', "Veuillez sélectionner une convention !")
					return False
				else:
					# Recuperation de la liste des centres sélectionnés
					cr.execute('select * from mcisogem_tarif_convention_centre_temp where write_uid=%s and choix=%s', (uid, True))
					lescentreselect = cr.dictfetchall()
					if len(lescentreselect) > 0:
						# Parcours de la liste des centres sélectionnés
						for cs in lescentreselect:
							cr.execute('select * from mcisogem_tarif_convention_centre where code_convention=%s and code_centre=%s', (vals['code_convention'], cs['code_centre']))
							verifcentreconventionnes = cr.dictfetchall()
							# Test le contenu du dictionnaire pour voir si le centre possède déjà une convention si oui on la desactive
							if len(verifcentreconventionnes) > 0:
								for cc in verifcentreconventionnes:
									cr.execute('update mcisogem_tarif_convention_centre set date_resiliation_tarif=%s, cod_res_conv=%s where id=%s', (datedujour, 1, cc['id']))
								# Recuperation de la liste de tous les actes de la convention dont cod_res_conv est = 0
						cr.execute('select * from mcisogem_tarif_convention where code_convention=%s and cod_res_conv=%s', (vals['code_convention'], 0))
						lesactestarifs = cr.dictfetchall()
						
								# Test pour voir si il existe des actes pour cette convention
						if len(lesactestarifs) > 0:
							# Parcours de la liste des centres et enregistrement des actes pour le centre
							for cent in lescentreselect:
								# Pour chaque centre on va inserer les données relatives au cout des actes
								# Parcours des actes tarifs
								for at in lesactestarifs:
									 data = {}
									 data['code_convention'] = vals['code_convention']
									 data['code_centre'] = cent['code_centre']
									 data['code_acte'] = at['code_acte']
									 data['montant_brut_tarif'] = at['montant_brut_tarif']
									 data['date_effet_tarif'] = vals['date_effet_tarif']
									 data['date_resiliation_tarif'] = vals['date_resiliation_tarif']
									 data['cod_res_conv'] = 0
									 data['affichage'] = 3
									 data['affichage_convention'] = 1
									 data['affichage_centre'] = 1
									 data['affichage_famille'] = 0
									 data['affichage_tab_centre'] = 0
									 data['affichage_tab_acte'] = 0
									 dernier_id = super(mcisogem_tarif_convention_centre, self).create(cr, uid, data, context=context)
							return dernier_id
						else:
							raise osv.except_osv('Attention !', "Cette convention ne comporte aucun acte !")
							return False
							
					else:
						raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un centre !")
						return False  
						
			else: 
				# Cas ajout ou remplacement d'un acte
				
				# Tentative de recuperation de la convention du centre
				conv_tarif_centre = {}
				cr.execute('select * from mcisogem_tarif_convention_centre where code_centre=%s and cod_res_conv=%s order by id desc', (vals['code_centre'], 0))
				laconventioncentre = cr.dictfetchall()
				if len(laconventioncentre) > 0:
					conv_tarif_centre = laconventioncentre[0]
					vals['code_convention'] = conv_tarif_centre['code_convention']
					# Recuperation de tous les actes sélectionnés
					cr.execute('select * from mcisogem_tarif_convention_temp where write_uid=%s and choix=%s', (uid, True))
					lesactestarifs = cr.dictfetchall()
					if len(lesactestarifs) > 0:
						# Parcours des actes pour verification de leur présence ou non dans la liste des tarifs convention centre
						cr.execute('select * from mcisogem_tarif_convention_centre where code_convention=%s and cod_res_conv=%s and code_centre=%s', (vals['code_convention'], 0, conv_tarif_centre['code_centre']))
						lesactesconventionnes = cr.dictfetchall()
						
						# Si il existe des actes on doit les résilier avant de poursuivre
						if len(lesactesconventionnes) > 0:
							for cc in lesactesconventionnes:
								cr.execute('update mcisogem_tarif_convention_centre set date_resiliation_tarif=%s, cod_res_conv=%s where id=%s', (datedujour, 1, cc['id']))
						 
						print'----------------------------////*****'
						print lesactestarifs 
						for act in lesactestarifs:
							# Insertion de la nouvelle ligne en base de données
							data = {}
							data['code_convention'] = conv_tarif_centre['code_convention']
							data['code_centre'] = conv_tarif_centre['code_centre']
							data['code_acte'] = act['code_acte']
							data['montant_brut_tarif'] = act['montant_brut_tarif']
							data['date_effet_tarif'] = vals['date_effet_tarif']
							data['date_resiliation_tarif'] = vals['date_resiliation_tarif']
							data['cod_res_conv'] = 0
							data['affichage'] = 3
							data['affichage_convention'] = 1
							data['affichage_centre'] = 1
							data['affichage_famille'] = 0
							data['affichage_tab_centre'] = 0
							data['affichage_tab_acte'] = 0  # Récuperation de l'utilisateur
							dernier_id = super(mcisogem_tarif_convention_centre, self).create(cr, uid, data, context=context)
							 # Enregistrement des données en base
						return dernier_id
					else:
						raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un acte !")
						return False
				else:
					raise osv.except_osv('Attention !', "Aucune convention n'a été définit pour ce centre !")
					return False
				
	def write(self, cr, uid, ids, vals, context=None):
		if vals['date_resiliation_tarif'] == '1900-01-01 00:00:00':
			vals['cod_res_conv'] = 0
		else:
			vals['cod_res_conv'] = 1
		return super(mcisogem_tarif_convention_centre, self).write(cr, uid, ids, vals, context=context) 

mcisogem_tarif_convention_centre()





class mcisogem_acte_tarif(osv.osv):
	_name = 'mcisogem.acte.tarif'
	_columns = {
		'acte_id' : fields.many2one('mcisogem.nomen.prest' , 'Acte' , required=True),
		'tarif' : fields.integer('Montant brut' , required=True),
	}



class mcisogem_tarif_centre(osv.osv):
	_name = 'mcisogem.tarif.centre'
	_columns = {

		'convention_id' : fields.many2one('mcisogem.convention.unique' , 'Convention' , required=True),

		'centre_ids': fields.many2many('mcisogem.centre', 'mcisogem_tarif__centre_rel', 'id', 
			'code_centre', 'Centres' , required=True),

		'centre_id' : fields.many2one('mcisogem.centre' , 'Centre' , readonly=True),



		'acte_ids' : fields.many2many('mcisogem.acte.tarif', 'mcisogem_tarif__acte_rel', 'id', 'acte_id', 'Actes' , required=False),

		'famille_acte_id' : fields.many2one('mcisogem.fam.prest' , 'Famille'),

		'famille_acte_ids': fields.many2many('mcisogem.fam.prest', 'mcisogem_tarif__famille_rel', 'id', 
			'name', "Famille d'actes" , required=False),


		'acte_id' : fields.many2one('mcisogem.nomen.prest' , 'Acte' , readonly=True),

		'tarif' : fields.integer('Montant brut'),
		'dt_effet' : fields.date("Date d'effet"),
		'name' : fields.char(''),
	}


	_defaults = {
		'dt_effet': time.strftime("%Y-%m-%d", time.localtime()),
	}
	

	def onchange_famille(self, cr, uid,ids,famille_acte_ids,context=None):

		if famille_acte_ids:

			familles = famille_acte_ids[0][2]

			cr.execute('DELETE FROM mcisogem_acte_tarif WHERE create_uid = %s' , (uid , ))

			acte_ids = self.pool.get('mcisogem.nomen.prest').search(cr,uid,[('code_fam_prest' , 'in' , familles)])

			for acte in self.pool.get('mcisogem.nomen.prest').browse(cr,uid,acte_ids):
				cr.execute('INSERT INTO mcisogem_acte_tarif(acte_id , tarif , create_uid) VALUES(%s , %s , %s)' , (acte.id , 0 , uid))

			# Recuperation des actes temporaires enregistré en base
			cr. execute("select * from mcisogem_acte_tarif where create_uid=%s", (uid,))
			lesactestemp = cr.dictfetchall()

			tabacte = []
			for act in lesactestemp:
				tabacte.append(act['id'])

			return {'value' : {'acte_ids' : tabacte }}


	def create(self, cr, uid, data, context=None):
		

		last_id = False

		centres = data['centre_ids'][0][2]
		actes = data['acte_ids'][0][2]
		vals = {}
		
		if len(centres) == 0:
			raise osv.except_osv(_('Attention'), _('Veuillez choisir au moins un centre.'))

		if len(actes)==0:
			raise osv.except_osv(_('Attention'), _('Veuillez choisir au moins un acte.'))


		for centre in centres:

			for acte in actes:

				acte_data = self.pool.get('mcisogem.acte.tarif').browse(cr,uid,acte)

				conv_srch = self.pool.get('mcisogem.convention').search(cr,uid,[('code_conv' , '=' , data['convention_id']) , ('code_acte' , '=' , acte_data.acte_id.id)])


				# if not conv_srch:
				# 	raise osv.except_osv('Attention !' , "Aucune convention n'a été trouvée pour un ou plusieurs actes.")


					
				conv_data = self.pool.get('mcisogem.convention').browse(cr,uid,conv_srch)


				srch = self.pool.get('mcisogem.tarif.centre').search(cr,uid,[('acte_id' , '=' , acte_data.acte_id.id) , ('centre_id' , '=' , centre)])

				if srch:
					raise osv.except_osv('Attention !' , 'Certains éléments que vous essayez de créer existent déjà.')



				data['tarif']  = acte_data.tarif
				data['acte_id'] = acte_data.acte_id.id
				data['centre_id'] = centre
				data['name'] = self.pool.get('mcisogem.centre').browse(cr,uid,centre).name + "-" +  acte_data.acte_id.name


				if conv_srch:
					if data['tarif'] > conv_data.montant_plafond_tarif:
						raise osv.except_osv('Attention !' , 'Le montant défini est supérieur à celui fixé dans le tarif de convention.')

				last_id = super(mcisogem_tarif_centre, self).create(cr, uid, data, context=context)

		vals['convention_id']  = data['convention_id']
		vals['centre_ids']  = data['centre_ids']
		self.pool.get('mcisogem.rata.convention').create(cr, uid, vals, context=context)

		return last_id