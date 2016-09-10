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



class mcisogem_histo_renouv_police(osv.osv):
	_name = "mcisogem.histo.renouv.police"
	_description="Historique de renouvelement de police"

	_columns ={
		'garant_id' : fields.many2one('mcisogem.garant' , 'Garant' , required=True),
		'police_ids': fields.many2many('mcisogem.police','mcisogem_histo_renouv_police_rel','num_interne_police','id','Polices', required=True),
	   	'date_debut' : fields.date('Date de début d\'exercice' , required=True),
	   	'date_fin' : fields.date('Date de fin  d\'exercice' , required=True),
	}

	_rec_name = "garant_id"
	

	def create(self, cr, uid, data , context=None):
		pol_ids = data['police_ids'] 
		
		for pol_id in pol_ids[0][2]:

			# je recupere tous les exercices de cette police

			exercice_ids = self.pool.get('mcisogem.exercice.police').search(cr,uid,[('police_id', '=' , pol_id)])

			for exercice_id in exercice_ids:

				# initialisation de l objet  exercice.police

				obj_exercice_police = self.pool.get('mcisogem.exercice.police')

				exercice = self.pool.get('mcisogem.exercice.police').search(cr,uid,[('id','=',exercice_id)])
				exercice_data = self.pool.get('mcisogem.exercice.police').browse(cr,uid,exercice)

				vals={}
				vals['date_debut_exercice'] = data['date_debut']
				vals['date_fin_exercice'] = data['date_fin']
				vals['num_interne_police'] = exercice_data['num_interne_police']
				vals['bl_exercice_clot'] = False
				vals['police_id'] = exercice_data['police_id']['id']
				vals['name'] = exercice_data['name']
				vals['exercice_id'] = exercice_data['exercice_id']['id']
				vals['prime_pol_exercice'] = exercice_data['prime_pol_exercice']
				vals['dernier_avenant'] = exercice_data['dernier_avenant']
				vals['cum_mnt_pol'] = exercice_data['cum_mnt_pol']
				vals['typ_prime'] = exercice_data['typ_prime']
				vals['masse_sal_pol'] = exercice_data['masse_sal_pol']
				vals['pc_masse_sal_pol'] = exercice_data['pc_masse_sal_pol']
				vals['bl_pc_masse_sal_pol'] = exercice_data['bl_pc_masse_sal_pol']
				vals['periodicite_paiem_pol'] = exercice_data['periodicite_paiem_pol']
				vals['rapport_sp_preced'] = exercice_data['rapport_sp_preced']
				vals['tot_sinistre_preced'] = exercice_data['tot_sinistre_preced']
				vals['tot_prime_preced'] = exercice_data['tot_prime_preced']
				vals['cod_sup'] = exercice_data['cod_sup']
				vals['repartition_prime'] = exercice_data['repartition_prime']
				vals['tva_oui_non'] = exercice_data['tva_oui_non']
				vals['imputation_accessoires'] = exercice_data['imputation_accessoires']
				vals['imputation_acc_cie'] = exercice_data['imputation_acc_cie']
				vals['imputation_acc_courtier'] = exercice_data['imputation_acc_courtier']
				vals['type_prime'] = exercice_data['type_prime']
				vals['ident_centre'] = exercice_data['ident_centre']
				vals['code_gest'] = exercice_data['code_gest']
				vals['code_langue'] = exercice_data['code_langue']

				cr.execute("insert into mcisogem_exercice_police(date_debut_exercice,date_fin_exercice,num_interne_police,bl_exercice_clot,police_id,name,exercice_id,prime_pol_exercice,dernier_avenant,cum_mnt_pol,typ_prime,masse_sal_pol,pc_masse_sal_pol,bl_pc_masse_sal_pol,periodicite_paiem_pol,rapport_sp_preced,tot_sinistre_preced,tot_prime_preced,cod_sup,repartition_prime,tva_oui_non,imputation_accessoires,imputation_acc_cie,imputation_acc_courtier,type_prime,ident_centre,code_gest,code_langue) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(vals['date_debut_exercice'],vals['date_fin_exercice'],vals['num_interne_police'],False,vals['police_id'],vals['name'],vals['exercice_id'],vals['prime_pol_exercice'],vals['dernier_avenant'],vals['cum_mnt_pol'],vals['typ_prime'],vals['masse_sal_pol'],vals['pc_masse_sal_pol'],vals['bl_pc_masse_sal_pol'],vals['periodicite_paiem_pol'],vals['rapport_sp_preced'],vals['tot_sinistre_preced'],vals['tot_prime_preced'],vals['cod_sup'],vals['repartition_prime'],vals['tva_oui_non'],vals['imputation_accessoires'],vals['imputation_acc_cie'],vals['imputation_acc_courtier'],vals['type_prime'],vals['ident_centre'],vals['code_gest'],vals['code_langue']))

		return super(mcisogem_histo_renouv_police , self).create(cr,uid,data,context)