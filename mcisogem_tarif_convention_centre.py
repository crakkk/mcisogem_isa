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

class mcisogem_tarif_convention_centre(osv.osv):
    _name = "mcisogem.tarif.convention.centre"
    _description = "Tarif Convention Centre"

    _columns = {
        'code_garant': fields.many2one('mcisogem.garant', 'Garant', required=True),
        'code_police': fields.many2one('mcisogem.police', 'Police', required=True),
        'code_college': fields.many2one('mcisogem.college', 'Collège', required=False),
        'code_college_ids':fields.many2many('mcisogem.convention.centre.college.temp',
                                       'mcisogem_convention_centre_college_temp_rel',
                                        'code_college_temp_id',
                                        'code_college', 'Choix des collèges', required=False),
        'code_centre_ids':fields.many2many('mcisogem.centre.convention.temp',
                                       'mcisogem_centre_convention_temp_rel',
                                        'code_centre_temp_id',
                                        'code_centre', 'Choix des centres', required=False),
        'affichage': fields.integer('affichage'),

        'num_tarif_conv_centre' : fields.integer('Code'),
        'code_centre': fields.many2one('mcisogem.centre', 'Centre', required=False),
        'code_acte': fields.many2one('mcisogem.nomen.prest', 'Acte', required=False),
        'code_convention': fields.many2one('mcisogem.convention', 'Convention', required=True),
        'date_effet_tarif': fields.datetime('Date d\'effet', required=True),
        'date_resiliation': fields.datetime('Date de résiliation'),
        'cod_res_conv' : fields.boolean('Code résiliation Convention'),
        'montant_brut_tarif' : fields.integer('Montant brut tarif'),
        'montant_plafond_tarif' : fields.integer('Montant plafond tarif'),
        'cod_sup' : fields.char('cod_sup', size=1),
    }

    _defaults = {
        'date_resiliation': '1900-01-01 00:00:00',
        'affichage' : 0,
    } 
  
    def onchange_code_police(self, cr, uid, ids, code_police, context=None):
         data = []
         if not code_police:
            return False
         else:  
            #Vidage de la table temporaire
            cr.execute("delete from mcisogem_convention_centre_college_temp where write_uid=%s", (uid,))

            #Récuperation de la liste des colleges de la police puis remplissage du tableau des collèges
            cr.execute("select * from mcisogem_histo_police where name = %s" , (code_police,))
            leshistopolice = cr.dictfetchall()
            #Parcours des histos police puis remplissage de la table temporaires des collèges
            if len(leshistopolice) > 0:
                for hp in leshistopolice:
                    #Recuperation des données sur l'historique de police en cours
                    hp_data = self.pool.get('mcisogem.histo.police').browse(cr, uid, hp['id'], context=context)
                    #Récuperation des données sur le collèges
                    college_data = self.pool.get('mcisogem.college').browse(cr, uid, hp['code_college'], context=context)
                    cr.execute("insert into mcisogem_convention_centre_college_temp (create_uid, choix, code, name, code_college, write_uid) values (%s, %s, %s, %s, %s, %s)", (uid, False,college_data.code_college, college_data.name, college_data.id, uid,))
                
                #Recuperation de la liste des collèges enregistrés pour l'affichage
                cr.execute('select * from mcisogem_convention_centre_college_temp where create_uid=%s', (uid,))
                lescollegesenreg = cr.dictfetchall()
                for lc in lescollegesenreg:
                    data.append(lc['id'])
            return {'value': {'code_college_ids': data }}
            
        
    def onchange_code_convention(self, cr, uid, ids, code_convention, context=None):
        #Recuperation de la liste des centres rattachés à la convention puis remplissage du tableau 
         data = []
         if not code_convention:
            return False
         else:  
            #Vidage de la table temporaire
            cr.execute("delete from mcisogem_centre_convention_temp where write_uid=%s", (uid,))
            
            #Récuperation de la liste des centres
            cr.execute("select * from mcisogem_centre")
            lescentres = cr.dictfetchall()
            #Parcours des histos police puis remplissage de la table temporaires des collèges
            if len(lescentres) > 0:
                for hp in lescentres:
                    #Recuperation des données sur l'historique de police en cours
                    centre_data = self.pool.get('mcisogem.centre').browse(cr, uid, hp['id'], context=context)
                    cr.execute("insert into mcisogem_centre_convention_temp (create_uid, choix, code, name, code_centre, write_uid) values (%s, %s, %s, %s, %s, %s)", (uid, False,centre_data.code_centre, centre_data.name, centre_data.id, uid,))
                
                #Recuperation de la liste des collèges enregistrés pour l'affichage
                cr.execute('select * from mcisogem_centre_convention_temp where create_uid=%s', (uid,))
                lescentresenreg = cr.dictfetchall()
                for lc in lescentresenreg:
                    data.append(lc['id'])
            return {'value': {'code_centre_ids': data }}
    
    def create(self, cr, uid, vals, context=None):
        dernier_id = 0
        #Recuperation de la liste des centres sélectionnés
        cr.execute("select * from mcisogem_centre_convention_temp where create_uid=%s and choix =%s", (uid, True,))
        lescentres = cr.dictfetchall()
        if len(lescentres)>0:
            #Récuperation de la liste des collèges sélectionnées
            cr.execute("select * from mcisogem_convention_centre_college_temp where create_uid=%s and choix =%s", (uid, True,))
            lescolleges = cr.dictfetchall()
            
            utilisateur_data = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            centre_gestion_data = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, utilisateur_data.code_gest_id.id, context=context)
            
            #Récuperation des données sur la convention
            cr.execute("select * from mcisogem_tarif_convention where code_convention = %s", (vals['code_convention'],))
            lestarifsconventions = cr.dictfetchall()
            if len(lestarifsconventions) > 0:
                if len(lescolleges) > 0:
                #Parcours des centres, des collèges puis des actes de la convention et insertion des données en base
                    for centr in lescentres:
                        for col in lescolleges:
                            for tc in lestarifsconventions:
                            #Insertion des données en base de données
                                data = {}
                                cr.execute("select * from mcisogem_tarif_convention_centre where id>%s", (0,))
                                data['num_tarif_conv_centre'] = len(cr.dictfetchall()) + 1
                                data['code_garant'] = vals['code_garant']
                                data['code_police'] = vals['code_police']
                                data['code_college'] = col['code_college']
                                data['affichage'] = 1
                                data['code_centre'] = centr['code_centre']
                                data['code_acte'] = tc['code_acte']
                                data['code_convention'] = vals['code_convention']
                                data['date_effet_tarif'] = vals['date_effet_tarif']
                                data['date_resiliation'] = vals['date_resiliation']
                                data['cod_res_conv'] = False
                                data['montant_brut_tarif'] = tc['montant_brut_tarif']
                                data['montant_plafond_tarif'] = 0
                                data['code_gest'] = utilisateur_data.code_gest_id.name
                                data['ident_centre'] = utilisateur_data.code_gest_id.id
                                data['code_langue'] = centre_gestion_data.langue_id.name
                                dernier_id = super(mcisogem_tarif_convention_centre, self).create(cr, uid, data, context=context)
                    return dernier_id
                else:
                    raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un collège !")
                    return False
            else:
                raise osv.except_osv('Attention !', "Aucun tarif n'a été trouvé pour cette convention !")
                return False  
        else:
            raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un centre !")
            return False
            
    
class mcisogem_convention_centre_college_temp(osv.osv):

    _name = "mcisogem.convention.centre.college.temp"
    _description = "Collège"

    _columns = {
        'choix': fields.boolean('Choix'),
        'code' : fields.char('Code' , readonly=True),
        'name' : fields.char('Libellé', readonly=True),
        'code_college':fields.many2one('mcisogem.college', 'name', 'Collège', readonly=True),
    }
    
    def onchange_choix_college(self, cr, uid, ids, choix, context=None):
        cr.execute("update mcisogem_convention_centre_college_temp set choix=%s where id=%s", (choix, ids[0]))
  
  
class mcisogem_centre_convention_temp(osv.osv):

    _name = "mcisogem.centre.convention.temp"
    _description = "Centre"

    _columns = {
        'choix': fields.boolean('Choix'),
        'code' : fields.char('Code' , readonly=True),
        'name' : fields.char('Libellé', readonly=True),
        'code_centre':fields.many2one('mcisogem.centre', 'name', 'Centre', readonly=True),
    }
    
    def onchange_choix_centre(self, cr, uid, ids, choix, context=None):
        cr.execute("update mcisogem_centre_convention_temp set choix=%s where id=%s", (choix, ids[0]))
  
    
    
