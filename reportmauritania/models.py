from tokenize import String
from django.db import models
from core import models as core_models
from report.services import run_stored_proc_report
from location.models import Location, HealthFacility
from policy.models import Policy
from insuree.models import Insuree
from collections import defaultdict
from django.db.models import Count
from django.db.models import F
from insuree.models import Insuree
from insuree.models import InsureePolicy
import datetime
import qrcode
import base64
from io import BytesIO

def beneficiary_card_query(user, **kwargs):

    # Create qr code instance
    qr = qrcode.QRCode()

    insureeObj = Insuree.objects.filter(
            chf_id="346940557",
            validity_to__isnull=True
            ).first()

    # The data that you want to store
    data = {
        'chf_id': insureeObj.chf_id,
        'last_name': insureeObj.last_name,      
        'other_names': insureeObj.other_names
    }

    # Add data
    qr.add_data(data)

    # Generate the QR Code
    qr.make()

    # Create an image from the QR Code instance
    img = qr.make_image()

    # Create a BytesIO object
    buffered = BytesIO()

    # Save the image to the BytesIO object
    img.save(buffered, format="png")

    # Get the byte data
    img_str = base64.b64encode(buffered.getvalue())
    #img_encoded = base64.b64encode(img.getvalue())
    print(img_str)
    print(insureeObj.photo.folder)
    print(insureeObj.photo.filename)
    dictBase =  {
        "QrCode": "data:image/PNG;base64,"+img_str.decode("utf-8"),
        "PhotoInsuree": "data:image/PNG;base64,"+img_str.decode("utf-8"),
        "Prenom" : insureeObj.other_names,
        "Nom" : insureeObj.last_name,
        "DateNaissance" : insureeObj.dob,
        "DateExpiration" : insureeObj.dob,
        }

    print(dictBase)
    return dictBase