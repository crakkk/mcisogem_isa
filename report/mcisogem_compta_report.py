# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields, osv

class mcisogem_compta_report(osv.Model):
    _name = "mcisogem.compta.report"
    _description = "Analyse des paiements"
    _auto = False
    _columns = {
        'nbr': fields.integer('Nombre de sinistre'),
        'montant': fields.float('Montant'),
        'period_id': fields.many2one('mcisogem.account.period', 'Période'),
        'garant_id': fields.many2one('mcisogem.garant', 'Garant'),
        'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice'),
        'mode_paiement': fields.many2one('mcisogem.regime', 'Type de remboursement'),
        }

    _depends = {
    	'mcisogem.account.period' : ['id','name','code'],
    	'mcisogem.exercice' : ['id','name'],
        'mcisogem.garant' : ['id','name'],
        'mcisogem.regime' : ['id', 'name']
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'mcisogem_compta_report')
        cr.execute("""
            create or replace view mcisogem_compta_report as (
            	SELECT
                    min(mcisogem_prestation.id) as id,
            		count(mcisogem_prestation.id) AS nbr,
            		sum(mcisogem_prestation.part_gest) AS montant,                 
            		mcisogem_account_period.id AS period_id,
            		mcisogem_exercice.id AS exercice_id,
                    mcisogem_garant.id AS garant_id,
                    mcisogem_regime.id AS mode_paiement
            	FROM
            		public.mcisogem_prestation,
            		public.mcisogem_account_period,
                    public.mcisogem_exercice,
                    public.mcisogem_garant,
                    public.mcisogem_regime
            	WHERE
            		mcisogem_prestation.garant_id = mcisogem_garant.id AND
                    mcisogem_prestation.periode_id = mcisogem_account_period.id AND
                    mcisogem_prestation.mode_paiement = mcisogem_regime.id AND
                    mcisogem_account_period.exercice_id = mcisogem_exercice.id AND
                    mcisogem_prestation.state = 'P'
                GROUP BY 
                    mcisogem_exercice.id, mcisogem_account_period.id, mcisogem_garant.id, mcisogem_regime.id
            )
        """)
