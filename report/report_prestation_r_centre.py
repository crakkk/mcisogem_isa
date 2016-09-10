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

class report_prestation_r_centre(osv.osv):
	_name = "report.prestation.r.centre"
	_description = "Graphes sur les prestation reglees par centre"
	_auto = False
   

	_columns = {
		
		'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'beneficiaire_id': fields.many2one('mcisogem.benef','Bénéficiaires', readonly=True),
		'nbr_total': fields.integer('Prestations', readonly=True),
		'montant_remb': fields.integer('Montant Remboursé', readonly=True),
		
	}
	
	_depends = {'mcisogem.garant' : ['id','name'] ,'mcisogem.police' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'],'mcisogem.benef' : ['id','name'],  'mcisogem.account.period' : ['id','name'] }

	def _get_centre(self, cr,uid,context):
		
		cr.execute('select centre_id from res_users where id=%s', (uid,))
		centre_user_id = cr.fetchone()[0]
		if centre_user_id:
			centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
			
			return centre.id
		else:
			return 0

	def init_server(self, cr, uid, context):
		# raise osv.except_osv('Attention' ,'action serveur execute en premier!')
		centre_id = self._get_centre(cr,uid,context)
		print('*************execute action serveur************')
		print('*************garant report************')
		print(centre_id)
		
		tools.drop_view_if_exists(cr, 'report_prestation_r_centre')
		cr.execute("""

				create or replace view report_prestation_r_centre as (
					SELECT
					min(mcisogem_prestation.id) AS id,
					mcisogem_prestation.garant_id as garant_id,
					mcisogem_prestation.police_id as police_id,
					mcisogem_prestation.exercice_id as exercice_id,
					mcisogem_prestation.periode_id as periode_id,
					mcisogem_prestation.beneficiaire_id as beneficiaire_id,
					COUNT(mcisogem_prestation.id) as nbr_total,
					SUM(mcisogem_prestation.part_gest) as montant_remb
					
					
					
				FROM
				  public.mcisogem_prestation,  public.mcisogem_police, public.mcisogem_garant, mcisogem_exercice,public.mcisogem_benef, public.mcisogem_account_period 
				WHERE
					mcisogem_prestation.centre_id = %s AND mcisogem_prestation.garant_id = mcisogem_garant.id  AND mcisogem_prestation.police_id = mcisogem_police.id AND mcisogem_prestation.exercice_id = mcisogem_exercice.id AND mcisogem_prestation.periode_id = mcisogem_account_period.id AND mcisogem_account_period.exercice_id = mcisogem_exercice.id AND mcisogem_prestation.beneficiaire_id = mcisogem_benef.id AND mcisogem_prestation.state = 'P' 
				GROUP BY
					mcisogem_prestation.centre_id, mcisogem_prestation.garant_id,mcisogem_prestation.police_id, mcisogem_prestation.exercice_id, mcisogem_prestation.periode_id,mcisogem_prestation.beneficiaire_id
			 
				)""", (centre_id,))

	
		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.prestation.r.centre.graph')], context=context)
		if view_ids:
			if centre_id:
				res = {
				'res_id': centre_id,
				'view_id': view_ids[0],
				'view_mode': 'graph',
				'view_type': 'form',
				'res_model': 'report.prestation.r.centre',
				'type': 'ir.actions.act_window',
				'context': context
				}
				print(res)
		else:
			print("TEST")
		return res


	def init(self, cr):
		tools.drop_view_if_exists(cr, 'report_prestation_r_centre')
		cr.execute("""
			create or replace view report_prestation_r_centre as (
				SELECT
					min(mcisogem_prestation.id) AS id,
					mcisogem_prestation.garant_id as garant_id,
					mcisogem_prestation.police_id as police_id,
					mcisogem_prestation.exercice_id as exercice_id,
					mcisogem_prestation.beneficiaire_id as beneficiaire_id,
					COUNT(mcisogem_prestation.id) as nbr_total,
					SUM(mcisogem_prestation.part_gest) as montant_remb
					
					
					
				FROM
				  public.mcisogem_prestation, public.mcisogem_police, mcisogem_exercice,public.mcisogem_benef
				WHERE
					mcisogem_prestation.police_id = mcisogem_police.id AND mcisogem_prestation.exercice_id = mcisogem_exercice.id AND mcisogem_prestation.beneficiaire_id = mcisogem_benef.id AND mcisogem_prestation.state = 'GF' 
				GROUP BY
					mcisogem_prestation.centre_id,mcisogem_prestation.garant_id, mcisogem_prestation.police_id, mcisogem_prestation.exercice_id, mcisogem_prestation.beneficiaire_id
			 
			)""")
	  


