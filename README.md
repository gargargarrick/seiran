# Seiran

![Seiran](icon.svg)

Seiran (/'seIran/, lit. blue-indigo) is a simple bookmarks manager. It's free software and cross-platform, built with Python and SQLite.

Seiran stores *your* bookmarks on *your* machine, where they belong. It's ideal if you

+ are tired of slowing down your browser with huge bookmark files
+ have bookmarks you don't trust others with
+ reject proprietary, black-box "cloud" services on principle
+ want to back up your bookmarks regularly, in a format that will work with any browser, just in case
+ use multiple different browsers or browser profiles
+ want to be able to edit your bookmarks with familiar SQL tools instead of a slow in-browser PHP interface
+ prefer terminals over GUI

Or all of the above!

Seiran does not connect to the Internet at any time. It does not download icons or validate your bookmarks. It does not automatically synchronize with anything. It doesn't even have an "open in browser" command. It may not be *that* useful, and it's certainly nothing fancy, but it does exactly what I want and need a bookmark manager to do.

At present Seiran is text-only. I've considered making a GUI interface for it, but the command line one works fine for now.

## Dependencies

+ Python >= 3.4
+ appdirs

That's all!

## How to run

Install Seiran (`python setup.py install`) and it will be added to your Python `Scripts` folder, `/bin`, etc. depending on your platform. If you like, add its location to your system path so you can use Seiran anywhere just by typing "seiran [command]".

Available commands:

```
add [a bookmark]
del[ete a bookmark]
list [all bookmarks]
search [bookmarks]
edit [a bookmark]
import [bookmarks from various sources]
export [bookmarks to other formats]
clean [bookmarks]
copyright
help
```

## Adding new bookmarks

Use `add` to add a single new bookmark to the database. You'll be prompted for its title, URL, and optional "folder"/category. (The date of creation will be added automatically.)

Optional arguments:

`-t TITLE, --title TITLE`  
A bookmark's name. Usually appears in \<h1\> or \<title\> tags on the page.

`-u URL, --url URL`  
A bookmark's Universal Resource Locator. Must be unique.

`-c CATEGORY, --category CATEGORY`  
A bookmark's category. This is inspired by Firefox's folders, but you can put almost anything here.

## Deleting bookmarks

You can remove a bookmark with the `del` command. Please be careful as bookmarks cannot be recovered once they are deleted.

Optional arguments:

`-u URL, --url URL`  
The Universal Resource Locator of the bookmark you want to delete.

## Editing bookmarks

Use `edit` to modify an existing bookmark's title or category/tag. To avoid shenanigans, URLs cannot be edited in Seiran.

Optional arguments:

`-u URL, --url URL`  
The Universal Resource Locator of the bookmark you want to edit. Must be unique.

`-f FIELD, --field FIELD`  
The column you want to edit. Available arguments are `title` or `category`.

`-n NEW, --new NEW`  
The new value you want an edited field to have.

## Listing bookmarks

You can see a list of all bookmarks with `list`. This could take a while for very large databases.

## Finding bookmarks

`search` allows you to find a specific bookmark based on its title, URL, or category.

`-f FIELD, --field FIELD`  
The column you want to search. Available arguments are `title`, `url`, `category`, or `all`.

`-q QUERY, --query QUERY`  
The term you want to search for.

## Exporting bookmarks

With `export`, you can export your bookmarks to a nicely-formatted, timestamped file. Of course, you can easily get a plain CSV with a simple SQLite command, so Seiran tries to add a bit of value by making its output a bit prettier.

Available formats for exporting include HTML and TXT.

Optional arguments:

`-x EXPORTFORMAT, --exportformat EXPORTFORMAT`  
The format you want to export your bookmarks to. Available arguments are `txt` or `html`.

## Importing bookmarks

Although it's experimental, you can import a whole bunch of bookmarks at once with the `import` command. Make sure to back up your existing database before using, just in case.

When you use the `import` command, you'll first be prompted to make sure you *really* meant to do that -- it could take a long time and add quite a large number of bookmarks to your database (and may still have bugs as well). If you're OK with that, type `y` for yes. There is no command-line argument to speed this along, just to make sure no accidents happen.

Next, Seiran supports importation from existing Seiran databases, Firefox (and derivatives, like IceCat), the [OneTab](https://www.one-tab.com/) browser add-on. You'll be asked which one you want to import bookmarks from.

Optional arguments:

`-i IMPORTFORMAT, --importformat IMPORTFORMAT`  
The system you want to import bookmarks from. Available arguments are `firefox`, `onetab`, or `seiran`.

### Firefox et al.

You must tell Seiran where to find your browser profile. This varies enough that it can't be determined automatically.

#### PC browsers

In the browser that you want to import from, either select `Help > Troubleshooting information` from the main menu or simply navigate to `about:support`. Scroll down to "Profile Folder" and press the "Show Folder" button. The profile folder will open up in your file manager; copy its path and paste that into Seiran.

Seiran will ask if this is a mobile browser's profile; say no, and the importation process will begin.

#### Android browsers

If you have access to an Android browser's profile (because you copied it with an add-on like [Copy Profile](https://addons.mozilla.org/en-US/android/addon/copy-profile/) and ADB, or are somehow running Seiran itself on mobile through science or magic), just point Seiran to the directory that contains `browser.db` (not the file itself).

Seiran will ask if this is a mobile browser's profile; say yes, and the importation process will begin.

### OneTab

Save the contents of OneTab's "Export URLs" into a plain text (.txt) file. When prompted by Seiran, copy and paste the path to the export file. Then the importation process will begin.

Caveat: OneTab does not store dates in its export file, so those will not be preserved by Seiran. The date that you imported the bookmark will be used instead.

### Seiran

If you have another Seiran database and you want to combine it with your main one, this function will allow that. It is highly experimental and may ruin all the things. I am not responsible if you lose your bookmarks; make sure both databases are backed up before you attempt this.

Seiran will prompt you for the **full path** to the database you want to import. Provide it and the importation process will begin.

## Cleaning bookmarks

`seiran clean` will look for bookmarks in your database that don't seem to have titles, and add their respective URL as a title instead. It will then look for bookmarks that have identical titles (which suggests they might be duplicates) and tell you if it finds any.

## License

Copyright 2015-2019 Matthew Ellison.

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses> or write to:

>Free Software Foundation  
>51 Franklin Street, Fifth Floor  
>Boston, MA 02110-1335  
>USA
