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



class mcisogem_tarif_convention_medecin(osv.osv):
    _name = "mcisogem.tarif.convention.medecin"
    _description = 'Tarif convention medecin'
    _columns = {
        'code_centre': fields.many2one('mcisogem.centre', "Centre", required=True),
        'code_medecin': fields.many2one('mcisogem.agr.prestat', "Medecin", required=True),
        'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte", required=True),
        'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", ),
        'montant_brut_tarif': fields.integer('Montant brut tarif', ),
        'plafond_tarif': fields.integer('plafond', ),
        'affichage' : fields.integer('affichage', required=False),
        'code_tarif_convention_medecin_temp': fields.many2many('mcisogem.tarif.convention.medecin.temp',
                                       'mcisogem_convention_medecin_temp_rel',
                                        'convention_medecin_temp_id',
                                        'code_convention_medecin',
                                        'Choix des actes', required=False),
        'date_effet_tarif': fields.datetime("Date d'effet", required=True),
        'date_resiliation_tarif': fields.date("Date de résiliation", required=True),
      
        'code_sup' : fields.char('cod_sup', size=1),

}
    _defaults = {
        'date_resiliation_tarif': '1900-01-01 00:00:00',
        'affichage': 0
}




    def onchange_code_famille_tarif_convention_medecin(self, cr, uid, ids, code_famille, context=None):
        
        # Avant tout on vide la table temporaire des tarifs convention medecin
        # Vidage des tables temporaires
        cr.execute("delete from mcisogem_tarif_convention_medecin_temp where write_uid=%s", (uid,))
        
        if not code_famille:
            return {'value': {'code_tarif_convention_medecin_temp': False}}
        if code_famille:
            data = []
            # Recuperation de la liste de tous les actes de la famille
            cr.execute("select * from mcisogem_nomen_prest where code_fam_prest=%s", (code_famille,))
            lesactes = cr.dictfetchall()
            print ('*********************************')
            print (len(lesactes))
            print ('*********************************')
            if len(lesactes) > 0:
            # Insertion de la liste des actes dans la table mcisogem_tarif_convention_medecin_temp
            # Parcours de la liste et enregistrement des donn�es en base
                for acte in lesactes:
                    cr.execute("insert into mcisogem_tarif_convention_medecin_temp (create_uid,choix_conv,code_famille,code_acte,montant_brut_tarif,plafond_tarifconv, write_uid) values(%s, %s, %s, %s, %s, %s, %s)", (uid, False, code_famille, acte['id'], 0, 0, uid))
                    cr.execute("select * from mcisogem_tarif_convention_medecin_temp where write_uid=%s", (uid,))
                    lestarifstemp = cr.dictfetchall()
                for tarif in lestarifstemp:
                        data.append(tarif['id'])
                return{'value': {'code_tarif_convention_medecin_temp': data}}
            else:
                return {'value': {'code_tarif_convention_medecin_temp': False}}
            
            
    def create(self, cr, uid, vals, context=None):

        dernier_id = 0
        # Recuperation de la date du jour
        
  
      # Recuperation des lignes qui ont été cochées dans la table mcisogem_tarif_convention_temp
        cr.execute("select * from mcisogem_tarif_convention_medecin_temp where write_uid=%s and choix_conv=%s", (uid, True))
        lesactes = cr.dictfetchall()
        print ('*********************************')
        print (len(lesactes))
        print ('*********************************')
        if len(lesactes) > 0:
          
          # Recuperation des valeurs par défaut
          #utilisateur_data = self.pool.get('res.users').browse(cr, uid, uid, context=context)
          #centre_gestion_data = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, utilisateur_data.code_gest_id.id, context=context)
          
          # Parcours de la liste des actes sélectionné
          for acte in lesactes:
              
                  
              
                 
               
                  data = {}
                  data['create_uid'] = uid      
                  data['code_centre'] = vals['code_centre']      
                  data['code_medecin'] = vals['code_medecin']   
                  data['code_acte'] = acte['code_acte']    
                  data['code_famille'] = acte['code_famille']      
                  data['date_effet_tarif'] = vals['date_effet_tarif']  
                    
                  data['write_uid'] = uid      
                  data['montant_brut_tarif'] = acte['montant_brut_tarif'] 
                  data['plafond_tarif'] = acte['plafond_tarifconv']     
                   
                  data['date_resiliation_tarif'] = vals['date_resiliation_tarif']    
                  data['affichage'] = 1
                  
                  dernier_id = super(mcisogem_tarif_convention_medecin, self).create(cr, uid, data, context=context)
          cr.execute("delete from mcisogem_tarif_convention_medecin_temp where write_uid=%s", (uid,))
          return dernier_id
        else:
          raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un acte!")
          return 0
        

mcisogem_tarif_convention_medecin()



class mcisogem_tarif_convention_medecin_temp(osv.osv):
    _name = "mcisogem.tarif.convention.medecin.temp"
    _description = 'Tarif convention temporaire'
    _columns = {
        'code_famille': fields.many2one('mcisogem.fam.prest', "Famille d'acte"),
        'choix_conv': fields.boolean('Choix'),
        'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte" ,readonly=True),
        'montant_brut_tarif': fields.integer('Montant brut tarif',),
        'plafond_tarifconv': fields.integer('plafond'),
}
    
mcisogem_tarif_convention_medecin_temp()    
  
    
