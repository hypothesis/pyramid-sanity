<a href="https://github.com/hypothesis/pyramid-sanity/actions/workflows/ci.yml?query=branch%3Amain"><img src="https://img.shields.io/github/workflow/status/hypothesis/pyramid-sanity/CI/main"></a>
<a href="https://pypi.org/project/pyramid-sanity"><img src="https://img.shields.io/pypi/v/pyramid-sanity"></a>
<a><img src="https://img.shields.io/badge/python-3.9 | 3.8-success"></a>
<a href="https://github.com/hypothesis/pyramid-sanity/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-BSD--2--Clause-success"></a>
<a href="https://github.com/hypothesis/cookiecutters/tree/main/pypackage"><img src="https://img.shields.io/badge/cookiecutter-pypackage-success"></a>
<a href="https://black.readthedocs.io/en/stable/"><img src="https://img.shields.io/badge/code%20style-black-000000"></a>

# pyramid-sanity

Sensible defaults to catch bad behavior.

`pyramid-sanity` is a Pyramid extension that catches certain crashes caused by
badly formed requests, turning them into `400: Bad Request` responses instead.

It also prevents apps from returning HTTP redirects with badly encoded locations
that can crash WSGI servers.

The aim is to have sensible defaults to make it easier to write a reliable Pyramid app.

For details of all the errors and fixes, and how to reproduce them see: [Error details](#error-details).

Usage
-----

```python
with Configurator() as config:
    config.add_settings({
        # See the section below for all settings...        
        "pyramid_sanity.check_form": False,
    })
    
    # Add this as near to the end of your config as possible:
    config.include("pyramid_sanity")
```

By default all fixes are enabled. You can disable them individually with settings:

```python
config.add_settings({
    # Don't check for badly declared forms.
    "pyramid_sanity.check_form": False
})
```

You can set `pyramid_sanity.disable_all` to `True` to disable all of the fixes,
then enable only certain fixes one by one:

```python
config.add_settings({
    # Disable all fixes.
    "pyramid_sanity.disable_all": True,

    # Enable only the badly encoded query params fix.
    "pyramid_sanity.check_params": True
})
```

Options
-------

| Option | Default | Effect |
|--------|---------|--------|
| `pyramid_sanity.disable_all` | `False` | Disable all checks by default
| `pyramid_sanity.check_form` | `True` | Check for badly declared forms
| `pyramid_sanity.check_params` | `True` | Check for badly encoded query params
| `pyramid_sanity.check_path` | `True` | Check for badly encoded URL paths
| `pyramid_sanity.ascii_safe_redirects` | `True` | Safely encode redirect locations

Exceptions
----------

All exceptions returned by `pyramid-sanity` are subclasses of
`pyramid_sanity.exceptions.SanityException`, which is a subclass of
`pyramid.httpexceptions.HTTPBadRequest`.

This means all `pyramid-sanity` exceptions trigger `400: Bad Request` responses.

Different exception subclasses are returned for different problems, so you can
register [custom exception views](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html#custom-exception-views)
to handle them if you want:

| Exception                                      | Returned for                    |
|------------------------------------------------|---------------------------------|
| `pyramid_sanity.exceptions.InvalidQueryString` | Badly encoded query params      |
| `pyramid_sanity.exceptions.InvalidFormData`    | Bad form posts                  |
| `pyramid_sanity.exceptions.InvalidURL`         | Badly encoded URL paths         |

Tween ordering
--------------

`pyramid-sanity` uses a number of Pyramid [tweens](https://docs.pylonsproject.org/projects/pyramid/en/latest/glossary.html#term-tween)
to do its work. It's important that your app's tween chain has:

 * Our tweens that check for errors in the request, first
 * Our tweens that check for errors in the output of your app, last

The easiest way to achieve this is to include `config.include("pyramid_sanity")`
**as late as possible** in your config. This uses Pyramid's
["best effort" implicit tween ordering](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#suggesting-implicit-tween-ordering)
to add the tweens and should work as long as your app doesn't add any
more tweens, or include any extensions that add tweens, afterwards.

You can to check the order of tweens in your app with Pyramid's
[`ptweens` command](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/commandline.html#displaying-tweens).
As long as there are no tweens which access `request.GET` or `request.POST`
above the input checking tweens, or generate redirects below output checking
tweens, you should be fine.

You can force the order with Pyramid's
[explicit tween ordering](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#explicit-tween-ordering)
if you need to.

### Tweens that raise non-ASCII redirects

`pyramid-sanity` protects against non-ASCII redirects raised by your app's
views by safely encoding them, but it can't protect against _other tweens_ that
_raise_ non-ASCII redirects.

For example this tween might cause a WSGI server (like Gunicorn) that's serving
your app to crash with `UnicodeEncodeError`:

```python
def non_ascii_redirecting_tween_factory(handler, registry):
    def non_ascii_redirecting_tween(request):
        from pyramid.httpexceptions import HTTPFound
        raise HTTPFound(location="http://example.com/€/☃")
    return non_ascii_redirecting_tween
```

You'll just have to make sure that your app doesn't have any tweens that do this!
Tweens should encode any redirect locations that they generate,
[like this](https://github.com/hypothesis/pyramid-sanity/blob/d8492620225ec6be0ba28b3eb49d329ef1e11dc2/src/pyramid_sanity/_egress.py#L22-L30).

Error details
-------------

If you would like to reproduce the errors an [example app](#addendum-example-application) is given at the end
of this section. All of the presented `curl` commands work with this app.

### Badly encoded query parameters makes `request.GET` crash

```terminal
curl 'http://localhost:6543/foo?q=%FC'
```

**By default**

WebOb raises `UnicodeDecodeError`. As there is no built-in exception view for
this exception the app crashes.

**With `pyramid-sanity`**

A `pyramid_sanity.exceptions.InvalidQueryString` is returned which results in a
`400: Bad Request` response.

Related issues:

* https://github.com/Pylons/pyramid/issues/3399
* https://github.com/Pylons/webob/issues/161

### A badly encoded path can cause a crash

```terminal
curl 'http://localhost:6543/%FC'
```

**By default**

Pyramid raises [`pyramid.exceptions.URLDecodeError`](https://docs.pylonsproject.org/projects/pyramid/en/latest/api/exceptions.html#pyramid.exceptions.URLDecodeError).
As there is no built-in exception view for this exception the app crashes.

**With `pyramid-sanity`**

A `pyramid_sanity.exceptions.InvalidURL` is returned which results in a
`400: Bad Request` response.

**Related issues**

* https://github.com/Pylons/pyramid/issues/434
* https://github.com/Pylons/pyramid/issues/1374
* https://github.com/Pylons/pyramid/issues/2047
* https://github.com/Pylons/webob/issues/114

### Bad or missing multipart boundary declarations make `request.POST` crash

```terminal
curl --request POST --url http://localhost:6543/foo --header 'content-type: multipart/form-data'
```

**By default**

WebOb raises an uncaught `ValueError`. As there is no built-in exception view
for this exception the app crashes.

**With `pyramid-sanity`**

A `pyramid_sanity.exceptions.InvalidFormData` is returned which results in a
`400: Bad Request` response.

Related issues:

* https://github.com/Pylons/pyramid/issues/1258

### Issuing redirects containing a non-ASCII location crashes the WSGI server

```terminal
curl http://localhost:6543/redirect
```

**By default**

The app will emit the redirect successfully, but the WSGI server running the app
may crash. With the example app below `wsgiref.simple_server` raises an
uncaught `AttributeError`.

**With `pyramid-sanity`**

The redirect is safely URL encoded.

#### Addendum: Example application

```python
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound


def redirect(request):
    # Return a redirect to a URL with a non-ASCII character in it.
    return HTTPFound(location="http://example.com/☃")


def hello_world(request):
    return Response(f"Hello World! Query string was: {request.GET}. Form body was: {request.POST}")


if __name__ == "__main__":
    with Configurator() as config:
        config.add_route("redirect", "/redirect")
        config.add_route("hello", "/{anything}")
        config.add_view(hello_world, route_name="hello")
        config.add_view(redirect, route_name="redirect")
        app = config.make_wsgi_app()

    server = make_server("0.0.0.0", 6543, app)
    server.serve_forever()
```

## Setting up Your pyramid-sanity Development Environment

First you'll need to install:

* [Git](https://git-scm.com/).
  On Ubuntu: `sudo apt install git`, on macOS: `brew install git`.
* [GNU Make](https://www.gnu.org/software/make/).
  This is probably already installed, run `make --version` to check.
* [pyenv](https://github.com/pyenv/pyenv).
  Follow the instructions in pyenv's README to install it.
  The **Homebrew** method works best on macOS.
  The **Basic GitHub Checkout** method works best on Ubuntu.
  You _don't_ need to set up pyenv's shell integration ("shims"), you can
  [use pyenv without shims](https://github.com/pyenv/pyenv#using-pyenv-without-shims).

Then to set up your development environment:

```terminal
git clone https://github.com/hypothesis/pyramid-sanity.git
cd pyramid-sanity
make help
```

## Releasing a New Version of the Project

1. First, to get PyPI publishing working you need to go to:
   <https://github.com/organizations/hypothesis/settings/secrets/actions/PYPI_TOKEN>
   and add pyramid-sanity to the `PYPI_TOKEN` secret's selected
   repositories.

2. Now that the pyramid-sanity project has access to the `PYPI_TOKEN` secret
   you can release a new version by just [creating a new GitHub release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
   Publishing a new GitHub release will automatically trigger
   [a GitHub Actions workflow](.github/workflows/pypi.yml)
   that will build the new version of your Python package and upload it to
   <https://pypi.org/project/pyramid-sanity>.

## Changing the Project's Python Versions

To change what versions of Python the project uses:

1. Change the Python versions in the
   [cookiecutter.json](.cookiecutter/cookiecutter.json) file. For example:

   ```json
   "python_versions": "3.10.4, 3.9.12",
   ```

2. Re-run the cookiecutter template:

   ```terminal
   make template
   ```

3. Commit everything to git and send a pull request

## Changing the Project's Python Dependencies

To change the production dependencies in the `setup.cfg` file:

1. Change the dependencies in the [`.cookiecutter/includes/setuptools/install_requires`](.cookiecutter/includes/setuptools/install_requires) file.
   If this file doesn't exist yet create it and add some dependencies to it.
   For example:

   ```
   pyramid
   sqlalchemy
   celery
   ```

2. Re-run the cookiecutter template:

   ```terminal
   make template
   ```

3. Commit everything to git and send a pull request

To change the project's formatting, linting and test dependencies:

1. Change the dependencies in the [`.cookiecutter/includes/tox/deps`](.cookiecutter/includes/tox/deps) file.
   If this file doesn't exist yet create it and add some dependencies to it.
   Use tox's [factor-conditional settings](https://tox.wiki/en/latest/config.html#factors-and-factor-conditional-settings)
   to limit which environment(s) each dependency is used in.
   For example:

   ```
   lint: flake8,
   format: autopep8,
   lint,tests: pytest-faker,
   ```

2. Re-run the cookiecutter template:

   ```terminal
   make template
   ```

3. Commit everything to git and send a pull request
