# pyramid-sanity

Sensible defaults to catch bad behavior

Features
--------

* This plugin provides a way to catch a number of encoding errors which happen
 which are otherwise difficult to handle in the Pyramid framework
* It provides checking for a number of encoding issues with URLs, forms and 
query parameters
* In each case a specific exception is raised so you can handle it how you would
like to

By default, all errors we cannot correct will be returned as a subtype of 
`BadRequest` causing 400 errors.

Usage
-----

```python
config.add_settings({
    "pyramid_sanity.ascii_safe_redirects": False
    # See below for all available settings
})  
config.include("pyramid_sanity")
```

Settings
--------


| Pyramid setting | Default | Effect |
|-----------------|--------|---------|
| `pyramid_sanity.disable_all` | `False` | Disable all features, so they can be selectively enabled
| `pyramid_sanity.check_form` | `True` | Check for encoding errors in POST form fields
| `pyramid_sanity.check_params` | `True` | Check for encoding errors in URL parameters
| `pyramid_sanity.check_path` | `True` | Check for encoding errors in the URL path
| `pyramid_sanity.ascii_safe_redirects` | `True` | Ensure redirects do not include raw unicode characters

Exceptions
----------

In most cases we simply check for error conditions that would occur before your
code runs. If we encounter them we raise distinct errors to allow you to handle
them however you'd like.

By default all errors are a child of `pyramid.httpexceptions. HTTPBadRequest`
and should result in a 400 error page.

All exceptions are defined in `pyramid_sanity.exceptions`:

| Exception            | Raised for                      |
|----------------------|---------------------------------|
| `InvalidQueryString` | Problems with URL parameters    |
| `InvalidFormData`    | Problems with POST'ed form data |
| `InvalidURL`         | Problems with the URL itself    |

Hacking
-------

### Installing pyramid-sanity in a development environment

#### You will need

* [Git](https://git-scm.com/)

* [pyenv](https://github.com/pyenv/pyenv)
  Follow the instructions in the pyenv README to install it.
  The Homebrew method works best on macOS.
  On Ubuntu follow the Basic GitHub Checkout method.

#### Clone the git repo

```terminal
git clone https://github.com/hypothesis/pyramid-sanity.git
```

This will download the code into a `pyramid-sanity` directory
in your current working directory. You need to be in the
`pyramid-sanity` directory for the rest of the installation
process:

```terminal
cd pyramid-sanity
```

#### Run the tests

```terminal
make test
```

**That's it!** You’ve finished setting up your pyramid-sanity
development environment. Run `make help` to see all the commands that're
available for linting, code formatting, packaging, etc.

### Updating the Cookiecutter scaffolding

This project was created from the
https://github.com/hypothesis/h-cookiecutter-pypackage/ template.
If h-cookiecutter-pypackage itself has changed since this project was created, and
you want to update this project with the latest changes, you can "replay" the
cookiecutter over this project. Run:

```terminal
make template
```

**This will change the files in your working tree**, applying the latest
updates from the h-cookiecutter-pypackage template. Inspect and test the
changes, do any fixups that are needed, and then commit them to git and send a
pull request.

If you want `make template` to skip certain files, never changing them, add
these files to `"options.disable_replay"` in
[`.cookiecutter.json`](.cookiecutter.json) and commit that to git.

If you want `make template` to update a file that's listed in `disable_replay`
simply delete that file and then run `make template`, it'll recreate the file
for you.
