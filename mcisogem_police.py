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

_logger = logging.getLogger(__name__)


class mcisogem_police(osv.osv):
    _name = "mcisogem.police"
    _description = 'Police'

    def _get_regime_centre(self, cr, uid, context=None):
        obj = self.pool.get('mcisogem.centre.gestion').search(cr, uid, [('id', '!=', 0)])
        gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, obj, context=context)
        return gest_obj[0].avoir_ro

    def _get_default_regime(self, cr, uid, context=None):
        if self._get_regime_centre(cr, uid, context):
            return 'C'
        else:
            return None

    def onchange_remb(self, cr, uid, ids, remb_souscr_assure, context=None):
        if remb_souscr_assure == 'Aut':
            return {'value': {'remb': False}}
        else:
            return {'value': {'remb': True}}

    def calcul_periode_jr(self, cr, uid, ids, field_name, arg, context=None):

        res = {}
        for police in self.pool.get('mcisogem.police').browse(cr, uid, ids, context):
            dt_deb = datetime.strptime(str(police.dt_effet), '%Y-%m-%d')
            dt_fin = datetime.strptime(str(police.dt_expiration), '%Y-%m-%d')

            duree = (dt_fin - dt_deb).days
            res[police.id] = duree

        return res

    REMB_SELECTION = [
        ('S', 'Souscripteur'),
        ('A', 'Assuré principal'),
        ('Aut', 'Autre')
    ]

    REGIME = [
        ('O', 'Obligatoire'),
        ('C', 'Complémentaire'),
    ]

    _columns = {
        'num_interne_police': fields.integer('Numéro interne de police', readonly=True),
        'num_police': fields.integer('t', required=False),
        'statut_police': fields.integer('Statut police'),
        'affiche_ro': fields.boolean(''),
        'name': fields.char('Libellé', required=True),
        'num_ave_interne_police': fields.integer('Numéro avenant interne police'),
        'remb_souscr_assure': fields.selection(REMB_SELECTION, 'Bénéficiaire du remboursement', required=True),
        'remb_autre': fields.char('Autre mode de remboursement'),
        'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', required=True),
        'dt_deb_exercice': fields.date('Début', readonly=True),
        'dt_fin_exercice': fields.date('Fin', readonly=True),
        'dt_effet': fields.date('Date d\'éffet'),
        'dt_expiration': fields.date('Date d\'expiration'),
        'num_police_assur': fields.char('Numéro police assureur'),
        'num_pol_remplacee': fields.char('Numéro police remplacée'),
        'type_contrat_id': fields.many2one('mcisogem.type.contrat', 'Type de contrat', required=True),
        'mod_recond_id': fields.many2one('mcisogem.mod.recond', 'Mode de reconduction', required=True),
        'territoire_id': fields.many2one('mcisogem.territoire', 'Térritorialité', required=True),
        'souscripteur_id': fields.many2one('mcisogem.souscripteur', 'Souscripteur', required=True),
        'souscripteur_pol': fields.char(''),
        'garant_id': fields.many2one('mcisogem.garant', 'Assureur', required=True),
        'courtier_id': fields.many2one('mcisogem.courtier', 'Intermédiaire', required=True),
        'code_regime': fields.many2one('mcisogem.regime', 'Type de remboursement', required=True),
        'periode_ferme_pol': fields.function(calcul_periode_jr, type='integer', string='Periode Jr', readonly=True),
        'dt_resil_pol': fields.date('Date de résiliation'),
        'cpta_pol': fields.integer('Compte interne'),
        'concurent_id': fields.many2one('mcisogem.concurent', 'Concurent'),

        'code_avenant_initial': fields.integer('Code avenant initiale'),
        'dt_emi_ave': fields.date('Exercice du'),
        'dt_fin_ave': fields.date('Au'),
        'typ_ave': fields.char('Type avenant'),
        'mnt_emi_ave': fields.integer('t'),
        'dt_eff_prime': fields.datetime('t'),
        'mnt_regl_prime_ave': fields.integer('t'),
        'cod_annul_ave': fields.integer('t'),
        'cod_avenant_initial': fields.integer('t'),
        'mnt_regl_prime_ave': fields.integer('t'),
        'calc_prime_ave': fields.integer('t'),
        'tva_oui_non': fields.boolean('Tva'),
        'taxe_enreg': fields.boolean('Taxe d\'enregistrement'),
        'taxe_exon': fields.boolean('Exonération'),
        'base_remb': fields.integer('Base de Remboursement'),
        'imputation_acc_cie': fields.boolean('Compagnie'),
        'imputation_acc_courtier': fields.boolean('Intermédiaire'),
        'imputation_acc_gestionnaire': fields.boolean('Gestionnaire'),
        'imputation_acc_autre': fields.boolean('Autres'),

        'type_prime': fields.selection([('1', 'Statut de bénéficiaire'), ('2', 'Tranche d\'age')],
                                       'Enregistrement prime par', required=True),
        'repartition_prime': fields.selection([('1', 'Mois'), ('2', 'Jour')], 'Repartition prime'),
        'typ_prime': fields.selection(
            [(1, 'Police'), (2, 'Collège'), (3, 'Famille'), (4, 'Bénéficiaire'), (5, 'Souscripteur')], 'typ_prime',
            required=True),
        'bl_exercice_clo': fields.integer('t'),
        'prime_pol_exercice': fields.integer('t'),
        'num_exercice_pol': fields.integer('t'),
        'masse_sal_pol': fields.integer('t'),
        'pc_masse_sal_pol': fields.integer('t'),
        'periodicite_paiem': fields.many2one('mcisogem.unite.temps', 'Périodicité paiement prime', required=True),

        'afiche': fields.boolean('t'),
        'remb': fields.boolean('t'),

        'state': fields.selection([
            ('draft', "Actif"),
            ('resil', "Resiliation"),
            ('lnoir', "Suspension"),
            ('cancel', "Annuler"),
        ], 'Statut', required=True),

        'a_college': fields.boolean(''),
        'a_histo_police': fields.boolean(''),

        'type_regime': fields.selection(REGIME, 'Régime'),
        'delai_carence': fields.integer('Delai de carence police (jours)'),
    }

    _defaults = {
        'statut_police': 0,
        'state': 'draft',
        'typ_ave': 1,
        'mnt_emi_ave': 0,
        'cod_annul_ave': 0,
        'dt_eff_prime': '1900-01-01 00:00:00',
        'mnt_regl_prime_ave': 0,
        'calc_prime_ave': 0,
        'cod_avenant_initial': 0,
        'num_ave_interne_police': 1,
        'afiche': False,
        'typ_prime': 1,
        'type_prime': '1',
        'periodicite_paiem': '1',
        'repartition_prime': '1',
        'dt_resil_pol': '1900-01-01 00:00:00',
        'affiche_ro': _get_regime_centre,
        'a_college': False,
        'a_histo_police': False,
        'type_regime': _get_default_regime,

    }

    def button_reseau(self, cr, uid, ids, context):
        police = self.browse(cr, uid, ids[0], context=context).id
        print('*****police******')
        print(police)

        reseaux_ids = []

        reseaux = self.pool.get('mcisogem.rata.reseau.police').search(cr, uid, [('police_id', '=', police)])

        for rs in self.pool.get('mcisogem.rata.reseau.police').browse(cr, uid, reseaux, context=context):
            reseaux_ids.append(rs.reseau_id.id)

        ctx7 = (context or {}).copy()
        ctx7['tree_view_ref'] = 'mcisogem_excl_tree'

        return {
            'name': 'liste des reseaux de soins',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'mcisogem.tarif.nego.police',
            'view_id': False,
            'target': 'current',
            'domain': [('reseau_id', 'in', reseaux_ids)],
            'type': 'ir.actions.act_window',
            'context': ctx7,
        }

    def button_inc_garant(self, cr, uid, ids, context):
        police = self.browse(cr, uid, ids[0], context=context).id

        print('*****police******')
        print(police)
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)
        ctx7 = (context or {}).copy()
        ctx7['garant'] = police_data.garant_id.id
        ctx7['police_inc_garant'] = police
        ctx7['aff_benf'] = True
        ctx7['tree_view_ref'] = 'view_benf_incorpo_tree'
        ctx7['form_view_ref'] = 'view_benf_incorpo_form'

        return {
            'name': 'Demande incorporation',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mcisogem.benf_incorpo',
            'view_id': False,
            'target': 'current',
            'domain': [('garant_id', '=', police_data.garant_id.id), ('police_id', '=', police)],
            'type': 'ir.actions.act_window',
            'context': ctx7,

        }

    def button_inc_inter(self, cr, uid, ids, context):
        police = self.browse(cr, uid, ids[0], context=context).id

        print('*****police******')
        print(police)
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)
        ctx7 = (context or {}).copy()
        ctx7['garant'] = police_data.garant_id.id
        ctx7['police'] = police
        ctx7['aff_benf'] = True
        ctx7['tree_view_ref'] = 'view_benf_incorpo_tree'
        ctx7['form_view_ref'] = 'view_benf_incorpo_form'

        return {
            'name': 'Demande incorporation',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mcisogem.benf_incorpo',
            'view_id': False,
            'target': 'current',
            'domain': [('intermediaire_id', '=', police_data.courtier_id.id), ('police_id', '=', police)],
            'type': 'ir.actions.act_window',
            'context': ctx7,

        }

    def button_bareme(self, cr, uid, ids, context):

        police = self.browse(cr, uid, ids[0], context=context).id
        print('*****police******')
        print(police)
        ctx7 = (context or {}).copy()
        ctx7['tree_view_ref'] = 'mcisogem_produit_police_tree'
        ctx7['search_default_group_college_id'] = 1
        ctx7['search_default_group_acte_id'] = 1
        return {
            'name': 'Produit de la police',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'mcisogem.produit.police',
            'view_id': False,
            'target': 'current',
            'domain': [('police_id', '=', police)],
            'type': 'ir.actions.act_window',
            'context': ctx7,
        }

    def onchange_exercice(self, cr, uid, ids, exercice_id, context=None):
        v = {}
        if exercice_id:
            exercice = self.pool.get('mcisogem.exercice').search(cr, uid, [('id', '=', exercice_id)])
            for exercice_data in self.pool.get('mcisogem.exercice').browse(cr, uid, exercice):
                v = {'dt_deb_exercice': exercice_data.date_debut, 'dt_fin_exercice': exercice_data.date_fin,
                     'dt_effet': exercice_data.date_debut, 'dt_expiration': exercice_data.date_fin,
                     'dt_emi_ave': exercice_data.date_debut, 'dt_fin_ave': exercice_data.date_fin}

        return {'value': v}

    def onchange_police(self, cr, uid, ids, police_name, context=None):

        v = {}
        if police_name:
            police = self.pool.get('mcisogem.police').search(cr, uid, [('name', '=', police_name)])
            p_data = self.pool.get('mcisogem.police').browse(cr, uid, police)

            v = {'type_contrat_id': p_data.type_contrat_id, 'mod_recond_id': p_data.mod_recond_id,
                 'num_interne_police': p_data.num_interne_police, 'territoire_id': p_data.territoire_id,
                 'souscripteur_id': p_data.souscripteur_id, 'garant_id': p_data.garant_id,
                 'code_regime': p_data.code_regime, 'courtier_id': p_data.courtier_id,
                 'dt_resil_pol': p_data.dt_resil_pol}

        return {'value': v}

    def button_resilier_police(self, cr, uid, ids, context=None):

        police = self.browse(cr, uid, ids[0], context=context).id
        num_interne = police
        police_table = self.search(cr, uid, [('id', '=', police)])

        police_data = self.browse(cr, uid, police_table)

        ctx = (context or {}).copy()
        ctx['police'] = police
        ctx['num_interne_police'] = num_interne
        ctx['form_view_ref'] = 'view_mcisogem_police_resilier_form'

        return {
            'name': 'Resiliation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mcisogem.histo.resil.police',
            'view_id': False,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def button_delai_carence(self, cr, uid, ids, context=None):
        police_data = self.browse(cr, uid, ids[0])

        ctx = (context or {}).copy()
        ctx['police'] = police_data.id

        form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa',
                                                                      'view_mcisogem_delai_carence_form')[1]
        tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa',
                                                                      'view_mcisogem_delai_carence_tree')[1]

        return {
            'name': 'Delai de Carence',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mcisogem.delai.carence',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'view_id': tree_id,
            'target': 'current',
            'domain': [('police_id', '=', police_data.id)],
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def button_to_lnoire(self, cr, uid, ids, context):
        police = self.browse(cr, uid, ids[0], context=context).id

        police_table = self.search(cr, uid, [('id', '=', police)])

        police_data = self.browse(cr, uid, police_table)

        ctx = (context or {}).copy()
        ctx['police'] = police
        ctx['form_view_ref'] = 'view_mcisogem_liste_noire_form'

        return {
            'name': 'Suspension',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mcisogem.liste.noire',
            'view_id': False,
            'target': 'new',
            'domain': [('police_id', '=', police)],
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def button_to_annuler(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context=context)
        histo = self.pool.get('mcisogem.histo.resil.police')
        context['police'] = data.id
        vals = {}
        vals['police_id'] = data.id
        vals['num_interne_pol'] = data.num_interne_police
        vals['lib_action'] = "Réactivation"
        vals['dt_action'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        if (data.state == 'resil'):
            # super(mcisogem_histo_resil_police , mcisogem_histo_resil_police).create(histo,cr,uid,vals,context)
            histo.create(cr, uid, vals, context)
        self.write(cr, uid, ids, {'state': 'draft', 'dt_resil_pol': '1900-01-01 00:00:00'}, context=context)

        return True

    def button_to_beneficiaire(self, cr, uid, ids, context):
        police = self.browse(cr, uid, ids[0], context=context).id
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)

        ctx = (context or {}).copy()
        ctx['garant'] = police_data.garant_id.id
        ctx['police'] = police_data.id
        ctx['search_default_group_college_id'] = 1
        ctx['date_eff'] = police_data.dt_effet
        ctx['tree_view_ref'] = 'mcisogem_benef_tree'
        ctx['form_view_ref'] = 'view_mcisogem_benef_form'
        form_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_mcisogem_benef_form')[1]
        tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_benef_tree')[1]
        kanban_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_benef_kanban')[1]

        return {
            'name': 'Bénéficiaire',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mcisogem.benef',
            'views': [(tree_id, 'tree'), (form_id, 'form'), (kanban_id, 'kanban')],
            'view_id': tree_id,
            'target': 'current',
            'domain': [('police_id', '=', police)],
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def onchange_souscr(self, cr, uid, ids, souscripteur_id):
        v = {}
        if souscripteur_id:
            souscr = self.pool.get('mcisogem.souscripteur').search(cr, uid, [('id', '=', souscripteur_id)])
            for souscr_data in self.pool.get('mcisogem.souscripteur').browse(cr, uid, souscr):
                v = {'souscripteur_pol': souscr_data.name}
        return {'value': v}

    def create(self, cr, uid, data, context=None):
        data['dt_emi_ave'] = self.onchange_exercice(cr, uid, 0, data['exercice_id'])['value']['dt_emi_ave']
        data['dt_fin_ave'] = self.onchange_exercice(cr, uid, 0, data['exercice_id'])['value']['dt_fin_ave']
        # data['name'] = str(data['name']).upper()


        # on verifie si la periode de la police se trouve dans la periode de l'exercice
        if data['dt_effet'] < data['dt_emi_ave']:
            raise osv.except_osv('Attention',
                                 "La date d'effet de la police doit être incluse dans la période d'exercice")

        if data['dt_effet'] > data['dt_fin_ave']:
            raise osv.except_osv('Attention',
                                 "La date d'effet de la police doit être incluse dans la période d'exercice")

        if data['dt_expiration'] > data['dt_fin_ave']:
            raise osv.except_osv('Attention',
                                 "La date d'expiration de la police doit être incluse dans la période d'exercice")

        if data['dt_expiration'] < data['dt_emi_ave']:
            raise osv.except_osv('Attention',
                                 "La date d'expiration de la police doit être incluse dans la période d'exercice")

        # Recuperation du centre de gestion et de l'utilisateur
        utilisateur_data = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        centre_gestion_data = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, utilisateur_data.code_gest_id.id,
                                                                              context=context)

        # Recuperation de la date de debut et de fin de l'exercice
        cr.execute('select date_debut from mcisogem_exercice where id=%s', (data['exercice_id'],))
        dtdeb = cr.fetchone()[0]

        cr.execute('select date_fin from mcisogem_exercice where id=%s', (data['exercice_id'],))
        dfin = cr.fetchone()[0]

        data['dt_deb_exercice'] = dtdeb
        data['dt_fin_exercice'] = dfin

        # Recuperation du numero interne de police et insertion de la police en base de données
        cr.execute("select id,num_police from mcisogem_numero")

        sql = cr.dictfetchall()
        sql = sql[0]
        if len(sql) > 0:
            # dernier_num = sql['num_police'] + 1

            # data['num_interne_police'] = sql['num_police']
            # data['num_police'] = sql['num_police']
            res = super(mcisogem_police, self).create(cr, uid, data, context)

            # Mise a jour des numeros dans la table des numéros
            # cr.execute("update mcisogem_numero set num_police=%s", (dernier_num,))

            datedujour = datetime.now()  # time.strftime('%y-%m-%d %H:%M:%S', time.localtime())

            # Création de l'exercice de police
            exopolice = {}
            if data['repartition_prime'] == '1':
                exopolice['repartition_prime'] = 1
            else:
                exopolice['repartition_prime'] = 0

            if data['type_prime'] == '1':
                exopolice['type_prime'] = 1
            else:
                exopolice['type_prime'] = 2

            cr.execute("""insert into mcisogem_exercice_police
			(police_id,name,num_interne_police,exercice_id,date_debut_exercice,date_fin_exercice,bl_exercice_clot,tva_oui_non,repartition_prime,type_prime,
			periodicite_paiem_pol,dernier_avenant, create_uid, write_uid, write_date, create_date,
			prime_pol_exercice,cum_mnt_pol,masse_sal_pol,pc_masse_sal_pol,bl_pc_masse_sal_pol,rapport_sp_preced,tot_sinistre_preced,tot_prime_preced,state) values
			(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
			""",
                       (res, data['name'], res, data['exercice_id'], data['dt_deb_exercice'], data['dt_fin_exercice'],
                        False, False, exopolice['repartition_prime'],
                        data['type_prime'],
                        data['periodicite_paiem'], 0,
                        uid, uid, datedujour, datedujour, 0, 0, 0, 0, 0, 0, 0, 0, 'actif'))

            if res:
                # Tentative de recuperation du type avenant AI (Avenant initial)
                if not self.pool.get('mcisogem.type.avenant').search(cr, uid, [('code_type_avenant', '=', 'AI')]):
                    num = res
                    # QUESTION : A QUOI SERT souscripteur_pol
                    cr.execute('select souscripteur_id from mcisogem_police where id=%s', (res,))
                    souscripteur_pol = cr.fetchone()[0]

                    # L'avenant initial n'existe pas on procede a sa creation
                    cr.execute(
                        "INSERT INTO mcisogem_type_avenant (code_type_avenant, name, create_uid, write_uid, create_date, write_date) VALUES (%s, %s, %s, %s, %s, %s)",
                        ('AI', 'Avenant initial', uid, uid, datedujour, datedujour))
                    cr.execute('select id from mcisogem_type_avenant where code_type_avenant=%s', ('AI',))
                    ai = cr.fetchone()[0]

                    cr.execute("""INSERT INTO mcisogem_avenant (code_avenant_initial, type_avenant_id, dt_deb_exercice_pol, dt_fin_exercice_pol,
					 name, mnt_emi_ave, num_ave_interne_police, mnt_regl_prime_ave, calc_prime_ave, police_id, souscripteur_police, state,
					 create_uid, write_uid, create_date, write_date, date_effet_prime, dt_eff_mod_pol,
					  dt_ope_deb_ave,periode_mvmt_du, dt_anul_ave,mnt_echea_paiemt,mnt_quitance_emi,prime_cal_ave,nbre_echea_paiemt,date_annuler,
					  dt_fin_ave,dt_ope_fin_ave, valider, date_effet_police)
					 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s)"""
                               , (
                               0, ai, dtdeb, dfin, 1, 0, 0, 0, 1, res, souscripteur_pol, 'valid', uid, uid, datedujour,
                               datedujour,
                               '1900-01-01 00:00:00', datedujour, dtdeb, datedujour, '1900-01-01 00:00:00', 0, 0, 0, 0,
                               '1900-01-01 00:00:00', dfin, dfin, False, dtdeb))

                else:
                    cr.execute('select id from mcisogem_type_avenant where code_type_avenant=%s', ('AI',))
                    ai = cr.fetchone()[0]

                    # QUESTION A QUOI SERT souscripteur_pol
                    cr.execute('select souscripteur_id from mcisogem_police where id=%s', (res,))
                    souscripteur_pol = cr.fetchone()[0]

                    # Création de l'avenant de la police
                    cr.execute("""INSERT INTO mcisogem_avenant (code_avenant_initial, type_avenant_id, dt_deb_exercice_pol, dt_fin_exercice_pol,
					 name, mnt_emi_ave, num_ave_interne_police, mnt_regl_prime_ave, calc_prime_ave, police_id, souscripteur_police, state,
					  create_uid, write_uid, create_date, write_date, date_effet_prime, dt_eff_mod_pol,
					  dt_ope_deb_ave,periode_mvmt_du, dt_anul_ave,mnt_echea_paiemt,mnt_quitance_emi,prime_cal_ave,nbre_echea_paiemt,date_annuler,
					  dt_fin_ave,dt_ope_fin_ave, valider,date_effet_police)
					 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s)"""
                               , (
                               0, ai, dtdeb, dfin, 1, 0, 0, 0, 1, res, souscripteur_pol, 'valid', uid, uid, datedujour,
                               datedujour,
                               '1900-01-01 00:00:00', datedujour, dtdeb, datedujour, '1900-01-01 00:00:00', 0, 0, 0, 0,
                               '1900-01-01 00:00:00', dfin, dfin, False, dtdeb))

            else:
                raise osv.except_osv('Attention !', "L'avenant initiale n'a pas été crée!")
            return res

        else:
            raise osv.except_osv('Attention !', "Aucun numéro n'a été créé !")

    def button_to_histo_police(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()

        police = self.browse(cr, uid, ids[0], context=context).id
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)

        ctx['police'] = police
        ctx['tree_view_ref'] = 'mcisogem_histo_police_tree'
        ctx['form_view_ref'] = 'view_mcisogem_histo_police_form'
        if ctx['police']:
            return {
                'name': 'Historique police',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mcisogem.histo.police',
                'view_id': False,
                'target': 'current',
                'type': 'ir.actions.act_window',
                'domain': [('name', '=', police)],
                'context': ctx,
                'nodestroy': True,
            }
        else:
            return True

    def button_to_histo_prime(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()

        police = self.browse(cr, uid, ids[0], context=context).id
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)

        ctx['police'] = self.browse(cr, uid, ids[0], context=context).id
        ctx['tree_view_ref'] = 'mcisogem_histo_prime_tree_1'
        ctx['form_view_ref'] = 'view_mcisogem_histo_prime_form'
        if ctx['police']:
            return {
                'name': 'Historique prime',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mcisogem.histo.prime',
                'view_id': False,
                'target': 'current',
                'type': 'ir.actions.act_window',
                'domain': [('police_id', '=', police_data.id)],
                'context': ctx,
                'nodestroy': True,
            }
        else:
            return True

    def button_to_bareme_pol(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()

        police = self.browse(cr, uid, ids[0], context=context).id
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)

        ctx['police'] = self.browse(cr, uid, ids[0], context=context).id
        ctx['tree_view_ref'] = 'mcisogem_produit_police_tree'
        ctx['form_view_ref'] = 'mcisogem_produit_police_form'
        ctx['search_default_group_college_id'] = 1
        ctx['search_default_group_acte_id'] = 1

        if ctx['police']:
            return {
                'name': 'Produit-Police',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mcisogem.produit.police',
                'view_id': False,
                'target': 'current',
                'type': 'ir.actions.act_window',
                'domain': [('police_id', '=', police_data.id)],
                'context': ctx,
                'nodestroy': True,
            }
        else:
            return True

    def button_to_exercice_pol(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()

        police = self.browse(cr, uid, ids[0], context=context).id
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)

        ctx['police'] = self.browse(cr, uid, ids[0], context=context).id
        ctx['tree_view_ref'] = 'mcisogem_exercice_police_tree'
        ctx['form_view_ref'] = 'view_mcisogem_exercice_police_form'
        if ctx['police']:
            return {
                'name': 'Exercice police',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mcisogem.exercice.police',
                'view_id': False,
                'target': 'current',
                'type': 'ir.actions.act_window',
                'domain': [('police_id', '=', police_data.id)],
                'context': ctx,
                'nodestroy': True,
            }
        else:
            return True

    def button_to_avenant(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()

        police = self.browse(cr, uid, ids[0], context=context).id
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)

        ctx['police'] = self.browse(cr, uid, ids[0], context=context).id
        ctx['tree_view_ref'] = 'mcisogem_avenant_tree'
        ctx['form_view_ref'] = 'view_mcisogem_avenant2_form'
        if ctx['police']:
            return {
                'name': 'Avenant',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mcisogem.avenant',
                'view_id': False,
                'target': 'current',
                'type': 'ir.actions.act_window',
                'domain': [('police_id', '=', police_data.id)],
                'context': ctx,
                'nodestroy': True,
            }
        else:
            return True

    def button_to_college(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()

        ctx['police'] = self.browse(cr, uid, ids[0], context=context).id
        ctx['tree_view_ref'] = 'mcisogem_college_tree'
        ctx['form_view_ref'] = 'view_mcisogem_college_form'

        form_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'view_mcisogem_college_form')[1]
        tree_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa', 'mcisogem_college_tree')[
            1]

        return {
            'name': 'Collège',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mcisogem.college',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'view_id': tree_id,
            'target': 'current',
            'domain': [('police_id', '=', ctx['police'])],
            'type': 'ir.actions.act_window',
            'context': ctx,
        }


class mcisogem_police_complementaire_beneficiaire(osv.osv):
    _name = "mcisogem.police.complementaire.beneficiaire"
    _description = 'Police complementaire'

    _columns = {
        'beneficiaire_id': fields.many2one('mcisogem.benef', 'Bénéficiaire'),
        'police_id': fields.many2one('mcisogem.police', 'Police'),
        'college_id': fields.many2one('mcisogem.college', 'Collège'),
        'niveau': fields.selection(
            [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
             ('9', '9')], 'Niveau', required=True),
    }


class mcisogem_histo_police(osv.osv):
    _name = "mcisogem.histo.police"
    _description = 'Historique de police'

    _columns = {
        'name': fields.many2one('mcisogem.police', 'Police', required=True, readonly=True),
        'dt_eff_histo_pol': fields.date('Date éffet histo police', required=True),
        'dt_eff_mod_pol': fields.date('Date effet police', readonly=True),
        'num_avenant': fields.integer('Numéro avenant', readonly=True),
        'souscripteur': fields.char('Souscripteur', readonly=True),
        'garant': fields.char('Garant', readonly=True),
        'intermediaire': fields.char('Assur. intermédiaire', readonly=True),
        'num_police': fields.integer('Numéro interne police', readonly=True),
        'code_type_contrat': fields.char('Type de contrat', readonly=True),
        'code_regroupe_territoire': fields.char('Térritorialite', readonly=True),
        'regime_id': fields.many2one('mcisogem.regime', 'Type de remboursement', readonly=True),
        'num_police_assur': fields.char('Numéro police assureur', readonly=True),

        # Informations liees au beneficiaire
        'bl_ouvert_assur': fields.boolean("Couverture assuré"),
        'bl_ouvert_conj': fields.boolean('Couverture conjoint(e)'),
        'bl_ouvert_conj_2': fields.boolean('Couverture Autre conjoint(e)'),
        'bl_ouvert_enfant': fields.boolean('Couverture enfant'),
        'bl_ouvert_enfant_2': fields.boolean('Couverture autre enfant'),
        'bl_ouvert_parent': fields.boolean('Couverture parent'),
        'bl_ouvert_grand_parent': fields.boolean('Couverture Grand-Parent'),
        'bl_ouvert_autre': fields.boolean('Couverture autre'),

        'limite_age_pol': fields.integer('Age Minimum'),
        'age_majorite_pol': fields.integer('Age Limite'),
        'age_majorite_eleve_pol': fields.integer('Age Majorité(élève)'),

        'mod_calcul_age': fields.selection([('1', 'Date anniversaire'), ('2', 'Année')], "Mode de calcul de l’age",
                                           required=True),

        # college
        'college_ids': fields.many2many('mcisogem.college', 'college_rel', 'name', 'code_college', 'Collèges'),
        'code_college': fields.many2one('mcisogem.college', 'Collège', required=False),

        'tranche_age_ids': fields.many2many('mcisogem.tranche.age', 'tranche_age_rel', 'name', 'fin_tranche',
                                            'Tranche d\'âge'),
        'code_tranche_age': fields.many2one('mcisogem.tranche.age', 'Tranche d\'âge', required=False),

        # Prestations autorisees
        'mnt_plfd_pol': fields.integer('Police', required=True),
        'mnt_plfd_col': fields.integer('Collège'),
        'mnt_plfd_ass': fields.integer('Assure principal (A)', required=True),
        'mnt_plfd_conj': fields.integer('Conjoint (C)', required=True),
        'mnt_plfd_enf': fields.integer('Enfant (E)', required=True),
        'mnt_plfd_dep': fields.integer('Dependants '),
        'mnt_plfd_fam': fields.integer('Famille', required=True),
        'mnt_plfd_tenf': fields.integer('Tous les enfants'),
        'mnt_plfd_parent': fields.integer('Parents'),
        'mnt_plfd_autre': fields.integer('Autres'),
        'mnt_plfd_parent_autre': fields.integer('Autre parent (X)'),

        'mnt_plfd_gen': fields.integer('Géniteur (G)'),
        'mnt_plfd_aut_conj': fields.integer('Autre conjointe (D)'),
        'mnt_plfd_enf_sup': fields.integer('Enfant supplémentaire (K)'),

        'mnt_plfd_territoire': fields.integer('Térritoire'),
        'statut_ids': fields.many2many('mcisogem.stat.benef', 'mcisogem__histo_police_stat_benef_rel', 'id_hp', 'id_s',
                                       'Statuts', required=True),
        'bl_carmed_exclusif': fields.integer(''),
        'code_tranche': fields.integer(''),
        'plf_an_pol': fields.integer(''),

        'affichage_ta': fields.integer('affichage_ta'),
        'affichage_college': fields.integer('affichage_college'),
        'affichage_col': fields.integer('affichage_col'),
        'affichage_tran': fields.integer('affichage_tran'),
    }

    def _get_context(self, cr, uid, context):
        context = context or {}
        return context.get('police')

    _defaults = {
        'name': _get_context,
        'bl_carmed_exclusif': 0,
        'plf_an_pol': 0,
        'code_tranche': 0,
        'affichage_ta': 0,
        'affichage_col': 0,
        'affichage_tran': 0,
        'affichage_college': 0,
        'mod_calcul_age': '1',
    }

    def button_to_create_histo(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()

        police = self.browse(cr, uid, ids[0], context=context).id
        police_table = self.search(cr, uid, [('id', '=', police)])
        police_data = self.browse(cr, uid, police_table)

        ctx['police'] = self.browse(cr, uid, ids[0], context=context).id
        ctx['form_view_ref'] = 'view_mcisogem_histo_police_form'
        if ctx['police']:
            return {
                'name': 'Historique police',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mcisogem.histo.police',
                'view_id': False,
                'target': 'new',
                'type': 'ir.actions.act_window',
                'domain': [('name', '=', police_data.id)],
                'context': ctx,
                'nodestroy': True,
                'res_id': ctx['police'],
            }
        else:
            return True

    def onchange_police(self, cr, uid, ids, name, context=None):

        if not name:
            return {'value': {'police_id': False}}
        else:
            les_cols = []
            d = {}
            obj_police_data = self.pool.get('mcisogem.police').browse(cr, uid, name, context=context)

            cr.execute('select id from mcisogem_college where police_id=%s', (name,))
            col_ids = cr.fetchall()

            for col in col_ids:
                les_cols.append(col[0])

            d = {'college_ids': [('id', 'in', les_cols)]}

            cr.execute('select souscripteur_id from mcisogem_police where id=%s', (name,))
            souscr = cr.fetchone()[0]
            cr.execute('select name from mcisogem_souscripteur where id=%s', (souscr,))
            souscr_name = cr.fetchone()[0]

            cr.execute('select garant_id from mcisogem_police where id=%s', (name,))
            garant_id = cr.fetchone()[0]
            cr.execute('select name from mcisogem_garant where id=%s', (garant_id,))
            garant = cr.fetchone()[0]

            cr.execute('select courtier_id from mcisogem_police where id=%s', (name,))
            courtier_id = cr.fetchone()[0]
            cr.execute('select name from mcisogem_courtier where id=%s', (courtier_id,))
            inter = cr.fetchone()[0]

            cr.execute('select type_contrat_id from mcisogem_police where id=%s', (name,))
            type_id = cr.fetchone()[0]
            cr.execute('select name from mcisogem_type_contrat where id=%s', (type_id,))
            typ = cr.fetchone()[0]

            cr.execute('select territoire_id from mcisogem_police where id=%s', (name,))
            ter_id = cr.fetchone()[0]
            cr.execute('select name from mcisogem_territoire where id=%s', (ter_id,))
            ter = cr.fetchone()[0]

            affichage = 0
            # Police par statut de bénéficiaire
            if obj_police_data.type_prime == '1':
                affichage = 0
            else:
                # Police par tranche d'age
                affichage = 1

            vals = {
                'num_police': obj_police_data.id,
                'num_police_assur': obj_police_data.num_police_assur,
                'dt_eff_mod_pol': obj_police_data.dt_deb_exercice,
                'dt_eff_histo_pol': obj_police_data.dt_deb_exercice,
                'num_avenant': 1,
                'souscripteur': souscr_name,
                'garant': garant,
                'intermediaire': inter,
                'code_type_contrat': typ,
                'code_regroupe_territoire': ter,
                'affichage_ta': affichage,
                'regime_id': obj_police_data.code_regime.id}
            return {'value': vals, 'domain': d}

    def unlink(self, cr, uid, ids, context=None):

        histo_polices_lies = self.pool.get('mcisogem.histo.police').search_count(cr, uid, [('name', '=', ids[0])])

        if histo_polices_lies > 0:

            raise osv.except_osv('Attention !', 'Cette police ne peut être supprimée.')

        else:

            return super(mcisogem_histo_police, self).unlink(cr, uid, ids, context=context)

    def create(self, cr, uid, data, context=None):

        dernier_id = 0

        name = self._get_context(cr, uid, context)
        cr.execute('select souscripteur_id from mcisogem_police where id=%s', (name,))
        souscr = cr.fetchone()[0]

        cr.execute('select type_prime from mcisogem_police where id=%s', (name,))
        type_prime = cr.fetchone()[0]

        cr.execute('select name from mcisogem_souscripteur where id=%s', (souscr,))
        data['souscripteur'] = cr.fetchone()[0]

        cr.execute('select dt_deb_exercice from mcisogem_police where id=%s', (name,))
        data['dt_eff_mod_pol'] = cr.fetchone()[0]

        cr.execute('select garant_id from mcisogem_police where id=%s', (name,))
        garant_id = cr.fetchone()[0]
        cr.execute('select name from mcisogem_garant where id=%s', (garant_id,))
        data['garant'] = cr.fetchone()[0]

        cr.execute('select courtier_id from mcisogem_police where id=%s', (name,))
        courtier_id = cr.fetchone()[0]
        cr.execute('select name from mcisogem_courtier where id=%s', (courtier_id,))
        data['intermediaire'] = cr.fetchone()[0]

        cr.execute('select type_contrat_id from mcisogem_police where id=%s', (name,))
        type_id = cr.fetchone()[0]
        cr.execute('select name from mcisogem_type_contrat where id=%s', (type_id,))
        data['code_type_contrat'] = cr.fetchone()[0]

        cr.execute('select territoire_id from mcisogem_police where id=%s', (name,))
        ter_id = cr.fetchone()[0]
        cr.execute('select name from mcisogem_territoire where id=%s', (ter_id,))
        data['code_regroupe_territoire'] = cr.fetchone()[0]

        cr.execute('select id from mcisogem_police where id=%s', (name,))
        data['num_police'] = cr.fetchone()[0]

        # Recuperation du numero avenant de la police
        cr.execute("select id from mcisogem_avenant where police_id=%s order by id desc", (name,))
        num_ave = cr.fetchone()[0]

        data['affichage_ta'] = 0
        data['affichage_col'] = 1
        data['affichage_college'] = 1

        compteur_create = 0
        compteur_data = 0

        obj_police_data = self.pool.get('mcisogem.police').browse(cr, uid, data['num_police'])
        data['regime_id'] = obj_police_data.code_regime.id

        self.pool.get('mcisogem.police').write(cr, uid, data['num_police'], {'a_histo_police': True}, context=context)

        data['num_avenant'] = 1

        # Test pour voir si il s'agit d'une police par tranche d'age ou statut de bénéficiaire
        if type_prime == '2':
            # Police par tranche d'age
            # Parcours des colleges puis des tranches d'age
            data['affichage_tran'] = 1

            if len(data['college_ids'][0][2]) and len(data['tranche_age_ids'][0][2]) > 0:

                for col in data['college_ids'][0][2]:

                    for tr in data['tranche_age_ids'][0][2]:

                        compteur_data = compteur_data + 1
                        # Insertion des données en base
                        data['code_college'] = col
                        data['code_tranche_age'] = tr

                        cr.execute(
                            "select * from mcisogem_histo_police where num_police=%s and dt_eff_histo_pol>=%s and code_college=%s and code_tranche_age=%s",
                            (data['num_police'], data['dt_eff_histo_pol'], col, tr))

                        if len(cr.dictfetchall()) == 0:
                            compteur_create = compteur_create + 1
                            dernier_id = super(mcisogem_histo_police, self).create(cr, uid, data, context)
                            cr.execute("update mcisogem_histo_police set num_avenant =%s where id=%s",
                                       (num_ave, dernier_id))

                if compteur_create == 0:
                    raise osv.except_osv('Attention !', "la date d'effet du nouvel historique de police doit être !")
                    return False
                else:
                    return dernier_id
                    """if compteur_create == compteur_data:
                        return dernier_id
                    else:
                        raise osv.except_osv('Attention !', "Erreur duplication lors de l'addition de l'enregistrement. " + str(compteur_create) +  " ligne(s) crée(s) !", (compteur_create,))
                        return dernier_id"""
            else:
                raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un collège et une tranche d'age !")
                return False

        else:
            # Police par statut de bénéficiaire
            # Parcours des collèges
            data['affichage_tran'] = 0
            if len(data['college_ids'][0][2]) > 0:
                for col in data['college_ids'][0][2]:
                    compteur_data = compteur_data + 1
                    data['code_college'] = col
                    cr.execute(
                        "select * from mcisogem_histo_police where num_police=%s and dt_eff_histo_pol>=%s and code_college=%s",
                        (data['num_police'], data['dt_eff_histo_pol'], col))
                    if len(cr.dictfetchall()) == 0:
                        compteur_create = compteur_create + 1
                        dernier_id = super(mcisogem_histo_police, self).create(cr, uid, data, context)
                        cr.execute("update mcisogem_histo_police set num_avenant =%s where id=%s",
                                   (num_ave, dernier_id))

                if compteur_create == 0:
                    raise osv.except_osv('Attention !', "Cet historique de police existe déjà !")
                    return False
                else:
                    return dernier_id
                    """if compteur_create == compteur_data:
                        return dernier_id
                    else:
                        raise osv.except_osv('Attention !', "Erreur duplication lors de l'addition de l'enregistrement. " + str(compteur_create) + " ligne(s) crée(s) !")
                        return dernier_id"""
            else:
                raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un collège !")
                return False


class mcisogem_liste_noire(osv.osv):
    _name = "mcisogem.liste.noire"
    _description = 'Liste noire'

    def _get_police(self, cr, uid, context):
        return context['police']

    def _get_etat_police(self, cr, uid, context):
        police = self.pool.get('mcisogem.police').search(cr, uid, [('id', '=', self._get_police(cr, uid, context))])
        if self.pool.get('mcisogem.police').browse(cr, uid, police).state == 'lnoir':
            return True
        else:
            return False

    _columns = {
        'police_id': fields.many2one('mcisogem.police', 'Police', required=True),
        'dt_eff': fields.date('Date effet'),
        'dt_levee': fields.date('Date levee'),
        'motif_suspen_id': fields.many2one('mcisogem.motif.suspen', 'Motif'),
        'actif': fields.boolean('Etat'),
    }

    def button_liste_noire(self, cr, uid, ids, context=None):
        print('OK')

    def create(self, cr, uid, vals, context):
        data = self.browse(cr, uid, context=context)
        vals['police_id'] = context['police']
        police = self.pool.get('mcisogem.police').search(cr, uid, [('id', '=', vals['police_id'])])
        police_data = self.pool.get('mcisogem.police').browse(cr, uid, police)

        if (police_data.state == 'lnoir'):
            vals['actif'] = False
            if (vals['dt_levee'] == False):
                raise osv.except_osv('Attention !', 'Vous n\'avez pas saisi la date de levée ')
                return false
            self.pool.get('mcisogem.police').write(cr, uid, police_data.ids, {'state': 'draft'}, context=context)
        else:
            vals['actif'] = True
            vals['dt_effet'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.pool.get('mcisogem.police').write(cr, uid, police_data.ids, {'state': 'lnoir'}, context=context)

        return super(mcisogem_liste_noire, self).create(cr, uid, vals, context)

    _defaults = {
        'actif': _get_etat_police,
        'police_id': _get_police,
    }


class mcisogem_exercice_police(osv.osv):
    _name = "mcisogem.exercice.police"
    _description = 'Exercice de la police'

    _columns = {
        'police_id': fields.many2one('mcisogem.police', 'Police', required=True),
        'num_interne_police': fields.integer('num_police', required=True),
        'name': fields.char(''),
        'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', required=True),
        'date_debut_exercice': fields.date('Date de début', readonly=True),
        'date_fin_exercice': fields.date('Date de fin', readonly=True),
        'bl_exercice_clot': fields.boolean('Cloturé'),
        'prime_pol_exercice': fields.integer('prime_pol_exercice'),
        'dernier_avenant': fields.integer('dernier_avenant'),
        'cum_mnt_pol': fields.integer('cum_mnt_pol'),
        'typ_prime': fields.integer('typ_prime'),
        'masse_sal_pol': fields.integer('masse_sal_pol'),
        'pc_masse_sal_pol': fields.integer('pc_masse_sal_pol'),
        'bl_pc_masse_sal_pol': fields.integer('bl_pc_masse_sal_pol'),
        # 'periodicite_paiem_pol': fields.selection([(1, 'Annuelle'), (2, 'Semestrielle'), (3, 'Trimestrielle'), (4, 'Bimensuelle'), (5, 'Mensuelle')], 'Périodicité paiement prime'),
        'periodicite_paiem_pol': fields.many2one('mcisogem.unite.temps', 'Périodicité paiement prime', required=True),

        'rapport_sp_preced': fields.integer('rapport_sp_preced'),
        'tot_sinistre_preced': fields.integer('tot_sinistre_preced'),
        'tot_prime_preced': fields.integer('tot_prime_preced'),
        'cod_sup': fields.char('cod_sup'),
        'repartition_prime': fields.selection([(0, 'Jour'), (1, 'Mois')], 'Repartition prime'),
        'tva_oui_non': fields.boolean('Tva'),
        'imputation_accessoires': fields.integer('imputation_accessoires'),
        'imputation_acc_cie': fields.integer('imputation_acc_cie'),
        'imputation_acc_courtier': fields.integer('imputation_acc_courtier'),
        'type_prime': fields.selection([(1, 'Statut bénéficiaire'), (2, 'Tranche d\'age')], 'Type prime'),
        'state': fields.selection([
            ('draft', "Brouillon"),
            ('actif', "Actif"),
            ('clot', "Cloturé"),
        ], 'Statut', readonly=True),
    }

    _sql_constraints = [('unique_exercice_police',
                         'unique(police_id , num_interne_police, date_debut_exercice, date_fin_exercice)',
                         "Cet exercice police existe déjà !"), ]

    def _get_context(self, cr, uid, context):
        context = context or {}
        return context.get('police')

    def button_activer_exercice_police(self, cr, uid, ids, context=None):

        nbre_exercice_actif = self.search_count(cr, uid, [('state', '=', 'actif'), ('police_id', '=', ids[0])])
        exercice = self.browse(cr, uid, ids[0]).exercice_id.id

        date_fin_exercice = self.pool.get('mcisogem.exercice').browse(cr, uid, exercice).date_fin

        if nbre_exercice_actif > 0:
            raise osv.except_osv('Attention', "Un autre exercice de police est en cours , veuillez le clôturer d'abord")

        return self.write(cr, uid, ids, {'state': 'actif', 'date_fin_exercice': date_fin_exercice}, context=context)

    def button_cloturer_exercice_police(self, cr, uid, ids, context=None):

        return self.write(cr, uid, ids,
                          {'state': 'clot', 'date_fin_exercice': time.strftime("%Y-%m-%d", time.localtime())},
                          context=context)

    _defaults = {
        'police_id': _get_context,
        'type_prime': 1,
        'repartition_prime': 1,
        # 'periodicite_paiem_pol': 1,
        'prime_pol_exercice': 0,
        'dernier_avenant': 0,
        'cum_mnt_pol': 0,
        'masse_sal_pol': 0,
        'pc_masse_sal_pol': 0,
        'bl_pc_masse_sal_pol': 0,
        'rapport_sp_preced': 0,
        'tot_sinistre_preced': 0,
        'tot_prime_preced': 0,
        'state': 'draft',
    }

    def onchange_police(self, cr, uid, ids, police_id, context=None):
        if not police_id:
            return False
        else:
            # Recuperation de l'ancien exercice de police
            cr.execute("select * from mcisogem_exercice_police where police_id=%s order by id desc", (police_id,))
            lesexopolice = cr.dictfetchall()
            if len(lesexopolice) > 0:
                exopolice = lesexopolice[0]
                return {'value': {'repartition_prime': exopolice['repartition_prime'],
                                  'type_prime': exopolice['type_prime'],
                                  'periodicite_paiem_pol': exopolice['periodicite_paiem_pol']}}
            else:
                return False

    def onchange_exercice(self, cr, uid, ids, exercice_id, context=None):
        # Recuperation de l'exercice
        if not exercice_id:
            return {'value': {'date_debut_exercice': False, 'date_fin_exercice': False}}
        else:
            cr.execute("select * from mcisogem_exercice where id=%s", (exercice_id,))
            lesexo = cr.dictfetchall()
            print lesexo
            exo = lesexo[0]
            return {'value': {'date_debut_exercice': exo['date_debut'], 'date_fin_exercice': exo['date_fin']}}

    def create(self, cr, uid, vals, context=None):

        # QUESTION : LA CREATION D'UN NOUVEL EXERCICE DE POLICE IMPLIQUE T'ELLE LA CREATION D'UN NOUVEL AVENANT ?
        cr.execute("select * from mcisogem_exercice where id=%s", (vals['exercice_id'],))
        lesexo = cr.dictfetchall()
        exo = lesexo[0]

        vals['date_debut_exercice'] = exo['date_debut']
        vals['date_fin_exercice'] = exo['date_fin']
        vals['periodicite_paiem_pol'] = self.onchange_police(cr, uid, 1, context.get('police'))['value'][
            'periodicite_paiem_pol']
        # Recuperation du numero interne de la police
        cr.execute("select num_interne_police, name from mcisogem_police where id=%s",
                   (self._get_context(cr, uid, context),))
        content = cr.dictfetchall()[0]

        vals['num_interne_police'] = content['num_interne_police']
        vals['name'] = content['name']

        return super(mcisogem_exercice_police, self).create(cr, uid, vals, context=context)

    # histo_prime


class mcisogem_histo_prime(osv.osv):
    _name = "mcisogem.histo.prime"
    _description = 'Historique de la prime'

    _columns = {
        'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
        'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
        'name': fields.char(''),
        'college_id': fields.many2one('mcisogem.college', 'College', required=False),
        'statut_benef_id': fields.many2one('mcisogem.stat.benef', 'Statut bénéficiaire', required=False),
        'dt_eff_mod_prime': fields.date("Date d'effet", readonly=False, required=True),
        'num_avenant': fields.integer('Numéro avenant', readonly=True),
        'dt_echea_pol': fields.date('Date écheance'),
        'cout_d_acte': fields.integer('cout d\'acte', required=False),
        'taxe_sur_prime': fields.integer('taxe sur prime', required=False),
        'taxe_sur_comm': fields.integer('taxe sur_comm', required=False),
        'prim_pol': fields.integer('prim pol', required=False),
        'prim_col': fields.integer('prim_col', required=False),
        'prim_fam': fields.integer('prim_fam', required=False),
        'prim_assure': fields.integer('Prime assuré', required=False),
        'prim_conj': fields.integer('prim_conj', required=False),
        'prim_enfant': fields.integer('prim_enfant', required=False),
        'masse_sal_pol': fields.integer('masse_sal_pol', required=False),
        'pc_sal_prime': fields.integer('pc_sal_prime', required=False),
        'dt_prem_ech': fields.date('dt_prem_ech', readonly=True, required=False),
        'num_police': fields.integer('Numero interne police', readonly=True, required=False),

        'cod_college_ids': fields.many2many('mcisogem.college',
                                            'mcisogem_histo_prime_college_rel',
                                            'college_temp_id',
                                            'code_college', 'Collèges', required=False),

        'cod_statut_benef_ids': fields.many2many('mcisogem.histo.prime.stat.benef.temp',
                                                 'mcisogem_histo_prime_stat_benef_temp_rel',
                                                 'stat_benef_temp_id',
                                                 'cod_statut_benef', 'Statuts de bénéficiaire', required=False),

        'bl_pc_sal_prime': fields.integer('bl_pc_sal_prime', required=False),
        'bl_cout_act': fields.integer('bl_cout_act', required=False),
        'type_prime': fields.integer('type_prime', required=False),
        'mode_calcul': fields.integer('mode_calcul', required=False),
        'mode_encaissement': fields.integer('mode_encaissement', required=False),
        'taux_majo_prime': fields.integer('taux_majo_prime', readonly=True, required=False),
        'cout_d_acte_courtier': fields.integer('cout_d_acte_courtier', readonly=True, required=False),
        'bl_cout_d_acte_courtier': fields.integer('bl_cout_d_acte_courtier', readonly=True, required=False),
        'cout_d_acte_assur': fields.integer('cout_d_acte_assur', readonly=True, required=False),
        'bl_cout_d_acte_assur': fields.integer('bl_cout_d_acte_assur', readonly=True, required=False),
        'taxe_acc_nostro': fields.integer('taxe_acc_nostro', readonly=True, required=False),
        'taxe_acc_courtier': fields.integer('taxe_acc_courtier', readonly=True, required=False),
        'taxe_acc_assureur': fields.integer('taxe_acc_assureur', readonly=True, required=False),
        'bl_taxe_acc_nostro': fields.integer('bl_taxe_acc_nostro', readonly=True, required=False),
        'bl_taxe_acc_courtier': fields.integer('t', readonly=True, required=False),
        'bl_taxe_acc_assureur': fields.integer('t', readonly=True, required=False),
        'bl_taxe_sur_prime': fields.integer('t', readonly=True, required=False),
        'bl_taxe_sur_comm': fields.integer('t', readonly=True, required=False),
        'bl_cout_d_acte': fields.integer('t', readonly=True, required=False),
        'prime_reassur': fields.integer('t', readonly=True, required=False),
        'bl_prime_reassur': fields.integer('t', readonly=True, required=False),
        'comm_reassur': fields.integer('t', readonly=True, required=False),
        'taxe_sur_prime_reassur': fields.integer('t', readonly=True, required=False),
        'bl_taxe_sur_prime_reassur': fields.integer('t', readonly=True, required=False),
        'taxe_sur_comm_reassur': fields.integer('t', readonly=True, required=False),
        'bl_taxe_sur_comm_reassur': fields.integer('t', readonly=True, required=False),
        'prime_parent': fields.integer('t', readonly=True, required=False),
        'prime_autre': fields.integer('t', readonly=True, required=False),
        'prime_sida': fields.integer('Prime SIDA', required=False),
        'prime_autre': fields.integer('t', readonly=True, required=False),
        'repartition_prime': fields.integer('t', readonly=True, required=False),
        'prime_mois_exercice': fields.many2one('mcisogem.unite.temps', 'Périodicité paiement prime', required=True),
        'tva_oui_non': fields.integer('t', readonly=True, required=False),
        'code_tranche_age': fields.many2one('mcisogem.tranche.age', 'Tranche d\'age', required=False),

        'cod_tranche_age_ids': fields.many2many('mcisogem.histo.prime.tranche.age.temp',
                                                'mcisogem_histo_prime_tranche_age_temp_rel',
                                                'tranche_age_temp_id',
                                                'tranche_age', 'Choix des tranches d\'age', required=False),

        'budget_sida': fields.integer('Budget sida', required=False),
        'budget_simple': fields.integer('Budget sans sida', required=False),
        'budget_ttc': fields.boolean('Montant TTC', required=False),
        'mode_prime': fields.integer('t', readonly=True, required=False),

        'affiche_tab_benef': fields.integer('affiche tab benef', required=False),
        'affiche_tab_tranche': fields.integer('affiche tab tranche', required=False),
        'affiche_budget': fields.integer('affiche budget', required=False),
        'affiche_tab_college': fields.integer('affiche college', required=False),
        'modification': fields.integer('Modification', required=False),
        'modification_tranche': fields.integer('Modification Tranche', required=False),
        'modification_benef': fields.integer('Modification benef', required=False),
    }

    _order = 'statut_benef_id ASC'

    def _get_context(self, cr, uid, context):
        context = context or {}
        return context.get('police')

    def _get_police_date_fin(self, cr, uid, context):
        police_id = context.get('police')
        s_police = self.pool.get('mcisogem.police').search(cr, uid, [('id', '=', police_id)])
        police_data = self.pool.get('mcisogem.police').browse(cr, uid, s_police)
        return police_data.dt_fin_exercice

    def _get_assur(self, cr, uid, context):
        context = context or {}
        pol = context.get('police')
        cr.execute('select garant_id from mcisogem_police where id=%s', (pol,))
        val = cr.fetchone()[0]
        return val

    _defaults = {
        'police_id': _get_context,
        'garant_id': _get_assur,
        'dt_echea_pol': _get_police_date_fin,
        'prime_mois_exercice': 1,
        'cout_d_acte': 0,
        'taxe_sur_prime': 0,
        'taxe_sur_comm': 0,
        'prim_pol': 0,
        'prim_col': 0,
        'prim_conj': 0,
        'prim_enfant': 0,
        'prim_fam': 0,
        'masse_sal_pol': 0,
        'pc_sal_prime': 0,
        'dt_prem_ech': '1900-01-01 00:00:00',
        'bl_pc_sal_prime': 0,
        'bl_cout_act': 0,
        'mode_encaissement': 1,
        'taux_majo_prime': 0,
        'cout_d_acte_courtier': 0,
        'bl_cout_d_acte_courtier': 0,
        'cout_d_acte_assur': 0,
        'bl_cout_d_acte_assur': 0,
        'taxe_acc_nostro': 0,
        'taxe_acc_courtier': 0,
        'taxe_acc_assureur': 0,
        'bl_taxe_acc_nostro': 0,
        'bl_taxe_acc_courtier': 0,
        'bl_taxe_acc_assureur': 0,
        'bl_taxe_sur_prime': 0,
        'bl_taxe_sur_comm': 0,
        'bl_cout_d_acte': 0,
        'prime_reassur': 0,
        'bl_prime_reassur': 0,
        'comm_reassur': 0,
        'taxe_sur_prime_reassur': 0,
        'bl_taxe_sur_prime_reassur': 0,
        'taxe_sur_comm_reassur': 0,
        'bl_taxe_sur_comm_reassur': 0,
        'prime_parent': 0,
        'prime_autre': 0,
        'affiche_tab_college': 0,
        'affiche_tab_benef': 0,
        'affiche_tab_tranche': 0,
        'affiche_budget': 0,
        'modification': 0,
        'modification_tranche': 0,
        'modification_benef': 0,
    }

    def onchange_garant(self, cr, uid, ids, garant_id, context=None):
        if not type_avenant_id:
            return False
        else:
            obj_police_data = self.pool.get('mcisogem.police').browse(cr, uid, garant_id, context=context)
            return {'value': {'affiche_budget': 0, 'affiche_tab_tranche': 0, 'affiche_tab_benef': 0,
                              'affiche_tab_college': 0, 'police_id': 0}}

    def onchange_police(self, cr, uid, ids, police_id, context=None):

        tabcollege = []
        tabtrancheage = []
        tabstatutbeneficiare = []

        # raise osv.except_osv('A' , police_id)
        exp = []
        if not police_id:
            return {'value': {'police_id': False}}
        else:

            obj_police_data = self.pool.get('mcisogem.police').browse(cr, uid, police_id)

            les_h = self.pool.get('mcisogem.histo.police').search(cr, uid, [('name', '=', police_id)])
            les_colleges = []

            for h in self.pool.get('mcisogem.histo.police').browse(cr, uid, les_h):
                les_colleges.append(h.id)

            # Tentative de recuperation de l'exercice de police de la police sélectionnée
            cr.execute("select * from mcisogem_exercice_police where police_id=%s order by id desc", (police_id,))
            lesexospolice = cr.dictfetchall()

            if len(lesexospolice) > 0:
                # Recuperation de la date d'effet de la police
                dt_eff_mod_prime = lesexospolice[0]['date_debut_exercice']
                # On vide la table college tampon
                # cr.execute("delete from mcisogem_histo_prime_college_temp where write_uid=%s", (uid,))
                # Recuperation de la police



                cr.execute('select id from mcisogem_histo_police where name=%s order by id desc', (police_id,))
                leshistopolices = cr.dictfetchall()

                if len(leshistopolices) == 0:
                    affiche_budget = 0
                    affiche_tab_tranche = 0
                    affiche_tab_benef = 0
                    raise osv.except_osv('Attention !',
                                         "Aucun historique de police n'a été trouvée pour cette police. Veuillez procéder à la création de l'historique de police !")
                    return {'value': {'police_id': False}}
                # else:

                # for un_histo in leshistopolices:

                # 		# Recuperation des colleges de la police
                # 		cr.execute('select c.id as col,crel.code_college as codc  from college_rel crel,mcisogem_college c where crel.code_college=c.id and crel.name=%s', (un_histo['id'],))
                # 		vals = cr.dictfetchall()

                # 		# Insertion des colleges recuperés dans la table temporaire
                # 		for elt in vals:
                # 			cr.execute("insert into mcisogem_histo_prime_college_temp (create_uid,choix,cod_college,write_uid) values(%s, %s, %s, %s)", (uid, True, elt['codc'], uid))

                # cr.execute("select * from mcisogem_histo_prime_college_temp where write_uid=%s", (uid,))
                # lescollegestemp = cr.dictfetchall()
                # for col in lescollegestemp:
                # 	tabcollege.append(col['id'])

                # # On va chercher a savoir si les champs budget doivent s'afficher ou non
                # # Recuperation du garant

                # if obj_police_data.garant_id.type_garant_id.code_type_garant in ['4', '3', '2']:
                #    affiche_budget = 1
                # else:
                #    affiche_budget = 0
                # A ce stade nous avons les colleges de la police et l'objet police pour les tests

                # Test pour savoir si il s'agit d'une police par beneficiare ou par tranche d'age

                if obj_police_data.type_prime == '2':
                    # Police par tranche d'age
                    # requete de recuperation des tranches d'age de la police
                    cr.execute("delete from mcisogem_histo_prime_tranche_age_temp where write_uid=%s", (uid,))
                    cr.execute('select * from tranche_age_rel where name=%s', (leshistopolices[0]['id'],))
                    lestrancheagepolice = cr.dictfetchall()

                    print lestrancheagepolice
                    if len(lestrancheagepolice) == 0:
                        raise osv.except_osv('Attention !', "Aucune tranche d'age n'a été trouvé pour la police !")
                        return {'value': {'police_id': False}}
                    else:
                        # Porcours des tranches d'ages
                        for tr in lestrancheagepolice:
                            obj_tranche_data = self.pool.get('mcisogem.tranche.age').browse(cr, uid, tr['fin_tranche'],
                                                                                            context=context)
                            cr.execute("""insert into mcisogem_histo_prime_tranche_age_temp (create_uid,montant_prime_sida,debut,fin,montant_prime,write_uid, code_tranche_age)
							 values(%s, %s, %s, %s, %s, %s,%s)""",
                                       (uid, 0, obj_tranche_data.debut_tranche, obj_tranche_data.fin_tranche, 0, uid,
                                        obj_tranche_data.id))
                        cr.execute("select * from mcisogem_histo_prime_tranche_age_temp where write_uid=%s", (uid,))
                        lestranchestemp = cr.dictfetchall()
                        for tr in lestranchestemp:
                            tabtrancheage.append(tr['id'])

                        affiche_tab_tranche = 1
                        affiche_tab_benef = 0
                        affiche_tab_college = 1
                        return {'value': {'dt_eff_mod_prime': dt_eff_mod_prime, 'cod_tranche_age_ids': tabtrancheage,
                                          'cod_college_ids': tabcollege, 'affiche_tab_tranche': 0,
                                          'affiche_tab_college': affiche_tab_college, 'affiche_tab_benef': 1,
                                          'type_prime': 2}}

                else:
                    # Police par statut bénéficiaire - Recuperation des statut benef
                    # cr.execute("delete from mcisogem_histo_prime_stat_benef_temp where write_uid=%s", (uid,))

                    # lesstatutsbenef = []
                    # histo_police_id = self.pool.get('mcisogem.histo.police').search(cr,uid,[('name' , '=' ,police_id)] , order="id DESC")

                    # for histo_police_data in self.pool.get('mcisogem.histo.police').browse(cr,uid,histo_police_id):

                    # 	for stat in histo_police_data.statut_ids:

                    # 		if stat not in lesstatutsbenef:

                    # 			lesstatutsbenef.append(stat)




                    # 	if len(lesstatutsbenef) == 0:
                    # 		affiche_budget = 0
                    # 		affiche_tab_tranche = 0
                    # 		affiche_tab_benef = 0
                    # 		raise osv.except_osv('Attention !', "Aucun statut de bénéficiaire n'a ete trouve !")
                    # 		return {'value': {'police_id': False}}
                    # 	else:
                    # 		for statut in lesstatutsbenef:
                    # 			# Insertion des statuts dans la table temporaire

                    # 			sch = self.pool.get('mcisogem.histo.prime.stat.benef.temp').search(cr,uid,[('cod_statut_benef' , '=' , statut.id)])
                    # 			if not sch:

                    # 				cr.execute("insert into mcisogem_histo_prime_stat_benef_temp (create_uid,choix,cod_statut_benef,write_uid) values(%s, %s, %s, %s)", (uid, True, statut.id, uid))


                    # cr.execute("select * from mcisogem_histo_prime_stat_benef_temp where write_uid=%s", (uid,))
                    # lesstatutstemp = cr.dictfetchall()

                    # for stemp in lesstatutstemp:

                    # 	if stemp not in tabstatutbeneficiare:

                    # 		tabstatutbeneficiare.append(stemp['id'])

                    statut_ids = []
                    tabstatut = []
                    for col in les_colleges:

                        histo = self.pool.get('mcisogem.histo.police').search(cr, uid, [('name', '=', police_id),
                                                                                        ('code_college', '=', col)])

                        for h in self.pool.get('mcisogem.histo.police').browse(cr, uid, histo):

                            for st in h.statut_ids:

                                if st.id not in statut_ids:
                                    statut_ids.append(st.id)

                    cr.execute("delete from mcisogem_histo_prime_stat_benef_temp where write_uid=%s", (uid,))

                    for st in statut_ids:
                        cr.execute(
                            "insert into mcisogem_histo_prime_stat_benef_temp (create_uid,cod_statut_benef,write_uid) values(%s, %s, %s)",
                            (uid, st, uid))

                    cr.execute('select * from mcisogem_histo_prime_stat_benef_temp where create_uid= %s', (uid,))
                    lesstattemp = cr.dictfetchall()

                    for st in lesstattemp:
                        tabstatut.append(st['id'])

                    affiche_tab_benef = 1
                    affiche_tab_tranche = 0
                    affiche_tab_college = 1

                    return {'value': {'dt_eff_mod_prime': dt_eff_mod_prime, 'cod_college_ids': les_colleges,
                                      'affiche_tab_tranche': 1, 'affiche_tab_benef': affiche_tab_benef,
                                      'affiche_tab_college': affiche_tab_college, 'type_prime': 1,
                                      'cod_statut_benef_ids': tabstatut},
                            'domain': {'cod_college_ids': [('id', 'in', les_colleges)]}}
            else:
                raise osv.except_osv('Attention !', "Cette police ne possède pas d'exercice de police !")
                return {'value': {'police_id': False}}

    def onchange_college(self, cr, uid, ids, police_id, cod_college_ids, context=None):

        colleges = cod_college_ids[0][2]
        cr.execute("delete from mcisogem_histo_prime_stat_benef_temp where write_uid=%s", (uid,))

        statut_ids = []
        tabstatut = []
        for col in colleges:

            histo = self.pool.get('mcisogem.histo.police').search(cr, uid, [('name', '=', police_id),
                                                                            ('code_college', '=', col)])

            for h in self.pool.get('mcisogem.histo.police').browse(cr, uid, histo):

                for st in h.statut_ids:

                    if st.id not in statut_ids:
                        statut_ids.append(st.id)

        for st in statut_ids:
            cr.execute(
                "insert into mcisogem_histo_prime_stat_benef_temp (create_uid,cod_statut_benef,write_uid) values(%s, %s, %s)",
                (uid, st, uid))

        cr.execute('select * from mcisogem_histo_prime_stat_benef_temp where create_uid= %s', (uid,))
        lesstattemp = cr.dictfetchall()

        for st in lesstattemp:
            tabstatut.append(st['id'])

        return {'value': {'cod_statut_benef_ids': tabstatut}}

    def create(self, cr, uid, vals, context=None):

        dernier_id = 0
        vals['police_id'] = context.get('police')
        # Recuperation des informations relatives à l'exercice de la police
        cr.execute("select * from mcisogem_exercice_police where police_id=%s order by id desc", (vals['police_id'],))
        lesexercicespolices = cr.dictfetchall()

        # Recuperation de la liste des colleges sélectionnés
        # cr.execute("select * from mcisogem_histo_prime_college_temp where write_uid=%s and choix=%s", (uid, True))
        # lescollegesselect = cr.dictfetchall()

        # Recuperation des données relatives à la police
        cr.execute("select * from mcisogem_police where id=%s", (vals['police_id'],))
        lapolice = cr.dictfetchall()[0]

        # Test pour voir si cette police possède un exercice de police
        if len(lesexercicespolices) > 0:
            vals['garant_id'] = lapolice['garant_id']
            # Test pour voir si au moins un collège a été sélectionné
            college_ids = vals['cod_college_ids'][0][2]

            if len(college_ids) > 0:
                # Test pour voir si il s'agit d'une police par tranche d'age ou par statut de bénéficiaire
                if vals['affiche_tab_benef'] == 1:

                    statut_ids = vals['cod_statut_benef_ids'][0][2]
                    # Police par statut de beneficiaire
                    # Recuperation de la liste des statuts de bénéficiaire cochés
                    # cr.execute("select * from mcisogem_histo_prime_stat_benef_temp where write_uid=%s", (uid, True))

                    # lesstatutbenefselect = cr.dictfetchall()

                    if len(statut_ids) > 0:

                        compteur_create = 0

                        # Parccours des collèges pour insertion des données en base
                        for college in college_ids:

                            college_data = self.pool.get('mcisogem.college').browse(cr, uid, college)

                            # parcours des statuts bénef
                            for stat in vals['cod_statut_benef_ids'][0][2]:

                                statut_data = self.pool.get('mcisogem.histo.prime.stat.benef.temp').browse(cr, uid,
                                                                                                           stat)

                                real_statut_data = self.pool.get('mcisogem.stat.benef').browse(cr, uid,
                                                                                               statut_data.cod_statut_benef.id)

                                # cr.execute("select * from mcisogem_histo_prime_stat_benef_temp where write_uid=%s and choix=%s and id = %s", (uid, True , stat))

                                # stat = cr.dictfetchone()

                                # print('---------- STAT ---------')
                                # print(stat)

                                cr.execute(
                                    "select id, dt_eff_mod_prime from mcisogem_histo_prime where college_id=%s and statut_benef_id=%s and police_id = %s order by dt_eff_mod_prime desc",
                                    (college_data.id, real_statut_data.id, vals['police_id']))
                                leshistoprimes = cr.dictfetchall()

                                test_create = True
                                vals['garant_id'] = self._get_assur(cr, uid, context)

                                if len(leshistoprimes) > 0:
                                    histop = leshistoprimes[0]
                                    if vals['dt_eff_mod_prime'] > histop['dt_eff_mod_prime']:

                                        # 1er niveau de vérification
                                        datedujour = time.strftime('%Y-%m-%d', time.localtime())
                                        # cr.execute("update mcisogem_histo_prime set dt_eff_mod_prime=%s where id=%s", (datedujour, histop['id']))
                                        test_create = True


                                    else:

                                        raise osv.except_osv('Attention !',
                                                             "La date d'éffet doit être supérieur à la date d'éffet de la précédente historique de prime !")

                                hito_search = self.pool.get('mcisogem.histo.police').search(cr, uid, [
                                    ('name', '=', vals['police_id']), ('code_college', '=', college_data.id)],
                                                                                            order='dt_eff_histo_pol DESC',
                                                                                            limit=1)
                                histo_datas = self.pool.get('mcisogem.histo.police').browse(cr, uid, hito_search)

                                stat_ok = False

                                for s in histo_datas.statut_ids:

                                    if s.id == real_statut_data.id:
                                        stat_ok = True

                                        break

                                if test_create and stat_ok:
                                    compteur_create = compteur_create + 1
                                    data = {}
                                    data['college_id'] = college_data.id
                                    data['statut_benef_id'] = real_statut_data.id
                                    data['garant_id'] = vals['garant_id']
                                    data['police_id'] = vals['police_id']
                                    data['dt_eff_mod_prime'] = vals['dt_eff_mod_prime']
                                    data['num_avenant'] = 0

                                    data['prim_assure'] = statut_data.montant_prime
                                    data['prime_sida'] = statut_data.montant_prime_sida

                                    data['num_police'] = lapolice['num_interne_police']
                                    data['name'] = lapolice['name']
                                    data['type_prime'] = int(lapolice['type_prime'])
                                    data['mode_calcul'] = lapolice['repartition_prime']
                                    data['repartition_prime'] = lapolice['repartition_prime']
                                    data['prime_mois_exercice'] = lapolice['periodicite_paiem']
                                    # data['code_tranche_age'] = 1
                                    data['budget_sida'] = vals['budget_sida']
                                    data['budget_simple'] = vals['budget_simple']
                                    data['budget_ttc'] = vals['budget_ttc']
                                    data['affiche_tab_college'] = 0
                                    data['affiche_tab_benef'] = 0
                                    data['affiche_tab_tranche'] = 0
                                    data['affiche_budget'] = vals['affiche_budget']
                                    data['modification'] = 1
                                    data['modification_tranche'] = 0
                                    data['modification_benef'] = 1

                                    rech = self.pool.get('mcisogem.histo.prime').search(cr, uid,
                                                                                        [('statut_benef_id', '=',
                                                                                          real_statut_data.id), (
                                                                                         'police_id', '=',
                                                                                         vals['police_id']), (
                                                                                         'college_id', '=',
                                                                                         data['college_id'])])

                                    for rech_data in self.pool.get('mcisogem.histo.prime').browse(cr, uid, rech):
                                        new_date_fin = datetime.strptime(data['dt_eff_mod_prime'],
                                                                         '%Y-%m-%d') - timedelta(days=1)
                                        cr.execute("update mcisogem_histo_prime set dt_echea_pol = %s where id = %s",
                                                   (new_date_fin, rech_data.id))

                                    dernier_id = super(mcisogem_histo_prime, self).create(cr, uid, data,
                                                                                          context=context)

                                #####################################""

                                #######################################
                                # A quel moment doit-on crée le budget ???????? #
                                ##################################

                                # valeur = {}
                                # # données à enregistrer dans la table budget
                                # valeur['num_histo_prime'] = dernier_id
                                # valeur['mnt_budget_restant'] = vals['budget_simple']
                                # valeur['mnt_budget_simple_rea'] = 0
                                # valeur['mnt_budget_sida_rea'] = 0
                                # valeur['type_budget'] = 'I'
                                # valeur['statut_budget'] = 'A'
                                # valeur['state'] = 'A'
                                # valeur['ident_centre'] = self._get_cod_gest_id(cr,uid)
                                # valeur['code_gest'] = self._get_cod_gest(cr,uid)
                                # valeur['code_langue'] = self._get_cod_lang(cr,uid)

                                # self.pool.get('mcisogem.budget').create(cr,uid,valeur,context)

                        # On va vider les tables temporaires

                        cr.execute("delete from mcisogem_histo_prime_stat_benef_temp where write_uid=%s", (uid,))
                        cr.execute("delete from mcisogem_histo_prime_college_temp where write_uid=%s", (uid,))

                        return dernier_id
                    else:
                        raise osv.except_osv('Attention !',
                                             "Veuillez sélectionner au moins un statut de bénéficiaire !")
                        return False
                else:
                    # Police par tranche d'age
                    # Recuperation de la liste des tranches d'age cochées
                    cr.execute("select * from mcisogem_histo_prime_tranche_age_temp where write_uid=%s", (uid,))
                    lestarnchesagesselect = cr.dictfetchall()
                    compteur_create = 0

                    if len(lestarnchesagesselect) > 0:
                        # Parcours des collèges
                        for college in lescollegesselect:
                            # Parcours des traches d'ages
                            for tranche in lestarnchesagesselect:
                                # Insertion des données en base
                                # Avant insertion on va chercher a voir si un enregistrement possédant le meme statut benef et le meme college
                                # Si un enregistrement a été trouvé on récuprer la date d'effet qu'on va comparer a la nouvelle date. La nouvelle date d'effet doit etre supérieur à la précédente date
                                cr.execute(
                                    "select id, dt_eff_mod_prime from mcisogem_histo_prime where college_id=%s and code_tranche_age=%s order by dt_eff_mod_prime desc",
                                    (college['cod_college'], tranche['code_tranche_age']))
                                leshistoprimes = cr.dictfetchall()

                                test_create = True

                                if len(leshistoprimes) > 0:
                                    histop = leshistoprimes[0]
                                    if vals['dt_eff_mod_prime'] > histop['dt_eff_mod_prime']:
                                        # 1er niveau de vérification
                                        datedujour = time.strftime('%Y-%m-%d', time.localtime())
                                        cr.execute("update mcisogem_histo_prime set dt_eff_mod_prime=%s where id=%s",
                                                   (datedujour, histop['id']))
                                        test_create = True
                                    else:
                                        test_create = False

                                if test_create:
                                    compteur_create = compteur_create + 1
                                    data = {}
                                    data['college_id'] = college['cod_college']
                                    data['garant_id'] = vals['garant_id']
                                    data['police_id'] = vals['police_id']
                                    data['dt_eff_mod_prime'] = vals['dt_eff_mod_prime']
                                    data['num_avenant'] = 0
                                    data['dt_echea_pol'] = lesexercicespolices[0]['date_fin_exercice']
                                    data['prim_assure'] = tranche['montant_prime']
                                    data['prime_sida'] = tranche['montant_prime_sida']
                                    data['num_police'] = lapolice['num_interne_police']
                                    data['type_prime'] = int(lapolice['type_prime'])
                                    data['mode_calcul'] = lapolice['repartition_prime']
                                    data['name'] = lapolice['name']
                                    data['repartition_prime'] = lapolice['repartition_prime']
                                    data['prime_mois_exercice'] = vals['prime_mois_exercice']
                                    data['code_tranche_age'] = tranche['code_tranche_age']
                                    data['budget_sida'] = vals['budget_sida']
                                    data['budget_simple'] = vals['budget_simple']
                                    data['budget_ttc'] = vals['budget_ttc']
                                    data['affiche_tab_college'] = 0
                                    data['affiche_tab_benef'] = 0
                                    data['affiche_tab_tranche'] = 0
                                    data['modification'] = 1
                                    data['modification_tranche'] = 1
                                    data['modification_benef'] = 0
                                    data['affiche_budget'] = vals['affiche_budget']
                                    dernier_id = super(mcisogem_histo_prime, self).create(cr, uid, data,
                                                                                          context=context)

                        if compteur_create == 0:
                            raise osv.except_osv('Attention !',
                                                 "La date d'éffet doit être supérieur à la date d'éffet de la précédente historique de prime !")
                            return False
                        else:
                            # On va vider les tables temporaires
                            cr.execute("delete from mcisogem_histo_prime_tranche_age_temp where write_uid=%s", (uid,))
                            cr.execute("delete from mcisogem_histo_prime_college_temp where write_uid=%s", (uid,))
                            return dernier_id
                    else:
                        raise osv.except_osv('Attention !', "Veuillez sélectionner au moins une tranche d'age !")
                        return False

            else:
                raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un collège !")
                return False
        else:
            raise osv.except_osv('Attention !', "Cette police n'a pas été associé à un exercice de police !")
            return False


class mcisogem_histo_prime_stat_benef_temp(osv.osv):
    _name = "mcisogem.histo.prime.stat.benef.temp"
    _description = 'Statut du beneficiaire'

    _columns = {
        'choix': fields.boolean('Choix'),
        'montant_prime': fields.integer('Montant prime', required=False),
        'montant_prime_sida': fields.integer('Montant prime SIDA', required=False),
        'cod_statut_benef': fields.many2one('mcisogem.stat.benef', 'Statut', readonly=True),

    }

    _order = 'cod_statut_benef ASC'

    def onchange_choix(self, cr, uid, ids, choix, context=None):
        cr.execute("update mcisogem_histo_prime_stat_benef_temp set choix=%s where id=%s", (choix, ids[0]))

    def onchange_montant_prime(self, cr, uid, ids, montant_prime, context=None):
        cr.execute("update mcisogem_histo_prime_stat_benef_temp set montant_prime=%s where id=%s",
                   (montant_prime, ids[0]))

    def onchange_montant_prime_sida(self, cr, uid, ids, montant_prime_sida, context=None):
        cr.execute("update mcisogem_histo_prime_stat_benef_temp set montant_prime_sida=%s where id=%s",
                   (montant_prime_sida, ids[0]))


class mcisogem_histo_prime_college_temp(osv.osv):
    _name = "mcisogem.histo.prime.college.temp"
    _description = 'College'

    _columns = {
        'choix': fields.boolean('Choix'),
        'cod_college': fields.many2one('mcisogem.college', 'name', 'College', readonly=True),

    }

    def onchange_choix(self, cr, uid, ids, choix, context=None):
        cr.execute("update mcisogem_histo_prime_college_temp set choix=%s where id=%s", (choix, ids[0]))


class mcisogem_histo_prime_tranche_age_temp(osv.osv):
    _name = "mcisogem.histo.prime.tranche.age.temp"
    _description = 'Tranche age'

    _columns = {
        'code_tranche_age': fields.many2one('mcisogem.tranche.age', 'name', 'Tranche_age', readonly=True),
        'debut': fields.integer('debut', required=False, readonly=True),
        'fin': fields.integer('fin', required=False, readonly=True),
        'montant_prime': fields.integer('Montant prime', required=False),
        'montant_prime_sida': fields.integer('Montant prime sida', required=False),

    }

    def onchange_montant_prime(self, cr, uid, ids, montant_prime, context=None):
        cr.execute("update mcisogem_histo_prime_tranche_age_temp set montant_prime=%s where id=%s",
                   (montant_prime, ids[0]))

    def onchange_montant_prime_sida(self, cr, uid, ids, montant_prime_sida, context=None):
        cr.execute("update mcisogem_histo_prime_tranche_age_temp set montant_prime_sida=%s where id=%s",
                   (montant_prime_sida, ids[0]))


class mcisogem_produit(osv.osv):
    _name = "mcisogem.produit"
    _description = 'Produit'

    _columns = {
        'name': fields.char('Produit', required=True),
    }


class mcisogem_produit_police(osv.osv):
    _name = "mcisogem.produit.police"
    _description = 'PRODUIT- POLICE'

    def _get_context(self, cr, uid, context):
        context = context or {}
        return context.get('police')

    _columns = {
        'police_id': fields.many2one('mcisogem.police', 'police', required=True, readonly=True),
        'produit_id': fields.many2one('mcisogem.produit', 'Produit', required=True),
        'dt_effet_produit': fields.date('Date d\'effet du produit', required=True),
        'college_id': fields.many2one('mcisogem.college', 'College'),
        'statut_id': fields.many2one('mcisogem.stat.benef', 'Statut'),
        'acte_id': fields.many2one('mcisogem.nomen.prest', 'Acte'),
        'sous_acte': fields.many2one('mcisogem.sous.actes', 'Sous acte'),
        'delai': fields.integer('Delai de Carence'),
        'ticm_assure': fields.integer('Ticket Mod.', required=False),
        'unite_temps_id': fields.many2one('mcisogem.unite.temps', 'Périodicité'),
        'state': fields.selection([
            ('N', "Nouveau"),
            ('A', "Actif"),
        ], 'Statut', required=True),
        'cod_college_ids': fields.many2many('mcisogem.college', 'mcisogem_college_produit_rel', 'code_college',
                                            'produit_id', 'Collèges', required=True),
        'cod_statut_benef_ids': fields.many2many('mcisogem.stat.benef', 'mcisogem_stat_benef_produit_rel', 'id',
                                                 'produit_id', 'Statuts', required=False),

    }

    def onchange_college(self, cr, uid, ids, college_ids, context=None):

        if college_ids:
            colleges = college_ids[0][2]
            lesstatutsbenef = []

            statut_ids = []

            for col in colleges:

                histo = self.pool.get('mcisogem.histo.police').search(cr, uid, [('code_college', '=', col)],
                                                                      order="id DESC", limit=1)

                for h in self.pool.get('mcisogem.histo.police').browse(cr, uid, histo):

                    for st in h.statut_ids:

                        if st.id not in statut_ids:
                            statut_ids.append(st.id)

            return {'value': {'cod_statut_benef_ids': statut_ids}}

    def onchange_police(self, cr, uid, ids, police_id, context=None):

        if police_id:
            col_ids = self.pool.get('mcisogem.college').search(cr, uid, [('police_id', '=', police_id)])

            d = {'cod_college_ids': [('id', 'in', col_ids)]}
            return {'domain': d}

    def onchange_produit(self, cr, uid, ids, produit_id):
        if produit_id:
            bareme = self.pool.get('mcisogem.bareme').search(cr, uid, [('produit_id', '=', produit_id)])

            d = {'cod_acte_ids': [('id', 'in', bareme)]}

            return {'domain': d}

    def _get_default_colleges(self, cr, uid, context):
        return self.pool.get('mcisogem.college').search(cr, uid, [('police_id', '=', context.get('police'))])

    def _get_default_statut(self, cr, uid, context):
        histo_police_id = self.pool.get('mcisogem.histo.police').search(cr, uid, [('name', '=', context.get('police'))],
                                                                        order="id DESC")
        lesstatutsbenef = []

        for h in self.pool.get('mcisogem.histo.police').browse(cr, uid, histo_police_id):

            for stat in h.statut_ids:

                if stat.id not in lesstatutsbenef:
                    lesstatutsbenef.append(stat.id)

        return self.pool.get('mcisogem.stat.benef').search(cr, uid, [('id', 'in', lesstatutsbenef)])

    _sql_constraints = [('unique_produit_police', 'unique(police_id,produit_id,sous_acte,acte_id,college_id,statut_id)',
                         "Ce rattachement existe déjà !"), ]

    _defaults = {
        'cod_statut_benef_ids': _get_default_statut,
        'police_id': _get_context,
        'cod_college_ids': _get_default_colleges,
        'state': 'N',
    }

    _rec_name = 'police_id'

    def create(self, cr, uid, vals, context=None):

        colleges = vals['cod_college_ids'][0][2]

        actes = self.pool.get('mcisogem.bareme').search(cr, uid, [('produit_id', '=', vals['produit_id'])])

        if not actes:
            raise osv.except_osv('Attention !' , 'Ce produit ne contient aucun élément.')
        dernier_id = False

        for col in colleges:

            for acte in actes:

                bareme_data  = self.pool.get('mcisogem.bareme').browse(cr,uid,acte)

                vals['college_id'] = col
                vals['statut_id'] = bareme_data.statut_id.id
                vals['acte_id'] = bareme_data.acte_id.id

                if bareme_data.sous_acte:
                    vals['sous_acte'] = bareme_data.sous_acte.id

                vals['delai'] = bareme_data.delai
                vals['ticm_assure'] = bareme_data.ticm_assure

                if bareme_data.sous_acte:

                    rech_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('college_id', '=', col),
                                                                                   ('statut_id', '=', bareme_data.statut_id.id),
                                                                                   ('sous_acte' , '=' , vals['sous_acte'])])

                else:


                    rech_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('college_id', '=', col),
                                                                                       ('statut_id', '=', bareme_data.statut_id.id), (
                                                                                           'acte_id', '=',
                                                                                           vals['acte_id'])])


                if rech_s:
                    raise osv.except_osv('Attention !',
                                         'Le collège ne peut être rattaché à plusieurs produits pour le même acte/sous acte et le même statut d\'assuré')

                dernier_id = super(mcisogem_produit_police, self).create(cr, uid, vals, context=context)

        return dernier_id


class mcisogem_bareme(osv.osv):
    _name = "mcisogem.bareme"
    _description = 'Barème Police'

    _sql_constraints = [('unique_produit', 'unique(produit_id , sous_acte , statut_id)', "Ce produit existe déjà !"), ]

    _columns = {
        'produit_id': fields.many2one('mcisogem.produit', 'Produit', required=True),
        'acte_id': fields.many2one('mcisogem.nomen.prest', "Acte", required=False),
        'sous_acte': fields.many2one('mcisogem.sous.actes', 'Sous acte', required=False),

        'date_effet_mod_bareme': fields.date('Date éffet'),
        'categ_bar': fields.char('Code Centre', size=30, required=False),
        'state': fields.selection([
            ('N', "Nouveau"),
            ('A', "Actif"),
            ('R', "Resilié"),
        ], 'Statut', required=True),
        'plf_prest_assure': fields.integer('Plafond / Transaction', required=False),
        'ticm_assure': fields.integer('Ticket modérateur', required=False),
        'bl_ticm_assure_tx': fields.boolean('', ),
        'ticm_conj': fields.integer('ticm_conj', required=False),
        'bl_ticm_conj_tx': fields.boolean('bl_ticm_conj_tx', required=False),
        'ticm_enfant': fields.integer('ticm_enfant', required=False),
        'bl_ticm_enfant_tx': fields.boolean('bl_ticm_enfant_tx', required=False),
        'plf_prest_conj': fields.integer('plf_prest_conj', required=False),
        'plf_prest_enfant': fields.integer('plf_prest_enfant', required=False),
        'plf_prest_parent_autre': fields.integer('plf_prest_parent_autre', required=False),
        'plf_prest_parent': fields.integer('plf_prest_parent', required=False),
        'ticm_parent': fields.integer('ticm_parent', required=False),
        'bl_ticm_parent_tx': fields.boolean('bl_ticm_parent_tx', required=False),
        'plf_prest_autre': fields.integer('plf_prest_autre', required=False),
        'ticm_autre': fields.integer('ticm_autre', required=False),
        'bl_ticm_autre_tx': fields.integer('bl_ticm_autre_tx', required=False),
        'nbre_plfd_tous': fields.integer('nbre_plfd_tous', required=False),
        'plf_prest_tous': fields.integer('plf_prest_tous', required=False),
        'nbre_plfd_parent_autre': fields.integer('nbre_plfd_parent_autre', required=False),
        'prest_espece_bar': fields.integer('prest_espece_bar', required=False),
        'plf_an_prest': fields.integer('Plafond / période', required=False),
        'max_act_an_benef': fields.integer('Quantité', required=False),
        'bar_perio_prescrit': fields.integer('Périodicité de prescription', required=False),
        'bar_unite_period': fields.char('bar_unite_period', size=1, required=False),
        'num_ave': fields.char('Avenant', size=1, required=False),
        'plf_prest_fam': fields.integer('Plafond / famille assuré', required=False),
        'nbre_plfd_pol': fields.integer('nbre_plfd_pol', required=False),
        'nbre_plfd_fam': fields.integer('nbre_plfd_fam', required=False),
        'cod_sup': fields.char('cod_sup', size=1, required=False),
        'territoire_id': fields.many2one('mcisogem.territoire', "Térritorialité", required=False),
        'cod_statut_benef': fields.many2one('mcisogem.stat.benef', "Statut Bénéficiaire", required=False),
        'date_resiliation_bareme': fields.date('Date de résiliation'),
        'mode_bareme': fields.selection([('Q', 'Quantité autorisée'), ('D', 'Date Anniversaire'), ('A', 'Année')],
                                        'Mode barème', required=False),
        'plf_an_fam_act': fields.integer('Plafond famille acte', required=False),
        'max_fam_act_an_benef': fields.integer('max_fam_act_an_benef', required=False),
        'plf_jour': fields.integer('Plafond / jour', required=False),
        'unite_temps_id': fields.many2one('mcisogem.unite.temps', "Périodicité de prescription", required=False),
        'plafond_tick_mod': fields.float('Plafond / période', size=50),
        'tick_mod': fields.float('Nouveau ticket modérateur', size=50),
        'tick_mod_pourcentage': fields.boolean('%'),
        'delai': fields.integer('Delai de carence (en jrs)'),
        ''

        # Champs pour le formatage de l'affichage
        'type_prime': fields.selection([('1', 'Statut de bénéficiaire'), ('2', 'Tranche d\'age')],
                                       'Enregistrement prime par'),

        'chp_date_effet_histo_police': fields.date('Date effet histo police', required=False, readonly=True),
        'chp_date_effet_police': fields.date('Date effet police', required=False, readonly=True),
        'chp_souscripteur': fields.char('Souscripteur', readonly=True),
        'chp_assureur': fields.char('Assureur', readonly=True),
        'chp_intermediaire': fields.char('Assur. Interm.', readonly=True),
        'chp_typecontrat': fields.char('Type de contrat', readonly=True),
        'chp_territorialite': fields.char('Térritorialité', readonly=True),
        'plafond_transaction_temp': fields.integer('Plafond / Transaction', required=False),

        'cod_acte_ids': fields.many2many('mcisogem.bareme.acte.temp',
                                         'mcisogem_bareme_acte_temp_rel',
                                         'acte_temp_id',
                                         'cod_acte', 'Choix des actes', required=False),

        'cod_fam_ids': fields.many2many('mcisogem.fam.prest',
                                        'mcisogem_bareme_fam_acte_rel',
                                        'bareme_id',
                                        'fam_id', 'Famille d\'acte', required=False),

        'chp_affiche': fields.integer('affiche', ),

        'mnt_plfd_pol': fields.integer('Police', required=False),
        'mnt_plfd_col': fields.integer('Collège'),
        'mnt_plfd_ass': fields.integer('Assure principal (A)', required=False),
        'mnt_plfd_conj': fields.integer('Conjoint (C)', required=False),
        'mnt_plfd_enf': fields.integer('Enfant (E)', required=False),
        'mnt_plfd_dep': fields.integer('Dependants '),
        'mnt_plfd_tenf': fields.integer('Tous les enfants'),
        'mnt_plfd_parent': fields.integer('Parents'),

        'mnt_plfd_parent_autre': fields.integer('Autre parent (X)'),
        'mnt_plfd_gen': fields.integer('Géniteur (G)'),
        'mnt_plfd_aut_conj': fields.integer('Autre conjointe (D)'),
        'mnt_plfd_enf_sup': fields.integer('Enfant supplémentaire (K)'),
        'famille_acte_id': fields.many2one('mcisogem.fam.prest', 'Famille'),
        'param_glob': fields.boolean('Paramètres groupés'),

        'cod_statut_benef_ids': fields.many2many('mcisogem.stat.benef', 'mcisogem_stat_benef_produit__rel', 'id',
                                                 'produit_id', 'Statuts', required=True),

        'statut_id' : fields.many2one('mcisogem.stat.benef' , 'Statut'),

    }

    _rec_name = 'acte_id'

    def _get_default_statut(self, cr, uid, context):
        return self.pool.get('mcisogem.stat.benef').search(cr, uid, [])


    def _get_context(self, cr, uid, context):
        context = context or {}
        return context.get('police')

    def button_resilier_bareme(self, cr, uid, ids, context=None):

        bareme = self.browse(cr, uid, ids[0], context=context).id
        police_data = self.browse(cr, uid, ids[0])

        ctx = (context or {}).copy()
        ctx['id'] = ids[0]
        ctx['action'] = 'resil'
        form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa',
                                                                      'view_mcisogem_bareme_resilier_form')[1]

        return {
            'name': 'Resiliation du Barême',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mcisogem.bareme',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def button_annuler_bareme(self, cr, uid, ids, context=None):

        super(mcisogem_bareme, self).write(cr, uid, ids, {'state': 'A', 'date_resiliation_bareme': None},
                                           context=context)
        return True

    _defaults = {

        'plf_prest_assure': 0,
        'state': 'N',
        'num_ave': 0,
        'plf_prest_fam': 0,
        'nbre_plfd_pol': 0,
        'nbre_plfd_fam': 0,
        'plf_an_fam_act': 0,
        'max_fam_act_an_benef': 0,
        'plf_jour': 0,
        'plafond_transaction_temp': 0,
        'max_act_an_benef': 0,
        'cod_statut_benef_ids' : _get_default_statut,
        'chp_affiche': 0,
        'mode_bareme': 'A',
        'bl_ticm_assure_tx': True
    }

    def onchange_code_police(self, cr, uid, ids, police_id, context=None):
        if not police_id:
            return False
        else:
            # Recuperation des infos sur la police pour affichage
            police_data = self.pool.get('mcisogem.police').browse(cr, uid, police_id, context=context)
            # Recuperation de la date de l'histo police
            cr.execute('select dt_eff_mod_pol from mcisogem_histo_police where name=%s order by id desc',
                       (police_data.id,))
            leshistopolice = cr.dictfetchall()
            if len(leshistopolice) > 0:
                histopolice = leshistopolice[0]
                return {'value': {'chp_date_effet_police': police_data.dt_effet,
                                  'chp_souscripteur': police_data.souscripteur_id.name,
                                  'chp_assureur': police_data.garant_id.name,
                                  'chp_intermediaire': police_data.courtier_id.name,
                                  'chp_typecontrat': police_data.type_contrat_id.name,
                                  'chp_territorialite': police_data.territoire_id.name,
                                  'chp_date_effet_histo_police': histopolice['dt_eff_mod_pol'],
                                  'date_effet_mod_bareme': police_data.dt_effet,
                                  'type_prime': police_data.type_prime}}
            else:
                raise osv.except_osv('Attention !', "Aucune historique de police n'a été trouvée pour cette police !")
                return {'value': {'police_id': False}}

    def onchange_famille(self, cr, uid, ids, cod_fam_ids, police_id, context=None):

        if police_id:

            tabacte = []
            les_famille = []

            cr.execute("delete from mcisogem_bareme_acte_temp where write_uid=%s", (uid,))

            for f_id in cod_fam_ids[0][2]:
                les_famille.append(f_id)

            if len(les_famille) > 0:

                for f in les_famille:
                    les_actes_du_produit = []

                    ls = self.pool.get('mcisogem.bareme').search(cr, uid, [('produit_id', '=', police_id)])
                    for l in self.pool.get('mcisogem.bareme').browse(cr, uid, ls):
                        les_actes_du_produit.append(l.acte_id.id)

                    # if les_actes_du_produit:
                    #
                    #     les_actes_temp = self.pool.get('mcisogem.nomen.prest').search(cr, uid,
                    #                                                                   [('code_fam_prest', '=', f), (
                    #                                                                   'id', 'not in',
                    #                                                                   tuple(les_actes_du_produit))])
                    #
                    # else:

                    les_actes_temp = self.pool.get('mcisogem.nomen.prest').search(cr, uid,
                                                                                      [('code_fam_prest', '=', f)])


                    for acte in les_actes_temp:
                        data_temp = {}
                        les_sous_actes_temp = self.pool.get('mcisogem.sous.actes').search(cr, uid,
                                                                                          [('code_acte', '=',
                                                                                            acte)])
                        data_temp['cod_acte'] = acte


                        if les_sous_actes_temp:

                            for sous_acte in les_sous_actes_temp:

                                data_temp['sous_acte'] = sous_acte
                                data_temp['bl_ticm_assure_tx'] = 'T'
                                data_temp['ticm_assure'] = 0
                                data_temp['delai'] = 0
                                data_temp['unite_temps_id'] = self.pool.get('mcisogem.unite.temps').search(cr,uid,[],order='id DESC')[3]
                                data_temp['max_act_an_benef'] = 0
                                data_temp['plf_prest_assure'] = 0
                                data_temp['plafond_tick_mod'] = 0
                                data_temp['plf_jour'] = 0
                                data_temp['plf_prest_fam'] = 0

                                last_id = self.pool.get('mcisogem.bareme.acte.temp').create(cr,uid,data_temp)

                        else:
                            data_temp['bl_ticm_assure_tx'] = 'T'
                            data_temp['ticm_assure'] = 0
                            data_temp['delai'] = 0
                            data_temp['unite_temps_id'] = \
                            self.pool.get('mcisogem.unite.temps').search(cr, uid, [] , order='id DESC')[3]
                            data_temp['max_act_an_benef'] = 0
                            data_temp['plf_prest_assure'] = 0
                            data_temp['plafond_tick_mod'] = 0
                            data_temp['plf_jour'] = 0
                            data_temp['plf_prest_fam'] = 0

                            last_id = self.pool.get('mcisogem.bareme.acte.temp').create(cr, uid, data_temp)

                    # Recuperation des actes temporaires enregistré en base
                    cr.execute("select * from mcisogem_bareme_acte_temp where create_uid=%s", (uid,))
                    lesactestemp = cr.dictfetchall()

                    for act in lesactestemp:
                        tabacte.append(act['id'])

                return {'value': {'cod_acte_ids': tabacte}}

            else:
                return {'value': {'cod_acte_ids': None}}

    def button_valide(self, cr, uid, ids, context):
        print('************ OK **********')

    def create(self, cr, uid, vals, context=None):

        if context.get('action') == 'resil':
            ctx = context or {}
            ctx['action'] = ''
            context = ctx
            ctx['action'] = 'resil'
            data = {}

            cr.execute("update mcisogem_bareme set date_resiliation_bareme =%s , state = %s  where id=%s",
                       (vals['date_resiliation_bareme'], 'R', context.get('id')))
            return context.get('id')

        vals['police_id'] = self._get_context(cr, uid, context)
        testTicket = True

        les_polices_rattaches = []
        les_colleges_rattaches = []
        les_statuts_rattaches = []

        les_produits_police = self.pool.get('mcisogem.produit.police').search(cr, uid,
                                                                              [('produit_id', '=', vals['produit_id'])])

        date_effet = None
        for prodpol in self.pool.get('mcisogem.produit.police').browse(cr, uid, les_produits_police):

            if prodpol.police_id.id not in les_polices_rattaches:
                les_polices_rattaches.append(prodpol.police_id.id)

                date_effet = prodpol.dt_effet_produit



        # Si bl_ticm_assure_tx est à True on doit s'assurer que le ticket modérateur est compris entre 0 et 100
        if vals['bl_ticm_assure_tx']:
            if vals['ticm_assure'] < 0 or vals['ticm_assure'] > 100:
                testTicket = False

        if not testTicket:
            raise osv.except_osv('Attention !', "La valeur du ticket modérateur doit être comprise entre 1 et 100 !")
            return False
        else:

            datedujour = time.strftime("%Y-%m-%d", time.localtime())

            utilisateur_data = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            centre_gestion_data = self.pool.get('mcisogem.centre.gestion').browse(cr, uid,
                                                                                  utilisateur_data.code_gest_id.id,
                                                                                  context=context)

            lesactesselect = vals['cod_acte_ids'][0][2]
            lesstatuts = vals['cod_statut_benef_ids'][0][2]

            if len(lesactesselect) > 0:
                dernier_id = 0
                # Parcours des données récupérées
                compteur_create = 0
                for act in lesactesselect:

                    cr.execute("select * from mcisogem_bareme_acte_temp where id=%s", (act,))
                    act = cr.dictfetchall()[0]

                    # Recuperation des données de la police
                    police_data = self.pool.get('mcisogem.police').browse(cr, uid, self._get_context(cr, uid, context),
                                                                          context=context)

                    # #Avant insertion on va chercher à savoir si ce bareme n'existe pas déjà en base de données.
                    test_create = True




                    for statut in lesstatuts:

                        if act['sous_acte']:

                            searchh = self.pool.get('mcisogem.bareme').search(cr, uid,
                                                                              [('produit_id', '=', vals['produit_id']),
                                                                               ('sous_acte', '=', act['sous_acte']) , ('statut_id' , '=' , statut)])
                        else:

                            searchh = self.pool.get('mcisogem.bareme').search(cr, uid,
                                                                              [('produit_id', '=', vals['produit_id']),
                                                                               ('acte_id', '=', act['cod_acte']) , ('statut_id' , '=' , statut)])


                        if searchh:
                            test_create = False

                        if test_create:
                            compteur_create = compteur_create + 1
                            data = {}
                            data = vals

                            if vals['param_glob']:

                                data['acte_id'] = act['cod_acte']
                                data['sous_acte'] = act['sous_acte']
                                data['num_ave'] = 0
                                data['famille_acte_id'] = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, act[
                                    'cod_acte']).code_fam_prest.id
                                data['chp_affiche'] = 1
                                data['statut_id'] = statut

                                dernier_id = super(mcisogem_bareme, self).create(cr, uid, data, context=context)


                            else:

                                values = {}

                                data = vals
                                data['statut_id'] = statut
                                data['delai'] = act['delai']
                                data['acte_id'] = act['cod_acte']
                                data['sous_acte'] = act['sous_acte']
                                data['bl_ticm_assure_tx'] = act['bl_ticm_assure_tx']
                                data['ticm_assure'] = act['ticm_assure']
                                data['unite_temps_id'] = act['unite_temps_id']
                                data['max_act_an_benef'] = act['max_act_an_benef']
                                #data['plf_prest_assure'] = act['plf_prest_assure']
                                data['plafond_transaction_temp'] = act['plf_prest_assure']
                                data['plafond_tick_mod'] = act['plafond_tick_mod']
                                data['plf_an_prest'] = act['plafond_tick_mod']

                                data['plf_jour'] = act['plf_jour']
                                data['plf_prest_fam'] = act['plf_prest_fam']
                                data['plafond_transaction_temp'] = vals['plafond_transaction_temp']
                                data['unite_temps_id'] = vals['unite_temps_id']
                                data['num_ave'] = 0
                                data['famille_acte_id'] = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, act[
                                    'cod_acte']).code_fam_prest.id
                                data['chp_affiche'] = 1

                                dernier_id = super(mcisogem_bareme, self).create(cr, uid, data, context=context)




                            for police in les_polices_rattaches:
                                les_produits_police = self.pool.get('mcisogem.produit.police').search(cr, uid, [
                                    ('produit_id', '=', vals['produit_id']), ('police_id', '=', police)])

                                for ligne in self.pool.get('mcisogem.produit.police').browse(cr, uid, les_produits_police):

                                    if ligne.college_id.id not in les_colleges_rattaches:
                                        les_colleges_rattaches.append(ligne.college_id.id)

                                    if ligne.statut_id.id not in les_statuts_rattaches:
                                        les_statuts_rattaches.append(ligne.statut_id.id)

                                prodpol_data = {}

                                for col in les_colleges_rattaches:

                                    for statut in les_statuts_rattaches:

                                        prodpol_data['acte_id'] = act['cod_acte']
                                        prodpol_data['delai'] = vals['delai']
                                        prodpol_data['statut_id'] = statut
                                        prodpol_data['college_id'] = col
                                        prodpol_data['dt_effet_produit'] = date_effet
                                        prodpol_data['produit_id'] = vals['produit_id']
                                        prodpol_data['police_id'] = police
                                        prodpol_data['ticm_assure'] = vals['ticm_assure']
                                        rech_s = self.pool.get('mcisogem.produit.police').search(cr, uid,
                                                                                                 [('college_id', '=', col),
                                                                                                  (
                                                                                                  'statut_id', '=', statut),
                                                                                                  ('acte_id', '=',
                                                                                                   act['cod_acte'])])

                                        if not rech_s:
                                            super(mcisogem_produit_police, self.pool.get('mcisogem.produit.police')).create(
                                                cr, uid, prodpol_data, context=context)

                                les_colleges_rattaches = []
                                les_statuts_rattaches = []

                if compteur_create == 0:
                    raise osv.except_osv('Attention !',
                                         "Vous tentez de créer un ou plusieurs produits qui existent déjà !")
                else:
                    return dernier_id

            else:
                raise osv.except_osv('Attention !', "Veuillez sélectionner au moins un acte  !")

    def write(self, cr, uid, ids, vals, context=None):
        # Recuperation des données sur le bareme
        data = self.pool.get('mcisogem.bareme').browse(cr, uid, ids[0], context=context)

        if 'cod_statut_benef' in vals:
            # Recuperation du statut de
            statut_benef_data = self.pool.get('mcisogem.stat.benef').browse(cr, uid, vals['cod_statut_benef'],
                                                                            context=context)
            if statut_benef_data.cod_statut_benef == 'A':
                if vals['plafond_transaction_temp']:
                    cr.execute(
                        "update mcisogem_bareme set plf_prest_assure=%s,  plf_prest_conj=%s, plf_prest_enfant=%s where id=%s",
                        (vals['plafond_transaction_temp'], 0, 0, ids[0]))
                else:
                    cr.execute(
                        "update mcisogem_bareme set plf_prest_assure=%s,  plf_prest_conj=%s, plf_prest_enfant=%s where id=%s",
                        (data['plafond_transaction_temp'], 0, 0, ids[0]))

            elif statut_benef_data.cod_statut_benef == 'C':
                if vals['plafond_transaction_temp']:
                    cr.execute(
                        "update mcisogem_bareme set plf_prest_assure=%s,  plf_prest_conj=%s, plf_prest_enfant=%s where id=%s",
                        (0, vals['plafond_transaction_temp'], 0, ids[0]))
                else:
                    cr.execute(
                        "update mcisogem_bareme set plf_prest_assure=%s,  plf_prest_conj=%s, plf_prest_enfant=%s where id=%s",
                        (0, data['plafond_transaction_temp'], 0, ids[0]))

            else:
                if vals['plafond_transaction_temp']:
                    cr.execute(
                        "update mcisogem_bareme set plf_prest_assure=%s,  plf_prest_conj=%s, plf_prest_enfant=%s where id=%s",
                        (0, 0, vals['plafond_transaction_temp'], ids[0]))
                else:
                    cr.execute(
                        "update mcisogem_bareme set plf_prest_assure=%s,  plf_prest_conj=%s, plf_prest_enfant=%s where id=%s",
                        (0, 0, data['plafond_transaction_temp'], ids[0]))

        if 'ticm_assure' in vals:
            cr.execute("update mcisogem_bareme set ticm_assure=%s, ticm_conj=%s, ticm_enfant=%s where id=%s",
                       (vals['ticm_assure'], vals['ticm_assure'], vals['ticm_assure'], ids[0]))

        if 'bl_ticm_assure_tx' in vals:
            cr.execute(
                "update mcisogem_bareme set bl_ticm_assure_tx=%s, bl_ticm_conj_tx=%s, bl_ticm_enfant_tx=%s where id=%s",
                (vals['bl_ticm_assure_tx'], vals['bl_ticm_assure_tx'], vals['bl_ticm_assure_tx'], ids[0]))

        if 'unite_temps_id' in vals:
            unite_temps_data = self.pool.get('mcisogem.unite.temps').browse(cr, uid, vals['unite_temps_id'],
                                                                            context=context)
            cr.execute("update mcisogem_bareme set bar_unite_period=%s where id=%s",
                       (unite_temps_data.code_unite_temps, ids[0]))

        return super(mcisogem_bareme, self).write(cr, uid, ids, vals, context=context)
