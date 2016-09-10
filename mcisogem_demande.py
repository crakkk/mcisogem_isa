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

class hr_mci_notification_user(osv.osv):    
	_name = "hr.mci.notification.user"

	_columns = {
		'user_id': fields.many2one('res.users', "Personne à notifier", required=True),
	}
	_rec_name = 'user_id'


class mcisogem_categoriep(osv.osv):
	_name = 'mcisogem.categoriep'
	_description = 'Categorie plainte'

	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			print('*******garant id********')
			print(garant.id)
			return garant.id
		else:
			return False

	def _get_centre_user(self, cr, uid, context=None):
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]
		if centre_user_id:
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
			print('***************************Centre*************************')
			print(centre.id)
			return centre.id
		else:
			return False

	_columns = {
		'garant_id' : fields.integer('Identifiant garant'),
		'id_centre' : fields.integer('Identifiant centre'),
		'name' :  fields.char('Categorie', required=True),
		# 'code' : fields.char('Code'),
		'objetp_id' : fields.one2many('mcisogem.objetp','categoriep_id','Objet plaine'),
		'plainte_id' : fields.one2many('mcisogem.plainte','categoriep_id','plainte'),
	}
	_defaults ={
		'garant_id':_get_garant,
		'id_centre':_get_centre_user

	}
	


class mcisogem_objetp(osv.osv):
	_name = 'mcisogem.objetp'
	_description = 'Objet de plainte'

	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			print('*******garant id********')
			print(garant.id)
			return garant.id
		else:
			return False

	def _get_centre_user(self, cr, uid, context=None):
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]
		if centre_user_id:
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
			print('***************************Centre*************************')
			print(centre.id)
			return centre.id
		else:
			return False
	_columns = {
		'garant_id' : fields.integer('Identifiant garant'),
		'id_centre' : fields.integer('Identifiant centre'),
		'name' : fields.char('Objet', required=True),
		'categoriep_id' : fields.many2one('mcisogem.categoriep','Categorie',ondelete="cascade",required=True),
		'plainte_id' : fields.one2many('mcisogem.plainte','objetp_id','plainte'),
	}
	_defaults ={
		'garant_id':_get_garant,
		'id_centre':_get_centre_user

	}


class mcisogem_plainte(osv.osv):
	_name = 'mcisogem.plainte'
	_description = 'Plaintes et suggestion'
	_inherit = ['mail.thread']

	_mail_post_access = 'read'

	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			print('*******garant id********')
			print(garant.id)
			return garant.id
		else:
			return False

	def _get_centre_user(self, cr, uid, context=None):
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]
		if centre_user_id:
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
			print('***************************Centre*************************')
			print(centre.id)
			return centre.id
		else:
			return False

	def _get_souscr_user(self, cr, uid, context=None):
		cr.execute('select souscr_id from res_users where id=%s', (uid,))
		souscr_user_id = cr.fetchone()[0]
		if souscr_user_id:
			souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, souscr_user_id, context=context)
			print('***************************souscripteur*************************')
			print(souscripteur.id)
			return souscripteur.id
		else:
			return False

	_columns = {
		'garant_id' : fields.integer('Identifiant garant'),
		'garant_ids' : fields.many2one('mcisogem.garant','garant'),
		'id_centre' : fields.integer('Identifiant centre'),
		'centre_ids' : fields.many2one('mcisogem.centre','centre'),
		'souscripteur' : fields.integer('Identifiant souscripteur'),
		'souscripteur_id' : fields.many2one('mcisogem.souscripteur','souscripteur'),
		'categoriep_id' : fields.many2one('mcisogem.categoriep','Categorie', ondelete="cascade",required=True),
		'objetp_id' : fields.many2one('mcisogem.objetp','Objet de la plainte', ondelete="cascade",required=True),
		'description' : fields.text('Description',required=True),
		'affi_objet' : fields.boolean(''),
	}
	_defaults ={
		'garant_id':_get_garant,
		'garant_ids':_get_garant,
		'id_centre':_get_centre_user,
		'centre_ids':_get_centre_user,
		'souscripteur':_get_souscr_user,
		'souscripteur_id':_get_souscr_user,
		'affi_objet' : False,
	}
	_rec_name = 'objetp_id'

	def onchange_cat(self,cr,uid,context,valeur):
		if valeur :
			v = {}
			v = {'affi_objet':True}
			return {'value' : v}




	def create(self, cr, uid, vals, context=None):

		########### envoi des notifications aux responsables médical pour une plainte et suggestion
		# msg = str("Une nouvelle plainte/suggestion vien d'être créer.Vous devez l'examiner pour validation")

		# cr.execute("select id from res_groups where name='RESPONSABLE MEDICAL'")
		# groupe_id = cr.fetchone()[0]

		# sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		# cr.execute(sql)
		# user_ids = cr.fetchall()

		# les_ids = []
		# for u_id in user_ids:
		# 	les_ids.append(u_id[0])

		# res_users = self.pool['res.users']
		# partner_ids = list(set(u.partner_id.id for u in res_users.browse(cr, uid, les_ids , context)))

		# self.message_post(
		# 	cr, uid, False,
		# 	body=msg ,
		# 	partner_ids=partner_ids,
		# 	subtype='mail.mt_comment',
		# 	subject="[MCI] - Validation Médical",
		# 	context=context
		# 	)

		###################################################

		body_mail = str("Une nouvelle plainte/suggestion vient d'être émise. Merci de l'examiner.")
		partner_ids = []
		user_ids = self.pool.get('hr.mci.notification.user').search(cr, uid, [])

		for us in self.pool.get('hr.mci.notification.user').browse(cr, uid, user_ids):
			if us.user_id.partner_id:
				partner_ids.append(us.user_id.partner_id.id)

		if partner_ids != []:
			self.message_post(
			cr, uid, False,
			body=body_mail,
			partner_ids=partner_ids,
			subtype='mail.mt_comment',
			subject="[ISA-WEB] - Plaintes et suggestions",
			context=context
		)



		return super(mcisogem_plainte,self).create(cr, uid, vals, context)

class mcisogem_centre_tempo(osv.osv):
	_name = 'mcisogem.centre.tempo'
	_columns = {
		'centre_id':fields.integer('Identifiant centre'),
		'name' : fields.char('Nom centre'),
	}	


class mcisogem_entente(osv.osv):
	_name = 'mcisogem.entente'
	_description = 'Demande entente prealable'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_mail_post_access = 'read'

	
	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)


	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			print('*******garant id********')
			print(garant.id)
			return garant.id
		else:
			return False

	def _get_centre_user(self, cr, uid, context=None):
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]
		if centre_user_id:
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
			print('***************************Centre*************************')
			print(centre.id)
			return centre.id
		else:
			return False

	def _get_utilisateur(self, cr,uid,context):
		
		return uid	

	_columns = {
		'user_id' : fields.integer('Identifiant Utilisateur'),
		'garant_id' : fields.integer('Identifiant Garant'),
		'garant_p_id' : fields.integer('mcisogem_garant','Garant'),
		'police_id' : fields.integer('Identifiant police beneficiaire'),
		'id_centre' : fields.integer('Identifiant centre'),
		'periode_id' : fields.many2one('mcisogem.account.period' , 'Periode'),
		'exercice_id' : fields.many2one('mcisogem.exercice' , 'Exercice'),
		'college_id' : fields.integer('Identifiant collège'),
		'beneficiaire_id' : fields.many2one('mcisogem.benef', 'Beneficiaire', ondelete="cascade"),
		'benef_test_id' : fields.char('Beneficiaire',required=True),
		'centre_id' : fields.many2one('mcisogem.centre','Centre executant'),
		# 'cent_id' : fields.many2one('mcisogem.centre.tempo','Centre executant'),
		'affection_id' : fields.many2one('mcisogem.affec', 'Affection', ondelete="cascade",required=True),
		# 'acteent_id' : fields.many2one('mcisogem.acte.entente.prealable', 'Acte', ondelete="cascade",required=True),
		'acteent_id' : fields.many2one('mcisogem.nomen.prest', 'Acte', domain=[('bl_nomen_envig','=',True)],required=True),
		's_acteent_id' : fields.many2many('mcisogem.sous.actes', 'pcharge_sacte_rel_2', 'id_pc', 'id_sa', 'Sous actes'),
		'motif' : fields.text('Motif',required=True),
		'motif_valider' : fields.text('Motif pour Validation'),
		'motif_rejet' : fields.text('Motif pour rejet'),
		'image': fields.binary("Image",
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.entente': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.entente': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		'state': fields.selection([
			('nouveau', "Nouveau"),
			('attente', "En attente"),
			('valide', "Acceptée"),
			('rejet', "Rejetée"),
			
		   
		], 'Status', required=True, readonly=True),
		'num_entente':fields.integer('Numero :'),
		
		'mail_benef': fields.char('Mail'),
		'nom_benef' : fields.char('Nom'),
		'prenom_benef' : fields.char('Prenoms'),
		'tel_benef' : fields.char('Telephone'),
		'affichebenef': fields.boolean(''),
		'affichdetail': fields.boolean(''),
		'affichsacte': fields.boolean(''),
	}
	_defaults ={
		'state': 'nouveau',
		'affichdetail': False,
		'affichebenef': False,
		'affichsacte': False,
		'user_id':_get_utilisateur,
	}
	_rec_name = 'beneficiaire_id'
	
	
	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "UTILISATEUR MEDICAL" or group_obj.name == "RESPONSABLE MEDICAL" or group_obj.name == "MEDECIN CONSEIL":
					return [('state', '=', 'attente')]
				# if group_obj.name == "PRESTATAIRE":
				# 	return [('state', '=', 'valide')]
			return False
		else:
			return False	


	def valide_demande(self, cr, uid, ids, context=None):

		entente_id = self.browse(cr, uid, ids[0], context=context).id

		entente_table = self.search(cr, uid, [('id', '=', entente_id)])

		entente_id_data = self.browse(cr, uid, entente_table)

		ctx = (context or {}).copy()
		ctx['entente'] = entente_id
		ctx['type_motif'] = 'VALIDATION'
		ctx['form_view_ref'] = 'view_mcisogem_motif_vep_form'
		
		return {
		  'name':'Motif',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.motif.vep',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}
		
		
	def rejet_demande(self, cr, uid, ids, context=None):
		
		entente_id = self.browse(cr, uid, ids[0], context=context).id

		entente_table = self.search(cr, uid, [('id', '=', entente_id)])

		entente_id_data = self.browse(cr, uid, entente_table)

		ctx = (context or {}).copy()
		ctx['entente'] = entente_id
		ctx['type_motif'] = 'REJET'
		ctx['form_view_ref'] = 'view_mcisogem_motif_vep_form'
		
		return {
		  'name':'Motif',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.motif.vep',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}
	
	def annuler_assures(self, cr, uid, ids, context=None):
		statut = self.pool.get('mcisogem.entente').browse(cr,uid,ids,context)
		print('******************************')
		print(statut.state)

		if(statut.state=='valide'):
			# self.write(cr, uid, ids, {'state':'attente', 'motif_valider' : ''}, context=context)
			cr.execute("update mcisogem_entente set state='attente', motif_valider = ''  where id = %s", (ids[0],))
		if(statut.state=='rejet'):
			# self.write(cr, uid, ids, {'state':'attente', 'motif_rejet' : ''}, context=context)
			cr.execute("update mcisogem_entente set state='attente', motif_rejet = ''  where id = %s", (ids[0],))


	def sous_acte_change(self,cr,uid,context,valeur):
		print('****ONCHANGE SOUS ACTES*****')
		if valeur:
			s_acte_id = self.pool.get('mcisogem.sous.actes').search_count(cr, uid, [('code_acte', '=', valeur)])
			print('****Nombre des sous actes*****')
			print(s_acte_id)
			if s_acte_id > 0 :
				v={'affichsacte':True}
				return {'value':v}
			else:
				if s_acte_id <= 0 :
					v={'affichsacte':False}
					return {'value':v}



	def onchange_centre_tempo(self,cr,uid,context,valeur,valeur2,valeur3):
		cr.execute('DELETE  FROM mcisogem_centre_tempo WHERE create_uid=%s', (uid,))

		print('**valeur 1 et 2 et 3**')
		print(valeur)
		print(valeur2)
		print(valeur2)

		if (valeur and valeur2 and valeur3 ): 
			
			cr.execute('SELECT distinct centre_id FROM mcisogem_tarif_nego_police WHERE college_id=%s AND police_id=%s AND garant_id=%s', (valeur,valeur2,valeur3,))
			centre_liste = cr.fetchall()
			print('*****LISTE des centres par garant*****')
			print(centre_liste)
			for ind_centre in centre_liste:
				print(ind_centre)
				centre = self.pool.get('mcisogem.centre').browse(cr, uid, ind_centre, context)
				print(centre.id)
				print(centre.name)
				data = {}
				data['centre_id'] = centre.id
				data['name'] = centre.name
				
				self.pool.get('mcisogem.centre.tempo').create(cr,uid,data,context)
	def onchange_centre_tempo2(self,cr,uid,context,valeur,valeur2):
		
		if valeur : 
			
			print(valeur)
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, valeur, context)
			print(centre.id)
			print(centre.name)
			data = {}
			data['centre_id'] = centre.id
			data['name'] = centre.name
				
			self.pool.get('mcisogem.centre.tempo').create(cr,uid,data,context)

	def create(self, cr, uid, vals, context=None):

		# vals['motif'] = str(vals['motif']).upper()

		########### envoi des notifications aux responsables médical pour demande d'entente préalable
		msg = str("Une nouvelle demande d'enttente préalable vient d'être émise. Vous devez l'examiner pour validation.")

		cr.execute("select id from res_groups where name='RESPONSABLE MEDICAL'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation de demande d'entente préalable",
			context=context
			)

			###################################################
		# pour le niveau garant
		if 'garant_id' in vals :
			cr.execute("SELECT max(num_entente) FROM mcisogem_entente WHERE garant_id = %s AND id_centre = 0", (vals['garant_id'],))
			num_entente = cr.fetchone()[0]

			print("***************************************")
			print(num_entente)
			if not num_entente:
				num_entente = 1

			else:
				num_entente = num_entente+1

		if 'id_centre' in vals :
			cr.execute("SELECT max(num_entente) FROM mcisogem_entente WHERE id_centre = %s AND garant_id  = 0", (vals['id_centre'],))
			num_entente = cr.fetchone()[0]

			print("***************************************")
			print(num_entente)
			if not num_entente:
				num_entente = 1

			else:
				num_entente = num_entente+1


		if 'benef_test_id' in vals:
			benef_1 = self.pool.get('mcisogem.benef').search(cr, uid, [('name','=',vals['benef_test_id'])])
			benef_2 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_chez_souscr','=',vals['benef_test_id'])])
			benef_3 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_isa','=',vals['benef_test_id'])])

			code_periode = time.strftime("%m/%Y", time.localtime())

			periode_id = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',code_periode)])
			periode_data = self.pool.get('mcisogem.account.period').browse(cr,uid,periode_id)

			

			if benef_1:
				data_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('name', '=', vals['benef_test_id'])])
				benef_id = self.pool.get('mcisogem.benef').browse(cr,uid,data_benef,context)
				donne={}

				donne = self.benef_change(cr, uid ,0, benef_id.name)['value']
				vals['beneficiaire_id']=benef_id.id
				vals['nom_benef']=donne['nom_benef']
				vals['prenom_benef'] = donne['prenom_benef']
				vals['tel_benef'] = donne['tel_benef']
				vals['mail_benef'] = donne['mail_benef']
				vals['affichebenef'] = donne['affichebenef']
				vals['image_medium'] = donne['image_medium']
			
			else:
				if benef_2:
					data_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_chez_souscr', '=', vals['benef_test_id'])])
					benef_id = self.pool.get('mcisogem.benef').browse(cr,uid,data_benef,context)
					donne={}

					donne = self.benef_change(cr, uid ,0, benef_id.matric_chez_souscr)['value']
					vals['beneficiaire_id']=benef_id.id
					vals['nom_benef']=donne['nom_benef']
					vals['prenom_benef'] = donne['prenom_benef']
					vals['tel_benef'] = donne['tel_benef']
					vals['mail_benef'] = donne['mail_benef']
					vals['affichebenef'] = donne['affichebenef']
					vals['image_medium'] = donne['image_medium']
					
				else:
					if benef_3:
						data_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_isa', '=', vals['benef_test_id'])])
						benef_id = self.pool.get('mcisogem.benef').browse(cr,uid,data_benef,context)
						donne={}

						donne = self.benef_change(cr, uid ,0, benef_id.matric_isa)['value']
						vals['beneficiaire_id']=benef_id.id
						vals['nom_benef']=donne['nom_benef']
						vals['prenom_benef'] = donne['prenom_benef']
						vals['tel_benef'] = donne['tel_benef']
						vals['mail_benef'] = donne['mail_benef']
						vals['affichebenef'] = donne['affichebenef']
						vals['image_medium'] = donne['image_medium']

			# centre_t = self.pool.get('mcisogem.centre.tempo').browse(cr, uid, vals['cent_id'], context)
				

			vals['num_entente'] = num_entente
			vals['state'] = "attente"
			# vals['centre_id'] = centre_t.centre_id
			vals['garant_p_id'] = vals['garant_id']
			vals['periode_id'] = periode_data.id
			vals['exercice_id'] = periode_data.exercice_id.id

			########### VERIFICATION DES EXCLUSION ###########

			fam_acte_id = vals['facte_id']
			acte_id = vals['acte_id']
			affection_id = vals['affection_id']

			police = benef_id.police_id.id
			college = benef_id.college_id.id
			statut_benef = benef_id.statut_benef.id
			benef = benef_id.id

			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('code_statut_id' , '=' , statut_benef), ('cod_col_id' , '=' , college), ('fam_acte_id' , '=' , fam_acte_id)]) > 0:
				raise osv.except_osv('Attention' ,'La famille d\'acte est exclue pour le statut de ce bénéficiaire.!')

			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('cod_benef_id' , '=' , benef), ('cod_col_id' , '=' , college), ('fam_acte_id' , '=' , fam_acte_id)]) > 0:
				raise osv.except_osv('Attention' ,'La famille d\'acte est exclu pour ce bénéficiaire.!')



			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('code_statut_id' , '=' , statut_benef), ('cod_col_id' , '=' , college), ('code_acte_id' , '=' , acte_id)]) > 0:
				raise osv.except_osv('Attention' ,'L\'acte est exclu pour le statut de ce bénéficiaire.!')

			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('cod_benef_id' , '=' , benef), ('cod_col_id' , '=' , college), ('code_acte_id' , '=' , acte_id)]) > 0:
				raise osv.except_osv('Attention' ,'L\'acte est exclu pour ce bénéficiaire.!')



			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('code_statut_id' , '=' , statut_benef), ('cod_col_id' , '=' , college), ('code_aff_id' , '=' , affection_id)]) > 0:
				raise osv.except_osv('Attention' ,'L\'affection est exclue pour le statut de ce bénéficiaire.!')

			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('cod_benef_id' , '=' , benef), ('cod_col_id' , '=' , college), ('code_aff_id' , '=' , affection_id)]) > 0:
				raise osv.except_osv('Attention' ,'L\'affection est exclue pour ce bénéficiaire.!')

			if vals['s_acteent_id'][0][2]:

				for s_acte_id in vals['s_acteent_id'][0][2]:

					if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('code_statut_id' , '=' , statut_benef), ('cod_col_id' , '=' , college), ('code_s_acte_id' , '=' , s_acte_id)]) > 0:
						raise osv.except_osv('Attention' ,'Le sous acte est exclu pour le statut de ce bénéficiaire.!')

					if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('cod_benef_id' , '=' , benef), ('cod_col_id' , '=' , college), ('code_s_acte_id' , '=' , s_acte_id)]) > 0:
						raise osv.except_osv('Attention' ,'Le sous acte est exclu pour ce bénéficiaire.!')

		return super(mcisogem_entente,self).create(cr, uid, vals, context)

	def benef_change(self,cr,uid,ids,benef_mat,context=None):
		if benef_mat:
			#nombre de ligne repondant au matricule saisi
			nbr_benef_1 = self.pool.get('mcisogem.benef').search_count(cr, uid, [('name', '=', benef_mat)])
			nbr_benef_2 = self.pool.get('mcisogem.benef').search_count(cr, uid, [('matric_chez_souscr', '=', benef_mat)])
			nbr_benef_3 = self.pool.get('mcisogem.benef').search_count(cr, uid, [('matric_isa', '=', benef_mat)])
			#recuperation des innformation du beneficiaire
			benef_1 = self.pool.get('mcisogem.benef').search(cr, uid, [('name','=',benef_mat)])
			benef_2 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_chez_souscr','=',benef_mat)])
			benef_3 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_isa','=',benef_mat)])

			exiiste_benef = False

			if benef_1:
				beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_1,context)
				exiiste_benef = True
			else:
				if benef_2:
					beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_2,context)
					exiiste_benef = True
				else:
					if benef_3:
						beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_3,context)
						exiiste_benef = True
					# else:
					# 	beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_1,context)
			if exiiste_benef:

				#recuperation du statut de la police du beneficiaire
				police = self.pool.get('mcisogem.police').browse(cr,uid,beneficiaire.police_id.id,context)
				police_stat = police.state
				print('****police******')
				print(beneficiaire.police_id.id)

				print('****college******')
				print(beneficiaire.college_id.id)

				reseau = False

				college_id = beneficiaire.college_id.id
				#historique de la police
				id_age = self.pool.get('mcisogem.histo.police').search(cr, uid, [('name', '=', beneficiaire.police_id.id),('code_college', '=', college_id)])
				histo_pol = self.pool.get('mcisogem.histo.police').browse(cr, uid, id_age, context)
				age_lim = histo_pol.limite_age_pol
				age_maj = histo_pol.age_majorite_pol


				print('**Age limite benef**')
				print(age_lim)
				print(age_maj)
				

				college = self.pool.get('mcisogem.college').browse(cr, uid, beneficiaire.college_id.id).name
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, beneficiaire.souscripteur_id.id).name
				statut = self.pool.get('mcisogem.stat.benef').browse(cr, uid, beneficiaire.statut_benef.id).name

				cr.execute('select garant_id from res_users where id=%s', (uid,))
				garant_user_id = cr.fetchone()[0]
				cr.execute('select centre_id from res_users where id=%s', (uid,))
				# centre_user_id = cr.fetchone()[0]
				centre_user_id = cr.fetchall()

				cr.execute('select centre_id from res_users where id=%s', (uid,))
				id_centre = cr.fetchone()[0]

				if garant_user_id:
					garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
					print('*******garant id********')
					print(garant.id)
					v={'garant_id':garant.id,'college_id': beneficiaire.college_id.id,'beneficiaire_id':beneficiaire.id,'police_id':beneficiaire.police_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'tel_benef':beneficiaire.tel_benef,'mail_benef':beneficiaire.adr_benef,'affichebenef':False,'affichdetail':True,'image_medium':beneficiaire.image_medium}	
					#v={'affichebenef':False,'affichdetail':True}
				else:
					if centre_user_id:
						centre = self.pool.get('mcisogem.centre').browse(cr, uid, id_centre, context=context)
						print('***************************Centre*************************')
						print(centre.id)
						v={'centre_id':centre.id,'id_centre':centre.id,'college_id': beneficiaire.college_id.id,'beneficiaire_id':beneficiaire.id,'police_id':beneficiaire.police_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'tel_benef':beneficiaire.tel_benef,'mail_benef':beneficiaire.adr_benef,'affichebenef':False,'affichdetail':True,'image_medium':beneficiaire.image_medium}
						#v={'affichebenef':False,'affichdetail':True}
					else:
						#v={'beneficiaire_id':beneficiaire.id,'police_id':beneficiaire.police_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'tel_benef':beneficiaire.tel_benef,'mail_benef':beneficiaire.adr_benef,'affichebenef':False,'affichdetail':True,'image_medium':beneficiaire.image_medium}
						v={'affichebenef':False,'affichdetail':True}


				print('***************************IB Beneficiaire*************************')
				print(beneficiaire.id)
				ctx2 = (context or {}).copy()
				ctx2['id_benef'] = beneficiaire.id

				if ((nbr_benef_1==0) and (nbr_benef_2==0) and (nbr_benef_3==0)):	
					raise osv.except_osv('Attention' ,'Beneficiaire inexistant!')
				else:
					dn_benef = beneficiaire.dt_naiss_benef
					date_new = time.strftime("%Y-%m-%d")
					age = (int(date_new[0:4]) - int(str(dn_benef)[0:4])) 
					print('**Age benef**')
					print(age)

					if self.pool.get('mcisogem.entente').search_count(cr,uid,[('beneficiaire_id' , '=' ,beneficiaire.id) , ('state' , '=' , 'attente')]) > 0:
						raise osv.except_osv('Attention' , 'Ce bénéficiaire a déjà une demande en attente !')

					if ((beneficiaire.statut=='R') or (beneficiaire.statut=='S')):
						raise osv.except_osv('Attention' ,'Aucune action ne peut être effectué sur ce bénéficiaire!')
						
					if  garant_user_id:
						if (garant_user_id != beneficiaire.garant_id.id):
							raise osv.except_osv('Attention' ,'Mauvais garant!')

						if ((police_stat=='resil') or (police_stat=='lnoir') or (police_stat=='cancel')):
							raise osv.except_osv('Attention' ,'Police invalide')

						if (age_lim !=0) and (age_maj !=0):
							print('test age!!')
							if (((age_lim  < age) and (age > age_maj)) or (age_lim > age)):
								raise osv.except_osv('Attention' ,'Age invalide...')
							else:
								print('**test age**')
								print('Age inferieur a la limite')
					else:
						if centre_user_id:
							if ((police_stat=='resil') or (police_stat=='lnoir') or (police_stat=='cancel')):
								raise osv.except_osv('Attention' ,'Oups Police invalide')

							if (age_lim !=0) and (age_maj !=0):
								print('test age!!')
								if (((age_lim  < age) and (age > age_maj)) or (age_lim > age)):
									raise osv.except_osv('Attention' ,'Age invalide...')
								else:
									print('**test age**')
									print('Age inferieur a la limite')
							
							les_reseaux = []

							# on verifie si le beneficiaire est dans son réseau de soins

							les_data = self.pool.get('mcisogem.rata.reseau.police').search(cr,uid, [('police_id' , '=' , beneficiaire.police_id.id) , ('college_id' , '=' , beneficiaire.college_id.id)])

							for ld in self.pool.get('mcisogem.rata.reseau.police').browse(cr,uid,les_data):
								les_reseaux.append(ld.reseau_id.id)


							for res in les_reseaux:
								d = self.pool.get('mcisogem.tarif.nego.police').search(cr,uid,[('reseau_id' , '=' , res) , ('centre_id' , '=' , centre_user_id[0])])


								if d:
									reseau =  True
									break



							if beneficiaire.police_complementaire_ids and reseau==False:

								#A revoir plus tard
								for ind_pol in beneficiaire.police_complementaire_ids[0][2]:

									les_reseaux = []


									la_police_comp = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr,uid,ind_pol)

									# on verifie si le beneficiaire est dans son réseau de soins

									les_data = self.pool.get('mcisogem.rata.reseau.police').search(cr,uid, [('police_id' , '=' , la_police_comp.police_id.id) , ('college_id' , '=' , la_police_comp.college_id.id)])


									if les_data:

										for ld in self.pool.get('mcisogem.rata.reseau.police').browse(cr,uid,les_data):
											les_reseaux.append(ld.reseau_id.id)


										for res in les_reseaux:
											d = self.pool.get('mcisogem.tarif.nego.police').search(cr,uid,[('reseau_id' , '=' , res) , ('centre_id' , '=' , centre_user_id[0])])

											if d:
												reseau =  True
											break



							if (reseau == False):
								raise osv.except_osv('Attention' ,'Mauvais resaux de soin!')

						else:

							raise osv.except_osv('Attention' ,'Aucun utilisateur connecté')
				
				return {'value':v,'context':ctx2}
				#return {'value':v}
			else:
				raise osv.except_osv('Attention' ,'Beneficiaire inexistant!')

		else:

			benef = self.pool.get('mcisogem.benef').search(cr, uid, [('name','=',benef_mat)])
			beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef,context)
			v={'nom_benef':'','prenom_benef':'','tel_benef':'','mail_benef':'','affichebenef':True}
			return {'value':v}

class mcisogem_motif_vep(osv.osv):
	_name = "mcisogem.motif.vep"
	_description = 'Motif de validation des ententes préalables'


	def _get_entente(self, cr, uid, context):
		if context.get('entente'):
			return context.get('entente')
		else:
			return False

	def _get_type(self, cr, uid, context):
		if context.get('type_motif'):
			return context.get('type_motif')
		else:
			return False

	_columns = {
		'entente_id': fields.many2one('mcisogem.entente', 'Prise en charge',required=True),
		'type' : fields.text('Type de motif',required=True),
		'name' : fields.text('Motif',required=True),
	}

	def button_valider(self, cr, uid , ids, context=None):
		print('OK')

	def create(self, cr, uid , vals , context):
		# vals['name'] = str(vals['name']).upper()
		data =  self.browse(cr, uid, context=context)
		vals['entente_id'] = context['entente']
		pcharge = self.pool.get('mcisogem.entente').search(cr,uid,[('id' , '=' , vals['entente_id'])])
		pcharge_data = self.pool.get('mcisogem.entente').browse(cr, uid, pcharge)

		
		if vals['type'] == 'VALIDATION':
			# self.pool.get('mcisogem.entente').write(cr,uid,pcharge_data.ids,{'state':'valide', 'motif_valider':vals['name']},context=context)
			cr.execute("update mcisogem_entente set state='valide', motif_valider = %s  where id = %s", (vals['name'],pcharge_data.id,))

		if vals['type'] == 'REJET':
			# self.pool.get('mcisogem.entente').write(cr,uid,pcharge_data.ids,{'state':'rejet', 'motif_rejet':vals['name']},context=context)
			cr.execute("update mcisogem_entente set state='rejet', motif_rejet = %s  where id = %s", (vals['name'],pcharge_data.id,))

		
	
		return super(mcisogem_motif_vep , self).create(cr,uid,vals,context)

	_defaults = {
		'entente_id' : _get_entente,
		'type' : _get_type,
	}



class mcisogem_praticien_tempo(osv.osv):
	_name = 'mcisogem.praticien.tempo'
	_columns = {
		'praticien_id':fields.integer('Identifiant praticien'),
		'nom_prat' : fields.char('Nom Medecin'),
		'prenom_prat' : fields.char('Prenoms Medecin'),
	}
	_rec_name = 'nom_prat'		


class mcisogem_prisecharge(osv.osv):
	_name = 'mcisogem.pcharge'
	_description = 'Prise en charge'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_mail_post_access = 'read'


	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)


	
	def _get_centre_user(self, cr, uid, context=None):
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]
		if centre_user_id:
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
			return centre.id
		else:
			return False


	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			return garant.id
		else:
			return False	


	def _get_utilisateur(self, cr,uid,context):
		
		return uid	

	

			

	_columns = {
		'user_id' : fields.integer('Identifiant Utilisateur'),
		'garant_id' : fields.integer('Identifiant Garant'),
		'garant_p_id' : fields.integer('mcisogem_garant','Garant'),
		'id_centre' : fields.integer('Identifiant centre'),
		'centre' : fields.many2one('mcisogem.centre','Centre'),
		'periode_id' : fields.many2one('mcisogem.account.period' , 'Periode'),
		'exercice_id' : fields.many2one('mcisogem.exercice' , 'Exercice'),
		'police_id' : fields.integer('Identifiant police beneficiaire'),
		'college_id' : fields.integer('Identifiant collège'),
		'beneficiaire_id' : fields.many2one('mcisogem.benef', 'Beneficiaire', ondelete="cascade"),
		'mat_princ' : fields.many2one('mcisogem.benef', 'Matricule assure principal'),
		'nom_princ' : fields.char('nom assure principle'),
		'prenom_princ' : fields.char('prenom assure principle'),
		'benef_test_id' : fields.char('Beneficiaire',required=True),
		'praticien_id' :  fields.many2one('mcisogem.praticien', 'Medecin', ondelete="cascade"),
		'police_benef_id' :  fields.many2one('mcisogem.police', 'Police'),
		'college_benef_id' :  fields.many2one('mcisogem.college', 'College'),
		'prati_id' :  fields.many2one('mcisogem.praticien.tempo', 'Medecin'),

		'quantite' : fields.integer('Quantite'),
		'montant_total_med' : fields.integer('Montant total des médicaments'),

		'date_hospi' : fields.date('Date d\'hospitalisation'),
		'dure_demande' : fields.integer('Durée en jours de la demande'),
		'nbr_jour_acc' : fields.integer('Durée en jours accordés'),
		'dur_sup_demande' : fields.integer('Prorogation demande'),
		'dure_courier' : fields.integer('Nombre de jours accordés'),

		'monatant' : fields.integer('Montant à payer'),
		'ticket_mod' : fields.integer('Ticket moderateur'),
		'taux_pc' : fields.integer('Taux de prise en charge'),
		'plafond_chambre' : fields.integer('Plafont chambre'),


		'affection_id' : fields.many2one('mcisogem.affec', 'Affection',required=True),
		'facte_id' : fields.many2one('mcisogem.fam.prest', 'Famille acte',required=True),
		'acte_id' : fields.many2one('mcisogem.nomen.prest', 'Acte',required=True),
		's_acteent_id' : fields.many2many('mcisogem.sous.actes', 'pcharge_sacte_rel_1', 'id_pc', 'id_sa', 'Sous actes'),
		
		'image': fields.binary("Image",
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.pcharge': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.pcharge': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		
		'motif' : fields.text('Observations',required=True),
		'motif_valider' : fields.text('Motif pour Validation'),
		'motif_rejet' : fields.text('Motif pour rejet'),
		'motif_prorogation' : fields.text('Motif prorogation'),
		'age_patient' : fields.integer('Age du patient'),
		'ident' : fields.many2one('res.users'),
		'fichier_join' : fields.binary('Piece jointe',
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'state': fields.selection([
			('nouveau', "Nouveau"),
			('attente', " En attente"),
			('valide', "Acceptée"),
			('rejet', "Rejetée"),
			
		   
		], 'Status', required=True, readonly=True),
		'statut' : fields.char('Statut'),
		'num_pchrage':fields.integer('Numero :'),
		'pcharge_id' : fields.many2one('mcisogem.pcharge','Prise en charge'),
		
		'mail_benef': fields.char('Mail'),
		'nom_benef' : fields.char('Nom'),
		'prenom_benef' : fields.char('Prenoms'),
		'tel_benef' : fields.char('Telephone'),
		'nom_prat' : fields.char('Nom Medecin'),
		'prenom_prat' : fields.char('Prenoms Medecin'),
		'mail_prat' : fields.char('Mail'),
		'tel_prat' : fields.char('Contact'),
		'affichebenef': fields.boolean(''),
		'afficheprat': fields.boolean(''),
		'affichdetail': fields.boolean(''),
		'affichprorog': fields.boolean(''),
		
		'aff_quantite': fields.boolean(''),
		'aff_mont_tt': fields.boolean(''),
		'aff_hos_mat': fields.boolean(''),
		'aff_mont': fields.boolean(''),
		'imprimer': fields.boolean(''),
		'affichsacte': fields.boolean(''),
		'en_cours': fields.boolean(''),
	}
	
	_defaults ={'state':'nouveau','affichebenef':True,'afficheprat':False,'affichdetail':False, 'quantite':1, 'user_id':_get_utilisateur,'imprimer':False, 'affichsacte': False}	
	
	_rec_name = 'beneficiaire_id'

	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "UTILISATEUR MEDICAL" or group_obj.name == "RESPONSABLE MEDICAL":
					return [('state', '=', 'attente')]
				if group_obj.name == "PRESTATAIRE":
					return [('state', '=', 'valide'), ('imprimer', '=', False)]
			return False
		else:
			return False



	def button_courier(self, cr, uid , ids, context=None):
		print('OK')

	def button_prorogation(self,cr,uid,ids,context):
	
		pcharge_data = self.browse(cr, uid, ids, context=context)

		f_acte_id = pcharge_data.facte_id.id
		famille_acte = self.pool.get('mcisogem.fam.prest').browse(cr, uid, f_acte_id)

		if (famille_acte.name != "HOSPITALISATION"):
			raise osv.except_osv('Attention' ,'Impossible de faire une demande de prorogation pour cette prise en charge!')

		ctx = (context or {}).copy()
		
		ctx['pcharge_id'] = ids[0]
		ctx['prorogation'] = True
		ctx['statut'] = 'PROROGATION'
		ctx['beneficiaire'] = pcharge_data.beneficiaire_id.id
		ctx['nom'] = pcharge_data.nom_benef
		ctx['prenom'] = pcharge_data.prenom_benef
		ctx['tel'] = pcharge_data.tel_benef
		ctx['mail'] = pcharge_data.mail_benef
		ctx['image_medium'] = pcharge_data.image_medium
		ctx['centre'] = pcharge_data.centre.id
		ctx['praticien'] = pcharge_data.praticien_id.id
		ctx['affection'] = pcharge_data.affection_id.id
		ctx['fact'] = pcharge_data.facte_id.id
		ctx['acte'] = pcharge_data.acte_id.id
		ctx['date_hospi'] = pcharge_data.date_hospi
		ctx['dure_demande'] = pcharge_data.dure_courier
		ctx['motif'] = pcharge_data.motif
		ctx['quantite'] = pcharge_data.quantite


		form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_prorogation_form')[1]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_prorogation_tree')[1]

		return {
				'name':'Demande de prorogation',
				'view_type':'form',
				'view_mode':'form,tree',
				'res_model':'mcisogem.prorogation',
				'target':'current',
				'views': [(tree_id ,'tree'),(form_id, 'form')],
				'view_id': form_id,
				'type':'ir.actions.act_window',
				'domain':[('pcharge_id', '=',ctx['pcharge_id'] )],
				'context':ctx,
				'nodestroy':True,
				}

	# def init_server_hospitalisation_cours(self, cr, uid, context):
		
	# 	res = {}

	# 	date_jour = time.strftime("%m/%Y", time.localtime())

	# 	view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'mcisogem.pcharge.tree')], context=context)
	# 	if view_ids:
			
	# 		res = {
	# 		'view_id': view_ids[0],
	# 		'view_mode': 'tree',
	# 		'view_type': 'form',
	# 		'res_model': 'mcisogem.pcharge',
	# 		'type': 'ir.actions.act_window',
	# 		'domain': [('facte_id','in',(6,9)),('state','=','valide')],
	# 		'context': context
	# 		}
	# 		print(res)
	# 	else:
	# 		print("TEST")
	# 	return res

	def hospitalisation_en_cours(self,cr,uid,context=None):
		print('###############  EN COURS #######################')

		cr.execute('SELECT id FROM mcisogem_pcharge')
		pcharge_id_liste = cr.fetchall()

		date = time.strftime("%Y-%m-%d", time.localtime())
		# date_jour = datetime.strptime(str(date), '%Y-%m-%d')

		# date_jour = datetime.strptime(str(time.strftime("%Y-%m-%d", time.localtime())), '%Y-%m-%d')
		date_jour = time.strftime("%Y-%m-%d", time.localtime())
		date_jour = datetime.strptime(str(date_jour), '%Y-%m-%d')

		print('###############  date_jour ######################')
		print(date_jour)

		for ind in pcharge_id_liste:
			pcharge_id = self.pool.get('mcisogem.pcharge').browse(cr, uid, ind, context)

			if ((pcharge_id.facte_id.name == 'HOSPITALISATION') and (pcharge_id.state == 'valide')):

				date_debu = datetime.strptime(str(pcharge_id.date_hospi), '%Y-%m-%d')
				print('###############  date_debu ######################')
				print(date_debu)

				if (pcharge_id.dure_courier):
					nombre_jour = pcharge_id.dure_courier
			
					DATE_1 = datetime.strptime(str(pcharge_id.date_hospi), '%Y-%m-%d')
					end_date = DATE_1 + timedelta(days=nombre_jour)
					

					print('###############  date_fin ######################')
					# print(date_fin)
					print(end_date)
				else:
					nombre_jour = pcharge_id.nbr_jour_acc
					

					DATE_1 = datetime.strptime(str(pcharge_id.date_hospi), '%Y-%m-%d')
					end_date = DATE_1 + timedelta(days=nombre_jour)
					

					print('###############  date_fin ######################')
					print(end_date)

				if ((date_debu <= date_jour) and (date_jour <= end_date)):
					cr.execute("update mcisogem_pcharge set en_cours = 'True'  where id = %s", (pcharge_id.id,))
				else:
					cr.execute("update mcisogem_pcharge set en_cours = 'False'  where id = %s", (pcharge_id.id,))
			else:
				cr.execute("update mcisogem_pcharge set en_cours = 'False'  where id = %s", (pcharge_id.id,))

			if ((pcharge_id.facte_id.name != 'HOSPITALISATION') and (pcharge_id.state == 'valide')): 
				cr.execute("update mcisogem_pcharge set en_cours = 'False'  where id = %s", (pcharge_id.id,))

			if ((pcharge_id.facte_id.name == 'HOSPITALISATION') and (pcharge_id.state == 'rejet')): 
				cr.execute("update mcisogem_pcharge set en_cours = 'False'  where id = %s", (pcharge_id.id,))




	def print_recherche(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids, [], context=context)
		# ident = self.browse(cr, uid, ids[0], context=context).ident
		self.write(cr, uid, ids, {'imprimer':True}, context=context)
		# self.write(cr, uid, ids, {'imprimer':True, 'write_uid':ident}, context=context)
		# print('###############UID########################################3')
		# print(uid.praticien_id.prenoms_prestat)

		return {
				'type': 'ir.actions.report.xml',
				'report_name': 'mcisogem_isa.report_bon_pcharge',
				'data': data,
		}
			


	def valide_demande(self, cr, uid, ids, context=None):

		pcharge_id = self.browse(cr, uid, ids[0], context=context).id

		pcharge_table = self.search(cr, uid, [('id', '=', pcharge_id)])

		pcharge_data = self.browse(cr, uid, pcharge_table)

		ctx = (context or {}).copy()
		ctx['pcharge'] = pcharge_id
		ctx['type_motif'] = 'VALIDATION'
		ctx['form_view_ref'] = 'view_mcisogem_motif_vpc_form'
		
		return {
		  'name':'Motif',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.motif.vpc',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}


	def rejet_demande(self, cr, uid, ids, context=None):
		
		pcharge_id = self.browse(cr, uid, ids[0], context=context).id

		pcharge_table = self.search(cr, uid, [('id', '=', pcharge_id)])

		pcharge_data = self.browse(cr, uid, pcharge_table)

		ctx = (context or {}).copy()
		ctx['pcharge'] = pcharge_id
		ctx['type_motif'] = 'REJET'
		ctx['form_view_ref'] = 'view_mcisogem_motif_vpc_form'
		
		return {
		  'name':'Motif',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.motif.vpc',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}
	
	def annuler_assures(self, cr, uid, ids, context=None):
		statut = self.pool.get('mcisogem.pcharge').browse(cr,uid,ids,context)
		print('******************************')
		print(statut.state)

		if(statut.state=='valide'):
			# self.write(cr, uid, ids, {'state':'attente', 'motif_valider' : '', 'nbr_jour_acc' : 0,'dure_courier':0}, context=context)
			cr.execute("update mcisogem_pcharge set state='attente', motif_valider = '', nbr_jour_acc = 0,dure_courier = 0  where id = %s", (ids[0],))
		if(statut.state=='rejet'):
			# self.write(cr, uid, ids, {'state':'attente', 'motif_rejet' : ''}, context=context)
			cr.execute("update mcisogem_pcharge set state='attente', motif_rejet = '' where id = %s", (ids[0],))

	def sous_acte_change(self,cr,uid,context,valeur):
		print('****ONCHANGE SOUS ACTES*****')
		if valeur:
			s_acte_id = self.pool.get('mcisogem.sous.actes').search_count(cr, uid, [('code_acte', '=', valeur)])
			print('****Nombre des sous actes*****')
			print(s_acte_id)
			if s_acte_id > 0 :
				v={'affichsacte':True}
				return {'value':v}
			else:
				if s_acte_id <= 0 :
					v={'affichsacte':False}
					return {'value':v}
		
	def onchange_famille_acte(self,cr,uid,context,fact_id):
		if fact_id:
			print('**valeur de famille d acte id**')
			print(fact_id)
			# ind_fam_act = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('id', '=', fact_id)])
			famille_acte = self.pool.get('mcisogem.fam.prest').browse(cr, uid, fact_id)
			v = {}
			if (famille_acte.name == "OPTIQUE"):
				v={'aff_mont':True,'aff_quantite':False,'aff_mont_tt':False,'aff_hos_mat':False}
				return {'value':v}

			if (famille_acte.name == "DENTAIRE"):
				v={'aff_quantite':True,'aff_mont':False,'aff_mont_tt':False,'aff_hos_mat':False}
				return {'value':v}

			if (famille_acte.name == "PHARMACIE"):
				v={'aff_mont_tt':True,'aff_mont':False,'aff_quantite':False,'aff_hos_mat':False}
				return {'value':v}

			if (famille_acte.name == "HOSPITALISATION"):
				v={'aff_hos_mat':True,'aff_mont':False,'aff_quantite':False,'aff_mont_tt':False}
				return {'value':v}

			if (famille_acte.name == "MATERNITE"):
				v={'aff_hos_mat':True,'aff_mont':False,'aff_quantite':False,'aff_mont_tt':False}
				return {'value':v}

			if (famille_acte.name == "AUTRES EXAMENS"):
				v={'aff_quantite':True,'aff_mont':False,'aff_mont_tt':False,'aff_hos_mat':False}
				return {'value':v}
		else:
			v={'aff_quantite':False,'aff_mont':False,'aff_mont_tt':False,'aff_hos_mat':False}
			return {'value':v}

		
		

	def onchange_prat_tempo(self,cr,uid,context,valeur,valeur2,valeur3):
		cr.execute('DELETE  FROM mcisogem_praticien_tempo WHERE create_uid=%s', (uid,))
		if valeur and valeur2 and valeur3 : 
			
			cr.execute('SELECT distinct centre_id FROM mcisogem_tarif_nego_police WHERE college_id=%s AND police_id=%s AND garant_id=%s', (valeur,valeur2,valeur3,))
			centre_liste = cr.fetchall()
			print('*****LISTE des centres par garant*****')
			print(centre_liste)
			for ind_centre in centre_liste:
				print(ind_centre)
				cr.execute('SELECT distinct libelle_court_prestat FROM mcisogem_agr_prestat,praticien_rel WHERE mcisogem_agr_prestat.id=praticien_rel.praticien_rel_id AND code_centre=%s', (ind_centre,))
				medecin_liste = cr.fetchall()
				print('*****LISTE des Medecin par centre*****')
				print(medecin_liste)
				#
				for ind_medecin in medecin_liste:
					medecin = self.pool.get('mcisogem.praticien').browse(cr, uid, ind_medecin,context)
					print(ind_medecin)
					print(medecin.nom_prestat)
					print(medecin.prenoms_prestat)
					data = {}
					data['praticien_id'] = medecin.id
					data['nom_prat'] = medecin.nom_prestat
					data['prenom_prat'] = medecin.prenoms_prestat
					existe = self.pool.get('mcisogem.praticien.tempo').search(cr, uid , [('praticien_id', '=', medecin.id),('nom_prat', '=', medecin.nom_prestat),('prenom_prat', '=', medecin.prenoms_prestat)])
					if (not existe) : 
						self.pool.get('mcisogem.praticien.tempo').create(cr,uid,data,context)

	def onchange_prat_tempo2(self,cr,uid,context,valeur,valeur2):
		# cr.execute('DELETE  FROM mcisogem_praticien_tempo WHERE create_uid=%s', (uid,))
		if valeur : 
			
			
			centre_user_id = valeur
			print('*****centres*****')
			print(centre_user_id)
			cr.execute('SELECT distinct libelle_court_prestat FROM mcisogem_agr_prestat,praticien_rel WHERE mcisogem_agr_prestat.id=praticien_rel.praticien_rel_id AND code_centre=%s', (centre_user_id,))
			medecin_liste = cr.fetchall()
			print('*****LISTE des Medecin par centre CENTRE*****')
			
			for ind_medecin in medecin_liste:
				medecin = self.pool.get('mcisogem.praticien').browse(cr, uid, ind_medecin,context)
				
				data = {}
				data['praticien_id'] = medecin.id
				data['nom_prat'] = medecin.nom_prestat
				data['prenom_prat'] = medecin.prenoms_prestat
				self.pool.get('mcisogem.praticien.tempo').create(cr,uid,data,context)



	def create(self, cr, uid, vals, context=None):
		# vals['motif'] = str(vals['motif']).upper()

		########### envoi des notifications aux responsable médical pour demande de prise en charge
		msg = str("Une nouvelle demande de prise en charge vient d'être émise. Vous devez l'examiner pour validation.")

		cr.execute("select id from res_groups where name='RESPONSABLE MEDICAL'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation de demande de prise en charge",
			context=context
			)

			###################################################""
		# niveau priche en charge
		if 'garant_id' in vals :
			print('***val garant_id***')
			print(vals['garant_id'])
			cr.execute("SELECT max(num_pchrage) FROM mcisogem_pcharge WHERE garant_id  = %s AND id_centre = 0", (vals['garant_id'],))
			num_pchrage = cr.fetchone()[0]

			print("***************************************")
			print(num_pchrage)
			if not num_pchrage:
				num_pchrage = 1
			else:
				num_pchrage = num_pchrage+1

		if 'id_centre' in vals :
			cr.execute("SELECT max(num_pchrage) FROM mcisogem_pcharge WHERE id_centre = %s AND garant_id  = 0", (vals['id_centre'],))
			num_pchrage = cr.fetchone()[0]

			print("***************************************")
			print(num_pchrage)
			if not num_pchrage:
				num_pchrage = 1
			else:
				num_pchrage = num_pchrage+1

		
		if 'benef_test_id' in vals:
			# print('***************************test*************************')
			# print(context.get('mat_benef'))
			# data_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('name', '=', vals['benef_test_id'])])
			# benef_id = self.pool.get('mcisogem.benef').browse(cr,uid,data_benef,context)

			benef_1 = self.pool.get('mcisogem.benef').search(cr, uid, [('name','=',vals['benef_test_id'])])
			benef_2 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_chez_souscr','=',vals['benef_test_id'])])
			benef_3 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_isa','=',vals['benef_test_id'])])

			code_periode = time.strftime("%m/%Y", time.localtime())

			periode_id = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',code_periode)])
			periode_data = self.pool.get('mcisogem.account.period').browse(cr,uid,periode_id)


			

			if benef_1:
				data_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('name', '=', vals['benef_test_id'])])
				benef_id = self.pool.get('mcisogem.benef').browse(cr,uid,data_benef,context)
				donne={}

				donne = self.benef_change(cr, uid ,0, benef_id.name)['value']
				vals['beneficiaire_id']=benef_id.id
				vals['nom_benef']=donne['nom_benef']
				vals['prenom_benef'] = donne['prenom_benef']
				vals['tel_benef'] = donne['tel_benef']
				vals['mail_benef'] = donne['mail_benef']
				vals['affichebenef'] = donne['affichebenef']
				vals['image_medium'] = donne['image_medium']

				vals['police_benef_id'] = donne['police_benef_id']
				vals['college_benef_id'] = donne['college_benef_id']
			
			else:
				if benef_2:
					data_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_chez_souscr', '=', vals['benef_test_id'])])
					benef_id = self.pool.get('mcisogem.benef').browse(cr,uid,data_benef,context)
					donne={}

					donne = self.benef_change(cr, uid ,0, benef_id.matric_chez_souscr)['value']
					vals['beneficiaire_id']=benef_id.id
					vals['nom_benef']=donne['nom_benef']
					vals['prenom_benef'] = donne['prenom_benef']
					vals['tel_benef'] = donne['tel_benef']
					vals['mail_benef'] = donne['mail_benef']
					vals['affichebenef'] = donne['affichebenef']
					vals['image_medium'] = donne['image_medium']

					vals['police_benef_id'] = donne['police_benef_id']
					vals['college_benef_id'] = donne['college_benef_id']
					
				else:
					if benef_3:
						data_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_isa', '=', vals['benef_test_id'])])
						benef_id = self.pool.get('mcisogem.benef').browse(cr,uid,data_benef,context)
						donne={}

						donne = self.benef_change(cr, uid ,0, benef_id.matric_isa)['value']
						vals['beneficiaire_id']=benef_id.id
						vals['nom_benef']=donne['nom_benef']
						vals['prenom_benef'] = donne['prenom_benef']
						vals['tel_benef'] = donne['tel_benef']
						vals['mail_benef'] = donne['mail_benef']
						vals['affichebenef'] = donne['affichebenef']
						vals['image_medium'] = donne['image_medium']

						vals['police_benef_id'] = donne['police_benef_id']
						vals['college_benef_id'] = donne['college_benef_id']
			
		vals['num_pchrage'] = num_pchrage

		prat_tempo_id = self.pool.get('mcisogem.praticien.tempo').search(cr, uid, [('id', '=', vals['prati_id'])])
		prat_tempo = self.pool.get('mcisogem.praticien.tempo').browse(cr,uid,prat_tempo_id,context)

		praticien= self.pool.get('mcisogem.praticien').browse(cr,uid,prat_tempo.praticien_id,context)
		vals['praticien_id'] = praticien.id
		vals['garant_p_id'] = vals['garant_id']
		

		donne1=self.prat_change(cr,uid,0,vals['prati_id'])['value']
		vals['nom_prat']=donne1['nom_prat']
		vals['prenom_prat'] = donne1['prenom_prat']
		# vals['mail_prat'] = donne1['mail_prat']
		vals['tel_prat'] = donne1['tel_prat']
		vals['afficheprat'] = donne1['afficheprat']
		vals['state'] = "attente"
		vals['periode_id'] = periode_data.id
		vals['exercice_id'] = periode_data.exercice_id.id
		vals['en_cours'] = 'False'

		if 'acte_id' in vals:
			police = benef_id.police_id.id
			college = benef_id.college_id.id
			statut_benef = benef_id.statut_benef.id
			garant = benef_id.garant_id.id

			produit_id = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police), ('acte_id', '=', vals['acte_id']), ('college_id', '=', college), ('statut_id', '=', statut_benef)])
			produit = self.pool.get('mcisogem.produit.police').browse(cr,uid,produit_id,context)

			bareme_id = self.pool.get('mcisogem.bareme').search(cr, uid, [('produit_id', '=', produit.produit_id.id), ('acte_id', '=', vals['acte_id'])])
			bareme = self.pool.get('mcisogem.bareme').browse(cr,uid,bareme_id,context)

			if (benef_id.code_statut == 'A'):	
				vals['ticket_mod'] = bareme.ticm_assure
			else:
				if (benef_id.code_statut == 'E'):
					vals['ticket_mod'] = bareme.ticm_assure
				else:
					if (benef_id.code_statut == 'C'):
						vals['ticket_mod'] = bareme.ticm_assure

			vals['plafond_chambre'] = bareme.plf_prest_fam
			vals['taux_pc'] = (100 - vals['ticket_mod'])




			########### VERIFICATION DES EXCLUSION ###########

			fam_acte_id = vals['facte_id']
			acte_id = vals['acte_id']
			affection_id = vals['affection_id']

			police = benef_id.police_id.id
			college = benef_id.college_id.id
			statut_benef = benef_id.statut_benef.id
			benef = benef_id.id

			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('code_statut_id' , '=' , statut_benef), ('cod_col_id' , '=' , college), ('fam_acte_id' , '=' , fam_acte_id)]) > 0:
				raise osv.except_osv('Attention' ,'La famille d\'acte est exclue pour le statut de ce bénéficiaire.!')

			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('cod_benef_id' , '=' , benef), ('cod_col_id' , '=' , college), ('fam_acte_id' , '=' , fam_acte_id)]) > 0:
				raise osv.except_osv('Attention' ,'La famille d\'acte est exclu pour ce bénéficiaire.!')



			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('code_statut_id' , '=' , statut_benef), ('cod_col_id' , '=' , college), ('code_acte_id' , '=' , acte_id)]) > 0:
				raise osv.except_osv('Attention' ,'L\'acte est exclu pour le statut de ce bénéficiaire.!')

			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('cod_benef_id' , '=' , benef), ('cod_col_id' , '=' , college), ('code_acte_id' , '=' , acte_id)]) > 0:
				raise osv.except_osv('Attention' ,'L\'acte est exclu pour ce bénéficiaire.!')



			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('code_statut_id' , '=' , statut_benef), ('cod_col_id' , '=' , college), ('code_aff_id' , '=' , affection_id)]) > 0:
				raise osv.except_osv('Attention' ,'L\'affection est exclue pour le statut de ce bénéficiaire.!')

			if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('cod_benef_id' , '=' , benef), ('cod_col_id' , '=' , college), ('code_aff_id' , '=' , affection_id)]) > 0:
				raise osv.except_osv('Attention' ,'L\'affection est exclue pour ce bénéficiaire.!')

			if vals['s_acteent_id'][0][2]:

				for s_acte_id in vals['s_acteent_id'][0][2]:

					if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('code_statut_id' , '=' , statut_benef), ('cod_col_id' , '=' , college), ('code_s_acte_id' , '=' , s_acte_id)]) > 0:
						raise osv.except_osv('Attention' ,'Le sous acte est exclu pour le statut de ce bénéficiaire.!')

					if self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , police) , ('cod_benef_id' , '=' , benef), ('cod_col_id' , '=' , college), ('code_s_acte_id' , '=' , s_acte_id)]) > 0:
						raise osv.except_osv('Attention' ,'Le sous acte est exclu pour ce bénéficiaire.!')




		
		
		

		return super(mcisogem_prisecharge,self).create(cr, uid, vals, context)
	
	def benef_change(self,cr,uid,ids,benef_mat,context=None):

		if benef_mat:
			#nombre de ligne repondant au matricule saisi
			nbr_benef_1 = self.pool.get('mcisogem.benef').search_count(cr, uid, [('name', '=', benef_mat)])
			nbr_benef_2 = self.pool.get('mcisogem.benef').search_count(cr, uid, [('matric_chez_souscr', '=', benef_mat)])
			nbr_benef_3 = self.pool.get('mcisogem.benef').search_count(cr, uid, [('matric_isa', '=', benef_mat)])
			#recuperation des innformation du beneficiaire
			benef_1 = self.pool.get('mcisogem.benef').search(cr, uid, [('name','=',benef_mat)])
			benef_2 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_chez_souscr','=',benef_mat)])
			benef_3 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_isa','=',benef_mat)])


			

			exiiste_benef = False

			if benef_1:
				beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_1,context)
				exiiste_benef = True
			else:
				if benef_2:
					beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_2,context)
					exiiste_benef = True
				else:
					if benef_3:
						beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_3,context)
						exiiste_benef = True
					# else:
					# 	beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_1,context)

			if exiiste_benef:

				if (beneficiaire.sexe == 'M'):
					hospi_id = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('name','in',['HOSPITALISATION','ACTES DE CHIRURGIE','BIOLOGIE','IMAGERIE ET EXAMENS SPECIALISES','OPTIQUE','DENTAIRES','AUTRES EXAMENS'])])
					# famille_hospi = self.pool.get('mcisogem.fam.prest').browse(cr, uid, hospi_id).id

					d = {}
					d = {'facte_id':[('id',  'in', hospi_id)]}


				else:
					if ((beneficiaire.sexe == 'F') or (beneficiaire.code_statut == 'E')):
						hospi_id = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('name','in',['HOSPITALISATION','MATERNITE','ACTES DE CHIRURGIE','BIOLOGIE','IMAGERIE ET EXAMENS SPECIALISES','OPTIQUE','DENTAIRES','AUTRES EXAMENS'])])
						# famille_hospi_med = self.pool.get('mcisogem.fam.prest').browse(cr, uid, hospi_id).id

						d = {}
						d = {'facte_id':[('id',  'in', hospi_id)]}

				police = self.pool.get('mcisogem.police').browse(cr,uid,beneficiaire.police_id.id,context)
				police_stat = police.state

				reseau = False
				college_id = beneficiaire.college_id.id


				print('****police******')
				print(beneficiaire.police_id.id)

				print('****college******')
				print(beneficiaire.college_id.id)

				#historique de la police
				id_age = self.pool.get('mcisogem.histo.police').search(cr, uid, [('name', '=', beneficiaire.police_id.id),('code_college', '=', college_id)])
				histo_pol = self.pool.get('mcisogem.histo.police').browse(cr, uid, id_age, context)
				age_lim = histo_pol.limite_age_pol
				age_maj = histo_pol.age_majorite_pol


				print('**Age limite benef**')
				print(age_lim)
				print(age_maj)
				
				cr.execute('select garant_id from res_users where id=%s', (uid,))
				garant_user_id = cr.fetchone()[0]
				cr.execute('select centre_id from res_users where id=%s', (uid,))
				# centre_user_id = cr.fetchone()[0]
				centre_user_id = cr.fetchall()

				cr.execute('select centre_id from res_users where id=%s', (uid,))
				id_centre = cr.fetchone()[0]
				
				if garant_user_id:

					dn_patient = beneficiaire.dt_naiss_benef
					jour = time.strftime("%Y-%m-%d")
					age_patient = (int(jour[0:4]) - int(str(dn_patient)[0:4])) 
					# print('**Age benef**')
					# print(age_patient)

					if (beneficiaire.code_statut == 'A'):

						garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
						print('*******garant id********')
						print(garant.id)
						v={'garant_id':garant.id,'mat_princ':beneficiaire.id,'nom_princ':beneficiaire.nom,'prenom_princ':beneficiaire.prenom_benef,'age_patient':age_patient,'college_id': beneficiaire.college_id.id,'beneficiaire_id':beneficiaire.id,'police_id':beneficiaire.police_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'tel_benef':beneficiaire.tel_benef,'mail_benef':beneficiaire.adr_benef,'affichebenef':False,'affichdetail':True,'image_medium':beneficiaire.image_medium,'police_benef_id':beneficiaire.police_id.id,'college_benef_id':beneficiaire.college_id.id}	
					else:
						if ((beneficiaire.code_statut == 'C') or (beneficiaire.code_statut == 'E')):
							garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
							print('*******garant id********')
							print(garant.id)
							v={'garant_id':garant.id,'mat_princ':beneficiaire.benef_id,'nom_princ':beneficiaire.nom_assur_princ,'prenom_princ':beneficiaire.prenom_assur_princ,'age_patient':age_patient,'college_id': beneficiaire.college_id.id,'beneficiaire_id':beneficiaire.id,'police_id':beneficiaire.police_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'tel_benef':beneficiaire.tel_benef,'mail_benef':beneficiaire.adr_benef,'affichebenef':False,'affichdetail':True,'image_medium':beneficiaire.image_medium,'police_benef_id':beneficiaire.police_id.id,'college_benef_id':beneficiaire.college_id.id}	
				else:
					if centre_user_id:

						dn_patient = beneficiaire.dt_naiss_benef
						jour = time.strftime("%Y-%m-%d")
						age_patient = (int(jour[0:4]) - int(str(dn_patient)[0:4])) 
						# print('**Age benef**')
						# print(age_patient)
						if (beneficiaire.code_statut == 'A'):

							centre = self.pool.get('mcisogem.centre').browse(cr, uid, id_centre, context=context)
							print('***************************Centre*************************')
							print(centre.id)
							v={'id_centre':centre.id,'centre':centre.id,'mat_princ':beneficiaire.id,'nom_princ':beneficiaire.nom,'prenom_princ':beneficiaire.prenom_benef,'age_patient':age_patient,'college_id': beneficiaire.college_id.id,'beneficiaire_id':beneficiaire.id,'police_id':beneficiaire.police_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'tel_benef':beneficiaire.tel_benef,'mail_benef':beneficiaire.adr_benef,'affichebenef':False,'affichdetail':True,'image_medium':beneficiaire.image_medium,'police_benef_id':beneficiaire.police_id.id,'college_benef_id':beneficiaire.college_id.id}
						else:
							if ((beneficiaire.code_statut == 'C') or (beneficiaire.code_statut == 'E')):
								centre = self.pool.get('mcisogem.centre').browse(cr, uid, id_centre, context=context)
								print('***************************Centre*************************')
								print(centre.id)
								v={'id_centre':centre.id,'centre':centre.id,'mat_princ':beneficiaire.benef_id,'nom_princ':beneficiaire.nom_assur_princ,'prenom_princ':beneficiaire.prenom_assur_princ,'age_patient':age_patient,'college_id': beneficiaire.college_id.id,'beneficiaire_id':beneficiaire.id,'police_id':beneficiaire.police_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'tel_benef':beneficiaire.tel_benef,'mail_benef':beneficiaire.adr_benef,'affichebenef':False,'affichdetail':True,'image_medium':beneficiaire.image_medium,'police_benef_id':beneficiaire.police_id.id,'college_benef_id':beneficiaire.college_id.id}
					else:
						#v={'beneficiaire_id':beneficiaire.id,'police_id':beneficiaire.police_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'tel_benef':beneficiaire.tel_benef,'mail_benef':beneficiaire.adr_benef,'affichebenef':False,'affichdetail':True,'image_medium':beneficiaire.image_medium}
						v={'affichebenef':False,'affichdetail':True}

				print('***************************IB Beneficiaire*************************')
				print(beneficiaire.id)
				ctx2 = (context or {}).copy()
				ctx2['id_benef'] = beneficiaire.id

				if ((nbr_benef_1==0) and (nbr_benef_2==0) and (nbr_benef_3==0)):	
					raise osv.except_osv('Attention' ,'Beneficiaire inexistant!')
				else:
					dn_benef = beneficiaire.dt_naiss_benef
					date_new = time.strftime("%Y-%m-%d")
					age = (int(date_new[0:4]) - int(str(dn_benef)[0:4])) 
					print('**Age benef**')
					print(age)

					if self.pool.get('mcisogem.pcharge').search_count(cr,uid,[('beneficiaire_id' , '=' ,beneficiaire.id) , ('state' , '=' , 'attente')]) > 0:
						raise osv.except_osv('Attention' , 'Ce bénéficiaire a déjà une demande en attente !')



					if ((beneficiaire.statut=='R') or (beneficiaire.statut=='S')):
						raise osv.except_osv('Attention' ,'Aucune action ne peut être effectué sur ce bénéficiaire!')


				
					if  garant_user_id:
						if (garant_user_id != beneficiaire.garant_id.id):
							raise osv.except_osv('Attention' ,'Oups Dsl mauvais garant!')

						if ((police_stat=='resil') or (police_stat=='lnoir') or (police_stat=='cancel')):
							raise osv.except_osv('Attention' ,'Oups Police invalide')



						if (age_lim !=0) and (age_maj !=0):
								print('test age!!')
								if (((age_lim  < age) and (age > age_maj)) or (age_lim > age)):
									raise osv.except_osv('Attention' ,'Age invalide...')
								else:
									print('**test age**')
									print('Age inferieur a la limite')

					else:
						if centre_user_id:

							if ((police_stat=='resil') or (police_stat=='lnoir') or (police_stat=='cancel')):
								raise osv.except_osv('Attention' ,'Oups Police invalide')

							if (age_lim !=0) and (age_maj !=0):
								print('test age!!')
								if (((age_lim  < age) and (age > age_maj)) or (age_lim > age)):
									raise osv.except_osv('Attention' ,'Age invalide...')
								else:
									print('**test age**')
									print('Age inferieur a la limite')
							
							les_reseaux = []

							# on verifie si le beneficiaire est dans son réseau de soins

							les_data = self.pool.get('mcisogem.rata.reseau.police').search(cr,uid, [('police_id' , '=' , beneficiaire.police_id.id) , ('college_id' , '=' , beneficiaire.college_id.id)])

							for ld in self.pool.get('mcisogem.rata.reseau.police').browse(cr,uid,les_data):
								les_reseaux.append(ld.reseau_id.id)


							for res in les_reseaux:
								r = self.pool.get('mcisogem.tarif.nego.police').search(cr,uid,[('reseau_id' , '=' , res) , ('centre_id' , 'in' , centre_user_id[0])])


								if r:
									reseau =  True
									break


							


							if beneficiaire.police_complementaire_ids and reseau==False:

								#A revoir plus tard
								for ind_pol in beneficiaire.police_complementaire_ids[0][2]:

									les_reseaux = []


									la_police_comp = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr,uid,ind_pol)

									# on verifie si le beneficiaire est dans son réseau de soins

									les_data = self.pool.get('mcisogem.rata.reseau.police').search(cr,uid, [('police_id' , '=' , la_police_comp.police_id.id) , ('college_id' , '=' , la_police_comp.college_id.id)])


									if les_data:

										for ld in self.pool.get('mcisogem.rata.reseau.police').browse(cr,uid,les_data):
											les_reseaux.append(ld.reseau_id.id)


										for res in les_reseaux:
											r = self.pool.get('mcisogem.tarif.nego.police').search(cr,uid,[('reseau_id' , '=' , res) , ('centre_id' , '=' , centre_user_id[0])])

											if r:
												reseau =  True
											break


							

							if (reseau == False):
								raise osv.except_osv('Attention' ,'Mauvais resaux de soin!')

						else:

							raise osv.except_osv('Attention' ,'Aucun utilisateur connecté')
				
				return {'value':v,'context':ctx2, 'domain':d}

			else:
				raise osv.except_osv('Attention' ,"Ce matricule n'existe pas!")

		# else:
		# 	benef = self.pool.get('mcisogem.benef').search(cr, uid, [('name','=',benef_mat)])
		# 	beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef,context)
		# 	v={'nom_benef':'','prenom_benef':'','tel_benef':'','mail_benef':'','affichebenef':True}
		# 	return {'value':v}

	def prat_change(self,cr,uid,context,ouvr_id):
		
		if ouvr_id:
			prati_t = self.pool.get('mcisogem.praticien.tempo').browse(cr,uid,ouvr_id,context)
			prat_id =  prati_t.praticien_id
			praticien = self.pool.get('mcisogem.praticien').browse(cr,uid,prat_id,context)
			v={'nom_prat':praticien.nom_prestat,'prenom_prat':praticien.prenoms_prestat,'mail_prat':praticien.email_prestat,'tel_prat':praticien.tel1_prestat,'afficheprat':True}
			return {'value':v}
		else:
			praticien = self.pool.get('mcisogem.praticien').browse(cr,uid,ouvr_id,context)
			v={'nom_prat':'','prenom_prat':'','mail_prat':'','tel_prat':'','afficheprat':False}
			return {'value':v}


class mcisogem_motif_vpc(osv.osv):
	_name = "mcisogem.motif.vpc"
	_description = 'Motif de validation de prise en charge'


	def _get_pcharge(self, cr, uid, context):
		if context.get('pcharge'):
			return context.get('pcharge')
		else:
			return False

	def _get_type(self, cr, uid, context):
		if context.get('type_motif'):
			return context.get('type_motif')
		else:
			return False

	def _get_affiche_jours(self, cr, uid, context):
		if context.get('pcharge'):
			pcharge_id = context.get('pcharge')
			f_acte_id = self.pool.get('mcisogem.pcharge').browse(cr,uid,pcharge_id,context).facte_id.id

			famille_acte = self.pool.get('mcisogem.fam.prest').browse(cr, uid, f_acte_id)
			if (famille_acte.name == "HOSPITALISATION"):
				return True
			else :
				return False
			

	_columns = {
		'pcharge_id': fields.many2one('mcisogem.pcharge', 'Prise en charge',required=True),
		'type' : fields.text('Type de motif',required=True),
		'name' : fields.text('Motif',required=True),
		'nbr_jour_acc' : fields.integer('Nombre de jours accordés'),
		'affiche_jours' : fields.boolean(''),
	}


	def button_valider(self, cr, uid , ids, context=None):
		print('OK')

	def create(self, cr, uid , vals , context):
		# vals['name'] = str(vals['name']).upper()
		data =  self.browse(cr, uid, context=context)
		vals['pcharge_id'] = context['pcharge']
		pcharge = self.pool.get('mcisogem.pcharge').search(cr,uid,[('id' , '=' , vals['pcharge_id'])])
		pcharge_data = self.pool.get('mcisogem.pcharge').browse(cr, uid, pcharge)
		dure_courier = pcharge_data.dure_courier
		dure_demande = pcharge_data.dure_demande

		if (dure_demande >= (vals['nbr_jour_acc'])):
		
			if vals['type'] == 'VALIDATION':
				# self.pool.get('mcisogem.pcharge').write(cr,uid,pcharge_data.ids,{'state':'valide', 'motif_valider':vals['name'], 'nbr_jour_acc':vals['nbr_jour_acc'],'dure_courier':(dure_courier + vals['nbr_jour_acc']) },context=context)
				cr.execute("update mcisogem_pcharge set state='valide', motif_valider = %s, nbr_jour_acc = %s,dure_courier = %s,ident= %s  where id = %s", (vals['name'],vals['nbr_jour_acc'],(dure_courier + vals['nbr_jour_acc']), uid,pcharge_data.id,))

			if vals['type'] == 'REJET':
				# self.pool.get('mcisogem.pcharge').write(cr,uid,pcharge_data.ids,{'state':'rejet', 'motif_rejet':vals['name']},context=context)
				cr.execute("update mcisogem_pcharge set state='rejet', motif_rejet = %s where id = %s", (vals['name'],pcharge_data.id,))
		else:
			raise osv.except_osv('Attention' ,'Le nombre de jours accordé doits être inferieur ou égale au nombre de jours demandés!')


		
	
		return super(mcisogem_motif_vpc , self).create(cr,uid,vals,context)

	_defaults = {
		'pcharge_id' : _get_pcharge,
		'type' : _get_type,
		'affiche_jours':_get_affiche_jours,
	}


class mcisogem_prorogation(osv.osv):
	_name = 'mcisogem.prorogation'
	_description = 'Demande de prorogation'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_mail_post_access = 'read'


	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)


	def _get_pcharge_id(self, cr,uid,context):
		if context.get('pcharge_id'):
			return context.get('pcharge_id')
		else:
			return False

	
			

	_columns = {
		'centre_id' : fields.integer('Identifiant Centre'),
		'centre' : fields.many2one('mcisogem.centre','Centre'),
		'beneficiaire_id' : fields.many2one('mcisogem.benef', 'Beneficiaire',required=True),
		'praticien_id' :  fields.many2one('mcisogem.praticien', 'Medecin'),
		'quantite' : fields.integer('Quantite'),
		'montant_total_med' : fields.integer('Montant total des médicaments'),
		'date_hospi' : fields.date('Date d\'hospitalisation'),
		'dure_demande' : fields.integer('Durée en jours deja accordés'),
		'dur_sup_demande' : fields.integer('Prorogation demande' , required=True),
		'nbr_jour_acc' : fields.integer('Durée en jours accordés'),
		'monatant' : fields.integer('Montant à payer'),
		'affection_id' : fields.many2one('mcisogem.affec', 'Affection',required=True),
		'facte_id' : fields.many2one('mcisogem.fam.prest', 'Famille acte',required=True),
		'acte_id' : fields.many2one('mcisogem.nomen.prest', 'Acte', required=True),
		'image': fields.binary("Image",
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.prorogation': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.prorogation': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),

		'motif_prorogation' : fields.text('Motif prorogation',required=True),
		'motif_valider' : fields.text('Motif pour Validation'),
		'motif_rejet' : fields.text('Motif pour rejet'),
		'state': fields.selection([
			('nouveau', "Nouveau"),
			('attente', " En attente"),
			('valide', "Acceptée"),
			('rejet', "Rejetée"),
			
		   
		], 'Status', required=True, readonly=True),

		'num_prorogation':fields.integer('Numero :'),
		'pcharge_id' : fields.many2one('mcisogem.pcharge', 'prise en charge'),
		'ident' : fields.many2one('res.users'),
		'mail_benef': fields.char('Mail'),
		'nom_benef' : fields.char('Nom'),
		'prenom_benef' : fields.char('Prenoms'),
		'tel_benef' : fields.char('Telephone'),
		'nom_prat' : fields.char('Nom'),
		'prenom_prat' : fields.char('Prenoms'),
		'mail_prat' : fields.char('Mail'),
		
	}
	
	# _defaults ={'state':'nouveau','affichebenef':True,'afficheprat':False,'affichdetail':False, 'quantite':1}	
	_defaults ={
		'state':'nouveau',
		'pcharge_id' : _get_pcharge_id,
		
		
	}
	_rec_name = 'pcharge_id'

	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "UTILISATEUR MEDICAL" or group_obj.name == "RESPONSABLE MEDICAL" or group_obj.name == "MEDECIN CONSEIL":
					return [('state', '=', 'attente')]
				if group_obj.name == "PRESTATAIRE":
					return [('state', '=', 'valide')]
			return False
		else:
			return False


	def print_recherche(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids, [], context=context)

		return {
				'type': 'ir.actions.report.xml',
				'report_name': 'mcisogem_isa.report_bon_prorogation',
				'data': data,
		}
			


	def valide_demande(self, cr, uid, ids, context=None):
		
		prorgation_id = self.browse(cr, uid, ids[0], context=context).id

		prorgation_table = self.search(cr, uid, [('id', '=', prorgation_id)])

		prorgation_data = self.browse(cr, uid, prorgation_table)

		ctx = (context or {}).copy()
		ctx['prorogation'] = prorgation_id
		ctx['type_motif'] = 'VALIDATION'
		ctx['form_view_ref'] = 'view_mcisogem_motif_vpro_form'
		
		return {
		  'name':'Motif',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.motif.vpro',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}

	def rejet_demande(self, cr, uid, ids, context=None):
		
		prorgation_id = self.browse(cr, uid, ids[0], context=context).id

		prorgation_table = self.search(cr, uid, [('id', '=', prorgation_id)])

		prorgation_data = self.browse(cr, uid, prorgation_table)

		ctx = (context or {}).copy()
		ctx['prorogation'] = prorgation_id
		ctx['type_motif'] = 'REJET'
		ctx['form_view_ref'] = 'view_mcisogem_motif_vpro_form'
		
		return {
		  'name':'Motif',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.motif.vpro',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}

	
	def annuler_assures(self, cr, uid, ids, context=None):
		statut = self.pool.get('mcisogem.prorogation').browse(cr,uid,ids,context)
		print('******************************')
		print(statut.state)

		if(statut.state=='valide'):
			# self.write(cr, uid, ids, {'state':'attente', 'motif_valider' : '', 'nbr_jour_acc' : 0}, context=context)
			cr.execute("update mcisogem_prorogation set state='attente', motif_valider = '' , nbr_jour_acc = 0  where id = %s", (ids[0],))
			# self.pool.get('mcisogem.pcharge').write(cr,uid,statut.pcharge_id.id,{'dure_courier':statut.dure_demande },context=context)
			cr.execute("update mcisogem_pcharge set dure_courier = %s  where id = %s", (statut.dure_demande,statut.pcharge_id.id,))

		if(statut.state=='rejet'):
			# self.write(cr, uid, ids, {'state':'attente', 'motif_rejet' : ''}, context=context)
			cr.execute("update mcisogem_prorogation set state='attente', motif_rejet = ''  where id = %s", (ids[0],))
		
	
	def pcharge_change(self,cr,uid,context,valeur):
		
		if valeur:
			
			pcharge = self.pool.get('mcisogem.pcharge').browse(cr,uid,valeur,context)
			v={'centre_id':pcharge.centre.id,'image_medium':pcharge.image_medium,'beneficiaire_id':pcharge.beneficiaire_id.id,'nom_benef' :pcharge.nom_benef,'prenom_benef' :pcharge.prenom_benef,'mail_benef':pcharge.mail_benef,'tel_benef' :pcharge.tel_benef,'centre' :pcharge.centre.id,'praticien_id' :pcharge.praticien_id.id,'nom_prat':pcharge.nom_prat,'prenom_prat':pcharge.prenom_prat, 'affection_id' : pcharge.affection_id.id, 'facte_id' : pcharge.facte_id.id, 'acte_id' : pcharge.acte_id.id, 'date_hospi' : pcharge.date_hospi, 'dure_demande' : pcharge.dure_courier}
			return {'value':v}
		else:
			
			v={'centre_id':'','image_medium':'','beneficiaire_id':'','nom_benef' :'','prenom_benef' :'','mail_benef':'','tel_benef' :'','centre' :'','praticien_id' :'','nom_prat':'','prenom_prat':'', 'affection_id' : '', 'facte_id' : '', 'acte_id' : '', 'date_hospi' : '', 'dure_demande' : ''}
			return {'value':v}
	


	def create(self, cr, uid, vals, context=None):

		########### envoi des notifications aux responsable médical pour demande de prise en charge
		msg = str("Une nouvelle demande de prorogation vient d'être émise. Vous devez l'examiner pour validation.")

		cr.execute("select id from res_groups where name='RESPONSABLE MEDICAL'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation de demande de prorogation",
			context=context
			)

			###################################################""

		if 'centre_id' in vals :
			cr.execute("SELECT max(num_prorogation) FROM mcisogem_prorogation WHERE centre_id = %s", (vals['centre_id'],))
			num_prorogation = cr.fetchone()[0]

			print("***************************************")
			print(num_prorogation)
			if not num_prorogation:
				num_prorogation = 1
			else:
				num_prorogation = num_prorogation+1
		

		if 'pcharge_id' in vals:
			
			data_pcharge = self.pool.get('mcisogem.pcharge').search(cr, uid, [('id', '=', vals['pcharge_id'])])
			pcharge = self.pool.get('mcisogem.pcharge').browse(cr,uid,data_pcharge,context)
			

		donne={}

		donne=self.pcharge_change(cr, uid ,0, pcharge.id)['value']
		vals['beneficiaire_id']=donne['beneficiaire_id']
		vals['nom_benef']=donne['nom_benef']
		vals['prenom_benef'] = donne['prenom_benef']
		vals['tel_benef'] = donne['tel_benef']
		vals['mail_benef'] = donne['mail_benef']
		vals['image_medium'] = donne['image_medium']
		vals['centre']=donne['centre']
		vals['praticien_id']=donne['praticien_id']
		vals['nom_prat'] = donne['nom_prat']
		vals['prenom_prat'] = donne['prenom_prat']
		vals['affection_id'] = donne['affection_id']
		vals['facte_id'] = donne['facte_id']
		vals['acte_id']=donne['acte_id']
		vals['date_hospi']=donne['date_hospi']
		vals['dure_demande'] = donne['dure_demande']
		vals['state'] = 'attente'
		vals['num_prorogation'] = num_prorogation



		return super(mcisogem_prorogation,self).create(cr, uid, vals, context)




class mcisogem_motif_vpro(osv.osv):
	_name = "mcisogem.motif.vpro"
	_description = 'Motif de validation des prorogations'


	def _get_prorogation(self, cr, uid, context):
		if context.get('prorogation'):
			return context.get('prorogation')
		else:
			return False

	def _get_type(self, cr, uid, context):
		if context.get('type_motif'):
			return context.get('type_motif')
		else:
			return False

	_columns = {
		'prorogation_id': fields.many2one('mcisogem.prorogation', 'Prise en charge',required=True),
		'nbr_jour_acc' : fields.integer('Durée en jours accordés'),
		'type' : fields.text('Type de motif',required=True),
		'name' : fields.text('Motif',required=True),
	}

	def button_valider(self, cr, uid , ids, context=None):
		print('OK')

	def create(self, cr, uid , vals , context):
		# vals['name'] = str(vals['name']).upper()
		data =  self.browse(cr, uid, context=context)
		vals['prorogation_id'] = context['prorogation']
		prorogation = self.pool.get('mcisogem.prorogation').search(cr,uid,[('id' , '=' , vals['prorogation_id'])])
		prorogation_data = self.pool.get('mcisogem.prorogation').browse(cr, uid, prorogation)
		dure_proro = vals['nbr_jour_acc']
		pcharge_id = prorogation_data.pcharge_id.id
		# pcharge = self.pool.get('mcisogem.pcharge').browse(cr, uid, pcharge_id)
		# dure_courier = pcharge.dure_courier
		dure_demande = prorogation_data.dur_sup_demande

		if (dure_demande >= (vals['nbr_jour_acc'])):
		
			if vals['type'] == 'VALIDATION':
				# self.pool.get('mcisogem.prorogation').write(cr,uid,prorogation_data.ids,{'state':'valide', 'motif_valider':vals['name'], 'nbr_jour_acc':vals['nbr_jour_acc']},context=context)
				cr.execute("update mcisogem_prorogation set state='valide', motif_valider = %s , nbr_jour_acc = %s, ident = %s  where id = %s", (vals['name'],vals['nbr_jour_acc'],uid,prorogation_data.id,))
				
				pcharge = self.pool.get('mcisogem.pcharge').browse(cr, uid, pcharge_id)
				dure_courier = pcharge.dure_courier
				# cr.execute("select dure_courier from mcisogem_pcharge where id=%s", (pcharge_id,))
				# dure_courier = cr.fetchone()[0]
				
				
				# self.pool.get('mcisogem.pcharge').write(cr,uid,pcharge.id,{'dure_courier':(dure_courier + dure_proro) },context=context)
				cr.execute("update mcisogem_pcharge set dure_courier = %s  where id = %s", ((dure_courier + dure_proro),pcharge.id,))

			if vals['type'] == 'REJET':
				# self.pool.get('mcisogem.prorogation').write(cr,uid,prorogation_data.ids,{'state':'rejet', 'motif_rejet':vals['name']},context=context)
				cr.execute("update mcisogem_prorogation set state='rejet', motif_rejet = %s where id = %s", (vals['name'],prorogation_data.id,))
		else:
			raise osv.except_osv('Attention' ,'Le nombre de jours accordé doits être inferieur ou égale au nombre de jours demandés!')


		
	
		return super(mcisogem_motif_vpro , self).create(cr,uid,vals,context)

	_defaults = {
		'prorogation_id' : _get_prorogation,
		'type' : _get_type,
	}



class mcisogem_info_demande_garant(osv.osv):
	_name = 'mcisogem.info_demande_garant'
	_columns = {
		'name' : fields.char('Name'),
	}

	def button_pcharge(self, cr, uid , ids, vals, context=None):
		print('***le button_pcharge***')
		
		ctx11 = (context or {}).copy()
		ctx11['form_view_ref'] = 'view_pcharge_tree'
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demande de prise en charge',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.pcharge',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('centre', '=',centre_user_id)],
		}
	def button_enttente(self, cr, uid , ids, vals, context=None):
		print('***le bouton police_garant***')
		
		ctx11 = (context or {}).copy()
		ctx11['form_view_ref'] = 'view_entente_tree'
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demandes d\'entente préalable',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.entente',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('centre_id', '=',centre_user_id)],
		}

	def button_prorogation(self, cr, uid , ids, vals, context=None):
		print('***le bouton police_garant***')
		
		ctx11 = (context or {}).copy()
		ctx11['form_view_ref'] = 'view_prorogation_tree'
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demandes de prorogation',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.prorogation',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('centre', '=',centre_user_id)],
		}

	def button_incorporation(self, cr, uid , ids, vals, context=None):
		print('***le bouton incorporation garant***')
		
		ctx11 = (context or {}).copy()
		ctx11['form_view_ref'] = 'view_benf_incorpo_tree'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demandes d\'incorporations',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.benf_incorpo',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('garant_id', '=',garant_user_id)],
		}

	def button_retrait(self, cr, uid , ids, vals, context=None):
		print('***le bouton retrait garant***')
		
		ctx11 = (context or {}).copy()
		ctx11['tree_view_ref'] = 'view_retrait_tree'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demandes des retraits',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.retrait',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('garant_id', '=',garant_user_id)],
		}

	def button_suspend(self, cr, uid , ids, vals, context=None):
		print('***le bouton suspend garant***')
		
		ctx11 = (context or {}).copy()
		ctx11['tree_view_ref'] = 'view_suspend_tree'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demandes de suspensions',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.suspend',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('garant_id', '=',garant_user_id)],
		}

class mcisogem_info_demande_inter(osv.osv):
	_name = 'mcisogem.info_demande_inter'
	_columns = {
		'name' : fields.char('Name'),
	}


	def button_incorporation(self, cr, uid , ids, vals, context=None):
		print('***le bouton incorporation inter***')
		
		ctx11 = (context or {}).copy()
		ctx11['form_view_ref'] = 'view_benf_incorpo_tree'
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		interm_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demandes d\'incorporations',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.benf_incorpo',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('intermediaire_id', '=',interm_user_id)],
		}

	def button_retrait(self, cr, uid , ids, vals, context=None):
		print('***le bouton retrait inter***')
		
		ctx11 = (context or {}).copy()
		ctx11['tree_view_ref'] = 'view_retrait_tree'
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		interm_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demandes des retraits',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.retrait',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('intermediaire_id', '=',interm_user_id)],
		}

	def button_suspend(self, cr, uid , ids, vals, context=None):
		print('***le bouton suspend inter***')
		
		ctx11 = (context or {}).copy()
		ctx11['tree_view_ref'] = 'view_suspend_tree'
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		interm_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des demandes de suspensions',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.suspend',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx11,
		  'domain': [('intermediaire_id', '=',interm_user_id)],
		}



	
class mcisogem_souscripteur_garant(osv.osv):
	_name = 'mcisogem.souscripteur.garant'
	_columns = {
		'souscripteur_id':fields.integer('Identifiant souscripteur'),
		'name' : fields.char('souscripteur'),
	}

class mcisogem_college_garant(osv.osv):
	_name = 'mcisogem.college.garant'
	_columns = {
		'college_id':fields.integer('Identifiant college'),
		'name' : fields.char('Collège'),
	}

class mcisogem_police_inc_garant(osv.osv):
	_name = 'mcisogem.police.inc.garant'
	_description = 'police pour incorporation par garant'
	_columns = {
		'name':fields.char(''),
	}

	def button_police_inc(self, cr, uid , ids, vals, context=None):
		print('***le bouton police garant***')
		
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'police_garant_inc_tree'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'police_garant_inc_tree')[1]

		return {
		  'name':'Polices',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.police',
		   'views': [(tree_id , 'tree')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx15,
		  'domain': [('garant_id', '=',garant_user_id)],
		}

	def button_retrait(self, cr, uid , ids, vals, context=None):
		print('***le bouton retrait benef garant***')
		
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'benef_garant_tree'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'benef_garant_tree')[1]

		return {
		  'name':'Beneficiaire',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.benef',
		   'views': [(tree_id , 'tree')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx15,
		  'domain': [('garant_id', '=',garant_user_id)],
		}

	def button_suspend(self, cr, uid , ids, vals, context=None):
		print('***le bouton suspension benef garant***')	
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'benef_garant_tree2'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'benef_garant_tree2')[1]

		return {
		  'name':'Beneficiaire',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.benef',
		  'views': [(tree_id , 'tree')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx15,
		  'domain': [('garant_id', '=',garant_user_id)],
		}

class mcisogem_benef_inc_inter(osv.osv):
	_name = 'mcisogem.benef.inc.inter'
	_description = 'beneficiaire pour incorporation par intermediaire'
	_columns = {
		'name':fields.char('Matricule'),
		'beneficiaire_id' : fields.integer('Id beneficiaire'),
		'nom' : fields.char('Nom'),
		'prenom' : fields.char('Prenoms'),
		'statut_benef' : fields.char('Statut'),
		'intermediaire_id' : fields.many2one('mcisogem.courtier' , 'Intermediaire'),
		'police_id' : fields.many2one('mcisogem.police', 'Polices'),
	}

	def button_demande_retrait(self,cr,uid,ids,context):
		benef = self.browse(cr, uid, ids[0], context=context).beneficiaire_id
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		inter_user_id = cr.fetchone()[0]
		if inter_user_id:
			ctx7 = (context or {}).copy()
			ctx7['beneficiaire'] = benef
			ctx7['tree_view_ref'] = 'view_retrait_tree'
			ctx7['form_view_ref'] = 'mcisogem_retrait_form'
			return {
				'name' : 'Demande de retrait',
				'view_type' : 'form',
				'view_mode' : 'form,tree',
				'res_model' : 'mcisogem.retrait',
				'view_id':False,
				'target':'current',
				'domain' : [('intermediaire_id', '=', inter_user_id)],
				'type' : 'ir.actions.act_window',
				'context': ctx7,

			}

	def button_demande_suspend(self,cr,uid,ids,context):
		benef = self.browse(cr, uid, ids[0], context=context).beneficiaire_id
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		inter_user_id = cr.fetchone()[0]
		if inter_user_id:
			ctx7 = (context or {}).copy()
			ctx7['beneficiaire'] = benef
			ctx7['tree_view_ref'] = 'view_suspend_tree'
			ctx7['form_view_ref'] = 'mcisogem_suspend_form'
			return {
				'name' : 'Demande de suspension',
				'view_type' : 'form',
				'view_mode' : 'form,tree',
				'res_model' : 'mcisogem.suspend',
				'view_id':False,
				'target':'current',
				'domain' : [('intermediaire_id', '=', inter_user_id)],
				'type' : 'ir.actions.act_window',
				'context': ctx7,

			}

class mcisogem_police_inc_inter(osv.osv):
	_name = 'mcisogem.police.inc.inter'
	_description = 'police pour incorporation par intermediaire'
	_columns = {
		'name':fields.char(''),
	}

	def button_police_inc(self, cr, uid , ids, vals, context=None):
		print('***le bouton police inter***')
		
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'police_inter_inc_tree'
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		inter_user_id = cr.fetchone()[0]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'police_inter_inc_tree')[1]

		return {
		  'name':'Polices',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.police',
		   'views': [(tree_id , 'tree')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx15,
		  'domain': [('courtier_id', '=',inter_user_id)],
		}

	def button_retrait(self, cr, uid , ids, vals, context=None):
		print('***le bouton retrait benef garant***')
		cr.execute('DELETE  FROM mcisogem_benef_inc_inter WHERE create_uid=%s', (uid,))
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		inter_user_id = cr.fetchone()[0]

		cr.execute('select distinct id from mcisogem_police where courtier_id =%s', (inter_user_id,)) 
		police_liste = cr.fetchall()
		print('*****LISTE des polices par intermediaire*****')
		print(police_liste)
		for ind_pol in police_liste:
			print(ind_pol) 
			cr.execute('select distinct id from mcisogem_benef where police_id =%s', (ind_pol,)) 
			benef_liste = cr.fetchall()
			for ind_benef in benef_liste:	
				benef = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef,context)
				data = {}
				
				data['beneficiaire_id'] = benef.id
				data['name'] = benef.name
				data['nom'] = benef.nom	
				data['prenom'] = benef.prenom_benef
				data['statut_benef'] = benef.code_statut
				data['intermediaire_id'] = inter_user_id
				data['police_id'] = benef.police_id.id
				existe = self.pool.get('mcisogem.benef.inc.inter').search(cr, uid , [('beneficiaire_id', '=', benef.id),('name', '=', benef.name),('nom', '=', benef.nom),('prenom', '=', benef.prenom_benef),('statut_benef', '=', benef.code_statut),('intermediaire_id', '=', inter_user_id),('police_id', '=', benef.police_id.id)])
				if (not existe) :
					self.pool.get('mcisogem.benef.inc.inter').create(cr,uid,data,context)
			
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'benef_inter_tree'
		
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'benef_inter_tree')[1]

		return {
		  'name':'Beneficiaire',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.benef.inc.inter',
		   'views': [(tree_id , 'tree')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx15,
		  'domain': [('intermediaire_id', '=',inter_user_id)],
		}

	def button_suspend(self, cr, uid , ids, vals, context=None):
		print('***le bouton suspension benef inter***')	
		cr.execute('DELETE  FROM mcisogem_benef_inc_inter WHERE create_uid=%s', (uid,))
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		inter_user_id = cr.fetchone()[0]

		cr.execute('select distinct id from mcisogem_police where courtier_id =%s', (inter_user_id,)) 
		police_liste = cr.fetchall()
		print('*****LISTE des polices par intermediaire*****')
		print(police_liste)
		for ind_pol in police_liste:
			print(ind_pol) 
			cr.execute('select distinct id from mcisogem_benef where police_id =%s', (ind_pol,)) 
			benef_liste = cr.fetchall()
			for ind_benef in benef_liste:	
				benef = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef,context)
				data = {}
				
				data['beneficiaire_id'] = benef.id
				data['name'] = benef.name
				data['nom'] = benef.nom	
				data['prenom'] = benef.prenom_benef
				data['statut_benef'] = benef.code_statut
				data['intermediaire_id'] = inter_user_id
				data['police_id'] = benef.police_id.id
				existe = self.pool.get('mcisogem.benef.inc.inter').search(cr, uid , [('beneficiaire_id', '=', benef.id),('name', '=', benef.name),('nom', '=', benef.nom),('prenom', '=', benef.prenom_benef),('statut_benef', '=', benef.code_statut),('intermediaire_id', '=', inter_user_id),('police_id', '=', benef.police_id.id)])
				if (not existe) :
					self.pool.get('mcisogem.benef.inc.inter').create(cr,uid,data,context)
			
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'benef_inter_tree2'
		
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'benef_inter_tree2')[1]

		return {
		  'name':'Beneficiaire',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.benef.inc.inter',
		   'views': [(tree_id , 'tree')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx15,
		  'domain': [('intermediaire_id', '=',inter_user_id)],
		}

	
		

class mcisogem_info_garant(osv.osv):
	_name = 'mcisogem.info_garant'
	_columns = {
		'name':fields.char(''),
	}

	def button_beneficiaire(self, cr, uid, ids, vals, context=None):
		print('***le bouton benef_garant***')
		
		ctx10 = (context or {}).copy()
		ctx10['tree_view_ref'] = 'mcisogem_benef_tree'
		ctx10['form_view_ref'] = 'view_mcisogem_benef_form'
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_benef_tree')[1]
		form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_mcisogem_benef_form')[1]
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des beneficaires',
		  'view_type':'form',
		  'view_mode':'tree,form',
		  'res_model':'mcisogem.benef',
		  'views': [(tree_id ,'tree') , (form_id , 'form')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx10,
		  'domain': [('garant_id', '=',garant_user_id)],
		}

	def button_police(self, cr, uid , ids, vals, context=None):
		print('***le bouton police_garant***')
		
		ctx10 = (context or {}).copy()
		
		# ctx10['form_view_ref'] = 'mcisogem_police_tree'
		ctx10['form_view_ref'] = 'mcisogem_police_tree'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]

		return {
		  'name':'Liste des polices',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.police',
		  'view_id':False,
		  'type':'ir.actions.act_window',
		  'context':ctx10,
		  'domain': [('garant_id', '=',garant_user_id)],
		}


	def button_college(self, cr, uid , ids, vals, context=None):
		print('****le button college garant*****')
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT college_id FROM mcisogem_histo_prime WHERE garant_id=%s', (garant_user_id,))
			college_liste = cr.fetchall()
			print(college_liste)
			for ind_col in college_liste:
				college = self.pool.get('mcisogem.college').browse(cr, uid, ind_col,context)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data,context)

			ctx10 = (context or {}).copy()
			ctx10['tree_view_ref'] = 'college_garant_tree'
			#form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'college_garant_tree')[1]
			print('***Ok college***')
			return {
			  'name':'College liste',
			  'view_type':'form',
			  'view_mode':'tree',
			  'res_model':'mcisogem.college.garant',
			  #'views': [(form_id, 'tree')],
			  'view_id': False,
			  'domain': [('create_uid', '=',uid)],
			  'type':'ir.actions.act_window',
			  'context':ctx10,
			}

	def button_souscripteur(self, cr, uid , ids, vals, context=None):
		print('****le button souscripteur garant*****')
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE garant_id=%s', (garant_user_id,))
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol,context)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data,context)
				

			ctx10 = (context or {}).copy()
			ctx10['tree_view_ref'] = 'souscripteur_garant_tree'
			
			print('***Ok souscripteur***')
			return {
			  'name':'souscripteur liste',
			  'view_type':'form',
			  'view_mode':'tree',
			  'res_model':'mcisogem.souscripteur.garant',
			 
			  'view_id': False,
			  'domain': [('create_uid', '=',uid)],
			  'type':'ir.actions.act_window',
			  'context':ctx10,
			}



class mcisogem_recherche_benef_garant(osv.osv):
	_name = 'mcisogem.recherche.benef.garant'

	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			return garant.id
		else:
			return False
	def _get_user(self, cr,uid,context):
		
		if uid:
			return uid
		else:
			return False

	_columns = {
		'users' : fields.integer('Identifiant Utilisateur'),
		'garant_id' : fields.integer('Garant'),
		'garant' : fields.many2one('mcisogem.garant','Garant'),
		'police_id' : fields.many2one('mcisogem.police','Police'),
		'souscripteur_id_tempo' : fields.many2one('mcisogem.souscripteur.garant','Souscripteur'),
		'college_id_tempo' : fields.many2one('mcisogem.college.garant','Collège'),
		'souscripteur_id' : fields.many2one('mcisogem.souscripteur','Souscripteur'),
		'college_id' : fields.many2one('mcisogem.college','Collège'),
		'beneficiaire_id' : fields.one2many('mcisogem.recherche.benef.garant2','critere_id',' '),
		'recherche' : fields.char('Recherche'),
		'date_d' : fields.date('Debut'),
		'date_f' : fields.date('Fin'),
		'stat_incorp' : fields.boolean('Incorporation'),
		# 'regime_id' : fields.many2one('mcisogem.image.carte.1','regime', required=True),
		
	}
	_rec_name = "recherche"
	_defaults = {
		'garant_id' : _get_garant,
		'recherche': 'Recherche',
		'users': _get_user,
		'stat_incorp': False,
	
	}

	def onchange_sous_col(self,cr,uid,context,valeur):
		
		if valeur:
			### remplissage de la table college_garant ###

			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT college_id FROM mcisogem_histo_prime WHERE garant_id=%s', (valeur,))
			college_liste = cr.fetchall()
			print(college_liste)
			for ind_col in college_liste:
				college = self.pool.get('mcisogem.college').browse(cr, uid, ind_col,context)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data,context)

			### remplissage de la table souscripteur_garant ###

			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE garant_id=%s', (valeur,))
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol,context)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data,context)


	def onchange_sous_col2(self,cr,uid,context,valeur,valeur2):
		
		if valeur:
			### remplissage de la table college_garant ###

			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT id FROM mcisogem_college WHERE police_id=%s', (valeur,))
			college_liste = cr.fetchall()
			print ('******college liste******')
			print(college_liste)
			for ind_col in college_liste:
				
				college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
				print ('******college ind******')
				print(college_ids)
				college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data)

			### remplissage de la table souscripteur_garant ###

			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE id=%s', (valeur,))
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

			v = {}
			v = {'college_id_tempo':''}
			return {'value' : v}

		else:
			if valeur2:
				### remplissage de la table college_garant ###

				cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
				cr.execute('SELECT DISTINCT college_id FROM mcisogem_histo_prime WHERE garant_id=%s', (valeur2,))
				college_liste = cr.fetchall()
				print(college_liste)
				for ind_col in college_liste:
					college = self.pool.get('mcisogem.college').browse(cr, uid, ind_col)
					print(ind_col)
					print(college.id)
					print(college.name)
					data = {}
					data['college_id'] = college.id
					data['name'] = college.name
					self.pool.get('mcisogem.college.garant').create(cr,uid,data)

				### remplissage de la table souscripteur_garant ###

				cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
				cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE garant_id=%s', (valeur2,))
				police_liste = cr.fetchall()
				print(police_liste)
				for ind_pol in police_liste:
					souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
					print(ind_pol)
					print(souscripteur.id)
					print(souscripteur.name)
					data = {}
					data['souscripteur_id'] = souscripteur.id
					data['name'] = souscripteur.name
					self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

				v = {}
				v = {'police_id':'','souscripteur_id_tempo':'','college_id_tempo':''}
				return {'value' : v}
			else:
				cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))

				cr.execute('SELECT id FROM mcisogem_college')
				college_liste = cr.fetchall()
				print ('******college liste******')
				print(college_liste)
				for ind_col in college_liste:
					
					college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
					print ('******college ind******')
					print(college_ids)
					college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
					print(ind_col)
					print(college.id)
					print(college.name)
					data = {}
					data['college_id'] = college.id
					data['name'] = college.name
					self.pool.get('mcisogem.college.garant').create(cr,uid,data)


				cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))

				cr.execute('SELECT id FROM mcisogem_souscripteur')
				police_liste = cr.fetchall()
				print(police_liste)
				for ind_pol in police_liste:
					souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
					print(ind_pol)
					print(souscripteur.id)
					print(souscripteur.name)
					data = {}
					data['souscripteur_id'] = souscripteur.id
					data['name'] = souscripteur.name
					self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)


	def create(self, cr, uid, vals, context=None):
		
		
		if 'souscripteur_id_tempo' in vals:
			souscripteur = self.pool.get('mcisogem.souscripteur.garant').browse(cr, uid, vals['souscripteur_id_tempo'],context).souscripteur_id
			vals['souscripteur_id'] = souscripteur
		


		if 'college_id_tempo' in vals:
			college = self.pool.get('mcisogem.college.garant').browse(cr, uid, vals['college_id_tempo'],context).college_id


			vals['college_id'] = college
			
		

		if 'garant_id' in vals:
			
			vals['garant'] = vals['garant_id']

		vals['aff_print'] = True
 
		return super(mcisogem_recherche_benef_garant, self).create(cr,uid,vals,context)
		

	def print_recherche(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids, [], context=context)
		critere = self.browse(cr, uid, ids[0], context)

		nbr_benef = self.pool.get('mcisogem.recherche.benef.garant2').search_count(cr, uid, [('create_uid', '=', uid)])
		print('****nombre de bene recherche*****')
		print(nbr_benef)
		# raise osv.except_osv('Attention' ,'stop!')

		if (nbr_benef != 0 ):

			if (not critere.stat_incorp):

				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'mcisogem_isa.report_benef_garant',
						'data': data,
				}
			else:

				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'mcisogem_isa.report_benef_inc_garant',
						'data': data,
				}
		else:
			raise osv.except_osv('Impossible' ,'aucun élement à imprimer!')

	# def print_carte(self, cr, uid, ids, context=None):
	# 	data = self.read(cr, uid, ids, [], context=context)
	# 	critere = self.browse(cr, uid, ids[0], context)

	# 	nbr_benef = self.pool.get('mcisogem.recherche.benef.garant2').search_count(cr, uid, [('create_uid', '=', uid)])
	# 	print('****nombre de bene recherche*****')
	# 	print(nbr_benef)
	# 	# raise osv.except_osv('Attention' ,'stop!')

	# 	if (nbr_benef != 0 ):
	# 		return {
	# 				'type': 'ir.actions.report.xml',
	# 				'report_name': 'mcisogem_isa.report_benef_carte',
	# 				'data': data,
	# 		}	
	# 	else:
	# 		raise osv.except_osv('Impossible' ,'aucun élement à imprimer!')

	def button_recherche(self, cr, uid , ids, context=None):

		critere = self.browse(cr, uid, ids[0])
		garant = critere.garant_id
		police = critere.police_id.id
		college_id = critere.college_id_tempo.id
		college = self.pool.get('mcisogem.college.garant').browse(cr, uid, college_id,context).college_id
		souscripteur_id = critere.souscripteur_id_tempo.id
		souscripteur = self.pool.get('mcisogem.souscripteur.garant').browse(cr, uid, souscripteur_id,context).souscripteur_id
		# regime = critere.regime_id.id
		
		debut = critere.date_d
		fin = critere.date_f

		stat_incorp = critere.stat_incorp


		data = {}
		data['police_id'] = police
		data['souscripteur_id'] = souscripteur
		data['college_id'] = college
		data['stat_incorp'] = stat_incorp
		# data['regime_id'] = regime
		
		self.pool.get('mcisogem.recherche.benef.garant').write(cr,uid,ids[0],data,context)
		
		data = {}
		statut_p_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ASSURE PRINCIPAL',)])
		statut_p = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_p_id, context).id

		statut_c_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'CONJOINT',)])
		statut_c = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_c_id, context).id

		statut_e_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ENFANT',)])
		statut_e = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_e_id, context).id

		statut_d_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'AUTRE CONJOINT(E)',)])
		statut_d = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_d_id, context).id

		statut_k_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ENFANT SUPPLEMENTAIRE',)])
		statut_k = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_k_id, context).id

		statut_x_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'AUTRE PARENT',)])
		statut_x = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_x_id, context).id
		
		statut_g_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'GENITEUR (ASCENDANT)',)])
		statut_g = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_g_id, context).id
		
		requette = "SELECT id From mcisogem_benef WHERE statut_benef = {} AND ".format(statut_p)
		requette2 = "SELECT id From mcisogem_benef WHERE "
		if garant == False:
			requette += '1=1 '
			requette2 += '1=1 '
		else:
			requette += 'garant_id = {} '.format(garant)
			requette2 += 'garant_id = {} '.format(garant)
		if police == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else : 
			if police != "":
				requette += 'AND police_id = {} '.format(police)
				requette2 += 'AND police_id = {} '.format(police)
		if (not college):
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if college != "":
				requette += 'AND college_id = {} '.format(college)
				requette2 += 'AND college_id = {} '.format(college)
		if (not souscripteur):
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if souscripteur != "":
				requette += 'AND souscripteur_id = {} '.format(souscripteur)
				requette2 += 'AND souscripteur_id = {} '.format(souscripteur)
		if stat_incorp == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if stat_incorp == True:
				requette += "AND creat_incorpo = 'I' "
				requette2 += "AND creat_incorpo = 'I' "

		if (fin and debut):
			if (fin>debut):
				debut = datetime.strftime(datetime.strptime(debut, "%Y-%m-%d"), "%Y-%m-%d %H:%M:%S.%f")
				fin = datetime.strftime(datetime.strptime(fin, "%Y-%m-%d"), "%Y-%m-%d %H:%M:%S.%f")
				# debut = critere.date_d
				# fin = critere.date_f
				type_debut = type(debut)
				type_fin = type(fin)
				print('** les dates converties **')
				print(type_debut)
				print(debut)
				print(type_fin)
				print(fin)
				# raise osv.except_osv('Attention' ,'Oups #TDC! dates valides')
				requette += "AND create_date BETWEEN '{}' ".format(debut)
				requette2 += "AND create_date BETWEEN '{}' ".format(debut)
				requette +="AND '{}' ".format(fin)
				requette2 +="AND '{}' ".format(fin)
			
			else :
				
					raise osv.except_osv('Attention' ,'Oups #TDC! dates invalides')
		else:
			if (((fin) and ( not debut)) or ((not fin) and (debut))):
				raise osv.except_osv('Attention' ,'Oups #TDC! dates invalides')
			else:
				if ((not fin) and ( not debut)):
				# 	raise osv.except_osv('Attention' ,'Oups #TDC! veuillez remplir correctement les dates')
					requette += 'AND 1=1'
					requette2 += 'AND 1=1 '

		req2 = requette2

		print('** la requette **')
		print(requette)
		print('** identifiant critere **')
		print(ids[0])
		#raise osv.except_osv('Attention' ,'Oups #TDC!')

		cr.execute('DELETE  FROM mcisogem_recherche_benef_garant2 WHERE create_uid = %s', (uid,))
		########### A
		cr.execute(requette)
		beneficiaire_liste = cr.fetchall()
		print('**Lise des beneficiaire recherchés**')
		print(beneficiaire_liste)
		
		
		for ind_benef in beneficiaire_liste:
			beneficiairep = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef, context)
			print(beneficiairep.name)
			data = {}
			
			data['beneficiaire'] = beneficiairep.name
			data['nom_benef'] = beneficiairep.nom
			data['prenom_benef'] = beneficiairep.prenom_benef
			data['souscripteur_id'] = beneficiairep.souscripteur_id.id
			data['date'] = beneficiairep.dt_naiss_benef
			data['date_ef'] = beneficiairep.dt_effet
			data['statut'] = beneficiairep.statut_benef.id
			data['genre'] = beneficiairep.sexe
			data['image_medium'] = beneficiairep.image_medium
			# data['regime_id'] = regime
			data['critere_id'] = ids[0]

			self.pool.get('mcisogem.recherche.benef.garant2').create(cr, uid, data, context)

			########### C 

			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {} '.format(statut_c)
			# requette2 +='OR statut_benef = {}'.format(statut_d)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2

			for ind_benef_c in beneficiairec_liste:
				print(ind_benef_c)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_c, context)
				print(beneficiairec.name)
				data2 = {}

				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef.garant2').create(cr, uid, data2, context)

			########### D

			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {} '.format(statut_d)
			# requette2 +='OR statut_benef = {}'.format(statut_d)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2

			for ind_benef_c in beneficiairec_liste:
				print(ind_benef_c)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_c, context)
				print(beneficiairec.name)
				data2 = {}

				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef.garant2').create(cr, uid, data2, context)

			########### E 


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_e)
			# requette2 +='OR statut_benef = {}'.format(statut_k)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef.garant2').create(cr, uid, data2, context)


			########### K


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_k)
			# requette2 +='OR statut_benef = {}'.format(statut_k)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef.garant2').create(cr, uid, data2, context)

			########### G 


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_g)
			# requette2 +='OR statut_benef = {}'.format(statut_x)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef.garant2').create(cr, uid, data2, context)


			########### X


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_x)
			# requette2 +='OR statut_benef = {}'.format(statut_x)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef.garant2').create(cr, uid, data2, context)


class mcisogem_recherche_benef_garant2(osv.osv):
	_name = 'mcisogem.recherche.benef.garant2'

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

	_columns = {
		'critere_id': fields.many2one('mcisogem.recherche.benef.garant','critere'),
		'beneficiaire' : fields.char('Matricule'),
		'nom_benef' : fields.char('Nom'),
		'prenom_benef' : fields.char('Prenom'),
		'souscripteur_id' : fields.many2one('mcisogem.souscripteur','Souscripteur'),
		'ass_p_id' : fields.many2one('mcisogem.benef','Adhérent'),
		'date' : fields.datetime('Date de naissance'),
		'date_ef' : fields.datetime('Date effet'),
		'statut' : fields.many2one('mcisogem.stat.benef' , 'Statut Bénéficiare'),
		'genre' : fields.char('Genre'),
		# 'regime_id' : fields.many2one('mcisogem.image.carte.1','regime'),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.recherche.benef.garant2': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.recherche.benef.garant2': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
	
	}
	_rec_name = "beneficiaire"


class mcisogem_benf_incorpo(osv.osv):
	_name = 'mcisogem.benf_incorpo'
	_description = 'Beneficiaire incorpore'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	_mail_post_access = 'read'


	GROUPE = [
		('A+', 'A+'),
		('A-', 'A-'),
		('B+', 'B+'),
		('B-', 'B-'),
		('O+', 'O+'),
		('O-', 'O-'),
		('AB+', 'AB+'),
		('AB-', 'AB-')
	]

	MOTIF = [
		('0', 'Suspension Tier payant'),
		('1', 'Suspension totale'),
		('2', 'Décès')
	]

	SEXE = [
		('M', 'Masculin'),
		('F', 'Feminin')
	]

	LIEN =[('E', 'Enfant') , ('C' , 'Conjoint')]

	def _get_group(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel  where uid=%s', (uid,))
		group_id = cr.fetchone()[0]
		group_obj = self.pool.get('res.groups').browse(cr, uid, group_id, context=context)
		if group_obj.name == 'Financial Manager':
			return True
		else:
			return False
	
	
	def _get_cod_gest(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		return gest_obj.code_centre
	

	def _get_regime_centre(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		return gest_obj.avoir_ro


	def _get_cod_lang(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		cod_gest_id = cr.fetchone()[0]
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
		# lang_obj = self.pool.get('mcisogem.langue').browse(cr, uid, gest_obj.langue_id, context=context)
		return gest_obj.langue_id.name
	
	def _get_cod_gest_id(self, cr, uid, context=None):
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))        
		cod_gest_id = cr.fetchone()[0]
		return cod_gest_id
	
	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)


	def _get_garant(self, cr,uid,context):
		if context.get('garant'):
			print('*****garant inter******')
			print(context.get('garant'))
			return context.get('garant')
		else:
			cr.execute('select garant_id from res_users where id=%s', (uid,))
			garant_user_id = cr.fetchone()[0]
			if garant_user_id:
				garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
				print('*******garant id********')
				print(garant.id)
				return garant.id
			else:
				return False

	def _get_date_effet(self, cr,uid,context):
		if context.get('date_eff'):
			return context.get('date_eff')
		else:
			return False

	def _get_assure_princ(self, cr,uid,context):
		if context.get('benef_id'):
			return context.get('benef_id')
		else:
			return False


	def _get_est_depend(self , cr , uid, context):
		if context.get('est_assur_depend'):
			return True
		else:
			return False


	def _get_police(self, cr,uid,context):
		if context.get('police'):
			return (context.get('police'))
			
		else:
			if context.get('police_inc_garant'):
				return (context.get('police_inc_garant'))
			else:
				print('*****Aucune police en contexte******')
				return False

	def _get_benef(self, cr,uid,context):
		print('*****Je suis dans le context de beneficiaire******')
		if context.get('benef_incp_id'):
			print('*****valeur benef_id context******')
			print(context.get('benef_incp_id'))
			return (context.get('benef_incp_id'))
		else:
			
			return False

	def _get_statut_benef(self, cr,uid,context):
		if context.get('statut_benef'):
			return context.get('statut_benef')
		else:
			stat = self.pool.get('mcisogem.stat.benef').search(cr,uid,[('cod_statut_benef' , '=' , 'A')])
			statut = self.pool.get('mcisogem.stat.benef').browse(cr,uid,stat).id
			return statut	
	

	def _get_aff_benf(self, cr,uid,context):
		if context.get('aff_benf') == False:
			return context.get('aff_benf')
		else:
			if context.get('aff_benf_pol'):
				return False
			else:
				return True

	def _get_aff_benf_pol(self, cr,uid,context):
		if context.get('aff_benf_pol'):
			return context.get('aff_benf_pol')
		else:
			return False


	def _get_aff_benf_i(self, cr,uid,context):
		if context.get('aff_benf_i'):
			return context.get('aff_benf_i')
		else:
			return False
	

	def _get_garant_user(self, cr, uid, context=None):
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
		print('*******garant id********')
		print(garant.id)
		return garant.id

	def _get_inter_user(self, cr, uid, context=None):
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		interm_user_id = cr.fetchone()[0]
		if interm_user_id:
			inter = self.pool.get('mcisogem.courtier').browse(cr, uid, interm_user_id, context=context)
			print('*******intermediaire id********')
			print(inter.id)
			return inter.id
		else:
			return False

	def _get_statut_a(self, cr, uid, context=None):
		statut_search = self.pool.get('mcisogem.stat.benef').search(cr,uid,[('cod_statut_benef' , '=' , 'A')])
		statut = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut_search).id
		if statut:
			print('############# Statut A ID #############')
			print(statut)
			return statut
		else:
			return False





	_columns = {
		'garant_id' : fields.integer('Garant'),
		'garant' : fields.many2one('mcisogem.garant','Garant'),
		'intermediaire_id' : fields.integer('intermediaire'),
		'intermediaire' : fields.integer('mcisogem.courtier','intermediaire'),
		'police_id': fields.many2one('mcisogem.police', "Police", required=True),
		'id_police': fields.integer("Polices"),
		'college_id': fields.many2one('mcisogem.college', 'Collège' , required=True),
		'periode_id' : fields.many2one('mcisogem.account.period' , 'Periode'),
		'exercice_id' : fields.many2one('mcisogem.exercice' , 'Exercice'),
		'est_assur_depend' : fields.boolean('Dépendant ?'),
		'benef_id' : fields.many2one('mcisogem.benf_incorpo' , 'Assuré Principal Dépendant'),
		'benef_p_id' : fields.many2one('mcisogem.benef' , 'Assuré Principal Garant'),
		'benef_pol_id' : fields.many2one('mcisogem.benef' , 'Assuré Principal'),
		'nom_assur_princ' : fields.char('Nom'),
		'prenom_assur_princ' : fields.char('Prénoms'),
		'statut_benef' : fields.many2one('mcisogem.stat.benef' , 'Statut de Bénéficiare' ),
		'code_statut' : fields.char(''),
		'creat_incorpo' : fields.selection([('C','creation')] , ' ' , required=True),
		'motif_suspension' : fields.selection(MOTIF,'Motif de suspension',select=True),
		
		'avenant_id':fields.many2one('mcisogem.avenant', 'Avenant'),
		'souscripteur_id': fields.many2one('mcisogem.souscripteur', 'Souscripteur', required=True),
		'matric_benef': fields.char('matricule',readonly=True),
		'new_matricule_benef' : fields.char('Matricule' , size=15 ),
		
		'nom': fields.char('Nom', required=True),
		'nom_jeun_fille': fields.char('Nom de jeune fille'),
		'prenom_benef': fields.char('prenom',required=True),
		'adr_benef': fields.char('adresse'),
		'cod_bp_benef': fields.char('code BP'),
		'bp_benef': fields.char('Bp benef'),
		'tel_benef': fields.char('Téléphone',required=True),
		'fax_benef': fields.char('Fax'),
		
		'dt_naiss_benef': fields.date('Date de naissance', required=True),
		'lieu_naiss_benef':fields.char('Lieu de naissance'),
		

		'sexe': fields.selection(SEXE, 'Genre',required=True),
		'mod_paiem_benef': fields.integer('mod_paiem_benef'),
		'num_banq_benef': fields.char('Code Banque'),
		'num_guichet_benef': fields.char('No Guichet'),
		'num_compt_benef': fields.char('No Compte Bancaire'),
		'cle_rib_benef': fields.char('Clé Rib'),
		'cum_an_recl_benef': fields.integer('cum_an_recl_benef'),
		'cum_an_recl_fam': fields.integer('cum_an_recl_fam'),
		'poids_benef': fields.char('Poids bénef'),
		'taille_benef': fields.char('Taille'),
		'dt_mensuration': fields.datetime('Date mensuration'),
		'group_sang_benef': fields.selection(GROUPE, 'Groupe Sanguin', select=True),
		'bl_trt_en_cours': fields.char('Bl. Traitement en cours'),
		'trt_en_cours_until':fields.char('Traitement en cours'),
		'specif_trav_benef': fields.char('Specifications travail'),
		'predisp_benef': fields.char('Predispositon'),
		'allergie_benef': fields.char('Allergie'),
		'anteced_medic': fields.char('Antecedant médical'), 
		'anteced_obstetric': fields.char('Antecedant obstetric'), 
		'anteced_fam': fields.char('Antecedants familiaux'),
		'anteced_chir': fields.char('Antecedant chirugical'), 
		'transfus_benef': fields.char('Transfusion'), 
		'prothese_benef': fields.char('Prothese'), 
		'obs_benef': fields.char('obs_benef'),
		'image': fields.binary("Image",
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.benf_incorpo': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.benf_incorpo': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		'numavenant': fields.integer('numero avenant'), 
		'numcarte': fields.char('numero carte'), 
		'tmp_stamp_photo': fields.char('tmp_stamp_photo'), 
		'cod_photo': fields.integer('cod_photo'),
		'photo_ben': fields.char('photo_ben'),
		'affiche': fields.boolean('',),
		'affiche_col':fields.boolean('',),
		'ident_centre': fields.many2one('mcisogem.centre.gestion', 'Centre de gestion'),
		'code_gest': fields.char('libelle_gest', size=10),
		'code_langue': fields.char('code_langue', size=10),
		'state': fields.selection([
			('nouveau', "Nouveau"),
			('attente', "En attente"),
			('valide', "Valider"),
			('retire', "Retirer"),
			('annuler', "Annuler"),
		], 'Status', required=True, readonly=True),
		
		
		
		'valide_quittance': fields.integer('valide_quittance'),
		'date_quittance': fields.datetime('Date quittance'),
		
		'aff_benf_i': fields.boolean(''),
		'aff_benf': fields.boolean(''),
		'aff_benf_pol': fields.boolean(''),
		'aff_non_fille' : fields.boolean(''),
		'aff_detail' : fields.boolean(''),
		'statut_a' : fields.integer('Id statut a'),
	}


	_rec_name = "nom"

	_defaults = {
		'aff_non_fille' : False,
		'aff_detail' : False,
		'aff_benf_pol':_get_aff_benf_pol,
		'aff_benf':_get_aff_benf,
		'aff_benf_i': _get_aff_benf_i,
		
		'id_police':_get_police,
		'police_id': _get_police,
		
		
		'state':'nouveau',
		
		'est_assur_depend' : _get_est_depend,
		'valide_quittance' : 0,
		
		
		'benef_id' : _get_assure_princ,
		
		# 'avoir_ss_id' : _get_regime_centre,
		'affiche':_get_group,
		'benef_id' : _get_assure_princ,
		'code_gest': _get_cod_gest,
		'ident_centre': _get_cod_gest_id,
		'code_langue': _get_cod_lang,
		
		'garant_id' : _get_garant,
		'garant' : _get_garant,
		'intermediaire_id' : _get_inter_user,
		'intermediaire' : _get_inter_user,
		
		'creat_incorpo' : 'C', 
		'statut_benef' : _get_statut_benef,
		'statut_a' : _get_statut_a,
		# 'college_id' : 3,

		
	} 

	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "UTILISATEUR PRODUCTION" or group_obj.name == "RESPONSABLE PRODUCTION":
					return [('state', '=', 'attente')]
			return False
		else:
			return False

	def onchange_ss_id(self, cr, uid, ids, avoir_ss_id, context=None):
		v = {}
		if avoir_ss_id:
			v = {'avoir_ss_id':True , 'ss_id':''}
			return {'value' : v}

	def onchange_code_statut(self, cr, uid, ids, statut, context=None):
		v = {}
		statut = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut)
		if statut:
			v = {'code_statut':statut.cod_statut_benef}
			return {'value' : v}


	

	def onchange_benef_p_id(self, cr, uid, ids, benef_id, context=None):
		v = {}

		if benef_id:
			print('*** valeur benef p id ***')
			print(benef_id)
			s_benef = self.pool.get('mcisogem.benef').search(cr,uid,[('id','=',benef_id)])
			benef_data = self.pool.get('mcisogem.benef').browse(cr,uid,s_benef)
			v = {'nom_assur_princ':benef_data.nom , 'prenom_assur_princ':benef_data.prenom_benef,'police_id':benef_data.police_id,'college_id':benef_data.college_id,'souscripteur_id':benef_data.souscripteur_id, 'aff_detail' : True}
			return {'value' : v}
		else:
			v = {'aff_detail' : False}
			return {'value' : v}

	def onchange_benef_id(self, cr, uid, ids, benef_id, context=None):
		v = {}

		if benef_id:
			print('*** valeur benef id ***')
			print(benef_id)
			s_benef = self.pool.get('mcisogem.benf_incorpo').search(cr,uid,[('id','=',benef_id)])
			benef_data = self.pool.get('mcisogem.benf_incorpo').browse(cr,uid,s_benef)
			v = {'nom_assur_princ':benef_data.nom , 'prenom_assur_princ':benef_data.prenom_benef,'police_id':benef_data.police_id,'college_id':benef_data.college_id,'souscripteur_id':benef_data.souscripteur_id, 'aff_detail' : True}
			return {'value' : v}
		else:
			v = {'aff_detail' : False}
			return {'value' : v}


	def onchange_sexe(self, cr, uid, ids, sexe, context=None):
		if sexe:
			print('***valeu de sexe***')
			print(sexe)
			v = {}
			if (sexe == "M"):
				return {'value': {'aff_non_fille':False}}
			else:
				if (sexe == "F"):
					return {'value': {'aff_non_fille':True}}

	def onchange_assur_depend(self, cr, uid, ids, est_assur_depend, context=None):
	
		statut_search = self.pool.get('mcisogem.stat.benef').search(cr,uid,[('cod_statut_benef' , '=' , 'A')])
		statut = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut_search).id

		v = {}
		v = {'benef_id':False, 'benef_p_id':False, 'benef_pol_id':False, 'nom_assur_princ' : '' , 'prenom_assur_princ' : '' , 'statut_benef' : statut}
		d = {}
		d = {'statut_benef':[('id','=',statut)]}
		
		if est_assur_depend == True:
			d = {'statut_benef':[('id','!=',statut)]}
			v = {'statut_benef' : int(statut) + 1}

			# print('############# Statut A ID + 1 #############')
			# print(int(statut) + 1)

		return {'value' : v , 'domain':d}



	def onchange_police(self, cr, uid, ids, police_id, context=None):        
		if not police_id:
			return False
		else:

			s_police = self.pool.get('mcisogem.police').search(cr,uid,[('id' , '=' , police_id)])
			la_police = self.pool.get('mcisogem.police').browse(cr,uid,s_police,context)

			datedujour = time.strftime('%Y-%m-%d', time.localtime())
			cr.execute("select distinct code_college from mcisogem_histo_police where name=%s and dt_eff_histo_pol >=%s", (police_id, datedujour))
			lescollegespolices = cr.dictfetchall()

			cr.execute("delete from mcisogem_college_temporaire where create_uid=%s", (uid,))

			for col in lescollegespolices:                 
				 cr.execute("insert into mcisogem_college_temporaire (create_uid,write_uid,name) values(%s, %s, %s)", (uid, uid, col['code_college']))


			return {'value' : {'souscripteur_id' : la_police.souscripteur_id}}


	def button_histo_benef_incorp(self,cr,uid,ids,context):
		benef_inc_data = self.browse(cr, uid, ids, context=context)


		#la police du beneficiaire
		police_search = self.pool.get('mcisogem.police').search(cr,uid,[('id' , '=' , benef_inc_data.police_id.id)])
		police_data = self.pool.get('mcisogem.police').browse(cr,uid,police_search)

		statut_search = self.pool.get('mcisogem.stat.benef').search(cr,uid,[('cod_statut_benef' , '=' , 'A')])
		statut = self.pool.get('mcisogem.stat.benef').browse(cr,uid,statut_search).id

		ctx12 = (context or {}).copy()
		ctx12['garant'] = police_data.garant_id.id
		ctx12['police'] = police_data.id
		ctx12['ccollege'] = benef_inc_data.college_id.id
	
		ctx12['action'] = 'histo'
		ctx12['benef_id'] = ids[0]
		ctx12['aff_benf_i'] = True
		ctx12['aff_benf'] = False

		ctx12['est_assur_depend'] = True
		ctx12['nom'] = benef_inc_data.nom
		ctx12['prenom'] = benef_inc_data.prenom_benef
		ctx12['num_interne_police'] = benef_inc_data.police_id.id
		ctx12['statut_benef'] = int(statut) + 1
		form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_benf_incorpo_form')[1]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_benf_incorpo_tree')[1]
		

		return {
				'name':'Incorporation de dépendants',
				'view_type':'form',
				'view_mode':'tree,form,kanban',
				'res_model':'mcisogem.benf_incorpo',
				'target':'current',
				'views': [(tree_id ,'tree') , (form_id, 'form')],
				'view_id': form_id,
				'type':'ir.actions.act_window',
				'domain':[('benef_id', '=',ctx12['benef_id'] )],
				'context':ctx12,
				'nodestroy':True,
				}


	def button_action_valider(self, cr, uid, ids, context=None):
		benef_incop=self.pool.get('mcisogem.benf_incorpo').browse(cr,uid,ids,context)
		ctx5 = (context or {}).copy()
		ctx5['form_view_ref'] = 'view_mcisogem_benef_form'
		form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_mcisogem_benef_form')[1]
		ctx5['garant'] = benef_incop.garant_id
		ctx5['police'] = benef_incop.police_id.id
		ctx5['college_id'] = benef_incop.college_id.id
		ctx5['est_assur_dependi'] = benef_incop.est_assur_depend
		if (benef_incop.benef_p_id.id ):
			ctx5['benef_idi'] = benef_incop.benef_p_id.id
		ctx5['nom_assur_princ'] = benef_incop.nom_assur_princ
		ctx5['prenom_assur_princ'] = benef_incop.prenom_assur_princ
		print('*********************state benef**************************')
		print(benef_incop.statut_benef.id)
		ctx5['statut_benef'] = benef_incop.statut_benef.id
		ctx5['code_statut'] = benef_incop.code_statut
		ctx5['creat_incorpo'] = 'I'
		ctx5['motif_suspension'] = benef_incop.motif_suspension
		ctx5['souscripteur_id'] = benef_incop.souscripteur_id.id
		ctx5['matric_benef'] = benef_incop.matric_benef
		ctx5['new_matricule_benef'] = benef_incop.new_matricule_benef
		ctx5['nom'] = benef_incop.nom
		ctx5['nom_jeun_fille'] = benef_incop.nom_jeun_fille
		ctx5['prenom_benef'] = benef_incop.prenom_benef
		ctx5['adr_benef'] = benef_incop.adr_benef
		ctx5['cod_bp_benef'] = benef_incop.cod_bp_benef
		ctx5['bp_benef'] = benef_incop.bp_benef
		ctx5['tel_benef'] = benef_incop.tel_benef
		ctx5['fax_benef'] = benef_incop.fax_benef
		ctx5['dt_naiss_benef'] = benef_incop.dt_naiss_benef
		ctx5['lieu_naiss_benef'] = benef_incop.lieu_naiss_benef
		ctx5['sexe'] = benef_incop.sexe
		ctx5['mod_paiem_benef'] = benef_incop.mod_paiem_benef
		ctx5['num_banq_benef'] = benef_incop.num_banq_benef
		ctx5['num_guichet_benef'] = benef_incop.num_guichet_benef
		ctx5['num_compt_benef'] = benef_incop.num_compt_benef
		ctx5['cle_rib_benef'] = benef_incop.cle_rib_benef
		ctx5['cum_an_recl_benef'] = benef_incop.cum_an_recl_benef
		ctx5['cum_an_recl_fam'] = benef_incop.cum_an_recl_fam
		ctx5['poids_benef'] = benef_incop.poids_benef
		ctx5['taille_benef'] = benef_incop.taille_benef
		ctx5['dt_mensuration'] = benef_incop.dt_mensuration
		ctx5['group_sang_benef'] = benef_incop.group_sang_benef
		ctx5['bl_trt_en_cours'] = benef_incop.bl_trt_en_cours
		ctx5['trt_en_cours_until'] = benef_incop.trt_en_cours_until
		ctx5['specif_trav_benef'] = benef_incop.specif_trav_benef
		ctx5['predisp_benef'] = benef_incop.predisp_benef
		ctx5['allergie_benef'] = benef_incop.allergie_benef
		ctx5['anteced_medic'] = benef_incop.anteced_medic
		ctx5['anteced_obstetric'] = benef_incop.anteced_obstetric
		ctx5['anteced_fam'] = benef_incop.anteced_fam
		ctx5['anteced_chir'] = benef_incop.anteced_chir
		ctx5['transfus_benef'] = benef_incop.transfus_benef
		ctx5['prothese_benef'] = benef_incop.prothese_benef
		ctx5['obs_benef'] = benef_incop.obs_benef
		ctx5['image'] = benef_incop.image
		ctx5['image_medium'] = benef_incop.image_medium
		ctx5['image_small'] = benef_incop.image_small
		ctx5['numavenant'] = benef_incop.numavenant
		ctx5['numcarte'] = benef_incop.numcarte
		ctx5['tmp_stamp_photo'] = benef_incop.tmp_stamp_photo
		ctx5['cod_photo'] = benef_incop.cod_photo
		ctx5['photo_ben'] = benef_incop.photo_ben
		ctx5['affiche_col'] = benef_incop.affiche_col
		ctx5['valide_quittance'] = benef_incop.valide_quittance
		ctx5['date_quittance'] = benef_incop.date_quittance
		ctx5['id_benf_i'] = benef_incop.id


		return {
			'name' : 'Bénéficiare',
			'view_type' : 'form',
			'view_mode' : 'form',
			'res_model' : 'mcisogem.benef',
			'views': [(form_id , 'form')],
		  	'view_id':form_id,
			'type':'ir.actions.act_window',
			'context':ctx5,
		}


 



		

	def button_action_retirer(self, cr, uid, ids, context=None):
		
		self.write(cr, uid, ids, {'state':'retire'}, context=context)
		

	def button_action_annuler(self, cr, uid, ids, context=None):
		statut = self.pool.get('mcisogem.benf_incorpo').browse(cr,uid,ids,context)
		print('******************************')
		print(statut.state)

		if(statut.state=='valide'):
			self.write(cr, uid, ids, {'state':'attente'}, context=context)
		if(statut.state=='retire'):
			self.write(cr, uid, ids, {'state':'valide'}, context=context)
		if(statut.state=='suspend'):
			self.write(cr, uid, ids, {'state':'valide'}, context=context)

	def create(self, cr, uid, vals, context=None):
		vals['state'] = 'attente'
		code_periode = time.strftime("%m/%Y", time.localtime())
		periode_id = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',code_periode)])
		periode_data = self.pool.get('mcisogem.account.period').browse(cr,uid,periode_id)
		vals['periode_id'] = periode_data.id
		vals['exercice_id'] = periode_data.exercice_id.id
		print('***************test benef*************')
		print(vals['benef_id'])

		if vals['benef_p_id'] :
			donne1=self.onchange_benef_p_id(cr, uid ,context, vals['benef_p_id'])['value']
		
			vals['nom_assur_princ'] = donne1['nom_assur_princ']
			vals['prenom_assur_princ'] = donne1['prenom_assur_princ']
			vals['police_id'] = donne1['police_id'].id
			vals['souscripteur_id'] = donne1['souscripteur_id'].id
			vals['college_id'] = donne1['college_id'].id
		print('***************test benef p*************')
		print(vals['benef_p_id'])
		if vals['benef_id'] :
			donne=self.onchange_benef_id(cr, uid ,context, vals['benef_id'])['value']
		
			vals['nom_assur_princ'] = donne['nom_assur_princ']
			vals['prenom_assur_princ'] = donne['prenom_assur_princ']
			vals['police_id'] = donne['police_id'].id
			vals['souscripteur_id'] = donne['souscripteur_id'].id
			vals['college_id'] = donne['college_id'].id

		if (not (vals['benef_id']) and (not vals['benef_p_id'])) : 
			donne2=self.onchange_police(cr, uid ,context, vals['id_police'])['value']
			vals['souscripteur_id'] = donne2['souscripteur_id'].id

		

		########### envoi des notifications a Mci pour incorporation
		msg = str("Une nouvelle demande d'incorporation vient d'être émise. Vous devez l'examiner pour validation.")

		cr.execute("select id from res_groups where name='RESPONSABLE PRODUCTION'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation de demande d'incorporation",
			context=context
			)

			###################################################""
		print('***copie dans benef incorp***28/10/2015')
		print(vals['garant_id'])

		
		return super(mcisogem_benf_incorpo, self).create(cr,uid,vals,context)





class mcisogem_retrait(osv.osv):

	_name = 'mcisogem.retrait'
	_description = 'Demande de retrait'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_mail_post_access = 'read'

	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			print('*******garant id********')
			print(garant.id)
			return garant.id
		else:
			return False

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

	def _get_beneficiare(self, cr,uid,context):
		if context.get('beneficiaire'):
			print('**id benef btn retrait**')
			print(context.get('beneficiaire'))
			return context.get('beneficiaire')

		else:
			return False

	def _get_inter_user(self, cr, uid, context=None):
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		interm_user_id = cr.fetchone()[0]
		if interm_user_id:
			inter = self.pool.get('mcisogem.courtier').browse(cr, uid, interm_user_id, context=context)
			print('*******intermediaire id********')
			print(inter.id)
			return inter.id
		else:
			return False

		
	_columns = {
		'garant_id' : fields.integer('Identifiant Garant'),
		'garant' : fields.many2one('mcisogem.garant','Garant'),
		'police_id' : fields.many2one('mcisogem.police', 'Police'),
		'intermediaire_id' : fields.integer('Identifiant intermediaire'),
		'intermediaire' : fields.many2one('mcisogem.courtier','intermediaire'),
		'periode_id' : fields.many2one('mcisogem.account.period' , 'Periode'),
		'exercice_id' : fields.many2one('mcisogem.exercice' , 'Exercice'),
		'beneficiaire_id' : fields.many2one('mcisogem.benef', 'Beneficiaire', required=True),
		'benef_id' : fields.integer('Matricule'),
		'motif' : fields.text('Motif',required=True),
		'image': fields.binary("Image",
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.retrait': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.retrait': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		'state': fields.selection([
			('nouveau', "Nouveau"),
			('attente', "En attente"),
			('valide', "Acceptée"),
			('rejet', "Rejetée"),  
		], 'Status', required=True, readonly=True),
		'num_retrait':fields.integer('Numero :'),
		'nom_benef' : fields.char('Nom'),
		'prenom_benef' : fields.char('Prenoms'),
		# 'affichebenef': fields.boolean(''),
		# 'affichdetail': fields.boolean(''),
		'stat_benef_init' : fields.char('Statut du beneficiaire'),
	}


	_defaults ={'state':'nouveau', 'beneficiaire_id': _get_beneficiare, 'benef_id':_get_beneficiare,'garant_id': _get_garant,'garant': _get_garant, 'intermediaire_id':_get_inter_user , 'intermediaire':_get_inter_user}
	# _defaults ={'state':'nouveau','affichebenef':False,'affichdetail':False}
	_rec_name = 'beneficiaire_id'


	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "UTILISATEUR PRODUCTION" or group_obj.name == "RESPONSABLE PRODUCTION":
					return [('state', '=', 'attente')]
			return False
		else:
			return False

	def valide_demande(self, cr, uid, ids, context=None):
		
		self.write(cr, uid, ids, {'state':'valide'}, context=context)
		cr.execute("update mcisogem_retrait set state='valide' where id = %s", (ids[0],))

		data_retrait = self.browse(cr, uid, ids[0], context)

		benef = self.pool.get('mcisogem.benef').browse(cr,uid,data_retrait.benef_id,context)
		# self.write(cr,uid,ids[0],{'stat_benef_init':benef.statut},context)
		cr.execute("update mcisogem_retrait set stat_benef_init= %s where id = %s", (benef.statut,ids[0],))
		self.pool.get('mcisogem.benef').write(cr,uid,data_retrait.benef_id,{'statut':'R'},context)

		########### envoi des notifications aux responsables production pour une demande valide
		msg = str("Une demande de retrait vient d'être validée !")

		cr.execute("select id from res_groups where name='UTILISATEUR PRODUCTION'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation Médical",
			context=context
			)

			###################################################


	def rejet_demande(self, cr, uid, ids, context=None):
		
		# self.write(cr, uid, ids, {'state':'rejet'}, context=context)
		cr.execute("update mcisogem_retrait set state='rejet' where id = %s", (ids[0],))
		data_retrait = self.browse(cr, uid, ids[0], context)

		if data_retrait.stat_benef_init:
			self.pool.get('mcisogem.benef').write(cr,uid,data_retrait.benef_id,{'statut':data_retrait.stat_benef_init},context)
		########### envoi des notifications aux responsables production pour une demande rejete
		msg = str("Une demande de retrait vient d'être rejetée !")

		cr.execute("select id from res_groups where name='UTILISATEUR PRODUCTION'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation Médical",
			context=context
			)

			###################################################

	
	def annuler_assures(self, cr, uid, ids, context=None):
		statut = self.pool.get('mcisogem.entente').browse(cr,uid,ids,context)
		print('******************************')
		print(statut.state)

		if(statut.state=='valide'):
			# self.write(cr, uid, ids, {'state':'attente'}, context=context)
			cr.execute("update mcisogem_retrait set state='attente' where id = %s", (ids[0],))
		if(statut.state=='rejet'):
			# self.write(cr, uid, ids, {'state':'attente'}, context=context)
			cr.execute("update mcisogem_retrait set state='attente' where id = %s", (ids[0],))

	def benef_change(self,cr,uid,ids,benef_mat,context=None):
		if benef_mat:
			
			beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_mat,context)
			v={'garant_id':beneficiaire.garant_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'image_medium':beneficiaire.image_medium, 'police_id':beneficiaire.police_id.id}	
			return {'value':v}



	def create(self, cr, uid, vals, context=None):

		########### envoi des notifications aux responsables production pour une demande de retrait
		msg = str("Une nouvelle demande de retrait vient d'être émise. Vous devez l'examiner pour validation.")

		cr.execute("select id from res_groups where name='RESPONSABLE PRODUCTION'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation de demande de retrait",
			context=context
			)

			###################################################
		# pour le niveau garant
		if 'garant_id' in vals :
			cr.execute("SELECT max(num_retrait) FROM mcisogem_retrait WHERE garant_id = %s", (vals['garant_id'],))
			num_retrait = cr.fetchone()[0]

			print("***************************************")
			print(num_retrait)
			if not num_retrait:
				num_retrait = 1

			else:
				num_retrait = num_retrait+1

		code_periode = time.strftime("%m/%Y", time.localtime())
		periode_id = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',code_periode)])
		periode_data = self.pool.get('mcisogem.account.period').browse(cr,uid,periode_id)
		vals['periode_id'] = periode_data.id
		vals['exercice_id'] = periode_data.exercice_id.id

		donne={}

		donne=self.benef_change(cr,uid,0,vals['benef_id'])['value']

		vals['nom_benef']=donne['nom_benef']
		vals['prenom_benef'] = donne['prenom_benef']
		vals['image_medium'] = donne['image_medium']
		vals['num_retrait'] = num_retrait
		vals['state'] = "attente"
		
		

		return super(mcisogem_retrait,self).create(cr, uid, vals, context)



class mcisogem_suspend(osv.osv):

	_name = 'mcisogem.suspend'
	_description = 'Demande de suspension'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_mail_post_access = 'read'

	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			print('*******garant id********')
			print(garant.id)
			return garant.id
		else:
			return False

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

	def _get_beneficiare(self, cr,uid,context):
		if context.get('beneficiaire'):
			print('**id benef btn suspend**')
			print(context.get('beneficiaire'))
			return context.get('beneficiaire')
		else:
			return False
	
	def _get_inter_user(self, cr, uid, context=None):
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		interm_user_id = cr.fetchone()[0]
		if interm_user_id:
			inter = self.pool.get('mcisogem.courtier').browse(cr, uid, interm_user_id, context=context)
			print('*******intermediaire id********')
			print(inter.id)
			return inter.id
		else:
			return False

	_columns = {
		'garant_id' : fields.integer('Identifiant Garant'),
		'garant' : fields.many2one('mcisogem.garant','Garant'),
		'police_id' : fields.many2one('mcisogem.police', 'Police'),
		'intermediaire_id' : fields.integer('Identifiant intermediaire'),
		'intermediaire' : fields.many2one('mcisogem.courtier','intermediaire'),
		'periode_id' : fields.many2one('mcisogem.account.period' , 'Periode'),
		'exercice_id' : fields.many2one('mcisogem.exercice' , 'Exercice'),
		'beneficiaire_id' : fields.many2one('mcisogem.benef', 'Beneficiaire', required=True),
		'benef_id' : fields.integer('Matricule'),
		'motif' : fields.text('Motif',required=True),
		'image': fields.binary("Image",
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.suspend': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.suspend': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		'state': fields.selection([
			('nouveau', "Nouveau"),
			('attente', "En attente"),
			('valide', "Acceptée"),
			('rejet', "Rejetée"),  
		], 'Status', required=True, readonly=True),
		'num_suspend':fields.integer('Numero :'),
		'nom_benef' : fields.char('Nom'),
		'prenom_benef' : fields.char('Prenoms'),
		'stat_benef_init' : fields.char('Statut du beneficiaire'),
		# 'affichebenef': fields.boolean(''),
		# 'affichdetail': fields.boolean(''),
	}


	_defaults ={'state':'nouveau', 'beneficiaire_id': _get_beneficiare, 'benef_id':_get_beneficiare, 'garant_id' : _get_garant,'garant':_get_garant, 'intermediaire_id':_get_inter_user,'intermediaire':_get_inter_user}
	# _defaults ={'state':'nouveau','affichebenef':False,'affichdetail':False}
	_rec_name = 'beneficiaire_id'

	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "UTILISATEUR PRODUCTION" or group_obj.name == "RESPONSABLE PRODUCTION":
					return [('state', '=', 'attente')]
			return False
		else:
			return False

	def valide_demande(self, cr, uid, ids, context=None):
		
		# self.write(cr, uid, ids, {'state':'valide'}, context=context)
		cr.execute("update mcisogem_suspend set state='valide' where id = %s", (ids[0],))

		data_suspend = self.browse(cr, uid, ids[0], context)
		benef = self.pool.get('mcisogem.benef').browse(cr,uid,data_suspend.benef_id,context)
		self.write(cr,uid,ids[0],{'stat_benef_init':benef.statut},context)
		self.pool.get('mcisogem.benef').write(cr,uid,data_suspend.benef_id,{'statut':'S'},context)

		########### envoi des notifications aux responsables production pour une demande valide
		msg = str("Une demande de suspension vient d'être validée !")

		cr.execute("select id from res_groups where name='UTILISATEUR PRODUCTION'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation Médical",
			context=context
			)

			###################################################

	def rejet_demande(self, cr, uid, ids, context=None):
		
		# self.write(cr, uid, ids, {'state':'rejet'}, context=context)
		cr.execute("update mcisogem_suspend set state='rejet' where id = %s", (ids[0],))
		data_suspend = self.browse(cr, uid, ids[0], context)
		if data_suspend.stat_benef_init:
			self.pool.get('mcisogem.benef').write(cr,uid,data_suspend.benef_id,{'statut':data_suspend.stat_benef_init},context)
			########### envoi des notifications aux responsables production pour une demande rejete
		msg = str("Une demande de suspension vient d'être rejetée !")

		cr.execute("select id from res_groups where name='UTILISATEUR PRODUCTION'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation Médical",
			context=context
			)

			###################################################

	
	def annuler_assures(self, cr, uid, ids, context=None):
		statut = self.pool.get('mcisogem.entente').browse(cr,uid,ids,context)
		print('******************************')
		print(statut.state)

		if(statut.state=='valide'):
			# self.write(cr, uid, ids, {'state':'attente'}, context=context)
			cr.execute("update mcisogem_suspend set state='attente' where id = %s", (ids[0],))
		if(statut.state=='rejet'):
			# self.write(cr, uid, ids, {'state':'attente'}, context=context)
			cr.execute("update mcisogem_suspend set state='attente' where id = %s", (ids[0],))

	def benef_change(self,cr,uid,ids,benef_mat,context=None):
		if benef_mat:
			beneficiaire = self.pool.get('mcisogem.benef').browse(cr,uid,benef_mat,context)
			v={'garant_id':beneficiaire.garant_id.id,'nom_benef':beneficiaire.nom,'prenom_benef':beneficiaire.prenom_benef,'image_medium':beneficiaire.image_medium, 'police_id':beneficiaire.police_id.id}	
			return {'value':v}



	def create(self, cr, uid, vals, context=None):

		########### envoi des notifications aux responsables production pour une demande de suspension
		msg = str("Une nouvelle demande de suspension vient d'être émise. Vous devez l'examiner pour validation.")

		cr.execute("select id from res_groups where name='RESPONSABLE PRODUCTION'")
		groupe_id = cr.fetchone()[0]

		sql = "select uid from res_groups_users_rel where gid={}".format(groupe_id)
		cr.execute(sql)
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
			subject="[ISA-WEB] - Validation de demande de suspension",
			context=context
			)

			###################################################
		# pour le niveau garant
		if 'garant_id' in vals :
			cr.execute("SELECT max(num_suspend) FROM mcisogem_suspend WHERE garant_id = %s", (vals['garant_id'],))
			num_suspend = cr.fetchone()[0]

			print("***************num enreg**************")
			print(num_suspend)
			if not num_suspend:
				num_suspend = 1

			else:
				num_suspend = num_suspend+1

		code_periode = time.strftime("%m/%Y", time.localtime())
		periode_id = self.pool.get('mcisogem.account.period').search(cr,uid,[('code','=',code_periode)])
		periode_data = self.pool.get('mcisogem.account.period').browse(cr,uid,periode_id)
		vals['periode_id'] = periode_data.id
		vals['exercice_id'] = periode_data.exercice_id.id


		donne={}

		donne=self.benef_change(cr,uid,0,vals['benef_id'])['value']

		vals['nom_benef']=donne['nom_benef']
		vals['prenom_benef'] = donne['prenom_benef']
		vals['image_medium'] = donne['image_medium']
		vals['num_suspend'] = num_suspend
		vals['state'] = "attente"
		


		return super(mcisogem_suspend,self).create(cr, uid, vals, context)


class mcisogem_bar_inter(osv.osv):
	_name = 'mcisogem.bar.inter'
	_description = 'button bareme/acte/reseau'
	_columns = {
		'name':fields.char(''),
	}
	def button_bareme(self, cr, uid , ids, vals, context=None):
		print('***le bouton bareme inter ou sous***')
		
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'police_inter_bareme_tree'
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		inter_user_id = cr.fetchone()[0]
		cr.execute('select souscr_id from res_users where id=%s', (uid,))
		souscr_user_id = cr.fetchone()[0]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'police_inter_bareme_tree')[1]

		if inter_user_id :
			return {
			  'name':'Polices',
			  'view_type':'form',
			  'view_mode':'tree',
			  'res_model':'mcisogem.police',
			   'views': [(tree_id , 'tree')],
			  'view_id':tree_id,
			  'type':'ir.actions.act_window',
			  'context':ctx15,
			  'domain': [('courtier_id', '=',inter_user_id)],
			}
		else:
			if souscr_user_id:
				return {
				  'name':'Polices',
				  'view_type':'form',
				  'view_mode':'tree',
				  'res_model':'mcisogem.police',
				   'views': [(tree_id , 'tree')],
				  'view_id':tree_id,
				  'type':'ir.actions.act_window',
				  'context':ctx15,
				  'domain': [('souscripteur_id', '=',souscr_user_id)],
				}

	def button_reseau(self, cr, uid , ids, vals, context=None):
		print('***le bouton reseau de soin inter ou sous***')
		
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'police_sous_res_tree'
		cr.execute('select intermediaire_id from res_users where id=%s', (uid,))
		inter_user_id = cr.fetchone()[0]
		cr.execute('select souscr_id from res_users where id=%s', (uid,))
		souscr_user_id = cr.fetchone()[0]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'police_sous_res_tree')[1]

		if inter_user_id :
			return {
			  'name':'Polices',
			  'view_type':'form',
			  'view_mode':'tree',
			  'res_model':'mcisogem.police',
			   'views': [(tree_id , 'tree')],
			  'view_id':tree_id,
			  'type':'ir.actions.act_window',
			  'context':ctx15,
			  'domain': [('courtier_id', '=',inter_user_id)],
			}
		else:
			if souscr_user_id:
				return {
				  'name':'Polices',
				  'view_type':'form',
				  'view_mode':'tree',
				  'res_model':'mcisogem.police',
				   'views': [(tree_id , 'tree')],
				  'view_id':tree_id,
				  'type':'ir.actions.act_window',
				  'context':ctx15,
				  'domain': [('souscripteur_id', '=',souscr_user_id)],
				}






	# def button_acte_soumis(self, cr, uid , ids, vals, context=None):
	# 	print('***le bouton acte en entente prealable inter***')
	# 	ctx15 = (context or {}).copy()
	# 	ctx15['tree_view_ref'] = 'mcisogem_acte_entente_prealable_tree'
	# 	tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_acte_entente_prealable_tree')[1]
	# 	return {
	# 	  'name':' Liste Actes soumis à entente préalable',
	# 	  'view_type':'form',
	# 	  'view_mode':'tree',
	# 	  'res_model':'mcisogem.acte.entente.prealable',
	# 	   'views': [(tree_id , 'tree')],
	# 	  'view_id':tree_id,
	# 	  'type':'ir.actions.act_window',
	# 	  'context':ctx15,
	# 	  # 'domain': [],
	# 	}

class mcisogem_info_demande_mc(osv.osv):
	_name = 'mcisogem.info.demande.mc'
	_description = 'activite sur les prises en charges'
	_columns = {
		'name':fields.char(''),
	}
	def button_pcharge_valide(self, cr, uid , ids, vals, context=None):
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'view_pcharge_tree'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_pcharge_tree')[1]
		return {
		  'name':'Prise en charges valides',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.pcharge',
		   'views': [(tree_id , 'tree')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx15,
		  'domain': [('state', '=','valide'),('garant_id', '=',garant_user_id)],
		}

	def button_pcharge_rejete(self, cr, uid , ids, vals, context=None):
		ctx15 = (context or {}).copy()
		ctx15['tree_view_ref'] = 'view_pcharge_tree'
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_pcharge_tree')[1]
		return {
		  'name':'Prise en charges valides',
		  'view_type':'form',
		  'view_mode':'tree',
		  'res_model':'mcisogem.pcharge',
		   'views': [(tree_id , 'tree')],
		  'view_id':tree_id,
		  'type':'ir.actions.act_window',
		  'context':ctx15,
		  'domain': [('state', '=','rejet'),('garant_id', '=',garant_user_id)],
		}


class mcisogem_genre_reclamation(osv.osv):
	_name = 'mcisogem.genre.reclamation'
	_description = 'Genre des reclamations'

	_columns = {
		'name' :  fields.char('Categorie', required=True),
		'reclamation_id' : fields.one2many('mcisogem.reclamation','genre_id','reclamation'),
	}
	

class mcisogem_reclamation(osv.osv):
	_name = 'mcisogem.reclamation'
	_description = 'Réclamation en tous genres'
	_inherit = ['mail.thread']

	_mail_post_access = 'read'

	# def _get_garant(self, cr,uid,context):
		
	# 	cr.execute('select garant_id from res_users where id=%s', (uid,))
	# 	garant_user_id = cr.fetchone()[0]
	# 	if garant_user_id:
	# 		garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
	# 		print('*******garant id********')
	# 		print(garant.id)
	# 		return garant.id
	# 	else:
	# 		return False

	# def _get_centre_user(self, cr, uid, context=None):
	# 	cr.execute('select centre_id from res_users where id=%s', (uid,))
	# 	centre_user_id = cr.fetchone()[0]
	# 	if centre_user_id:
	# 		centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
	# 		print('***************************Centre*************************')
	# 		print(centre.id)
	# 		return centre.id
	# 	else:
	# 		return False

	def _get_souscr_user(self, cr, uid, context=None):
		cr.execute('select souscr_id from res_users where id=%s', (uid,))
		souscr_user_id = cr.fetchone()[0]
		if souscr_user_id:
			souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, souscr_user_id, context=context)
			print('***************************souscripteur*************************')
			print(souscripteur.id)
			return souscripteur.id
		else:
			return False

	_columns = {
		# 'garant_id' : fields.integer('Identifiant garant'),
		# 'garant_ids' : fields.many2one('mcisogem.garant','garant'),
		# 'id_centre' : fields.integer('Identifiant centre'),
		# 'centre_ids' : fields.many2one('mcisogem.centre','centre'),
		'souscripteur' : fields.integer('Identifiant souscripteur'),
		'souscripteur_id' : fields.many2one('mcisogem.souscripteur','souscripteur'),
		'genre_id' : fields.many2one('mcisogem.genre.reclamation','Genre',required=True),
		'motif' : fields.text('Motif',required=True),
		'description' : fields.text('Description',required=True),
	}
	_defaults ={
		# 'garant_id':_get_garant,
		# 'garant_ids':_get_garant,
		# 'id_centre':_get_centre_user,
		# 'centre_ids':_get_centre_user,
		'souscripteur':_get_souscr_user,
		'souscripteur_id':_get_souscr_user,
	}
	_rec_name = 'description'


class mcisogem_image_carte_1(osv.osv):
	_name = 'mcisogem.image.carte.1'

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

	_columns = {
		
		'name' : fields.char('REGIME'),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.image.carte.1': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.image.carte.1': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		'image_1': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.image.carte.1': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_2': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.image.carte.1': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_3': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.image.carte.1': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_4': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.image.carte.1': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_5': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.image.carte.1': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
	
	}



class mcisogem_recherche_carte(osv.osv):
	_name = 'mcisogem.recherche.carte'

	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			return garant.id
		else:
			return False
	def _get_user(self, cr,uid,context):
		
		if uid:
			return uid
		else:
			return False

	_columns = {
		'users' : fields.integer('Identifiant Utilisateur'),
		'garant_id' : fields.many2one('mcisogem.garant','Garant', required=True),
		'police_id' : fields.many2one('mcisogem.police','Police'),
		'souscripteur_id' : fields.many2one('mcisogem.souscripteur','Souscripteur'),
		'souscripteur_id_tempo' : fields.many2one('mcisogem.souscripteur.garant','Souscripteur'),
		'college_id' : fields.many2one('mcisogem.college','Collège'),
		'college_id_tempo' : fields.many2one('mcisogem.college.garant','Collège'),
		'benef_id' : fields.many2one('mcisogem.benef','Matricule'),
		'beneficiaire_id' : fields.one2many('mcisogem.recherche.carte2','critere_id',' '),
		'recherche' : fields.char('Recherche'),
		'date_d' : fields.date('Debut'),
		'date_f' : fields.date('Fin'),
		# 'stat_incorp' : fields.boolean('Incorporation'),
		'regime_id' : fields.many2one('mcisogem.image.carte.1','regime', required=True),
		
	}
	_rec_name = "recherche"
	_defaults = {
		'recherche': 'Recherche',
		'users': _get_user,
		'stat_incorp': False,
	
	}

	def onchange_sous_col(self,cr,uid,context,valeur):
		
		if valeur:
			### remplissage de la table college_garant ###

			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT college_id FROM mcisogem_histo_prime WHERE garant_id=%s', (valeur,))
			college_liste = cr.fetchall()
			print(college_liste)
			for ind_col in college_liste:
				college = self.pool.get('mcisogem.college').browse(cr, uid, ind_col)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data)

			### remplissage de la table souscripteur_garant ###

			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE garant_id=%s', (valeur,))
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

			v = {}
			v = {'police_id':'','souscripteur_id_tempo':'','college_id_tempo':''}
			return {'value' : v}
		else:
			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))

			cr.execute('SELECT id FROM mcisogem_college')
			college_liste = cr.fetchall()
			print ('******college liste******')
			print(college_liste)
			for ind_col in college_liste:
				
				college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
				print ('******college ind******')
				print(college_ids)
				college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data)


			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))

			cr.execute('SELECT id FROM mcisogem_souscripteur')
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

	def onchange_sous_col2(self,cr,uid,context,valeur,valeur2):
		
		if valeur:
			### remplissage de la table college_garant ###

			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT id FROM mcisogem_college WHERE police_id=%s', (valeur,))
			college_liste = cr.fetchall()
			print ('******college liste******')
			print(college_liste)
			for ind_col in college_liste:
				
				college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
				print ('******college ind******')
				print(college_ids)
				college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data)

			### remplissage de la table souscripteur_garant ###

			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE id=%s', (valeur,))
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

			v = {}
			v = {'college_id_tempo':''}
			return {'value' : v}

		else:
			if valeur2:
				### remplissage de la table college_garant ###

				cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
				cr.execute('SELECT DISTINCT college_id FROM mcisogem_histo_prime WHERE garant_id=%s', (valeur2,))
				college_liste = cr.fetchall()
				print(college_liste)
				for ind_col in college_liste:
					college = self.pool.get('mcisogem.college').browse(cr, uid, ind_col)
					print(ind_col)
					print(college.id)
					print(college.name)
					data = {}
					data['college_id'] = college.id
					data['name'] = college.name
					self.pool.get('mcisogem.college.garant').create(cr,uid,data)

				### remplissage de la table souscripteur_garant ###

				cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
				cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE garant_id=%s', (valeur2,))
				police_liste = cr.fetchall()
				print(police_liste)
				for ind_pol in police_liste:
					souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
					print(ind_pol)
					print(souscripteur.id)
					print(souscripteur.name)
					data = {}
					data['souscripteur_id'] = souscripteur.id
					data['name'] = souscripteur.name
					self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

				v = {}
				v = {'police_id':'','souscripteur_id_tempo':'','college_id_tempo':''}
				return {'value' : v}
			else:
				cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))

				cr.execute('SELECT id FROM mcisogem_college')
				college_liste = cr.fetchall()
				print ('******college liste******')
				print(college_liste)
				for ind_col in college_liste:
					
					college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
					print ('******college ind******')
					print(college_ids)
					college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
					print(ind_col)
					print(college.id)
					print(college.name)
					data = {}
					data['college_id'] = college.id
					data['name'] = college.name
					self.pool.get('mcisogem.college.garant').create(cr,uid,data)


				cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))

				cr.execute('SELECT id FROM mcisogem_souscripteur')
				police_liste = cr.fetchall()
				print(police_liste)
				for ind_pol in police_liste:
					souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
					print(ind_pol)
					print(souscripteur.id)
					print(souscripteur.name)
					data = {}
					data['souscripteur_id'] = souscripteur.id
					data['name'] = souscripteur.name
					self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)


	def create(self, cr, uid, vals, context=None):

		if 'souscripteur_id_tempo' in vals:
			souscripteur = self.pool.get('mcisogem.souscripteur.garant').browse(cr, uid, vals['souscripteur_id_tempo'],context).souscripteur_id
			vals['souscripteur_id'] = souscripteur
		


		if 'college_id_tempo' in vals:
			college = self.pool.get('mcisogem.college.garant').browse(cr, uid, vals['college_id_tempo'],context).college_id


			vals['college_id'] = college
		
		vals['aff_print'] = True
 
		return super(mcisogem_recherche_carte, self).create(cr,uid,vals,context)
		

	
	def print_carte(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids, [], context=context)
		critere = self.browse(cr, uid, ids[0], context)

		nbr_benef = self.pool.get('mcisogem.recherche.carte2').search_count(cr, uid, [('create_uid', '=', uid)])
		print('****nombre de bene recherche*****')
		print(nbr_benef)
		# raise osv.except_osv('Attention' ,'stop!')

		if (nbr_benef != 0 ):
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'mcisogem_isa.report_benef_carte',
					'data': data,
			}	
		else:
			raise osv.except_osv('Impossible' ,'aucun élement à imprimer!')

	def button_recherche(self, cr, uid , ids, context=None):

		critere = self.browse(cr, uid, ids[0])
		garant = critere.garant_id.id
		police = critere.police_id.id
		benef = critere.benef_id.id
		college_id = critere.college_id_tempo.id
		college = self.pool.get('mcisogem.college.garant').browse(cr, uid, college_id,context).college_id
		souscripteur_id = critere.souscripteur_id_tempo.id
		souscripteur = self.pool.get('mcisogem.souscripteur.garant').browse(cr, uid, souscripteur_id,context).souscripteur_id
		regime = critere.regime_id.id
		
		debut = critere.date_d
		fin = critere.date_f

		# stat_incorp = critere.stat_incorp


		data = {}
		data['garant_id'] = garant
		data['police_id'] = police
		data['benef_id'] = benef
		data['souscripteur_id'] = souscripteur
		data['college_id'] = college
		# data['stat_incorp'] = stat_incorp
		data['regime_id'] = regime
		
		self.pool.get('mcisogem.recherche.carte').write(cr,uid,ids[0],data,context)
		
		data = {}
		statut_p_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ASSURE PRINCIPAL',)])
		statut_p = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_p_id, context).id

		statut_c_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'CONJOINT',)])
		statut_c = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_c_id, context).id

		statut_e_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ENFANT',)])
		statut_e = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_e_id, context).id

		statut_d_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'AUTRE CONJOINT(E)',)])
		statut_d = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_d_id, context).id

		statut_k_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ENFANT SUPPLEMENTAIRE',)])
		statut_k = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_k_id, context).id

		statut_x_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'AUTRE PARENT',)])
		statut_x = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_x_id, context).id
		
		statut_g_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'GENITEUR (ASCENDANT)',)])
		statut_g = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_g_id, context).id
		
		requette = "SELECT id From mcisogem_benef WHERE statut_benef = {} AND ".format(statut_p)
		requette2 = "SELECT id From mcisogem_benef WHERE "
		if benef == False:
			requette += '1=1 '
			requette2 += '1=1 '
		else:
			requette += 'id = {} '.format(benef)
			requette2 += '(id = {} '.format(benef)
			# requette1 += 'or benef_id = {} )'.format(benef)
			requette2 += 'or benef_id = {} ) '.format(benef)
		if garant == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			requette += 'AND garant_id = {} '.format(garant)
			requette2 += 'AND garant_id = {} '.format(garant)
		if police == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else : 
			if police != "":
				requette += 'AND police_id = {} '.format(police)
				requette2 += 'AND police_id = {} '.format(police)
		if (not college):
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if college != "":
				requette += 'AND college_id = {} '.format(college)
				requette2 += 'AND college_id = {} '.format(college)
		if (not souscripteur):
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if souscripteur != "":
				requette += 'AND souscripteur_id = {} '.format(souscripteur)
				requette2 += 'AND souscripteur_id = {} '.format(souscripteur)
		# if stat_incorp == False:
		# 	requette += 'AND 1=1 '
		# 	requette2 += 'AND 1=1 '
		# else:
		# 	if stat_incorp == True:
		# 		requette += "AND creat_incorpo = 'I' "
		# 		requette2 += "AND creat_incorpo = 'I' "

		if (fin and debut):
			if (fin>debut):
				debut = datetime.strftime(datetime.strptime(debut, "%Y-%m-%d"), "%Y-%m-%d %H:%M:%S.%f")
				fin = datetime.strftime(datetime.strptime(fin, "%Y-%m-%d"), "%Y-%m-%d %H:%M:%S.%f")
				# debut = critere.date_d
				# fin = critere.date_f
				type_debut = type(debut)
				type_fin = type(fin)
				print('** les dates converties **')
				print(type_debut)
				print(debut)
				print(type_fin)
				print(fin)
				# raise osv.except_osv('Attention' ,'Oups #TDC! dates valides')
				requette += "AND create_date BETWEEN '{}' ".format(debut)
				requette2 += "AND create_date BETWEEN '{}' ".format(debut)
				requette +="AND '{}' ".format(fin)
				requette2 +="AND '{}' ".format(fin)
			
			else :
				
					raise osv.except_osv('Attention' ,'Oups #TDC! dates invalides')
		else:
			if (((fin) and ( not debut)) or ((not fin) and (debut))):
				raise osv.except_osv('Attention' ,'Oups #TDC! dates invalides')
			else:
				if ((not fin) and ( not debut)):
				# 	raise osv.except_osv('Attention' ,'Oups #TDC! veuillez remplir correctement les dates')
					requette += 'AND 1=1'
					requette2 += 'AND 1=1 '

		req2 = requette2
		req3 = requette2
		requette3 = requette2

		print('** la requette **')
		print(requette)
		print('** la requette 2 **')
		print(requette2)
		print('** identifiant critere **')
		print(ids[0])
		#raise osv.except_osv('Attention' ,'Oups #TDC!')

		cr.execute('DELETE  FROM mcisogem_recherche_carte2 WHERE create_uid = %s', (uid,))
		########### A
		cr.execute(requette)
		beneficiaire_liste = cr.fetchall()
		print('**Lise des beneficiaire recherchés**')
		print(beneficiaire_liste)
		
		

		for ind_benef in beneficiaire_liste:
			beneficiairep = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef, context)
			print(beneficiairep.name)
			data = {}
			
			data['beneficiaire'] = beneficiairep.name
			data['nom_benef'] = beneficiairep.nom
			data['prenom_benef'] = beneficiairep.prenom_benef
			data['souscripteur_id'] = beneficiairep.souscripteur_id.id
			data['date'] = beneficiairep.dt_naiss_benef
			data['date_ef'] = beneficiairep.dt_effet
			data['statut'] = beneficiairep.statut_benef.id
			data['genre'] = beneficiairep.sexe
			data['image_medium'] = beneficiairep.image_medium
			data['regime_id'] = regime
			data['critere_id'] = ids[0]

			self.pool.get('mcisogem.recherche.carte2').create(cr, uid, data, context)


			########### C 

			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {} '.format(statut_c)
			# requette2 +='OR statut_benef = {}'.format(statut_d)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2

			for ind_benef_c in beneficiairec_liste:
				print(ind_benef_c)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_c, context)
				print(beneficiairec.name)
				data2 = {}

				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.carte2').create(cr, uid, data2, context)


			########### D

			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {} '.format(statut_d)
			# requette2 +='OR statut_benef = {}'.format(statut_d)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2

			for ind_benef_c in beneficiairec_liste:
				print(ind_benef_c)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_c, context)
				print(beneficiairec.name)
				data2 = {}

				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.carte2').create(cr, uid, data2, context)

			########### E 


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_e)
			# requette2 +='OR statut_benef = {}'.format(statut_k)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.carte2').create(cr, uid, data2, context)

			########### K


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_k)
			# requette2 +='OR statut_benef = {}'.format(statut_k)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.carte2').create(cr, uid, data2, context)

			########### G


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_g)
			# requette2 +='OR statut_benef = {}'.format(statut_x)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.carte2').create(cr, uid, data2, context)


			########### X


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_x)
			# requette2 +='OR statut_benef = {}'.format(statut_x)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.carte2').create(cr, uid, data2, context)




		if ((benef) and (critere.benef_id.code_statut != 'A')):
			print('** CONDITION POUR ASSUREES DEPENDANTS **')
			print('** la requette3 **')
			print(requette3)
			cr.execute(requette3)
			beneficiairec_liste = cr.fetchall()
			requette3 = req3
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.carte2').create(cr, uid, data2, context)



class mcisogem_recherche_carte2(osv.osv):
	_name = 'mcisogem.recherche.carte2'

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

	_columns = {
		'critere_id': fields.many2one('mcisogem.recherche.carte','critere'),
		'beneficiaire' : fields.char('Matricule'),
		'nom_benef' : fields.char('Nom'),
		'prenom_benef' : fields.char('Prenom'),
		'souscripteur_id' : fields.many2one('mcisogem.souscripteur','Souscripteur'),
		'ass_p_id' : fields.many2one('mcisogem.benef','Adhérent'),
		'date' : fields.datetime('Date de naissance'),
		'date_ef' : fields.datetime('Date effet'),
		'statut' : fields.many2one('mcisogem.stat.benef' , 'Statut Bénéficiare'),
		'genre' : fields.char('Genre'),
		'regime_id' : fields.many2one('mcisogem.image.carte.1','regime'),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.recherche.carte2': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.recherche.carte2': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
	
	}
	_rec_name = "beneficiaire"


#######################NEW PARAMETRE POUR ETATS BENEF(tables temporaires)#########################

class mcisogem_garant_etat_benef(osv.osv):
	_name = 'mcisogem.garant.etat.benef'

	_columns = {
		'garant_id' : fields.many2one('mcisogem.garant','garant'),
		'tempo1_id' : fields.many2one('mcisogem.recherche.benef','tempo1_id'),
	}


class mcisogem_police_etat_benef(osv.osv):
	_name = 'mcisogem.police.etat.benef'

	_columns = {
		'police_id' : fields.many2one('mcisogem.police','police'),
		'garant_id' : fields.many2one('mcisogem.garant','garant'),
		'tempo2_id' : fields.many2one('mcisogem.recherche.benef','tempo2_id'),
	}


class mcisogem_college_etat_benef(osv.osv):
	_name = 'mcisogem.college.etat.benef'

	_columns = {
		'college_id' : fields.many2one('mcisogem.college','college'),
		'police_id' : fields.many2one('mcisogem.police','police'),
		'garant_id' : fields.many2one('mcisogem.garant','garant'),
		'tempo3_id' : fields.many2one('mcisogem.recherche.benef','tempo3_id'),
		'nombre_famille' : fields.integer('Nombre famille'),
		'nombre_a' : fields.integer('Nombre assuré principal'),
		'nombre_c' : fields.integer('Nombre Conjoint'),
		'nombre_e' : fields.integer('Nombre Enfant'),
		'nombre_p' : fields.integer('Nombre Parent'),
		'nombre_autre' : fields.integer('Nombre autre'),
	}

###################################################################


class mcisogem_recherche_benef(osv.osv):
	_name = 'mcisogem.recherche.benef'

	
	def _get_user(self, cr,uid,context):
		
		if uid:
			return uid
		else:
			return False

	_columns = {
		'users' : fields.integer('Identifiant Utilisateur'),
		'garant_id' : fields.many2one('mcisogem.garant','Garant'),
		'garant_ids' : fields.one2many('mcisogem.garant.etat.benef', 'tempo1_id'),
		'police_id' : fields.many2one('mcisogem.police','Police'),
		'police_ids' : fields.one2many('mcisogem.police.etat.benef', 'tempo2_id'),
		'souscripteur_id_tempo' : fields.many2one('mcisogem.souscripteur.garant','Souscripteur'),
		'college_id_tempo' : fields.many2one('mcisogem.college.garant','Collège'),
		'souscripteur_id' : fields.many2one('mcisogem.souscripteur','Souscripteur'),
		'college_id' : fields.many2one('mcisogem.college','Collège'),
		'college_ids' : fields.one2many('mcisogem.college.etat.benef', 'tempo3_id'),
		'beneficiaire_id' : fields.one2many('mcisogem.recherche.benef2','critere_id',' '),
		'recherche' : fields.char('Recherche'),
		'date_d' : fields.date('Debut'),
		'date_f' : fields.date('Fin'),
		'stat_incorp' : fields.boolean('Incorporation'),
		'stat_ret' : fields.boolean('Retrait'),
		'stat_susp' : fields.boolean('Suspension'),
		'limit_age' : fields.boolean('Limite ages'),
		'age' : fields.integer('Limite Age'),
		'r_statut' : fields.boolean('Statut'),
		'statut_ids' : fields.many2many('mcisogem.stat.benef' ,'regl_stat_rel', 'id_r' , 'id_s' , 'Statut'),
		
	}
	_rec_name = "recherche"
	_defaults = {
		# 'garant_id' : _get_garant,
		'recherche': 'Recherche',
		'users': _get_user,
		'stat_incorp': False,
	
	}

	def onchange_inc(self,cr,uid,context,choix):

		if choix:
			v = {}

			v={'stat_ret':False,'stat_susp':False,'limit_age':False,'r_statut':False}

			return {'value':v}

	def onchange_ret(self,cr,uid,context,choix):

		if choix:
			v = {}

			v={'stat_incorp':False,'stat_susp':False,'limit_age':False,'r_statut':False}

			return {'value':v}

	def onchange_sus(self,cr,uid,context,choix):

		if choix:
			v = {}

			v={'stat_incorp':False,'stat_ret':False,'limit_age':False,'r_statut':False}

			return {'value':v}

	def onchange_age(self,cr,uid,context,choix):

		if choix:
			v = {}

			v={'stat_incorp':False,'stat_ret':False,'stat_susp':False,'r_statut':False}

			return {'value':v}

	def onchange_verifier_age(self,cr,uid,context,choix):

		if choix:
			# print ('******date du jour******')
			# print time.strftime('%Y',time.localtime())
			# date_jour =  time.strftime('%Y',time.localtime())
			# age_test = int(date_jour) - 1992
			# print ('******age******')
			# print (age_test)
			if (choix<0 or choix>100):
				# raise osv.except_osv('Attention' ,'mauvais age')
				v = {}

				v={'age':''}

				return {'value':v}

	def onchange_statut(self,cr,uid,context,choix):

		if choix:
			v = {}

			v={'stat_incorp':False,'stat_ret':False,'stat_susp':False,'limit_age':False,}

			return {'value':v}




	def onchange_sous_col(self,cr,uid,context,valeur):
		
		if valeur:
			### remplissage de la table college_garant ###

			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT college_id FROM mcisogem_histo_prime WHERE garant_id=%s', (valeur,))
			college_liste = cr.fetchall()
			print ('******college liste******')
			print(college_liste)
			for ind_col in college_liste:
				
				college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
				print ('******college ind******')
				print(college_ids)
				college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data)

			### remplissage de la table souscripteur_garant ###

			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE garant_id=%s', (valeur,))
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

			v = {}
			v = {'police_id':'','souscripteur_id_tempo':'','college_id_tempo':''}
			return {'value' : v}

		else:
			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))

			cr.execute('SELECT id FROM mcisogem_college')
			college_liste = cr.fetchall()
			print ('******college liste******')
			print(college_liste)
			for ind_col in college_liste:
				
				college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
				print ('******college ind******')
				print(college_ids)
				college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data)


			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))

			cr.execute('SELECT id FROM mcisogem_souscripteur')
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

	def onchange_sous_col2(self,cr,uid,context,valeur,valeur2):
		
		if valeur:
			### remplissage de la table college_garant ###

			cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT id FROM mcisogem_college WHERE police_id=%s', (valeur,))
			college_liste = cr.fetchall()
			print ('******college liste******')
			print(college_liste)
			for ind_col in college_liste:
				
				college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
				print ('******college ind******')
				print(college_ids)
				college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
				print(ind_col)
				print(college.id)
				print(college.name)
				data = {}
				data['college_id'] = college.id
				data['name'] = college.name
				self.pool.get('mcisogem.college.garant').create(cr,uid,data)

			### remplissage de la table souscripteur_garant ###

			cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
			cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE id=%s', (valeur,))
			police_liste = cr.fetchall()
			print(police_liste)
			for ind_pol in police_liste:
				souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
				print(ind_pol)
				print(souscripteur.id)
				print(souscripteur.name)
				data = {}
				data['souscripteur_id'] = souscripteur.id
				data['name'] = souscripteur.name
				self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

			v = {}
			v = {'souscripteur_id_tempo':'','college_id_tempo':''}
			return {'value' : v}

		else:
			if valeur2:
				### remplissage de la table college_garant ###

				cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))
				cr.execute('SELECT DISTINCT college_id FROM mcisogem_histo_prime WHERE garant_id=%s', (valeur2,))
				college_liste = cr.fetchall()
				print(college_liste)
				for ind_col in college_liste:
					college = self.pool.get('mcisogem.college').browse(cr, uid, ind_col)
					print(ind_col)
					print(college.id)
					print(college.name)
					data = {}
					data['college_id'] = college.id
					data['name'] = college.name
					self.pool.get('mcisogem.college.garant').create(cr,uid,data)

				### remplissage de la table souscripteur_garant ###

				cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))
				cr.execute('SELECT DISTINCT souscripteur_id FROM mcisogem_police WHERE garant_id=%s', (valeur2,))
				police_liste = cr.fetchall()
				print(police_liste)
				for ind_pol in police_liste:
					souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
					print(ind_pol)
					print(souscripteur.id)
					print(souscripteur.name)
					data = {}
					data['souscripteur_id'] = souscripteur.id
					data['name'] = souscripteur.name
					self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)

				v = {}
				v = {'police_id':'','souscripteur_id_tempo':'','college_id_tempo':''}
				return {'value' : v}
			else:
				cr.execute('DELETE  FROM mcisogem_college_garant WHERE create_uid=%s', (uid,))

				cr.execute('SELECT id FROM mcisogem_college')
				college_liste = cr.fetchall()
				print ('******college liste******')
				print(college_liste)
				for ind_col in college_liste:
					
					college_ids = self.pool.get('mcisogem.college').search(cr, uid, [('id','=', ind_col)])
					print ('******college ind******')
					print(college_ids)
					college = self.pool.get('mcisogem.college').browse(cr, uid, college_ids)
					print(ind_col)
					print(college.id)
					print(college.name)
					data = {}
					data['college_id'] = college.id
					data['name'] = college.name
					self.pool.get('mcisogem.college.garant').create(cr,uid,data)


				cr.execute('DELETE  FROM mcisogem_souscripteur_garant WHERE create_uid=%s', (uid,))

				cr.execute('SELECT id FROM mcisogem_souscripteur')
				police_liste = cr.fetchall()
				print(police_liste)
				for ind_pol in police_liste:
					souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, ind_pol)
					print(ind_pol)
					print(souscripteur.id)
					print(souscripteur.name)
					data = {}
					data['souscripteur_id'] = souscripteur.id
					data['name'] = souscripteur.name
					self.pool.get('mcisogem.souscripteur.garant').create(cr,uid,data)






	def create(self, cr, uid, vals, context=None):
		
		
		if 'souscripteur_id_tempo' in vals:
			souscripteur = self.pool.get('mcisogem.souscripteur.garant').browse(cr, uid, vals['souscripteur_id_tempo'],context).souscripteur_id
			vals['souscripteur_id'] = souscripteur
		


		if 'college_id_tempo' in vals:
			college = self.pool.get('mcisogem.college.garant').browse(cr, uid, vals['college_id_tempo'],context).college_id


			vals['college_id'] = college

		vals['aff_print'] = True
 
		return super(mcisogem_recherche_benef, self).create(cr,uid,vals,context)
		

	def print_recherche(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids, [], context=context)
		critere = self.browse(cr, uid, ids[0], context)

		nbr_benef = self.pool.get('mcisogem.recherche.benef2').search_count(cr, uid, [('create_uid', '=', uid)])
		print('****nombre de bene recherche*****')
		print(nbr_benef)
		

		if (nbr_benef != 0 ):


			if (critere.stat_incorp):

				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'mcisogem_isa.report_benef_inc',
						'data': data,
				}
			elif (critere.stat_ret):

				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'mcisogem_isa.report_benef_ret',
						'data': data,
				}
			elif (critere.stat_susp):

				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'mcisogem_isa.report_benef_sus',
						'data': data,
				}
			elif (critere.limit_age):
				if critere.age:
					return {
							'type': 'ir.actions.report.xml',
							'report_name': 'mcisogem_isa.report_benef_age',
							'data': data,
					}
			elif (critere.r_statut):
				if critere.statut_ids:
					return {
							'type': 'ir.actions.report.xml',
							'report_name': 'mcisogem_isa.report_benef_stat',
							'data': data,
					}
			else:
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'mcisogem_isa.report_benef',
						'data': data,
				}
		else:
			raise osv.except_osv('Impossible' ,'aucun élement à imprimer!')

	

	def button_recherche(self, cr, uid , ids, context=None):

		critere = self.browse(cr, uid, ids[0])
		garant = critere.garant_id.id
		police = critere.police_id.id
		college_id = critere.college_id_tempo.id
		college = self.pool.get('mcisogem.college.garant').browse(cr, uid, college_id,context).college_id
		souscripteur_id = critere.souscripteur_id_tempo.id
		souscripteur = self.pool.get('mcisogem.souscripteur.garant').browse(cr, uid, souscripteur_id,context).souscripteur_id
		# regime = critere.regime_id.id
		limit_age = critere.limit_age
		age = critere.age
		r_statut = critere.r_statut
		
		debut = critere.date_d
		fin = critere.date_f

		stat_incorp = critere.stat_incorp
		stat_ret = critere.stat_ret
		stat_susp = critere.stat_susp

		# print('**nombre de statut***')
		# print(len(critere.statut_ids))
		# raise osv.except_osv('Attention' ,'test statut_ids')

		data = {}

		data['garant_id'] = garant
		data['police_id'] = police
		data['souscripteur_id'] = souscripteur
		data['college_id'] = college
		data['stat_incorp'] = stat_incorp
		data['stat_ret'] = stat_ret
		data['stat_susp'] = stat_susp
		data['limit_age'] = limit_age
		data['age'] = age
		data['statut_ids'] = critere.statut_ids		
		
		self.pool.get('mcisogem.recherche.benef').write(cr,uid,ids[0],data,context)
		
		data = {}
		statut_p_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ASSURE PRINCIPAL',)])
		statut_p = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_p_id, context).id

		statut_c_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'CONJOINT',)])
		statut_c = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_c_id, context).id

		statut_e_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ENFANT',)])
		statut_e = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_e_id, context).id

		statut_d_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'AUTRE CONJOINT(E)',)])
		statut_d = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_d_id, context).id

		statut_k_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'ENFANT SUPPLEMENTAIRE',)])
		statut_k = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_k_id, context).id

		statut_x_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'AUTRE PARENT',)])
		statut_x = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_x_id, context).id
		
		statut_g_id = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('name','=', 'GENITEUR (ASCENDANT)',)])
		statut_g = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_g_id, context).id
		
		requette = "SELECT id From mcisogem_benef WHERE statut_benef = {} AND ".format(statut_p)
		requette2 = "SELECT id From mcisogem_benef WHERE "
		if garant == False:
			requette += '1=1 '
			requette2 += '1=1 '
		else:
			requette += 'garant_id = {} '.format(garant)
			requette2 += 'garant_id = {} '.format(garant)
		if police == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else : 
			if police != "":
				requette += 'AND police_id = {} '.format(police)
				requette2 += 'AND police_id = {} '.format(police)
		if (not college):
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if college != "":
				requette += 'AND college_id = {} '.format(college)
				requette2 += 'AND college_id = {} '.format(college)
		if (not souscripteur):
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if souscripteur != "":
				requette += 'AND souscripteur_id = {} '.format(souscripteur)
				requette2 += 'AND souscripteur_id = {} '.format(souscripteur)
		if stat_incorp == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if stat_incorp == True:
				requette += "AND creat_incorpo = 'I' "
				requette2 += "AND creat_incorpo = 'I' "
		if stat_ret == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if stat_ret == True:
				requette += "AND statut = 'R' "
				requette2 += "AND statut = 'R' "
		if stat_susp == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if stat_susp == True:
				requette += "AND statut = 'S' "
				requette2 += "AND statut = 'S' "
		if limit_age == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if limit_age == True:
				if age :
					date_jour =  int(time.strftime('%Y',time.localtime()))
					requette += "AND  ({} - ".format(date_jour)
					requette2 += "AND  ({} - ".format(date_jour)
					requette += "date_part('year',dt_naiss_benef)) <= {}".format(age)
					requette2 += "date_part('year',dt_naiss_benef)) <= {}".format(age)
		if r_statut == False:
			requette += 'AND 1=1 '
			requette2 += 'AND 1=1 '
		else:
			if r_statut == True:
				if critere.statut_ids :
					print('**nombre de statut***')
					print(len(critere.statut_ids))
					ct1 = len(critere.statut_ids)
					ct2 = 0
					requette += 'AND ('
					requette2 += 'AND ('
					for ind in critere.statut_ids:
						ct2 += 1
						requette += 'statut_benef = {}'.format(ind.id)
						requette2 += 'statut_benef = {}'.format(ind.id) 
						if (ct1 == ct2): 
							break
						requette += ' or '
						requette2 += ' or '
					requette += ')'
					requette2 += ')'


					


		if (fin and debut):
			if (fin>debut):
				debut = datetime.strftime(datetime.strptime(debut, "%Y-%m-%d"), "%Y-%m-%d %H:%M:%S.%f")
				fin = datetime.strftime(datetime.strptime(fin, "%Y-%m-%d"), "%Y-%m-%d %H:%M:%S.%f")
				# debut = critere.date_d
				# fin = critere.date_f
				type_debut = type(debut)
				type_fin = type(fin)
				print('** les dates converties **')
				print(type_debut)
				print(debut)
				print(type_fin)
				print(fin)
				# raise osv.except_osv('Attention' ,'Oups #TDC! dates valides')
				requette += "AND create_date BETWEEN '{}' ".format(debut)
				requette2 += "AND create_date BETWEEN '{}' ".format(debut)
				requette +="AND '{}' ".format(fin)
				requette2 +="AND '{}' ".format(fin)
			
			else :
				
					raise osv.except_osv('Attention' ,'Oups #TDC! dates invalides')
		else:
			if (((fin) and ( not debut)) or ((not fin) and (debut))):
				raise osv.except_osv('Attention' ,'Oups #TDC! dates invalides')
			else:
				if ((not fin) and ( not debut)):
				# 	raise osv.except_osv('Attention' ,'Oups #TDC! veuillez remplir correctement les dates')
					requette += 'AND 1=1'
					requette2 += 'AND 1=1 '

		req2 = requette2
		req3 = requette2
		requette3 = requette2

		print('** la requette **')
		print(requette)
		print('** identifiant critere **')
		print(ids[0])
		#raise osv.except_osv('Attention' ,'Oups #TDC!')

		cr.execute('DELETE  FROM mcisogem_recherche_benef2 WHERE create_uid = %s', (uid,))
		########### A
		cr.execute(requette)
		beneficiaire_liste = cr.fetchall()
		print('**Lise des beneficiaire recherchés**')
		print(beneficiaire_liste)
		
		
		for ind_benef in beneficiaire_liste:
			beneficiairep = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef, context)

			nombre_dependant = self.pool.get('mcisogem.benef').search_count(cr, uid, [('benef_id', '=', beneficiairep.id)])

			print(beneficiairep.name)
			data = {}
			
			data['beneficiaire'] = beneficiairep.name
			data['nom_benef'] = beneficiairep.nom
			data['prenom_benef'] = beneficiairep.prenom_benef
			data['garant_id'] = beneficiairep.garant_id.id
			data['police_id'] = beneficiairep.police_id.id
			data['college_id'] = beneficiairep.college_id.id
			data['souscripteur_id'] = beneficiairep.souscripteur_id.id
			data['date'] = beneficiairep.dt_naiss_benef
			data['date_ef'] = beneficiairep.dt_effet
			data['statut'] = beneficiairep.statut_benef.id
			data['genre'] = beneficiairep.sexe
			data['nombre_famille'] = (nombre_dependant+1)
			data['nombre_a'] = 1
			data['image_medium'] = beneficiairep.image_medium
			data['critere_id'] = ids[0]

			self.pool.get('mcisogem.recherche.benef2').create(cr, uid, data, context)

			depend_ids = self.pool.get('mcisogem.recherche.benef2').search(cr, uid, [('beneficiaire', '=', beneficiairep.name),('statut', '=', beneficiairep.statut_benef.id)])
			depend_id = self.pool.get('mcisogem.recherche.benef2').browse(cr, uid, depend_ids)

			print('** ID PARENT **')
			print(depend_id.id)

			########### C

			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {} '.format(statut_c)
			# requette2 +='OR statut_benef = {}'.format(statut_d)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2

			for ind_benef_c in beneficiairec_liste:
				print(ind_benef_c)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_c, context)
				print(beneficiairec.name)
				data2 = {}

				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['garant_id'] = beneficiairec.garant_id.id
				data2['police_id'] = beneficiairec.police_id.id
				data2['college_id'] = beneficiairec.college_id.id
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				# data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['ass_p_id'] = depend_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['nombre_c'] = 1
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef2').create(cr, uid, data2, context)

			########### D

			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {} '.format(statut_d)
			# requette2 +='OR statut_benef = {}'.format(statut_d)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2

			for ind_benef_c in beneficiairec_liste:
				print(ind_benef_c)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_c, context)
				print(beneficiairec.name)
				data2 = {}

				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['garant_id'] = beneficiairec.garant_id.id
				data2['police_id'] = beneficiairec.police_id.id
				data2['college_id'] = beneficiairec.college_id.id
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				# data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['ass_p_id'] = depend_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['nombre_autre'] = 1
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef2').create(cr, uid, data2, context)

			########### E 


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_e)
			# requette2 +='OR statut_benef = {}'.format(statut_k)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['garant_id'] = beneficiairec.garant_id.id
				data2['police_id'] = beneficiairec.police_id.id
				data2['college_id'] = beneficiairec.college_id.id
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				# data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['ass_p_id'] = depend_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['nombre_e'] = 1
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef2').create(cr, uid, data2, context)

			########### K


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_k)
			# requette2 +='OR statut_benef = {}'.format(statut_k)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['garant_id'] = beneficiairec.garant_id.id
				data2['police_id'] = beneficiairec.police_id.id
				data2['college_id'] = beneficiairec.college_id.id
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				# data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['ass_p_id'] = depend_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['nombre_autre'] = 1
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef2').create(cr, uid, data2, context)

			########### G


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_g)
			# requette2 +='OR statut_benef = {}'.format(statut_x)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['garant_id'] = beneficiairec.garant_id.id
				data2['police_id'] = beneficiairec.police_id.id
				data2['college_id'] = beneficiairec.college_id.id
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				# data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['ass_p_id'] = depend_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['nombre_p'] = 1
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]
				# raise osv.except_osv('Attention' ,'Oups #avant enregistrement!')
				self.pool.get('mcisogem.recherche.benef2').create(cr, uid, data2, context)
				#raise osv.except_osv('Attention' ,'Oups #apres enregistrement!')

			########### X


			requette2 += 'AND benef_id = {} '.format(beneficiairep.id)
			requette2 +='AND statut_benef = {}'.format(statut_x)
			# requette2 +='OR statut_benef = {}'.format(statut_x)

			print('** la requette2 **')
			print(requette2)
			print(beneficiairep.name)
			cr.execute(requette2)
			beneficiairec_liste = cr.fetchall()
			requette2 = req2
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['garant_id'] = beneficiairec.garant_id.id
				data2['police_id'] = beneficiairec.police_id.id
				data2['college_id'] = beneficiairec.college_id.id
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				# data2['ass_p_id'] = beneficiairec.benef_id.id
				data2['ass_p_id'] = depend_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['nombre_autre'] = 1
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef2').create(cr, uid, data2, context)

		if ((stat_incorp) or (stat_ret) or (stat_susp) or (limit_age ) or (r_statut)):
			cr.execute('DELETE  FROM mcisogem_recherche_benef2 WHERE create_uid = %s', (uid,))
			print('** CONDITION POUR ASSUREES DEPENDANTS **')
			print('** la requette3 **')
			print(requette3)
			cr.execute(requette3)
			beneficiairec_liste = cr.fetchall()
			requette3 = req3
			for ind_benef_e in beneficiairec_liste:
				print(ind_benef_e)

				beneficiairec = self.pool.get('mcisogem.benef').browse(cr, uid, ind_benef_e, context)
				print(beneficiairec.name)
				data2 = {}
			
				data2['beneficiaire'] = beneficiairec.name
				data2['nom_benef'] = beneficiairec.nom
				data2['prenom_benef'] = beneficiairec.prenom_benef
				data2['garant_id'] = beneficiairec.garant_id.id
				data2['police_id'] = beneficiairec.police_id.id
				data2['college_id'] = beneficiairec.college_id.id
				data2['souscripteur_id'] = beneficiairec.souscripteur_id.id
				data2['ass_p_id'] = depend_id.id
				data2['date'] = beneficiairec.dt_naiss_benef
				data2['date_ef'] = beneficiairec.dt_effet
				data2['statut'] = beneficiairec.statut_benef.id
				data2['genre'] = beneficiairec.sexe
				data2['image_medium'] = beneficiairec.image_medium
				# data2['regime_id'] = regime
				data2['critere_id'] = ids[0]

				self.pool.get('mcisogem.recherche.benef2').create(cr, uid, data2, context)



		####################### REMPLISSAGE DES PARAMETTRES #########################

		cr.execute('DELETE  FROM mcisogem_garant_etat_benef WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT garant_id FROM mcisogem_recherche_benef2 WHERE create_uid = %s', (uid,))
		garant_liste = cr.fetchall()
		for ind_garant in garant_liste:
			centre = self.pool.get('mcisogem.garant').browse(cr, uid, ind_garant, context)
			data1 = {}
			data1['garant_id'] = centre.id
			data1['tempo1_id'] = ids[0]
			self.pool.get('mcisogem.garant.etat.benef').create(cr, uid, data1, context)


		cr.execute('DELETE  FROM mcisogem_police_etat_benef WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT garant_id FROM mcisogem_garant_etat_benef WHERE create_uid = %s', (uid,))
		garant_liste = cr.fetchall()
		for ind_garant in garant_liste:
			cr.execute('SELECT DISTINCT police_id FROM mcisogem_recherche_benef2 WHERE create_uid = %s and garant_id =%s', (uid,ind_garant,))
			police_liste = cr.fetchall()
			for ind_police in police_liste:
				police = self.pool.get('mcisogem.police').browse(cr, uid, ind_police, context)
				data1 = {}
				data1['garant_id'] = ind_garant
				data1['police_id'] = police.id
				data1['tempo2_id'] = ids[0]
				self.pool.get('mcisogem.police.etat.benef').create(cr, uid, data1, context)


		cr.execute('DELETE  FROM mcisogem_college_etat_benef WHERE create_uid = %s', (uid,))
		cr.execute('SELECT DISTINCT garant_id FROM mcisogem_garant_etat_benef WHERE create_uid = %s', (uid,))
		garant_liste = cr.fetchall()
		cr.execute('SELECT DISTINCT police_id FROM mcisogem_police_etat_benef WHERE create_uid = %s', (uid,))
		police_liste = cr.fetchall()
		for ind_garant in garant_liste:
			for ind_police in police_liste:
				cr.execute('SELECT DISTINCT college_id FROM mcisogem_recherche_benef2 WHERE create_uid = %s and garant_id =%s and police_id =%s', (uid,ind_garant,ind_police,))
				college_liste = cr.fetchall()
				for ind_college in college_liste:
					college = self.pool.get('mcisogem.college').browse(cr, uid, ind_college, context)

					cr.execute('SELECT sum(nombre_a) as nombre_a,sum(nombre_c) as nombre_c,sum(nombre_e) as nombre_e,sum(nombre_p) as nombre_p,sum(nombre_autre) as nombre_autre FROM mcisogem_recherche_benef2 WHERE create_uid = %s and garant_id =%s and police_id =%s and college_id =%s', (uid,ind_garant,ind_police,ind_college,))
					nombres = cr.fetchone()

					print('** LES TOTAUX **')
					print(nombres)

					if (nombres[0]):

						nombre_a = nombres[0]
					else:
						nombre_a = 0

					if (nombres[1]):

						nombre_c = nombres[1]
					else:
						nombre_c = 0

					if (nombres[2]):

						nombre_e = nombres[2]
					else:
						nombre_e = 0

					if (nombres[3]):

						nombre_p = nombres[3]
					else:
						nombre_p = 0

					if (nombres[4]):

						nombre_autre = nombres[4]
					else:
						nombre_autre = 0

					

					data1 = {}
					data1['garant_id'] = ind_garant
					data1['police_id'] = ind_police
					data1['college_id'] = college.id
					data1['nombre_famille'] = (nombre_a + nombre_c + nombre_e + nombre_p + nombre_autre)
					data1['nombre_a'] = nombre_a
					data1['nombre_c'] = nombre_c
					data1['nombre_e'] = nombre_e
					data1['nombre_p'] = nombre_p
					data1['nombre_autre'] = nombre_autre
					data1['tempo3_id'] = ids[0]
					self.pool.get('mcisogem.college.etat.benef').create(cr, uid, data1, context)


		###############################################################
	

class mcisogem_recherche_benef2(osv.osv):
	_name = 'mcisogem.recherche.benef2'

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

	_columns = {
		'critere_id': fields.many2one('mcisogem.recherche.benef','critere'),
		'beneficiaire' : fields.char('Matricule'),
		'nom_benef' : fields.char('Nom'),
		'prenom_benef' : fields.char('Prenom'),
		'garant_id' : fields.many2one('mcisogem.garant','Garant'),
		'police_id' : fields.many2one('mcisogem.police','Police'),
		'college_id' : fields.many2one('mcisogem.college','Collège'),
		'souscripteur_id' : fields.many2one('mcisogem.souscripteur','Souscripteur'),
		'ass_p_id' : fields.integer('Adhérent'),
		'date' : fields.datetime('Date de naissance'),
		'date_ef' : fields.datetime('Date effet'),
		'statut' : fields.many2one('mcisogem.stat.benef' , 'Statut Bénéficiare'),
		'genre' : fields.char('Genre'),
		'nombre_famille' : fields.integer('Nombre famille'),
		'nombre_a' : fields.integer('Nombre assuré principal'),
		'nombre_c' : fields.integer('Nombre Conjoint'),
		'nombre_e' : fields.integer('Nombre Enfant'),
		'nombre_p' : fields.integer('Nombre Parent'),
		'nombre_autre' : fields.integer('Nombre autre'),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.recherche.benef2': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.recherche.benef2': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
	
	}
	_rec_name = "beneficiaire"
