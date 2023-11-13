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

### Installation

---

```
$ git clone https://github.com/chpe1/furious.git
$ cd ../path/to/the/file
$ pip install --upgrade -r requirements.txt
$ python ./main.py

or download the exe file on Windows and enjoy !!!
```
