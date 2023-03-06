from distutils.command import upload
from reportmauritania.models import  beneficiary_card_query
from reportmauritania.report_templates import rptBeneficiaryCard


report_definitions = [ 
    {
        "name": "beneficiary_card_mauritania",
        "engine": 0,
        "default_report":rptBeneficiaryCard.template,
        "description": "Etat de paiement",
        "module": "reportmauritania",
        "python_query": beneficiary_card_query, 
        "permission": ["131215"],
    }
    
]