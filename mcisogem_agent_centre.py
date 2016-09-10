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

class mcisogem_agent_centre(osv.osv):
    _name =  "mcisogem.agent.centre"
    _description = "Agent Centre"

    _columns = {
        
        
        'Code_agent' : fields.char('Code_agent', required=True),
        'centre_id' : fields.many2one('mcisogem.centre' , 'Centre'),
        'lbc_centre' : fields.char('Libelle du centre'),

        'Num_prest_exec' : fields.integer('Num_prest_exec'),

        'Nom_agent' : fields.char('Nom de l\'agent',size=50),
        'Prenom_agent' : fields.char('Prénom de l\'agent',size=50),
        'login_agent' : fields.char('Login',size=50,required=True),
        'Mdp_agent' : fields.char('Mot de passe',size=50,required=True),
        
        'email_agent' : fields.char('Email de l\'agent',size=50),
        'Dte_arr_ag' : fields.datetime('Date d \'agrement'),
       
        'Active_agent' : fields.boolean('Active_agent'),
        
        'nivo_agent' : fields.integer('nivo_agent'),
        'statut_agent' : fields.selection([('1', 'Actif'), ('2', 'Inactif')] , 'Statut'),
    }

   
    def onchange_centre(self, cr, uid, ids, centre_id, context=None):
        v = {}
        
        centre = self.pool.get('mcisogem.centre').search(cr, uid,[('id', '=', centre_id)])
        centre_data = self.pool.get('mcisogem.centre').browse(cr, uid, centre)
        
        
        v = {'lbc_centre':centre_data.code_centre }
        return {'value' : v}
    
    
    
    
    def create(self, cr, uid, data, context=None):
        
        
            vals = {}
            vals['Code_agent']=data['Code_agent']
            vals['login_agent']=data['login_agent']
            vals['Mdp_agent']=data['Mdp_agent']
            vals['Nom_agent']=data['Nom_agent']
            vals['Prenom_agent']=data['Prenom_agent']
            vals['email_agent']=data['email_agent']
            vals['Dte_arr_ag']=data['Dte_arr_ag']
            vals['statut_agent']=data['statut_agent']
            vals['Active_agent']=0
            vals['nivo_agent']=1
            vals['Num_prest_exec']=0
            vals['centre_id']= data['centre_id']
            
            centre_data = self.pool.get('mcisogem.centre').browse(cr, uid,data['centre_id'] )
            vals['lbc_centre']=centre_data.name
           
            
            lagent = super(mcisogem_agent_centre , self).create(cr, uid, vals, context=context)
                            
             
            return lagent

# Fin exclusion d'acte par police 