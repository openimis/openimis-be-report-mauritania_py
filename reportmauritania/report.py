from distutils.command import upload
# from reportmauritania.models import  beneficiary_card_query
# from reportmauritania.report_templates import rptBeneficiaryCard
from reportmauritania.models import  beneficiaries_list_card_query, beneficiaries_membership_card_query
from reportmauritania.report_templates import rptBeneficiaries_list_Card, rptBeneficiaries_membership_card


report_definitions = [ 
    {
        "name": "beneficiary_card_mauritania",
        "engine": 0,
        "default_report":rptBeneficiaries_list_Card.template,
        "description": "Insuree Card",
        "module": "reportmauritania",
        "python_query": beneficiaries_list_card_query, 
        "permission": ["131215"],
    },
    {
        "name": "beneficiary_membership_card",
        "engine": 0,
        "default_report":rptBeneficiaries_membership_card.template,
        "description": "Membership Card",
        "module": "reportmauritania",
        "python_query": beneficiaries_membership_card_query, 
        "permission": ["131215"],
    }
    
]