from distutils.command import upload
from reportcs.models import  beneficiary_card_query
from reportcs.report_templates import rptBeneficiaryCard


report_definitions = [ 
    {
        "name": "beneficiary_card_mauritania",
        "engine": 0,
        "default_report":rptBeneficiaryCard.template,
        "description": "Etat de paiement",
        "module": "reportcs",
        "python_query": beneficiary_card_query, 
        "permission": ["131215"],
    }
    
]