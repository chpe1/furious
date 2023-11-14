# FURIOUS

FORENSIC UTILITY FOR RAPID INFORMATION ON UNDECODED SYSTEMS

## Table of Contents

1. [General Info](#general-info)
1. [Dependencies](#dependencies)
1. [Installation](#installation)

### General Info

---

This script takes as parameter a ZIP archive corresponding to an iPhone FULL FILE SYSTEM.
It opens the ZIP but extracts only files relevant to the survey. Some are system files, already known and present on all systems, others are application files. The script is particularly interested in plist files and SQLITE databases.
After extracting these files, the script executes a function to process the data.
At the end of its execution, it generates a text file summarizing all the elements found.
During execution, the program offers to download the media contained in the phone's gallery.
It compares all these files with the thumbnails in the PHOTODATA directory, enabling the retrieval of thumbnails of photos deleted from the gallery.

At a time when iPhones are getting bigger and bigger in terms of data, this script aims to start working on extraction data while commercial software is still decoding...

The files of interest are extracted so that you can check the information.

This script is bound to improve...
Thanks for your comeback report.

### Dependencies

---

This script uses https://github.com/ScottKjr3347/iOS_Local_PL_Photos.sqlite_Queries to work with the photos.sqlite database.
You need the biplist library to work with plist files

Ce projet open-source utilise le script APOLLO sous licence "BSD-like with acknowledgment clause." Vous trouverez ci-dessous la licence du script APOLLO :

LICENSE 1 ("BSD-like with acknowledgment)
Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restri
1. Redistributions of source code must retain the above copyright notice, disclaimer, and this list of conditions.
2. Redistributions in binary form must reproduce the above copyright notice, disclaimer, and this list of conditions in the documentation and/or other materials provided with the distribution.
3. All advertising, training, and documentation materials mentioning features or use of this software must display the following acknowledgment. Character-limited social media may abbreviate this acknowledgment to include author and APOLLO name ie: "This new feature brought to you by @iamevltwin's APOLLO". Please make an effort credit the appropriate authors on specific APOLLO modules. The spirit of this clause is to give public acknowledgment to researchers where credit is due.
This product includes software developed by Sarah Edwards (Station X Labs, LLC, @iamevltwin, mac4n6.com) and other contributors as part of APOLLO (Apple Pattern of Life Lazy 
Output'er). 
Le script APOLLO est développé par Sarah Edwards (Station X Labs, LLC, 
@iamevltwin, mac4n6.com). Nous reconnaissons et respectons les droits de l'auteur 
de ce script, conformément à la licence APOLLO. Merci à Sarah Edwards et aux 
autres contributeurs d'APOLLO pour leur travail précieux.

### Installation

---

```
$ git clone https://github.com/chpe1/furious.git
$ cd ../path/to/the/file
$ pip install --upgrade -r requirements.txt
$ python ./main.py

or download the exe file on Windows and enjoy !!!
```
