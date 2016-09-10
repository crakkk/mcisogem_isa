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
        'convention_id': fields.many2one('mcisogem.convention.unique', "Convention", required=True),
        'centre_ids':fields.many2many('mcisogem.centre',
                                       'mcisogem_centre_rel',
                                        'mcisogem_centre_rel_id',
                                        'code_centre', 'des centres', required=True),
        
    }
    _rec_name = 'convention_id'
    
    
    
    

    
    
