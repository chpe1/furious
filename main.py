import zipfile
import os
import apple
import outils

print("""

███████╗██╗   ██╗██████╗ ██╗ ██████╗ ██╗   ██╗███████╗
██╔════╝██║   ██║██╔══██╗██║██╔═══██╗██║   ██║██╔════╝
█████╗  ██║   ██║██████╔╝██║██║   ██║██║   ██║███████╗
██╔══╝  ██║   ██║██╔══██╗██║██║   ██║██║   ██║╚════██║
██║     ╚██████╔╝██║  ██║██║╚██████╔╝╚██████╔╝███████║
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝  ╚═════╝ ╚══════╝
FORENSIC UTILITY FOR RAPID INFORMATION ON UNDECODED SYSTEMS
@created by JN for LION 59
@Licence MIT
version : 1.2.3
"""
      )


db_dir = "./db/"
dcim_dir = "./DCIM/"
thumb_dir = "./thumb/"
lines_dict = []
logs = []
message_log = ''

dict_unpath = {
    'Preferences/com.apple.commcenter.plist': apple.commcenter,
    'Preferences/com.apple.Preferences.plist': apple.preferences,
    'Databases/CellularUsage.db': apple.cellular_usage,
    'FrontBoard/applicationState.db': apple.application_state,
    'MobileInstallation/LastBuildInfo.plist': apple.lastbuildinfo,
    'Preferences/com.apple.aggregated.plist': apple.aggregated,
    'SystemConfiguration/NetworkInterfaces.plist': apple.networkinterface,
    'Accounts/Accounts3.sqlite': apple.accounts,
    'Notes/notes.sqlite': apple.notes,
    'Lockdown/data_ark.plist': apple.data_ark,
    'Health/healthdb_secure.sqlite': apple.healthdb_secure,
    'Passes/passes23.sqlite': None,
    'PhotoData/Photos.sqlite': apple.photos,
    'SMS/sms.db': apple.sms,
    'activation_records/activation_record.plist': apple.activation_record,
    'arroyo/arroyo.db': None,
    'cachecontroller/cache_controller.db': None,
    'DocObjects/primary.docobjects': None,
    'Documents/user.db': apple.waze,
    'Library/Preferences/com.burbn.instagram.plist': apple.instagram,
    '.obliterated': apple.obliterated,
    'Safari/History.db': apple.safari
}

# Crée le répertoire de sortie
os.makedirs(db_dir, exist_ok=True)


def extract_unknown_path_file(zip_ref, file_to_extract, function_to_execute, db_dir, lines_dict):
    """
    Extract a specified file from a ZIP archive when the path is unknown and optionally execute a provided function.

    Args:
        zip_ref (ZipFile): The zipfile from which to extract the file.
        file_to_extract (str): The name of the file to be extracted from the archive.
        function_to_execute (callable or None): A function to execute after extraction, or None if not needed.
        db_dir (str): The directory where the file will be extracted.
        lines_dict (list): A list to store lines to write in the output file "furious.txt."

    Returns:
        None

    This function checks if the specified file exists in the provided ZIP archive and extracts it to the specified directory. If the extraction is successful, it optionally executes a given function and appends lines returned by the function to the 'lines_dict' list.

    If any errors occur during file extraction or function execution, they are captured and printed as error messages."""
    # Comme on ne connait pas le chemin absolu du fichier qu'on veut extraire (à cause de l'uuid), on parcourt chaque fichier du zip.
    for file_in_zip in zip_ref.namelist():
        # On récupère juste le nom et on compare avec le nom du fichier
        if file_in_zip.endswith(f"/{file_to_extract}"):
            if file_to_extract != '.obliterated':
                # On regarde si le fichier n'est pas déjà extrait.
                extract_path = os.path.join(
                    db_dir, os.path.basename(file_to_extract))
                # S'il n'est pas déjà extrait
                if not os.path.exists(extract_path):
                    try:
                        # On extrait le fichier
                        zip_ref.extract(file_in_zip, path=db_dir)
                        message_log = f'File extraction "{
                            file_to_extract}" ... success'
                        print(message_log)
                        logs.append(message_log)
                        # Et on le rapatrie à la racine de '/db'
                        outils.move_to_root(db_dir, file_in_zip)
                    except WindowsError:
                        message_log = 'Impossible to move file to root, it already exists.'
                        print(message_log)
                        logs.append(message_log)
                    except Exception as e:
                        message_log = f'File extraction "{
                            file_to_extract}" ... error : {e}'
                        print(message_log)
                        logs.append(message_log)
                    # Si function_to_execute est différent de None, on execute la fonction adéquate
                    if function_to_execute:
                        try:
                            return_execution_func = function_to_execute()
                            lines_dict.append(return_execution_func)
                            message_log = f'{
                                function_to_execute} executed with success.'
                            if return_execution_func:
                                message_log += ' => Data'
                            else:
                                message_log += ' => No Data'
                            logs.append(message_log)
                        except Exception as e:
                            message_log = f'An error occurred when executing the function {
                                function_to_execute} : {e}'
                            print(message_log)
                            logs.append(message_log)
            else:
                # Gestion du .obliterated qu'on n'a pas besoin d'extraire
                lines_dict.append(function_to_execute(zip_ref, file_in_zip))
                logs.append(f'{function_to_execute} executed with success.')


def extract_gallery(zip_ref, dcim_dir):
    """
    Extract media from the gallery

    Args:
        zip_ref (ZipFile): The zipfile containing gallery files (Full File System)
        dcim_dir (str): The target directory for extracting files.

    Returns:
        list: A list of files in the gallery.

    This function iterates through the files in the ZIP archive, creates a list with only those located in the DCIM directory.
    It then offers to download these files and moves them to the target directory. The path of each extracted file is added to the 'liste_photos' list.
    """
    liste_photos = []
    message_log = 'Gallery content browsing...'
    print(message_log)
    logs.append(message_log)
    # On parcourt la liste des fichiers du zip et on ajoute à la liste uniquement les fichiers qui se trouvent dans le répertoire DCIM.
    for file_in_zip in zip_ref.namelist():
        if '/Media/DCIM/' in file_in_zip and not file_in_zip.endswith('/') and not file_in_zip.endswith('.bin'):
            liste_photos.append(file_in_zip)

    # S'il y a des photos, on propose de les télécharger.
    if len(liste_photos) > 0:
        download = input(
            f'There are {len(liste_photos)} medias in this phone\'s gallery. Would you like to download them? (Y, n): ')

        if download != 'n':
            print(
                "Gallery download...\nThis operation can last for a long time. \nPlease wait...")
            logs.append('Gallery download...')
            # On utilise la liste pour ne pas à avoir à reparcourir tous les fichiers du zip.
            for photo in liste_photos:
                parent = os.path.dirname(os.path.dirname(photo))
                original_file_path = photo.replace(
                    parent, '')
                destination_path = dcim_dir + original_file_path.split('/')[1]
                try:
                    zip_ref.extract(photo, path=dcim_dir)
                except FileExistsError:
                    message_log = f'Error extracting {
                        photo}: file already exists'
                    print(message_log)
                    logs.append(message_log)
                except Exception as e:
                    message_log = f'Error extracting {photo} : {e}'
                    print(message_log)
                    logs.append(message_log)
                # Et on le rapatrie à la racine de '/dcim'
                outils.move_to_dir(dcim_dir, destination_path, photo)
            message_log = 'Gallery download completed'
            print(message_log)
            logs.append(message_log)
    return liste_photos


def extract_thumbnails(zip_ref, liste_photos):
    """
    Extract the thumbnails corresponding to the media missing from the gallery

    Args:
        zip_ref (ZipFile): The zipfile containing gallery files (Full File System)
        liste_photos (list): List of all files in the DCIM directory

    Returns:
        None
    """
    print('Search thumbnails... Please wait')
    logs.append("Search thumbnails...")
    thumbnails = []
    medias_manquants = []

    for file_in_zip in zip_ref.namelist():
        # On cherche à récupérer la liste des dossiers IMG_001.JPG/
        if '/Media/PhotoData/Thumbnails/V2/DCIM/' in file_in_zip and file_in_zip.endswith('JPG'):
            thumbnails.append(os.path.dirname(file_in_zip))
            thumb_name = file_in_zip.split('/')[-1]

    for dossier in thumbnails:
        # donc on formate "dossier" pour ne récupérer que la partie avec DCIM :
        thumbnail = ''.join(dossier.split('/V2/')[1]).rstrip('/')
        # thumbnail a maintenant la forme : 'DCIM/100APPLE/IMG_001.MOV'
        if not any(thumbnail in photo for photo in liste_photos):
            medias_manquants.append(dossier)
    if len(medias_manquants) > 0:
        download = input(
            f'There are  {len(medias_manquants)} media thumbnails no longer in this phone\'s gallery but still present in the /private/var/mobile/Media/PhotoData/Thumbnails/V2/DCIM/ directory. Would you like to download them? (Y, n): ')
        logs.append(f'There are  {len(
            medias_manquants)} media thumbnails no longer in this phone\'s gallery but still present in the /private/var/mobile/Media/PhotoData/Thumbnails/V2/DCIM/ directory.')
    else:
        download = 'n'
        message_log = str(
            len(thumbnails)) + ' thumbnails detected ! Originals are all in the DCIM folder.'
        print(message_log)
        logs.append(message_log)

    if download != 'n':
        message_log = "Thumbnails download...\nThis operation can last for a long time. \nPlease wait..."
        print(message_log)
        logs.append(message_log)
        for media in medias_manquants:
            parent = os.path.dirname(os.path.dirname(media))
            original_file_path = media.replace(
                parent, '') + "/" + thumb_name
            destination_path = thumb_dir + original_file_path.lstrip('/')
            media = media + '/' + thumb_name
            zip_ref.extract(media, path=thumb_dir)
            # Et on le rapatrie à la racine de '/thumb'
            outils.move_to_thumb(thumb_dir, destination_path, media)


def extract_zip(my_zip):
    """
    Extract artefacts from the Full File System.

    Args:
        my_zip (ZipFile Object) : the path of the zip file

    Returns:
        None

    This function opens the zip archive and executes the functions extract_file_known_path, extract_unknown_path_file. It handles the specific cases of .obliterated and Snapchat account history whose artifacts don't need to be extracted. Finally, it executes the extract_gallery and extract_thumbnails functions.
    """
    print('Open the zipfile. Please wait...')
    try:
        with zipfile.ZipFile(my_zip, 'r') as zip_ref:

            # Extraction des fichiers
            for file_to_extract, function_to_execute in dict_unpath.items():
                extract_unknown_path_file(zip_ref, file_to_extract, function_to_execute,
                                          db_dir, lines_dict)

            lines_dict.append(apple.snapchat(zip_ref))

            # Extraction des fichiers de la galerie
            liste_photos = extract_gallery(zip_ref, dcim_dir)
            extract_thumbnails(zip_ref, liste_photos)
    except FileExistsError:
        message_log = 'Erreur lors de l\'extraction du fichier : le fichier existe déjà.'
        print(message_log)
        logs.append(message_log)
    except Exception as e:
        message_log = f'Erreur lors de l\'extraction du fichier : {e}'
        print(message_log)
        logs.append(message_log)


if __name__ == "__main__":
    my_zip = input(
        'Please specify the relative path to the ZIP file containing the Full File System : ')

    extract_zip(my_zip)

    # Suppression des répertoires inutiles (private...)
    directories = [db_dir, dcim_dir, thumb_dir]

    for directory in directories:
        outils.remove_private_and_filesystems(directory)

    # Ecriture du fichier standard
    outils.write_file(lines_dict)

    # Ecriture du fichier de logs
    with open('logs.txt', "w", encoding="utf-8") as log_file:
        log_file.writelines('\n'.join(logs))

    input("Program complete. Press [ENTER] to exit the program... ")
