{
    'name': "MCI-SOGEM",
    'category': '1.0.0',
    'sequence': 3,
    'author': 'SmileCI',
    'website': 'http://www.smile.ci',
    'summary': 'Gestion de la Sante',
    'description': """
TRANSFORMATION ISA
==============================

This application enables you to manage important aspects of your company's

You can manage:
---------------
* Production
* Medical
* Prestation
* Comptabilite
    """,
    'depends' : [
        'base',
        'web',
        'mail'
    ],
    'data' : [
        'security/mcisogem_security.xml',
        'security/ir.model.access.csv',
        # 'mcisogem_isa_data.xml',
        'mcisogem_isa_data_2.xml',
		
        
        'views/mcisogem_isa_production_view.xml',
        'views/mcisogem_isa_tableref_view.xml',
        'views/mcisogem_isa_admin_view.xml',
        'views/mcisogem_isa_exercice_police_view.xml',
        'views/mcisogem_tarif_negocie_view.xml',
        'views/mcisogem_isa_medical_view.xml',
        'views/mcisogem_isa_police_view.xml',
        'views/mcisogem_resil_suspension_pol_view.xml',
        'views/mcisogem_surprime_view.xml',
        'views/mcisogem_budget_encaissement_view.xml',
        'views/mcisogem_budget_reajustement_view.xml',
      
        'views/mcisogem_isa_exercice_police_view.xml',
        'views/mcisogem_histo_copie_tarif_view.xml',
        'views/mcisogem_ticket_moderateur_view.xml',
        'views/mcisogem_benef_view.xml',
        'views/mcisogem_excl_acte_benef_view.xml',
        'views/mcisogem_tarif_nego_benef_view.xml',
        'views/mcisogem_tick_mod_benef_view.xml',
        'views/mcisogem_histo_clot_police_view.xml',
        'views/mcisogem_histo_renouv_police_view.xml',
       
        'views/medical/mcisogem_typechambre_view.xml',
        'views/medical/mcisogem_intervalle2actes_view.xml',
        'views/medical/mcisogem_agr_prestat_view.xml',
        'views/medical/mcisogem_rata_convention.xml',
        'views/medical/mcisogem_agent_centre_view.xml',
        'views/medical/mcisogem_actes_lies_autres_view.xml',
        'views/medical/mcisogem_tarif_convention_centre_view.xml',
        'views/medical/mcisogem_tarif_convention_medecin_view.xml',
        'views/medical/mcisogem_chapitre_affection_view.xml',
        #
        'views/mcisogem_plafond_affection.xml',
        #
        'report/report_quittance_all.xml',
       
        'views/mcisogem_delai_carence_view.xml',
        'views/prestation/mcisogem_prestation.xml',
       
		'views/mcisogem_demande.xml',
        'views/prestation/mcisogem_alerte.xml',
        'views/mcisogem_exclusion_acte.xml',
        'views/mcisogem_exclusion_acte_view.xml',
		'views/mcisogem_menu_demande.xml',
        'views/mcisogem_menu_production.xml',
        'views/prestation/mcisogem_menu_prestation.xml',
         'views/mcisogem_quittancier_view.xml',
        'views/comptabilite/mcisogem_compta_view.xml',
        'report/report_brouillard.xml',
        'report/bon_prestation.xml',
        'report/report_menu.xml',
        'report/report_benef_report_view.xml',
        'report/mcisogem_compta_report.xml',
        'report/report_ententep_view.xml',
        'report/report_pcharge_view.xml',
        'report/report_benef_inc_garant.xml',
        'report/report_benef_garant.xml',
        'report/report_benef_inter_view.xml',
        'report/report_incorporation_view.xml',
        'report/report_retrait_view.xml',
       
        'report/report_benef_n_garant_view.xml',
        'report/report_incorporation_garant_view.xml',
        'report/report_retrait_garant.xml',
      
        'report/report_ententep_centre.xml',
        'report/report_pcharge_centre.xml',
        'report/report_bon_pcharge.xml',
        'report/report_bon_prorogation.xml',
        'report/report_bon_consultation.xml',
        'report/report_prestation_view.xml',
        'report/report_prestation_garant.xml',
        'report/report_prestation_r_centre.xml',
       
        'report/report_sinistre_c.xml',
        'report/report_sinistre_v.xml',
        'report/report_benef.xml',
        'report/report_benef_inc.xml',
        'report/report_benef_ret.xml',
        'report/report_benef_sus.xml',
        'report/report_benef_age.xml',
        'report/report_benef_stat.xml',

        'report/report_sinistre_c_new.xml',
        'report/report_prestation_view_age.xml',
        # 'views/saas.xml',
        
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
