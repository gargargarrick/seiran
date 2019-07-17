## Import bookmarks from the OneTab addon.
## This is not extremely well-tested. Use at your own risk!

import sqlite3, datetime, os, sys

def importFromTxt():
    onetab_file = input("Enter the path to the .txt exported from OneTab. > ")
    with open(onetab_file,"r",encoding="utf-8") as f:
        onetab_raw = f.read().splitlines()
    onetab = []
    for entry in onetab_raw:
        if entry == "" or entry == "\n":
            pass
        else:
            entry_pieces = entry.split(" | ",1)
            if len(entry_pieces) > 1:
                title = entry_pieces[1]
                url = entry_pieces[0]
            else:
                title = entry_pieces[0]
                url = entry_pieces[0]
            date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            category = "OneTab"
            bookmark = (title,url,date,category)
            onetab.append(bookmark)
    return(onetab)

