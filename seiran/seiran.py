#!/usr/bin/python3
# -*- coding: utf-8 -*-

##    Seiran 1.0

##    Copyright 2015-2018 Matthew "garrick" Ellison.

##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.

##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.

##    You should have received a copy of the GNU General Public License
##    along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Seiran -- a local bookmarks manager."""

name = "seiran"
author = "gargargarrick"
__version__ = '1.0'

import datetime, os, sys
import sqlite3
from appdirs import *
import seiran.ff_bkm_import
import seiran.onetab_bkm_import

##There's probably a better way to do this, but first we must see if the
##bookmarks database exists already or not.
def initBookmarks():
    print("Trying database...")
    try:
        c.execute('''CREATE TABLE bookmarks
            (title text,url text NOT NULL,date text,folder text,PRIMARY KEY(url))''')
        print("Database created.")
    except sqlite3.OperationalError:
        print("Database exists.")

def addBKM():
    title = input("Title? > ")
    url = input("URL? > ")

    ##I don't want to connect to the net to validate bookmarks (that's what browsers
    ##are for) so this only looking the first few characters and does absolutely
    ##no other checking or processing.
    ##Checking is done to make opening bookmarks in the browser a bit easier;
    ## feel free to take that part out if you don't want or need this feature.
    ##I would recommend leaving in checking for empty URLs, though.

    while url == "" or url[0:4] != "http":
        print("Sorry, that is empty or doesn't seem to be a URL. (Make sure your URL uses the HTTP or HTTPS protocol.)")
        url = input("URL? > ")
    ##add the current date
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    folder = input("Folder/Category? (can be left blank) > ")
    bkm = (title,url,date,folder)
    ##Frankly, I don't know how necessary SQL injection countermeasures are for
    ##this specific program (what, are you going to inject your OWN database?)
    ##but it always pays to be careful in my opinion.
    try:
        c.execute("INSERT INTO bookmarks VALUES (?,?,?,?)",bkm)
        print("Inserted.")
        conn.commit()
    ##I don't want users to end up with databases full of duplicated bookmarks
    ##by mistake, so URLs must be unique.
    except sqlite3.IntegrityError:
        print("Already exists.")
    except sqlite3.OperationalError:
        print("Operational error")

def delBKM():
    url = input("URL to delete? (Deleted bookmarks cannot be recovered!) > ")
    url = (url,)
    try:
        c.execute("DELETE FROM bookmarks WHERE url=?",url)
        conn.commit()
        print("DELETED!")
    except:
        ##Yeah, I got nothing.
        print("Unable to delete for unknown reasons.")

## List all bookmarks in the database.
## You can normally do that by dumping a CSV, so I made it a bit fancy.
def listBKMs():
    c.execute("SELECT * from bookmarks")
    template = "\nTitle: {title}\n  URL: {url}\n  Date: {date}\n  Folder: {folder}"
    for i in c.fetchall():
        print(template.format(title=i[0],url=i[1],date=i[2],folder=i[3]))

## Search just one column.
def oneSearch(search_term,column):
    search_term = "%"+search_term+"%"
    t = (search_term,)
    if column == "title":
        c.execute("SELECT * from bookmarks WHERE title LIKE ?",t)
    elif column == "url":
        c.execute("SELECT * from bookmarks WHERE url LIKE ?",t)
    elif column == "folder":
        c.execute("SELECT * from bookmarks WHERE folder LIKE ?",t)
    result_list = c.fetchall()
    if result_list == []:
        print("No results.")
    else:
        template = "\nTitle: {title}\n  URL: {url}\n  Date: {date}\n  Folder: {folder}"
        for i in result_list:
            print(template.format(title=i[0],url=i[1],date=i[2],folder=i[3]))

## Search titles and URLs in one go.
def searchAll(search_term):
    search_term = "%"+search_term+"%"
    t = (search_term,)
    results = []
    c.execute("SELECT * from bookmarks WHERE title LIKE ?",t)
    result_list = c.fetchall()
    for i in result_list:
        results.append(i)
    c.execute("SELECT * from bookmarks WHERE url LIKE ?",t)
    result_list = c.fetchall()
    for i in result_list:
        if i not in results:
            results.append(i)
    c.execute("SELECT * from bookmarks WHERE folder LIKE ?",t)
    result_list = c.fetchall()
    for i in result_list:
        if i not in results:
            results.append(i)
    if results == []:
        print("No results.")
    else:
        template = "\nTitle: {title}\n  URL: {url}\n  Date: {date}\n  Folder: {folder}"
        for i in results:
            print(template.format(title=i[0],url=i[1],date=i[2],folder=i[3]))

## Edit a bookmark.
def editBKM():
    url = input("Which URL do you want to edit? > ")
    urlT = (url,)
    c.execute("SELECT * from bookmarks WHERE url = ?",urlT)
    ##error handling goes here
    you_found_it = False
    for row in c:
        print(row)
        you_found_it = True
    if you_found_it == False:
        print("Sorry, that doesn't seem to be a URL in the database. Try again.")
        return
    ## TODO: Let peoples leave without changing anything
    editField = input("Which field do you wish to edit? (title/category)> ")
    if editField.lower() == "title":
        new_title = input("What should the new title be? > ")
        new_title = str(new_title)
        newBKM = (new_title,url)
        c.execute("UPDATE bookmarks SET title=? WHERE url=?",newBKM)
        conn.commit()
    elif editField.lower() == "category":
        new_cat = input("What should the new category be? > ")
        new_cat = str(new_cat)
        newBKM = (new_cat,url)
        c.execute("UPDATE bookmarks SET folder=? WHERE url=?",newBKM)
        conn.commit()
    else:
        return

## Experimental Firefox (and derivatives) bookmark importer.
## May ruin EVERYTHING. Please back up your DB before use.
def getFirefoxBookmarks():
    ## Grab the Firefox bookmarks.
    fmarks = seiran.ff_bkm_import.importDatabase()
    ## Add them to Seiran's database.
    for i in fmarks:
        bkm = (i[0], i[1], str(i[2]), i[3])
        try:
            c.execute("INSERT INTO bookmarks VALUES (?,?,?,?)",bkm)
            conn.commit()
        except sqlite3.IntegrityError:
            print("Duplicate found. Ignoring {i}.".format(i=i[1]))
        except sqlite3.OperationalError:
            print("Operational error")
    print("Import complete!")
    return

def getOneTabBookmarks():
    ## Get bookmarks from OneTab importer.
    omarks = seiran.onetab_bkm_import.importFromTxt()
    for i in omarks:
        bkm = (i[0], i[1], str(i[2]), i[3])
        try:
            c.execute("INSERT INTO bookmarks VALUES (?,?,?,?)",bkm)
            conn.commit()
        except sqlite3.IntegrityError:
            print("Duplicate found. Ignoring {i}.".format(i=i[1]))
        except sqlite3.OperationalError:
            print("Operational error")
    print("Import complete!")
    return

def getSeiranBookmarks():
    ## Import bookmarks from an existing Seiran database.
    print("Warning! This is not well-tested and may ruin everything.")
    print("Back up your database before use!")
    seiran_file = input("Enter the path to the Seiran database you want to copy. > ")
    if seiran_file.lower() == "q":
        print("Import cancelled.")
        return
    sconn = sqlite3.connect(seiran_file)
    sc = sconn.cursor()
    attach_main = "ATTACH DATABASE ? as x"
    main_db_path = installToConfig()
    main_db = (main_db_path,)
    c.execute(attach_main,main_db)
    attach_branch = "ATTACH DATABASE ? as y"
    branch_db = (seiran_file,)
    c.execute(attach_branch,branch_db)
    c.execute("INSERT OR IGNORE INTO x.bookmarks SELECT * FROM y.bookmarks;")
    conn.commit()
    # except sqlite3.OperationalError:
    #     print("Operational error")
    print("Import complete!")
    return
    

def exportBookmarks(format):
    c.execute("SELECT * from bookmarks")
    if format == "txt":
        ## Using the same format as [list]
        template = "Title: {title}\n  URL: {url}\n  Date: {date}\n  Folder: {folder}\n"
    elif format == "html":
        template = "<p><a href={url}>{title}</a> ({folder}) [<time='{date}'>{date}</a>]</p>"
    bookmarks = []
    for i in c.fetchall():
        if i[0] == "":
            title=i[1]
        else:
            title = i[0]
        bookmarks.append(template.format(title=title,url=i[1],date=i[2],folder=i[3]))
    if format == "txt":
        bookmarks_write = "\n".join(bookmarks)
    elif format == "html":
        front_matter = ["<!DOCTYPE HTML>","<html>","<head>","<title>Seiran Bookmarks</title>","<meta charset='utf-8'/>","</head>","<body>","<h1>Seiran Bookmarks</h1>"]
        end_matter = ["</body>","</html>"]
        bookmarks_write = "\n".join(front_matter+bookmarks+end_matter)
    save_path = user_data_dir(name, author)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_name = "seiran_bookmarks_export_{date}.{format}".format(date=datetime.datetime.now().strftime("%Y-%m-%d"),format=format)
    bookmarks_out = os.path.join(save_path,file_name)
    with open(bookmarks_out,"w",encoding="utf-8") as f_out:
        f_out.write(bookmarks_write)
    print("Exported to {bookmarks_out}.".format(bookmarks_out=bookmarks_out))
    return

## Stick Seiran in the user's data directory,
## and get the path to the bookmarks database.
def installToConfig():
    config_path = user_data_dir(name, author)
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    bookmarks_file = os.path.join(config_path,"bookmarks.db")
    return(bookmarks_file)

def main():
    global c
    global conn
    bookmarks_file = installToConfig()
    conn = sqlite3.connect(bookmarks_file)
    c = conn.cursor()
    initBookmarks()

    ## Use with the command line or don't!
    if len(sys.argv) <= 1:
        choice = input("Action? (add, del, list, search, edit, import, export, copyright, help) > ")
    else:
        choice = sys.argv[1]

    if choice.lower() == "add":
        addBKM()
    elif choice.lower() == "del":
        delBKM()
    elif choice.lower() == "list":
        print("Listing all bookmarks...")
        listBKMs()
        return
    elif choice.lower() == "search":
        field = input("  Which field? (title/url/category/all) > ")
        search_term = input("  Search term? (case insensitive) > ")
        if field == "title":
            oneSearch(search_term,"title")
        elif field == "url":
            oneSearch(search_term,"url")
            return
        elif field == "category":
            oneSearch(search_term,"folder")
            return
        else:
            searchAll(search_term)
            return
    elif choice.lower() == "edit":
        editBKM()
    elif choice.lower() == "import":
        ic = input("Are you sure you want to import bookmarks? It might take a while. Back up your database first! (y/n) > ")
        if ic.lower() == "y" or ic.lower() == "yes":
            importer_c = input("Import from Firefox-type browser, OneTab export, or another Seiran database? (firefox/onetab/seiran) > ")
            if importer_c == "firefox":
                getFirefoxBookmarks()
                return
            elif importer_c == "onetab":
                getOneTabBookmarks()
                return
            elif importer_c == "seiran":
                getSeiranBookmarks()
                return
        else:
            print("OK, nothing will be copied.")
    elif choice.lower() == "export":
        ex_form = input("Which format? (html,txt) > ")
        if ex_form == "html":
            exportBookmarks("html")
            return
        if ex_form == "txt":
            exportBookmarks("txt")
            return
        else:
            print("Export cancelled.")
            return
    elif choice.lower() == "copyright":
        print("Copyright 2015-2018 Matthew 'garrick' Ellison. Released under the GNU GPL version 3.")
    elif choice.lower() == "help":
        print("Available arguments: add [a bookmark], del[ete a bookmark], list [all bookmarks], search [bookmarks], edit [a bookmark], import [bookmarks from other system], export [bookmarks to other formats], copyright, help")
    else:
        conn.close()

if __name__ == '__main__':
    main()
