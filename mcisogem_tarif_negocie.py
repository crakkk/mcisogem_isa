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


class mcisogem_reseau(osv.osv):
	_name = "mcisogem.reseau"
	_description = 'Libelle Reseau'
	_columns = {
		'name': fields.char('Réseau' , required=True),
	}

# class mcisogem_reseau_soins(osv.osv):
# 	_name = "mcisogem.reseau.soins"
# 	_description = 'Reseau de soins'
# 	_columns = {
# 		'reseau_id': fields.many2one('mcisogem.reseau' , 'Réseau' ,  required=True),
# 		'centre_ids':fields.many2many('mcisogem.stat.benef','mcisogem_stat_benef_produit_rel','id' , 'produit_id' , 'Statuts' ,  required=True),
# 	}




class mcisogem_tarif_nego_police(osv.osv):
	_name  = "mcisogem.tarif.nego.police"
	_description = "Reseau de soins"

	_columns= {

		'reseau_id':fields.many2one('mcisogem.reseau' , 'Réseau' , required=True),

		
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		

		'convention_id': fields.many2one('mcisogem.convention.unique', 'Convention'),
		
		'dt_effet_tarif' : fields.date('Date d\'effet'),
		'dt_res_tarif' : fields.date('Date de résiliation'),
		'name' : fields.char(''),
		'state' : fields.selection([('N', 'Actif'), ('A', 'Résilié')] , 'Statut'),


		'code_centre_temp': fields.many2many('mcisogem.tarif.nego.centre.temp',
										'mcisogem_tarif_centre_rel',
										'tarif_centre_id',
										'id',
										'Choix des centres', required=True),


		'centre_ids': fields.many2many('mcisogem.centre',
										'mcisogem_tarif_police_rel',
										'tarif_police_temp_id',
										'id',
										'Centres', required=True),

		'pharma_ids': fields.many2many('mcisogem.centre',
										'mcisogem_pharma_rel',
										'pharma_id',
										'id',
										'Pharmacies', required=True),


		'chargement' : fields.integer(),
	}


	#METRE ça dans le default
	# chargement des tables temporaires centre , acte
	def onchange_chargement(self, cr, uid, context=None):
		
		cr.execute("delete from mcisogem_tarif_nego_centre_temp where write_uid=%s", (uid,))
	   
		sql = "SELECT mcisogem_centre.id as centre_id, mcisogem_centre.name as centre, mcisogem_convention_unique.libelle as convention , mcisogem_convention_unique.id as convention_id FROM mcisogem_centre, mcisogem_centre_rel, mcisogem_rata_convention , mcisogem_convention_unique WHERE mcisogem_centre_rel.code_centre = mcisogem_centre.id AND mcisogem_centre_rel.mcisogem_centre_rel_id = mcisogem_rata_convention.id AND mcisogem_rata_convention.convention_id = mcisogem_convention_unique.id"
		

		cr.execute(sql)

		centres = cr.dictfetchall()

		pharma = self.pool.get('mcisogem.type.centre').search(cr,uid,[('code_type_centre2' , '=' , 'P')])
		pharmas = self.pool.get('mcisogem.centre').search(cr,uid,[('code_type_centre' , '=' , pharma)])

		if len(centres) > 0:
			for centre in centres:
				if centre['centre_id'] not in pharmas:
					cr.execute("insert into mcisogem_tarif_nego_centre_temp(create_uid,create_date,centre_id,centre, write_uid , convention_id , convention) values(%s,%s, %s , %s , %s , %s , %s)",(uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),centre['centre_id'],centre['centre'], uid , centre['convention_id'] , centre['convention']))


		cr.execute('select * from mcisogem_tarif_nego_centre_temp where create_uid=%s' , (uid , ))
		centres = cr.dictfetchall()

		

		if pharma:
			pharma = pharma[0]

		

		return{'domain': {'pharma_ids': [('id' , 'in' , pharmas)]}}


	_defaults = {
		'dt_effet_tarif' : time.strftime('%Y-%m-%d', time.localtime()),
		# 'code_centre_temp' : onchange_chargement,
	}

	

	_sql_constraints = [('unique_reseau', 'unique(centre_id,police_id,college_id,state,convention_id)', "Ce réseau existe déjà !"), ] 
	

			

	def details_police(self,cr,uid, police_id):
		# cette fonction retourne les détails sur une police  donnée
		police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
		police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)
		return police_data


	def details_centre(self,cr,uid, centre_id):
		# cette fonction retourne les détails sur un centre donné 
		centre =  self.pool.get('mcisogem.centre').search(cr,uid,[('id','=',centre_id)])
		centre_data = self.pool.get('mcisogem.centre').browse(cr,uid,centre)
		return centre_data

	
	def details_acte(self,cr,uid, acte_id):
		# cette fonction retourne les détails sur un ac1te donné 
		acte =  self.pool.get('mcisogem.nomen.prest').search(cr,uid,[('id','=',acte_id)])
		acte_data = self.pool.get('mcisogem.nomen.prest').browse(cr,uid,acte)
		return acte_data


	def check_etat_police(self,cr,uid, police_id):
		# cette fonction retourne l'état de la police qu'on lui passe en paramètre 
		police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
		result = self.pool.get('mcisogem.police').search_count(cr,uid,[('id','=',police_id)])
		if result > 0:

			police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)
			return police_data.state
		else:
			return False

	def button_action_resilier(self, cr, uid, ids, context=None):
	   
		# ouvre le formulaire de resiliation d'une négociation de tarif
		tarif = self.browse(cr, uid, ids[0], context=context).id

		tarif_table = self.search(cr, uid, [('id', '=', tarif)])
		tarif_data = self.browse(cr,uid,tarif_table)

		ctx = (context or {}).copy()

		ctx['id_tar'] = ids[0]
		ctx['ids'] = tarif_data.ids
		ctx['form_view_ref'] = 'mcisogem_tarif_annul_nego_police_form'

		return {
		  'name':'Résiliation du tarif négocié',
		  'view_type':'form',
		  'view_mode':'form',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		  'res_model':'mcisogem.tarif.nego.police',
		}

	def create(self, cr, uid, data, context=None):
		last_id = 0

		if data['dt_res_tarif']==False or data['dt_res_tarif']=='':

			centre = data['code_centre_temp']
			pharmas = data['pharma_ids'][0][2]
				
			data['state']  = 'N'
			data['dt_res_tarif']= None

		

			for ctr_id in centre[0][2]:
				ctr_idt = self.pool.get('mcisogem.tarif.nego.centre.temp').browse(cr,uid,ctr_id).centre_id.id

				data['centre_id'] = ctr_idt
				data['convention_id'] = self.pool.get('mcisogem.tarif.nego.centre.temp').browse(cr,uid,ctr_id).convention_id.id
				
				centre_name = self.pool.get('mcisogem.tarif.nego.centre.temp').browse(cr,uid,ctr_id).centre_id.name
				convention_name = self.pool.get('mcisogem.convention.unique').browse(cr,uid,data['convention_id']).libelle
				reseau_name = self.pool.get('mcisogem.reseau').browse(cr,uid,data['reseau_id']).name


				data['name'] = reseau_name + ' - ' + convention_name + ' - ' + centre_name

				if self.pool.get('mcisogem.tarif.nego.police').search_count(cr,uid,[('centre_id' , '=' , data['centre_id']) ,('convention_id' , '=' , data['convention_id'])]) > 0:

					raise osv.except_osv('Attention' , 'Cetains éléments que vous essayez de créer existent déjà !')

				last_id = super(mcisogem_tarif_nego_police , self).create(cr, uid, data, context=context)


			for ph in pharmas:
				data['centre_id'] = ph
				data['convention_id'] = None
				centre_name = self.pool.get('mcisogem.centre').browse(cr,uid,ph).name
				
				reseau_name = self.pool.get('mcisogem.reseau').browse(cr,uid,data['reseau_id']).name


				data['name'] = reseau_name + ' - ' + centre_name

				if self.pool.get('mcisogem.tarif.nego.police').search_count(cr,uid,[('centre_id' , '=' , data['centre_id']) ,('reseau_id' , '=' , data['reseau_id'])]) > 0:

					raise osv.except_osv('Attention' , 'Cetains éléments que vous essayez de créer existent déjà !')

				last_id = super(mcisogem_tarif_nego_police , self).create(cr, uid, data, context=context)

			return last_id   # return last_id
			
		else:
			ctx = (context or {}).copy()
			ctx['dt_res_tarif'] = data['dt_res_tarif']
			return context.get('ids')[0]



	def button_negocier(self,cr,uid,ids,context=None):
		return self.write(cr, uid, ids, {'state':'N', 'dt_res_tarif':False}, context=context)

	def button_resilier(self,cr,uid,ids,context=None):
		self.write(cr, uid, context.get('ids'), {'state':'A' , 'dt_res_tarif' : context.get('dt_res_tarif')}, context=context)
		return True

	

class mcisogem_tarif_college_temp(osv.osv):
	_name = "mcisogem.tarif.college.temp"
	_description = 'College'
	_columns = {
		'police_id': fields.many2one('mcisogem.police', "Police"),
		'code_college': fields.many2one('mcisogem.college' , 'Collège'),
}


class mcisogem_tarif_nego_centre_temp(osv.osv):
	_name = "mcisogem.tarif.nego.centre.temp"
	_description = 'Tarif Centre'
	_columns = {
		'centre_id': fields.many2one('mcisogem.centre', 'Centre'),
		'convention_id': fields.many2one('mcisogem.convention.unique', 'Convention'),
		'centre' : fields.char('Centre') , 
		'convention' : fields.char('Convention') , 
}


class mcisogem_rata_reseau_police(osv.osv):
	_name = "mcisogem.rata.reseau.police"

	_description = "Rattachement reseau de soins police"

	_columns = {
		'reseau_id' : fields.many2one('mcisogem.reseau' , 'Réseau' , required=True),
		'par_college' : fields.boolean('Par collège'),
		'college_ids' : fields.many2many('mcisogem.college' , 'mcisogem_college_reseau_rel' , 'rata_id' , 'col_id'),
		'police_ids' : fields.many2many('mcisogem.police' , 'mcisogem_police_reseau_rel' , 'rata_id' , 'pol_id'),
		'college_id' : fields.many2one('mcisogem.college' , 'Collège'),
		'police_id' : fields.many2one('mcisogem.police' , 'Police'),
		'name' : fields.char(''),
	}



	def onchange_police(self,cr,uid,ids,police_ids,context=None):

		if police_ids[0][2]:

			polices = police_ids[0][2]


			colleges = self.pool.get('mcisogem.college').search(cr,uid,[('police_id' , 'in' , polices)])

			d = {}
			d = {'college_ids' : [('id' , 'in' , colleges)]}


			return {'domain' : d}


	def create(self, cr, uid, data, context=None):
		last_id = False

		
		if data['par_college'] == True:

			if len(data['college_ids'][0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins un collège !')

			
			colleges = data['college_ids'][0][2]

			for col in colleges:

				reseau_name = self.pool.get('mcisogem.reseau').browse(cr,uid,data['reseau_id']).name

				college_data = self.pool.get('mcisogem.college').browse(cr,uid,col)

				data['college_id'] = col
				data['police_id'] = college_data.police_id.id
				data['name'] = reseau_name + ' - ' + college_data.police_id.name + ' - ' + college_data.name


				if self.pool.get('mcisogem.rata.reseau.police').search_count(cr,uid,[('college_id' , '=' , col)]) > 0:
					raise osv.except_osv('Attention' , "L'un des éléments que vous tentez de créer existe déjà !")

				last_id = super(mcisogem_rata_reseau_police , self).create(cr, uid, data, context=context)

		
		else:
			
			if len(data['police_ids'][0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins une police !')


			polices = data['police_ids'][0][2]


			for pol in polices:

				colleges = self.pool.get('mcisogem.college').search(cr,uid,[('police_id' , '=' , pol)])

				for col in colleges:

					college_data = self.pool.get('mcisogem.college').browse(cr,uid,col)


					reseau_name = self.pool.get('mcisogem.reseau').browse(cr,uid,data['reseau_id']).name

					data['college_id'] = col
					data['police_id'] = pol

					data['name'] = reseau_name + ' - ' + college_data.police_id.name + ' - ' + college_data.name

					if self.pool.get('mcisogem.rata.reseau.police').search_count(cr,uid,[('college_id' , '=' , col)]) > 0:

						raise osv.except_osv('Attention' , "L'un des éléments que vous tentez de créer existe déjà !")


					last_id = super(mcisogem_rata_reseau_police , self).create(cr, uid, data, context=context)





		return last_id   # return last_id
			
		


