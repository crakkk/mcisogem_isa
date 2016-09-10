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

class mcisogem_intervalle2actes(osv.osv):
	_name  = "mcisogem.intervalle2actes"
	_description = "Intervalle de jours entre 02 actes"

	_columns= {

		'num_intervalle' : fields.integer('Code'),
		'code_acte': fields.many2one('mcisogem.nomen.prest', 'Acte', required=True),
		'intervallejr' : fields.integer('Nombre de jours', required=True),
		'avecaffection' : fields.boolean('Avec la même affection', required=False),
		# 'code_acte_gratuit': fields.many2one('mcisogem.nomen.prest', 'Acte gratuit de rechange', required=True),
		'dt_eff_inter_2actes': fields.date('Date d\'effet', required=True),
		'dt_resil_inter_2actes': fields.date('Date de résiliation'),
		'qteautorise' : fields.integer('Quantité autorisé', required=True),
		# 'perioprescrit' : fields.many2one('mcisogem.unite.temps', 'Périodicité de prescription', required=True),
		'nbre_jr' : fields.integer('Nombre de jour'),
		'cod_sup' : fields.char('cod_sup', size=1),
		'state': fields.selection([
			('A', "Actif"),
			('R', "Résilié"),
		], 'Statut'),

	}

	_rec_name = 'code_acte'



	_defaults = {
		'state' : 'A',
	}
	
	def button_activer(self,cr,uid,ids,context=None):
		return self.write(cr, uid, ids, {'state':'A', 'dt_resil_inter_2actes':False}, context=context)

	def button_resilier(self,cr,uid,ids,context=None):
		return self.write(cr, uid, ids, {'state':'R', 'dt_resil_inter_2actes':time.strftime("%Y-%m-%d")}, context=context)



	# def create(self, cr, uid, vals, context=None):
	# 	#Récuperation du nombre d'intervalle puis définition du code de la chambre
	# 	cr.execute("select * from mcisogem_intervalle2actes where id>%s", (0,))
	# 	vals['num_intervalle'] = len(cr.dictfetchall()) + 1
	# 	#Recuperation des données sur l'unité de temps
	# 	cr.execute("select * from mcisogem_unite_temps where id=%s", (str(vals['perioprescrit']),))
	# 	unite_temps = cr.dictfetchall()[0]
	# 	vals['nbre_jr'] = unite_temps['nbre_jour']
	# 	return super(mcisogem_intervalle2actes, self).create(cr, uid, vals, context=context)
