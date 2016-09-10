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

class mcisogem_report_stat_retrait_garant(osv.osv):
	_name = "mcisogem.report.stat.retrait.garant"
	_description = "Graphes sur demande de retrait par garant"
	# _auto = False
   

	_columns = {
		
		'beneficiaire_id': fields.many2one('mcisogem.benef', ''),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'nbr_attente': fields.integer('Attente', readonly=True),
		'nbr_valide': fields.integer('Valide', readonly=True),
		'nbr_rejete': fields.integer('Rejete', readonly=True),
		'nbr_total': fields.integer('Total', readonly=True),
		
	}
	
	_depends = {'mcisogem.police' : ['id','name'], 'mcisogem.exercice' : ['id','name','date_debut','date_fin'],'mcisogem.benef' : ['id','name']}


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
		
	# 	tools.drop_view_if_exists(cr, 'report_retrait_garant')
	# 	cr.execute("""

	# 			create or replace view report_retrait_garant as (
	# 				select
	# 					min(mcisogem_retrait.id) AS id,
	# 				count(mcisogem_retrait.id) as nbr_total,  
	# 				mcisogem_retrait.beneficiaire_id as beneficiaire_id,
	# 				mcisogem_police.id as police_id,
	# 				mcisogem_exercice.id as exercice_id
					
	# 				from
	# 					public.mcisogem_retrait, public.mcisogem_benef , public.mcisogem_police,  public.mcisogem_exercice	
	# 				where
	# 					mcisogem_retrait.garant_id = %s and mcisogem_retrait.beneficiaire_id = mcisogem_benef.id and mcisogem_benef.police_id = mcisogem_police.id and mcisogem_exercice.id = mcisogem_police.exercice_id
	# 				group by
	# 					mcisogem_retrait.garant_id,  mcisogem_police.id, mcisogem_retrait.beneficiaire_id, mcisogem_exercice.id
	# 			)""", (garant_id,))

	
	# 	res = {}
	# 	view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.retrait.garant.graph')], context=context)
	# 	if view_ids:
	# 		if garant_id:
	# 			res = {
	# 			'res_id': garant_id,
	# 			'view_id': view_ids[0],
	# 			'view_mode': 'graph',
	# 			'view_type': 'form',
	# 			'res_model': 'report.retrait.garant',
	# 			'type': 'ir.actions.act_window',
	# 			'context': context
	# 			}
	# 			print(res)
	# 	else:
	# 		print("TEST")
	# 	return res


	# def init(self, cr):
	# 	tools.drop_view_if_exists(cr, 'report_retrait_garant')
	# 	cr.execute("""
	# 		create or replace view report_retrait_garant as (
	# 			select
	# 				min(mcisogem_retrait.id) AS id,
	# 				count(mcisogem_retrait.id) as nbr_total,  
	# 				mcisogem_retrait.garant as garant_id,
	# 				mcisogem_retrait.beneficiaire_id as beneficiaire_id,
	# 				mcisogem_police.id as police_id,
	# 				mcisogem_exercice.id as exercice_id
					

	# 			from
	# 			  public.mcisogem_retrait, public.mcisogem_garant, public.mcisogem_police,  public.mcisogem_exercice , public.mcisogem_benef
	# 			where
	# 				mcisogem_retrait.garant = mcisogem_garant.id and mcisogem_retrait.beneficiaire_id = mcisogem_benef.id and mcisogem_benef.police_id = mcisogem_police.id and mcisogem_exercice.id = mcisogem_police.exercice_id
	# 			group by
	# 				mcisogem_retrait.garant,  mcisogem_police.id, mcisogem_exercice.id, mcisogem_retrait.beneficiaire_id 
 
			 
	# 		)""")
	  


