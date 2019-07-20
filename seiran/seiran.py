#!/usr/bin/python3
# -*- coding: utf-8 -*-

##    Seiran 1.3.0

##    Copyright 2015-2019 Matthew "garrick" Ellison.

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
__author__ = "gargargarrick"
__version__ = '1.3.0'
__copyright__ = "Copyright 2015-2019 Matthew Ellison"
__license__ = "GPL"
__maintainer__ = "gargargarrick"
__status__ = "Development"

import datetime, os, sys, argparse
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

def addBKM(title,url,folder):
    if title == None:
        title = input("Title? > ")
    if url == None:
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
    if folder == None:
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
    if url == None:
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
## The spaces at the ends of lines are so that it parses as Markdown too.
def listBKMs():
    c.execute("SELECT * from bookmarks")
    template = "\nTitle: {title}  \n  URL: {url}  \n  Date: {date}  \n  Folder: {folder}"
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

## Search titles URLs, and categories in one go.
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
        template = "\nTitle: {title}  \n  URL: {url}  \n  Date: {date}  \n  Folder: {folder}"
        for i in results:
            print(template.format(title=i[0],url=i[1],date=i[2],folder=i[3]))

## Edit a bookmark.
def editBKM(url,field,new):
    if url == None:
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
    if field == None:
        field = input("Which field do you wish to edit? (title/category/none)> ")
    if field not in ["title", "category"]:
        return
    if new == None:
        new = input("What should the new {field} be? > ".format(field=field))
        new = str(new)
    newBKM = (new,url)
    if field == "title":
        c.execute("UPDATE bookmarks SET title=? WHERE url=?",newBKM)
        conn.commit()
    elif field == "category":
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
        template = "Title: {title}  \n  URL: {url}  \n  Date: {date}  \n  Folder: {folder}\n"
    elif format == "html":
        template = "<p><a href={url}>{title}</a> ({folder}) [<time='{date}'>{date}</a>]</p>"
    bookmarks = []
    for i in c.fetchall():
        if i[0] == "" or i[0] == None or i[0] == "None":
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

def cleanBKMs():
    c.execute("SELECT * from bookmarks")
    for i in c.fetchall():
        # This functiom checks for empty and duplicate titles.
        if i[0] == "" or i[0] == None or i[0] == "None":
            print("Bookmark {url} doesn't have a title. Adding URL as title.".format(url=i[1]))
            new_title = i[1]
            newBKM = (new_title,i[1])
            c.execute("UPDATE bookmarks SET title=? WHERE url=?",newBKM)
            conn.commit()
    c.execute("SELECT title, COUNT(*) c FROM bookmarks GROUP BY title HAVING c > 1;")
    result_list = c.fetchall()
    if result_list == []:
        print("No results.")
    else:
        template = """\n{count} bookmarks have the title "{title}":"""
        for i in result_list:
            print(template.format(title=i[0],count=i[1]))
            t = (i[0],)
            c.execute("SELECT url from bookmarks where title is ?",t)
            url_list = c.fetchall()
            for u in url_list:
                print("  - {url}".format(url=u[0]))
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
    print("{name} by {author}, v.{version}.".format(name=name,author=__author__,version=__version__))
    
    parser = argparse.ArgumentParser(prog='seiran')
    subparsers = parser.add_subparsers(dest="command", help='Commands')
    parser_help = subparsers.add_parser("help", help="List commands")
    parser_add = subparsers.add_parser("add", help="Create a new bookmark.")
    parser_del = subparsers.add_parser("del", help="Remove a bookmark.")
    parser_list = subparsers.add_parser("list", help="Display all bookmarks in the database.")
    parser_search = subparsers.add_parser("search", help="Find specific bookmark(s).")
    parser_edit = subparsers.add_parser("edit", help="Change a bookmark's metadata.")
    parser_import = subparsers.add_parser("import", help="Add bookmarks from anothe system to the database.")
    parser_export = subparsers.add_parser("export", help="Save all bookmarks to a formatted file.")
    parser_clean = subparsers.add_parser("clean", help="Tidy up bookmark metadata.")
    parser_copyright = subparsers.add_parser("copyright", help="Show legal information.")
    
    parser_add.add_argument("-t", "--title", help="A bookmark's name. Usually appears in <h1> or <title> tags on the page.")
    parser_add.add_argument("-u", "--url", help="A bookmark's Universal Resource Locator. Must be unique.")
    parser_edit.add_argument("-u", "--url", help="A bookmark's Universal Resource Locator. Must be unique.")
    parser_del.add_argument("-u", "--url", help="The Universal Resource Locator of the bookmark you want to delete.")
    parser_add.add_argument("-c", "--category", help="A bookmark's category. This is inspired by Firefox's folders, but you can put almost anything here.")
    parser_search.add_argument("-f", "--field", help="The column you want to search. Available arguments are title, url, category, or all.")
    parser_edit.add_argument("-f", "--field", help="The column you want to edit. Available arguments are title or category.")
    parser_search.add_argument("-q", "--query", help="The term you want to search for.")
    parser_edit.add_argument("-n", "--new", help="The new value you want an edited field to have.")
    parser_import.add_argument("-i", "--importformat", help="The system you want to import bookmarks from. Available arguments are firefox, onetab, or seiran.")
    parser_export.add_argument("-x", "--exportformat", help="The format you want to export your bookmarks to. Available options are txt or html.")
    choice = parser.parse_args()

    if choice.command == "add":
        addBKM(choice.title, choice.url, choice.category)
    elif choice.command == "del":
        delBKM(choice.url)
    elif choice.command == "list":
        print("Listing all bookmarks...")
        listBKMs()
        return
    elif choice.command == "search":
        field = choice.field
        if field == None:
            field = input("  Which field? (title/url/category/all) > ")
        search_term = choice.query
        if search_term == None:
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
    elif choice.command == "edit":
        editBKM(choice.url,choice.field,choice.new)
    elif choice.command == "import":
        ## This has a big enough possibility to mess things up that I'm not adding an
        ## argument to do it automatically. You must accept manually to avoid accidents.
        ic = input("Are you sure you want to import bookmarks? It might take a while. Back up your database first! (y/n) > ")
        if ic.lower() == "y" or ic.lower() == "yes":
            importer_c = choice.importformat
            if importer_c == None:
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
    elif choice.command == "export":
        ex_form = choice.exportformat
        if ex_form == None:
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
    elif choice.command == "clean":
        cleanBKMs()
        return
    elif choice.command == "copyright":
        print("Copyright 2015-2019 Matthew 'gargargarrick' Ellison. Released under the GNU GPL version 3. See LICENSE for full details.")
    elif choice.command == "help":
        print("Available arguments: add [a bookmark], del[ete a bookmark], list [all bookmarks], search [bookmarks], edit [a bookmark], import [bookmarks from other system], export [bookmarks to other formats], clean [bookmark metadata], copyright, help")
    else:
        conn.close()

if __name__ == '__main__':
    main()
