import sqlite3
import csv
import os
import datetime
import shutil


def write_file(lines_dict):
    """
    Each application function returns a dictionary containing a list. Each element of the list is a line to be written to the output file. This function will read all these lines and create a file named "furious.txt" which will be the report on the execution of this program.

    Args:
        lines_dict : dictionary containing a list where each element is a line for the txt file

    Returns:
        None

    Create a txt file named "furious.txt".
    """
    erreur = 0
    try:
        with open('furious.txt', 'a', encoding="utf-8") as txt:
            for dico in lines_dict:
                if dico != None:
                    categorie = list(dico.keys())[0]
                    txt.write(f'---- {categorie} ----\n')
                    value = dico[categorie]

                    # On vérifie si la valeur est une liste ou une liste de listes (CellularUsage)
                    if isinstance(value, list):
                        if all(isinstance(sublist, list) for sublist in value):
                            # S'il s'agit d'une liste de listes, on l'applatit avant d'écrire dans le fichier
                            flattened_value = [
                                item for sublist in value for item in sublist]
                            for line in flattened_value:
                                txt.write(line + '\n')
                        else:
                            # S'il s'agit d'une liste normale, on écrit ses éléments dans le fichier
                            for line in value:
                                txt.write(line + '\n')
                    else:
                        # S'il ne s'agit pas d'une liste, il suffit de l'écrire dans le fichier
                        txt.write(str(value) + '\n')

                    txt.write('\n')
    except Exception:
        erreur += 1
    if erreur == 0:
        print('A file named "furious.txt" has been created, which contains information about the Full File System.')
    else:
        print('An error occurred while creating the file "furious.txt".')


def format_mac(mac_bytes):
    """
    Format a binary MAC ADDRESS

    Args: 
        mac_bytes : a binary MAC ADDRESS

    Return:
        formatted_mac (str), the MAC ADDRESS formated and transformed to string
    """
    formatted_mac = ':'.join('%02X' % b for b in mac_bytes)
    return formatted_mac


def extract_and_save(query, csv_filename, database, output_folder):
    """
    Execute a query in a database, create a csv file and save it in a specific folder

    Args: 
        query (str) : the query to execute
        csv_filename (str) : the name of the csv file to create
        database (str) : the path of the sqlite database
        output_folder (str) : the path to the folder where the csv file is to be extracted

    Return:
        None

    Create a folder and csv files
    """
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    column_names = [col[0] for col in cursor.description]
    conn.close()

    if len(data) > 1:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        csv_path = os.path.join(output_folder, csv_filename)
        with open(csv_path, "w", newline="", encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(column_names)
            csv_writer.writerows(data)
        return True
    else:
        return False


def move_to_root(dir_target, file_to_move):
    """
    Function that returns the extracted files to the root of /db

    Args: 
        dir_target (str) : /db
        file_to_move (str) : the file to move (/db/private/var/mobile/file.db for example)

    Returns:
        None
    """
    extracted_file_path = os.path.join(
        dir_target, file_to_move.lstrip('/'))
    new_extracted_file_path = os.path.join(
        dir_target, os.path.basename(file_to_move))
    os.rename(extracted_file_path, new_extracted_file_path)


def move_to_dir(dir, dir_path, file_to_move):
    """
    Function that returns the extracted files to the root of /dcim

    Args: 
        dir (str) : /dcim
        dir_path (str) : /100APPLE for example
        file_to_move (str) : the file to move (/dcim/private/var/mobile/Media/DCIM/IMG_001.JPG for example)

    Returns:
        None
    """
    extracted_file_path = os.path.join(
        dir, file_to_move.lstrip('/'))
    new_extracted_file_path = dir_path + '/' + os.path.basename(file_to_move)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    try:
        os.rename(extracted_file_path, new_extracted_file_path)
    except FileExistsError:
        print(
            f'Erreur lors du déplacement du fichier, ce fichier existe déjà dans {new_extracted_file_path}')
    except Exception as e:
        print(
            f'Erreur lors du déplacement du fichier : {e}')


def move_to_thumb(dir_thumb, dir_path, file_to_move):
    """
    Function that returns the extracted files to the root of /thumbs

    Args: 
        dir_thumb (str) : /thumbs
        dir_path (str) : /100APPLE/IMG_001.JPG for example
        file_to_move (str) : the file to move (/thumb/private/var/mobile/Media/PhotoData/Thumbnails/V2/DCIM/100APPLE/IMG_001.JPG/5005.JPG for example)

    Returns:
        None
    """
    extracted_file_path = os.path.join(
        dir_thumb, file_to_move.lstrip('/'))
    new_dir = dir_thumb + \
        dir_path.split('/')[-3] + '/' + dir_path.split('/')[-2]
    new_extracted_file_path = new_dir + '/' + os.path.basename(file_to_move)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir, exist_ok=True)
    os.rename(extracted_file_path, new_extracted_file_path)


def convert_to_mac_absolutetime(timestamp):
    """
    Convert a timestamp in MAC ABSOLUTE TIME IN UTC

    Args :
        timestamp (str) : a timestamp to convert

    Returns : 
        datestring (str) : a datetime Object transformed to string
    """
    mac_absolute_time = timestamp + 978307200
    dt = datetime.datetime(1970, 1, 1) + \
        datetime.timedelta(seconds=mac_absolute_time)
    return dt.strftime("%d/%m/%Y à %H:%M:%S")


def remove_directory(directory, subdirectory):
    subdirectory_path = os.path.join(directory, subdirectory)
    if os.path.exists(subdirectory_path):
        shutil.rmtree(subdirectory_path)


def remove_private_and_filesystems(directory):
    remove_directory(directory, 'private')
    remove_directory(directory, 'filesystem1')
    remove_directory(directory, 'filesystem2')
