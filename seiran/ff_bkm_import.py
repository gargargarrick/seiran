## Import bookmarks from Firefox and derivatives (Pale Moon, IceCat, etc.)
## This is not extremely well-tested. Use at your own risk!

import sqlite3, datetime, os
from collections import OrderedDict

def formList(bookmark_tup):
    title = bookmark_tup[0]
    url = bookmark_tup[1]
    date_raw = str(bookmark_tup[2])
    date_cut = date_raw[0:10]
    date = datetime.datetime.fromtimestamp(int(date_cut)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    return([title,url,date])

def importDatabase():
    ## Get the full path of your Firefox profile.
    firefox = input("Please enter the directory of the Firefox profile you wish to import. > ")
    
    ## For whatever reason, Android profiles are set up completely differently.
    mobile = input("Is this from a mobile version of Firefox? If you're unsure, it probably is not. (y/n) > ")
    if mobile.lower() == "y" or mobile.lower() == "y":
        mobile = True
        database = os.path.join(firefox,"browser.db")
    else:
        mobile = False
        database = os.path.join(firefox,"places.sqlite")

    try:
        conn = sqlite3.connect(database)
    except sqlite3.OperationalError:
        print("Couldn't find a profile database of that type in {location}. You may be looking in the wrong directory, or it may be a different platform's database.".format(location=firefox))
    cursor = conn.cursor()

    if mobile == False:
        sql = "select id,title from moz_bookmarks where type=2;"
        cursor.execute(sql)
        folders = cursor.fetchall()

        bookmarks = OrderedDict()

        ## Get folders first

        for id in folders:
            bookmarks[id[1]] = (cursor.execute(
                "select b.title, a.url, b.dateAdded from moz_places a, moz_bookmarks b where a.id=b.fk and b.parent='%s';"
                % (id[0])).fetchall())

        tup_list = []
        for i in bookmarks.items():
            tup_list.append(i)

        fmarks = []

        for i in tup_list:
            folderName = i[0]
            if folderName == "":
                folderName == "Blank"
            for item in i:
                if i[1]:
                    bms = i[1]
                    for bookmark in bms:
                        bookmark_list = formList(bookmark)
                        bookmark_list.append(folderName)
                        fmarks.append(bookmark_list)
                else:
                    pass

        ## Now the individual, non-foldered bookmarks.
        bookmarks = OrderedDict()

        sql = "select id,title from moz_bookmarks where type=1;"
        cursor.execute(sql)
        single_bookmarks = cursor.fetchall()

        tup_list = []
        single_bookmarks = single_bookmarks[0:20]

        for id in single_bookmarks:
            bookmarks[id[1]] = (cursor.execute(
                "select b.title, a.url, b.dateAdded from moz_places a, moz_bookmarks b where a.id=b.fk;").fetchall())

        for i in bookmarks.items():
            tup_list.append(i)

        tup_list = tup_list[0][1]

        for i in tup_list:
            bookmark_list = formList(i)
            bookmark_list.append("")
            fmarks.append(bookmark_list)
    else:
    
    ## The Android browsers don't have folders and the database is set up much more straightforwardly.

        fmarks = []
    
        sql = "select title,url,created from bookmarks;"
        
        bookmarks = (cursor.execute(sql).fetchall())
        
        for i in bookmarks:
            bookmark_list = formList(i)
            bookmark_list.append("")
            fmarks.append(bookmark_list)

    conn.close()

    return(fmarks)


