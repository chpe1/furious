import os
import sqlite3
import datetime
import plistlib
import biplist
import outils
import json
import sys


def obliterated(zip_ref, path):
    """
    Examine a ZipFile object to check if the file '/private/var/root/.obliterated' is present. 
    If the file is found, it retrieves the creation date but does not extract it.

    Parameters:
    zip_ref (ZipFile): A ZipFile object representing the archive to be examined (Full File System)
    path (str): the file path

    Returns:
    dict: A dictionary containing information about the '/private/var/root/.obliterated' file for integration in txt output.
        If the file is present:
            - 'DATE DE REINITIALISATION (.obliterated)': [reinit]
                where 'reinit' is the formatted creation date in the format 'dd/mm/yyyy à HH:MM:SS'.
        If the creation date cannot be determined:
            - 'DATE DE REINITIALISATION (.obliterated)': ['LE FICHIER A ETE TROUVE MAIS LE PROGRAMME N\'A PAS REUSSI A DETERMINER LA DATE DE CE DERNIER. UNE VERIFICATION MANUELLE EST NECESSAIRE']
    """
    # Si le fichier à extraire est obliterated, alors on récupère la date de création mais on ne l'extrait pas.
    info = zip_ref.getinfo(path)
    reinit = datetime.datetime(
        *info.date_time).strftime('%d/%m/%Y à %H:%M:%S')
    if reinit != '':
        return {
            'DATE DE REINITIALISATION (.obliterated):': [reinit]
        }
    else:
        return {
            'DATE DE REINITIALISATION (.obliterated):': ['LE FICHIER A ETE TROUVE MAIS LE PROGRAMME N\'A PAS REUSSI A DETERMINER LA DATE DE CE DERNIER. UNE VERIFICATION MANUELLE EST NECESSAIRE']
        }


def cellular_usage():
    """
    Retrieves informations from the CellularUsage.db database and returns a dictionary for integration in txt output.

    Returns:
        dict: A dictionary containing information from CellularUsage.db in the form of a list of lists.
              Each sub-list represents the details of a record.

    Example of output structure :
    {
        'CellularUsage': [
            ['-------------------------------',
             'INDEX: 1',
             'ICCID: 123456789',
             'MSISDN: 987654321',
             'DATE DE DERNIERE MISE A JOUR: 01/01/2023 à 14:30:45',
             'EMPLACEMENT: 1'],
            ...
        ]
    }
    """
    connexion = sqlite3.connect("./db/CellularUsage.db")
    cursor = connexion.cursor()
    cursor.execute(
        "SELECT ROWID, subscriber_id, subscriber_mdn, last_update_time, slot_id FROM subscriber_info")
    columns = [description[0] for description in cursor.description]
    dict_cellular_usage = [dict(zip(columns, row))
                           for row in cursor.fetchall()]

    line_export = {'CellularUsage': []}

    for dictionnaire in dict_cellular_usage:
        date_str = outils.convert_to_mac_absolutetime(
            dictionnaire['last_update_time'])
        dictionnaire['mac_absolute_time'] = date_str
        list_temp = [
            '-------------------------------',
            'INDEX: ' + str(dictionnaire['ROWID']),
            'ICCID: ' + str(dictionnaire['subscriber_id']),
            'MSISDN: ' + str(dictionnaire['subscriber_mdn']),
            'DATE DE DERNIERE MISE A JOUR: ' +
            str(dictionnaire['mac_absolute_time']),
            'EMPLACEMENT: ' + str(dictionnaire['slot_id'])
        ]
        line_export['CellularUsage'].append(list_temp)

    cursor.close()
    connexion.close()

    return line_export


def application_state():
    """
    Retrieves informations from the applicationState.db database (installed applications) and returns a dictionary for integration in txt output.
    Keeps only third-party applications.

    Returns:
        dict: A dictionary containing a list with the third-party applications who are installing on the system.
    """
    line_export = dict()
    connexion = sqlite3.connect(
        "./db/applicationState.db")
    cursor = connexion.cursor()
    cursor.execute(
        "select application_identifier_tab.[application_identifier], kvs.[value] from kvs, key_tab, application_identifier_tab where key_tab.[key]='compatibilityInfo' and kvs.[key]=key_tab.[id] and application_identifier_tab.[id]=kvs.[application_identifier] order by application_identifier_tab.[id]")
    columns = [description[0] for description in cursor.description]
    dict_application_state = [dict(zip(columns, row))
                              for row in cursor.fetchall()]
    name_app = list()
    for dictionnaire in dict_application_state:
        if not dictionnaire['application_identifier'].startswith("com.apple"):
            name_app.append(dictionnaire['application_identifier'])

    line_export['Applications tierces installées (applicationState.db)'] = name_app

    return line_export


def commcenter():
    """
    Read the file com.apple.commcenter.plist and extract the relevant informations.

    Returns:
        dict: A dictionary containing a list with the relevant informations for the txt output.
    """
    with open('./db/com.apple.commcenter.plist', 'rb') as fp:
        line_export = {
            'APPLE COMMCENTER :': []}

        plist_data = plistlib.load(fp)
        personal_wallet = plist_data['PersonalWallet']

        if 'SIMPhoneNumber' in plist_data.keys():
            line_export['APPLE COMMCENTER :'].append('Numéro de téléphone de la carte sim (SIMPhoneNumber) :' +
                                                     plist_data['SIMPhoneNumber'])

        if 'SecondSIMPhoneNumber' in plist_data.keys():
            line_export['APPLE COMMCENTER :'].append('Second numéro de téléphone de la carte sim (SIMPhoneNumber) :' +
                                                     plist_data['SecondSIMPhoneNumber'])

        if 'lastKnownOSVersion' in plist_data.keys():
            line_export['APPLE COMMCENTER :'].append(
                'Dernière version de l\'OS connu (LastKnownOSVersion): ' + str(plist_data['lastKnownOSVersion']))

        if 'LastKnownICCID' in plist_data.keys():
            line_export['APPLE COMMCENTER :'].append('Dernier ICCID connu (LastKnownICCID) :' +
                                                     str(plist_data['LastKnownICCID']))

        if 'PhoneNumber' in plist_data.keys():
            line_export['APPLE COMMCENTER :'].append('Numéro d\'appel enregistré dans le téléphone (PhoneNumber) : ' +
                                                     plist_data['PhoneNumber'])

        for k, v in personal_wallet.items():
            construct_line = 'ICCID : ' + k + ' { '
            if 'CarrierEntitlements' in personal_wallet[k].keys():
                if 'lastGoodImsi' in personal_wallet[k]['CarrierEntitlements']:
                    construct_line = construct_line + 'IMSI : ' + \
                        personal_wallet[k]['CarrierEntitlements']['lastGoodImsi']
                if 'kEntitlementsSelfRegistrationUpdateImei' in personal_wallet[k]['CarrierEntitlements']:
                    construct_line = construct_line + ', IMEI : ' + \
                        personal_wallet[k]['CarrierEntitlements']['kEntitlementsSelfRegistrationUpdateImei']
            if 'phonebook' in personal_wallet[k].keys():
                if 'CopiedSIMPhoneNumber' in personal_wallet[k]['phonebook']:
                    construct_line = construct_line + ', Numéro d\'appel : ' + \
                        personal_wallet[k]['phonebook']['CopiedSIMPhoneNumber']
            construct_line = construct_line + ' }'
            line_export['APPLE COMMCENTER :'].append(construct_line)
    return line_export


def lastbuildinfo():
    """
    Read the file LastBuildInfo.plist and extract the relevant informations (UUID APPLE and iOS version.)

    Returns:
        dict: A dictionary containing a list with UUID APPLE and iOS version for the txt output.
    """
    with open('./db/LastBuildInfo.plist', 'rb') as fp:
        plist_data = plistlib.load(fp)

        return {
            'LAST BUILD INFO :': [
                'Identifiant APPLE : ' + plist_data['BuildID'],
                'Version d\'iOS : ' + plist_data['FullVersionString']
            ]
        }


def aggregated():
    """
    Read the file com.apple.aggregated.plist and extract the last boot time.

    Returns:
        dict: A dictionary containing a list with the last boot time information for the txt output.
    """
    with open('./db/com.apple.aggregated.plist', 'rb') as fp:
        plist_data = plistlib.load(fp)
        line_export = {
            'AGGREGATED.PLIST :': []
        }

        if 'LastBoottime' in plist_data.keys():
            date_reboot = datetime.datetime.fromtimestamp(
                plist_data['LastBoottime']).strftime('%d-%m-%Y %H:%M:%S Heure Locale')
            line_export['AGGREGATED.PLIST :'].append(
                'Date de dernier redémarrage : ' + date_reboot)

        if 'UserName' in plist_data.keys():
            username = plist_data['UserName']
            line_export['AGGREGATED.PLIST :'].append(f'USERNAME : {username}')

    return line_export


def networkinterface():
    """
    Read the file NetworkInterfaces.plist and extract the MAC ADDRESS WIFI.

    Returns:
        dict: A dictionary containing a list with the MAC ADDRESS WIFI for the txt output.
    """
    with open('./db/NetworkInterfaces.plist', 'rb') as fp:
        plist_data = plistlib.load(fp)
        adresse_mac_wifi = ''
        for interface in plist_data['Interfaces']:
            if interface['SCNetworkInterfaceInfo']['UserDefinedName'] == 'Wi-Fi':
                adresse_mac_wifi = outils.format_mac(interface['IOMACAddress'])
        line_export = {
            'NETWORK INTERFACES.PLIST :': [
                'ADRESSE MAC WIFI : ' + str(adresse_mac_wifi),
            ]
        }
    return line_export


def accounts():
    """
    Query the Accounts3.sqlite database for extract the accounts.

    Returns:
        dict: A dictionary containing a list with the accounts found for the txt output.
    """
    line_export = dict()
    connexion = sqlite3.connect(
        "./db/Accounts3.sqlite")
    cursor = connexion.cursor()
    cursor.execute(
        "select ZUSERNAME from ZACCOUNT")
    columns = [description[0] for description in cursor.description]
    dict_account = [dict(zip(columns, row))
                    for row in cursor.fetchall()]
    usernames = set()
    for dictionnaire in dict_account:
        if dictionnaire['ZUSERNAME'] is not None and dictionnaire['ZUSERNAME'] != 'local':
            usernames.add(dictionnaire['ZUSERNAME'])

    line_export['COMPTES TROUVES (Accounts3.sqlite) : '] = usernames

    return line_export


def waze():
    """
    Query the Waze database for extract the travels
    Performs 3 queries (places, recents and favorites) and generates 1 csv for the answers to each query.

    Returns:
        dict: A dictionary containing a list with the information on the created file.
    """
    queries = [
        ("SELECT DATETIME(PLACES.created_time, 'UNIXEPOCH') AS \"Date UTC\", PLACES.name AS \"Nom\", PLACES.house AS \"N°\", PLACES.street AS \"rue\", PLACES.city AS \"Ville\", PLACES.state AS \"Etat\", PLACES.country AS \"Pays\", ROUND(PLACES.latitude, 6)/1000000 AS \"Latitude\", ROUND(PLACES.longitude, 6)/1000000 AS \"Longitude\" FROM PLACES", "places.csv"),
        ("SELECT RECENTS.place_id, DATETIME(RECENTS.created_time, 'UNIXEPOCH') AS \"Date de Création UTC\", DATETIME(RECENTS.access_time, 'UNIXEPOCH') AS \"Date de dernière d'utilisation UTC\", PLACES.name as \"Nom\", PLACES.house as \"N°\", places.street as \"rue\", PLACES.city as \"Ville\", PLACES.state as \"Etat\", PLACES.country as \"Pays\", DATETIME(PLACES.created_time, 'UNIXEPOCH') AS \"Date Création Places UTC\", round(PLACES.latitude, 6)/1000000 as \"Latitude\", ROUND(PLACES.longitude, 6)/1000000 as \"Longitude\" FROM RECENTS, PLACES WHERE RECENTS.place_id = PLACES.id", "recents.csv"),
        ("SELECT FAVORITES.place_id, DATETIME(FAVORITES.created_time, 'UNIXEPOCH') AS \"Date de Création UTC\", DATETIME(FAVORITES.modified_time, 'UNIXEPOCH') AS \"Date de modification UTC\", DATETIME(FAVORITES.access_time, 'UNIXEPOCH') AS \"Date d'accès UTC\", PLACES.name as \"Nom\", PLACES.house as \"N°\", places.street as \"rue\", PLACES.city as \"Ville\", PLACES.state as \"Etat\", PLACES.country as \"Pays\", round(PLACES.latitude, 6)/1000000 as \"Latitude\", ROUND(PLACES.longitude, 6)/1000000 as \"Longitude\" FROM FAVORITES, PLACES WHERE FAVORITES.place_id = PLACES.id", "favorites.csv")
    ]

    for query, csv_filename in queries:
        result = outils.extract_and_save(
            query, csv_filename, "./db/user.db", 'Waze')

    if result:
        line_export = {
            'APPLICATION WAZE :': [
                'Les données de cette application ont été exportées en 3 fichiers : places.csv, recents.csv et favorites.csv\nCes fichiers sont placés dans le dossier "Waze"',
            ]
        }
    else:
        line_export = {
            'APPLICATION WAZE :': [
                'Il n\'y a pas de données retournées par les requêtes pour l\'application WAZE',
            ]
        }
    return line_export


def snapchat(zip_ref):
    """
    Searches the Zip Object for folder names starting with com.snap.file_manager_3_SCContent_, retrieves the associated uuid, retrieves the modification dates of each file this folder contains and returns a time-stamped history of Snapchat accounts that have been associated with the phone.

    Returns:
        dict: A dictionary containing a list with the information on the history of Snapchat accounts

    Example of output structure : 
    abced1ef-1234-5678-gftr-2fdt1541abc0 contient des fichiers horodatés du : 01-01-2023 à 00:18:44 au 11-01-2023 à 01:12:45
    """
    associated_snap_accounts = {}
    line_export_snapchat = {
        'SNAPCHAT :': []
    }
    # zip_ref.infolist() contient les informations sur l'ensemble des fichiers du zip
    for file_info in zip_ref.infolist():
        # Pour chaque fichier on récupère son chemin (le répertoire qui le contient)
        dirname = '/'.join(file_info.filename.split('/')[:-1])
        # Si on est dans un des répertoires snap
        if 'com.snap.file_manager_3_SCContent_' in dirname:
            # on récupère la date du fichier
            modification_date = datetime.datetime(*file_info.date_time, 0)
            # on récupère le nom du compte associé
            old_account = dirname.split('_')[-1]
            # si le compte avait déjà été trouvé (donc présent dans associated_snap_accounts)
            if old_account in associated_snap_accounts.keys():
                associated_snap_accounts[old_account].add(modification_date)
            # si le compte n'avait pas été trouvé, on l'ajoute
            else:
                associated_snap_accounts[old_account] = {modification_date}

    if len(associated_snap_accounts) > 0:
        for ancien_compte, horodatage in associated_snap_accounts.items():
            if os.path.exists('./db/primary.docobjects'):
                try:
                    connexion = sqlite3.connect("./db/primary.docobjects")
                    cursor = connexion.cursor()
                    cursor.execute(
                        "SELECT username FROM index_snapchatterusername as index_s INNER JOIN snapchatter as sn ON sn.rowid = index_s.rowid WHERE userId = ?", (ancien_compte,))
                    resultat = cursor.fetchone()
                    username = ' (' + str(resultat[0]) + ') '
                    connexion.close()
                except:
                    username = ' '
            else:
                username = ' '

            if len(horodatage) > 1:
                line_export_snapchat['SNAPCHAT :'].append(
                    ancien_compte + username + 'contient des fichiers horodatés du : ' + min(horodatage).strftime('%d-%m-%Y à %H:%M:%S') + ' au ' + max(horodatage).strftime('%d-%m-%Y à %H:%M:%S'))
            else:
                line_export_snapchat['SNAPCHAT :'].append(
                    ancien_compte + username + ' contient des fichiers horodatés du : ' + str(next(iter(horodatage))))
    else:
        line_export_snapchat['SNAPCHAT :'].append(
            'Pas d\'historique de comptes trouvés')
    return line_export_snapchat


def preferences():
    """
    Read the file com.apple.Preferences.plist and extract the phone's model.

    Returns:
        dict: A dictionary containing a list with the phone's model for the txt output if the 'SSdeviceType' key exists
    """
    with open('./db/com.apple.Preferences.plist', 'rb') as fp:
        plist_data = plistlib.load(fp)
        if 'SSDeviceType' in plist_data.keys():
            if 'hardwareModel' in plist_data['SSDeviceType'].keys():
                return {
                    'PREFERENCES.PLIST :': [
                        'Modèle : ' +
                        plist_data['SSDeviceType']['hardwareModel']
                    ]
                }


def data_ark():
    """
    Read the file data_ark.plist and extract the phone's name if in the plist

    Returns:
        dict: A dictionary containing a list with the phone's name for the txt output or an empty dictionary
    """
    with open('./db/data_ark.plist', 'rb') as fp:
        plist_data = plistlib.load(fp)
        if '-DeviceName' in plist_data.keys():
            line_export = {
                'DATA_ARK :': [
                    'Nom de l\'appareil :' + plist_data['-DeviceName']
                ]
            }
            return line_export
    return {}


def activation_record():
    """
    Read the file activation_record.plist, decode it and transform it in json for extract IMEI, serial, product, uuid Apple and iccid

    Returns:
        dict: A dictionary containing a list with the relevant information for the txt output.

    Example of output structure : 
    ---- ACTIVATION_RECORD.PLIST : ----
    IMEI 1 : 123456789
    IMEI 2 : 123456789
    Numéro de série : 123456789
    IMSI : 123456789
    Produit : iPhone12,1
    UUID Apple : 00008000-000123456789
    ICCID : 123456789
    """
    with open('./db/activation_record.plist', 'rb') as fp:
        plist_data = plistlib.load(fp)
        valeur = plist_data['AccountToken'].decode()
        valeur = valeur.replace("\n", '')
        valeur = valeur.replace("\t", '')
        valeur = valeur.replace(' = ', ':')
        valeur = valeur.replace(';', ',')
        valeur = valeur.replace(',}', '}')
        dictionnaire = json.loads(valeur)
    line_export = {'ACTIVATION_RECORD.PLIST :': []}
    if 'InternationalMobileEquipmentIdentity' in dictionnaire.keys():
        line_export['ACTIVATION_RECORD.PLIST :'].append(
            'IMEI 1 : ' + dictionnaire['InternationalMobileEquipmentIdentity'])
    if 'InternationalMobileEquipmentIdentity2' in dictionnaire.keys():
        line_export['ACTIVATION_RECORD.PLIST :'].append('IMEI 2 : ' +
                                                        dictionnaire['InternationalMobileEquipmentIdentity2'])
    if 'SerialNumber' in dictionnaire.keys():
        line_export['ACTIVATION_RECORD.PLIST :'].append(
            'Numéro de série : ' + dictionnaire['SerialNumber'])
    if 'InternationalMobileSubscriberIdentity' in dictionnaire.keys():
        line_export['ACTIVATION_RECORD.PLIST :'].append('IMSI : ' +
                                                        dictionnaire['InternationalMobileSubscriberIdentity'])
    if 'ProductType' in dictionnaire.keys():
        line_export['ACTIVATION_RECORD.PLIST :'].append(
            'Produit : ' + dictionnaire['ProductType'])
    if 'UniqueDeviceID' in dictionnaire.keys():
        line_export['ACTIVATION_RECORD.PLIST :'].append(
            'UUID Apple : ' + dictionnaire['UniqueDeviceID'])
    if 'IntegratedCircuitCardIdentity' in dictionnaire.keys():
        line_export['ACTIVATION_RECORD.PLIST :'].append(
            'ICCID : ' + dictionnaire['IntegratedCircuitCardIdentity'])
    return line_export


def photos():
    """
    Search the iOS version, use the queries in https://github.com/ScottKjr3347/iOS_Local_PL_Photos.sqlite_Queries in photos.sqlite database
    Create a csv with the results

    Returns:
        dict: A dictionary containing a list with the information on the created file.
    """
    print('Querie to photos.sqlite.')
    osv = ''
    with open('./db/data_ark.plist', 'rb') as fp:
        plist_data = plistlib.load(fp)
        if '-DarkProductVersion' in plist_data.keys():
            osv = plist_data['-DarkProductVersion'].split('.')[0]
    if osv == '':
        with open('./db/LastBuildInfo.plist', 'rb') as fp:
            plist_data = plistlib.load(fp)
            if 'FullVersionString' in plist_data.keys():
                osv = plist_data['FullVersionString'].split()[1].split('.')[0]
    if osv != '':
        # Accès au fichier de requêtes avec Pyinstaller
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        # Accès au fichier de requêtes normal
        else:
            base_path = os.path.abspath("ScottKjr3347/")

        file_path = os.path.join(base_path, f'{osv}.txt')
        with open(file_path) as req:
            query = req.read()

        try:
            result = outils.extract_and_save(query, 'photos_sqlite.csv',
                                             "./db/Photos.sqlite", "Photos SQLITE")
            if result:
                line_export = {
                    'PHOTOS.SQLITE :': [
                        'Un fichier Excel nommé "photos_sqlite.csv" a été généré depuis la base de données Photos.sqlite dans le dossier "Photos SQLITE".'
                    ]
                }
                print('photos_sqlite.csv created with success')
            else:
                line_export = {
                    'PHOTOS.SQLITE :': [
                        'Photos.sqlite est vide'
                    ]
                }
                print('Photos.sqlite est vide')
        except Exception:
            line_export = {
                'PHOTOS.SQLITE :': [
                    'le fichier "photos_sqlite.csv" n\'a pas pu être généré correctement.'
                ]
            }
    else:
        line_export = {
            'PHOTOS.SQLITE :': [
                'La fonction photo() n\'a pas réussi à récupérer la version d\'iOS et ne peut donc pas traiter la base de données photos.sqlite'
            ]
        }
    return line_export


def nbr_photos(zip_ref):
    """
    Calculates the number of photos in the phone's gallery (DCIM folder)

    Args:
        zip_ref : A ZipFile Object

    Returns:
        number : the number of photos
    """
    nbr_photos = 0
    for file_in_zip in zip_ref.namelist():
        if file_in_zip.startswith('/private/var/mobile/Media/DCIM/'):
            nbr_photos += 1
    return nbr_photos


def healthdb_secure():
    """
    Query the healthdb_secure.sqlite database for extract timezone and devices associated with iCloud Accounts
    Performs 2 queries and generates 2 csv for the answers to each query.

    Returns:
        dict: A dictionary containing a list with the information on the created files.
    """
    queries = [
        ('SELECT tz_name as "Fuseau", count(tz_name) as "Nb" from data_provenances group by tz_name ORDER by "Nb" DESC', "fuseaux_horaires.csv"),
        ('SELECT rowid, device_id, origin_product_type, source_id from data_provenances ORDER by device_id', "devices.csv"),
    ]

    result_query = []

    for query, csv_filename in queries:
        result_query.append(outils.extract_and_save(query, csv_filename,
                                                    "./db/healthdb_secure.sqlite", 'Healthdb_Secure'))

    messages = []
    if result_query[0]:
        messages.append(
            'La liste des fuseaux horaires synchronisés avec le compte icloud a été exportée dans le fichier fuseaux_horaires.csv')
    else:
        messages.append(
            'Aucun fuseaux horaires synchronisés avec le compte icloud n\'a été trouvé')
    if result_query[1]:
        messages.append(
            'La liste des appareils associés au compte iCloud de l\'utilisateur a été exportée dans le fichier devices.csv')
    else:
        messages.append(
            'Aucun appareils associés au compte icloud de l\'utilisateur n\'a été trouvé')

    line_export = {
        'DONNEES DE SANTE (HEALTHDB_SECURE) :': [
            messages[0],
            messages[1]
        ]
    }
    return line_export


def instagram():
    """
    Read the file com.burbn.instagram.plist and extract the last user who used the instagram application with the date.

    Returns:
        dict: A dictionary containing a list with the last user (with profile picture) and the last device log time and for the txt output.
    """
    with open('./db/com.burbn.instagram.plist', 'rb') as fp:
        line_export = {
            'APPLICATION INSTAGRAM : ': []}
        plist_data = plistlib.load(fp)
        date_str = outils.convert_to_mac_absolutetime(
            plist_data['last-device-log-time'])
        if 'last-device-log-time' in plist_data.keys():
            line_export['APPLICATION INSTAGRAM : '].append('Date de dernière connexion à l\'application : ' +
                                                           date_str + ' UTC')
        if 'last-logged-in-account-dict' in plist_data.keys():
            if 'username' in plist_data['last-logged-in-account-dict'] and 'profilePictureURLString' in plist_data['last-logged-in-account-dict']:
                line_export['APPLICATION INSTAGRAM : '].append('Dernier utilisateur qui s\'est connecté : ' +
                                                               plist_data['last-logged-in-account-dict']['username'] + ' (' + plist_data['last-logged-in-account-dict']['profilePictureURLString'] + ')')
    return line_export


def sms():
    """
    Query the sms.db database for extract SMS
    Generates 1 csv with the messages
    Use the APOLLO Script : https://github.com/mac4n6/APOLLO/blob/master/modules/sms_chat.txt

    Returns:
        dict: A dictionary containing a list with the information on the created files.
    """
    query = """
    SELECT
		CASE
			WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
			WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
			ELSE "N/A"
    		END "MESSAGE DATE",			
		CASE 
			WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
			WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
			ELSE "N/A"
		END "DATE DELIVERED",
		CASE 
			WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
			WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
			ELSE "N/A"
		END "DATE READ",
		MESSAGE.TEXT AS "MESSAGE",
		HANDLE.ID AS "CONTACT ID",
		MESSAGE.SERVICE AS "SERVICE",
		MESSAGE.ACCOUNT AS "ACCOUNT",
		MESSAGE.IS_DELIVERED AS "IS DELIVERED",
		MESSAGE.IS_FROM_ME AS "IS FROM ME",
		ATTACHMENT.FILENAME AS "FILENAME",
		ATTACHMENT.MIME_TYPE AS "MIME TYPE",
		ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
		ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
	FROM MESSAGE
	LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
	LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
	LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
    """
    result = outils.extract_and_save(query, 'sms.csv',
                                     "./db/sms.db", 'SMS')

    if result:
        line_export = {
            'SMS :': [
                'Les SMS ont été exportés dans le dossier SMS (fichier sms.csv)',
            ]
        }
    else:
        line_export = {
            'SMS :': [
                'Aucun sms n\'a été trouvé dans la base de données sms.db',
            ]
        }

    return line_export


def safari():
    """
    Query the history.db database for extract history internet navigation
    Generates 1 csv
    Use the APOLLO Script : https://github.com/mac4n6/APOLLO/blob/master/modules/safari_history.txt

    Returns:
        dict: A dictionary containing a list with the information on the created files.
    """
    query = """ 
    SELECT
    DATETIME(HISTORY_VISITS.VISIT_TIME+978307200,'UNIXEPOCH') AS "VISIT TIME",
    HISTORY_ITEMS.URL AS "URL",
    HISTORY_ITEMS.VISIT_COUNT AS "VISIT COUNT",
    HISTORY_VISITS.TITLE AS "TITLE",
    CASE HISTORY_VISITS.ORIGIN
        WHEN 1 THEN "ICLOUD SYNCED DEVICE"
        WHEN 0 THEN "VISITED FROM THIS DEVICE"
        ELSE HISTORY_VISITS.ORIGIN
    END "ICLOUD SYNC",
    HISTORY_VISITS.LOAD_SUCCESSFUL AS "LOAD SUCCESSFUL",
    HISTORY_VISITS.id AS "VISIT ID",
    HISTORY_VISITS.REDIRECT_SOURCE AS "REDIRECT SOURCE",
    HISTORY_VISITS.REDIRECT_DESTINATION AS "REDIRECT DESTINATION",
    HISTORY_VISITS.ID AS "HISTORY ITEM ID"
    FROM HISTORY_ITEMS
    LEFT OUTER JOIN HISTORY_VISITS ON HISTORY_ITEMS.ID == HISTORY_VISITS.HISTORY_ITEM
    """

    result = outils.extract_and_save(query, 'internet_history.csv',
                                     "./db/History.db", 'SAFARI')

    if result:
        line_export = {
            'SAFARI :': [
                'L\'historique internet du navigateur SAFARI a été exporté dans le dossier SAFARI (fichier internet_history.csv)',
            ]
        }
    else:
        line_export = {
            'SAFARI :': [
                'Aucun historique internet n\'a été trouvé dans la base de données History.db',
            ]
        }
    return line_export


def notes():
    """
    Query the notes.db database for extract apple notes
    Generates 1 csv

    Returns:
        dict: A dictionary containing a list with the information on the created files.
    """
    query = """ 
    SELECT
    ZNOTE.Z_PK,
    DATETIME(ZNOTE.ZCREATIONDATE+978307200,'UNIXEPOCH','LOCALTIME') AS "CREATION DATE",
    DATETIME(ZNOTE.ZMODIFICATIONDATE+978307200,'UNIXEPOCH','LOCALTIME') AS "MODIFICATION DATE",
    ZNOTE.ZDELETEDFLAG,
    ZNOTE.ZSUMMARY,
    ZNOTE.ZTITLE,
    ZNOTE.ZAUTHOR,
    ZNOTE.ZGUID,
    ZACCOUNT.ZNAME AS "ACCOUNT NAME",
    ZNOTEBODY.ZCONTENT,
    ZNOTEATTACHMENT.ZCONTENTID,
    ZNOTEATTACHMENT.ZFILENAME
    FROM ZNOTE
    LEFT JOIN ZSTORE ON ZNOTE.ZSTORE == ZSTORE.Z_PK
    LEFT JOIN ZACCOUNT ON ZSTORE.ZACCOUNT == ZACCOUNT.Z_PK
    LEFT JOIN ZNOTEBODY ON ZNOTE.ZBODY == ZNOTEBODY.Z_PK
    LEFT JOIN ZNOTEATTACHMENT ON ZNOTE.Z_PK == ZNOTEATTACHMENT.ZNOTE
    ORDER BY "CREATION DATE"
    """

    result = outils.extract_and_save(query, 'notes.csv',
                                     "./db/notes.sqlite", 'NOTES')

    if result:
        line_export = {
            'NOTES :': [
                'Le contenu de la base de données "notes.db" été exporté dans le dossier NOTES (fichier notes.csv)',
            ]
        }
    else:
        line_export = {
            'NOTES :': [
                'Aucune note n\'a été trouvée dans la base de données notes.sqlite',
            ]
        }
    return line_export
