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

class mcisogem_histo_copie_tarif_police(osv.osv):
    _name = "mcisogem.histo.copie.tarif.police"
    _description = "Historique des copies de tarif par police"

    _columns = {
        'police_source_id' : fields.many2one('mcisogem.police','Police source' , required=True),
        'police_dest_id' : fields.many2one('mcisogem.police' , 'Police de destination' , required=True),
        'dt_effet_tarif': fields.date('Date d\'effet' , required=True),
        'resilie_compris': fields.boolean('Prendre en compte les polices résiliées'),
    }

    _defaults ={
        'dt_effet_tarif' : time.strftime("%Y-%m-%d", time.localtime()),
    }

    def check_etat_police(self,cr,uid, police_id):
        # cette fonction retourne l'état de la police qu'on lui passe en paramètre 
        police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
        result = self.pool.get('mcisogem.police').search_count(cr,uid,[('id','=',police_id)])
        if result > 0:

            police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)
            return police_data.state
        else:
            return False


    def create(self,cr,uid,vals,context):



        if vals['police_dest_id'] == vals['police_source_id']:
            raise osv.except_osv('Attention !', "La police source et la police de destination sont identiques ! ") 

        obj_tarif_negocie = self.pool.get('mcisogem.tarif.nego.police') # on recupere l objet tarif.nego.police
        data ={}
        
        #print(vals['police_dest_id'])
        # on selectionne toutes les lignes ou apparait la police source
        les_tarifs = self.pool.get('mcisogem.tarif.nego.police').search(cr,uid,[('police_id','=',vals['police_source_id'])])

        cr.execute('select code_gest_id from res_users where id=%s', (uid,))
        cod_gest_id = cr.fetchone()[0]

        p = self.pool.get('mcisogem.police').search(cr,uid,[('id','=',vals['police_dest_id'])])
        p_dat = self.pool.get('mcisogem.police').browse(cr,uid,p)

        for les_tarif_data in self.pool.get('mcisogem.tarif.nego.police').browse(cr,uid,les_tarifs):

            data['code_gest'] = les_tarif_data.code_gest
            data['police_id'] = vals['police_dest_id']
            data['libelle_court_acte'] = les_tarif_data.libelle_court_acte
            data['lbc_nonem_prest'] = les_tarif_data.lbc_nonem_prest
            data['nomen_prest_id'] = les_tarif_data.nomen_prest_id['id']
            data['centre_id'] = les_tarif_data.centre_id['id']
            data['code_centre'] = les_tarif_data.code_centre
            data['lb_centre'] = les_tarif_data.lb_centre
            data['num_interne_pol'] = les_tarif_data.num_interne_pol
            data['lb_police'] = p_dat.name
            data['affichage']=les_tarif_data.affichage
            data['affichage_garant'] = les_tarif_data.affichage_garant
            data['ident_centre'] = cod_gest_id
            data['code_langue'] = les_tarif_data.code_langue
            data['dt_effet_tarif'] = vals['dt_effet_tarif']
            data['mnt_brut_tarif'] = les_tarif_data.mnt_brut_tarif
            data['mnt_plfd_tarif'] = les_tarif_data.mnt_plfd_tarif
            data['state'] = 'N'


            tarif_existe = self.pool.get('mcisogem.tarif.nego.police').search_count(cr,uid,[('nomen_prest_id','=',data['nomen_prest_id']),('centre_id','=',data['centre_id']),('police_id','=',data['police_id']),('dt_effet_tarif','=',data['dt_effet_tarif'])])

            if vals['resilie_compris']==False:#si les polices resiliees ne sont pas prises en compte
                if self.check_etat_police(cr,uid,data['police_id']) == "draft":

                    if tarif_existe == 0:  # on verifie si cette ligne n'existe pas avant de l'enregistrer

                        cr.execute("insert into mcisogem_tarif_nego_police(nomen_prest_id,libelle_court_acte,lbc_nonem_prest,code_centre,centre_id,police_id,num_interne_pol,lb_police,dt_effet_tarif,mnt_brut_tarif,mnt_plfd_tarif,state,ident_centre,code_langue,code_gest,affichage,affichage_garant,lb_centre) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data['nomen_prest_id'],data['libelle_court_acte'],data['lbc_nonem_prest'],data['code_centre'],data['centre_id'],data['police_id'],data['num_interne_pol'],data['lb_police'],data['dt_effet_tarif'],data['mnt_brut_tarif'],data['mnt_plfd_tarif'],data['state'],data['ident_centre'],data['code_langue'],self._get_cod_gest(cr, uid),data['affichage'],data['affichage_garant'],data['lb_centre']))
            
            else:
                if tarif_existe == 0:
                    cr.execute("insert into mcisogem_tarif_nego_police(nomen_prest_id,libelle_court_acte,lbc_nonem_prest,code_centre,centre_id,police_id,num_interne_pol,lb_police,dt_effet_tarif,mnt_brut_tarif,mnt_plfd_tarif,state,ident_centre,code_langue,code_gest,affichage,affichage_garant) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data['nomen_prest_id'],data['libelle_court_acte'],data['lbc_nonem_prest'],data['code_centre'],data['centre_id'],data['police_id'],data['num_interne_pol'],data['lb_police'],data['dt_effet_tarif'],data['mnt_brut_tarif'],data['mnt_plfd_tarif'],data['state'],data['ident_centre'],data['code_langue'],self._get_cod_gest(cr, uid),data['affichage'],data['affichage_garant']))

        return super(mcisogem_histo_copie_tarif_police,self).create(cr,uid,vals,context)


class mcisogem_histo_copie_tarif_centre(osv.osv):
    _name = "mcisogem.histo.copie.tarif.centre"
    _description = "Historique des copies de tarif par centre"

    def check_etat_police(self,cr,uid, police_id):
        # cette fonction retourne l'état de la police qu'on lui passe en paramètre 
        police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
        result = self.pool.get('mcisogem.police').search_count(cr,uid,[('id','=',police_id)])
        if result > 0:

            police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)
            return police_data.state
        else:
            return False


    _columns = {
        'centre_source_id' : fields.many2one('mcisogem.centre','Centre source' , required=True),
        'centre_dest_id' : fields.many2one('mcisogem.centre' , 'Centre de destination' , required=True),
        'dt_effet_tarif': fields.date('Date d\'effet' , required=True),
        'resilie_compris': fields.boolean('Prendre en compte les polices résiliées'),
    }

    _defaults ={
        'dt_effet_tarif' : time.strftime("%Y-%m-%d", time.localtime()),
    }

    def create(self,cr,uid,vals,context=None):
        

        if vals['centre_dest_id'] == vals['centre_source_id']:
            raise osv.except_osv('Attention !', "Le centre source et le centre de destination sont identiques ! ")

            
        obj_tarif_negocie = self.pool.get('mcisogem.tarif.nego.police') # on recupere l objet tarif.nego.police

        cr.execute('select code_gest_id from res_users where id=%s', (uid,))        
        cod_gest_id = cr.fetchone()[0]


        les_tarifs = self.pool.get('mcisogem.tarif.nego.police').search(cr,uid,[('centre_id','=',vals['centre_source_id'])])

        c= self.pool.get('mcisogem.centre').search(cr,uid,[('id','=',vals['centre_dest_id'])])
        c_dat = self.pool.get('mcisogem.centre').browse(cr,uid,c)
        
        for tarif in self.pool.get('mcisogem.tarif.nego.police').browse(cr,uid,les_tarifs):

            data = {}
            data['police_id'] = tarif.police_id['id']
            data['libelle_court_acte'] = tarif.libelle_court_acte
            data['lbc_nonem_prest'] = tarif.lbc_nonem_prest
            data['nomen_prest_id'] = tarif.nomen_prest_id['id']
            data['centre_id'] = vals['centre_dest_id']
            data['code_centre'] = tarif.code_centre
            data['lb_centre'] = c_dat.name
            data['num_interne_pol'] = tarif.num_interne_pol
            data['lb_police'] = tarif.lb_police
            data['affichage']=tarif.affichage
            data['affichage_garant'] = tarif.affichage_garant
            data['code_gest'] = tarif.code_gest
            data['code_langue'] = tarif.code_langue
            data['dt_effet_tarif'] = tarif.dt_effet_tarif
            data['mnt_brut_tarif'] = tarif.mnt_brut_tarif
            data['mnt_plfd_tarif'] = tarif.mnt_plfd_tarif
            data['state'] = 'N'
            data['code_gest'] = tarif.code_gest
            data['code_langue'] = tarif.code_langue

            tarif_existe = self.pool.get('mcisogem.tarif.nego.police').search_count(cr,uid,[('nomen_prest_id','=',data['nomen_prest_id']),('centre_id','=',data['centre_id']),('police_id','=',data['police_id']),('dt_effet_tarif','=',data['dt_effet_tarif'])])

            cr.execute('select code_gest_id from res_users where id=%s', (uid,))
            cod_gest_id = cr.fetchone()[0]
            gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, cod_gest_id, context=context)
            
            print(type(data['code_gest']))
            if tarif_existe == 0:

                cr.execute("insert into mcisogem_tarif_nego_police(nomen_prest_id,libelle_court_acte,lbc_nonem_prest,code_centre,centre_id,police_id,num_interne_pol,lb_police,dt_effet_tarif,mnt_brut_tarif,mnt_plfd_tarif,state,ident_centre,code_langue,code_gest,affichage,affichage_garant,lb_centre) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data['nomen_prest_id'],data['libelle_court_acte'],data['lbc_nonem_prest'],data['code_centre'],data['centre_id'],data['police_id'],data['num_interne_pol'],data['lb_police'],data['dt_effet_tarif'],data['mnt_brut_tarif'],data['mnt_plfd_tarif'],data['state'],cod_gest_id,data['code_langue'],data['code_gest'],data['affichage'],data['affichage_garant'],data['lb_centre']))
            
        return super(mcisogem_histo_copie_tarif_centre , self).create(cr,uid,vals,context)