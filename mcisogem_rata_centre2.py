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

class mcisogem_rata_convention(osv.osv):
    _name = "mcisogem.rata.convention"
    _description = "Rattachement convention centre"

    _columns = {
        'code_centre': fields.many2one('mcisogem.centre', 'Centre', required=True),
        'dt_agr_prestat': fields.date('Date d\'agrément'),
        'dt_retr_prestat': fields.date('Date de résiliation'),
        'motif_retr_prestat' : fields.char('Motif du retrait', size=30),
        'praticien_ids':fields.many2many('mcisogem.praticien',
                                       'mcisogem_praticien_rel',
                                        'mcisogem_praticien_rel_id',
                                        'libelle_court_prestat', 'Choix du(es) praticien(s)', required=True),
        
    }
    _rec_name = 'code_centre'
    
    
    
    

    
    
