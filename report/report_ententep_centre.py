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

class report_ententep_centre(osv.osv):
	_name = "report.ententep.centre"
	_description = "Graphes sur les ententes prealable par centre"
	_auto = False
   

	_columns = {
		
		# 'centre_id': fields.many2one('mcisogem.centre', 'Centre', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'nbr_attente': fields.integer('Attente', readonly=True),
		'nbr_valide': fields.integer('Valide', readonly=True),
		'nbr_rejete': fields.integer('Rejete', readonly=True),
		'nbr_total': fields.integer('Total', readonly=True),
		
		
	}
	
	_depends = {'mcisogem.police' : ['id','name'],'mcisogem.account.period' : ['id','name'], 'mcisogem.exercice' : ['id','name','date_debut','date_fin']}

	def _get_centre(self, cr,uid,context):
		
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]
		if centre_user_id:
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
			
			return centre.id
		else:
			return 0



	def init_server_centre(self, cr, uid, context):
		# raise osv.except_osv('Attention' ,'action serveur execute en premier!')
		centre_id = self._get_centre(cr,uid,context)
		print('*************execute action serveur************')
		print('*************centre report************')
		print(centre_id)

		
		cr.execute("select report_entente_centre(%s)", (centre_id,))
		# cr.execute("select report_entente_centre(3)")
		tools.drop_view_if_exists(cr, 'report_ententep_centre')
		cr.execute("""

				create or replace view report_ententep_centre as (
					SELECT 

				 	min(mcisogem_report_stat_ententep_centre.id) AS id, 
					mcisogem_report_stat_ententep_centre.exercice_id as exercice_id,
					mcisogem_report_stat_ententep_centre.periode_id as periode_id,
					mcisogem_report_stat_ententep_centre.police_id as police_id,
					mcisogem_report_stat_ententep_centre.nbr_attente as nbr_attente,
					mcisogem_report_stat_ententep_centre.nbr_valide as nbr_valide,
					mcisogem_report_stat_ententep_centre.nbr_rejete as nbr_rejete,
					mcisogem_report_stat_ententep_centre.nbr_total as nbr_total


    			FROM mcisogem_report_stat_ententep_centre

    			group by
					  exercice_id, police_id, periode_id, nbr_total, nbr_valide,  nbr_attente, nbr_rejete
				)""")

	
		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.ententep.centre.graph')], context=context)
		if view_ids:
			if centre_id:
				res = {
				'res_id': centre_id,
				'view_id': view_ids[0],
				'view_mode': 'graph',
				'view_type': 'form',
				'res_model': 'report.ententep.centre',
				'type': 'ir.actions.act_window',
				'context': context
				}
				print(res)
		else:
			print("TEST")
		return res


	def init(self, cr):
		cr.execute("select report_entente()")
		tools.drop_view_if_exists(cr, 'report_ententep_centre')
		cr.execute("""
			create or replace view report_ententep_centre as (
				 SELECT 

				 	min(mcisogem_report_stat_ententep.id) AS id,
					mcisogem_report_stat_ententep.exercice_id as exercice_id,
					mcisogem_report_stat_ententep.police_id as police_id,
					mcisogem_report_stat_ententep.nbr_attente as nbr_attente,
					mcisogem_report_stat_ententep.nbr_valide as nbr_valide,
					mcisogem_report_stat_ententep.nbr_rejete as nbr_rejete,
					mcisogem_report_stat_ententep.nbr_total as nbr_total


    			FROM mcisogem_report_stat_ententep

    			group by
					  exercice_id, police_id, nbr_total, nbr_valide,  nbr_attente, nbr_rejete

			)""")
	  


