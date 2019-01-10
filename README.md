# Keypirinha Plugin: EasySearch

This is EasySearch, a plugin for the
[Keypirinha](http://keypirinha.com) launcher.

This package provides a short way to search the internet, just like WebSearch package but simpler.

![EasySearch usage](./images/2019-01-08_00-34-29.gif "EasySearch usage")


## Download

Download the plugin file from [here](https://github.com/bantya/Keypirinha-EasySearch/releases).


## Install

Once the `EasySearch.keypirinha-package` file is installed,
move it to the `InstalledPackage` folder located at:

* `Keypirinha\portable\Profile\InstalledPackages` in **Portable mode**
* **Or** `%APPDATA%\Keypirinha\InstalledPackages` in **Installed mode** (the
  final path would look like
  `C:\Users\%USERNAME%\AppData\Roaming\Keypirinha\InstalledPackages`)


## Usage
1. Open the EasySearch config file.

![Keypirinha configuration](./images/2019-01-09_22-04-13.jpg "Keypirinha configuration")

2. Add the desired web search URLs.
* The syntax for the URL entry should be:
    ```
    [distinct keyword] = [Search Engine name] [Search Engine URL with %s as a search term]

    e.g.

    g = Google https://www.google.com/search?q={q}
    php = PHP.net http://php.net/manual-lookup.php?pattern={q}
    gh = Github https://github.com/search?utf8=%E2%9C%93&q={q}
    ```
* All the fields in the above syntax are REQUIRED.

![EasySearch config file](./images/2019-01-09_22-06-10.jpg "EasySearch config file")

3. Invoke Keypirinha and put the search engine keyword and the search term.
* The syntax for the usage should be:
    ```
    [keyword] [Search term (can contain spaces)]

    e.g.

    g  keypirinha launcher  -> searches 'keypirinha launcher' on google
    gh  bantya/Keypirinha-EasySearch  -> searches 'bantya/Keypirinha-EasySearch' on github
    ```
![Keypirinha invoke](./images/2019-01-09_22-02-09.jpg "Keypirinha invoke")


## Quirks
As the suggestions are presented according to the **fuzzy search**, please keep in mind that the search-keyword MUST NOT be unrecognizably different than the search engine name.

i.e. Setting a keyword `xyz` for `Github` won't work, (Obviously!) but `gh` may work.


## Change Log

### v1.1.0
* `private_mode` and `new_window` settings added.
* Multiword name now works. Has to be separated by an underscore ( _ ).
* Single space now works for all the cases.
* Some refactoring.

### v1.0.0
* Updated README and added screenshots.
* Bumped the version to 1.0.0

### v0.0.3
* Removed debug and comments.

### v0.0.2
* Included the ability to reload the configuration after any changes in EasySearch config file.

### v0.0.1
* Initial commit.


## License

This package is distributed under the terms of the MIT license.


## Credits

_Waiting for the first name_.


## Contribute

This is how to contribute:
1. Check for open issues or open a fresh issue to start a discussion around a
   feature idea or a bug.
2. Fork this repository on GitHub to start making your changes to the **dev**
   branch.
3. Send a pull request.
4. Add yourself to the *Contributors* section below (or create it if needed)!
