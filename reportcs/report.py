from distutils.command import upload
from reportcs.models import  assisted_birth_with_cs_query, cesarienne_rate_query, closed_cs_query, complicated_birth_with_cs_query, cpn1_with_cs_query, cs_in_use_query, invoice_per_fosa_query, severe_malaria_cost_query, mother_cpon_with_cs_query, newborn_cpon_with_cs_query, pregnant_woman_ref_rate_query, cpn4_with_cs_query, periodic_paid_bills_query,periodic_rejected_bills_query, invoice_cs_query
from reportcs.report_templates import rptAssistedBirth
from reportcs.report_templates import rptCponUnderCs
from reportcs.report_templates import rptNewbornCPoN
from reportcs.report_templates import rptReferalRate
from reportcs.report_templates import rptCpn4UnderCheck
from reportcs.report_templates import rptCpn1UnderCheck
from reportcs.report_templates import rptInvoicePerFosa
from reportcs.report_templates import rptPaidInvoice
from reportcs.report_templates import rptComplicatedDel
from reportcs.report_templates import rptCesarianRate
from reportcs.report_templates import rptRejectedBills
from reportcs.report_templates import rptcsInUse
from reportcs.report_templates import rptClosedCs
from reportcs.report_templates import rptSevereMalariaCost
from reportcs.report_templates import rptInvoiceperPeriod


report_definitions = [ 
    {
        "name": "invoice_fosa_cs",
        "engine": 0,
        "default_report":rptInvoiceperPeriod.template,
        "description": "Etat de paiement",
        "module": "reportcs",
        "python_query": invoice_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "cpn1_under_cs",
        "engine": 0,
        "default_report":rptCpn1UnderCheck.template,
        "description": " Nombres de CPN1 réalisés sous chèque santé",
        "module": "reportcs",
        "python_query": cpn1_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "cpn4_under_cs",
        "engine": 0,
        "default_report":rptCpn4UnderCheck.template,
        "description": "Nombre de femmes enceintes avec CS venues en CPN4",
        "module": "reportcs",
        "python_query": cpn4_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "assisted_birth_under_cs",
        "engine": 0,
        "default_report": rptAssistedBirth.template ,
        "description": "Nombre d’accouchements assistés réalisés sous chèque santé",
        "module": "reportcs",
        "python_query": assisted_birth_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "CPON_under_check_report",
        "engine": 0,
        "default_report": rptCponUnderCs.template  ,
        "description": "Nombre de CPoN Mère réalisées sous chèque santé",
        "module": "reportcs",
        "python_query": mother_cpon_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "newborn_CPoN_report",
        "engine": 0,
        "default_report": rptNewbornCPoN.template ,
        "description": "Nombre de CPoN nouveau-nés réalisées sous Chèque santé",
        "module": "reportcs",
        "python_query": newborn_cpon_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "complicated_birth_with_cs",
        "engine": 0,
        "default_report": rptComplicatedDel.template ,
        "description": "Taux d'accouchements compliqués CS au cours d’une période déterminée",
        "module": "reportcs",
        "python_query": complicated_birth_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "cesarian_cs_rate",
        "engine": 0,
        "default_report": rptCesarianRate.template,
        "description": "Taux de césariennes CS au cours d’une période déterminée",
        "module": "reportcs",
        "python_query": cesarienne_rate_query, 
        "permission": ["131215"],
    },
    {
        "name": "pregnant_woman_reference_rate",
        "engine": 0,
        "default_report": rptReferalRate.template ,
        "description": "Taux de référencement des femmes enceintes",
        "module": "reportcs",
        "python_query": pregnant_woman_ref_rate_query, 
        "permission": ["131215"],
    },
    {
        "name": "invoice_per_period_report",
        "engine": 0,
        "default_report": rptInvoicePerFosa.template ,
        "description": "Total des factures sur une période par FOSA",
        "module": "reportcs",
        "python_query": invoice_per_fosa_query, 
        "permission": ["131215"],
    },
    {
        "name": "paid_invoice_per_period_report",
        "engine": 0,
        "default_report": rptPaidInvoice.template ,
        "description": "Total des factures payés sur une période par FOSA ",
        "module": "reportcs",
        "python_query": periodic_paid_bills_query, 
        "permission": ["131215"],
    },
    {
        "name": "rejected_invoice_per_period_report",
        "engine": 0,
        "default_report": rptRejectedBills.template  ,
        "description": "Total des factures rejetés sur une période par FOSA",
        "module": "reportcs",
        "python_query": periodic_rejected_bills_query, 
        "permission": ["131215"],
    },
    {
        "name": "check_in_use_report",
        "engine": 0,
        "default_report": rptcsInUse.template  ,
        "description": "Nombre de CS en cours d’utilisation (activé, et non clôturé)",
        "module": "reportcs",
        "python_query": cs_in_use_query,
        "permission": ["131215"],
    },
    {
        "name": "closed_check_report",
        "engine": 0,
        "default_report": rptClosedCs.template  ,
        "description": "Nombre de CS clôturés",
        "module": "reportcs",
        "python_query": closed_cs_query,
        "permission": ["131215"],
    },
    {
        "name": "severe_malaria_cost_report",
        "engine": 0,
        "default_report": rptSevereMalariaCost.template,
        "description": "Coût moyen du paludisme grave pris en charge par les bénéficiaires du chèque",
        "module": "reportcs",
        "python_query": severe_malaria_cost_query,
        "permission": ["131215"],
    },
    
]