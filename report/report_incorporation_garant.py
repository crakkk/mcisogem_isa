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

class report_incorporation_garant(osv.osv):
	_name = "report.incorporation.garant"
	_description = "Graphes sur demande d'incorporation"
	_auto = False
   

	_columns = {
		
		# 'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'nbr_attente': fields.integer('En attente', readonly=True),
		'nbr_valide': fields.integer('Valide', readonly=True),
		'nbr_rejete': fields.integer('Rejete', readonly=True),
		'nbr_total': fields.integer('Total', readonly=True),
		
	}
	
	_depends = {'mcisogem.police' : ['id','name'] ,'mcisogem.account.period' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin']}

	def _get_garant(self, cr,uid,context):
		
		cr.execute('select garant_id from res_users where id=%s', (uid,))
		garant_user_id = cr.fetchone()[0]
		if garant_user_id:
			garant = self.pool.get('mcisogem.garant').browse(cr, uid, garant_user_id, context=context)
			
			return garant.id
		else:
			return 0


	def init_server(self, cr, uid, context):
		# raise osv.except_osv('Attention' ,'action serveur execute en premier!')
		garant_id = self._get_garant(cr,uid,context)
		print('*************execute action serveur************')
		print('*************garant report************')
		print(garant_id)
		
		cr.execute("select report_incoporation_garant(%s)", (garant_id,))

		tools.drop_view_if_exists(cr, 'report_incorporation_garant')
		cr.execute("""

				create or replace view report_incorporation_garant as (
					SELECT 

				 	min(mcisogem_report_stat_incorporation_garant.id) AS id, 
					mcisogem_report_stat_incorporation_garant.exercice_id as exercice_id,
					mcisogem_report_stat_incorporation_garant.police_id as police_id,
					mcisogem_report_stat_incorporation_garant.periode_id as periode_id,
					mcisogem_report_stat_incorporation_garant.nbr_attente as nbr_attente,
					mcisogem_report_stat_incorporation_garant.nbr_valide as nbr_valide,
					mcisogem_report_stat_incorporation_garant.nbr_rejete as nbr_rejete,
					mcisogem_report_stat_incorporation_garant.nbr_total as nbr_total


    			FROM mcisogem_report_stat_incorporation_garant

    			group by
					  exercice_id, police_id,periode_id, nbr_total, nbr_valide,  nbr_attente, nbr_rejete
					
				)""")

	
		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.incorporation.garant.graph')], context=context)
		if view_ids:
			if garant_id:
				res = {
				'res_id': garant_id,
				'view_id': view_ids[0],
				'view_mode': 'graph',
				'view_type': 'form',
				'res_model': 'report.incorporation.garant',
				'type': 'ir.actions.act_window',
				'context': context
				}
				print(res)
		else:
			print("TEST")
		return res






	def init(self, cr):
		tools.drop_view_if_exists(cr, 'report_incorporation_garant')
		cr.execute("""
			create or replace view report_incorporation_garant as (
				select
					min(mcisogem_benf_incorpo.id) AS id,
					count(mcisogem_benf_incorpo.id) as nbr_total,  
					mcisogem_benf_incorpo.garant_id as garant_id,
					mcisogem_benf_incorpo.police_id as police_id,
					mcisogem_exercice.id as exercice_id
					

				from
				  public.mcisogem_benf_incorpo, public.mcisogem_garant, public.mcisogem_police,  public.mcisogem_exercice 
				where
					mcisogem_benf_incorpo.garant_id = mcisogem_garant.id and mcisogem_benf_incorpo.police_id = mcisogem_police.id and mcisogem_exercice.id = mcisogem_police.exercice_id
				group by
					mcisogem_benf_incorpo.garant_id,  mcisogem_benf_incorpo.police_id, mcisogem_exercice.id

 
			 
			)""")
	  


	  


