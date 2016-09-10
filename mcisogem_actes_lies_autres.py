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

class mcisogem_actes_lies_autres(osv.osv):
    _name =  "mcisogem.actes.lies.autres"
    _description = "Actes lies a un autre"

    _columns = {
        'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
        'code_familles': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
        'lbc_nomprest_p': fields.many2one('mcisogem.nomen.prest', "Acte", required=True),
        'acte_ids': fields.many2many('mcisogem.nomen.prest',
                                       'mcisogem_famacte_rel',
                                        'acte_id',
                                        'code_acte',
                                        'Actes'),
        
        'dt_eff_plfd_grpe_acte_det': fields.datetime("Date d'effet", required=True),
        'date_resiliation': fields.datetime("Date de résiliation", required=True),
        'code_langue': fields.char('code_langue', size=10 ),
    }

   
    def onchange_codefamille(self, cr, uid, ids, code_famille, context=None):
        tabactes=[]
        if not code_famille:
            return {'value': {'lbc_nomprest_p': False}}
        if code_famille:
            
            #Recuperation de la liste de tous les actes liés au groupe de famille
            cr.execute("select * from mcisogem_nomen_prest where code_fam_prest=%s", (code_famille,))
            lesactes = cr.dictfetchall()
            if len(lesactes)>0:
              
                for acte in lesactes:
    
                    tabactes.append(acte['id'])
                    print'**************************'
                    print(tabactes)
                return {'value': {'lbc_nomprest_p': tabactes}}