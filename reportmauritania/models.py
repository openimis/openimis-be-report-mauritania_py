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
import os
from PIL import Image, ImageDraw, ImageFont

# def beneficiary_card_query(user, **kwargs):

#     # Create qr code instance
#     qr = qrcode.QRCode()

#     insureeObj = Insuree.objects.filter(
#             chf_id="070707070",
#             validity_to__isnull=True
#             ).first()

#     # The data that you want to store
#     data = {
#         'chf_id': insureeObj.chf_id,
#         'last_name': insureeObj.last_name,      
#         'other_names': insureeObj.other_names
#     }

#     # Add data
#     qr.add_data(data)

#     # Generate the QR Code
#     qr.make()

#     # Create an image from the QR Code instance
#     img = qr.make_image()

#     # Create a BytesIO object
#     buffered = BytesIO()

#     # Save the image to the BytesIO object
#     img.save(buffered, format="png")

#     # Get the byte data
#     img_str = base64.b64encode(buffered.getvalue())
#     #img_encoded = base64.b64encode(img.getvalue())

#     filename = "openIMISphone/"+insureeObj.photo.folder+"/"+insureeObj.photo.filename
#     print(filename)
#     if os.path.exists(filename):
#         with open(filename, "rb") as image_file:
#             encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
#     else :
#         with open("default-img.png", "rb") as image_file:
#             encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
#         print("File not found")


#     dictBase =  {
#         "QrCode": "data:image/PNG;base64,"+img_str.decode("utf-8"),
#         "PhotoInsuree": "data:image/PNG;base64,"+encoded_img,
#         "Prenom" : insureeObj.other_names,
#         "Nom" : insureeObj.last_name,
#         "DateNaissance" : insureeObj.dob,
#         "DateExpiration" : insureeObj.dob,
#         "idInsuree" : insureeObj.chf_id
#         }

#     print(dictBase)
#     return dictBase

def beneficiaries_list_card_query(user, **kwargs):
    ids = kwargs.get("insureeids", [])
    insurees_ids = []
    if ids:
        ids = ids.split(',')
        insurees_ids = [eval(i) for i in ids]
    # Create qr code instance
    qr = qrcode.QRCode()
    
    insuree_list = Insuree.objects.filter(
            id__in=insurees_ids,
            validity_to__isnull=True
            )

    insurees_data = []
    print("list is ", insuree_list)
    for insureeObj in insuree_list:
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

        filename = ""
        try:
            filename = "openIMISphone/"+insureeObj.photo.folder+"/"+insureeObj.photo.filename
        except:
            pass
        print(filename)
        if os.path.exists(filename):
            with open(filename, "rb") as image_file:
                encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
        else :
            with open("default-img.png", "rb") as image_file:
                encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
            print("File not found")

        insuree_policy = InsureePolicy.objects.filter(
            insuree__id=insureeObj.id,
            validity_to__isnull=True).order_by('-expiry_date').first()
        
        # Last name as image
        font = ImageFont.truetype("/openimis-be/openIMIS/fonts/arabic.ttf", size=60)
        img_prenom = Image.new('RGB', (500, 60), color = (255, 255, 255))
        d = ImageDraw.Draw(img_prenom)
        d.text((10,10), str(insureeObj.other_names), fill=(63, 22, 168), font=font)
        my_buffered = BytesIO()
        img_prenom.save(my_buffered, format="png")
        img_prenom_str = base64.b64encode(my_buffered.getvalue())

        # Firstname as image
        img_nom = Image.new('RGB', (500, 60), color = (255, 255, 255))
        d = ImageDraw.Draw(img_nom)
        d.text((10,10), str(insureeObj.last_name), fill=(63, 22, 168), font=font)
        my_buffered = BytesIO()
        img_nom.save(my_buffered, format="png")
        img_nom_str = base64.b64encode(my_buffered.getvalue())

        mydata = {
            "QrCode": "data:image/PNG;base64,"+img_str.decode("utf-8"),
            "PhotoInsuree": "data:image/PNG;base64,"+encoded_img,
            "Prenom" : insureeObj.other_names,
            "Nom" : insureeObj.last_name,
            "DateNaissance" : insureeObj.dob,
            "idInsuree" : insureeObj.chf_id,
            "imagePrenom": "data:image/PNG;base64,"+img_prenom_str.decode("utf-8"),
            "imageNom": "data:image/PNG;base64,"+img_nom_str.decode("utf-8")
            }
        if insuree_policy:
            mydata.update({
                "DateExpiration" : insuree_policy.expiry_date
                }
            )
        insurees_data.append(mydata)
    dictBase =  {
        "InsureeList" : insurees_data
        }

    print(dictBase)
    return dictBase
