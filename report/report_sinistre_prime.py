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

class report_sinistre_prime(osv.osv):
	_name = "report.sinistre.prime"
	_description = "Le rapport des sinistre sur prime"
	_auto = False
   

	_columns = {
		
		'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'beneficiaire_id': fields.many2one('mcisogem.benef','Bénéficiaires', readonly=True),
		'sinistre_montant': fields.float('Montant sinistre', readonly=True),
		'sinistre_prime': fields.float('Sinistre/prime', readonly=True),
	}
	
	_depends = {'mcisogem.garant': ['id','name'] ,'mcisogem.police' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'],'mcisogem.account.period' : ['id','name'],'mcisogem.benef' : ['id','name']  }



	def init_server(self, cr, uid, context):
		print('*************execute init************')
		print('*************sinistre sur prime************')
		cr.execute("select report_sinistre_prime()")
		tools.drop_view_if_exists(cr, 'report_sinistre_prime')
		cr.execute("""
			create or replace view report_sinistre_prime as (
				 SELECT 

				 	min(mcisogem_report_stat_sinistre_prime.id) AS id, 
					mcisogem_report_stat_sinistre_prime.garant_id as garant_id,
					mcisogem_report_stat_sinistre_prime.police_id as police_id,
					mcisogem_report_stat_sinistre_prime.exercice_id as exercice_id,
					mcisogem_report_stat_sinistre_prime.beneficiaire_id as beneficiaire_id,
					mcisogem_report_stat_sinistre_prime.sinistre_montant as sinistre_montant,
					mcisogem_report_stat_sinistre_prime.sinistre_prime as sinistre_prime
					


    			FROM mcisogem_report_stat_sinistre_prime

    			group by
					garant_id, police_id, beneficiaire_id, exercice_id, sinistre_montant, sinistre_prime
				
			 
			)""")
		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.sinistre.prime.graph')], context=context)
		if view_ids:
			# if garant_id:
			res = {
			# 'res_id': garant_id,
			'view_id': view_ids[0],
			'view_mode': 'graph',
			'view_type': 'form',
			'res_model': 'report.sinistre.prime',
			'type': 'ir.actions.act_window',
			'context': context
			}
			print(res)
		else:
			print("TEST")
		return res

	def init(self, cr):
		print('*************execute init************')
		print('*************sinistre sur prime************')
		cr.execute("select report_sinistre_prime()")
		tools.drop_view_if_exists(cr, 'report_sinistre_prime')
		cr.execute("""
			create or replace view report_sinistre_prime as (
				 SELECT 

				 	min(mcisogem_report_stat_sinistre_prime.id) AS id, 
					mcisogem_report_stat_sinistre_prime.garant_id as garant_id,
					mcisogem_report_stat_sinistre_prime.police_id as police_id,
					mcisogem_report_stat_sinistre_prime.exercice_id as exercice_id,
					mcisogem_report_stat_sinistre_prime.beneficiaire_id as beneficiaire_id,
					mcisogem_report_stat_sinistre_prime.sinistre_montant as sinistre_montant,
					mcisogem_report_stat_sinistre_prime.sinistre_prime as sinistre_prime
					


    			FROM mcisogem_report_stat_sinistre_prime

    			group by
					garant_id, police_id, beneficiaire_id, exercice_id, sinistre_montant, sinistre_prime
				
			 
			)""")
	  


