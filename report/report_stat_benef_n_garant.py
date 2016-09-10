# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import fields, osv

class mcisogem_report_stat_benef_n_garant(osv.osv):
	_name = "mcisogem.report.stat.benef.n.garant"
	_description = "Graphes sur les Bénéficiaires pour les garants"
	# _auto = False
   

	_columns = {
		
		# 'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'nbr_benef_inc': fields.integer('Incorporés', readonly=True),
		'nbr_benef_ret': fields.integer('Rétirés', readonly=True),
		'nbr_benef_suspend': fields.integer('Suspendu', readonly=True),
		'nbr_benef_total': fields.integer('Total', readonly=True)
		
	}
	
	_depends = {'mcisogem.police' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'] }

	# def _get_garant(self, cr,uid,context):
		
	# 	cr.execute('select garant_id from res_users where id=%s', (uid,))
	# 	garant_user_id = cr.fetchone()[0]
	# 	if garant_user_id:
	# 		garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			
	# 		return garant.id
	# 	else:
	# 		return 0



	# def init_server(self, cr, uid, context):
	# 	# raise osv.except_osv('Attention' ,'action serveur execute en premier!')
	# 	garant_id = self._get_garant(cr,uid,context)
	# 	print('*************execute action serveur************')
	# 	print('*************garant report************')
	# 	print(garant_id)
		
	# 	tools.drop_view_if_exists(cr, 'report_benef_n_garant')
	# 	cr.execute("""

	# 			create or replace view report_benef_n_garant as (
	# 				select
	# 					min(mcisogem_benef.id) AS id,
	# 					count(mcisogem_benef.id) as nbr_benef_total,  
	# 					mcisogem_benef.souscripteur_id as souscripteur_id,
	# 					mcisogem_police.exercice_id as exercice_id,
	# 					mcisogem_benef.police_id as police_id

	# 				from
	# 				  public.mcisogem_souscripteur, public.mcisogem_police, public.mcisogem_benef,  public.mcisogem_exercice 
	# 				where
	# 					mcisogem_benef.garant_id = %s and mcisogem_benef.souscripteur_id = mcisogem_souscripteur.id and  mcisogem_benef.police_id = mcisogem_police.id  and mcisogem_exercice.id = mcisogem_police.exercice_id
	# 				group by
	# 					mcisogem_benef.garant_id, mcisogem_benef.souscripteur_id, mcisogem_benef.police_id, mcisogem_police.exercice_id  
	# 			)""", (garant_id,))

	
	# 	res = {}
	# 	view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.benef.n.garant.graph')], context=context)
	# 	if view_ids:
	# 		if garant_id:
	# 			res = {
	# 			'res_id': garant_id,
	# 			'view_id': view_ids[0],
	# 			'view_mode': 'graph',
	# 			'view_type': 'form',
	# 			'res_model': 'report.benef.n.garant',
	# 			'type': 'ir.actions.act_window',
	# 			'context': context
	# 			}
	# 			print(res)
	# 	else:
	# 		print("TEST")
	# 	return res





	# def init(self, cr):
	# 	# raise osv.except_osv('Attention' ,'action init execute en premier!')
	# 	print('*************execute init************')
	# 	tools.drop_view_if_exists(cr, 'report_benef_n_garant')
	# 	cr.execute("""
	# 		create or replace view report_benef_n_garant as (
	# 			select
	# min(mcisogem_benef.id) AS id,
	# 				count(mcisogem_benef.id) as nbr_benef_total,  
	# 				mcisogem_benef.garant_id as garant_id,
	# 				mcisogem_benef.souscripteur_id as souscripteur_id,
	# 				mcisogem_police.exercice_id as exercice_id,
	# 				mcisogem_benef.police_id as police_id

	# 			from
	# 			  public.mcisogem_garant, public.mcisogem_souscripteur, public.mcisogem_police, public.mcisogem_benef,  public.mcisogem_exercice 
	# 			where
	# 				mcisogem_benef.garant_id = mcisogem_garant.id and mcisogem_benef.souscripteur_id = mcisogem_souscripteur.id and  mcisogem_benef.police_id = mcisogem_police.id  and mcisogem_exercice.id = mcisogem_police.exercice_id
	# 			group by
	# 				mcisogem_benef.garant_id, mcisogem_benef.souscripteur_id, mcisogem_police.exercice_id, mcisogem_benef.police_id 
	# 		)""")
	  


