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

class report_benef_inter(osv.osv):
	_name = "report.benef.inter"
	_description = "Graphes sur les Bénéficiaires"
	_auto = False
   

	_columns = {
		'intermediaire_id' : fields.many2one('mcisogem.courtier', 'Intermediaire', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'nbr_benef_total': fields.integer('Total Bénéficiaires', readonly=True)
		
	}
	
	_depends = {'mcisogem.courtier': ['id','name'] ,'mcisogem.police' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'] }


	def init(self, cr):
		tools.drop_view_if_exists(cr, 'report_benef_inter')
		cr.execute("""
			create or replace view report_benef_inter as (
				select
					min(mcisogem_benef.id) AS id,
					count(mcisogem_benef.id) as nbr_benef_total,  
					mcisogem_courtier.id as intermediaire_id,
					mcisogem_exercice.id as exercice_id,
					mcisogem_police.id as police_id

				from
				   public.mcisogem_courtier, public.mcisogem_police, public.mcisogem_benef,  public.mcisogem_exercice 
				where
					mcisogem_courtier.id = mcisogem_police.courtier_id and mcisogem_exercice.id = mcisogem_police.exercice_id and mcisogem_police.id = mcisogem_benef.police_id
				group by
					mcisogem_courtier.id, mcisogem_exercice.id, mcisogem_police.id 
			)""")
	  


