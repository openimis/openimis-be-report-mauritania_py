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
import imghdr, time
from claim.models import Claim, ClaimService, ClaimItem
from core import fields

val_de_zero = [
    'million', 'milliard', 'billion',
    'quadrillion', 'quintillion', 'sextillion',
    'septillion', 'octillion', 'nonillion',
    'décillion', 'undecillion', 'duodecillion',
    'tredecillion', 'quattuordecillion', 'sexdecillion',
    'septendecillion', 'octodecillion', 'icosillion', 'vigintillion'
]

to_19_fr = (
    'zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six',
    'sept', 'huit', 'neuf', 'dix', 'onze', 'douze', 'treize',
    'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf'
)

tens_fr  = (
    'vingt', 'trente', 'quarante', 'cinquante', 'soixante', 'soixante',
    'quatre-vingts', 'quatre-vingt'
)

denom_fr = (
    '', 'mille', 'million', 'milliard', 'billion', 'quadrillion',
    'quintillion', 'sextillion', 'septillion', 'octillion', 'nonillion',
    'décillion', 'undecillion', 'duodecillion', 'tredecillion',
    'quattuordecillion', 'sexdecillion', 'septendecillion',
    'octodecillion', 'icosillion', 'vigintillion'
)

denoms_fr = (
    '', 'mille', 'millions', 'milliards', 'billions', 'quadrillions',
    'quintillions', 'sextillions', 'septillions', 'octillions', 'nonillions',
    'décillions', 'undecillions', 'duodecillions', 'tredecillions',
    'quattuordecillions', 'sexdecillions', 'septendecillions',
    'octodecillions', 'icosillions', 'vigintillions'
)
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

def _convert_nnn_fr(val):
    """
    \detail         convert a value < 1000 to french
        special cased because it is the level that kicks 
        off the < 100 special case.  The rest are
        more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    \param  val     value(int or float) to convert
    \return         a string value
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if (rem>1 and rem <10 and mod <= 0): 
             word = to_19_fr[rem] + ' cents'
        else: 
             word = to_19_fr[rem] + ' cent'
             
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_fr(mod)
    return word

def _convert_nn_fr(val):
    """
    \brief       convert a value < 100 to French
    \param  val  value to convert 
    """
    if val < 20:
        return to_19_fr[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
        if dval + 10 > val:
            if dval in (70,90):
                return dcap + '-' + to_19_fr[val % 10 + 10]
            if val % 10:
                return dcap + '-' + to_19_fr[val % 10]
            return dcap

def french_number(val):
    
    """
    \brief       Convert a numeric value to a french string
        Dispatch diffent kinds of number depending
        on their value (<100 or < 1000)
        Then create a for loop to rewrite cutted number.
    \param  val  value(int or float) to convert
    \return      a string value
    """
    
    if val < 100:
        return _convert_nn_fr(val)
    if val < 1000:
         return _convert_nnn_fr(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            
            pref_final = _convert_nnn_fr(l)
            pref = pref_final.split(' ')
            if(pref[len(pref)-1] == ' cent'):
                pref[len(pref)-1] = " cents"
                pref_final = " ".join(x for x in pref)
            if l>1:    
                ret = pref_final + ' ' + denoms_fr[didx]
            else:
                ret = pref_final + ' ' + denom_fr[didx]
            if r > 0:
                ret = ret + ' ' + french_number(r)
            return ret

def amount_to_text_fr(number, currency):
    """
    \brief              convert amount value to french string
        reuse the french_number function
        to write the correct number
        in french, then add the specific cents for number < 0
        and add the currency to the string
    \param  number      the number to convert
    \param  currency    string value of the currency
    \return             the string amount in french
    """
    try:
        number = int(number)
    except:
        return 'Traduction error'
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = french_number(abs(int(list[0])))

    #On enleve le un au debut de la somme écrite en lettre.
    liste = str(start_word).split(' ')
    for i in range(len(liste)):
        item = liste[i]
        tab=liste
        if item =='un':
            if i==0 and len(liste) > 1:
                if liste[i+1] not in val_de_zero:
                    tab[i]=""
            elif i > 0 and len(liste) > 1:
                if i < len(liste)-1:
                    if liste[i+1] not in val_de_zero:
                        if not liste[i-1] in ["cent", "cents"] and not (liste[i+1] in val_de_zero or liste[i+1] in denom_fr or liste[i+1] in denoms_fr):
                            tab[i]=""
            start_word = " ".join(x for x in tab)
    french_number(int(list[1]))
    final_result = start_word +' '+units_name
    return final_result


class PrintedReportsHistory(models.Model):
    """ Class PrintedReportsHistory :
    Class for reports already printed
    """
    id = models.AutoField(db_column='ID', primary_key=True)
    seq = models.CharField(db_column='Sequence', max_length=6)
    fosa = models.CharField(db_column='Fosa', max_length=248)
    start_date = fields.DateField(db_column='startDate', blank=True, null=True)
    end_date = fields.DateField(db_column='endDate', blank=True, null=True)

    class Meta:
        db_table = "tblPrintedReportsHistory"

def invoice_report_query(user, **kwargs):
    date_from = kwargs.get("dateFrom")
    date_to = kwargs.get("dateTo")
    hflocation = kwargs.get("hflocation")
    format = "%Y-%m-%d"
    date_from_object = datetime.datetime.strptime(date_from, format)
    date_from_str = date_from_object.strftime("%d/%m/%Y")

    date_to_object = datetime.datetime.strptime(date_to, format)
    date_to_str = date_to_object.strftime("%d/%m/%Y")
    report_fetch = PrintedReportsHistory.objects.filter(
        start_date=date_from,
        end_date=date_to,
        fosa=hflocation
    )
    print("report_fetch ", report_fetch)
    if report_fetch:
        numero_facture = report_fetch[0].seq
        print("Exitant ", numero_facture)
    else:
        print("Non exitant")
        report_max_seq = PrintedReportsHistory.objects.filter(
            fosa=hflocation
        ).order_by('-seq').first()
        prochain = 1
        if report_max_seq:
            prochain = int(report_max_seq.seq) + 1
        numero_facture = "{:0>6}".format(str(prochain))
        PrintedReportsHistory.objects.create(
            **{
                "seq": "{:0>6}".format(str(prochain)),
                "fosa": hflocation,
                "start_date": date_from,
                "end_date": date_to
            }
        )   

    dict_geo = {}
    data = []
    maintenant = time.strftime("%d/%m/%Y")
    annee = date_from_str.split("/")[2]
    mois = ""
    debut = int(str(date_from_str).split("/")[1])
    fin = int(str(date_to_str).split("/")[1])
    for i in range(debut, fin+1):
        mois += str(i)
        if i != fin:
            mois += ", "
    dictBase = {
        "date_impression": str(maintenant).replace("/", "."),
        "mois_facturation": mois,
        "numero_facture": hflocation + "/" + annee + "/" + str(date_from_str).split("/")[1] + "/" + numero_facture,
        "periode": str(date_from_str).replace("/", ".") + " au " + str(date_to_str).replace("/", "."),
        "data1": "Numéro de compte de la structure sanitaire:\nN°: ",
        "data2": "Adresse:\n\nTéléphone:\n\nE-mail:"
    }
    total_forfait = 0
    total_montant_moderateur = 0
    if hflocation:
        hflocation_obj = HealthFacility.objects.filter(
            code=hflocation,
            validity_to__isnull=True
            ).first()
        dictBase["fosa"] = hflocation_obj.name
        dictBase["responsable"] = hflocation_obj.responsible or ""
        adresse = "Adresse:\n\n"
        if hflocation_obj.address:
            adresse = "Adresse: " + hflocation_obj.address + "\n\n"
        telephone = "Téléphone: \n\n"
        if hflocation_obj.phone:
            telephone = "Téléphone: " + hflocation_obj.phone + "\n\n"
        email = "E-mail: "
        if hflocation_obj.email:
            email = "E-mail: " + hflocation_obj.email
        dictBase["data2"] = adresse + telephone + email
        if hflocation_obj.acc_code:
            dictBase["data1"] +=  hflocation_obj.acc_code
        claim_list = Claim.objects.filter(
            status__gte=4
        ).filter(
            submit_stamp__gte=date_from,
            submit_stamp__lte=date_to,
            validity_to__isnull=True,
            health_facility=hflocation_obj.id,
            **dict_geo
        )
        count = 1
        if claim_list:
            for claim in claim_list:
                claim_services = ClaimService.objects.filter(
                    claim = claim,
                    status=1
                )
                type_visite = ""
                if claim.visit_type == "1":
                    type_visite = "Urgence"
                elif claim.visit_type == "2":
                    type_visite = "Référence"
                elif claim.visit_type == "3":
                    type_visite = "Maladie"
                elif claim.visit_type == "4":
                    type_visite = "Maternité"
                elif claim.visit_type == "5":
                    type_visite = "Suivi de l'HTA"
                elif claim.visit_type == "6":
                    type_visite = "Suivi du diabète"
                elif claim.visit_type == "7":
                    type_visite = "Réanimation"
                elif claim.visit_type == "8":
                    type_visite = "AVP"
                elif claim.visit_type == "9":
                    type_visite = "Autres"
                for claim_service in claim_services:
                    montant_ticket_moderateur = 0
                    if claim_service.price_valuated:
                        if claim_service.service.price > claim_service.price_valuated:
                            montant_ticket_moderateur = claim_service.service.price - claim_service.price_valuated
                            total_montant_moderateur += montant_ticket_moderateur
                    total_forfait += claim_service.service.price
                    val = {
                        "numero": str(count),
                        "type_visite": type_visite,
                        "montant_forfait": str("{:,.0f}".format(claim_service.service.price)),
                        "montant_ticket_moderateur": str("{:,.0f}".format(montant_ticket_moderateur)),
                        "code_assure": claim.insuree.chf_id,
                        "nom_complet": claim.insuree.last_name + " " + claim.insuree.other_names,
                        "date_prestation": str(claim.date_from),
                        "numero_feuille": claim.code
                    }
                    count +=1
                    data.append(val)
            for claim in claim_list:
                claim_items = ClaimItem.objects.filter(
                    claim = claim,
                    status=1
                )
                type_visite = ""
                if claim.visit_type == "1":
                    type_visite = "Urgence"
                elif claim.visit_type == "2":
                    type_visite = "Référence"
                elif claim.visit_type == "3":
                    type_visite = "Maladie"
                elif claim.visit_type == "4":
                    type_visite = "Maternité"
                elif claim.visit_type == "5":
                    type_visite = "Suivi de l'HTA"
                elif claim.visit_type == "6":
                    type_visite = "Suivi du diabète"
                elif claim.visit_type == "7":
                    type_visite = "Réanimation"
                elif claim.visit_type == "8":
                    type_visite = "AVP"
                elif claim.visit_type == "9":
                    type_visite = "Autres"
                for claim_item in claim_items:
                    montant_ticket_moderateur = 0
                    if claim_item.price_valuated:
                        if claim_item.item.price > claim_item.price_valuated:
                            montant_ticket_moderateur = claim_item.item.price - claim_item.price_valuated
                            total_montant_moderateur += montant_ticket_moderateur
                    total_forfait += claim_item.item.price
                    val = {
                        "numero": str(count),
                        "type_visite": type_visite,
                        "montant_forfait": str("{:,.0f}".format(claim_item.item.price)),
                        "montant_ticket_moderateur": str("{:,.0f}".format(montant_ticket_moderateur)),
                        "code_assure": claim.insuree.chf_id,
                        "nom_complet": claim.insuree.last_name + " " + claim.insuree.other_names,
                        "date_prestation": str(claim.date_from),
                        "numero_feuille": claim.code
                    }
                    count +=1
                    data.append(val)
    dictBase["total_forfait"] = str("{:,.0f}".format(total_forfait))
    dictBase["total_moderateur"] = str("{:,.0f}".format(total_montant_moderateur))
    dictBase["total_a_payer"] = str("{:,.0f}".format(total_forfait - total_montant_moderateur))
    dictBase["montant_en_lettre"] = amount_to_text_fr(int(total_forfait - total_montant_moderateur), 'MRU')
    dictBase["service_and_itemsList"] = data
    # print(dictBase)
    return dictBase

def invoice_report_query_payment(user, **kwargs):
    date_from = kwargs.get("dateFrom")
    date_to = kwargs.get("dateTo")
    hflocation = kwargs.get("hflocation")
    format = "%Y-%m-%d"
    date_from_object = datetime.datetime.strptime(date_from, format)
    date_from_str = date_from_object.strftime("%d/%m/%Y")

    date_to_object = datetime.datetime.strptime(date_to, format)
    date_to_str = date_to_object.strftime("%d/%m/%Y")
    report_fetch = PrintedReportsHistory.objects.filter(
        start_date=date_from,
        end_date=date_to,
        fosa=hflocation
    )
    print("report_fetch ", report_fetch)
    if report_fetch:
        numero_facture = report_fetch[0].seq
        print("Exitant ", numero_facture)
    else:
        print("Non exitant")
        report_max_seq = PrintedReportsHistory.objects.filter(
            fosa=hflocation
        ).order_by('-seq').first()
        prochain = 1
        if report_max_seq:
            prochain = int(report_max_seq.seq) + 1
        numero_facture = "{:0>6}".format(str(prochain))
        PrintedReportsHistory.objects.create(
            **{
                "seq": "{:0>6}".format(str(prochain)),
                "fosa": hflocation,
                "start_date": date_from,
                "end_date": date_to
            }
        )   

    dict_geo = {}
    data = []
    maintenant = time.strftime("%d/%m/%Y")
    annee = date_from_str.split("/")[2]
    mois = ""
    debut = int(str(date_from_str).split("/")[1])
    fin = int(str(date_to_str).split("/")[1])
    for i in range(debut, fin+1):
        mois += str(i)
        if i != fin:
            mois += ", "
    dictBase = {
        "date_impression": str(maintenant).replace("/", "."),
        "mois_facturation": mois,
        "numero_facture": hflocation + "/" + annee + "/" + str(date_from_str).split("/")[1] + "/" + numero_facture,
        "periode": str(date_from_str).replace("/", ".") + " au " + str(date_to_str).replace("/", "."),
        "data1": "Numéro de compte de la structure sanitaire:\nN°: ",
        "data2": "Adresse:\n\nTéléphone:\n\nE-mail:"
    }
    total_forfait = 0
    total_montant_moderateur = 0
    if hflocation:
        hflocation_obj = HealthFacility.objects.filter(
            code=hflocation,
            validity_to__isnull=True
            ).first()
        dictBase["fosa"] = hflocation_obj.name
        dictBase["responsable"] = hflocation_obj.responsible or ""
        adresse = "Adresse:\n\n"
        if hflocation_obj.address:
            adresse = "Adresse: " + hflocation_obj.address + "\n\n"
        telephone = "Téléphone: \n\n"
        if hflocation_obj.phone:
            telephone = "Téléphone: " + hflocation_obj.phone + "\n\n"
        email = "E-mail: "
        if hflocation_obj.email:
            email = "E-mail: " + hflocation_obj.email
        dictBase["data2"] = adresse + telephone + email
        if hflocation_obj.acc_code:
            dictBase["data1"] +=  hflocation_obj.acc_code
        claim_list = Claim.objects.filter(
            status=16
        ).filter(
            submit_stamp__gte=date_from,
            submit_stamp__lte=date_to,
            validity_to__isnull=True,
            health_facility=hflocation_obj.id,
            **dict_geo
        )
        count = 1
        if claim_list:
            for claim in claim_list:
                claim_services = ClaimService.objects.filter(
                    claim = claim,
                    status=1
                )
                type_visite = ""
                if claim.visit_type == "1":
                    type_visite = "Urgence"
                elif claim.visit_type == "2":
                    type_visite = "Référence"
                elif claim.visit_type == "3":
                    type_visite = "Maladie"
                elif claim.visit_type == "4":
                    type_visite = "Maternité"
                elif claim.visit_type == "5":
                    type_visite = "Suivi de l'HTA"
                elif claim.visit_type == "6":
                    type_visite = "Suivi du diabète"
                elif claim.visit_type == "7":
                    type_visite = "Réanimation"
                elif claim.visit_type == "8":
                    type_visite = "AVP"
                elif claim.visit_type == "9":
                    type_visite = "Autres"
                for claim_service in claim_services:
                    montant_ticket_moderateur = 0
                    if claim_service.price_valuated:
                        if claim_service.service.price > claim_service.price_valuated:
                            montant_ticket_moderateur = claim_service.service.price - claim_service.price_valuated
                            total_montant_moderateur += montant_ticket_moderateur
                    total_forfait += claim_service.service.price
                    val = {
                        "numero": str(count),
                        "type_visite": type_visite,
                        "montant_forfait": str("{:,.0f}".format(claim_service.service.price)),
                        "montant_ticket_moderateur": str("{:,.0f}".format(montant_ticket_moderateur)),
                        "code_assure": claim.insuree.chf_id,
                        "nom_complet": claim.insuree.last_name + " " + claim.insuree.other_names,
                        "date_prestation": str(claim.date_from),
                        "numero_feuille": claim.code
                    }
                    count +=1
                    data.append(val)
            for claim in claim_list:
                claim_items = ClaimItem.objects.filter(
                    claim = claim,
                    status=1
                )
                type_visite = ""
                if claim.visit_type == "1":
                    type_visite = "Urgence"
                elif claim.visit_type == "2":
                    type_visite = "Référence"
                elif claim.visit_type == "3":
                    type_visite = "Maladie"
                elif claim.visit_type == "4":
                    type_visite = "Maternité"
                elif claim.visit_type == "5":
                    type_visite = "Suivi de l'HTA"
                elif claim.visit_type == "6":
                    type_visite = "Suivi du diabète"
                elif claim.visit_type == "7":
                    type_visite = "Réanimation"
                elif claim.visit_type == "8":
                    type_visite = "AVP"
                elif claim.visit_type == "9":
                    type_visite = "Autres"
                for claim_item in claim_items:
                    montant_ticket_moderateur = 0
                    if claim_item.price_valuated:
                        if claim_item.item.price > claim_item.price_valuated:
                            montant_ticket_moderateur = claim_item.item.price - claim_item.price_valuated
                            total_montant_moderateur += montant_ticket_moderateur
                    total_forfait += claim_item.item.price
                    val = {
                        "numero": str(count),
                        "type_visite": type_visite,
                        "montant_forfait": str("{:,.0f}".format(claim_item.item.price)),
                        "montant_ticket_moderateur": str("{:,.0f}".format(montant_ticket_moderateur)),
                        "code_assure": claim.insuree.chf_id,
                        "nom_complet": claim.insuree.last_name + " " + claim.insuree.other_names,
                        "date_prestation": str(claim.date_from),
                        "numero_feuille": claim.code
                    }
                    count +=1
                    data.append(val)
    dictBase["total_forfait"] = str("{:,.0f}".format(total_forfait))
    dictBase["total_moderateur"] = str("{:,.0f}".format(total_montant_moderateur))
    dictBase["total_a_payer"] = str("{:,.0f}".format(total_forfait - total_montant_moderateur))
    dictBase["montant_en_lettre"] = amount_to_text_fr(int(total_forfait - total_montant_moderateur), 'MRU')
    dictBase["service_and_itemsList"] = data
    # print(dictBase)
    return dictBase

def beneficiaries_membership_card_query(user, **kwargs):
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
        font = ImageFont.truetype("/openimis-be/openIMIS/fonts/arabic.ttf", size=65)
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
        d.text((10,10), str(insureeObj.last_name), fill=(0, 0, 0), font=font)
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
        d.text((10,10), str(arab_last_name), fill=(0, 0, 0), font=font, direction='rtl', align='right')
        my_buffered = BytesIO()
        img_nom_arabe.save(my_buffered, format="png")
        img_nom_arabe_str = base64.b64encode(my_buffered.getvalue())

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
            "telephone": insureeObj.phone,
            "numAsuree": insureeObj.chf_id,
            "nni": insureeObj.passport or ""
        }
        if insuree_policy:
            date_ouverture_droit = datetime.datetime.strptime(str(insuree_policy.policy.effective_date), '%Y-%m-%d').strftime("%d-%m-%Y")
            expiry_date = datetime.datetime.strptime(str(insuree_policy.policy.expiry_date), '%Y-%m-%d').strftime("%d-%m-%Y")
            mydata.update({
                "DateOuvertureDroit": str(insuree_policy.policy.effective_date),
                "DateValidite": str(insuree_policy.policy.expiry_date),
                "DateOuvertureDroitArabe": str(date_ouverture_droit),
                "DateValiditeArabe": str(expiry_date),
                "MontantCotisation": str("{:,.0f}".format(float(int(insuree_policy.policy.value))))
                }
            )
        insurees_data.append(mydata)
    dictBase =  {
        "InsureeList" : insurees_data,
        }
    return dictBase