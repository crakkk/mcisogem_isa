# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields, osv

class lono_recharge_report(osv.Model):
    _name = "lono.recharge.report"
    _description = "Statistiques des rechargements"
    _auto = False
    _columns = {
        'montant': fields.integer('Montant', readonly=True),
        'nbre': fields.integer('Nombre de rechargement'),
        'client_id': fields.many2one('lono.client', 'Client'),
        'type_id': fields.many2one('lono.type.recharge', 'Type de rechargement'),
        'exercice_id': fields.many2one('lono.exercice', 'Exercice', readonly=True),
        'periode_id': fields.many2one('lono.account.period', 'Période', readonly=True)
        }
    _depends = {
        'lono.client' : ['id','name'],
        'lono.type.recharge' : ['id','name'],
        'lono.exercice' : ['id','name'],
        'lono.account.period' : ['id','name','code']
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'lono_recharge_report')
        cr.execute("""
            create or replace view lono_recharge_report as (
                    select
                        min(lono_recharge.id) as id,
                        count(lono_recharge.id) as nbre,
                        sum(cast(lono_recharge.montant as INT)) as montant,
                        lono_client.id as client_id,
                        lono_type_recharge.id as type_id,
                        lono_account_period.exercice_id as exercice_id,
                        lono_account_period.id as periode_id                        
                    from
                        public.lono_recharge, public.lono_type_recharge, public.lono_client, public.lono_account_period
                    where 
                        lono_recharge.client_id = lono_client.id and 
                        lono_recharge.type_id = lono_type_recharge.id and 
                        lono_recharge.periode_id = lono_account_period.id
                    group by
                        lono_account_period.exercice_id,
                        lono_type_recharge.id,
                        lono_account_period.id,
                        lono_client.id
                        
            )
        """)

