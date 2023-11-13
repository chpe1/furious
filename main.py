import zipfile
import os
import shutil
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
version : 1.0.0
"""
      )


db_dir = "./db/"
dcim_dir = "./DCIM/"
thumb_dir = "./thumb/"
my_zip = input(
    'Please specify the relative path to the ZIP file containing the Full File System : ')
lines_dict = []

dict_to_extract = {
    '/private/var/wireless/Library/Preferences/com.apple.commcenter.plist': apple.commcenter,
    '/private/var/mobile/Library/Preferences/com.apple.Preferences.plist': apple.preferences,
    '/private/var/wireless/Library/Databases/CellularUsage.db': apple.cellular_usage,
    '/private/var/mobile/Library/FrontBoard/applicationState.db': apple.application_state,
    '/private/var/installd/Library/MobileInstallation/LastBuildInfo.plist': apple.lastbuildinfo,
    '/private/var/mobile/Library/Preferences/com.apple.aggregated.plist': apple.aggregated,
    '/private/var/preferences/SystemConfiguration/NetworkInterfaces.plist': apple.networkinterface,
    '/private/var/mobile/Library/Accounts/Accounts3.sqlite': apple.accounts,
    '/private/var/mobile/Library/Notes/notes.sqlite': None,
    '/private/var/root/Library/Lockdown/data_ark.plist': apple.data_ark,
    '/private/var/mobile/Library/Health/healthdb_secure.sqlite': apple.healthdb_secure,
    '/private/var/mobile/Library/Passes/passes23.sqlite': None,
    '/private/var/mobile/Media/PhotoData/Photos.sqlite': apple.photos,
}

dict_unpath = {
    'activation_record.plist': apple.activation_record,
    'arroyo.db': None,
    'cache_controller.db': None,
    'primary.docobjects': None,
    'user.db': apple.waze,
    'com.burbn.instagram.plist': apple.instagram
}

# Crée le répertoire de sortie
os.makedirs(db_dir, exist_ok=True)


def extract_file_known_path(zip_ref, file_to_extract, function_to_execute, db_dir, lines_dict):
    """
    Extract a specified file from a ZIP archive when the path is known and optionally execute a provided function.

    Args:
        zip_ref (ZipFile): The zipfile from which to extract the file.
        file_to_extract (str): The path of the file to be extracted from the archive.
        function_to_execute (callable or None): A function to execute after extraction, or None if not needed.
        db_dir (str): The directory where the file will be extracted.
        lines_dict (list): A list to store lines to write in the output file "furious.txt."

    Returns:
        None

    This function checks if the specified file exists in the provided ZIP archive and extracts it to the specified directory. If the extraction is successful, it optionally executes a given function and appends lines returned by the function to the 'lines_dict' list.

    If any errors occur during file extraction or function execution, they are captured and printed as error messages.

    """
    # Vérification si le fichier à extraire existe dans l'archive
    # zip_ref.namelist() est une liste contenant le chemin absolu de tous les fichiers et répertoires
    if file_to_extract in zip_ref.namelist():
        # Si oui on extrait le fichier demandé
        try:
            zip_ref.extract(file_to_extract, path=db_dir)
            print(f'File extraction "{file_to_extract}" ... success')
            # On le rapatrie à la racine du répertoire "./db/"
            outils.move_to_root(db_dir, file_to_extract)
        except WindowsError:
            print('Impossible de déplacer le fichier à la racine, il existe déjà.')
        except Exception as e:
            print(f'File extraction "{file_to_extract}" ... error : {e}')
        # Si function_to_execute est différent de None, on execute la fonction adéquate
        if function_to_execute:
            try:
                lines_dict.append(function_to_execute())
            except Exception as e:
                print(f'An error occurred when executing the function {
                      function_to_execute} : {e}')


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
            try:
                # On extrait le fichier
                zip_ref.extract(file_in_zip, path=db_dir)
                print(f'File extraction "{file_to_extract}" ... success')
                # Et on le rapatrie à la racine de '/db'
                outils.move_to_root(db_dir, file_in_zip)
            except WindowsError:
                print('Impossible de déplacer le fichier à la racine, il existe déjà.')
            except Exception as e:
                print(f'File extraction "{file_to_extract}" ... error : {e}')
            # Si function_to_execute est différent de None, on execute la fonction adéquate
            if function_to_execute:
                try:
                    lines_dict.append(function_to_execute())
                except Exception as e:
                    print(f'An error occurred when executing the function {function_to_execute} : {e}')


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
    print('Gallery content browsing...')
    # On parcourt la liste des fichiers du zip et on ajoute à la liste uniquement les fichiers qui se trouvent dans le répertoire DCIM.
    for file_in_zip in zip_ref.namelist():
        if file_in_zip.startswith('/private/var/mobile/Media/DCIM/') and not file_in_zip.endswith('/') and not file_in_zip.endswith('.bin'):
            liste_photos.append(file_in_zip)

    # S'il y a des photos, on propose de les télécharger.
    if len(liste_photos) > 0:
        download = input(
            f'There are {len(liste_photos)} photos in this phone\'s gallery. Would you like to download them? (Y, n): ')

        if download != 'n':
            print(
                "Gallery download...\nThis operation can last for a long time. \nPlease wait...")
            # On utilise la liste pour ne pas à avoir à reparcourir tous les fichiers du zip.
            for photo in liste_photos:
                original_file_path = photo.replace(
                    '/private/var/mobile/Media/DCIM/', '')
                destination_path = os.path.join(
                    dcim_dir, original_file_path.split('/')[:-1][0])
                zip_ref.extract(photo, path=dcim_dir)
                # Et on le rapatrie à la racine de '/dcim'
                outils.move_to_dir(dcim_dir, destination_path, photo)
            print('Gallery download completed')
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
    thumbnails = []
    medias_manquants = []

    for file_in_zip in zip_ref.namelist():
        if file_in_zip.startswith('/private/var/mobile/Media/PhotoData/Thumbnails/V2/DCIM/') and file_in_zip.count('/') == 11 and not file_in_zip.endswith('5005.JPG'):
            thumbnails.append(file_in_zip)

    for dossier in thumbnails:
        # dossier a cette forme là : '/private/var/mobile/Media/PhotoData/Thumbnails/V2/DCIM/100APPLE/IMG_001.MOV/'
        # donc on le formate pour ne récupérer que la partie avec DCIM :
        thumbnail = ''.join(dossier.split('/V2/')[1]).rstrip('/')
        # thumbnail a maintenant la forme : 'DCIM/100APPLE/IMG_001.MOV'
        if '/private/var/mobile/Media/' + thumbnail not in liste_photos:
            medias_manquants.append(dossier)
    if len(medias_manquants) > 0:
        download = input(
            f'There are  {len(medias_manquants)} media thumbnails no longer in this phone\'s gallery but still present in the /private/var/mobile/Media/PhotoData/Thumbnails/V2/DCIM/ directory. Would you like to download them? (Y, n): ')
    else:
        download = 'n'
        print(str(len(thumbnails)) +
              ' thumbnails detected ! Originals are all in the DCIM folder.')

    if download != 'n':
        print(
            "Thumbnails download...\nThis operation can last for a long time. \nPlease wait...")
        for media in medias_manquants:
            destination_path = ''.join(media.split(
                '/')[-3]) + '/' + media.split('/')[-2] + '/'
            media = media + '5005.JPG'
            zip_ref.extract(media, path=thumb_dir)
            # Et on le rapatrie à la racine de '/thumb'
            outils.move_to_thumb(thumb_dir, '/' + destination_path, media)


def extract_zip():
    """
    Extract artefacts from the Full File System.

    Args:
        None

    Returns:
        None

    This function opens the zip archive and executes the functions extract_file_known_path, extract_unknown_path_file. It handles the specific cases of .obliterated and Snapchat account history whose artifacts don't need to be extracted. Finally, it executes the extract_gallery and extract_thumbnails functions.
    """
    print('Open the zipfile. Please wait...')
    with zipfile.ZipFile(my_zip, 'r') as zip_ref:
        # Extraction des fichiers de la liste list_to_extract
        for file_to_extract, function_to_execute in dict_to_extract.items():
            extract_file_known_path(zip_ref, file_to_extract,
                                    function_to_execute, db_dir, lines_dict)

        # Extraction des fichiers dont le chemin n'est pas connu (db d'applications)
        for file_to_extract, function_to_execute in dict_unpath.items():
            extract_unknown_path_file(zip_ref, file_to_extract, function_to_execute,
                                      db_dir, lines_dict)

        # Cas spécifiques
        lines_dict.append(apple.obliterated(zip_ref))
        lines_dict.append(apple.snapchat(zip_ref))

        # Extraction des fichiers de la galerie
        liste_photos = extract_gallery(zip_ref, dcim_dir)
        extract_thumbnails(zip_ref, liste_photos)


if __name__ == "__main__":
    extract_zip()

    # Suppression des répertoires inutiles (private...)
    directories = [db_dir, dcim_dir, thumb_dir]
    for directory in directories:
        directory_to_remove = os.path.join(directory, 'private')
        if os.path.exists(directory_to_remove):
            shutil.rmtree(directory_to_remove)

    # Ecriture du fichier standard
    outils.write_file(lines_dict)

    input("Program complete. Press [ENTER] to exit the program... ")
