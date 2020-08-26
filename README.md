# pyramid-sanity

Sensible defaults to catch bad behavior

Features
--------

* This plugin provides a way to catch a number of encoding errors which happen
 which are otherwise difficult to handle in the Pyramid framework
* Various crashes should now become `BadRequest` causing 400 errors:
   * Calling with bad unicode query parameters
   * Calling with bad unicode in the URL
   * Calling with poorly specified form boundaries
* In each case a specific exception is raised so you can handle it how you would
like to
* There is also one fix:
   * Pyramid emitting redirects with unicode in the URL

Usage
-----

```python
config.add_settings({
    "pyramid_sanity.ascii_safe_redirects": False
    # See below for all available settings
})

# Important! Add as near to the end of your config as possible:
config.include("pyramid_sanity")
```

Settings
--------

| Pyramid setting | Default | Effect |
|-----------------|--------|---------|
| `pyramid_sanity.disable_all` | `False` | Disable all features, so they can be selectively enabled
| `pyramid_sanity.check_form` | `True` | Check for badly declared forms
| `pyramid_sanity.check_params` | `True` | Check for encoding errors in URL parameters
| `pyramid_sanity.check_path` | `True` | Check for encoding errors in the URL path
| `pyramid_sanity.ascii_safe_redirects` | `True` | Ensure redirects do not include raw unicode characters

Exceptions
----------

In most cases we simply check for error conditions that would occur before your
code runs. If we encounter them we raise distinct errors to allow you to handle
them however you'd like.

By default all errors are a child of `pyramid.httpexceptions.HTTPBadRequest`
and should result in a `400 Bad Request` error page.

All exceptions are defined in `pyramid_sanity.exceptions`:

| Exception            | Raised for                      |
|----------------------|---------------------------------|
| `InvalidQueryString` | Problems with URL parameters    |
| `InvalidFormData`    | Problems with POST'ed form data |
| `InvalidURL`         | Problems with the URL itself    |

Tween ordering
--------------

`pyramid_sanity` uses a couple of Pyramid [tweens](https://docs.pylonsproject.org/projects/pyramid/en/latest/glossary.html#term-tween)
to do its work. It's important that your app's tween chain has:
 
 * `pyramid_sanity.IngressTweenFactory` first
 * `pyramid_sanity.EgressTweenFactory` last 

The easiest way to achieve this is to include `config.include("pyramid_sanity")`
**as late as possible** in your config. This uses Pyramid's
["best effort" implicit tween ordering](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#suggesting-implicit-tween-ordering)
to add the tweens and should work as long as your app doesn't add any 
more tweens, or include any extensions that add tweens, afterwards.

You can to check the order of tweens in your app with Pyramid's 
[`ptweens` command](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/commandline.html#displaying-tweens).
As long as there are no tweens which access `request.GET` or 
`request.POST` above `pyramid_sanity.IngressTweenFactory`, or generate 
redirects below `pyramid_sanity.EgressTweenFactory`, you should be fine.

You can force the order with Pyramid's
[explicit tween ordering](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#explicit-tween-ordering)
if you need to.

### Tweens that raise non-ASCII redirects

`pyramid_sanity` protects against non-ASCII redirects raised by your app's
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

The code that ended up here was all initially based on: 

 * https://github.com/pypa/warehouse/blob/master/warehouse/sanity.py
 
From the excellent PyPI [Warehouse](https://github.com/pypa/warehouse/blob/master/README.rst) project. 
 
The major modifications to this are around the ergonomics:

 * Different errors to allow fine grained handling if you want
 * Configurable checkers and fixers
 * Packaging as a separate package etc.

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
