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

_logger = logging.getLogger(__name__)


class mcisogem_benef(osv.osv):
	_name = "mcisogem.benef"
	_description = 'beneficiaire'

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

	TYPE_SURPRIME = [
		('F', 'Forfait'),
		('T', 'Taux (%)')
	]




	LIEN = [('E', 'Enfant'), ('C', 'Conjoint')]

	def _get_group(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel  where uid=%s', (uid,))
		group_id = cr.fetchone()[0]
		group_obj = self.pool.get('res.groups').browse(cr, uid, group_id, context=context)
		if group_obj.name == 'Financial Manager':
			return True
		else:
			return False

	def _get_regime_centre(self, cr, uid, context=None):
		cod_gest_id = self.pool.get('mcisogem.centre.gestion').search(cr,uid,[],limit=1)
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)

		return gest_obj.avoir_ro

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

	def _get_garant(self, cr, uid, context):
		if context.get('garant'):
			return context.get('garant')
		else:
			return False

	def _get_date_effet(self, cr, uid, context):
		if context.get('date_eff'):
			return context.get('date_eff')
		else:
			return False

	def _get_assure_princ(self, cr, uid, context):
		if context.get('benef_id'):
			return context.get('benef_id')
		else:
			if context.get('benef_idi'):
				return context.get('benef_idi')
			else:
				return False
			if context.get('est_assur_dependi'):
				return True
			else:
				return False

	def _get_est_depend(self, cr, uid, context):
		if context.get('est_assur_depend'):
			return True
		else:
			if context.get('est_assur_dependi'):
				return True
			else:
				return False

	def _get_police(self, cr, uid, context):
		if context.get('police'):
			return context.get('police')
		else:
			return False

	def _get_nom(self, cr, uid, context):
		if context.get('nom'):
			return context.get('nom')
		else:
			return False

	def _get_prenom(self, cr, uid, context):
		if context.get('prenom_benef'):
			return context.get('prenom_benef')
		else:
			return False

	def _get_college(self, cr, uid, context):
		if context.get('college_id'):
			return context.get('college_id')
		else:
			return False

	def _get_nom_assur_princ(self, cr, uid, context):
		if context.get('nom_assur_princ'):
			return context.get('nom_assur_princ')
		else:
			return False

	def _get_prenom_assur_princ(self, cr, uid, context):
		if context.get('prenom_assur_princ'):
			return context.get('prenom_assur_princ')
		else:
			return False

	def _get_statut_benef(self, cr, uid, context):
		if context.get('statut_benef'):
			return context.get('statut_benef')
		else:
			return False

	def _get_code_statut(self, cr, uid, context):
		if context.get('code_statut'):
			return context.get('code_statut')
		else:
			return False

	def _get_creat_incorpo(self, cr, uid, context):
		if context.get('creat_incorpo'):
			return 'I'
		else:
			return 'C'

	def _get_motif_suspension(self, cr, uid, context):
		if context.get('motif_suspension'):
			return context.get('motif_suspension')
		else:
			return False

	def _get_souscripteur_id(self, cr, uid, context):
		if context.get('souscripteur_id'):
			return context.get('souscripteur_id')
		else:
			return False

	def _get_nom_jeun_fille(self, cr, uid, context):
		if context.get('nom_jeun_fille'):
			return context.get('nom_jeun_fille')
		else:
			return False

	def _get_adr_benef(self, cr, uid, context):
		if context.get('adr_benef'):
			return context.get('adr_benef')
		else:
			return False

	def _get_cod_bp_benef(self, cr, uid, context):
		if context.get('cod_bp_benef'):
			return context.get('cod_bp_benef')
		else:
			return False

	def _get_bp_benef(self, cr, uid, context):
		if context.get('bp_benef'):
			return context.get('bp_benef')
		else:
			return False

	def _get_tel_benef(self, cr, uid, context):
		if context.get('tel_benef'):
			return context.get('tel_benef')
		else:
			return False

	def _get_fax_benef(self, cr, uid, context):
		if context.get('fax_benef'):
			return context.get('fax_benef')
		else:
			return False

	def _get_matric_chez_souscr(self, cr, uid, context):
		if context.get('matric_chez_souscr'):
			return context.get('matric_chez_souscr')
		else:
			return False

	def _get_dt_naiss_benef(self, cr, uid, context):
		if context.get('dt_naiss_benef'):
			return context.get('dt_naiss_benef')
		else:
			return False

	def _get_lieu_naiss_benef(self, cr, uid, context):
		if context.get('lieu_naiss_benef'):
			return context.get('lieu_naiss_benef')
		else:
			return False

	def _get_sexe(self, cr, uid, context):
		if context.get('sexe'):
			return context.get('sexe')
		else:
			return False

	def _get_mod_paiem_benef(self, cr, uid, context):
		if context.get('mod_paiem_benef'):
			return context.get('mod_paiem_benef')
		else:
			return False

	def _get_num_banq_benef(self, cr, uid, context):
		if context.get('num_banq_benef'):
			return context.get('num_banq_benef')
		else:
			return False

	def _get_num_guichet_benef(self, cr, uid, context):
		if context.get('num_guichet_benef'):
			return context.get('num_guichet_benef')
		else:
			return False

	def _get_num_compt_benef(self, cr, uid, context):
		if context.get('num_compt_benef'):
			return context.get('num_compt_benef')
		else:
			return False

	def _get_cle_rib_benef(self, cr, uid, context):
		if context.get('cle_rib_benef'):
			return context.get('cle_rib_benef')
		else:
			return False

	def _get_cum_an_recl_benef(self, cr, uid, context):
		if context.get('cum_an_recl_benef'):
			return context.get('cum_an_recl_benef')
		else:
			return False

	def _get_cum_an_recl_fam(self, cr, uid, context):
		if context.get('cum_an_recl_fam'):
			return context.get('cum_an_recl_fam')
		else:
			return False

	def _get_poids_benef(self, cr, uid, context):
		if context.get('poids_benef'):
			return context.get('poids_benef')
		else:
			return False

	def _get_taille_benef(self, cr, uid, context):
		if context.get('taille_benef'):
			return context.get('taille_benef')
		else:
			return False

	def _get_dt_mensuration(self, cr, uid, context):
		if context.get('dt_mensuration'):
			return context.get('dt_mensuration')
		else:
			return False

	def _get_group_sang_benef(self, cr, uid, context):
		if context.get('group_sang_benef'):
			return context.get('group_sang_benef')
		else:
			return False

	def _get_bl_trt_en_cours(self, cr, uid, context):
		if context.get('bl_trt_en_cours'):
			return context.get('bl_trt_en_cours')
		else:
			return False

	def _get_trt_en_cours_until(self, cr, uid, context):
		if context.get('trt_en_cours_until'):
			return context.get('trt_en_cours_until')
		else:
			return False

	def _get_specif_trav_benef(self, cr, uid, context):
		if context.get('specif_trav_benef'):
			return context.get('specif_trav_benef')
		else:
			return False

	def _get_predisp_benef(self, cr, uid, context):
		if context.get('predisp_benef'):
			return context.get('predisp_benef')
		else:
			return False

	def _get_allergie_benef(self, cr, uid, context):
		if context.get('allergie_benef'):
			return context.get('allergie_benef')
		else:
			return False

	def _get_anteced_medic(self, cr, uid, context):
		if context.get('anteced_medic'):
			return context.get('anteced_medic')
		else:
			return False

	def _get_anteced_obstetric(self, cr, uid, context):
		if context.get('anteced_obstetric'):
			return context.get('anteced_obstetric')
		else:
			return False

	def _get_anteced_fam(self, cr, uid, context):
		if context.get('anteced_fam'):
			return context.get('anteced_fam')
		else:
			return False

	def _get_anteced_chir(self, cr, uid, context):
		if context.get('anteced_chir'):
			return context.get('anteced_chir')
		else:
			return False

	def _get_transfus_benef(self, cr, uid, context):
		if context.get('transfus_benef'):
			return context.get('transfus_benef')
		else:
			return False

	def _get_prothese_benef(self, cr, uid, context):
		if context.get('prothese_benef'):
			return context.get('prothese_benef')
		else:
			return False

	def _get_obs_benef(self, cr, uid, context):
		if context.get('obs_benef'):
			return context.get('obs_benef')
		else:
			return False

	def _get_imagei(self, cr, uid, context):
		if context.get('image'):
			return context.get('image')
		else:
			return False

	def _get_image_medium(self, cr, uid, context):
		if context.get('image_medium'):
			return context.get('image_medium')
		else:
			return False

	def _get_image_small(self, cr, uid, context):
		if context.get('image_small'):
			return context.get('image_small')
		else:
			return False

	def _get_numavenant(self, cr, uid, context):
		if context.get('numavenant'):
			return context.get('numavenant')
		else:
			return False

	def _get_numcarte(self, cr, uid, context):
		if context.get('numcarte'):
			return context.get('numcarte')
		else:
			return False

	def _get_tmp_stamp_photo(self, cr, uid, context):
		if context.get('tmp_stamp_photo'):
			return context.get('tmp_stamp_photo')
		else:
			return False

	def _get_cod_photo(self, cr, uid, context):
		if context.get('cod_photo'):
			return context.get('cod_photo')
		else:
			return False

	def _get_photo_ben(self, cr, uid, context):
		if context.get('photo_ben'):
			return context.get('photo_ben')
		else:
			return False

	def _get_statut(self, cr, uid, context):
		if context.get('statut'):
			return context.get('statut')
		else:
			return 'A'

	def _get_valide_quittance(self, cr, uid, context):
		if context.get('valide_quittance'):
			return context.get('valide_quittance')
		else:
			return 0

	def _get_date_quittance(self, cr, uid, context):
		if context.get('date_quittance'):
			return context.get('date_quittance')
		else:
			return False

	def calcul_age(self, cr, uid, ids, field_name, arg, context=None):

		res = {}
		for benef in self.pool.get('mcisogem.benef').browse(cr, uid, ids, context):
			dn_benef = benef.dt_naiss_benef

			date_today = time.strftime("%Y-%m-%d", time.localtime())
			date_today = datetime.strptime(str(date_today), "%Y-%m-%d")

			age_benef = (int(str(date_today)[0:4]) - int(str(dn_benef)[0:4]))

			res[benef.id] = age_benef

		return res

	def a_droit(self,cr,uid,field_name, arg, context=None):
		res = {}
		
		for prestation in self.pool.get('mcisogem.prestation').browse(cr,uid,ids,context):
			a_droit = False
			
			if self.pool.get('res.users').browse(cr,uid,uid).centre_id == prestation.centre_id:
				a_droit = True
			
			res['prestation.id'] = a_droit
			
		return res
		

	_columns = {
		'police_id': fields.many2one('mcisogem.police', "Police", required=True),
		'college_id': fields.many2one('mcisogem.college', 'Collège', required=True),
		'avoir_ss_id': fields.boolean('A un numéro de sécurité sociale ?', readonly=True),
		'ss_id': fields.char('N° Sécurité sociale'),
		'avoir_surprime': fields.boolean('A une surprime ?'),
		'surprime': fields.integer('Valeur'),
		'type_surprime' : fields.selection(TYPE_SURPRIME, 'Type surprime', required=False),
		'eleve': fields.boolean('Elève'),
		'est_assur_depend': fields.boolean('Dépendant ?'),
		'benef_id': fields.many2one('mcisogem.benef', 'Assuré Principal'),
		'mat_assur_princ': fields.char('Matricule'),
		'nom_assur_princ': fields.char('Nom'),
		'prenom_assur_princ': fields.char('Prénoms'),
		'statut_benef': fields.many2one('mcisogem.stat.benef', 'Statut de Bénéficiare'),
		'code_statut': fields.char(''),
		'chargement': fields.integer(''),
		'creat_incorpo': fields.selection([('C', 'creation'), ('I', 'Incorporation')], 'Statut', required=True),
		'motif_suspension': fields.many2one('mcisogem.motif.suspen.benef', 'Motif de suspension', select=True),
		'date_suspension': fields.datetime('Date de suspension'),
		'date_exclusion': fields.datetime('Date de retrait'),
		'garant_id': fields.many2one('mcisogem.garant', "Garant", required=True),
		'avenant_id': fields.many2one('mcisogem.avenant', 'Avenant'),
		'souscripteur_id': fields.many2one('mcisogem.souscripteur', 'Souscripteur', required=True, readonly=True),
		'matric_benef': fields.char('matricule', readonly=True),
		'new_matricule_benef': fields.char('Matricule', size=15),
		'name': fields.char('beneficiaire'),
		'nom': fields.char('Nom', required=True),
		'nom_jeun_fille': fields.char('Nom de jeune fille'),
		'prenom_benef': fields.char('prenom', required=True),
		'adr_benef': fields.char('adresse'),
		'cod_bp_benef': fields.char('code BP'),
		'bp_benef': fields.char('Bp benef'),
		'tel_benef': fields.char('Téléphone'),
		'fax_benef': fields.char('Fax'),
		'matric_chez_souscr': fields.char('Matricule chez souscripteur'),
		'matric_isa': fields.char('Matricule ISA'),
		'dt_naiss_benef': fields.date('Date de naissance', required=True),
		'lieu_naiss_benef': fields.char('Lieu de naissance'),
		'couverture': fields.integer('Couverture'),
		'rang': fields.integer('Rang'),

		'sexe': fields.selection(SEXE, 'Genre', required=True),
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
		'trt_en_cours_until': fields.char('Traitement en cours'),
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
											'mcisogem.benef': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
										},
										help="Medium-sized image of the product. It is automatically " \
											 "resized as a 128x128px image, with aspect ratio preserved, " \
											 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
									   string="Small-sized image", type="binary", multi="_get_image",
									   store={
										   'mcisogem.benef': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
									   },
									   help="Small-sized image of the product. It is automatically " \
											"resized as a 64x64px image, with aspect ratio preserved. " \
											"Use this field anywhere a small image is required."),
		'numavenant': fields.integer('numero avenant'),
		'numcarte': fields.char('numero carte'),
		'tmp_stamp_photo': fields.char('tmp_stamp_photo'),
		'cod_photo': fields.integer('cod_photo'),
		'photo_ben': fields.char('photo_ben'),
		'affiche': fields.boolean('', ),
		'affiche_col': fields.boolean('', ),
		'state': fields.selection([
			('draft', "Nouveau"),
			('sent', "Comptabilité"),
			('done', "Informations Comptable"),
			('cancel', "Annuler"),
			('finish', "Terminer"),
		], 'Statut', required=True, readonly=True),
		'statut': fields.selection([('A', 'Actif'), ('S', 'Suspendu'), ('R', 'Retiré')], 'Etat du Bénéficiare'),
		'dt_entree': fields.date('Date d\'entrée', required=True),
		'dt_effet': fields.date('Date d\'effet', required=True),
		'nbre_police_comp': fields.integer('Nombre de polices complémentaires'),
		'police_complementaire_ids': fields.one2many('mcisogem.police.complementaire.beneficiaire', 'beneficiaire_id',
													 'Police(s) complémentaire(s)'),
		'valide_quittance': fields.integer('valide_quittance'),
		'date_quittance': fields.datetime('Date quittance'),
		'age': fields.function(calcul_age, type='integer', string='Age'),

	}

	'''def _numero_matricule(self, cr, uid, context=None):
		cr.execute('select num_benef from mcisogem_numero')
		numero = cr.fetchone()[0]
		print '*****************'
		print numero
		inc_num=numero + 1
		print '*****************'
		print inc_num
		return inc_num '''

	_defaults = {
		# 'est_assur_depend' : True,
		'valide_quittance': 0,
		'chargement': 1,
		'police_id': _get_police,
		'college_id': _get_college,
		'avoir_ss_id': _get_regime_centre,
		'benef_id': _get_assure_princ,
		'garant_id': _get_garant,
		'creat_incorpo': _get_creat_incorpo,
		'dt_effet': _get_date_effet,
		'dt_entree': time.strftime("%Y-%m-%d", time.localtime()),
		'type_surprime' : 'F',
		'est_assur_depend': _get_est_depend,
		'nom_assur_princ': _get_nom_assur_princ,
		'prenom_assur_princ': _get_prenom_assur_princ,
		'statut_benef': _get_statut_benef,
		'souscripteur_id': _get_souscripteur_id,
		'nom': _get_nom,
		'nom_jeun_fille': _get_nom_jeun_fille,
		'prenom_benef': _get_prenom,
		'adr_benef': _get_adr_benef,
		'cod_bp_benef': _get_cod_bp_benef,
		'bp_benef': _get_bp_benef,
		'tel_benef': _get_tel_benef,
		'matric_chez_souscr': _get_matric_chez_souscr,
		'dt_naiss_benef': _get_dt_naiss_benef,
		'lieu_naiss_benef': _get_lieu_naiss_benef,
		'couverture': 0,
		'rang': 0,
		'sexe': _get_sexe,
		'mod_paiem_benef': _get_mod_paiem_benef,
		'num_banq_benef': _get_num_banq_benef,
		'num_guichet_benef': _get_num_guichet_benef,
		'num_compt_benef': _get_num_compt_benef,
		'cle_rib_benef': _get_cle_rib_benef,
		'cum_an_recl_benef': _get_cum_an_recl_benef,
		'cum_an_recl_fam': _get_cum_an_recl_fam,
		'poids_benef': _get_poids_benef,
		'taille_benef': _get_taille_benef,
		'dt_mensuration': _get_dt_mensuration,
		'group_sang_benef': _get_group_sang_benef,
		'bl_trt_en_cours': _get_bl_trt_en_cours,
		'trt_en_cours_until': _get_trt_en_cours_until,
		'specif_trav_benef': _get_specif_trav_benef,
		'predisp_benef': _get_predisp_benef,
		'allergie_benef': _get_allergie_benef,
		'anteced_medic': _get_anteced_medic,
		'anteced_obstetric': _get_anteced_obstetric,
		'anteced_fam': _get_anteced_fam,
		'anteced_chir': _get_anteced_chir,
		'transfus_benef': _get_transfus_benef,
		'prothese_benef': _get_prothese_benef,
		'obs_benef': _get_obs_benef,
		'image': _get_imagei,
		'image_medium': _get_image_medium,
		'image_small': _get_image_small,
		'numavenant': _get_numavenant,
		'numcarte': _get_numcarte,
		'tmp_stamp_photo': _get_tmp_stamp_photo,
		'cod_photo': _get_cod_photo,
		'photo_ben': _get_photo_ben,
		'affiche': _get_regime_centre,
		'state': 'draft',
		'statut': _get_statut,
	}

	def button_demande_retrait(self,cr,uid,ids,context):
		benef = self.browse(cr, uid, ids[0], context=context).id
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if self.pool.get('mcisogem.retrait').search_count(cr,uid,[('beneficiaire_id' , '=' ,benef) , ('state' , '=' , 'attente')]) > 0:
			raise osv.except_osv('Attention' , 'Ce bénéficiaire a déjà une demande en attente !')
		if garant_user_id:
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
				'domain' : [('garant_id', '=', garant_user_id)],
				'type' : 'ir.actions.act_window',
				'context': ctx7,

			}

	def button_demande_suspend(self,cr,uid,ids,context):
		benef = self.browse(cr, uid, ids[0], context=context).id
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if self.pool.get('mcisogem.suspend').search_count(cr,uid,[('beneficiaire_id' , '=' ,benef) , ('state' , '=' , 'attente')]) > 0:
			raise osv.except_osv('Attention' , 'Ce bénéficiaire a déjà une demande en attente !')
		if garant_user_id:
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
				'domain' : [('garant_id', '=', garant_user_id)],
				'type' : 'ir.actions.act_window',
				'context': ctx7,

			}

	def button_to_prestation(self, cr, uid, ids, context):
		context = {'search_default_group_exercice_id': 1,'search_default_group_periode_id': 1}
		ctx = (context or {}).copy()
		ctx['beneficiaire_id'] = ids[0]
		# ctx['context'] = {'search_default_group_exercice_id': 1,'search_default_group_periode_id': 1}
		tree_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_prestation_tree')[1]
		form_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_prestation_form')[1]
		search_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_prestation_filter')[1]
		return {
			'name': 'Prestations',
			'view_type': 'form',
			'view_mode': 'form,tree',
			'res_model': 'mcisogem.prestation',
			'target': 'current',
			'views': [(tree_id, 'tree'), (form_id, 'form')],
			'view_id': form_id,
			'type': 'ir.actions.act_window',
			'domain': [('beneficiaire_id', '=', ctx['beneficiaire_id'])],
			'context': ctx,
			'nodestroy': True,
		}

	def button_reseau_soins(self, cr, uid, ids, context):
		benef_id = ids[0]

		polices = []
		colleges = []

		police_id = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id).police_id.id
		college_id = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id).college_id.id

		polices.append(police_id)
		colleges.append(college_id)

		p = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid,
																				[('beneficiaire_id', '=', benef_id)],
																				order='niveau ASC')

		if p:
			for police_id in self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid, p):
				polices.append(police_id.police_id.id)
				colleges.append(police_id.college_id.id)

		form_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_mcisogem_rata_reseau_police_form')[
			1]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_rata_reseau_police_tree')[1]

		return {
			'name': 'Réseau de soins',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'mcisogem.rata.reseau.police',
			'target': 'current',
			# 'views': [(tree_id, 'tree'), (form_id, 'form')],
			# 'view_id': form_id,
			'view_id' : False,
			'type': 'ir.actions.act_window',
			'domain': [('college_id', 'in', colleges), ('police_id', 'in', polices)],
			'nodestroy': True,
		}

	def button_histo_benef(self, cr, uid, ids, context):
		benef_data = self.browse(cr, uid, ids, context=context)

		# la police du beneficiaire
		police_search = self.pool.get('mcisogem.police').search(cr, uid, [('id', '=', benef_data.police_id.id)])
		police_data = self.pool.get('mcisogem.police').browse(cr, uid, police_search)

		ctx = (context or {}).copy()
		ctx['garant'] = police_data.garant_id.id
		ctx['police'] = police_data.id
		ctx['action'] = 'histo'
		ctx['benef_id'] = ids[0]

		ctx['est_assur_depend'] = True
		ctx['nom'] = benef_data.nom
		ctx['prenom'] = benef_data.prenom_benef
		ctx['num_interne_police'] = benef_data.police_id.id
		
		stat = self.pool.get('mcisogem.stat.benef').search(cr,uid,[('cod_statut_benef' , '=' , 'C')])
		ctx['statut_benef'] = self.pool.get('mcisogem.stat.benef').browse(cr,uid,stat).id
		
		form_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_mcisogem_benef_form')[1]
		tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_benef_tree')[1]
		kanban_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_benef_kanban')[1]

		return {
			'name': 'Incorporation de dépendants',
			'view_type': 'form',
			'view_mode': 'tree,form,kanban',
			'res_model': 'mcisogem.benef',
			'target': 'current',
			'views': [(tree_id, 'tree'), (form_id, 'form'), (kanban_id, 'kanban')],
			'view_id': form_id,
			'type': 'ir.actions.act_window',
			'domain': [('benef_id', '=', ctx['benef_id'])],
			'context': ctx,
			'nodestroy': True,
		}

	def button_surprime(self, cr, uid, ids, context):
		benef_data = self.browse(cr, uid, ids, context=context)

		# la police du beneficiaire
		police_search = self.pool.get('mcisogem.police').search(cr, uid, [('id', '=', benef_data.police_id.id)])
		police_data = self.pool.get('mcisogem.police').browse(cr, uid, police_search)

		ctx = (context or {}).copy()
		ctx['garant'] = police_data.garant_id.id
		ctx['police'] = police_data.id
		ctx['benef_id'] = ids[0]

		form_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_surprime_form')[1]
		tree_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_surprime_tree')[1]

		return {
			'name': 'Surprime',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'mcisogem.surprime',
			'target': 'current',
			'views': [(tree_id, 'tree'), (form_id, 'form')],
			'view_id': form_id,
			'type': 'ir.actions.act_window',
			'domain': [('benef_id', '=', ctx['benef_id'])],
			'context': ctx,
			'nodestroy': True,
		}

	def button2_to_sent(self, cr, uid, ids, context=None):
		"""L utilisateur envoi la requete a la comptabilite pour ajouter les informations comptable"""
		# souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, uid, context=context)
		# usr = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		message = 'Un souscripteur a ete creer veuillez renseigner les informations comptable'

		cr.execute('select id from res_groups where name=%s', ('Settings',))
		group_id = cr.fetchone()[0]
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		ident_centre = cr.fetchone()[0]
		res_users = self.pool('res.users')
		user_ids = res_users.search(
				cr, SUPERUSER_ID, [
					('code_gest_id', '=', ident_centre),
					('groups_id', 'in', group_id)
				], context=context)
		partner_id = []

		if user_ids:
			partner = self.pool.get('res.partner').browse(cr, uid, uid, context=context)
			partner_id = list(
				set(u.partner_id.id for u in res_users.browse(cr, SUPERUSER_ID, user_ids, context=context)))
			partner.message_post(cr, uid, False,
								 body=message,
								 partner_ids=partner_id,
								 subtype='mail.mt_comment', context=context
								 )
		return self.write(cr, uid, ids, {'state': 'done'}, context=context)

	def button2_to_done(self, cr, uid, ids, context=None):
		"""La comptabilite renseigne et valide les informations comptable"""
		compta = self.read(cr, uid, ids, ['num_banq_benef', 'num_compt_benef', 'num_compt_benef', \
										  'cle_rib_benef'])
		if not compta['num_banq_benef'] or not compta['num_compt_benef'] or not compta['num_compt_benef'] or not compta[
			'cle_rib_benef']:
			raise osv.except_osv('Attention !', "Vous devez renseigner tous les champs comptable avant de valider!")
			return False;
		self.write(cr, uid, ids, {'state': 'finish'}, context=context)
		return True

	def button2_to_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'done'}, context=context)
		return True

	def onchange_police(self, cr, uid, ids, police_id, context=None):
		if not police_id:
			return False
		else:

			s_police = self.pool.get('mcisogem.police').search(cr, uid, [('id', '=', police_id)])
			la_police = self.pool.get('mcisogem.police').browse(cr, uid, s_police, context)

			datedujour = time.strftime('%Y-%m-%d', time.localtime())

			cr.execute(
				"select distinct code_college from mcisogem_histo_police where name=%s and dt_eff_histo_pol >=%s",
				(police_id, datedujour))

			lescollegespolices = cr.dictfetchall()

			cr.execute("delete from mcisogem_college_temporaire where create_uid=%s", (uid,))

			for col in lescollegespolices:
				cr.execute("insert into mcisogem_college_temporaire (create_uid,write_uid,name) values(%s, %s, %s)",
						   (uid, uid, col['code_college']))

			return {'value': {'souscripteur_id': la_police.souscripteur_id}}

	def onchange_ss_id(self, cr, uid, ids, avoir_ss_id, context=None):
		v = {}
		d = {}
		if avoir_ss_id:
			police = self._get_police(cr, uid, context)
			# d = {'police_complementaire_ids' : [('police_id' , '!=' , police)]}
			v = {'avoir_ss_id': True, 'ss_id': ''}
			return {'value': v , 'domain' : d}

	def onchange_code_statut(self, cr, uid, ids, statut, context=None):
		v = {}
		statut = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut)
		if statut:
			v = {'code_statut': statut.cod_statut_benef}
			return {'value': v}

	def onchange_benef_id(self, cr, uid, ids, benef_id, context=None):
		v = {}
		if benef_id:
			s_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('id', '=', benef_id)])
			benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, s_benef)

			if benef_data.ss_id:
				mat = benef_data.ss_id
			else:
				mat = benef_data.new_matricule_benef

			v = {'nom': benef_data.nom, 'nom_assur_princ': benef_data.nom,
				 'prenom_assur_princ': benef_data.prenom_benef, 'police_id': benef_data.police_id,
				 'souscripteur_id': benef_data.souscripteur_id, 'garant_id': benef_data.garant_id,
				 'college_id': benef_data.college_id, 'mat_assur_princ': mat}
			return {'value': v}

	def onchange_assur_depend(self, cr, uid, ids, est_assur_depend, context=None):
		statut_search = self.pool.get('mcisogem.stat.benef').search(cr, uid, [('cod_statut_benef', '=', 'A')])
		statut = self.pool.get('mcisogem.stat.benef').browse(cr, uid, statut_search).id

		v = {}
		v = {'benef_id': False, 'nom_assur_princ': '', 'prenom_assur_princ': '', 'statut_benef': statut}
		d = {}
		d = {'statut_benef': [('id', '=', statut)]}

		if est_assur_depend == True:
			d = {'statut_benef': [('id', '!=', statut)]}
			stat_idd = self.pool.get('mcisogem.stat.benef').search(cr,uid,[('cod_statut_benef' , '=' , 'C')])
			if stat_idd:
			    v = {'statut_benef': stat_idd}

		return {'value': v, 'domain': d}

	def button_histo_suspension(self, cr, uid, ids, context=None):
		ctx = (context or {}).copy()

		tree_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_histo_suspension_tree')[
			1]
		form_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_histo_suspension_form')[
			1]

		return {
			'type': 'ir.actions.act_window',
			'name': 'Historique de Suspension du Bénéficaire',
			'view_type': 'form',
			'view_mode': 'tree, form',
			'res_model': 'mcisogem.histo.suspension',
			'views': [(tree_id, 'tree'), (form_id, 'form')],
			'view_id': tree_id,
			'domain': [('benef_id', '=', ids[0])],
			'target': 'current',
			'context': ctx,
		}

	def button_histo_exclusion(self, cr, uid, ids, context=None):
		ctx = (context or {}).copy()

		tree_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_histo_retrait_tree')[1]
		form_id = \
		self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_histo_retrait_form')[1]
		return {
			'type': 'ir.actions.act_window',
			'name': 'Historique de retrait du Bénéficaire',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'mcisogem.histo.retrait',
			'views': [(tree_id, 'tree'), (form_id, 'form')],
			'view_id': tree_id,
			'domain': [('benef_id', '=', ids[0])],
			'target': 'current',
			'context': ctx,
		}

	def button_action_suspendre(self, cr, uid, ids, context=None):
		ctx = (context or {}).copy()

		benef = self.pool.get('mcisogem.benef').search(cr, uid, [('id', '=', ids[0])])
		benef_data = self.browse(cr, uid, benef, context)
		ctx['ids'] = ids
		ctx['id'] = benef_data.id
		ctx['name'] = benef_data.name
		ctx['nom'] = benef_data.nom
		ctx['prenom_benef'] = benef_data.prenom_benef
		ctx['action'] = 'sus'

		form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa',
																	  'view_mcisogem_suspension_benef_form')[1]

		if ctx['name']:
			return {
				'type': 'ir.actions.act_window',
				'name': 'Suspension du Bénéficaire',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'mcisogem.benef',
				'views': [(form_id, 'form')],
				'view_id': form_id,
				'domain': [('name', '=', ctx['name'])],
				'target': 'new',
				'context': ctx,
			}

	def button_action_exclure(self, cr, uid, ids, context=None):
		ctx = (context or {}).copy()

		benef = self.pool.get('mcisogem.benef').search(cr, uid, [('id', '=', ids[0])])
		benef_data = self.browse(cr, uid, benef, context)
		ctx['ids'] = ids
		ctx['id'] = benef_data.id
		ctx['name'] = benef_data.name
		ctx['nom'] = benef_data.nom
		ctx['prenom_benef'] = benef_data.prenom_benef
		ctx['action'] = 'exc'

		form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa',
																	  'view_mcisogem_exclusion_benef_form')[1]

		if ctx['name']:
			return {
				'type': 'ir.actions.act_window',
				'name': 'Retrait bénéficiaire',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'mcisogem.benef',
				'views': [(form_id, 'form')],
				'view_id': form_id,
				'domain': [('name', '=', ctx['name'])],
				'target': 'new',
				'context': ctx,
			}

	def button_action_annuler(self, cr, uid, ids, context=None):

		benef = self.pool.get('mcisogem.benef').search(cr, uid, [('benef_id', '=', ids[0])])
		benef_data = self.browse(cr, uid, ids[0], context)

		if benef_data.statut == 'S':

			self.pool.get('mcisogem.histo.suspension').create(cr, uid,
															  {'benef_id': ids[0],
															   'dt_action': time.strftime("%Y-%m-%d %H:%M:%S",
																						  time.localtime()),
															   'statut': 0, 'action': 'Annulation'})

			for bnf in self.pool.get('mcisogem.benef').browse(cr, uid, benef):
				self.pool.get('mcisogem.benef').write(cr, uid, bnf.id,
													  {'statut': 'A', 'date_suspension': None, 'date_exclusion': None,
													   'valide_quittance': 0, 'creat_incorpo': 'I',
													   'dt_effet': time.strftime("%Y-%m-%d", time.localtime())},
													  context)

				vals = {}
				vals['benef_id'] = bnf.id
				vals['dt_action'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				vals['statut'] = 0
				vals['action'] = 'Annulation'

				self.pool.get('mcisogem.histo.suspension').create(cr, uid, vals)

		if benef_data.statut == 'R':

			self.pool.get('mcisogem.histo.retrait').create(cr, uid,
														   {'benef_id': ids[0],
															'dt_action': time.strftime("%Y-%m-%d %H:%M:%S",
																					   time.localtime()), 'statut': 0,
															'action': 'Annulation'})

			for bnf in self.pool.get('mcisogem.benef').browse(cr, uid, benef):
				vals = {}
				vals['benef_id'] = bnf.id
				vals['dt_action'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				vals['statut'] = 0
				vals['action'] = 'Annulation'

				self.pool.get('mcisogem.benef').write(cr, uid, bnf.id,
													  {'statut': 'A', 'date_suspension': None, 'date_exclusion': None,
													   'valide_quittance': 0, 'creat_incorpo': 'I',
													   'dt_effet': time.strftime("%Y-%m-%d", time.localtime())},
													  context)

				self.pool.get('mcisogem.histo.retrait').create(cr, uid, vals)

		self.write(cr, uid, ids[0],
				   {'statut': 'A', 'date_suspension': None, 'date_exclusion': None, 'valide_quittance': 0,
					'creat_incorpo': 'I', 'dt_effet': time.strftime("%Y-%m-%d", time.localtime())})
		return True

	# valider l exclusion
	def button_valider_exclusion(self, cr, uid, ids, context):
		print('************ OK **********')

	# valider la suspension
	def button_valider(self, cr, uid, ids, context):
		print('************ OK **********')

	def write(self, cr, uid, ids, vals, context=None):
		if "num_banq_benef" in vals or "num_guichet_benef" in vals or "num_compt_benef" in vals or "cle_rib_benef" in vals:
			vals['state'] = 'finish'

		return super(mcisogem_benef, self).write(cr, uid, ids, vals, context=context)

	def create(self, cr, uid, vals, context=None):

		if context.get('action') == 'sus':
			ctx = context or {}

			son_id = self.pool.get('mcisogem.benef').write(cr, uid, context.get('ids')[0],
														   {'statut': 'S',
															'motif_suspension': vals['motif_suspension']}, context)

			self.pool.get('mcisogem.histo.suspension').create(cr, uid,
															  {'benef_id': context.get('ids')[0],
															   'dt_action': time.strftime("%Y-%m-%d %H:%M:%S",
																						  time.localtime()),
															   'statut': True,
															   'motif_suspension': vals['motif_suspension'],
															   'action': 'Suspension'})

			benef = self.pool.get('mcisogem.benef').search(cr, uid, [('benef_id', '=', context.get('ids')[0])])

			for bnf in self.pool.get('mcisogem.benef').browse(cr, uid, benef):
				self.pool.get('mcisogem.benef').write(cr, uid, bnf.id,
													  {'statut': 'S', 'motif_suspension': vals['motif_suspension'],
													   'date_suspension': time.strftime("%Y-%m-%d %H:%M:%S",
																						time.localtime()),
													   'action': 'Suspension'}, context)

				last_id = self.pool.get('mcisogem.histo.suspension').create(cr, uid,
																			{'benef_id': bnf.id,
																			 'dt_action': time.strftime(
																				 "%Y-%m-%d %H:%M:%S", time.localtime()),
																			 'statut': True, 'motif_suspension': vals[
																				'motif_suspension'],
																			 'action': 'Suspension'})

			ctx['action'] = ''
			context = ctx

			return context.get('ids')[0]

		if context.get('action') == 'exc':
			ctx = context or {}

			son_id = self.pool.get('mcisogem.benef').write(cr, uid, context.get('ids')[0],
														   {'statut': 'R', 'date_exclusion': vals['date_exclusion']},
														   context)

			the_id = self.pool.get('mcisogem.histo.retrait').create(cr, uid,
																	{'benef_id': context.get('ids')[0],
																	 'dt_action': time.strftime("%Y-%m-%d %H:%M:%S",
																								time.localtime()),
																	 'statut': True, 'action': 'Exclusion'})

			benef_data = self.browse(cr, uid, context.get('ids')[0], context)
			benef = self.pool.get('mcisogem.benef').search(cr, uid, [('benef_id', '=', benef_data.name)])

			for bnf in self.pool.get('mcisogem.benef').browse(cr, uid, benef):
				self.pool.get('mcisogem.benef').write(cr, uid, bnf.id,
													  {'statut': 'R', 'date_exclusion': vals['date_exclusion']},
													  context)

				self.pool.get('mcisogem.histo.retrait').create(cr, uid,
															   {'benef_id': bnf.id,
																'dt_action': time.strftime("%Y-%m-%d %H:%M:%S",
																						   time.localtime()),
																'statut': True, 'action': 'Exclusion'})

			ctx['action'] = ''
			context = ctx
			return context.get('ids')[0]

		else:
			if vals['dt_effet'] < vals['dt_naiss_benef']:
				raise osv.except_osv('Attention', "La date d'entrée doit être supérieure à la date de naissance ! ")


			

			statut_valide = False

			les_histo = self.pool.get('mcisogem.histo.police').search(cr,uid,[('code_college' , '=' , vals['college_id'])])

			for histo in self.pool.get('mcisogem.histo.police').browse(cr,uid,les_histo):

				for stat in histo.statut_ids:

					if vals['statut_benef'] == stat.id:
						statut_valide = True

						break

				if statut_valide:
					break



			if statut_valide == False:
				raise osv.except_osv('Attention' , "Le statut de bénéficiaire n'est pas pris en compte dans l'historique de police")


			vals['code_statut'] = self.pool.get('mcisogem.stat.benef').browse(cr, uid,
																			  vals['statut_benef']).cod_statut_benef

			vals['garant_id'] = context.get('garant')

			if vals['benef_id']:
				les_valeurs = self.onchange_benef_id(cr, uid, 1, vals['benef_id'])['value']

				vals['police_id'] = les_valeurs['police_id'].id
				vals['souscripteur_id'] = les_valeurs['souscripteur_id'].id
				vals['garant_id'] = les_valeurs['garant_id'].id

			vals['police_id'] = context.get('police')
			vals['avoir_ss_id'] = False

			s_police = self.pool.get('mcisogem.police').search(cr, uid, [('id', '=', context.get('police'))])
			la_police = self.pool.get('mcisogem.police').browse(cr, uid, s_police, context)
			vals['souscripteur_id'] = la_police.souscripteur_id.id

			if vals['benef_id']:
				s_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('id', '=', vals['benef_id'])])
				benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, s_benef)
				vals['mat_assur_princ'] = benef_data.new_matricule_benef
				vals['nom_assur_princ'] = benef_data.nom
				vals['prenom_assur_princ'] = benef_data.prenom_benef

			if self._get_regime_centre(cr, uid):

				if not vals['ss_id']:
					raise osv.except_osv('Attention !', " Vous n'avez pas renseigné  le N° de sécurité sociale !")
				else:


					# on verifie l'unicite du N° de securite sociale
					search_ss_id = self.pool.get('mcisogem.benef').search(cr,uid,[('ss_id' , '=' , vals['ss_id'])])
					if search_ss_id:
						raise osv.except_osv('Attention !', "Ce N° de sécurité sociale a déjà été utilisé !")

					vals['name'] = vals['ss_id']
					vals['avoir_ss_id'] = True

			cr.execute('select code_centre from mcisogem_centre_gestion')
			centre_data = cr.fetchone()[0]
			cr.execute('select pays_id from mcisogem_centre_gestion')
			pays_data = cr.fetchone()[0]

			new_matricule_benef = ''

			pays = self.pool.get('mcisogem.pays').search(cr, uid, [('id', '=', pays_data)])
			pays_data = self.pool.get('mcisogem.pays').browse(cr, uid, pays)


			new_matricule_benef = str(pays_data.name.code) + str(centre_data)


			if vals['sexe'] == 'M':
				if vals['code_statut'] == 'A':
					new_matricule_benef = new_matricule_benef + '0'

				elif vals['code_statut'] == 'C':
					new_matricule_benef = new_matricule_benef + '2'

				elif vals['code_statut'] == 'E':
					new_matricule_benef = new_matricule_benef + '4'

				elif vals['code_statut'] == 'G':
					new_matricule_benef = new_matricule_benef + '6'
				else:
					new_matricule_benef = new_matricule_benef + str(vals['statut_benef'])



			else:

				
				if vals['code_statut'] == 'A':
					new_matricule_benef = new_matricule_benef + '1'

				elif vals['code_statut'] == 'C':
					new_matricule_benef = new_matricule_benef + '3'

				elif vals['code_statut'] == 'E':
					new_matricule_benef = new_matricule_benef + '5'

				elif vals['code_statut'] == 'G':
					new_matricule_benef = new_matricule_benef + '7'
				else:
					new_matricule_benef = new_matricule_benef + str(vals['statut_benef'])


					# Recuperation des informations relatives à l'exercice de la police
			cr.execute("select * from mcisogem_exercice_police where police_id=%s order by id desc",
					   (vals['police_id'],))
			lesexercicespolices = cr.dictfetchall()



			# Recuperation des données relatives à la police
			cr.execute("select * from mcisogem_police where id=%s", (vals['police_id'],))
			lapolice = cr.dictfetchall()[0]

			nbre_quittance_ai = self.pool.get('mcisogem.quittancier').search_count(cr, uid, [
				('police_id', '=', vals['police_id']), ('type_avenant_id', '=', 1)])

			if nbre_quittance_ai > 0:
				vals['creat_incorpo'] = 'I'
			else:
				vals['creat_incorpo'] = 'C'


				# Test pour voir si cette police possède un exercice de police
			if len(lesexercicespolices) > 0:

				# recuperation du numero auto dans la table avenant
				cr.execute("select * from mcisogem_avenant where type_avenant_id=%s order by id desc",
						   (lapolice['typ_ave'],))
				# numave = cr.dictfetchall()[0]
				numave = 1

				# contraintes ajout benef

				nbr_benef = self.pool.get('mcisogem.benef').search_count(cr, uid, [('nom', '=', vals['nom']), (
				'prenom_benef', '=', vals['prenom_benef']), ('sexe', '=', vals['sexe']), ('dt_naiss_benef', '=',
																						  vals['dt_naiss_benef'])])
				cr.execute('select num_benef from mcisogem_numero')
				numero = cr.fetchone()[0]
				benef = numero + 1

				if nbr_benef == 0:

					vals['matric_benef'] = benef
					vals['cum_an_recl_benef'] = 0
					vals['cum_an_recl_fam'] = 0
					vals['numcarte'] = 0
					vals['state'] = 'done'

					image = vals['image_medium']

					res = super(mcisogem_benef, self).create(cr, uid, vals, context=context)

					cr.execute("update mcisogem_numero set num_benef=%s", (benef,))

					if context.get('id_benf_i'):
						self.pool.get('mcisogem.benf_incorpo').write(cr,uid,context.get('id_benf_i'),{'state':'valide','benef_p_id':res},context)

						cr.execute("update mcisogem_benf_incorpo set benef_p_id = %s where benef_id = %s" , (res,context.get('id_benf_i'),))

						

					cr.execute('select id from mcisogem_histo_benef order by id DESC limit 1')

					mat = str(res)

					for i in range(10):
						if len(mat) < 9:
							mat = '0' + mat

					new_matricule_benef = new_matricule_benef + mat


					##################################### Matricule SWAN ##################################

					# new_matricule_benef = '225'

					# mat = str(vals['statut_benef'])
					# for i in range(2):
					# 	if len(mat) < 2:
					# 		mat = '0' + mat

					# new_matricule_benef += mat


					# mat = str(vals['police_id'])
					# for i in range(4):
					# 	if len(mat) < 4:
					# 		mat = '0' + mat

					# new_matricule_benef += mat


					# mat = str(vals['college_id'])
					# for i in range(4):
					# 	if len(mat) < 4:
					# 		mat = '0' + mat


					# new_matricule_benef += mat
					# mat = str(res)
					# for i in range(4):
					# 	if len(mat) < 4:
					# 		mat = '0' + mat


					# new_matricule_benef += mat

					##################################### Matricule SWAN ##################################






					# si le centre a un regime obligatoire
					if not self._get_regime_centre(cr, uid):
						vals['name'] = new_matricule_benef

					super(mcisogem_benef, self).write(cr, uid, res, {'new_matricule_benef': new_matricule_benef,
																	 'name': vals['name'] , 'image_medium' : image}, context=context)


				

				else:
					raise osv.except_osv('Attention !', "Ce beneficiaire existe déja !")
					return {'value': {'police_id': False}}

				obj_histo_benef = self.pool.get('mcisogem.histo.benef')
				# Test pour voir si il s'agit d'une police par tranche d'age ou par statut de bénéficiaire


				data = {}

				data['name'] = vals['name']
				data['avoir_ss_id'] = vals['avoir_ss_id']
				# police par statut beneficiaire
				if lapolice['type_prime'] == '1':

					# insertion des donnees

					data['ss_id'] = vals['ss_id']
					data['matric_benef'] = new_matricule_benef
					data['ass_matric_benef'] = new_matricule_benef
					data['new_matricule_benef'] = new_matricule_benef
					data['statut_benef'] = vals['statut_benef']
					# data['lien_parente'] = vals['lien_parente']
					data['nom'] = vals['nom']
					data['prenom_benef'] = vals['prenom_benef']
					vals['col_id'] = vals['college_id']
					data['police_id'] = vals['police_id']
					data['college_id'] = vals['college_id']
					data['garant_id'] = vals['garant_id']
					# data['avenant_id']=vals['avenant_id']
					data['souscripteur_id'] = vals['souscripteur_id']
					data['dt_eff_mod_benef'] = vals['dt_effet']
					data['police_id'] = vals['police_id']
					data['lbc_souscr_id'] = lapolice['souscripteur_id']
					# data['id_tran_age']=None
					data['sal_brut_benef'] = 0
					data['dt_naiss_benef'] = vals['dt_naiss_benef']
					data['dt_entree_benef'] = time.strftime("%Y-%m-%d", time.localtime())
					data['st_creat_incorpo'] = vals['creat_incorpo']
					data['creat_incorpo'] = vals['creat_incorpo']
					data['st_retr_excl'] = 'A'
					data['dt_sortie_benef'] = '01-01-1900 00:00:00'
					data['bl_excl_definitive'] = 2
					data['college_id'] = vals['college_id']
					data['bl_remb_autorise'] = 1
					data['st_ace_benef'] = 'A'
					data['tmp_stamp'] = time.strftime("%Y-%m-%d", time.localtime())
					# data['num_ave']=numave['id']
					data['num_ave'] = 1
					data['pc_sal_prime'] = 0
					data['bl_pc_sal_prime'] = 0
					data['num_ave_cal'] = 0
					# data['num_ave_pol']=numave['num_ave_interne_police']
					data['num_ave_pol'] = 1
					data['statut'] = 'A'
					data['histo_st_eleve'] = 0
					data['cod_statut_benef'] = 'C'
					# data['matric_chez_souscr'] = vals['matric_chez_souscr']
					data['activation'] = 0

					# data['id_tran_age']=1

					data['mode_prime'] = 0
					data['valide_quittance'] = 0
					data['date_quittance'] = '01-01-1900 00:00:00'
					data['cod_util_quittance'] = uid

					re = super(mcisogem_histo_benef, mcisogem_histo_benef).create(obj_histo_benef, cr, uid, data,
																				  context)
					return res
				else:
					# police par tranche d'age

					# insertion des donnees
					data['ss_id'] = vals['ss_id']

					data['nom'] = vals['nom']
					data['prenom_benef'] = vals['prenom_benef']
					data['police_id'] = vals['police_id']
					vals['college_id'] = vals['college_id']
					data['college_id'] = vals['college_id']
					data['garant_id'] = vals['garant_id']
					data['statut_benef'] = vals['statut_benef']
					# data['lien_parente'] = vals['lien_parente']
					# data['avenant_id']=vals['avenant_id']
					data['souscripteur_id'] = vals['souscripteur_id']
					data['matric_benef'] = new_matricule_benef
					data['new_matricule_benef'] = new_matricule_benef
					data['dt_eff_mod_benef'] = time.strftime("%Y-%m-%d", time.localtime())
					data['police_id'] = vals['police_id']
					data['lbc_souscr_id'] = lapolice['souscripteur_id']
					# data['id_tran_age']=None
					data['sal_brut_benef'] = 0
					data['dt_entree_benef'] = time.strftime("%Y-%m-%d", time.localtime())
					data['st_creat_incorpo'] = vals['creat_incorpo']
					data['st_retr_excl'] = 'A'
					data['dt_sortie_benef'] = '01-01-1900 00:00:00'
					data['bl_excl_definitive'] = 2
					data['college_id'] = vals['college_id']
					data['bl_remb_autorise'] = 1
					data['st_ace_benef'] = 'A'
					data['ass_matric_benef'] = new_matricule_benef
					data['tmp_stamp'] = time.strftime("%Y-%m-%d", time.localtime())
					data['num_ave'] = 1
					data['pc_sal_prime'] = 0
					data['bl_pc_sal_prime'] = 0
					data['num_ave_cal'] = 0
					data['dt_naiss_benef'] = vals['dt_naiss_benef']
					data['num_ave_pol'] = 1
					data['statut'] = 'A'
					data['creat_incorpo'] = vals['creat_incorpo']
					data['histo_st_eleve'] = 0
					data['cod_statut_benef'] = 'C'
					# data['matric_chez_souscr'] = vals['matric_chez_souscr']
					data['activation'] = 0

					# data['id_tran_age']=0

					data['mode_prime'] = 0
					data['valide_quittance'] = 0
					data['date_quittance'] = '01-01-1900 00:00:00'
					data['cod_util_quittance'] = uid
					re = super(mcisogem_histo_benef, mcisogem_histo_benef).create(obj_histo_benef, cr, uid, data,
																				  context)
					return res

			else:
				raise osv.except_osv('Attention !', "Cette police n'a pas été associée à un exercice de police !")
				return False


class mcisogem_sexe(osv.osv):
	_name = "mcisogem.sexe"
	_description = 'sexe'

	_columns = {

		'name': fields.char('Libellé'),
		'code': fields.char('code')
	}


class mcisogem_benef_college_temp(osv.osv):
	_name = "mcisogem.benef.college.temp"
	_description = 'College temporare'

	_columns = {

		'name': fields.many2one('mcisogem.college', 'name', 'College'),

	}


class mcisogem_typeavenant_temp(osv.osv):
	_name = "mcisogem.typeavenant.temp"
	_description = 'type avenant temporaire'

	_columns = {

		'name': fields.many2one('mcisogem.type.avenant', 'name', 'Type avenant'),

	}


class mcisogem_histo_benef(osv.osv):
	_name = "mcisogem.histo.benef"
	_description = 'historique de beneficiaire'
	LIEN = [('E', 'Enfant'), ('C', 'Conjoint')]

	MOTIF = [
		('0', 'Le bénéficiaire n\'a pas été suspendu'),
		('1', 'Suspension Tier payant'),
		('2', 'Suspension totale'),
		('3', 'Décès')
	]

	SEXE = [
		('M', 'Masculin'),
		('F', 'Feminin')
	]

	def _get_matric(self, cr, uid, context):
		if context.get('action') == 'sus':
			return context.get('ass_matric_benef')
		else:
			return 0

	def _get_nom(self, cr, uid, context):
		return context.get('nom')

	def _get_prenom(self, cr, uid, context):
		return context.get('prenom')

	def _get_garant(self, cr, uid, context):
		if context.get('garant'):
			return context.get('garant')
		else:
			return False

	def _get_police(self, cr, uid, context):
		if context.get('police'):
			return context.get('police')
		else:
			return False

	def _get_num_police(self, cr, uid, context):
		return context.get('num_interne_police')

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

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

	def get_assure_principal(self, cr, uid, context=None):
		return context.get('ass_matric_benef')

	_columns = {
		'police_id': fields.many2one('mcisogem.police', "Police"),
		'garant_id': fields.many2one('mcisogem.garant', "Garant"),
		'avoir_ss_id': fields.boolean('A un numéro de sécurité sociale ?'),

		'assur_princ': fields.boolean('Assuré Principal ?'),
		'histo_benef_id': fields.many2one('mcisogem.histo.benef', 'Assuré Principal'),
		'statut_benef': fields.many2one('mcisogem.stat.benef', 'Statut de Bénéficiare'),
		'ss_id': fields.char('N° Sécurité sociale'),
		'avenant_id': fields.many2one('mcisogem.avenant', "Type Avenant"),
		'college_id': fields.many2one('mcisogem.college', 'College'),
		'name': fields.char('Name'),
		'nom': fields.char('Nom'),
		'prenom_benef': fields.char('prenom'),
		'souscripteur_id': fields.many2one('mcisogem.souscripteur', 'Souscripteur'),
		'dt_naiss_benef': fields.date('Date de Naissance'),
		'matric_benef': fields.char('matricule'),
		'new_matric_benef': fields.char('Matricule', readonly=True),
		'dt_eff_mod_benef': fields.datetime('date effet', required=True),

		'lbc_souscr_id': fields.many2one('mcisogem.souscripteur', "Souscripteur"),
		'lbc_crit_stat': fields.char('Nom'),
		'zone_geo_id': fields.many2one('mcisogem.zone', 'Zone géographique'),
		'code_ville': fields.many2one('mcisogem.ville', "ville"),
		'sexe': fields.selection(SEXE, 'Genre'),
		'sal_brut_benef': fields.integer('Salaire brut'),
		'dt_entree_benef': fields.datetime('Date de traitement', required=True),
		'st_creat_incorpo': fields.char('st_creat_incorpo'),
		'st_retr_excl': fields.char('st_retr_excl'),
		'dt_sortie_benef': fields.datetime('Date de Sortie'),
		'bl_excl_definitive': fields.integer('bl_excl_definitive'),
		'bl_remb_autorise': fields.integer('bl_remb_autorise'),
		'st_ace_benef': fields.char('Statut du bénéficiaire'),
		'ass_matric_benef': fields.char('Assuré Principal', readonly=True),
		'tmp_stamp': fields.datetime('tmp_stamp'),
		'num_ave': fields.integer('num_ave'),
		'pc_sal_prime': fields.integer('pc_sal_prime'),
		'bl_pc_sal_prime': fields.integer('bl_pc_sal_prime'),
		'num_ave_cal': fields.integer('num_ave_cal'),
		'num_ave_pol': fields.integer('num_ave_pol'),
		'num_ave_ret': fields.integer('num_ave_ret'),
		'histo_st_eleve': fields.boolean('Statut Eleve'),
		'cod_statut_benef': fields.char('Statut beneficiaire', readonly=True),
		'matric_chez_souscr': fields.char('matric_chez_souscr'),
		'activation': fields.boolean('activation'),
		'photo_ben_fam': fields.char('photo ben fam'),
		'id_tran_age': fields.many2one('mcisogem.tranche.age', 'Tranche \'age'),
		'cod_gesti': fields.integer('cod_gesti'),
		'mode_prime': fields.integer('Mode prime'),
		'valide_quittance': fields.integer('valide_quittance'),
		'date_quittance': fields.datetime('Date quittance'),
		'motif_suspension': fields.selection(MOTIF, 'Motif de suspension', select=True),
		'cod_util_quittance': fields.char('cod_util_quittance'),
		'statut': fields.selection([('A', 'Actif'), ('S', 'Suspendu')], 'Etat du Bénéficiare'),
		'chargement': fields.integer(''),
		'lien_parente': fields.selection(LIEN, 'Lien de Parenté'),
		'creat_incorpo': fields.selection([('C', 'creation'), ('I', 'Incorporation')], 'Statut'),

		'image': fields.binary("Image",
							   help="This field holds the image used as image for the product, limited to 1024x1024px."),

		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
										string="Medium-sized image", type="binary", multi="_get_image",
										store={
											'mcisogem.histo.benef': (
											lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
										},
										help="Medium-sized image of the product. It is automatically " \
											 "resized as a 128x128px image, with aspect ratio preserved, " \
											 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
									   string="Small-sized image", type="binary", multi="_get_image",
									   store={
										   'mcisogem.histo.benef': (
										   lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
									   },
									   help="Small-sized image of the product. It is automatically " \
											"resized as a 64x64px image, with aspect ratio preserved. " \
											"Use this field anywhere a small image is required."),

		'nom_assur_princ': fields.char('Nom ', readonly=True),
		'prenom_assur_princ': fields.char('Prenom ', readonly=True),
		'num_interne_police': fields.integer('N° Police', readonly=True),
	}

	_defaults = {
		'chargement': 1,
		'num_interne_police': _get_num_police,
		'nom': _get_nom,
		'nom_assur_princ': _get_nom,
		'prenom_assur_princ': _get_prenom,
		'avoir_ss_id': _get_regime_centre,
		'motif_suspension': '0',
		'ass_matric_benef': get_assure_principal,
		'creat_incorpo': 'C',
		'matric_benef': _get_matric,
		'prenom_benef': _get_prenom
	}

	_sql_constraints = [('unique_beneficiaire_ssid',
						 'unique(ss_id)',
						 "Ce numéro de sécurité sociale existe déjà !"), ]


	# valider la suspension
	def button_valider(self, cr, uid, ids, context):
		print('success*****************')

	def create(self, cr, uid, data, context=None):
		vals = {}
		if context.get('action') == 'sus':

			data['statut'] = 'S'
			benef = self.pool.get('mcisogem.benef').search(cr, uid,
														   [('matric_benef', '=', context.get('matric_benef'))])

			for bnf in self.pool.get('mcisogem.benef').browse(cr, uid, benef):
				the_id = self.pool.get('mcisogem.benef').write(cr, uid, context.get('ids')[0], {'statut': 'S',
																								'motif_suspension': context.get(
																									'motif_suspension')},
															   context)

			return 1

		elif context.get('action') == 'histo':

			data['avoir_ss_id'] = False

			matricule = context.get('ass_matric_benef')  # matricule de l'assure principal
			benef = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_benef', '=', matricule)])
			b_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef)

			data['st_creat_incorpo'] = data['creat_incorpo']
			data['st_retr_exclu'] = 'A'
			data['police_id'] = b_data.police_id['id']
			data['college_id'] = b_data.college_id['id']
			data['garant_id'] = b_data.garant_id['id']
			data['avenant_id'] = b_data.avenant_id['id']
			data['souscripteur_id'] = b_data.souscripteur_id['id']
			data['st_ace_benef'] = data['lien_parente']
			data['statut'] = 'A'
			data['cod_statut_benef'] = 'A'
			data['valide_quittance'] = 0

			centre = self.pool.get('mcisogem.centre.gestion').search(cr, uid, [('id', '=', 1)])
			centre_data = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, centre)

			new_matricule_benef = ''
			centre_gest = centre_data.lettre_cle
			code_pays = centre_data.pays_id.code_pays
			new_matricule_benef = new_matricule_benef + '' + str(code_pays) + str(centre_gest)

			if data['sexe'] == 'M':
				if data['lien_parente'] == 'C':
					new_matricule_benef = new_matricule_benef + '0'
				else:
					new_matricule_benef = new_matricule_benef + '2'

			else:
				if data['lien_parente'] == 'C':
					new_matricule_benef = new_matricule_benef + '1'
				else:
					new_matricule_benef = new_matricule_benef + '3'

			res = super(mcisogem_histo_benef, self).create(cr, uid, data, context)

			cr.execute('select id from mcisogem_histo_benef order by id DESC limit 1')

			last_id = cr.fetchone()[0]

			mat = str(last_id)
			for i in range(10):
				if len(mat) < 9:
					mat = '0' + mat

			new_matricule_benef = new_matricule_benef + mat
			if self._get_regime_centre(cr, uid):
				if not data['ss_id']:
					raise osv.except_osv('Attention !', " Vous n'avez pas renseigné  le N° de sécurité sociale !")
				else:
					data['name'] = vals['ss_id']
					data['avoir_ss_id'] = True
			else:
				data['name'] = new_matricule_benef

			super(mcisogem_histo_benef, self).write(cr, uid, res,
													{'new_matric_benef': new_matricule_benef, 'name': data['name'],
													 'avoir_ss_id': data['avoir_ss_id']}, context=context)
			return res


class mcisogem_histo_retrait_masse(osv.osv):
	_name = "mcisogem.histo.retrait.masse"
	_description = "Historique des retraits en masse"

	_columns = {
		'garant_id': fields.many2one('mcisogem.garant', 'Garant'),
		'police_id': fields.many2one('mcisogem.police', 'Police'),
		'benef_ids': fields.many2many('mcisogem.benef', 'mcisogem_retrait_masse_rel', 'id_h', 'id_b', 'Bénéficiaires',
									  required=True),
		'date_retrait': fields.datetime('Date de retrait', help="date d'effet du retrait" , required="true"),
	}

	_rec_name = "police_id"

	def onchange_police(self, cr, uid, ids, police_id, context=None):

		d = {}
		les_benefs = []

		les_bnef_ids = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
			('police_id', '=', police_id)])

		for bnef in self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid, les_bnef_ids):
			les_benefs.append(bnef.beneficiaire_id.id)

		les_bnef_ids = self.pool.get('mcisogem.benef').search(cr, uid, [('police_id', '=', police_id)])

		for bnef in self.pool.get('mcisogem.benef').browse(cr, uid, les_bnef_ids):
			les_benefs.append(bnef.id)

		print('****------****')
		print(les_benefs)
		
		d = {'benef_ids': [('id', 'in', les_benefs)]}

		return {'domain': d}

	def create(self, cr, uid, data, context=None):
		benficiaires = data['benef_ids']

		for histo_benef_id in benficiaires[0][2]:
			histo_benef = self.pool.get('mcisogem.benef').search(cr, uid, [('id', '=', histo_benef_id)])

			histo_benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, histo_benef)

			self.pool.get('mcisogem.benef').write(cr, uid, histo_benef_id, {'statut': 'R'}, context)

			self.pool.get('mcisogem.histo.retrait').create(cr, uid,
														   {'benef_id': histo_benef_id,
															'dt_action':data['date_retrait'],
															'statut': True,
															'action': 'Retrait'})

		return super(mcisogem_histo_retrait_masse, self).create(cr, uid, data, context)


class mcisogem_histo_suspension(osv.osv):
	_name = "mcisogem.histo.suspension"
	_description = "Historique des suspensions"

	_columns = {
		'benef_id': fields.many2one('mcisogem.benef', 'Bénéficiaire', required=True),
		'dt_action': fields.datetime('Date', required=True),
		'motif_suspension': fields.many2one('mcisogem.motif.suspen.benef', 'Motif de suspension'),
		'statut': fields.boolean('Statut'),
		'action': fields.char('Action'),
	}

	_rec_name = "benef_id"


class mcisogem_histo_retrait(osv.osv):
	_name = "mcisogem.histo.retrait"
	_description = "Historique des retraits"

	_columns = {
		'benef_id': fields.many2one('mcisogem.benef', 'Bénéficiaire', required=True),
		'dt_action': fields.datetime('Date', required=True),
		'statut': fields.boolean('Statut'),
		'action': fields.char('Action'),
	}

	_rec_name = "benef_id"
