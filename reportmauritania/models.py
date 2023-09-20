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
import imghdr
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
    
    insuree_list = Insuree.objects.filter(
            id__in=insurees_ids,
            validity_to__isnull=True
            )

    insurees_data = []
    print("list is ", insuree_list)
    for insureeObj in insuree_list:
        # Create qr code instance
        qr = qrcode.QRCode()
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
 
        if insureeObj.photo and insureeObj.photo.photo:
            imageData = str(insureeObj.photo.photo)
            myimage = base64.b64decode((imageData))
            extension = imghdr.what(None, h=myimage)
            print("extension ", extension)
            if str(extension).lower() != 'png':
                # save image to png, image can have different format leading to an
                # error : image is not PNG
                imgFile = open('/tmp/'+insureeObj.chf_id+'.jpeg', 'wb')
                imgFile.write(myimage)
                imgFile.close()

                img1 = Image.open(r'/tmp/'+insureeObj.chf_id+'.jpeg')
                img1.save(r'/tmp/'+insureeObj.chf_id+'.png')

                with open('/tmp/'+insureeObj.chf_id+'.png', "rb") as image_file:
                    encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
            else:
                # already the expected extension (PNG)
                encoded_img = imageData
        else:
            filename = ""
            try:
                filename = "openIMISphone/"+insureeObj.photo.folder+"/"+insureeObj.photo.filename
            except Exception as e:
                print(e)
            print(filename)
            if os.path.exists(filename):
                with open(filename, "rb") as image_file:
                    imageData = base64.b64encode(image_file.read()).decode('utf-8')
                    myimage = base64.b64decode((imageData))
                    extension = imghdr.what(None, h=myimage)
                    print("extension is: ", extension)
                    if str(extension).lower() != 'png':
                        # save image to png, image can have different format leading to an
                        # error : image is not PNG
                        imgFile = open('/tmp/'+insureeObj.chf_id+'.jpeg', 'wb')
                        imgFile.write(myimage)
                        imgFile.close()

                        img1 = Image.open(r'/tmp/'+insureeObj.chf_id+'.jpeg')
                        img1.save(r'/tmp/'+insureeObj.chf_id+'.png')

                        with open('/tmp/'+insureeObj.chf_id+'.png', "rb") as image_file:
                            encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
                    else:
                        # already the expected extension (PNG)
                        encoded_img = imageData
            else:
                with open("default-img.png", "rb") as image_file:
                    encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
                print("File not found")

        insuree_policy = InsureePolicy.objects.filter(
            insuree__id=insureeObj.id,
            validity_to__isnull=True).order_by('-expiry_date').first()
        
        # Last name as image
        font = ImageFont.truetype("/openimis-be/openIMIS/fonts/arabic.ttf", size=50)
        img_prenom = Image.new('RGB', (500, 60), color = (255, 255, 255))
        d = ImageDraw.Draw(img_prenom)
        d.text((10,10), str(insureeObj.other_names), fill=(63, 22, 168), font=font)
        my_buffered = BytesIO()
        img_prenom.save(my_buffered, format="png")
        img_prenom_str = base64.b64encode(my_buffered.getvalue())

        # Last name (Arab) as image
        img_prenom_arabe = Image.new('RGB', (500, 60), color = (255, 255, 255))
        d = ImageDraw.Draw(img_prenom_arabe)
        arab_other_names = insureeObj.arab_other_names or ""
        if arab_other_names:
            taille = len(arab_other_names)
            print("taille ON ", taille)
            if taille < 35:
                # On ajoute les espaces pour pousser le texte a gauche, en arabe
                end = 35 - taille
                i = 1
                char = ""
                while i < end:
                    char += " "
                    i += 1
                arab_other_names += char
        d.text((10,10), str(arab_other_names), fill=(63, 22, 168), font=font, direction='rtl', align='right')
        my_buffered = BytesIO()
        img_prenom_arabe.save(my_buffered, format="png")
        img_prenom_arabe_str = base64.b64encode(my_buffered.getvalue())

        
        
        # Firstname as image
        img_nom = Image.new('RGB', (500, 60), color = (255, 255, 255))
        d = ImageDraw.Draw(img_nom)
        d.text((10,10), str(insureeObj.last_name), fill=(63, 22, 168), font=font)
        my_buffered = BytesIO()
        img_nom.save(my_buffered, format="png")
        img_nom_str = base64.b64encode(my_buffered.getvalue())

        # Firstname (Arab) as image
        img_nom_arabe = Image.new('RGB', (500, 60), color = (255, 255, 255))
        d = ImageDraw.Draw(img_nom_arabe)
        arab_last_name = insureeObj.arab_last_name or ""
        if arab_last_name:
            taille = len(arab_last_name)
            print("taille LN ", taille)
            if taille < 35:
                # On ajoute les espaces pour pousser le texte a gauche, en arabe
                end = 35 - taille
                i = 1
                char = ""
                while i < end:
                    char += " "
                    i += 1
                arab_last_name += char
        d.text((10,10), str(arab_last_name), fill=(63, 22, 168), font=font, direction='rtl', align='right')
        my_buffered = BytesIO()
        img_nom_arabe.save(my_buffered, format="png")
        img_nom_arabe_str = base64.b64encode(my_buffered.getvalue())

        # title as image
        boldfont = ImageFont.truetype("/openimis-be/openIMIS/fonts/arialbd.ttf", size=40)
        img_nom_titre = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_nom_titre)
        titre = "Prénom"
        d.text((10,55), str(titre), fill=(63, 22, 168), font=boldfont)
        my_buffered = BytesIO()
        img_nom_titre.save(my_buffered, format="png")
        img_titre_str = base64.b64encode(my_buffered.getvalue())

        mydata = {
            "QrCode": "data:image/PNG;base64,"+img_str.decode("utf-8"),
            "PhotoInsuree": "data:image/PNG;base64,"+str(encoded_img),
            "Prenom" : insureeObj.other_names,
            "Nom" : insureeObj.last_name,
            "DateNaissance" : insureeObj.dob,
            "idInsuree" : insureeObj.chf_id,
            "imagePrenom": "data:image/PNG;base64,"+img_prenom_str.decode("utf-8"),
            "imageNom": "data:image/PNG;base64,"+img_nom_str.decode("utf-8"),
            "imagePrenomArabe": "data:image/PNG;base64,"+img_prenom_arabe_str.decode("utf-8"),
            "imageNomArabe": "data:image/PNG;base64,"+img_nom_arabe_str.decode("utf-8"),
            }
        if insuree_policy:
            mydata.update({
                "DateExpiration" : insuree_policy.expiry_date
                }
            )
        insurees_data.append(mydata)
    dictBase =  {
        "InsureeList" : insurees_data,
        "image_title": "data:image/PNG;base64,"+img_titre_str.decode("utf-8")
        }

    print(dictBase)
    return dictBase

def beneficiaries_embership_card_query(user, **kwargs):
    ids = kwargs.get("insureeids", [])
    insurees_ids = []
    if ids:
        ids = ids.split(',')
        insurees_ids = [eval(i) for i in ids]
    
    insuree_list = Insuree.objects.filter(
            id__in=insurees_ids,
            # validity_to__isnull=True
            )

    insurees_data = []
    for insureeObj in insuree_list:
        # Create qr code instance
        qr = qrcode.QRCode()
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
 
        if insureeObj.photo and insureeObj.photo.photo:
            imageData = str(insureeObj.photo.photo)
            myimage = base64.b64decode((imageData))
            extension = imghdr.what(None, h=myimage)
            print("extension ", extension)
            if str(extension).lower() != 'png':
                # save image to png, image can have different format leading to an
                # error : image is not PNG
                imgFile = open('/tmp/'+insureeObj.chf_id+'.jpeg', 'wb')
                imgFile.write(myimage)
                imgFile.close()

                img1 = Image.open(r'/tmp/'+insureeObj.chf_id+'.jpeg')
                img1.save(r'/tmp/'+insureeObj.chf_id+'.png')

                with open('/tmp/'+insureeObj.chf_id+'.png', "rb") as image_file:
                    encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
            else:
                # already the expected extension (PNG)
                encoded_img = imageData
        else:
            filename = ""
            try:
                filename = "openIMISphone/"+insureeObj.photo.folder+"/"+insureeObj.photo.filename
            except Exception as e:
                print(e)
            print(filename)
            if os.path.exists(filename):
                with open(filename, "rb") as image_file:
                    imageData = base64.b64encode(image_file.read()).decode('utf-8')
                    myimage = base64.b64decode((imageData))
                    extension = imghdr.what(None, h=myimage)
                    print("extension is: ", extension)
                    if str(extension).lower() != 'png':
                        # save image to png, image can have different format leading to an
                        # error : image is not PNG
                        imgFile = open('/tmp/'+insureeObj.chf_id+'.jpeg', 'wb')
                        imgFile.write(myimage)
                        imgFile.close()

                        img1 = Image.open(r'/tmp/'+insureeObj.chf_id+'.jpeg')
                        img1.save(r'/tmp/'+insureeObj.chf_id+'.png')

                        with open('/tmp/'+insureeObj.chf_id+'.png', "rb") as image_file:
                            encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
                    else:
                        # already the expected extension (PNG)
                        encoded_img = imageData
            else:
                with open("default-img.png", "rb") as image_file:
                    encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
                print("File not found")

        insuree_policy = InsureePolicy.objects.filter(
            insuree__id=insureeObj.id,
            validity_to__isnull=True).order_by('-expiry_date').first()
        
        # Last name as image
        font = ImageFont.truetype("/openimis-be/openIMIS/fonts/arabic.ttf", size=50)
        img_prenom = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_prenom)
        d.text((10,10), str(insureeObj.other_names), fill=(0, 0, 0), font=font)
        my_buffered = BytesIO()
        img_prenom.save(my_buffered, format="png")
        img_prenom_str = base64.b64encode(my_buffered.getvalue())

        # Last name (Arab) as image
        font = ImageFont.truetype("/openimis-be/openIMIS/fonts/arabic.ttf", size=60)
        img_prenom_arabe = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_prenom_arabe)
        arab_other_names = insureeObj.arab_other_names or ""
        if arab_other_names:
            taille = len(arab_other_names)
            print("taille ON ", taille)
            if taille < 35:
                # On ajoute les espaces pour pousser le texte a gauche, en arabe
                end = 35 - taille
                i = 1
                char = ""
                while i < end:
                    char += " "
                    i += 1
                arab_other_names += char
        d.text((10,10), str(arab_other_names), fill=(0, 0, 0), font=font, direction='rtl', align='right')
        my_buffered = BytesIO()
        img_prenom_arabe.save(my_buffered, format="png")
        img_prenom_arabe_str = base64.b64encode(my_buffered.getvalue())

        
        
        # Firstname as image
        img_nom = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_nom)
        d.text((10,10), str(insureeObj.last_name), fill=(63, 22, 168), font=font)
        my_buffered = BytesIO()
        img_nom.save(my_buffered, format="png")
        img_nom_str = base64.b64encode(my_buffered.getvalue())

        # Firstname (Arab) as image
        font = ImageFont.truetype("/openimis-be/openIMIS/fonts/arabic.ttf", size=65)
        img_nom_arabe = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_nom_arabe)
        arab_last_name = insureeObj.arab_last_name or ""
        if arab_last_name:
            taille = len(arab_last_name)
            print("taille LN ", taille)
            if taille < 35:
                # On ajoute les espaces pour pousser le texte a gauche, en arabe
                end = 35 - taille
                i = 1
                char = ""
                while i < end:
                    char += " "
                    i += 1
                arab_last_name += char
        d.text((10,10), str(arab_last_name), fill=(63, 22, 168), font=font, direction='rtl', align='right')
        my_buffered = BytesIO()
        img_nom_arabe.save(my_buffered, format="png")
        img_nom_arabe_str = base64.b64encode(my_buffered.getvalue())

        # label_prenom as image
        boldfont = ImageFont.truetype("/openimis-be/openIMIS/fonts/arialbd.ttf", size=80)
        img_nom_titre = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_nom_titre)
        titre = "Prénom"
        d.text((10,0), str(titre), fill=(0, 0, 0), font=boldfont)
        my_buffered = BytesIO()
        img_nom_titre.save(my_buffered, format="png")
        label_prenom = base64.b64encode(my_buffered.getvalue())

        # label_telephone as image
        boldfont = ImageFont.truetype("/openimis-be/openIMIS/fonts/arialbd.ttf", size=80)
        img_label_tel = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_label_tel)
        titre = "Téléphone"
        d.text((10,0), str(titre), fill=(0, 0, 0), font=boldfont)
        my_buffered = BytesIO()
        img_label_tel.save(my_buffered, format="png")
        label_tel = base64.b64encode(my_buffered.getvalue())

        # label_numero_assure as image
        boldfont = ImageFont.truetype("/openimis-be/openIMIS/fonts/arialbd.ttf", size=60)
        img_numero_titre = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_numero_titre)
        titre = "N° d'assuré :"
        d.text((10,10), str(titre), fill=(0, 0, 0), font=boldfont)
        my_buffered = BytesIO()
        img_numero_titre.save(my_buffered, format="png")
        label_numero_assure = base64.b64encode(my_buffered.getvalue())

        # label_date_validite as image
        boldfont = ImageFont.truetype("/openimis-be/openIMIS/fonts/arialbd.ttf", size=50)
        img_date_titre = Image.new('RGB', (500, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_date_titre)
        titre = "Date de validité :"
        d.text((10,10), str(titre), fill=(0, 0, 0), font=boldfont)
        my_buffered = BytesIO()
        img_date_titre.save(my_buffered, format="png")
        label_date_validite = base64.b64encode(my_buffered.getvalue())

        # label_date_validite as image
        font = ImageFont.truetype("/openimis-be/openIMIS/fonts/arabic.ttf", size=70)
        img_doc_titre = Image.new('RGB', (900, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img_doc_titre)
        titre = "Attestation de droits à l'assurance maladie"
        d.text((10,10), str(titre), fill=(0, 0, 0), font=font)
        my_buffered = BytesIO()
        img_doc_titre.save(my_buffered, format="png")
        label_titre_doc = base64.b64encode(my_buffered.getvalue())

        mydata = {
            "QrCode": "data:image/PNG;base64,"+img_str.decode("utf-8"),
            "PhotoInsuree": "data:image/PNG;base64,"+str(encoded_img),
            "Prenom" : insureeObj.other_names,
            "Nom" : insureeObj.last_name,
            "DateNaissance" : insureeObj.dob,
            "idInsuree" : insureeObj.chf_id,
            "imagePrenom": "data:image/PNG;base64,"+img_prenom_str.decode("utf-8"),
            "imageNom": "data:image/PNG;base64,"+img_nom_str.decode("utf-8"),
            "imagePrenomArabe": "data:image/PNG;base64,"+img_prenom_arabe_str.decode("utf-8"),
            "imageNomArabe": "data:image/PNG;base64,"+img_nom_arabe_str.decode("utf-8"),
            "titre_prenom": "data:image/PNG;base64,"+label_prenom.decode("utf-8"),
            "titre_tel": "data:image/PNG;base64,"+label_tel.decode("utf-8"),
            "titre_numero_assuree": "data:image/PNG;base64,"+label_numero_assure.decode("utf-8"),
            "titre_date_validite": "data:image/PNG;base64,"+label_date_validite.decode("utf-8"),
            "telephone": insureeObj.phone,
            "numAsuree": insureeObj.chf_id,
            "image_titre_doc": "data:image/PNG;base64,"+label_titre_doc.decode("utf-8"),
        }
        if insureeObj.type_of_id:
            if insureeObj.type_of_id.code == "N":
                if insureeObj.passport:
                    mydata.update({"nni": insureeObj.passport})
        if insuree_policy:
            mydata.update({
                "DateOuvertureDroit": str(insuree_policy.start_date),
                "DateValidite": str(insuree_policy.effective_date),
                "MontantCotisation": str(insuree_policy.policy.value)
                }
            )
        insurees_data.append(mydata)
    dictBase =  {
        "InsureeList" : insurees_data,
        }
    return dictBase