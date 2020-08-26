# pyramid-sanity

A Pyramid extension that fixes crashes caused by certain badly formed requests,
turning them into 400 Bad Request responses instead.
Also prevents apps from returning HTTP redirects with badly encoded locations
that can crash WSGI servers.

<details>
<summary>Example Pyramid app that reproduces the crashes below</summary>

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

</details>

Crashes that `pyramid-sanity` fixes:

<details>
<summary>A request with a badly encoded query parameter can crash an app when the app tries to access <code>request.GET</code>.</summary>

With the example Pyramid app above, this will raise an uncaught
`UnicodeDecodeError` from WebOb:

```terminal
curl 'http://localhost:6543/foo?q=%FC'
```

`pyramid-sanity` catches this and turns it into a 400 Bad Request response.

Related issues:

* https://github.com/Pylons/pyramid/issues/3399
* https://github.com/Pylons/webob/issues/161

</details>

<details>
<summary>A request with a badly encoded path can crash an app.</summary>

With the example app above this will raise an uncaught
`pyramid.exceptions.URLDecodeError`:

```terminal
curl 'http://localhost:6543/%FC'
```

`pyramid-sanity` catches this and turns it into a 400 Bad Request response.

The 500 Server Error here is actually deliberate behavior from Pyramid:
Pyramid raises [`URLDecodeError`](https://docs.pylonsproject.org/projects/pyramid/en/latest/api/exceptions.html#pyramid.exceptions.URLDecodeError)
and does not have a built-in exception view for `URLDecodeError`. Apps can
change this to a 400 Bad Request by registering a custom exception view for
`URLDecodeError`. See <https://github.com/Pylons/pyramid/issues/312#issuecomment-2322368>.

Related issues:

* https://github.com/Pylons/pyramid/issues/434
* https://github.com/Pylons/pyramid/issues/1374
* https://github.com/Pylons/pyramid/issues/2047
* https://github.com/Pylons/webob/issues/114
* https://github.com/hypothesis/h/issues/4915
* https://github.com/hypothesis/h/pull/4916

</details>

<details>
<summary>A bad form submission can crash an app when the app tries to access <code>request.POST</code>.</summary>

With the example app above this will raise an uncaught `ValueError` from WebOb:

```terminal
curl --request POST --url http://localhost:6543/foo --header 'content-type: multipart/form-data'
```

`pyramid-sanity` catches this and turns it into a 400 Bad Request response.

Related issues:

* https://github.com/Pylons/pyramid/issues/1258

</details>

<details>
<summary>If an app returns a redirect with a badly encoded location it can crash the WSGI server.</summary>

With the example app above this will raise an uncaught `AttributeError` from `wsgiref.simple_server`:

```terminal
curl http://localhost:6543/redirect
```

`pyramid-sanity` intercepts this and safely encodes the redirect location.

</details>

Usage
-----

```python
with Configurator() as config:
    # Add this as near to the end of your config as possible:
    config.include("pyramid_sanity")
```

Settings
--------

By default all fixes are enabled. You can disable them individually with settings:

```python
with Configurator() as config:
    config.add_settings({
        # Don't check for badly declared forms.
        "pyramid_sanity.check_form": False,

        # Don't check for badly encoded query params.
        "pyramid_sanity.check_params": False,

        # Don't check for badly encoded URL paths.
        "pyramid_sanity.check_path": False,

        # Don't safely encode redirect locations.
        "pyramid_sanity.ascii_safe_redirects": False
    })
    config.include("pyramid_sanity")
```

You can set `pyramid_sanity.disable_all` to `True` to disable all of the fixes,
then enable only certain fixes one by one:

```python
with Configurator() as config:
    config.add_settings({
        # Disable all fixes.
        "pyramid_sanity.disable_all": True,

        # Enable only the badly encoded query params fix.
        "pyramid_sanity.check_params": True,
    })
    config.include("pyramid_sanity")
```

Exceptions
----------

`pyramid-sanity` triggers 400 Bad Request responses by returning
`pyramid.httpexceptions.HTTPBadRequest` subclasses.

All exceptions returned by `pyramid-sanity` are subclasses of
`pyramid_sanity.exceptions.SanityException` (which is a subclass of
`HTTPBadRequest`) and different exception subclasses are returned for different
problems, so you can register
[custom exception views](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html#custom-exception-views)
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
raise non-ASCII redirects. For example this tween might cause a WSGI server
(like Gunicorn) that's serving your app to crash with `UnicodeEncodeError`:

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

Attribution
-----------

`pyramid-sanity` was initially based on the solution used by
[Warehouse's `sanity.py`](https://github.com/pypa/warehouse/blob/master/warehouse/sanity.py),
but wraps the fixes up in a Pyramid extension that's easy to add to apps.

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
