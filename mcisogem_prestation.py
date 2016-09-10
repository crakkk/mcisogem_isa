# -*- coding:utf8 -*-
from pprint import pprint
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


# import erppeek


class mcisogem_brouillard_prestation_details(osv.osv):
    _name = 'mcisogem.brouillard.prestation.details'

    _inherit = ['ir.needaction_mixin']

    _mail_post_access = 'read'

    _columns = {
        'mode_paiement': fields.many2one('mcisogem.regime', ' Qualification de dépenses'),
        'centre_id': fields.many2one('mcisogem.centre', 'Centre'),
        'medecin_id': fields.many2one('mcisogem.praticien', 'Prescripteur'),
        'garant_id': fields.many2one('mcisogem.garant', 'Garant'),
        'num_fact': fields.char('N° Fact'),
        'periode_id': fields.many2one('mcisogem.account.period', 'Date Comptable'),
        'prestation_ids': fields.many2many('mcisogem.prestation', 'mcisogem_brouill_det_prest_rel', 'id_g', 'id_p',
                                           'Prestations'),
        'total_prest': fields.integer('Total prestataire'),
        'total_gest': fields.integer('Total Assureur'),
        'total_fact': fields.integer('Total Facture'),
        'prestation_brouillard_id': fields.many2one('mcisogem.brouillard.prestation')

    }


class mcisogem_brouillard_prestation(osv.osv):
    _name = 'mcisogem.brouillard.prestation'

    _inherit = ['ir.needaction_mixin']

    _mail_post_access = 'read'

    _columns = {
        'mode_paiement': fields.selection([
            ('TP', "Tiers payant"),
            ('RD', "Remboursement direct"),
          ] , "Qualification des dépenses" , required=True),

        'centre_id': fields.many2many('mcisogem.centre', 'mcisogem_brou_centre_rel', 'id_g', 'id_c', 'Centres'),
        'medecin_id': fields.many2one('mcisogem.praticien', 'Prescripteur'),
        'garant_id': fields.many2many('mcisogem.garant', 'mcisogem_brou_garant_rel', 'id_g', 'id_v', 'Garants'),
        'intermediaire_id': fields.many2many('mcisogem.courtier', 'mcisogem_brou_courtier_rel', 'id_c', 'id_v', 'Intermédiaires'),
        'souscripteur_id': fields.many2many('mcisogem.souscripteur', 'mcisogem_brou_souscripteur_rel', 'id_s', 'id_v',
                                             'Souscripteurs'),
        'police_id': fields.many2many('mcisogem.police', 'mcisogem_brou_police_rel', 'id_p', 'id_v',
                                            'polices'),

        'state': fields.selection([
            ('SS', "Prestation saisie"),
            ('VS', "Saisie validée"),
            ('P', "Payée"),
        ], 'Statut'),

        'user_id': fields.many2many('res.users', 'mcisogem_brou_user_rel', 'id_us', 'id_v',
                                      'Opérateurs'),

        'date_comptable': fields.date('Date Comptable', required=True),

        'num_fact': fields.char('N° Fact'),
        'periode_id': fields.many2one('mcisogem.account.period', 'Date Comptable', required=False),
        'prestation_ids': fields.many2many('mcisogem.prestation', 'mcisogem_brouill_prest_rel', 'id_g', 'id_p',
                                           'Prestations'),
        'total_prest': fields.integer(''),
        'total_gest': fields.integer(''),
        'total_fact': fields.integer(''),
        'total_patient': fields.integer(''),
        'total_total': fields.integer(''),
        'prestation_brouillard_details_id': fields.one2many('mcisogem.brouillard.prestation.details',
                                                            'prestation_brouillard_id'),

    }

    _rec_name = 'id'

    def onchange_param_rd(self, cr, uid, ids, garant_id,intermediaire_id,souscripteur_id,police_id,state,user_id,date_comptable, context=None):
        d = {}
        v = {}
        critere = []


        critere.append(('state', 'in', ['SS','VS','P']))

        if date_comptable:

            date_comptable = datetime.strptime(str(date_comptable), '%Y-%m-%d')
            code_periode = date_comptable.strftime('%m/%Y')
            periode_id = self.pool.get('mcisogem.account.period').search(cr, uid, [('code', '=', code_periode),
                                                                                   ('state', '=', 'Draft')])

            if periode_id:
                critere.append(('periode_id', '=', periode_id[0]))

        mode_paiement_ids = self.pool.get('mcisogem.regime').search(cr, uid, [
            ('code_regime', 'ilike', context.get('mode_paiement'))])

        critere.append(('mode_paiement', 'in', mode_paiement_ids))

        if len(intermediaire_id[0][2]) > 0:
            polices = self.pool.get('mcisogem.police').search(cr, uid, [
                ('courtier_id', 'in', intermediaire_id[0][2])])

            critere.append(('police_id', 'in',polices))

        if len(souscripteur_id[0][2]) > 0:
            polices = self.pool.get('mcisogem.police').search(cr, uid, [
                ('souscripteur_id', 'in', souscripteur_id[0][2])])

            critere.append(('police_id', 'in', polices))

        if len(police_id[0][2]) > 0:
            critere.append(('police_id', 'in', police_id[0][2]))

        if len(garant_id[0][2]) > 0:
            critere.append(('garant_id', 'in', garant_id[0][2]))

        if state:
            critere.append(('state', '=', state))

        if user_id[0][2]:
            critere.append(('create_uid', 'in', user_id[0][2]))


        d = {'prestation_ids': critere}

        p_ids = self.pool.get('mcisogem.prestation').search(cr,uid,critere)
        v = {'prestation_ids': p_ids}

        return {'domain': d, 'value': v}




    def onchange_param_tp(self, cr, uid, ids,garant_id, state , centre_id , num_fact,user_id , date_comptable, context=None):
        d = {}
        v = {}
        critere = []


        critere.append(('state', 'not in', ['SP', 'Draft']))

        if date_comptable:

            date_comptable = datetime.strptime(str(date_comptable), '%Y-%m-%d')
            code_periode = date_comptable.strftime('%m/%Y')
            periode_id = self.pool.get('mcisogem.account.period').search(cr, uid, [('code', '=', code_periode),
                                                                                   ('state', '=', 'Draft')])

            if periode_id:
                critere.append(('periode_id', '=', periode_id[0]))


        mode_paiement_ids = self.pool.get('mcisogem.regime').search(cr,uid,[('code_regime', 'ilike', context.get('mode_paiement'))])


        critere.append(('mode_paiement', 'in', mode_paiement_ids))

        if len(centre_id[0][2]) > 0:
            critere.append(('centre_id', 'in', centre_id[0][2]))

        if num_fact:
            critere.append(('num_fact', '=', num_fact))

        if state:
            critere.append(('state', '=', state))

        if len(garant_id[0][2]) > 0:
            critere.append(('garant_id', 'in', garant_id[0][2]))

        if len(centre_id[0][2]) > 0:
            critere.append(('garant_id', 'in', centre_id[0][2]))

        if user_id[0][2]:
            critere.append(('create_uid', 'in', user_id[0][2]))


        d = {'prestation_ids': critere}

        p_ids = self.pool.get('mcisogem.prestation').search(cr,uid,critere)
        v = {'prestation_ids': p_ids}

        return {'domain': d, 'value': v}


    def imprimer_brouillard(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)

        total_total = 0
        total_gest = 0
        total_patient = 0

        vals = self.browse(cr, uid, ids)

        if not vals.prestation_ids:
            raise osv.except_osv('Attention', 'Aucune prestation n\'a été choisie !')

        les_ids_prests = []

        for p in vals.prestation_ids:
            les_ids_prests.append(p.id)

        mode_paiement_ids = self.pool.get('mcisogem.regime').search(cr, uid, [
            ('code_regime', 'ilike', context.get('mode_paiement'))])[0]

        mode_paiement = self.pool.get('mcisogem.regime').browse(cr,uid,mode_paiement_ids).id

        centre_ids = vals.centre_id
        garant_ids = vals.garant_id

        date_comptable = datetime.strptime(str(vals.date_comptable), '%Y-%m-%d')
        code_periode = date_comptable.strftime('%m/%Y')
        periode_id = self.pool.get('mcisogem.account.period').search(cr, uid, [('code', '=', code_periode),
                                                                               ('state', '!=', 'Draft')])

        if periode_id:
            periode_id = periode_id[0]

            self.write(cr, uid, ids, {'periode_id': periode_id}, context=context)

        the_prestations = self.pool.get('mcisogem.prestation').search(cr, uid, [('id', 'in', les_ids_prests)])

        # ces listes seront utilisées au cas ou aucun centre ou garant n'a été selectionné
        the_centres = []
        the_garants = []
        the_centres_ids = []
        the_garants_ids = []

        if len(centre_ids) == 0:

            for p in self.pool.get('mcisogem.prestation').browse(cr, uid, the_prestations):

                if p.centre_id.id not in the_centres_ids:
                    the_centres_ids.append(p.centre_id.id)
                    the_centres.append(p.centre_id)

            the_prestations = self.pool.get('mcisogem.prestation').search(cr, uid, [('centre_id', 'in', the_centres_ids),
                                                                                    ('id', 'in', les_ids_prests)])

            centre_ids = the_centres

        if len(garant_ids) == 0:

            for p in self.pool.get('mcisogem.prestation').browse(cr, uid, the_prestations):

                if p.garant_id.id not in the_garants_ids:
                    the_garants_ids.append(p.garant_id.id)
                    the_garants.append(p.garant_id)

            the_centres = []
            the_centres_ids = []

            garant_ids = the_garants

        if len(centre_ids) == 0:
            the_prestations = self.pool.get('mcisogem.prestation').search(cr, uid, [('garant_id', 'in', the_garants_ids),
                                                                                    ('id', 'in', les_ids_prests)])

            for p in self.pool.get('mcisogem.prestation').browse(cr, uid, the_prestations):
                if p.centre_id.id not in the_centres_ids:
                    the_centres_ids.append(p.centre_id.id)
                    the_centres.append(p.centre_id)

            centre_ids = the_centres

        les_prestations = []

        for p in self.browse(cr, uid, ids).prestation_ids:
            total_total += p.montant_total
            total_gest += p.part_gest
            total_patient += p.part_patient
            les_prestations.append(p.id)

        for c in centre_ids:

            for g in garant_ids:

                les_factures = []
                dat = {}

                dat['mode_paiement'] = mode_paiement
                dat['centre_id'] = c.id
                dat['garant_id'] = g.id
                dat['periode_id'] = periode_id
                dat['prestation_brouillard_id'] = ids[0]

                prestations_temp = self.pool.get('mcisogem.prestation').search(cr, uid, [('centre_id', '=', c.id),
                                                                                         ('garant_id', '=', g.id),
                                                                                         ('id', 'in', les_ids_prests)])

                for p in self.pool.get('mcisogem.prestation').browse(cr, uid, prestations_temp):

                    if p.num_fact not in les_factures:
                        les_factures.append(p.num_fact)

                for nf in les_factures:

                    prestations_temp = self.pool.get('mcisogem.prestation').search(cr, uid, [('centre_id', '=', c.id),
                                                                                             ('garant_id', '=', g.id),
                                                                                             ('num_fact', '=', nf),
                                                                                             ('id', 'in', les_ids_prests)])
                    dat['total_fact'] = 0
                    dat['num_fact'] = nf

                    for p in self.pool.get('mcisogem.prestation').browse(cr, uid, prestations_temp):
                        dat['total_fact'] += p.montant_total

                    ligne_ids = self.pool.get('mcisogem.brouillard.prestation.details').search(cr, uid, [
                     ('centre_id', '=', c.id), ('garant_id', '=', g.id),
                        ('prestation_brouillard_id', '=', ids[0]), ('num_fact', '=', nf)])

                    print(ligne_ids)
                    if len(ligne_ids) == 0:
                        last_id = self.pool.get('mcisogem.brouillard.prestation.details').create(cr, uid, dat, context)

        for g in garant_ids:
            total_assur = 0  # total assureur

            details_assur_ids = self.pool.get('mcisogem.brouillard.prestation.details').search(cr, uid, [
                ('prestation_brouillard_id', '=', ids[0]), ('garant_id', '=', g.id)])

            for d in self.pool.get('mcisogem.brouillard.prestation.details').browse(cr, uid, details_assur_ids):
                total_assur += d.total_fact

            for c in centre_ids:
                total_prestataire = 0  # total centre
                details_centre_ids = self.pool.get('mcisogem.brouillard.prestation.details').search(cr, uid, [
                    ('prestation_brouillard_id', '=', ids[0]), ('centre_id', '=', c.id), ('garant_id', '=', g.id)])

                for d in self.pool.get('mcisogem.brouillard.prestation.details').browse(cr, uid, details_centre_ids):
                    total_prestataire += d.total_fact

                for d in details_centre_ids:
                    self.pool.get('mcisogem.brouillard.prestation.details').write(cr, uid, d,
                                                                                  {'total_prest': total_prestataire})

            for d in details_assur_ids:
                self.pool.get('mcisogem.brouillard.prestation.details').write(cr, uid, d, {'total_gest': total_assur})

        ct = []
        gr = []

        for p in centre_ids:
            ct.append(p.id)

        for p in garant_ids:
            gr.append(p.id)

        if not vals.centre_id:

            for c_rel in ct:
                cr.execute('insert into mcisogem_brou_centre_rel(id_g , id_c) values(%s , %s)', (ids[0], c_rel,))

        if not vals.garant_id:

            for g_rel in gr:
                cr.execute('insert into mcisogem_brou_garant_rel(id_g , id_v) values(%s , %s)', (ids[0], g_rel,))

        for c in ct:

            ps = self.pool.get('mcisogem.prestation').search(cr, uid,
                                                             [('centre_id', '=', c),
                                                              ('id', 'in', les_ids_prests), ('id', 'in', les_ids_prests)])

            if not ps:
                cr.execute('delete from mcisogem_brou_centre_rel where id_g = %s and id_c = %s', (ids[0], c,))

        for g in gr:
            ps = self.pool.get('mcisogem.prestation').search(cr, uid,
                                                             [('garant_id', '=', g),
                                                              ('id', 'in', les_ids_prests), ('id', 'in', les_ids_prests)])

            if not ps:
                cr.execute('delete from mcisogem_brou_garant_rel where id_g = %s and id_v = %s', (ids[0], g,))

        totaux = {}

        totaux['total_total'] = total_total
        totaux['total_gest'] = total_gest
        totaux['total_patient'] = total_patient

        data[0]['centre_id'] = ct
        data[0]['garant_id'] = gr
        data[0]['total_total'] = total_total
        data[0]['total_gest'] = total_gest
        data[0]['total_patient'] = total_patient

        w_id = self.write(cr, uid, ids, totaux)

        data = self.read(cr, uid, ids, [], context=context)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'mcisogem_isa.report_brouillard',
            'data': data,
        }


class mcisogem_validation_prestation(osv.osv):
    _name = 'mcisogem.validation.prestation'

    _inherit = ['ir.needaction_mixin']

    _mail_post_access = 'read'

    _columns = {
        'mode_paiement_': fields.selection([
            ('TP', "Tiers payant"),
            ('RD', "Remboursement direct"),
          ] , "Qualification des dépenses" , required=True),

        'num_fact': fields.char('N° Facture'),

        'num_prest' : fields.integer('N° de la prestation'),

        'centre_ids': fields.many2many('mcisogem.centre', 'mcisogem_valid_prest_centre_rel', 'id_g', 'id_c', 'Centres'),

        'date_comptable': fields.date('Date Comptable', required=False),

        'type_centre_id' : fields.many2one('mcisogem.type.centre' , 'Type de centre'),

        'user_ids': fields.many2many('res.users', 'mcisogem_valid_prest_user_rel', 'id_u', 'id_v', 'Opérateurs'),


        'garant_ids': fields.many2many('mcisogem.garant', 'mcisogem_valid_prest_garant_rel', 'id_g', 'id_v', 'Garants'),

        'souscripteur_id': fields.many2one('mcisogem.souscripteur', 'Souscripteur'),

        'police_ids': fields.many2many('mcisogem.police', 'mcisogem_valid_prest_police_rel', 'id_pol',
                                             'id_v', 'Polices'),

        'periode_ids': fields.many2one('mcisogem.account.period', 'Date Comptable'),

        'prestation_ids': fields.many2many('mcisogem.prestation', 'mcisogem_valid_prest_prest_rel', 'id_g', 'id_p',
                                           'Prestations'),

        'montant_cumul': fields.integer('Montant' , readonly=True),


    }

    _rec_name = 'id'

    def onchange_souscripteur(self, cr, uid, ids, souscripteur_id):
        if souscripteur_id:
            les_polices = self.pool.get('mcisogem.police').search(cr, uid, [('souscripteur_id', '=', souscripteur_id)])

            d = {}
            d = {'police_ids': [('id', 'in', les_polices)]}

            return {'domain': d}


    def onchange_type_centre(self,cr,uid,ids,type_centre_id):
        if type_centre_id:
            les_centres = self.pool.get('mcisogem.centre').search(cr,uid,[('code_type_centre' , '=' , type_centre_id)])
            d = {}
            d = {'centre_ids': [('id' , 'in' , les_centres)]}

            return {'domain' : d}

    def onchange_pram(self, cr, uid, ids, mode_paiement, centre_ids, garant_ids, date_comptable, num_fact,user_ids,police_ids,num_prest,
                      context=None):
        d = {}
        critere = []
        montant_cumul = 0
        critere.append(('state', '=', 'SS'))

        centres = centre_ids[0][2]
        garants = garant_ids[0][2]
        users = user_ids[0][2]
        polices = police_ids[0][2]


        if date_comptable:

            date_comptable = datetime.strptime(str(date_comptable), '%Y-%m-%d')
            code_periode = date_comptable.strftime('%m/%Y')
            periode_id = self.pool.get('mcisogem.account.period').search(cr, uid, [('code', '=', code_periode),
                                                                                   ('state', '!=', 'Draft')])

            if periode_id:
                critere.append(('periode_id', '=', periode_id[0]))

        if mode_paiement:
            mode_paiement_ids = self.pool.get('mcisogem.regime').search(cr, uid,
                                                                        [('code_regime', 'ilike', mode_paiement)])

            critere.append(('mode_paiement', 'in', mode_paiement_ids))


        if num_fact:
            critere.append(('num_fact', '=', num_fact))

        if num_prest:
            critere.append(('id', '=', num_prest))


        if len(centres) > 0:
            critere.append(('centre_id', 'in', centres))

        if len(garants) > 0:
            critere.append(('garant_id', 'in', garants))

        if len(users) > 0:
            critere.append(('create_uid', 'in', users))

        if len(polices) > 0:
            critere.append(('police_id', 'in', polices))


        d = {'prestation_ids': critere}
        p_ids = self.pool.get('mcisogem.prestation').search(cr, uid, critere)

        for p in self.pool.get('mcisogem.prestation').browse(cr,uid,p_ids):
            montant_cumul += p.montant_total

        v = {}
        v = {'prestation_ids': p_ids , 'montant_cumul' : montant_cumul}

        return {'domain': d, 'value': v}

    def _needaction_count(self, cr, uid, ids, context=None):
        cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
        lesgroups = cr.dictfetchall()
        if len(lesgroups) > 0:
            for group in lesgroups:
                group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
                if group_obj.name == "RESPONSABLE PRESTATION" or group_obj.name == "UTILISATEUR PRESTATION":
                    return self.pool.get('mcisogem.prestation').search_count(cr, uid, [('state', '=', 'SS')])

    def create(self, cr, uid, data, context=None):

        prestations = data['prestation_ids'][0][2]

        if len(prestations) == 0:
            raise osv.except_osv('Attention !', 'Aucune prestation choisie.')

        for prest in prestations:
            self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'state': 'VS'}, context=context)

        last_id = super(mcisogem_validation_prestation, self).create(cr, uid, data, context=context)
        return last_id


class mcisogem_validation_reception(osv.osv):
    _name = 'mcisogem.validation.reception'

    _inherit = ['ir.needaction_mixin']

    _mail_post_access = 'read'

    _columns = {
        'num_fact': fields.char('N° Facture'),
        'centre_ids': fields.many2many('mcisogem.centre', 'mcisogem_valid_recep_centre_rel', 'id_g', 'id_c', 'Centres'),

        'action': fields.selection([
            ('V', "Valider"),
            ('S', "Supprimer"),
        ], 'Action à exécuter', required=True),

        'garant_ids': fields.many2many('mcisogem.garant', 'mcisogem_valid_recep_garant_rel', 'id_g', 'id_v', 'Garants'),
        'periode_ids': fields.many2one('mcisogem.account.period', 'Date Comptable'),
        'prestation_ids': fields.many2many('mcisogem.prestation', 'mcisogem_valid_recep_prest_rel', 'id_g', 'id_p',
                                           'Prestations'),

    }

    _rec_name = 'id'

    def onchange_pram(self, cr, uid, ids, centre_ids, garant_ids, periode_ids, num_fact, context=None):
        d = {}
        p = {}
        critere = []

        critere.append(('state', '=', 'SP'))

        centres = centre_ids[0][2]

        garants = garant_ids[0][2]
        periodes = periode_ids


        if num_fact:
            critere.append(('num_fact', '=', num_fact))

        if periodes:
            critere.append(('periode_id', '=', periodes))

        if len(centres) > 0:
            critere.append(('centre_id', 'in', centres))

        if len(garants) > 0:
            critere.append(('garant_id', 'in', garants))

        d = {'prestation_ids': critere}

        p_ids = self.pool.get('mcisogem.prestation').search(cr, uid, critere)
        v = {'prestation_ids': p_ids}

        return {'domain': d, 'value': v}


    def _needaction_count(self, cr, uid, ids, context=None):
        cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
        lesgroups = cr.dictfetchall()
        if len(lesgroups) > 0:
            for group in lesgroups:
                group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
                if group_obj.name == "RESPONSABLE PRESTATION" or group_obj.name == "UTILISATEUR PRESTATION":
                    return self.pool.get('mcisogem.prestation').search_count(cr, uid, [('state', '=', 'SP')])

    def create(self, cr, uid, data, context=None):

        prestations = data['prestation_ids'][0][2]

        if len(prestations) == 0:
            raise osv.except_osv('Attention !', 'Aucune prestation choisie.')

        v = {}
        if data['action'] == 'V':
            v['state'] = 'SS'
        else:
            v['state'] = 'Draft'

        for prest in prestations:
            self.pool.get('mcisogem.prestation').write(cr, uid, prest, v, context=context)

        last_id = super(mcisogem_validation_reception, self).create(cr, uid, data, context=context)
        return last_id


class mcisogem_validation_prestation_direction(osv.osv):
    _name = 'mcisogem.validation.prestation.direction'

    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    _columns = {
        'centre_ids': fields.many2many('mcisogem.centre', 'mcisogem_valid_dir_centre_rel', 'id_g', 'id_c', 'Centres'),

        'garant_ids': fields.many2many('mcisogem.garant', 'mcisogem_valid_dir_garant_rel', 'id_g', 'id_v', 'Garants'),

        'periode_ids': fields.many2one('mcisogem.account.period', 'Date Comptable'),

        'date_comptable': fields.date('Date comptable', help='Date comptable'),

        'prestation_ids': fields.many2many('mcisogem.prestation', 'mcisogem_valid_dir_prest_rel', 'id_g', 'id_p',
                                           'Prestations'),

        'prestation_temp_ids': fields.many2many('mcisogem.prestation.recherche.result',
                                                'mcisogem_valid_dir_prest_temp_rel', 'id_g', 'id_p', 'Prestations')

    }

    _rec_name = 'id'

    def onchange_pram(self, cr, uid, ids,garant_ids, date_comptable, context=None):
        d = {}
        critere = []

        critere.append(('state', '!=', 'VD'))

        critere.append(('mode_paiement' , 'ilike' , context.get('code_regime')))
        garants = garant_ids[0][2]



        if date_comptable:

            date_comptable = datetime.strptime(str(date_comptable), '%Y-%m-%d')
            code_periode = date_comptable.strftime('%m/%Y')
            periode_id = self.pool.get('mcisogem.account.period').search(cr, uid, [('code', '=', code_periode),
                                                                                   ('state', '!=', 'Draft')])

            if periode_id:
                critere.append(('periode_id', '=', periode_id[0]))


        critere.append(('garant_id', 'in', garants))

        d = {'prestation_temp_ids': critere}
        p_ids = self.pool.get('mcisogem.prestation.recherche.result').search(cr, uid, critere)

        v = {}
        v = {'prestation_temp_ids': p_ids}

        return {'domain': d, 'value': v}

    def _needaction_count(self, cr, uid, ids, context=None):
        cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
        lesgroups = cr.dictfetchall()
        if len(lesgroups) > 0:
            for group in lesgroups:
                group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
                if group_obj.name == "RESPONSABLE PRESTATION" or group_obj.name == "UTILISATEUR PRESTATION":
                    return self.pool.get('mcisogem.prestation.recherche.result').search_count(cr, uid,
                                                                                              [('state', '!=', 'VD') , ('mode_paiement', 'ilike', context.get('code_regime'))])

    def create(self, cr, uid, data, context=None):

        prestations = data['prestation_temp_ids'][0][2]

        if len(prestations) == 0:
            raise osv.except_osv('Attention !', 'Aucune prestation choisie.')

        for prest in prestations:
            last_id = self.pool.get('mcisogem.prestation.recherche.result').write(cr, uid, prest, {'state': 'VD'},
                                                                                  context=context)

            les_prests = self.pool.get('mcisogem.prestation').search(cr, uid, [('regroup_id', '=', prest)])

            for pr in les_prests:
                self.pool.get('mcisogem.prestation').write(cr, uid, pr, {'state': 'VD'}, context=context)

        msg = str(
            "Des prestations ont été validées au niveau de la direction. Merci de valider les Règlements/Remboursements au niveau de la comptabilité.")

        cr.execute("select id from res_groups where name='RESPONSABLE COMPTABLE' or name='UTILISATEUR COMPTABLE'")
        groupe_ids = cr.dictfetchall()

        for groupe_id in groupe_ids:

            groupe_id = groupe_id['id']

            cr.execute('select uid from res_groups_users_rel  where gid=%s', (groupe_id,))

            user_ids = cr.fetchall()

            les_ids = []
            for u_id in user_ids:
                les_ids.append(u_id[0])

            res_users = self.pool['res.users']
            partner_ids = list(set(u.partner_id.id for u in res_users.browse(cr, uid, les_ids, context)))

            self.message_post(
                cr, uid, False,
                body=msg,
                partner_ids=partner_ids,
                subtype='mail.mt_comment',
                subject="[ISAWEB] - Validation comptable",
                context=context
            )

        return super(mcisogem_validation_prestation_direction, self).create(cr, uid, data, context=context)

    # data['periode_ids'][0][1] = last_id
    # return self.pool.get('mcisogem.validation.prestation.direction').write(cr, uid, last_id , data, context=context)


class mcisogem_validation_prestation_reglement(osv.osv):
    _name = 'mcisogem.validation.prestation.reglement'
    _inherit = ['ir.needaction_mixin', 'mail.thread']

    _mail_post_access = 'read'

    _columns = {

        'action': fields.selection([
            ('R', "Créer le(s) règlement(s)"),
            ('S', "Invalider"),
        ], 'Action à exécuter', required=True),

        'montant_cumul': fields.integer('Montant', readonly=True),

        'benef_ids': fields.many2many('mcisogem.benef', 'regl_benef_rel', 'id_b', 'id_v', 'Bénéficiaires'),
        'centre_ids': fields.many2many('mcisogem.centre', 'regl_centre_rel', 'id_g', 'id_c', 'Centres'),
        'num_fact': fields.char('N° Facture'),
        'date_comptable': fields.date('Date comptable', help='date comptable'),
        'date_reglement': fields.date('Date règlement'),
        'date_remboursement': fields.date('Date de remboursement'),


        'garant_ids': fields.many2many('mcisogem.garant', 'regl_garant_rel', 'id_g', 'id_v', 'Garants'),
        'periode_ids': fields.many2one('mcisogem.account.period', 'Date Comptable'),
        'prestation_ids': fields.many2many('mcisogem.prestation', 'regl_prest_rel', 'id_g', 'id_p', 'Prestations'),

    }

    _rec_name = 'id'

    _defaults = {
        'action': 'R',
        'date_reglement': time.strftime("%Y-%m-%d"),
        'date_remboursement': time.strftime("%Y-%m-%d")
    }

    def onchange_pram(self, cr, uid, ids, garant_ids, date_comptable,  context=None):
        d = {}
        critere = []
        montant_cumul = 0

        critere.append(('state', '=', 'VS'))

        garants = garant_ids[0][2]

        if context.get('code_regime'):
            codereg = self.pool.get('mcisogem.regime').search(cr,uid,[('code_regime' , 'ilike' , context.get('code_regime'))])

            critere.append(('mode_paiement', 'in', codereg))


        if date_comptable:

            date_comptable = datetime.strptime(str(date_comptable), '%Y-%m-%d')
            code_periode = date_comptable.strftime('%m/%Y')
            periode_id = self.pool.get('mcisogem.account.period').search(cr, uid, [('code', '=', code_periode),
                                                                                   ('state', '!=', 'Draft')])

            if periode_id:
                critere.append(('periode_id', '=', periode_id[0]))


        if len(garants) > 0:
            critere.append(('garant_id', 'in', garants))

        d = {'prestation_ids': critere}
        p_ids = self.pool.get('mcisogem.prestation').search(cr, uid, critere)

        for p in self.pool.get('mcisogem.prestation').browse(cr, uid, p_ids):
            montant_cumul += p.montant_total

        v = {}
        v = {'prestation_ids': p_ids, 'montant_cumul': montant_cumul}

        return {'domain': d, 'value': v}

    def _needaction_count(self, cr, uid, ids, context=None):
        cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
        lesgroups = cr.dictfetchall()
        if len(lesgroups) > 0:
            for group in lesgroups:
                group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
                if group_obj.name == "RESPONSABLE PRESTATION" or group_obj.name == "UTILISATEUR PRESTATION":
                    return self.pool.get('mcisogem.prestation').search_count(cr, uid, [('state', 'in', ['VS'])])

    def create(self, cr, uid, data, context=None):
        prestations = data['prestation_ids'][0][2]

        les_benef = []

        cr.execute("delete from mcisogem_centre_temp where create_uid=%s", (uid,))
        cr.execute("delete from mcisogem_garant_temp where create_uid=%s", (uid,))
        cr.execute("delete from mcisogem_prestation_recherche_temp where create_uid=%s", (uid,))
        cr.execute("delete from mcisogem_prestation_recherche_result where create_uid=%s", (uid,))
        cr.execute("delete from mcisogem_prestation_recherche_result where state=%s", ('P',))
        cr.execute("delete from mcisogem_prestation_temp where create_uid=%s", (uid,))
        cr.execute("delete from mcisogem_prest_temp where create_uid=%s", (uid,))


        if len(prestations) == 0:
            raise osv.except_osv('Attention !',
                                 'Vous devez ajouter au moins un sinistre avant de faire le regroupement.')

        for prest in prestations:
            prestation_data = self.pool.get('mcisogem.prestation').browse(cr, uid, prest)

            if prestation_data.state == 'P':
                raise osv.except_osv('Attention !', 'Un des sinistres que vous avez selectionner à  déjà été payé.')

        for prest in prestations:
            prestation_data = self.pool.get('mcisogem.prestation').browse(cr, uid, prest)
            cr.execute("insert into mcisogem_prest_temp (prest_id,create_uid) values(%s,%s)", (prestation_data.id, uid))
            cr.execute("select * from mcisogem_centre_temp where centre_id=%s and create_uid=%s",
                       (prestation_data.centre_id.id, uid))

            lescentres = cr.dictfetchall()
            cr.execute("select * from mcisogem_garant_temp where garant_id=%s and create_uid=%s",
                       (prestation_data.garant_id.id, uid))

            lesgarants = cr.dictfetchall()

            if len(lescentres) == 0:
                cr.execute("insert into mcisogem_centre_temp (centre_id,create_uid) values(%s,%s)",
                           (prestation_data.centre_id.id, uid))
            if len(lesgarants) == 0:
                cr.execute("insert into mcisogem_garant_temp (garant_id,create_uid) values(%s,%s)",
                           (prestation_data.garant_id.id, uid))

            if context.get('code_regime') == 'RD':

                if not prestation_data.beneficiaire_id.id in les_benef:

                    les_benef.append(prestation_data.beneficiaire_id.id)




        centre_table = self.pool.get('mcisogem.centre.temp').search(cr, uid, [('create_uid', '=', uid)])
        centre_ids = self.pool.get('mcisogem.centre.temp').browse(cr, uid, centre_table)

        garant_table = self.pool.get('mcisogem.garant.temp').search(cr, uid, [('create_uid', '=', uid)])
        garant_ids = self.pool.get('mcisogem.garant.temp').browse(cr, uid, garant_table)

        # if context.get('code_regime') == 'RD':



        for centre in centre_ids:

            for garant in garant_ids:
                # elem_table = self.search(cr,uid,[('id','=',ids)])
                # elem_obj = self.browse(cr,uid,elem_table)


                montant_total = 0
                montant_exclu = 0
                part_gest = 0
                nbre_prestat = 0

                for val in prestations:

                    if prestation_data.centre_id.id == centre.centre_id.id and prestation_data.garant_id.id == garant.garant_id.id:
                        montant_total += prestation_data.montant_total
                        montant_exclu += prestation_data.montant_exclu
                        nbre_prestat += 1
                vals = {}

                vals['centre_id'] = centre.centre_id.id
                vals['garant_id'] = garant.garant_id.id
                vals['montant_exclus'] = montant_exclu
                vals['montant_total'] = montant_total
                vals['nbre_prestat'] = nbre_prestat
                vals['banque_id'] = garant.garant_id.banque_id.id
                vals['code_journal'] = garant.garant_id.banque_id.code_journal
                vals['banque_int'] = garant.garant_id.cpt_tp2

                vals['mode_paiement'] = context.get('code_regime')

                vals['compte_tiers_prestataire'] = centre.centre_id.compta_prestat_tiers
                vals['compte_gle_prestataire'] = centre.centre_id.cpta_centre
                vals['state'] = "VF"


                for benef in les_benef:
                    vals['beneficiaire_id'] = benef
                    vals['banque_id'] = None
                    vals['code_journal'] = None
                    vals['banque_int'] = None




                    if prestation_data.beneficiaire_id.id == benef and prestation_data.garant_id.id == garant.garant_id.id:
                        montant_total += prestation_data.montant_total
                        montant_exclu += prestation_data.montant_exclu
                        nbre_prestat += 1




                    # Il y a t-il des prestations pour ce benef et le garant actuel ?
                    prest_existe = self.pool.get('mcisogem.prestation').search(cr, uid,
                                                                         [('beneficiaire_id', '=', benef),
                                                                          ('garant_id', '=',
                                                                           garant.garant_id.id)])


                    if prest_existe:
                        self.pool.get('mcisogem.prestation.temp').create(cr, uid, vals, context)

                        last_regroup_id = self.pool.get('mcisogem.prestation.recherche.result').create(cr, uid, vals,
                                                                                                       context)

                        for prest in prestations:

                            prestation_data = self.pool.get('mcisogem.prestation').browse(cr, uid, prest)

                            if prestation_data.beneficiaire_id.id == benef and prestation_data.garant_id.id == garant.garant_id.id:

                                for prest in prestations:

                                    prestation_data = self.pool.get('mcisogem.prestation').browse(cr, uid, prest)

                                    if prestation_data.centre_id.id == centre.centre_id.id and prestation_data.garant_id.id == garant.garant_id.id:

                                        self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'state': 'CRE',
                                                                                                    'date_remboursement': time.strftime(
                                                                                                        "%Y-%m-%d"),
                                                                                                    'regroup_id': last_regroup_id},
                                                                                   context=context)

                if context.get('code_regime') == 'TP':

                    if self.pool.get('mcisogem.prestation').search_count(cr, uid, [('centre_id', '=', centre.centre_id.id),
                                                                                   ('garant_id', '=',
                                                                                    garant.garant_id.id)]) > 0:

                        self.pool.get('mcisogem.prestation.temp').create(cr, uid, vals, context)

                        last_regroup_id = self.pool.get('mcisogem.prestation.recherche.result').create(cr, uid, vals,
                                                                                                       context)

                        for prest in prestations:

                            prestation_data = self.pool.get('mcisogem.prestation').browse(cr, uid, prest)

                            if prestation_data.centre_id.id == centre.centre_id.id and prestation_data.garant_id.id == garant.garant_id.id:

                                self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'state': 'CRL',
                                                                                            'date_reglement': time.strftime(
                                                                                                "%Y-%m-%d"),
                                                                                            'regroup_id': last_regroup_id},
                                                                           context=context)



        return super(mcisogem_validation_prestation_reglement, self).create(cr, uid, data, context=context)

    # def create(self, cr, uid, data, context=None):

    # 	prestations = data['prestation_ids'][0][2]

    # 	if len(prestations) == 0:
    # 		raise osv.except_osv('Attention !' ,'Aucune prestation choisie.' )

    # 	for prest in prestations:
    # 		if self.pool.get('mcisogem.regime').browse(cr,uid,data['mode_paiement']).code_regime == 'TP':

    # 			self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'state':'CRL' ,'date_reglement' : time.strftime("%Y-%m-%d") } , context=context)

    # 		else:

    # 			self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'state':'CRE' , 'date_remboursement' : time.strftime("%Y-%m-%d")} , context=context)



    # 	last_id = super(mcisogem_validation_prestation_reglement , self).create(cr, uid, data, context=context)
    # 	return last_id


class mcisogem_regroupement_prestation(osv.osv):
    _name = 'mcisogem.regroupement.prestation'

    _inherit = ['ir.needaction_mixin']

    _mail_post_access = 'read'

    def _get_centre(self, cr, uid, context=None):

        centre_id = self.pool.get('res.users').browse(cr, uid, uid).centre_id.id

        return centre_id

    def _get_les_praticiens(self, cr, uid, ids, context=None):

        centre = self._get_centre(cr, uid)
        rata_id = self.pool.get('mcisogem.agr.prestat').search(cr, uid, [('code_centre', '=', centre)])
        les_praticiens = []
        d = {}

        for med in self.pool.get('mcisogem.agr.prestat').browse(cr, uid, rata_id).praticien_ids:
            # if med.code_specialite.bl_prescr_autoris == True:

            les_praticiens.append(med.id)

        d = {'medecin_ids': [('id', 'in', les_praticiens)]}

        return {'domain': d}

    _columns = {
        'num_fact': fields.char('N° Facture', required=True),
        'medecin_ids': fields.many2many('mcisogem.praticien', 'mcisogem_regroup_prest_prat_rel', 'id_g', 'id_m',
                                        'Prescripteurs'),
        'garant_ids': fields.many2many('mcisogem.garant', 'mcisogem_regroup_prest_garant_rel', 'id_g', 'id_v',
                                       'Garants'),
        'periode_ids': fields.many2many('mcisogem.account.period', 'mcisogem_regroup_prest_period_rel', 'id_g', 'id_p',
                                        'Date Comptable'),
        'prestation_ids': fields.many2many('mcisogem.prestation', 'mcisogem_regroup_prest_prest_rel', 'id_g', 'id_p',
                                           'Prestations'),
        'init': fields.char(''),

    }

    _rec_name = 'num_fact'

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Attention !'), _('Impossible de dupliquer cet enregistrement.'))

    def onchange_pram(self, cr, uid, ids, medecin_ids, garant_ids, periode_ids, context=None):
        d = {}
        critere = []

        centre_id = self._get_centre(cr, uid)

        if centre_id == False:
            raise osv.except_osv('Attention!', "Vous n'êtes lié à aucun centre.")

        critere.append(('state', '=', 'SP'))
        critere.append(('create_uid', '=', uid))
        critere.append(('centre_id', '=', centre_id))

        medecins = medecin_ids[0][2]
        garants = garant_ids[0][2]
        periodes = periode_ids[0][2]

        if len(medecins) > 0:
            critere.append(('praticien_id', 'in', medecins))

        if len(garants) > 0:
            critere.append(('garant_id', 'in', garants))

        if len(periodes) > 0:
            critere.append(('periode_id', 'in', periodes))

        d = {'prestation_ids': critere}

        return {'domain': d}

    def create(self, cr, uid, data, context=None):

        prestations = data['prestation_ids'][0][2]

        if len(prestations) == 0:
            raise osv.except_osv('Attention !', 'Aucune prestation choisie.')

        for prest in prestations:
            self.pool.get('mcisogem.prestation').write(cr, uid, prest, {'num_fact': data['num_fact']}, context=context)

        last_id = super(mcisogem_regroupement_prestation, self).create(cr, uid, data, context=context)
        return last_id


class mcisogem_prestation_medicament(osv.osv):
    _name = 'mcisogem.prestation.medicament'
    _columns = {
        'acte_id': fields.many2one('mcisogem.nomen.prest', 'Famille'),
        'code_medicament': fields.integer('Code'),
        'name': fields.char('Libelle'),
        'ordo_ids': fields.one2many('mcisogem.prestation.ordornance', 'medicament_ids', 'Ordornance'),
    }


class mcisogem_type_exclusion_prestation(osv.osv):
    _name = 'mcisogem.type.exclusion.prestation'
    _columns = {
        'name': fields.char('Libelle', required=True)
    }

    def create(self, cr, uid, vals, context=None):
        vals['name'] = vals['name'].upper()
        return super(mcisogem_type_exclusion_prestation, self).create(cr, uid, vals, context=context)


class mcisogem_motif_exclusion_prestation(osv.osv):
    _name = 'mcisogem.motif.exclusion.prestation'
    _columns = {
        'name': fields.char('Libelle'),
        'type': fields.many2one('mcisogem.type.exclusion.prestation', 'Type', required=True),
    }

    def create(self, cr, uid, vals, context=None):
        vals['name'] = vals['name'].upper()
        return super(mcisogem_motif_exclusion_prestation, self).create(cr, uid, vals, context=context)


class mcisogem_motif_rejet_prestation(osv.osv):
    _name = 'mcisogem.motif.rejet.prestation'
    _columns = {
        'name': fields.char('Libelle', required=True)
    }

    def create(self, cr, uid, vals, context=None):
        vals['name'] = vals['name'].upper()
        return super(mcisogem_motif_rejet_prestation, self).create(cr, uid, vals, context=context)


class mcisogem_prestation_ordornance(osv.osv):
    _name = 'mcisogem.prestation.ordornance'
    _columns = {
        'acte_id': fields.many2one('mcisogem.nomen.prest', 'Famille'),
        'medicament_ids': fields.many2one('mcisogem.medicament', 'Medicaments', ),
        'prestation_ids': fields.many2one('mcisogem.prestation', 'Prestation', ),
        'quantite': fields.integer('Quantite'),
        'pu': fields.integer('Prix Unitaire'),
        'pharmacie': fields.boolean('Pharmacie ?'),
        't': fields.integer('T'),
    }

    def chargement(self, cr, uid, context=None):
        rech_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('libelle_court_famille', '=', 'FAR')])
        d = {}
        if not rech_ids:
            rech_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('libelle_court_famille', '=', 'PH')])

            if not rech_ids:
                rech_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('libelle_court_famille', '=', 'PHAR')])

        if rech_ids:
            d = {'acte_id': [('code_fam_prest', 'in', rech_ids), ('bl_nomen_envig', '=', False)]}
            v = {'t': rech_ids[0]}

        return rech_ids[0]

    def is_pharmacie(self, cr, uid, context=None):

        user = self.pool.get('res.users').browse(cr, uid, uid)

        if user.centre_id:
            centre = self.pool.get('mcisogem.centre').browse(cr, uid, user.centre_id.id)
            code_centre = centre.code_type_centre.name

            if code_centre == 'PHARMACIE':
                return True
            else:
                return False

        return False

    _defaults = {
        'pharmacie': is_pharmacie,
        't': chargement,

    }


class mcisogem_praticien_presta_tempo(osv.osv):
    _name = 'mcisogem.praticien.presta.tempo'
    _columns = {
        'praticien_id': fields.integer('Identifiant praticien'),
        'nom_prat': fields.char('Nom Medecin'),
        'prenom_prat': fields.char('Prenoms Medecin'),
        'nom_prenoms_prestat': fields.char('Prestataire')
    }
    _rec_name = 'nom_prenoms_prestat'


class mcisogem_acte_presta_tempo(osv.osv):
    _name = 'mcisogem.acte.presta.tempo'
    _columns = {
        'acte_id': fields.integer('Identifiant prestation'),
        'name': fields.char('Libelle'),

    }


class mcisogem_prestation_sous_acte(osv.osv):
    _name = "mcisogem.prestation.sous.actes"

    def _get_acte(self, cr, uid, context):
        return context.get('acte_id')

    _columns = {
        'prestation_id': fields.many2one('mcisogem.prestation', 'Prestation'),
        'acte_id': fields.many2one('mcisogem.nomen.prest', 'Acte'),
        'sous_acte_id': fields.many2one('mcisogem.sous.actes', 'Sous actes'),
        'qte': fields.integer('Quantité', required=True),

    }

    _defaults = {
        # 'acte' : _get_acte
    }
# def create(self, cr, uid, vals, context=None):
# 	vals['sous_acte_id'] = vals['sous_acte']
# 	return super(mcisogem_prestation_sous_acte, self).create(cr, uid, vals, context=context)


class mcisogem_sous_actes_temp(osv.osv):
    _name = "mcisogem.sous.actes.temp"
    _description = 'Sous Actes'
    _columns = {
        'code_acte': fields.many2one('mcisogem.nomen.prest', 'Acte'),
        'acte': fields.many2one('mcisogem.sous.actes', 'Sous Actes')
    }

    _rec_name = 'acte'


class mcisogem_prestation(osv.osv):
    _name = 'mcisogem.prestation'
    _description = 'Prestation'

    _inherit = ['ir.needaction_mixin']

    _mail_post_access = 'read'

    GROUPE = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ]

    SEXE = [
        ('M', 'Masculin'),
        ('F', 'Feminin')
    ]

    LIEN = [('E', 'Enfant'), ('C', 'Conjoint')]

    def a_droit(self, cr, uid, ids, field_name, arg, context=None):
        res = {}

        for prestation in self.pool.get('mcisogem.prestation').browse(cr, uid, ids, context):
            a_droit = False

            if self.pool.get('res.users').browse(cr, uid, uid).centre_id == prestation.centre_id:
                a_droit = True

            res[prestation.id] = a_droit

        return res

    def get_id(self , cr, uid, context):
        return context.get('id')

    def a_droit_search(self, cr, uid, obj, name, args, context=None):
        les_prestations = []

        les_ids = self.pool.get('mcisogem.prestation').search(cr, uid, [])

        for prestation in self.pool.get('mcisogem.prestation').browse(cr, uid, les_ids, context):

            if self.pool.get('res.users').browse(cr, uid, uid).centre_id == prestation.centre_id:
                les_prestations.append(prestation.id)

        return [('id', 'in', les_prestations)]

    # return super(mcisogem_prestation, self).search(cr, uid, args, offset, limit, order, context=context, count=count)

    def get_centre_gestion(self , cr , uid , context=None):
        centre_id = self.pool.get('mcisogem.centre.gestion').search(cr,uid,[] , limit=1)
        centre_data = self.pool.get('mcisogem.centre.gestion').browse(cr,uid,centre_id)
        return centre_data


    def onchange_acte(self, cr, uid, ids, acte_id, context=None):

        if acte_id:
            les_sous_actes = self.pool.get('mcisogem.sous.actes').search(cr, uid, [('code_acte', '=', acte_id)])
            d = {}
            v = {}
            if les_sous_actes:
                v['a_sous_acte'] = True
            else:
                v['a_sous_acte'] = False

            d = {'sous_acte_ids': [('sous_acte_id', 'in', les_sous_actes)]}

            return {'domain': d, 'value': v}

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)

    def _get_centre_user(self, cr, uid, context=None):

        centre_user_id = self.pool.get('res.users').browse(cr, uid, uid).centre_id.id
        if centre_user_id:
            centre = self.pool.get('mcisogem.centre').browse(cr, uid, centre_user_id, context=context)
            return centre.id
        else:
            return False

    def _get_recent_num_fact(self, cr, uid, mat, context=None):
        p_ids = self.pool.get('mcisogem.prestation').search(cr, uid, [('create_uid' , '=' , uid)], order='id desc', limit=1)

        if p_ids:
            num_fact = self.pool.get('mcisogem.prestation').browse(cr, uid, p_ids[0]).num_fact

            return num_fact

    _columns = {
        'garant_id': fields.many2one('mcisogem.garant', 'Garant'),

        'centre_user_id': fields.many2one('res.users', 'Utilisateur'),

        'centre_id': fields.many2one('mcisogem.centre', 'Centre exécutant'),

        'centre_exec_id': fields.many2one('mcisogem.centre', 'Centre prescripteur' , domain=[('code_type_centre.name','not in',['PHARMACIE' , 'IMAGERIE MEDICALE'  , 'OPTIQUE MEDICALE' , 'LABORATOIRE'])]),

        'college_id': fields.many2one('mcisogem.college', 'Collège'),

        'police_id': fields.many2one('mcisogem.police', 'Police'),

        'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice'),

        'affection_id': fields.many2one('mcisogem.affec', 'Affection', required=False),

        'a_sous_acte': fields.boolean('A un Sous-Acte ?'),

        'cout_total': fields.integer('Coût total'),

        'acte_phar_id': fields.many2one('mcisogem.nomen.prest', 'Prestation exécutée'),
    # acte ayant engendré la prestation en pharmacie
        'affec_phar_id': fields.many2one('mcisogem.affec', 'Affection'),
    # affection ayant engendré la prestation en pharmacie

        'praticien_acte_temp_id': fields.many2one('mcisogem.praticien.presta.tempo', 'Prescripteur'),

        'praticien_id': fields.many2one('mcisogem.praticien', 'Medecin Prescripteur'),

        'praticien_exec_id': fields.many2one('mcisogem.praticien', 'Medecin exécutant'),

        'periode_id': fields.many2one('mcisogem.account.period', 'Date comptable'),

        'dent_ids': fields.one2many('mcisogem.liste.dent', 'prestation_id', 'Dents'),

        'image': fields.binary("Image",
                               help="This field holds the image used as image for the product, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'mcisogem.prestation': (
                                            lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        },
                                        help="Medium-sized image of the product. It is automatically " \
                                             "resized as a 128x128px image, with aspect ratio preserved, " \
                                             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       store={
                                           'mcisogem.prestation': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       },
                                       help="Small-sized image of the product. It is automatically " \
                                            "resized as a 64x64px image, with aspect ratio preserved. " \
                                            "Use this field anywhere a small image is required."),

        'num_prestation': fields.integer('Numero :'),

        'matric_benef': fields.char('Matricule'),
        'code_regime': fields.char('Mode de remboursement'),

        'beneficiaire_id': fields.many2one('mcisogem.benef', 'Beneficiaire',
                                           help="Matricule ou Matricule ISA ou Matricule chez souscripteur"),

        'sexe': fields.selection(SEXE, 'Genre'),
        'nom_benef': fields.char('Nom'),
        'prenom_benef': fields.char('Prenoms'),
        'nom_prenom': fields.char('Nom & Prénoms'),
        'date_naiss': fields.date('Date'),
        'groupe_sg': fields.selection(GROUPE, 'Groupe sanguin', select=True),

        'souscripteur': fields.many2one('mcisogem.souscripteur', 'Souscripteur'),

        'Parente': fields.char('Parenté'),

        'affichebenef': fields.boolean(''),
        'affichdetail': fields.boolean(''),
        'aff_quantite': fields.boolean(''),
        'aff_hos_mat': fields.boolean(''),


        'base_remb': fields.integer('Base de remboursement'),


        'montant_total': fields.integer('Cout Total', readonly=False, required=True),
        'montant_exclu': fields.integer('Montant Exclu'),
        'tick_mod': fields.integer('Ticket modérateur'),
        'taux_part_patient': fields.integer('Taux part du patient', readonly=True),
        'part_patient': fields.integer('Part du patient', readonly=True),
        'taux_part_gest': fields.integer('Taux part du gestionnaire'),
        'part_gest': fields.integer('Montant reclamé'),

        'date_prest': fields.date('Date de la prestation'),
        'date_paiement': fields.date('Date de paiement'),
        'date_comptable': fields.date('Date comptable'),
        'date_recep': fields.date('Date de reception'),
        'date_remboursement': fields.date('Date de remboursement'),
        'date_reglement': fields.date('Date de règlements'),
        'ecriture_id': fields.many2one('mcisogem.ecriture.comptable'),
        'ordo_ids': fields.one2many('mcisogem.prestation.ordornance', 'prestation_ids', 'Médicaments'),
        'famille_acte_id': fields.many2one('mcisogem.fam.prest', 'Famille d\'acte '),
        'acte_id': fields.many2one('mcisogem.nomen.prest', 'Prestation exécutée', required=True),
        # 'sous_actes_ids' : fields.one2many('mcisogem.prestation.sous.actes.temp' , 'id' , 'Sous actes'),
        'sous_actes_ids': fields.one2many('mcisogem.prestation.sous.actes', 'prestation_id', 'Sous actes'),
        'num_cheque': fields.char('N° chèque'),
        'num_liasse': fields.char('N° Liasse'),
        'state': fields.selection([
            ('Draft', "Brouillon"),
            ('SP', "Prestation provisoire"),
            ('SS', "Prestation saisie"),
            ('VS', "Saisie validée"),
            ('CRL', "Règlement créer"),
            ('CRE', "Remboursement créer"),
            ('VD', "Validation direction"),
            ('VC', "Validation comptable"),
            ('P', "Payé"),
            ('GF', "Généré factures payées"),
        ], 'Statut', readonly=True),

        'num_bon': fields.char('N° du bon', required=False),
        'num_fact': fields.char('N° de Facture'),
        'mode_paiement': fields.many2one('mcisogem.regime', 'Type de remboursement'),


        'consultation': fields.boolean('CENTRES MEDICAUX'),
        'dentaire': fields.boolean('DENTAIRE'),
        'phamarcie': fields.boolean('PHARMACIE'),
        'acteenclinique': fields.boolean('ANALYSE'),
        'optique' : fields.boolean('OPTIQUE'),
        'radio' : fields.boolean('RADIO'),



        'quantite' : fields.integer('Quantite'),
        'date_hospi': fields.date('Date d\'hospitalisation'),
        'dure_demande': fields.integer('Durée en jours de la demande'),
        'erreur': fields.text('* Informations', readonly=True),
        'type_exclusion': fields.many2one('mcisogem.type.exclusion.prestation', 'Type d\'exclusion'),
        'motif_exclusion': fields.many2one('mcisogem.motif.exclusion.prestation', 'Motif d\'exclusion'),
        'motif_rejet': fields.many2one('mcisogem.motif.rejet.prestation', 'Motif de rejet'),
        'a_droit': fields.function(a_droit, type='boolean', string='Droit'),
        'type_centre': fields.char('type_centre'),
        'regroup_id': fields.many2one('mcisogem.prestation.recherche.result', 'Remboursement'),
        'date_comptable': fields.date('Date comptable'),

    }
    _defaults = {
        'centre_user_id': _get_centre_user,
        'centre_id': _get_centre_user,
        'affichebenef': False,
        'affichdetail': False,
        'quantite' : 1,
        'aff_quantite': False,
        'aff_hos_mat': False,
        'date_prest': time.strftime("%Y-%m-%d"),
        'date_recep': time.strftime("%Y-%m-%d"),
        'num_fact': _get_recent_num_fact,
        'state': 'Draft',
        # 'id' : get_id
    }

    _rec_name = "beneficiaire_id"

    def button_to_prestation(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()

        prestation_data = self.browse(cr, uid, ids[0], context=context)

        ctx['id'] = prestation_data.id

        tree_id = \
                self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa',
                                                                    'mcisogem_prestation_tree')[
                    1]

        if 'RD' in prestation_data.code_regime:
            form_id = \
                self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa',
                                                                    'mcisogem_prestation_mci_rd_form')[
                    1]

        else:
            form_id = \
                self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mcisogem_isa',
                                                                    'mcisogem_prestation_mci_form')[
                    1]

        return {
                'name': 'Prestations',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mcisogem.prestation',
                'res_id' : prestation_data.id,
                'views': [(form_id, 'form')],
                'view_id': form_id,
                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': ctx,
        }


    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Attention !'), _('Impossible de dupliquer cet enregistrement.'))

    def button_valider_prestation(self, cr, uid, ids, context=None):

        cr.execute('select num_bon from mcisogem_prestation where id = %s', (ids[0],))
        pr = cr.dictfetchone()

        num_bon = pr['num_bon']

        cr.execute("select * from mcisogem_prestation where state != 'Draft' and num_bon = %s and phamarcie != %s",
                   (num_bon, False,))
        pr_bon = cr.dictfetchall()

        for prest in pr_bon:
            if prest['num_bon'] == num_bon:
                raise osv.except_osv('Attention', 'Le numéro de bon n\'est plus valide')

        cr.execute("update mcisogem_prestation set state = 'SP' where id = %s", (ids[0],))
        # self.write(cr, uid, ids, {'state':'SP' , 'prescript'}, context=context)
        return True

    def valider_prestation(self, cr, uid, ids, context=None):

        cr.execute('select num_bon from mcisogem_prestation where id = %s', (ids[0],))
        pr = cr.dictfetchone()

        num_bon = pr['num_bon']

        cr.execute("select * from mcisogem_prestation where state != 'Draft' and num_bon = %s and phamarcie != %s",
                   (num_bon, False,))
        pr_bon = cr.dictfetchall()

        for prest in pr_bon:

            if prest['num_bon'] == num_bon:
                raise osv.except_osv('Attention', 'Le numéro de bon n\'est plus valide')

        cr.execute("update mcisogem_prestation set state = 'SP' where id = %s", (ids[0],))
        # self.write(cr, uid, ids, {'state':'SP' , 'prescript'}, context=context)
        return True

    def button_invalider_prestation(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'SP'}, context=context)
        return True

    def _get_benef_id(self, cr, uid, mat, context=None):
        # cette fonction retourne l ID du matricule passé en paramètre
        if mat:

            # benef_s = self.pool.get('mcisogem.benef').search(cr, uid,
            #                                                  ['|','|', ('name', '=', mat), ('matric_chez_souscr', '=', mat),
            #                                                   ('matric_isa', '=', mat)])


            benef_id_1 = self.pool.get('mcisogem.benef').search(cr, uid, [('name', '=', mat)])
            benef_id_2 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_chez_souscr', '=', mat)])
            benef_id_3 = self.pool.get('mcisogem.benef').search(cr, uid, [('matric_isa', '=', mat)])

            if benef_id_1:
                return self.pool.get('mcisogem.benef').browse(cr, uid, benef_id_1).id

            if benef_id_2:
                return self.pool.get('mcisogem.benef').browse(cr, uid, benef_id_2).id

            if benef_id_3:
                return self.pool.get('mcisogem.benef').browse(cr, uid, benef_id_3).id




        else:
            return False

    def _get_detail_bon(self, cr, uid, ids, num, context=None):

        if num:

            cr.execute(
                'select id , praticien_id ,  centre_id , beneficiaire_id , police_id , affection_id ,acte_id, taux_part_patient , centre_id from mcisogem_prestation where phamarcie =%s and num_bon =%s and state != %s limit 1',
                (False, num, 'Draft',))

            value = cr.dictfetchone()

            if value:

                prest_ids = []
                les_id = []

                cr.execute('select * from mcisogem_prestation_ordornance where prestation_ids = %s', (value['id'],))

                les_ids = cr.dictfetchall()

                for p in les_ids:
                    prest_ids.append(p['id'])

                    data = {}

                    data['acte_id'] = p['acte_id']

                    data['medicament_ids'] = p['medicament_ids']

                    data['quantite'] = p['quantite']

                    data['pu'] = p['pu']

                    the_id = self.pool.get('mcisogem.prestation.ordornance').create(cr, uid, data)

                    les_id.append(the_id)

                val = {}
                # val['taux_part_patient'] = self._get_ticket_moderateur(cr , uid, value['beneficiaire_id'] ,value['police_id'], value['centre_id'],value['acte_id'])

                val['police'] = value['police_id']
                val['acte_phar_id'] = value['acte_id']
                val['centre_id'] = value['centre_id']
                val['centre_exec_id'] = value['centre_id']
                val['ordo_ids'] = les_id

                val['praticien_id'] = value['praticien_id']
                val['affection_id'] = value['affection_id']
                val['affichdetail'] = True
                val['affec_phar_id'] = value['affection_id']

                return {'value': val}
            return False

    def check_dentaire(self, cr, uid, benef, police, exercice, num_dent, context=None):

        acte_DDC = self.pool.get('mcisogem.nomen.prest').search(cr, uid, [('libelle_court_acte', 'like', 'DDC')])
        acte_DDC_id = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, acte_DDC).id

        prests_ids = self.pool.get('mcisogem.prestation').search(cr, uid,
                                                                 [('beneficiaire_id', '=', benef),
                                                                  ('police_id', '=', police), ('dentaire', '=', True),
                                                                  ('exercice_id', '=', exercice.id),
                                                                  ('acte_id', '=', acte_DDC_id)])

        for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, prests_ids):

            for dent in prest.dent_ids:

                # on parcours les dents qui ont intervenu dans la prestation

                if dent.id == num_dent:
                    return True

        return False

    def _get_les_praticiens(self, cr, uid, ids, centre, context=None):

        type_centre = self.pool.get('mcisogem.centre').browse(cr, uid,
                                                              centre).code_type_centre.name


        rata_id = self.pool.get('mcisogem.agr.prestat').search(cr, uid, [('code_centre', '=', centre)])
        les_praticiens = []
        d = {}
        v = {}
        for med in self.pool.get('mcisogem.agr.prestat').browse(cr, uid, rata_id).praticien_ids:
            # if med.code_specialite.bl_prescr_autoris == True:
            les_praticiens.append(med.id)

        d = {'praticien_id': [('id', 'in', les_praticiens)]}
        v = {'type_centre' : type_centre}

        print('******* type de centre *************')
        print(type_centre)


        return {'domain': d , 'value' : v}

    def _get_details_benef(self, cr, uid, mat, context=None):
        # recuperer quelques informations sur le bénéficiaire
        benef_id = self._get_benef_id(cr, uid, mat)

        benef = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id)
        val = {}
        val['police_id'] = benef.police_id
        val['college_id'] = benef.college_id

        val['nom_benef'] = benef.nom
        val['prenom_benef'] = benef.prenom_benef
        val['nom_prenom'] = benef.nom + " " + benef.prenom_benef
        val['sexe'] = benef.sexe
        val['groupe_sg'] = benef.group_sang_benef
        val['date_naiss'] = benef.dt_naiss_benef
        val['beneficiaire_id'] = benef.id
        val['image'] = benef.image
        val['image_medium'] = benef.image_medium
        val['image_small'] = benef.image_small

        return val

    def _get_police_benef(self, cr, uid, mat, context=None):
        # recuperation des polices du beneficiaire
        benef_id = self._get_benef_id(cr, uid, mat, context)
        polices = []

        if benef_id:
            police_id = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id).police_id
            polices.append(police_id)

            p = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
                ('beneficiaire_id', '=', benef_id)], order='niveau ASC')

            if p:
                for police_id in self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid, p):
                    polices.append(police_id.police_id)

            return polices

    def check_existence_benef(self, cr, uid, mat, context=None):
        # on verifie l existence du beneficiaire dans la base
        if mat:
            nbre = self.pool.get('mcisogem.benef').search_count(cr, uid, [('name', '=', mat)])
            nbre_1 = self.pool.get('mcisogem.benef').search_count(cr, uid, [('matric_chez_souscr', '=', mat)])
            nbre_2 = self.pool.get('mcisogem.benef').search_count(cr, uid, [('matric_isa', '=', mat)])

            if nbre > 0 or nbre_1 > 0 or nbre_2 > 0:
                return True
            else:
                return False
        else:
            return False

    def check_state_benef(self, cr, uid, mat, date_prest, context=None):
        # on verifie le statut du beneficiaire

        if mat:
            benef_id = self._get_benef_id(cr, uid, mat, context)
            benef = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id)

            dt_effet = datetime.strptime(str(benef.dt_effet), '%Y-%m-%d')
            dt_today = date_prest

            if benef.statut == 'A':
                if dt_effet <= dt_today:

                    return True

                else:

                    return False
            else:
                return False
        else:
            return False

    def check_state_police(self, cr, uid, police, context=None):
        # verification de l etat d'une police
        police_state = self.pool.get('mcisogem.police').browse(cr, uid, police).state

        if police_state == 'draft':
            return True
        else:
            return False

    def check_age_benef(self, cr, uid, benef, police, college, date_prestation, context=None):

        # verification des conditions d age du bénéficiaire
        benef = self.pool.get('mcisogem.benef').browse(cr, uid, benef)
        dn_benef = benef.dt_naiss_benef
        date_new = date_prestation
        age_benef = (int(str(date_new)[0:4]) - int(str(dn_benef)[0:4]))

        histo_s = self.pool.get('mcisogem.histo.police').search(cr, uid,
                                                                [('name', '=', police), ('code_college', '=', college)])
        histo_data = self.pool.get('mcisogem.histo.police').browse(cr, uid, histo_s)

        min_age = histo_data.limite_age_pol
        max_age = histo_data.age_majorite_pol
        max_age_eleve = histo_data.age_majorite_eleve_pol

        if benef.code_statut in ['E', '']:

            if benef.eleve:

                if age_benef <= max_age_eleve or max_age_eleve == 0:

                    return True
                else:
                    return False

            if (age_benef >= min_age or max_age == 0) and (age_benef <= max_age or min_age == 0):
                return True

        else:

            if (age_benef >= min_age or min_age == 0) and (age_benef <= max_age or max_age == 0):
                return True

            return False

    def check_reseau_benef(self, cr, uid, centre, police, college, context=None):

        les_reseaux = []

        # on verifie si le beneficiaire est dans son réseau de soins

        les_data = self.pool.get('mcisogem.rata.reseau.police').search(cr, uid, [('police_id', '=', police),
                                                                                 ('college_id', '=', college)])

        for ld in self.pool.get('mcisogem.rata.reseau.police').browse(cr, uid, les_data):
            les_reseaux.append(ld.reseau_id.id)

        for res in les_reseaux:
            d = self.pool.get('mcisogem.tarif.nego.police').search(cr, uid, [('reseau_id', '=', res),
                                                                             ('centre_id', '=', centre)])

            if d:
                return True

        return False

    def check_acte(self, cr, uid, acte, police, centre, benef, date_prest, context=None):

        if context.get('code_regime'):
            return True

        # on va verifier si l'acte est couvert
        benef_id = self._get_benef_id(cr, uid, benef, context)

        benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id)

        centre_data = self.pool.get('mcisogem.centre').browse(cr, uid, centre)

        police_data = self.pool.get('mcisogem.police').browse(cr, uid, police)

        acte_data = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, acte)

        if police_data.type_regime == 'O' or police_data.type_regime == False:

            college = benef_data.college_id

        else:
            pol_comp_id = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
                ('beneficiaire_id', '=', benef_data.id), ('police_id', '=', police_data.id)])
            college = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid,
                                                                                          pol_comp_id).college_id

        if int(police_data.type_prime) == 1:
            # police par statut de beneficiaire


            nbre_bareme = self.pool.get('mcisogem.produit.police').search_count(cr, uid,
                                                                                [('police_id', '=', police_data.id),
                                                                                 ('college_id', '=', college.id),
                                                                                 ('acte_id', '=', acte_data.id), (
                                                                                 'statut_id', '=',
                                                                                 benef_data.statut_benef.id)])

            print('*************   bareme  *********')
            print(nbre_bareme)


        else:
            # police par tranche d'age

            nbre_bareme = self.pool.get('mcisogem.produit.police').search_count(cr, uid,
                                                                                [('college_id', '=', college.id),
                                                                                 ('acte_id', '=', acte_data.id)])

        if nbre_bareme > 0:

            exclu = False

            # on verifie si l'acte est exclu
            s = self.pool.get('mcisogem.act.excl.pol').search(cr, uid, [('police_id', '=', benef_data.police_id.id)])

            for d in self.pool.get('mcisogem.act.excl.pol').browse(cr, uid, s, context):

                for c in d.centre_ids:

                    if centre_data.id == c.id:

                        for ac in d.nomen_prest_ids:

                            if ac.id == acte_data.id:

                                if d.dat_eff_act_exc <= date_prest:
                                    exclu = True

            if exclu == True:

                return False

            else:

                # si l acte est soumis à entente préalable

                entente_s = self.pool.get('mcisogem.acte.entente.prealable').search(cr, uid, [])

                for data in self.pool.get('mcisogem.acte.entente.prealable').browse(cr, uid, entente_s):

                    for act in data.acte_ids:

                        if act.id == self.pool.get('mcisogem.nomen.prest').browse(cr, uid, acte):

                            entente_id = self.pool.get('mcisogem.entente').search(cr, uid,
                                                                                  [('beneficiaire_id', '=', benef),
                                                                                   ('centre_id', '=', centre),
                                                                                   ('acteent_id', '=', acte_data),
                                                                                   ('state', '=', 'valide')])

                            if entente_id:
                                return True
                            else:

                                return False
                return True





        else:
            return False

    def check_droit_prestation(self, cr, uid, acte, centre, benef, prescripteur, affection, date_prest, context=None):

        # prescripteur = self.pool.get('mcisogem.praticien.presta.tempo').browse(cr,uid,prescripteur).praticien_id
        benef_id = self._get_benef_id(cr, uid, benef, context)

        acte_consult_ids = []
        acte_consult = self.pool.get('mcisogem.nomen.prest').search(cr, uid,
                                                                    [('libelle_court_acte', 'in', ['C', 'CS'])],
                                                                    order='libelle_court_acte asc')

        for ac in self.pool.get('mcisogem.nomen.prest').browse(cr, uid, acte_consult):
            acte_consult_ids.append(ac.id)

        prest_du_jour = self.pool.get('mcisogem.prestation').search_count(cr, uid, [('beneficiaire_id', '=', benef),
                                                                                    ('centre_id', '=', centre),
                                                                                    ('praticien_id', '=', prescripteur),
                                                                                    ('date_prest', '=',
                                                                                     time.strftime("%Y-%m-%d")),
                                                                                    ('consultation', '=', False)])

        prest_du_jour_meme_acte = self.pool.get('mcisogem.prestation').search_count(cr, uid,
                                                                                    [('beneficiaire_id', '=', benef),
                                                                                     ('date_prest', '=', date_prest),
                                                                                     ('acte_id', '=', acte),
                                                                                     ('consultation', '=', False)])

        prest_consult_c = self.pool.get('mcisogem.prestation').search_count(cr, uid, [('beneficiaire_id', '=', benef),
                                                                                      ('centre_id', '=', centre),
                                                                                      ('date_prest', '=', date_prest), (
                                                                                      'acte_id', '=',
                                                                                      acte_consult_ids[0])])

        prest_consult_cs = self.pool.get('mcisogem.prestation').search_count(cr, uid, [('beneficiaire_id', '=', benef),
                                                                                       ('centre_id', '=', centre),
                                                                                       ('date_prest', '=', date_prest),
                                                                                       ('acte_id', '=',
                                                                                        acte_consult_ids[1])])

        prest_consult_cs_autre = self.pool.get('mcisogem.prestation').search_count(cr, uid,
                                                                                   [('beneficiaire_id', '=', benef),
                                                                                    ('date_prest', '=', date_prest), (
                                                                                    'acte_id', '=',
                                                                                    acte_consult_ids[1])])

        return True

    def check_droit_prestation2(self, cr, uid, acte, centre, benef, prescripteur, affection, date_prest, context=None):

        return True
        # prescripteur = self.pool.get('mcisogem.praticien.presta.tempo').browse(cr,uid,prescripteur).praticien_id
        benef_id = self._get_benef_id(cr, uid, benef, context)

        acte_consult_ids = []
        acte_consult = self.pool.get('mcisogem.nomen.prest').search(cr, uid,
                                                                    [('libelle_court_acte', 'in', ['C', 'CS'])],
                                                                    order='libelle_court_acte asc')

        for ac in self.pool.get('mcisogem.nomen.prest').browse(cr, uid, acte_consult):
            acte_consult_ids.append(ac.id)

        prest_du_jour = self.pool.get('mcisogem.prestation').search_count(cr, uid, [('beneficiaire_id', '=', benef),
                                                                                    ('centre_id', '=', centre),
                                                                                    ('praticien_id', '=', prescripteur),
                                                                                    ('date_prest', '=',
                                                                                     time.strftime("%Y-%m-%d")),
                                                                                    ('consultation', '=', False)])

        prest_du_jour_meme_acte = self.pool.get('mcisogem.prestation').search_count(cr, uid,
                                                                                    [('beneficiaire_id', '=', benef),
                                                                                     ('date_prest', '=', date_prest),
                                                                                     ('acte_id', '=', acte),
                                                                                     ('consultation', '=', False)])

        prest_consult_c = self.pool.get('mcisogem.prestation').search_count(cr, uid, [('beneficiaire_id', '=', benef),
                                                                                      ('centre_id', '=', centre),
                                                                                      ('date_prest', '=', date_prest), (
                                                                                      'acte_id', '=',
                                                                                      acte_consult_ids[0])])

        prest_consult_cs = self.pool.get('mcisogem.prestation').search_count(cr, uid, [('beneficiaire_id', '=', benef),
                                                                                       ('centre_id', '=', centre),
                                                                                       ('date_prest', '=', date_prest),
                                                                                       ('acte_id', '=',
                                                                                        acte_consult_ids[1])])

        prest_consult_cs_autre = self.pool.get('mcisogem.prestation').search_count(cr, uid,
                                                                                   [('beneficiaire_id', '=', benef),
                                                                                    ('date_prest', '=', date_prest), (
                                                                                    'acte_id', '=',
                                                                                    acte_consult_ids[1])])

        if acte in acte_consult_ids:

            if prest_consult_c > 0 and prest_consult_cs > 0:
                return False

            if acte == acte_consult_ids[0]:
                # consultation généraliste
                if prest_consult_c > 0:
                    return False

            else:

                # consultaion spécialiste
                if prest_consult_cs > 0:
                    return False

                if prest_consult_cs_autre > 1:
                    return False

        else:

            if prest_du_jour > 0:
                return False

            if prest_du_jour_meme_acte > 0:
                return False

        return True

    def check_delai(self, cr, uid, acte, centre, benef, pol, prescripteur,
                    date_prestation=time.strftime("%Y-%m-%d", time.localtime()), affection=None, context=None):

        if context.get('code_regime'):
            return True
        # on verifie le delai
        benef_id = self._get_benef_id(cr, uid, benef, context)

        benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id)
        acte_data = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, acte)
        police = self.pool.get('mcisogem.police').browse(cr, uid, pol)
        ecart = 0
        ecart_delai = 0
        nbre_jr_prescription = 0

        date_prestation = time.strftime("%Y-%m-%d", time.localtime())
        date_prestation = datetime.strptime(str(date_prestation), "%Y-%m-%d")

        if police.type_regime == 'O' or police.type_regime == False:

            college = benef_data.college_id

        else:
            pol_comp_id = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
                ('beneficiaire_id', '=', benef_data.id), ('police_id', '=', police.id)])
            college = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid,
                                                                                          pol_comp_id).college_id

        if int(police.type_prime) == 1:

            # police par statut
            bareme = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police.id),
                                                                               ('college_id', '=', college.id),
                                                                               ('acte_id', '=', acte_data.id), (
                                                                               'statut_id', '=',
                                                                               benef_data.statut_benef.id)])

            if bareme:
                nbre_jr_prescription = self.pool.get('mcisogem.produit.police').browse(cr, uid, bareme).delai

        else:

            # police par tranche d age
            bareme = self.pool.get('mcisogem.produit.police').search(cr, uid, [('college_id', '=', college.id),
                                                                               ('acte_id', '=', acte)])

            if bareme:
                nbre_jr_prescription = self.pool.get('mcisogem.produit.police').browse(cr, uid, bareme).delai

        # on recupere la toute dernière prestation du beneficiaire

        prest = self.pool.get('mcisogem.prestation').search(cr, uid, [('beneficiaire_id', '=', benef_data.id),
                                                                      ('acte_id', '=', acte)], limit=1, order='id desc')

        delai_carence = 0

        if prest:

            prest_data = self.pool.get('mcisogem.prestation').browse(cr, uid, prest)

            derniere_prest = prest_data.date_prest

            derniere_prest = datetime.strptime(str(derniere_prest), "%Y-%m-%d")

            ecart = (date_prestation - derniere_prest).days



        else:
            ecart = 999999999

        if ecart == 0:

            # prescripteur = self.pool.get('mcisogem.praticien.presta.tempo').browse(cr,uid,prescripteur).praticien_id

            if self.check_droit_prestation2(cr, uid, acte, centre, benef_id, prescripteur, affection, date_prestation,
                                            context) == True:
                return True

        delai_police = police.delai_carence

        delai_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police.id),
                                                                            ('college_id', '=', college.id),
                                                                            ('acte_id', '=', acte_data.id), (
                                                                            'statut_id', '=',
                                                                            benef_data.statut_benef.id)])

        delai = 0
        date_effet = benef_data.dt_effet
        date_effet = datetime.strptime(str(date_effet), "%Y-%m-%d")

        if delai_police > 0:
            ecart_delai = (date_prestation - date_effet).days

            if delai_police < ecart_delai:
                return True

            else:
                if not context.get('code_regime'):
                    raise osv.except_osv('Attention!', 'Le delai de carence de la police n\'est pas encore atteint')

        if delai_s:

            # il existe un delai de carence pour l acte
            for delai_data in self.pool.get('mcisogem.produit.police').browse(cr, uid, delai_s):
                delai = delai_data.delai

                ecart_delai = (date_prestation - date_effet).days

            if (delai) < ecart_delai:

                # checker intervalle de jour entre 2 actes
                interval_s = self.pool.get('mcisogem.intervalle2actes').search(cr, uid, [('code_acte', '=', acte), (
                'dt_eff_inter_2actes', '<', date_prestation)])
                interval_data = self.pool.get('mcisogem.intervalle2actes').browse(cr, uid, interval_s)

                if len(interval_data) > 0:

                    if interval_data.avecaffection:

                        cr.execute(
                            'select date_prest from mcisogem_prestation where affection_id = %s and  beneficiaire_id = %s order by id DESC',
                            (affection, benef_data.id))

                        if cr.fetchone():

                            derniere_prest = cr.fetchone()[0]
                            derniere_prest = datetime.strptime(str(derniere_prest), "%Y-%m-%d")

                            nbre_prest = len(cr.fetchone())
                            ecart = (date_prestation - derniere_prest).days

                            if ecart > interval_data.intervallejr and nbre_prest < interval_data.qteautorise:
                                return True
                            else:
                                if not context.get('code_regime'):
                                    raise osv.except_osv('Attention !',
                                                         'L\'intervalle de jours entre deux prestations pour cet acte n\'est pas atteint.')

                        else:

                            return True

                    else:

                        if interval_data.intervallejr < ecart:

                            return True


                        else:
                            if not context.get('code_regime'):
                                raise osv.except_osv('Attention !',
                                                     'L\'intervalle de jours entre deux prestations pour cet acte n\'est pas atteint.')

                else:
                    return True

            else:
                if not context.get('code_regime'):
                    raise osv.except_osv('Attention !',
                                         'Le bénéficiaire n\' pas encore atteint le delai de carence de l\'acte.')

        else:

            return True

    def check_delai2(self, cr, uid, acte, centre, benef, pol, prescripteur,
                     date_prestation=time.strftime("%Y-%m-%d", time.localtime()), affection=None, context=None):

        # on verifie le delai
        benef_id = self._get_benef_id(cr, uid, benef, context)

        benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id)
        acte_data = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, acte)
        police = self.pool.get('mcisogem.police').browse(cr, uid, pol)
        ecart = 0
        ecart_delai = 0
        nbre_jr_prescription = 0

        date_prestation = time.strftime("%Y-%m-%d", time.localtime())
        date_prestation = datetime.strptime(str(date_prestation), "%Y-%m-%d")

        if police.type_regime == 'O' or police.type_regime == False:

            college = benef_data.college_id

        else:
            pol_comp_id = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
                ('beneficiaire_id', '=', benef_data.id), ('police_id', '=', police.id)])
            college = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid,
                                                                                          pol_comp_id).college_id

        if int(police.type_prime) == 1:

            # police par statut
            bareme = self.pool.get('mcisogem.produit.police').search(cr, uid, [('college_id', '=', college.id),
                                                                               ('police_id', '=', police.id),
                                                                               ('acte_id', '=', acte_data.id), (
                                                                               'statut_id', '=',
                                                                               benef_data.statut_benef.id)])

            if bareme:
                nbre_jr_prescription = self.pool.get('mcisogem.produit.police').browse(cr, uid, bareme).delai
        else:

            # police par tranche d age
            bareme = self.pool.get('mcisogem.produit.police').search(cr, uid, [('college_id', '=', college.id),
                                                                               ('acte_id', '=', acte)])

            if bareme:
                nbre_jr_prescription = self.pool.get('mcisogem.produit.police').browse(cr, uid, bareme).delai

        # on recupere la toute dernière prestation du beneficiaire

        prest = self.pool.get('mcisogem.prestation').search(cr, uid, [('beneficiaire_id', '=', benef_data.id),
                                                                      ('acte_id', '=', acte)], limit=1, order='id desc')

        delai_carence = 0

        if prest:

            prest_data = self.pool.get('mcisogem.prestation').browse(cr, uid, prest)

            derniere_prest = prest_data.date_prest

            derniere_prest = datetime.strptime(str(derniere_prest), "%Y-%m-%d")

            ecart = (date_prestation - derniere_prest).days



        else:
            ecart = 999999999

        if ecart == 0:

            if self.check_droit_prestation2(cr, uid, acte, centre, benef_id, prescripteur, affection, date_prestation,
                                            context) == True:
                return True

        if nbre_jr_prescription <= ecart:

            delai_police = police.delai_carence

            delai_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police.id),
                                                                                ('college_id', '=', college.id),
                                                                                ('acte_id', '=', acte), (
                                                                                'statut_id', '=',
                                                                                benef_data.statut_benef.id)])

            delai = 0
            date_effet = benef_data.dt_effet
            date_effet = datetime.strptime(str(date_effet), "%Y-%m-%d")

            if delai_police > 0:
                ecart_delai = (date_prestation - date_effet).days

                if delai_police < ecart_delai:
                    return True

            if delai_s:

                # il existe un delai de carence pour l acte
                for delai_data in self.pool.get('mcisogem.produit.police').browse(cr, uid, delai_s):
                    delai = delai_data.delai

                    date_effet = benef_data.dt_effet
                    date_effet = datetime.strptime(str(date_effet), "%Y-%m-%d")

                    ecart_delai = (date_prestation - date_effet).days

                if (delai * 30) < ecart_delai:

                    # checker intervalle de jour entre 2 actes
                    interval_s = self.pool.get('mcisogem.intervalle2actes').search(cr, uid, [('code_acte', '=', acte), (
                    'dt_eff_inter_2actes', '<', date_prestation)])
                    interval_data = self.pool.get('mcisogem.intervalle2actes').browse(cr, uid, interval_s)

                    if len(interval_data) > 0:

                        if interval_data.avecaffection:
                            cr.execute(
                                'select date_prest from mcisogem_prestation where affection_id = %s and  beneficiaire_id = %s order by id DESC',
                                (affection, benef_data.id))

                            if cr.fetchone():

                                derniere_prest = cr.fetchone()[0]
                                derniere_prest = datetime.strptime(str(derniere_prest), "%Y-%m-%d")

                                nbre_prest = len(cr.fetchone())
                                ecart = (date_prestation - derniere_prest).days

                                if ecart > interval_data.intervallejr and nbre_prest < interval_data.qteautorise:
                                    return True

                            else:

                                return True

                        else:

                            if interval_data.intervallejr < ecart:

                                return True


                            else:

                                return False

                    else:
                        return True

                else:

                    return False

            else:

                return True
        else:
            return False

    def get_plafond(self, cr, uid, benef, police, college, acte, cout_acte, centre, exercice, affec,
                    date_prestation=time.strftime("%Y-%m-%d", time.localtime()), context=None):

        date_prestation = datetime.strptime(str(date_prestation), '%Y-%m-%d')

        # cout d acte represente la part que devra payer le gestionnaire
        police_data = self.pool.get('mcisogem.police').browse(cr, uid, police)
        benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef)
        centre_data = self.pool.get('mcisogem.centre').browse(cr, uid, centre)
        affection_data = self.pool.get('mcisogem.affec').browse(cr, uid, affec)

        if police_data.type_regime == 'O' or police_data.type_regime == False:

            college = benef_data.college_id

        else:
            pol_comp_id = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
                ('beneficiaire_id', '=', benef_data.id), ('police_id', '=', police_data.id)])
            college = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid,
                                                                                          pol_comp_id).college_id

        histo_s = self.pool.get('mcisogem.histo.police').search(cr, uid, [('name', '=', police_data.id),
                                                                          ('code_college', '=', college.id)])
        histo_data = self.pool.get('mcisogem.histo.police').browse(cr, uid, histo_s)

        acte_id = acte

        famille_acte = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, acte).code_fam_prest.id

        if int(police_data.type_prime) == 1:

            bareme_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police_data.id),
                                                                                 ('acte_id', '=', acte),
                                                                                 ('college_id', '=', college.id), (
                                                                                 'statut_id', '=',
                                                                                 benef_data.statut_benef.id)])

        else:

            bareme_s = self.pool.get('mcisogem.produit.police').search(
                [('police_id', '=', police_data.id), ('acte_id', '=', acte), ('college_id', '=', college.id)])

        bareme_data = self.pool.get('mcisogem.produit.police').browse(cr, uid, bareme_s)

        produit_search = self.pool.get('mcisogem.bareme').search(cr, uid,
                                                                 [('produit_id', '=', bareme_data.produit_id.id),
                                                                  ('acte_id', '=', acte)])

        produit_data = self.pool.get('mcisogem.bareme').browse(cr, uid, produit_search)

        plafond_affection = self.pool.get('mcisogem.plafond.affection').search(cr, uid, [
            ('code_aff_id', '=', affection_data.id)])

        pf_affec = 0
        for plf in self.pool.get('mcisogem.plafond.affection').browse(cr, uid, plafond_affection):
            if plf.tout_benef == True:
                pf_affec = plf.plafond

                break
            else:

                if plf.benef_id == benef_data.id:
                    pf_affec = plf.plafond

                    break

        pf_police = histo_data.mnt_plfd_pol
        pf_college = histo_data.mnt_plfd_col
        pf_famille = histo_data.mnt_plfd_fam
        pf_territoire = histo_data.mnt_plfd_territoire
        pf_ts_dep = histo_data.mnt_plfd_dep
        pf_periode = produit_data.plf_an_prest
        pf_jour = produit_data.plf_jour
        pf_trans = produit_data.plafond_transaction_temp
        pf_fam_acte = produit_data.plf_an_fam_act
        pf_benef = 0
        pf_ts_par = 0
        pf_ts_enf = 0

        mnt_benef = cout_acte
        mnt_fam_acte = cout_acte
        mnt_police = cout_acte
        mnt_ts_enf = 0
        mnt_ts_par = 0
        mnt_ts_dep = 0
        mnt_college = cout_acte
        mnt_famille = cout_acte
        mnt_periode = cout_acte
        mnt_jour = cout_acte
        mnt_trans = cout_acte
        mnt_territoire = 0
        mnt_affec = cout_acte

        periodicite_jr = bareme_data.unite_temps_id.nbre_jour

        pays_benef_id = police_data.garant_id.centre_gestion_id.pays_id.id
        pays_centre_id = centre_data.code_territoire.id

        if pays_benef_id != pays_centre_id:
            # le beneficiaire se trouve dans un autre pays

            les_prests_terr_id = self.pool.get('mcisogem.prestation').search(cr, uid, [('beneficiaire_id', '=', benef)])

            if les_prests_terr_id:

                for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_terr_id):
                    if prest.police_id.exercice_id == exercice:
                        # cumul de toutes les prestations pour l' exercice
                        mnt_territoire += prest.part_gest

                cr.execute(
                    'select part_gest from mcisogem_prestation where centre_id != %s and beneficiaire_id=%s and exercice_id=%s and state != "Draft"',
                    (centre_data.id, benef_data.id, exercice.id,))
                les_prestation_pharma = cr.dictfetchall()

                for p in les_prestation_pharma:
                    mnt_territoire += p['part_gest']

                les_prestation_pharma = None

        # prestations effetuées ce jour par le bénéficiaire
        les_prests_jr = self.pool.get('mcisogem.prestation').search(cr, uid, [('date_prest', '=', date_prestation),
                                                                              ('beneficiaire_id', '=', benef),
                                                                              ('acte_id', '=', acte),
                                                                              ('state', '!=', 'Draft')])

        if les_prests_jr:

            for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_jr):
                mnt_jour += prest.part_gest

            cr.execute(
                'select part_gest from mcisogem_prestation where centre_id != %s and beneficiaire_id=%s and exercice_id=%s and state != %s and date_prest=%s and acte_id=%s',
                (centre_data.id, benef_data.id, exercice.id, 'Draft', date_prestation, acte))

            les_prestation_pharma = cr.dictfetchall()

            for p in les_prestation_pharma:
                mnt_jour += p['part_gest']

            les_prestation_pharma = None

        # prestations effectuées par famille d'acte
        les_prests_fam_acte = self.pool.get('mcisogem.prestation').search(cr, uid, [('beneficiaire_id', '=', benef),
                                                                                    ('state', '!=', 'Draft')])

        if les_prests_fam_acte:
            for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_fam_acte):

                if (prest.police_id.exercice_id == exercice) and (prest.acte_id.code_fam_prest.id == famille_acte):
                    mnt_fam_acte += prest.part_gest

            cr.execute(
                'select part_gest from mcisogem_prestation where centre_id != %s and beneficiaire_id=%s and exercice_id=%s and state != %s and famille_acte_id=%s',
                (centre_data.id, benef_data.id, exercice.id, 'Draft', famille_acte))

            les_prestation_pharma = cr.dictfetchall()

            for p in les_prestation_pharma:
                mnt_fam_acte += p['part_gest']

            les_prestation_pharma = None

        # prestations effectuées sur la periode définie pour l'acte
        les_prests_period = self.pool.get('mcisogem.prestation').search(cr, uid, [('acte_id', '=', acte), (
        'date_prest', '>=', date_prestation - timedelta(days=periodicite_jr)), ('date_prest', '<=', date_prestation),
                                                                                  ('beneficiaire_id', '=', benef),
                                                                                  ('police_id', '=', police_data.id),
                                                                                  ('state', '!=', 'Draft')])

        if les_prests_period:
            for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_period):

                if prest.police_id.exercice_id == exercice:
                    mnt_periode += prest.part_gest

            cr.execute(
                'select part_gest from mcisogem_prestation where centre_id != %s and beneficiaire_id=%s and exercice_id=%s and state != %s and acte_id=%s and police_id = %s and date_prest >= %s and date_prest <= %s',
                (centre_data.id, benef_data.id, exercice.id, 'Draft', acte, police_data.id,
                 date_prestation - timedelta(days=periodicite_jr), date_prestation))

            les_prestation_pharma = cr.dictfetchall()

            for p in les_prestation_pharma:
                mnt_periode += p['part_gest']

            les_prestation_pharma = None

        les_prests_affec = self.pool.get('mcisogem.prestation').search(cr, uid,
                                                                       [('affection_id', '=', affection_data.id), (
                                                                       'date_prest', '>=', date_prestation - timedelta(
                                                                           days=periodicite_jr)),
                                                                        ('date_prest', '<=', date_prestation),
                                                                        ('beneficiaire_id', '=', benef),
                                                                        ('police_id', '=', police_data.id),
                                                                        ('state', '!=', 'Draft')])

        if les_prests_affec:
            for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_affec):

                if prest.police_id.exercice_id == exercice:
                    mnt_affec += prest.part_gest

            cr.execute(
                'select part_gest from mcisogem_prestation where centre_id != %s and beneficiaire_id=%s and exercice_id=%s and state != %s and affection_id=%s and police_id = %s and date_prest >= %s and date_prest <= %s',
                (centre_data.id, benef_data.id, exercice.id, 'Draft', affection_data.id, police_data.id,
                 date_prestation - timedelta(days=periodicite_jr), date_prestation))

            les_prestation_pharma = cr.dictfetchall()

            for p in les_prestation_pharma:
                mnt_affec += p['part_gest']

            les_prestation_pharma = None

        if benef_data.code_statut == 'A':

            # prestations effectuées par la famille de l'assuré principal
            benef_ids = self.pool.get('mcisogem.benef').search(cr, uid, [('benef_id', '=', benef_data.id),
                                                                         ('police_id', '=', police_data.id),
                                                                         ('state', '!=', 'Draft')])

            for benef in self.pool.get('mcisogem.benef').browse(cr, uid, benef_ids):

                les_prests_famille = self.pool.get('mcisogem.prestation').search(cr, uid,
                                                                                 [('beneficiaire_id', '=', benef.id),
                                                                                  ('police_id', '=', police_data.id),
                                                                                  ('exercice_id', '=', exercice.id),
                                                                                  ('state', '!=', 'Draft')])

                if les_prests_famille:

                    for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_famille):
                        mnt_famille += prest.part_gest

                    cr.execute(
                        'select part_gest from mcisogem_prestation where centre_id != %s and beneficiaire_id=%s and exercice_id=%s and state != %s and police_id = %s',
                        (centre_data.id, benef.id, exercice.id, 'Draft', police_data.id))

                    les_prestation_pharma = cr.dictfetchall()

                    for p in les_prestation_pharma:
                        mnt_famille += p['part_gest']

                    les_prestation_pharma = None

            # prestations effectuées par l assuré principal seul
            les_prests_A = self.pool.get('mcisogem.prestation').search(cr, uid,
                                                                       [('beneficiaire_id', '=', benef_data.id),
                                                                        ('exercice_id', '=', exercice.id),
                                                                        ('state', '!=', 'Draft')])

            for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_A):
                mnt_famille += prest.part_gest
                mnt_benef += prest.part_gest

            cr.execute(
                'select part_gest from mcisogem_prestation where centre_id != %s and beneficiaire_id=%s and exercice_id=%s and state != %s',
                (centre_data.id, benef_data.id, exercice.id, 'Draft'))

            les_prestation_pharma = cr.dictfetchall()

            for p in les_prestation_pharma:
                mnt_famille += p['part_gest']
                mnt_benef += p['part_gest']
            les_prestation_pharma = None



        else:

            benef_id = benef_data.benef_id.id
            benef_ids = self.pool.get('mcisogem.benef').search(cr, uid, [('benef_id', '=', benef_id)])
            mnt_ts_dep += cout_acte

            for benef in self.pool.get('mcisogem.benef').browse(cr, uid, benef_ids):

                les_prests_famille = self.pool.get('mcisogem.prestation').search(cr, uid,
                                                                                 [('beneficiaire_id', '=', benef.id),
                                                                                  ('exercice_id', '=', exercice.id),
                                                                                  ('police_id', '=', police_data.id),
                                                                                  ('state', '!=', 'Draft')])

                if les_prests_famille:

                    for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_famille):
                        mnt_famille += prest.part_gest
                        mnt_ts_dep += prest.part_gest

                cr.execute(
                    'select part_gest from mcisogem_prestation where centre_id = %s and beneficiaire_id=%s and exercice_id=%s and state != %s',
                    (centre_data.id, benef.id, exercice.id, 'Draft'))

                les_prestation_pharma = cr.dictfetchall()

                for p in les_prestation_pharma:
                    mnt_famille += p['part_gest']
                    mnt_ts_dep += p['part_gest']

                les_prestation_pharma = None

            les_prests_A = self.pool.get('mcisogem.prestation').search(cr, uid, [('beneficiaire_id', '=', benef_id),
                                                                                 ('police_id', '=', police_data.id),
                                                                                 ('exercice_id', '=', exercice.id),
                                                                                 ('state', '!=', 'Draft')])

            for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_A):
                mnt_famille += prest.part_gest

            cr.execute(
                'select part_gest from mcisogem_prestation where centre_id = %s and beneficiaire_id=%s and exercice_id=%s and state != %s and police_id = %s',
                (centre_data.id, benef_data.id, exercice.id, 'Draft', police_data.id))

            les_prestation_pharma = cr.dictfetchall()

            for p in les_prestation_pharma:
                mnt_famille += p['part_gest']

            les_prestation_pharma = None

        if benef_data.code_statut == 'A':
            pf_benef = histo_data.mnt_plfd_ass


        elif benef_data.code_statut in ['C', 'D']:

            if benef_data.code_statut == 'C':  # cas  conjoint
                pf_benef = histo_data.mnt_plfd_conj

            else:  # autre conjoint
                pf_benef = histo_data.mnt_plfd_aut_conj

            les_prests_C = self.pool.get('mcisogem.prestation').search(cr, uid, [('police_id', '=', police_data.id),
                                                                                 ('exercice_id', '=', exercice.id), (
                                                                                 'beneficiaire_id', '=', benef_data.id),
                                                                                 ('state', '!=', 'Draft')])

            for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_C):

                if benef_data.code_statut in ['C', 'D']:
                    mnt_benef += prest.part_gest

            cr.execute(
                'select part_gest from mcisogem_prestation where centre_id=%s and beneficiaire_id=%s and exercice_id=%s and state!=%s and police_id=%s',
                (centre_data.id, benef_data.id, exercice.id, 'Draft', police_data.id))

            les_prestation_pharma = cr.dictfetchall()

            for p in les_prestation_pharma:
                mnt_benef += p['part_gest']

            les_prestation_pharma = None




        elif benef_data.code_statut in ['E', 'K']:

            if benef_data.code_statut == 'E':  # cas d un enfant
                pf_benef = histo_data.mnt_plfd_enf
            else:
                pf_benef = histo_data.mnt_plfd_enf_sup

            pf_ts_enf = histo_data.mnt_plfd_tenf

            mnt_ts_enf += cout_acte

            benef_ids = self.pool.get('mcisogem.benef').search(cr, uid, [('benef_id', '=', benef_data.benef_id.id),
                                                                         ('code_statut', 'in', ['E', 'K'])])

            # Cumul de toutes les prestations des enfants et du benef actuel si c est un enfant
            for benef in self.pool.get('mcisogem.benef').browse(cr, uid, benef_ids):
                les_prests_E = self.pool.get('mcisogem.prestation').search(cr, uid, [('beneficiaire_id', '=', benef.id),
                                                                                     ('police_id', '=', police_data.id),
                                                                                     ('exercice_id', '=', exercice.id),
                                                                                     ('state', '!=', 'Draft')])

                for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_E):

                    if benef_data.id == benef.id:
                        mnt_benef += prest.part_gest

                    mnt_ts_enf += prest.part_gest

                cr.execute(
                    'select part_gest from mcisogem_prestation where centre_id = %s and beneficiaire_id=%s and exercice_id=%s and state != %s and police_id = %s',
                    (centre_data.id, benef_data.id, exercice.id, 'Draft', police_data.id))

                les_prestation_pharma = cr.dictfetchall()

                for p in les_prestation_pharma:
                    mnt_ts_enf += p['part_gest']

                les_prestation_pharma = None




        elif benef_data.code_statut in ['G', 'X']:

            if benef_data.code_statut == 'G':  # cas d un parent
                pf_benef = histo_data.mnt_plfd_gen
            else:
                pf_benef = histo_data.mnt_plfd_parent_autre

            pf_ts_par = histo_data.mnt_plfd_parent
            mnt_ts_par += cout_acte

            benef_id = benef_data.benef_id.id
            benef_ids = self.pool.get('mcisogem.benef').search(cr, uid, [('benef_id', '=', benef_id),
                                                                         ('code_statut', 'in', ['G', 'X'])])

            # Cumul de toutes les prestations des parents
            for benef in self.pool.get('mcisogem.benef').browse(cr, uid, benef_ids):
                les_prests_P = self.pool.get('mcisogem.prestation').search(cr, uid, [('beneficiaire_id', '=', benef.id),
                                                                                     ('exercice_id', '=', exercice.id),
                                                                                     ('state', '!=', 'Draft')])

                for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, les_prests_P):

                    if benef_data.id == benef.id:
                        mnt_benef += prest.part_gest

                    mnt_ts_par += prest.part_gest

                    cr.execute(
                        'select part_gest from mcisogem_prestation where centre_id = %s and beneficiaire_id=%s and exercice_id=%s and state != %s and police_id = %s',
                        (centre_data.id, benef_data.id, exercice.id, 'Draft', police_data.id))

                    les_prestation_pharma = cr.dictfetchall()

                    for p in les_prestation_pharma:
                        mnt_ts_par += p['part_gest']

                    les_prestation_pharma = None

        toutes_les_prests = self.pool.get('mcisogem.prestation').search(cr, uid, [('police_id', '=', police_data.id),
                                                                                  ('exercice_id', '=', exercice.id),
                                                                                  ('state', '!=', 'Draft')])

        # cumul des prestations pour la police et le collège
        for prest in self.pool.get('mcisogem.prestation').browse(cr, uid, toutes_les_prests):

            mnt_police += prest.part_gest

            if college.id == prest.college_id.id:
                mnt_college += prest.part_gest

        les_plafonds = {}
        les_plafonds['police'] = pf_police
        les_plafonds['college'] = pf_college
        les_plafonds['famille'] = pf_famille
        les_plafonds['territoire'] = pf_territoire
        les_plafonds['dependants'] = pf_ts_dep
        les_plafonds['periode'] = pf_periode
        les_plafonds['jour'] = pf_jour
        les_plafonds['transaction'] = pf_trans
        les_plafonds['famille_acte'] = pf_fam_acte
        les_plafonds['assure'] = pf_benef
        les_plafonds['parents'] = pf_ts_par
        les_plafonds['enfants'] = pf_ts_enf
        les_plafonds['benef'] = pf_benef
        les_plafonds['affection'] = pf_affec

        les_montants = {}
        les_montants['assure'] = mnt_benef
        les_montants['benef'] = mnt_benef
        les_montants['police'] = mnt_police
        les_montants['famille_acte'] = mnt_fam_acte
        les_montants['enfants'] = mnt_ts_enf
        les_montants['parents'] = mnt_ts_par
        les_montants['dependants'] = mnt_ts_dep
        les_montants['college'] = mnt_college
        les_montants['periode'] = mnt_periode
        les_montants['famille'] = mnt_famille
        les_montants['transaction'] = mnt_trans
        les_montants['territoire'] = mnt_territoire
        les_montants['jour'] = mnt_jour
        les_montants['affection'] = mnt_affec

        atteint_plafond = {}

        if mnt_police > pf_police and pf_police > 0:
            atteint_plafond['police'] = True
        else:
            atteint_plafond['police'] = False

        if mnt_college > pf_college and pf_college > 0:
            atteint_plafond['college'] = True
        else:
            atteint_plafond['college'] = False

        if mnt_ts_par > pf_ts_par and pf_ts_par > 0:
            atteint_plafond['parent'] = True
        else:
            atteint_plafond['parent'] = False

        if mnt_ts_enf > pf_ts_enf and pf_ts_enf > 0:
            atteint_plafond['enfant'] = True
        else:
            atteint_plafond['enfant'] = False

        if mnt_ts_dep > pf_ts_dep and pf_ts_dep > 0:
            atteint_plafond['dependant'] = True
        else:
            atteint_plafond['dependant'] = False

        if mnt_famille > pf_famille and pf_famille > 0:
            atteint_plafond['famille'] = True
        else:
            atteint_plafond['famille'] = False

        if mnt_periode > pf_periode and pf_periode > 0:
            atteint_plafond['periode'] = True
        else:
            atteint_plafond['periode'] = False

        if mnt_jour > pf_jour and pf_jour > 0:
            atteint_plafond['jour'] = True
        else:
            atteint_plafond['jour'] = False

        if mnt_trans > pf_trans and pf_trans > 0:
            atteint_plafond['transaction'] = True
        else:
            atteint_plafond['transaction'] = False

        if mnt_fam_acte > pf_fam_acte and pf_fam_acte > 0:
            atteint_plafond['famille_acte'] = True
        else:
            atteint_plafond['famille_acte'] = False

        if mnt_benef > pf_benef and pf_benef > 0:
            atteint_plafond['benef'] = True
        else:
            atteint_plafond['benef'] = False

        if mnt_affec > pf_affec and pf_affec > 0:
            atteint_plafond['affection'] = True
        else:
            atteint_plafond['affection'] = False

        return {
            'value': {'les_plafonds': les_plafonds, 'les_montants': les_montants, 'atteint_plafond': atteint_plafond}}

    def check_num_bon(self, cr, uid, centre, num, context=None):

        bon_valide = False

        nbre_prest = self.pool.get('mcisogem.prestation').search_count(cr, uid, [('num_bon', '=', num),
                                                                                 ('state', '!=', 'Draft')])

        if nbre_prest > 0:
            # ce numéro de bon a déjà été utilisé
            bon_valide = False

        else:

            lecentre = self.pool.get('mcisogem.centre').browse(cr, uid, centre)

            for plage in lecentre.plage_bon_ids:
                debut = plage.debut
                fin = plage.fin

                for i in range(debut, fin):
                    if int(num) == i:
                        # Ce numéro de bon a bel et bien été attribué à ce centre
                        bon_valide = True

        return bon_valide

    def get_le_plafond(self, cr, uid, benef, pol, centre, acte, context=None):

        benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef)

        police = self.pool.get('mcisogem.police').browse(cr, uid, pol)

        plafond = 0

        if police.type_regime == 'O' or police.type_regime == False:

            college = benef_data.college_id

        else:
            pol_comp_id = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
                ('beneficiaire_id', '=', benef_data.id), ('police_id', '=', police.id)])
            college = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid,
                                                                                          pol_comp_id).college_id

        if int(police.type_prime) == 1:

            bareme_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police.id),
                                                                                 ('acte_id', '=', acte),
                                                                                 ('college_id', '=', college.id), (
                                                                                 'statut_id', '=',
                                                                                 benef_data.statut_benef.id)])

        else:

            bareme_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police.id),
                                                                                 ('acte_id', '=', acte),
                                                                                 ('college_id', '=', college.id)])

        bareme_data = self.pool.get('mcisogem.produit.police').browse(cr, uid, bareme_s)

        produit_search = self.pool.get('mcisogem.bareme').search(cr, uid,
                                                                 [('produit_id', '=', bareme_data.produit_id.id),
                                                                  ('acte_id', '=', acte)])

        produit_data = self.pool.get('mcisogem.bareme').browse(cr, uid, produit_search)

        plafond = produit_data.plafond_transaction_temp

        return plafond

    def _get_ticket_moderateur(self, cr, uid, benef, pol, centre, acte, context=None):

        # le ticket est définie soit dans le produit ou dans ticket modérateur police

        benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef)
        police = self.pool.get('mcisogem.police').browse(cr, uid, pol)

        taux_ticket = 0

        ticket_s = self.pool.get('mcisogem.tick.mod.pol').search(cr, uid, [('police_id', '=', police.id),
                                                                           ('nomen_prest_id', '=', acte),
                                                                           ('centre_id', '=', centre)])

        if police.type_regime == 'O' or police.type_regime == False:

            college = benef_data.college_id

        else:
            pol_comp_id = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
                ('beneficiaire_id', '=', benef_data.id), ('police_id', '=', police.id)])
            college = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid,
                                                                                          pol_comp_id).college_id

        if ticket_s:

            ticket_data = self.pool.get('mcisogem.tick.mod.pol').browse(cr, uid, ticket_s)
            taux_ticket = ticket_data.mnt_tick_mod


        else:

            if int(police.type_prime) == 1:

                bareme_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police.id),
                                                                                     ('acte_id', '=', acte),
                                                                                     ('college_id', '=', college.id), (
                                                                                     'statut_id', '=',
                                                                                     benef_data.statut_benef.id)])

            else:

                bareme_s = self.pool.get('mcisogem.produit.police').search(cr, uid, [('police_id', '=', police.id),
                                                                                     ('acte_id', '=', acte),
                                                                                     ('college_id', '=', college.id)])

            bareme_data = self.pool.get('mcisogem.produit.police').browse(cr, uid, bareme_s)

            produit_search = self.pool.get('mcisogem.bareme').search(cr, uid,
                                                                     [('produit_id', '=', bareme_data.produit_id.id),
                                                                      ('acte_id', '=', acte)])

            produit_data = self.pool.get('mcisogem.bareme').browse(cr, uid, produit_search)

            taux_ticket = produit_data.ticm_assure

        return taux_ticket

    def _get_college_benef(self, cr, uid, mat, police, context):
        # cette fonction recupere le collège d 'un beneficiaire sur une police complementaire
        benef_id = self._get_benef_id(cr, uid, mat, context)
        benef = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id)

        for police in benef.police_complementaire_ids:
            return police.college_id.id

    def _get_montant_acte(self, cr, uid, centre, acte, benef, prescripteur,
                          context=None):

        tarif_nego_id = self.pool.get('mcisogem.tarif.nego.benef').search(cr, uid, [('benef_id', '=', benef),
                                                                                    ('nomen_prest_id', '=', acte),
                                                                                    ('centre_id', '=', centre),
                                                                                    ('state', '=', 'N')])

        if tarif_nego_id:
            montant = self.pool.get('mcisogem.tarif.nego.benef').browse(cr, uid, tarif_nego_id[0]).tarif

            return montant

        tarif_m_id = self.pool.get('mcisogem.tarif.convention.medecin').search(cr, uid, [('code_centre', '=', centre), (
        'code_medecin_id', '=', prescripteur), ('code_acte', '=', acte)])

        if tarif_m_id:
            tarif_data = self.pool.get('mcisogem.tarif.convention.medecin').browse(cr, uid, tarif_m_id)

            montant = tarif_data.montant_brut_tarif

            return montant

        tarif = self.pool.get('mcisogem.tarif.centre').search(cr, uid, [('acte_id', '=', acte),('centre_id', '=', centre)])


        if tarif:
            tarif_data = self.pool.get('mcisogem.tarif.centre').browse(cr, uid, tarif)

            montant = tarif_data.tarif
        else:

            montant = False



        # si la prestation est de type consultation , on verifie si une autre d'une même genre n'a pas eu lieu dans les 15 jours précéents inclus.
        # si tel est le cas , alors le cout est nul
        prest_cons = self.pool.get('mcisogem.prestation').search_count(cr, uid, [('beneficiaire_id', '=', benef),
                                                                                 ('centre_id', '=', centre), (
                                                                                 'date_prest', '>=', datetime.strptime(
                                                                                     str(time.strftime("%Y-%m-%d",
                                                                                                       time.localtime())),
                                                                                     '%Y-%m-%d') - timedelta(days=15)),
                                                                                 ('consultation', '=', True),
                                                                                 ('acte_id', '=', acte),
                                                                                 ('state', '!=', 'Draft')])
        if prest_cons:
            return 0

        return montant

    def _get_base_remb(self, cr, uid, centre, acte, police, college, context=None):
        plafond = 0
        # centre = self._get_centre_user(cr, uid, context)
        # cr.execute("select * from mcisogem_tarif_nego_police where police_id=%s and college_id =%s and centre_id =%s", (police, college,centre))
        # lescollegespolices = cr.dictfetchall()

        # table_conv = self.pool.get('mcisogem.tarif.nego.police').search(cr,uid,[('police_id' , '=' , police),('college_id' , '=' ,college),('centre_id' , '=' , centre)])
        # conv_data = self.pool.get('mcisogem.tarif.nego.police').browse(cr,uid,table_conv)

        # tarif_s = self.pool.get('mcisogem.tarif.convention').search(cr,uid,[('code_acte' , '=' , acte),('code_convention' , '=' , conv_data.id)])
        # tarif_data = self.pool.get('mcisogem.tarif.convention').browse(cr,uid,tarif_s)
        # plafond = tarif_data.montant_plafond_tarif

        return plafond

    def calcul_part_benef(self, cr, uid, cout_acte, taux_ticket, context=None):
        # si RO alors cout_acte = base de remboursement
        part_patient = 0

        if cout_acte != 0 and taux_ticket != 0:
            part_patient = (taux_ticket * cout_acte) / 100

        return part_patient

    def onchange_presta_prat(self, cr, uid, ids, valeur, context):
        cr.execute('DELETE  FROM mcisogem_praticien_presta_tempo WHERE create_uid=%s', (uid,))
        if valeur:
            centre_user_id = valeur

            ratach = self.pool.get('mcisogem.agr.prestat').search(cr, uid, [('code_centre', '=', centre_user_id)])

            for prat in self.pool.get('mcisogem.agr.prestat').browse(cr, uid, ratach).praticien_ids:
                # if prat.code_specialite.bl_prescr_autoris == True:

                data = {}
                data['praticien_id'] = prat.id
                data['nom_prat'] = prat.nom_prestat
                data['prenom_prat'] = prat.prenoms_prestat
                data['nom_prenoms_prestat'] = prat.nom_prenoms_prestat
                self.pool.get('mcisogem.praticien.presta.tempo').create(cr, uid, data, context)


    def onchange_consultation(self, cr, uid, ids, fam_acte, context):
        # cas des centres medicaux

        if fam_acte:
            v = {}
            d = {}

            v['aff_quantite'] = True
            v['aff_hos_mat'] = False

            v['consultation'] = True
            v['pharmacie'] = False
            v['acteenclinique'] = False
            v['radio'] = False
            v['optique'] = False
            v['dentaire'] = False


            # Retirer les pharmacies et les cabinet dentaire de la liste des centres prescripteurs
            type_centre = self.pool.get('mcisogem.type.centre').search(cr, uid, [('name', 'not in', ['PHARMACIE' , 'CABINET DENTAIRE'  , 'OPTIQUE MEDICALE' , 'LABORATOIRE' , 'IMAGERIE MEDICALE'])])
            les_centres = self.pool.get('mcisogem.centre').search(cr, uid, [('code_type_centre', 'in', type_centre)])


            famille_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('libelle_court_famille', 'not in', ['RAD' , 'DEN' , 'OPT' , 'PH' , 'BIO'])])

            if context.get('code_regime'):
                d = {'acte_id': [('code_fam_prest', 'in', famille_ids)] , 'centre_id' : [('id' , 'in' , les_centres)]}
            else:
                d = {'acte_id': [('code_fam_prest', 'in', famille_ids), ('bl_nomen_envig', '=', False)] , 'centre_id' : [('id' , 'in' , les_centres)]}



            return {'value': v, 'domain': d}

    def onchange_dentaire(self, cr, uid, ids, fam_acte, context):

        if fam_acte:
            v = {}
            d = {}

            v['aff_quantite'] = True
            v['aff_hos_mat'] = False

            v['consultation'] = False
            v['phamarcie'] = False
            v['acteenclinique'] = False
            v['radio'] = False
            v['optique'] = False
            v['dentaire'] = True


            rech_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('libelle_court_famille', '=', 'DEN')])
            famille_id = self.pool.get('mcisogem.fam.prest').browse(cr, uid, rech_ids).id

            type_centre = self.pool.get('mcisogem.type.centre').search(cr, uid, [('name', '=', 'CABINET DENTAIRE')])
            type_centre_id = self.pool.get('mcisogem.type.centre').browse(cr, uid, type_centre).id

            les_cab = self.pool.get('mcisogem.centre').search(cr, uid, [('code_type_centre', '=', type_centre_id)])


            if context.get('code_regime'):
                d = {'acte_id': [('code_fam_prest', '=', famille_id)] , 'centre_id' : [('id' , 'in' , les_cab)]}
            else:
                d = {'acte_id': [('code_fam_prest', '=', famille_id), ('bl_nomen_envig', '=', False)]  , 'centre_id' : [('id' , 'in' , les_cab)]}

            return {'value': v, 'domain': d}

    def onchange_optique(self, cr, uid, ids, fam_acte, context):

        if fam_acte:
            v = {}
            d = {}

            v['aff_quantite'] = True
            v['aff_hos_mat'] = False

            v['consultation'] = False
            v['phamarcie'] = False
            v['acteenclinique'] = False
            v['radio'] = False
            v['optique'] = True
            v['dentaire'] = False

            rech_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('libelle_court_famille', '=', 'OPT')])
            famille_id = self.pool.get('mcisogem.fam.prest').browse(cr, uid, rech_ids).id


            type_centre = self.pool.get('mcisogem.type.centre').search(cr, uid, [('name', '=', 'OPTIQUE MEDICALE')])
            type_centre_id = self.pool.get('mcisogem.type.centre').browse(cr, uid, type_centre).id

            les_opt = self.pool.get('mcisogem.centre').search(cr, uid, [('code_type_centre', '=', type_centre_id)])

            if context.get('code_regime'):
                d = {'acte_id': [('code_fam_prest', '=', famille_id)], 'centre_id': [('id', 'in', les_opt)]}
            else:
                d = {'acte_id': [('code_fam_prest', '=', famille_id), ('bl_nomen_envig', '=', False)],
                     'centre_id': [('id', 'in', les_opt)]}

            return {'value': v, 'domain': d}

    def onchange_radio(self, cr, uid, ids, fam_acte, context):

        if fam_acte:
            v = {}
            d = {}

            v['aff_quantite'] = True
            v['aff_hos_mat'] = False

            v['consultation'] = False
            v['phamarcie'] = False
            v['acteenclinique'] = False
            v['radio'] = True
            v['optique'] = False
            v['dentaire'] = False

            rech_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('libelle_court_famille', '=', 'RAD')])
            famille_id = self.pool.get('mcisogem.fam.prest').browse(cr, uid, rech_ids).id


            type_centre = self.pool.get('mcisogem.type.centre').search(cr, uid, [('name', '=', 'RADIOLOGIE')])
            type_centre_id = self.pool.get('mcisogem.type.centre').browse(cr, uid, type_centre).id

            les_opt = self.pool.get('mcisogem.centre').search(cr, uid, [('code_type_centre', '=', type_centre_id)])

            if context.get('code_regime'):
                d = {'acte_id': [('code_fam_prest', '=', famille_id)], 'centre_id': [('id', 'in', les_opt)]}
            else:
                d = {'acte_id': [('code_fam_prest', '=', famille_id), ('bl_nomen_envig', '=', False)],
                     'centre_id': [('id', 'in', les_opt)]}

            return {'value': v, 'domain': d}

    def onchange_phamarcie(self, cr, uid, ids, fam_acte, context):

        if fam_acte:
            v = {}
            d = {}

            v['aff_quantite'] = True
            v['aff_hos_mat'] = False

            v['consultation'] = False
            v['phamarcie'] = True
            v['acteenclinique'] = False
            v['radio'] = False
            v['optique'] = False
            v['dentaire'] = False


            rech_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [('libelle_court_famille', '=', 'PH')])

            type_centre = self.pool.get('mcisogem.type.centre').search(cr,uid,[('name' , '=' , 'PHARMACIE')])
            type_centre_id  = self.pool.get('mcisogem.type.centre').browse(cr,uid,type_centre).id
            les_pharmas = self.pool.get('mcisogem.centre').search(cr,uid,[('code_type_centre' , '=' , type_centre_id)])

            type_a_exclure = self.pool.get('mcisogem.type.centre').search(cr,uid,[('name' , 'in' , ['PHARMACIE' , 'LABORATOIRE' , 'RADIOLOGIE'])])


            famille_id = self.pool.get('mcisogem.fam.prest').browse(cr, uid, rech_ids).id

            if context.get('code_regime'):

                d = {'acte_id': [('code_fam_prest', '=', famille_id)]  , 'centre_id' : [('id' , 'in' , les_pharmas)]}


            else:
                d = {'acte_id': [('code_fam_prest', '=', famille_id), ('bl_nomen_envig', '=', False)] , 'centre_id' : [('id' , 'not in' , les_pharmas)]}

            return {'value': v, 'domain': d}

    def onchange_acteenclinique(self, cr, uid, ids, fam_acte, context):

        # Cas des analyses
        if fam_acte:
            d = {}
            v = {}

            v['aff_quantite'] = True
            v['aff_hos_mat'] = False

            v['consultation'] = False
            v['phamarcie'] = False
            v['acteenclinique'] = True
            v['radio'] = False
            v['optique'] = False
            v['dentaire'] = False


            type_centre = self.pool.get('mcisogem.type.centre').search(cr, uid, [
                ('name', 'in', ['LABORATOIRE'])])

            les_centres = self.pool.get('mcisogem.centre').search(cr, uid, [('code_type_centre', 'in', type_centre)])

            fam = []
            rech_ids = self.pool.get('mcisogem.fam.prest').search(cr, uid, [
                ('libelle_court_famille', 'in', ['RAD'])])

            for f in self.pool.get('mcisogem.fam.prest').browse(cr, uid, rech_ids):
                fam.append(f.id)

            if context.get('code_regime'):

                d = {'acte_id': [('code_fam_prest', 'in', fam)] ,'centre_id' : [('id' , 'in' , les_centres)]}

            else:
                d = {'acte_id': [('code_fam_prest', 'in', fam), ('bl_nomen_envig', '=', False)] , 'centre_id' : [('id' , 'in' , les_centres)]}

            return {'value': v, 'domain': d}

    def check_num_bon_pharmacie(self, cr, uid, centre, num, benef, context=None):

        cr.execute('select * from mcisogem_prestation where phamarcie =%s and num_bon =%s and state != %s',
                   (True, num, 'Draft'))
        existe = len(cr.dictfetchall())

        if existe > 0:
            return False

        # je verifie si le numero de bon  correspond a une prestation non Pharmacie et non dentaire de ce benef pour une periode <= 7 jours
        cr.execute(
            'select * from mcisogem_prestation where phamarcie =%s and num_bon =%s and beneficiaire_id = %s and dentaire = %s and date_prest >= %s',
            (False, num, benef, False,
             datetime.strptime(str(time.strftime("%Y-%m-%d", time.localtime())), '%Y-%m-%d') - timedelta(days=7)))

        nbre_prest = len(cr.dictfetchall())

        # cr.execute('select * from mcisogem_prestation where phamarcie =%s and num_bon =%s and beneficiaire_id = %s' , (False , num,benef))
        # nbre_prest_pharm = len(cr.dictfetchall())

        if (nbre_prest > 0):

            return True
        else:

            # sinon je verifie si le numero de bon  correspond a une prestation non Pharmacie et dentaire de ce benef pour une periode <= 15 jours
            cr.execute(
                'select * from mcisogem_prestation where phamarcie =%s and num_bon =%s and beneficiaire_id = %s and dentaire = %s and date_prest >=%s',
                (False, num, benef, False,
                 datetime.strptime(str(time.strftime("%Y-%m-%d", time.localtime())), '%Y-%m-%d') - timedelta(days=15)))
            nbre_prest = len(cr.dictfetchall())

            if (nbre_prest > 0):
                return True
            else:
                return False

    def benef_change(self, cr, uid, ids, benef_mat, context=None):

        erreur = ""
        date_prest = datetime.strptime(str(time.strftime("%Y-%m-%d")), '%Y-%m-%d')

        print('#############################benef')
        print(benef_mat)

        if benef_mat:

            if self.check_existence_benef(cr, uid, benef_mat) == True:

                print('************** le benef existe ')

                benef_id = self._get_benef_id(cr, uid, benef_mat, context)

                centre_id = self._get_centre_user(cr, uid, context)

                v = self._get_details_benef(cr, uid, benef_mat, context)

                if self.check_state_benef(cr, uid, benef_mat, date_prest, context):

                    print('************** le benef est actif ')

                    polices = self._get_police_benef(cr, uid, benef_mat, context)

                    for police in polices:

                        if self.check_state_police(cr, uid, police.id, context):
                            # la police est active

                            # on recupere le collège du benef sur chaque police

                            college = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id).college_id

                            if police.type_regime == 'O' or police.type_regime == False:

                                college = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id).college_id

                            elif police.type_regime == 'C':
                                college = self._get_college_benef(cr, uid, benef_mat, police, context)

                            if college and police and benef_id:

                                print('********** college OK et police OK')

                                if self.check_age_benef(cr, uid, benef_id, police.id, college.id, date_prest):
                                    # le benef respecte bel et bien les limites d ages

                                    if self.check_reseau_benef(cr, uid, centre_id, police.id, college.id,
                                                               context) == True:
                                        # le beneficiaire est dans son reseau de soins

                                        print('********** reseau OK')

                                        v['affichdetail'] = True
                                        v['affichebenef'] = True
                                        type_centre = self.pool.get('mcisogem.centre').browse(cr, uid,
                                                                                              centre_id).code_type_centre.name

                                        v['type_centre'] = type_centre

                                        if type_centre == 'PHARMACIE':
                                            v['pharmacie'] = True

                                        elif type_centre == 'CABINET DENTAIRE':
                                            v['dentaire'] = True

                                        elif type_centre == 'LABORATOIRE':
                                            v['acteenclinique'] = True

                                        elif type_centre == 'IMAGERIE MEDICALE':
                                            v['radio'] = True

                                        elif type_centre in ['OPTIQUE MEDICALE' , 'OPHTAMOLOGIE']:
                                            v['optique'] = True
                                        else:
                                            v['consultation'] = True




                                        print('######################################### TYPE CENTRE####')
                                        print(v['type_centre'])


                                    else:
                                        polices.remove(police)
                                        erreur += "Le bénéficiaire n'est pas dans son réseau de soins pour la police " + str(
                                            police.name) + ".\n"

                                        raise osv.except_osv('Attention !',
                                                             "Le bénéficiaire n' est pas dans son réseau de soins.")


                                else:
                                    polices.remove(police)
                                    erreur += "Le bénéficiaire n' a pas l'âge requis pour effectuer la prestation sur la police " + str(
                                        police.name) + ".\n"

                                    raise osv.except_osv('Attention !',
                                                         "Le bénéficiaire n' a pas l'âge requis pour effectuer la prestation")


                            else:
                                polices.remove(police)
                        else:
                            polices.remove(police)

                            erreur += "La police" + str(police.name) + " du bénéficiaire n\'est pas active. \n"
                            raise osv.except_osv('Attention !',
                                                 'La police du bénéficiaire bénéficiaire n\'est pas active !')

                    v['les_polices'] = polices

                    return {'value': v}

                else:
                    raise osv.except_osv('Attention !', 'Ce bénéficiaire n\'est pas actif !')

            else:

                raise osv.except_osv('Attention !', 'Ce bénéficiaire n\'existe pas !')

    def benef_change2(self, cr, uid, ids, benef_mat, context=None):

        erreur = ""
        date_prest = datetime.strptime(str(time.strftime("%Y-%m-%d")), '%Y-%m-%d')
        if benef_mat:

            if self.check_existence_benef(cr, uid, benef_mat) == True:

                benef_id = self._get_benef_id(cr, uid, benef_mat, context)

                centre_id = self._get_centre_user(cr, uid, context)

                v = self._get_details_benef(cr, uid, benef_mat, context)
                v['type_centre'] = 'GESTIONNAIRE'

                if self.check_state_benef(cr, uid, benef_mat, date_prest, context):

                    polices = self._get_police_benef(cr, uid, benef_mat, context)

                    for police in polices:

                        if self.check_state_police(cr, uid, police.id, context):
                            # la police est active

                            # on recupere le collège du benef sur chaque police

                            college = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id).college_id

                            if police.type_regime == 'O' or police.type_regime == False:

                                college = self.pool.get('mcisogem.benef').browse(cr, uid, benef_id).college_id

                            elif police.type_regime == 'C':
                                college = self._get_college_benef(cr, uid, benef_mat, police, context)

                            if college and police and benef_id:

                                if self.check_age_benef(cr, uid, benef_id, police.id, college.id, date_prest):
                                    # le benef respecte bel et bien les limites d ages

                                    if self.check_reseau_benef(cr, uid, centre_id, police.id, college.id,
                                                               context) == True:
                                        # le beneficiaire est dans son reseau de soins
                                        v['affichdetail'] = True
                                        v['affichebenef'] = True
                                        v['type_centre'] = 'GESTIONNAIRE'


                                    else:
                                        # polices.remove(police)
                                        erreur += "Le bénéficiaire n'est pas dans son réseau de soins pour la police " + str(
                                            police.name) + ".\n"


                                else:
                                    # polices.remove(police)
                                    erreur += "Le bénéficiaire n' a pas l'âge requis pour effectuer la prestation sur la police " + str(
                                        police.name) + ".\n"


                            else:
                                polices.remove(police)
                        else:
                            polices.remove(police)

                            erreur += "La police" + str(police.name) + " du bénéficiaire n\'est pas active. \n"

                    v['les_polices'] = polices

                else:
                    erreur += "Ce bénéficiaire n\'est pas actif.\n"

            else:
                raise osv.except_osv('Attention !', "Ce bénéficiaire n\'existe pas.")
                erreur += "Ce bénéficiaire n\'existe pas.\n"
                v['erreur'] = erreur

            v['affichdetail'] = True
            v['affichebenef'] = True

            print('*********** ---------   ************')
            print(v)

            return {'value': v}

    def imprimer_bon(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'mcisogem_isa.report_bon_consultation',
            'data': data,
        }




    def gerer_plafond(self, cr, uid, benef, police, college, acte, cout_acte, centre, exercice, affec,
                      date_prestation=time.strftime("%Y-%m-%d", time.localtime()), context=None):

        atteint_plafond = \
        self.get_plafond(cr, uid, benef, police, college, acte, cout_acte, centre, exercice, affec, date_prestation,
                         context)['value']['atteint_plafond']

        les_plafonds = \
        self.get_plafond(cr, uid, benef, police, college, acte, cout_acte, centre, exercice, affec, date_prestation,
                         context)['value']['les_plafonds']

        les_montants = \
        self.get_plafond(cr, uid, benef, police, college, acte, cout_acte, centre, exercice, affec, date_prestation,
                         context)['value']['les_montants']

        return {'les_montants': les_montants, 'les_plafonds': les_plafonds, 'atteint_plafond': atteint_plafond}

    def write(self, cr, uid, ids, data, context=None):

        old_datas = self.browse(cr, uid, ids)

        if 'montant_exclu' in data:
            part_patient_1 = old_datas.part_patient - old_datas.montant_exclu

            data['part_gest'] = old_datas.montant_total - part_patient_1 - data['montant_exclu']

            data['part_patient'] = part_patient_1 + data['montant_exclu']

        return super(mcisogem_prestation, self).write(cr, uid, ids, data, context=context)

    def create(self, cr, uid, vals, context=None):

        # initialisation
        erreur = ""
        cout_acte_mci = 0

        data = {}
        data = vals

        centre = self._get_centre_user(cr, uid, context)  # on recupere le centre
        a_mci = True

        cout_total_acte = 0
        cout_acte = 0
        cout_total__acte = 0

        benef = self._get_details_benef(cr, uid, vals['matric_benef'], context)['beneficiaire_id']

        benef_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef)


        detail_cg = self.get_centre_gestion(cr, uid, context)

        # si le champ centre est defini alors nous sommes dans un centre
        if centre:
            a_mci = False

        if detail_cg.cod_sup and data['a_sous_acte'] :

            if len(vals['sous_actes_ids']) == 0:

                raise osv.except_osv('Attention !' , 'Vous devez choisir au moins un sous acte.')

            else:
                if a_mci:
                    # vrai_cout_acte = self._get_montant_acte(cr, uid, data['centre_id'], vals['acte_id'], benef_data.id,
                    #                                 vals['praticien_id'],
                    #                               context)

                    vrai_cout_acte = vals['montant_total']



                else:
                    vrai_cout_acte = self._get_montant_acte(cr, uid, centre, vals['acte_id'], benef_data.id,
                                                            vals['praticien_id'],
                                                            context)

                    if vrai_cout_acte == False and vals['phamarcie'] == False:
                        raise osv.except_osv(_('Attention'), _("Aucun tarif n'a été trouvé pour cet acte."))

                montant_2 = 0

                for ss in vals['sous_actes_ids']:

                    sous_acte = self.pool.get('mcisogem.sous.actes').browse(cr, uid, ss[2]['sous_acte_id'])


                    montant_2 += (sous_acte.qte_cg * ss[2]['qte'] * vrai_cout_acte)

                vrai_cout_acte = montant_2
        else:
            if a_mci:

                # vrai_cout_acte = self._get_montant_acte(cr, uid, centre, data['centre_id'], benef_data.id,
                #                                         vals['praticien_id'],
                #
                #                                         context)
                vrai_cout_acte = vals['montant_total']
            else:
                vrai_cout_acte = self._get_montant_acte(cr, uid, centre, vals['acte_id'], benef_data.id,
                                                        vals['praticien_id'],

                                                        context)

            if vrai_cout_acte == False and vals['phamarcie'] == False:
                raise osv.except_osv(_('Attention'), _("Aucun tarif n'a été trouvé pour cet acte."))

        if 'date_comptable' in vals:
            vals['date_comptable'] = datetime.strptime(str(vals['date_comptable']), '%Y-%m-%d')

            code_periode = vals['date_comptable'].strftime('%m/%Y')

            if vals['date_comptable'] <= datetime.strptime(str(vals['date_prest']), '%Y-%m-%d'):
                raise osv.except_osv(_('Attention !'),
                                     _('La date comptable doit être postérieure à la date de prestation.'))

        else:
            code_periode = time.strftime("%m/%Y", time.localtime())





        if 'ordo_ids' not in vals:
            vals['ordo_ids'] = None

            # on verifie si la quantite de medicaments prescri n'est pas supérieure à 3

            if len(vals['ordo_ids']) > 0:
                qte = 0
                for o in vals['ordo_ids']:

                    if o[2].has_key('quantite'):
                        qte += o[2]['quantite']

                    else:
                        cr.execute('select quantite from mcisogem_prestation_ordornance where id = %s', (o[1],))
                        dt = cr.dictfetchone()
                        qte += dt['quantite']

                # si c'est le cas , un message d'erreur est généré
                if len(vals['ordo_ids']) > 3:
                    raise osv.except_osv('Attention', 'Vous ne pouvez prescrire plus de 3 médicaments à la fois!')

        if a_mci:
            code_regime = context.get('code_regime')


            if 'num_bon' not in vals:
                vals['num_bon'] = '1'

            data['centre_id'] = vals['centre_id']
            vals['type_centre'] = 'GESTIONNAIRE'
            date_prestation = vals['date_prest']
            les_polices = self.benef_change2(cr, uid, 1, vals['matric_benef'], context)['value']['les_polices']

            centre = vals['centre_id']


            # le centre gère les sous actes
            if vals['phamarcie'] == True:

                prescripteur = uid

                vals['affection_id'] = self._get_detail_bon(cr, uid, 1, vals['num_bon'], context)['value'][
                    'affection_id']

                self.check_droit_prestation2(cr, uid, vals['acte_id'], centre, benef, prescripteur,
                                             vals['affection_id'], date_prestation, context)
            else:
                self.check_droit_prestation2(cr, uid, vals['acte_id'], centre, benef, vals['praticien_id'],
                                             vals['affection_id'], date_prestation, context)

                vrai_cout_acte *= data['quantite']
                cout_acte_mci = vrai_cout_acte
                data['montant_total'] = vrai_cout_acte

        else:

            code_regime = 'TP'

            data['centre_user_id'] = uid
            data['centre_id'] = centre
            data['centre_exec_id'] = centre

            if vals['type_centre'] == 'PHARMACIE':
                vals['phamarcie'] = True
            else:
                vals['phamarcie'] = False

            date_prestation = time.strftime("%Y-%m-%d", time.localtime())
            les_polices = self.benef_change(cr, uid, 1, vals['matric_benef'], context)['value']['les_polices']

            if vals['type_centre'] == 'PHARMACIE':
                prescripteur = uid

            else:
                prescripteur = self.pool.get('mcisogem.praticien.presta.tempo').browse(cr, uid, vals[
                    'praticien_acte_temp_id']).praticien_id
                vals['praticien_id'] = prescripteur
                self.check_droit_prestation(cr, uid, vals['acte_id'], centre, benef, vals['praticien_id'],
                                            vals['affection_id'], date_prestation, context)

        cout_acte = 0
        montant_acte_a_considerer = 0



        if not a_mci:
            # Dans les entres , le cout de l'acte est connu d'avance
            vals['montant_total'] = vrai_cout_acte


        if vals['phamarcie'] == True:

            if self._get_detail_bon(cr, uid, 1, vals['num_bon'], context):
                les_polices = []

                police_id = self._get_detail_bon(cr, uid, 1, vals['num_bon'], context)['value']['police']
                police = self.pool.get('mcisogem.police').browse(cr, uid, police_id)
                les_polices.append(police)

                acte_phar_id = self._get_detail_bon(cr, uid, 1, vals['num_bon'], context)['value']['acte_phar_id']
                affec_phar_id = self._get_detail_bon(cr, uid, 1, vals['num_bon'], context)['value']['affec_phar_id']
                affec_id = self._get_detail_bon(cr, uid, 1, vals['num_bon'], context)['value']['affection_id']

                data['acte_phar_id'] = acte_phar_id
                data['affec_phar_id'] = affec_phar_id
                data['centre_exec_id'] = self._get_detail_bon(cr, uid, 1, vals['num_bon'], context)['value'][
                    'centre_id']
                data['acte_id'] = acte_phar_id
                data['affection_id'] = affec_id

        else:

            cout_total_acte = data['montant_total']
            cout_acte = data['montant_total']
            cout_total__acte = data['montant_total']





        famille_acte = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, vals['acte_id']).code_fam_prest.id

        periode_id = self.pool.get('mcisogem.account.period').search(cr, uid, [('code', '=', code_periode) ,  ('state' , '!=' , 'Draft')])
        periode_data = self.pool.get('mcisogem.account.period').browse(cr, uid, periode_id)


        print(cout_total_acte)
        print(cout_acte)
        print(cout_total__acte)

        part_patient = 0
        montant_exclu = 0
        montant_exclu_2 = 0


        if 'affection_id' not in vals:
            vals['affection_id'] = None

        data['beneficiaire_id'] = benef
        data['acte_id'] = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, vals['acte_id']).id
        data['nom_benef'] = benef_data.nom
        data['prenom_benef'] = benef_data.prenom_benef
        data['nom_prenom'] = benef_data.nom + " " + benef_data.prenom_benef
        data['date_naiss'] = benef_data.dt_naiss_benef
        data['sexe'] = benef_data.sexe
        data['groupe_sg'] = benef_data.group_sang_benef
        data['famille_acte_id'] = famille_acte
        data['date_prest'] = date_prestation
        data['periode_id'] = periode_data.id
        data['state'] = 'Draft'
        data['praticien_id'] = vals['praticien_id']
        data['image'] = benef_data.image
        data['image_medium'] = benef_data.image_medium
        data['image_small'] = benef_data.image_small



        if a_mci:

            prest_id = False
            prat_id = vals['praticien_id']
            centre = vals['centre_id']
            data['state'] = 'SS'
            data['base_remb'] = cout_acte_mci  - vals['montant_exclu']

            vals['montant_total'] = data['base_remb']
            vals['base_remb'] = data['base_remb']
            montant_exclu = vals['montant_exclu']

            cout_total_acte = vals['montant_total']
            cout_acte = vals['montant_total']
            cout_total__acte = vals['montant_total']



        else:
            prat_id = vals['praticien_id']

        print('-------------------')
        print(les_polices)



        for police in les_polices:


            if a_mci:

                if context.get('code_regime') not in police.code_regime.code_regime:
                    raise osv.except_osv(_('Attention !'), _("Le type de remboursement de cette police n'est pas pris en charge par le type de prestation choisi"))


            if police.code_regime.code_regime in ('RDE', 'RD') and a_mci == False:
                raise osv.except_osv('Attention!', 'Le mode de remboursement de cette police n\'est pas pris en compte')

            if vals['phamarcie'] == True:
                is_acte_ok = True

            else:
                # on verifie si le beneficiaire a droit à l acte
                is_acte_ok = self.check_acte(cr, uid, vals['acte_id'], police.id, centre, vals['matric_benef'],
                                             date_prestation, context)

            if is_acte_ok or a_mci:
                # on verifie le delai

                is_delai_ok = self.check_delai(cr, uid, vals['acte_id'], centre, vals['matric_benef'], police.id,
                                               vals['praticien_id'], date_prestation, vals['affection_id'],
                                               context)

                if is_delai_ok or a_mci:

                    if police.type_regime == 'O' or police.type_regime == False:

                        college = benef_data.college_id
                        taux_ticket = self._get_ticket_moderateur(cr, uid, benef, police.id, centre, vals['acte_id'],
                                                                  context)


                    else:

                        pol_comp_id = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr, uid, [
                            ('beneficiaire_id', '=', benef_data.id), ('police_id', '=', police.id)])
                        college = self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr, uid,
                                                                                                      pol_comp_id).college_id

                        taux_ticket = self._get_ticket_moderateur(cr, uid, benef, police.id, centre, vals['acte_id'],
                                                                  context)

                    data['college_id'] = college.id

                    plafond = 0

                    srch_excl_ids = None

                    # montant a considerer pour le calcul concernant la police en cours d utilisation
                    if vals['type_centre'] == 'PHARMACIE' or vals['phamarcie'] == True:

                        qte = 0
                        cout_acte = 0
                        cout_total__acte = 0
                        acte = None

                        for o in vals['ordo_ids']:

                            if o[2].has_key('quantite'):
                                qte = o[2]['quantite']

                            else:
                                cr.execute('select * from mcisogem_prestation_ordornance where id = %s', (o[1],))
                                dt = cr.dictfetchone()
                                qte = dt['quantite']
                                # acte = dt['medicament_ids']
                                acte = self.pool.get('mcisogem.medicament').browse(cr, uid,
                                                                                   o[2]['medicament_ids']).acte_id.id

                            srch_excl_ids = self.pool.get('mcisogem.exclusion.acte').search(cr, uid, [
                                ('police_id', '=', police.id), ('cod_col_id', '=', data['college_id']),
                                ('code_med_id', '=', acte), ('code_statut_id', '=', benef_data.statut_benef.id)])

                            if srch_excl_ids:

                                montant_exclu += qte * o[2]['pu']

                                if a_mci:

                                    erreur += "Un ou plusieurs médicaments sont exclu pour le statut du bénéficiaire. \n"
                                else:
                                    raise osv.except_osv('Attention',
                                                         "Un ou plusieurs médicaments sont exclu pour le statut du bénéficiaire.")


                            else:

                                srch_excl_ids = self.pool.get('mcisogem.exclusion.acte').search(cr, uid, [
                                    ('police_id', '=', police.id), ('cod_col_id', '=', data['college_id']),
                                    ('code_med_id', '=', acte), ('cod_benef_id', '=', benef_data.id)])

                                if srch_excl_ids:

                                    if a_mci:
                                        erreur += "Un ou plusieurs médicaments sont exclu pour ce bénéficiaire. \n"
                                    else:
                                        raise osv.except_osv('Attention',
                                                             "Un ou plusieurs médicaments sont exclu pour ce bénéficiaire.")

                                cout_acte += qte * o[2]['pu']

                            acte = None

                            print('******  PU  ***********')
                            print(o[2])

                            if o[2].has_key('medicament_ids'):
                                acte = self.pool.get('mcisogem.medicament').browse(cr, uid,
                                                                                   o[2]['medicament_ids']).acte_id.id

                            if o[2].has_key('quantite'):
                                # acte = o[2]['acte_id']

                                qte = o[2]['quantite']

                            else:
                                cr.execute('select quantite from mcisogem_prestation_ordornance where id = %s', (o[1],))

                                dt = cr.dictfetchone()

                                qte = o[2]['quantite']

                            plafond = self.get_le_plafond(cr, uid, benef, police.id, centre, acte, context)

                            taux_ticket = self._get_ticket_moderateur(cr, uid, benef, police.id, centre, acte, context)

                        montant_acte_a_considerer = cout_acte

                        if (cout_acte > plafond) and (plafond > 0):
                            montant_exclu_2 += cout_acte - plafond
                            montant_acte_a_considerer = plafond

                        # montant_acte_a_considerer += plafond


                    else:
                        srch_excl_ids = self.pool.get('mcisogem.exclusion.acte').search(cr, uid,
                                                                                        [('police_id', '=', police.id),
                                                                                         (
                                                                                         'cod_col_id', '=', college.id),
                                                                                         ('fam_acte_id', '=',
                                                                                          famille_acte), (
                                                                                         'code_statut_id', '=',
                                                                                         benef_data.statut_benef.id)])

                        # on check si l'acte ou la famille ou l'affection est exclue
                        if not srch_excl_ids:

                            srch_excl_ids = self.pool.get('mcisogem.exclusion.acte').search(cr, uid, [
                                ('police_id', '=', police.id), ('cod_col_id', '=', college.id),
                                ('fam_acte_id', '=', famille_acte), ('cod_benef_id', '=', benef_data.id)])

                            if not srch_excl_ids:

                                srch_excl_ids = self.pool.get('mcisogem.exclusion.acte').search(cr, uid, [
                                    ('police_id', '=', police.id), ('cod_col_id', '=', college.id),
                                    ('code_acte_id', '=', vals['acte_id']),
                                    ('code_statut_id', '=', benef_data.statut_benef.id)])

                                if not srch_excl_ids:

                                    srch_excl_ids = self.pool.get('mcisogem.exclusion.acte').search(cr, uid, [
                                        ('police_id', '=', police.id), ('cod_col_id', '=', college.id),
                                        ('code_acte_id', '=', vals['acte_id']), ('cod_benef_id', '=', benef_data.id)])

                                    if not srch_excl_ids:

                                        srch_excl_ids = self.pool.get('mcisogem.exclusion.acte').search(cr, uid, [
                                            ('police_id', '=', police.id), ('cod_col_id', '=', college.id),
                                            ('code_aff_id', '=', vals['affection_id']),
                                            ('cod_benef_id', '=', benef_data.id)])

                                        if not srch_excl_ids:
                                            srch_excl_ids = self.pool.get('mcisogem.exclusion.acte').search(cr, uid, [
                                                ('police_id', '=', police.id), ('cod_col_id', '=', college.id),
                                                ('code_aff_id', '=', vals['affection_id']),
                                                ('code_statut_id', '=', benef_data.statut_benef.id)])

                        if srch_excl_ids:

                            montant_exclu = cout_acte
                            erreur += "L'acte est exclu pour ce bénéficiaire. \n"



                        else:

                            # on verifie le plafond prevu pour l'acte
                            # si le montant inscrit est supérieur au plafond , le surplus est pris en charge par le patient
                            rata_reseau = self.pool.get('mcisogem.rata.reseau.police').search(cr, uid, [
                                ('police_id', '=', police.id), ('college_id', '=', college.id)], limit=1)

                            reseau_id = self.pool.get('mcisogem.rata.reseau.police').browse(cr, uid,
                                                                                            rata_reseau).reseau_id.id

                            convention_s = self.pool.get('mcisogem.tarif.nego.police').search(cr, uid, [
                                ('reseau_id', '=', reseau_id), ('centre_id', '=', centre)] , limit=1)

                            convention_id = self.pool.get('mcisogem.tarif.nego.police').browse(cr, uid,
                                                                                               convention_s).convention_id.id

                            tarif_search = self.pool.get('mcisogem.tarif.convention').search(cr, uid, [
                                ('code_convention', '=', convention_id), ('code_acte', '=', vals['acte_id'])])

                            tarif_data = self.pool.get('mcisogem.tarif.convention').browse(cr, uid, tarif_search)

                            plafond = tarif_data.montant_brut_tarif

                            montant_acte_a_considerer = cout_acte



                            if vals['montant_total'] > plafond and plafond > 0:
                                erreur += "Le montant brut est supérieur au tarif fixé pour cet acte. \n"

                                montant_exclu_2 = vals['montant_total'] - plafond
                                montant_acte_a_considerer = plafond

                    print('*********     ********')
                    print(montant_exclu_2)
                    print(montant_exclu)
                    print(montant_acte_a_considerer)



                    if not a_mci:
                        cout_total__acte = cout_acte
                        vals['montant_total'] = cout_acte

                    # part du patient selon son Ticket Modérateur  , part à laquelle il peut éventuellement s'ajouter le montant exclu

                    if not srch_excl_ids:

                        part_patient += self.calcul_part_benef(cr, uid, montant_acte_a_considerer, taux_ticket, context)

                        part_garant = montant_acte_a_considerer - part_patient

                        montant_acte_a_considerer = montant_acte_a_considerer - (
                                                                                taux_ticket * montant_acte_a_considerer) / 100

                    else:
                        part_patient = 0
                        part_garant = 0

                    atteint_plafond = \
                    self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'], montant_acte_a_considerer,
                                       centre, police.exercice_id, vals['affection_id'], date_prestation, context)[
                        'atteint_plafond']

                    les_plafonds = \
                    self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'], montant_acte_a_considerer,
                                       centre, police.exercice_id, vals['affection_id'], date_prestation, context)[
                        'les_plafonds']

                    les_montants = \
                    self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'], montant_acte_a_considerer,
                                       centre, police.exercice_id, vals['affection_id'], date_prestation, context)[
                        'les_montants']

                    if atteint_plafond['affection']:
                        montant_exclu += les_montants['affection'] - les_plafonds['affection']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        erreur += "Le bénéficiaire a atteint son plafond (" + str(
                            les_plafonds['affection']) + ") pour l'affection'. \n"

                    # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                    # 	erreur += "Le bénéficiaire a atteint son plafond (" + str(les_plafonds['affection']) + ") pour l'affection'. \n"

                    if atteint_plafond['famille_acte']:
                        montant_exclu += les_montants['famille_acte'] - les_plafonds['famille_acte']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        erreur += "Le bénéficiaire a atteint son plafond (" + str(
                            les_plafonds['famille_acte']) + ") pour la famille d'acte. \n"

                    # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                    # 	erreur += "Le bénéficiaire a atteint son plafond (" + str(les_plafonds['famille_acte']) + ") pour la famille d'acte. \n"

                    if atteint_plafond['transaction']:
                        montant_exclu += les_montants['transaction'] - les_plafonds['transaction']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        erreur += "Le bénéficiaire a atteint son plafond (" + str(
                            les_plafonds['transaction']) + ") pour la transaction. \n"

                    # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                    # 	erreur += "Le bénéficiaire a atteint son plafond (" + str(les_plafonds['transaction']) + ") pour la transaction. \n"

                    if atteint_plafond['jour']:
                        montant_exclu += les_montants['jour'] - les_plafonds['jour']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        erreur += "Le bénéficiaire a atteint son plafond (" + str(
                            les_plafonds['jour']) + ") pour la journée. \n"

                    # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                    # 	erreur += "Le bénéficiaire a atteint son plafond (" + str(les_plafonds['jour']) + ") pour la journée. \n"

                    if atteint_plafond['periode']:
                        montant_exclu += les_montants['periode'] - les_plafonds['periode']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        erreur += "Le bénéficiaire a atteint son plafond (" + str(
                            les_plafonds['periode']) + ") sur la période. \n"

                    # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                    # 	erreur += "Le bénéficiaire a atteint son plafond (" + str(les_plafonds['periode']) + ") sur la période. \n"

                    if atteint_plafond['benef']:
                        montant_exclu += les_montants['benef'] - les_plafonds['benef']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        erreur += "Le bénéficiaire a déjà atteint son plafond (" + str(
                            les_plafonds['benef']) + ") pour son statut. \n"

                    # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                    # 	erreur += "Le bénéficiaire a déjà atteint son plafond (" + str(les_plafonds['benef']) + ") pour son statut. \n"

                    if atteint_plafond['police']:

                        montant_exclu += les_montants['police'] - les_plafonds['police']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:
                            erreur += "Le bénéficiaire a déjà atteint son plafond (" + str(
                                les_plafonds['police']) + ") sur la police. \n"

                    if atteint_plafond['college']:
                        # erreur += "Plafond du collège sur la police " + str(police.name) + "atteint \n"

                        montant_exclu += les_montants['college'] - les_plafonds['college']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                        erreur += "Le bénéficiaire a déjà atteint son plafond (" + str(
                            les_plafonds['college']) + ") sur le collège. \n"

                    if atteint_plafond['parent']:
                        montant_exclu += les_montants['parents'] - les_plafonds['parents']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                        erreur += "Le plafond (" + str(
                            les_plafonds['parents']) + ") pour les parents est déjà atteint. \n"

                    if atteint_plafond['enfant']:
                        montant_exclu += les_montants['enfants'] - les_plafonds['enfants']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                        erreur += "Le plafond (" + str(
                            les_plafonds['enfants']) + ") pour les enfants est déjà atteint. \n"

                    if atteint_plafond['dependant']:
                        montant_exclu += les_montants['dependants'] - les_plafonds['dependants']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                        erreur += "Le plafond (" + str(
                            les_plafonds['dependants']) + ") pour les dependants est déjà atteint. \n"

                    if atteint_plafond['famille']:
                        montant_exclu += les_montants['famille'] - les_plafonds['famille']
                        montant_acte_a_considerer -= montant_exclu

                        atteint_plafond = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                             montant_acte_a_considerer, centre, police.exercice_id,
                                                             vals['affection_id'], date_prestation, context)[
                            'atteint_plafond']

                        les_plafonds = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_plafonds']

                        les_montants = self.gerer_plafond(cr, uid, benef, police.id, college, vals['acte_id'],
                                                          montant_acte_a_considerer, centre, police.exercice_id,
                                                          vals['affection_id'], date_prestation, context)[
                            'les_montants']

                        # if cout_total_acte == (montant_exclu + part_patient) and a_mci == False:

                        erreur += "Le plafond (" + str(
                            les_plafonds['famille']) + ") pour la famille est déjà atteint. \n"

                    if atteint_plafond['police'] or atteint_plafond['college'] or atteint_plafond['parent'] or \
                            atteint_plafond['enfant'] or atteint_plafond['dependant'] or atteint_plafond['famille'] or \
                            atteint_plafond['periode'] or atteint_plafond['jour'] or atteint_plafond['transaction'] or \
                            atteint_plafond['famille_acte'] or atteint_plafond['benef']:
                        plafond_pharma = True

                    data['exercice_id'] = police.exercice_id.id

                    print('****** --- plafond atteint---- ******')
                    print(atteint_plafond)

                    print('****** --- plafonds---- ******')
                    print(les_plafonds)

                    print('****** --- les montants---- ******')
                    print(les_montants)

                    if not a_mci:
                        data['montant_total'] = cout_total__acte


                    if vals['phamarcie'] == True and a_mci == False:
                        is_check_bon = self.check_num_bon_pharmacie(cr, uid, centre, vals['num_bon'], benef, context)

                        if is_check_bon == False:
                            raise osv.except_osv('Attention',
                                                 "Le N° Bon ne correspond à aucune autre prestation valide.")

                    else:

                        is_check_bon = self.check_num_bon(cr, uid, centre, vals['num_bon'], context)

                    if police.type_regime == 'O':
                        part_garant = police.base_remb

                    if not srch_excl_ids:

                        if part_garant != 0:
                            part_garant -= montant_exclu

                    if is_check_bon is not True and a_mci is False:
                        raise osv.except_osv('Attention !', "Le N° de Bon n'est pas valide.")

                    else:
                        data['police_id'] = police.id
                        data['garant_id'] = police.garant_id.id
                        data['acte_id'] = vals['acte_id']
                        data['souscripteur'] = police.souscripteur_id.id
                        data['taux_part_patient'] = taux_ticket
                        data['taux_part_gest'] = 100 - taux_ticket

                        code_regime = self.pool.get('mcisogem.regime').search(cr, uid,
                                                                              [('code_regime', '=', code_regime)])
                        code_regime_data = self.pool.get('mcisogem.regime').browse(cr, uid, code_regime)
                        data['mode_paiement'] = code_regime_data.id
                        data['code_regime'] = code_regime_data.code_regime

                        data['dent_ids'] = vals['dent_ids']
                        data['montant_exclu'] = montant_exclu + montant_exclu_2
                        data['part_patient'] = part_patient + montant_exclu + montant_exclu_2
                        data['part_gest'] = part_garant
                        data['erreur'] = erreur

                        if a_mci:
                            data['montant_total'] = cout_acte_mci
                            data['base_remb'] = cout_acte_mci - data['montant_exclu']


                        if police.code_regime.code_regime in ('TPG', 'RD/TPG') and a_mci == False:
                            data['part_patient'] = 0
                            data['taux_part_patient'] = 0
                            data['taux_part_gest'] = 100

                            data['part_gest'] = cout_total__acte

                        cout_total_acte = data['part_patient']

                        if vals['dentaire'] == True:

                            erreur_dent = ""

                            dents = vals['dent_ids']

                            for dt in dents[0][2]:

                                if self.check_dentaire(cr, uid, benef_data.id, police.id, police.exercice_id, dt,
                                                       context=None):
                                    dt = self.pool.get('mcisogem.liste.dent').browse(cr, uid, dt).name
                                    erreur_dent = "La dent N° " + str(dt) + " a déjà fait l'objet d'une extraction."

                                    raise osv.except_osv('Attention !', erreur_dent)

                            if erreur_dent == "":
                                prest_id = super(mcisogem_prestation, self).create(cr, uid, data, context)
                            # les_ids.append(prest_id)

                        else:

                            prest_id = super(mcisogem_prestation, self).create(cr, uid, data, context)

                        for o in vals['ordo_ids']:
                            l_id = o[1]
                            self.pool.get('mcisogem.prestation.ordornance').write(cr, uid, l_id,
                                                                                  {'prestation_ids': prest_id})

                else:
                    raise osv.except_osv('Attention !',
                                         'Le delai de carence n\'est pas encore atteint pour la police ' + str(
                                             police.name))

            else:
                raise osv.except_osv('Attention !', 'Le bénéficiaire n\' a pas droit à l\'acte.')

        return prest_id
