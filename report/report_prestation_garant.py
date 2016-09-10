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

class report_prestation_garant(osv.osv):
	_name = "report.prestation.garant"
	_description = "Graphes sur les prestation garant"
	_auto = False
   

	_columns = {
		
		
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'beneficiaire_id': fields.many2one('mcisogem.benef','Bénéficiaires', readonly=True),
		'montant_total': fields.integer('Montant total', readonly=True),
		'montant_remb': fields.integer('Montant rembourse', readonly=True),
		'montant_exclu': fields.integer('Montant exclus', readonly=True),
		
	}
	
	_depends = {'mcisogem.police' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'],'mcisogem.benef' : ['id','name']  }

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
		
		tools.drop_view_if_exists(cr, 'report_prestation_garant')
		cr.execute("""

				create or replace view report_prestation_garant as (
					SELECT
					min(mcisogem_prestation.id) AS id,
					mcisogem_prestation.police_id as police_id,
					mcisogem_prestation.exercice_id as exercice_id,
					mcisogem_prestation.beneficiaire_id as beneficiaire_id,
					SUM(mcisogem_prestation.montant_total) as montant_total,
					SUM(mcisogem_prestation.part_gest) as montant_remb,
					SUM(mcisogem_prestation.montant_exclu) as montant_exclu
					
					
				FROM
				  public.mcisogem_prestation,  public.mcisogem_police, mcisogem_exercice,public.mcisogem_benef
				WHERE
					mcisogem_prestation.garant_id = %s AND mcisogem_prestation.police_id = mcisogem_police.id AND mcisogem_prestation.exercice_id = mcisogem_exercice.id AND mcisogem_prestation.beneficiaire_id = mcisogem_benef.id AND (mcisogem_prestation.state NOT IN ('SS','SP')) 
				GROUP BY
					mcisogem_prestation.garant_id, mcisogem_prestation.police_id, mcisogem_prestation.exercice_id, mcisogem_prestation.beneficiaire_id
			 
				)""", (garant_id,))

	
		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.prestation.garant.graph')], context=context)
		if view_ids:
			if garant_id:
				res = {
				'res_id': garant_id,
				'view_id': view_ids[0],
				'view_mode': 'graph',
				'view_type': 'form',
				'res_model': 'report.prestation.garant',
				'type': 'ir.actions.act_window',
				'context': context
				}
				print(res)
		else:
			print("TEST")
		return res


	def init(self, cr):
		tools.drop_view_if_exists(cr, 'report_prestation_garant')
		cr.execute("""
			create or replace view report_prestation_garant as (
				SELECT
					min(mcisogem_prestation.id) AS id,
					mcisogem_prestation.police_id as police_id,
					mcisogem_prestation.exercice_id as exercice_id,
					mcisogem_prestation.beneficiaire_id as beneficiaire_id,
					SUM(mcisogem_prestation.montant_total) as montant_total,
					SUM(mcisogem_prestation.part_gest) as montant_remb,
					SUM(mcisogem_prestation.montant_exclu) as montant_exclu
					
					
				FROM
				  public.mcisogem_prestation, public.mcisogem_police, mcisogem_exercice,public.mcisogem_benef
				WHERE
					mcisogem_prestation.police_id = mcisogem_police.id AND mcisogem_prestation.exercice_id = mcisogem_exercice.id AND mcisogem_prestation.beneficiaire_id = mcisogem_benef.id AND (mcisogem_prestation.state NOT IN ('SS','SP')) 
				GROUP BY
					mcisogem_prestation.garant_id, mcisogem_prestation.police_id, mcisogem_prestation.exercice_id, mcisogem_prestation.beneficiaire_id
			 
			)""")
	  


