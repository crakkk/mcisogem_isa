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

class mcisogem_report_stat_ententep(osv.osv):
	_name = "mcisogem.report.stat.ententep"
	_description = "Graphes sur les Bénéficiaires"
	# _auto = False
   

	_columns = {
		
		'centre_id': fields.many2one('mcisogem.centre', 'Centre', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'nbr_attente': fields.integer('Attente', readonly=True),
		'nbr_valide': fields.integer('Valide', readonly=True),
		'nbr_rejete': fields.integer('Rejete', readonly=True),
		'nbr_total': fields.integer('Total', readonly=True),
		
	}
	
	_depends = {'mcisogem.centre' : ['id','name'], 'mcisogem.police' : ['id','name'],'mcisogem.account.period' : ['id','name'], 'mcisogem.exercice' : ['id','name','date_debut','date_fin']}


	# def init(self, cr):
	# 	tools.drop_view_if_exists(cr, 'report_ententep')
	# 	cr.execute("""
	# 		create or replace view report_ententep as (
	# 			select
	# 				min(mcisogem_entente.id) AS id,
	# 				count(mcisogem_entente.id) as nbr_demende_total,  
	# 				mcisogem_entente.centre_id as centre_id,
	# 				mcisogem_entente.beneficiaire_id as beneficiaire_id
						
	# 			from
	# 			  public.mcisogem_entente, public.mcisogem_centre, public.mcisogem_benef
	# 			where
	# 				mcisogem_entente.centre_id = mcisogem_centre.id and mcisogem_entente.beneficiaire_id = mcisogem_benef.id
	# 			group by 
	# 				mcisogem_entente.centre_id, mcisogem_entente.beneficiaire_id

	# 		)""")
	  


