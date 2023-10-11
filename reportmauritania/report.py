from distutils.command import upload
# from reportmauritania.models import  beneficiary_card_query
# from reportmauritania.report_templates import rptBeneficiaryCard
from reportmauritania.models import  beneficiaries_list_card_query, invoice_report_query
from reportmauritania.report_templates import rptBeneficiaries_list_Card, invoice_report_template


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
        "name": "invoice_mauritania",
        "engine": 0,
        "default_report":invoice_report_template.template,
        "description": "Mauritania Invoice report",
        "module": "reportmauritania",
        "python_query": invoice_report_query, 
        "permission": ["131215"],
    }
    
]