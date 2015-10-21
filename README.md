Review Board Package Installer
==============================

rbpkg is the official command line installer for Review Board and related
projects. It's used to download and install packages, manage upgrades, and tie
your system to a particular range of versions.


Features
--------

* Installs and upgrades Review Board, RBTools, or related packages.

* Keeps packages at a pinned version range, allowing smooth upgrades within a
  major x.y version range without accidentally upgrading beyond that.

* Ability to download all dependencies to a folder without installing, so that
  they can be consumed by an in-house build system.

* Makes it easy to switch to and from beta channels.

* Verifies builds, ensuring you're always getting what you expect to get.

* Auto-installs backported security fixes for older versions of Django
  that we support.


Installing rbpkg
----------------

Installation is simple. If you're running a new enough Review Board release,
you probably already have rbpkg. Otherwise, you can get it by running:

    $ pip install rbpkg

rbpkg will help keep itself up-to-date.


FAQ
---

### What does this support?

This supports Review Board 1.7.x onward, and RBTools 0.7.x onward.

It requires Python 2.6 or 2.7.


### Is this a new package manager?

Not really. Under the hood, rbpkg uses [pip](https://pip.pypa.io). The packages
that it installs are standard Python packages.

We don't maintain our own package database on your system, or anything like
that (though we do store some metadata to help upgrade to the right version of
Review Board).

rbpkg can be thought of as a very smart wrapper around pip. A wrapper that can
help ensure you're always running the version you want, with all the right
dependencies and the latest security fixes.


### Why not just use pip directly?

The Python world is consolidating around [PyPI](https://pypi.python.org/) and
pip, for many good reasons. pip is a great little installer for installing
Python modules and simple applications. PyPI is a great place to host these.

They're not perfect, though, and we've run into many limitations that make it
harder for us to handle releases and for our users to get going, largely
because we are not a simple application.

The primary problem we've run into is that PyPI/pip encourages -- and will soon
require -- modules to be uploaded to PyPI. Externally-hosted modules are
second-class citizens, and harder to work with and install. There are good
reasons for the Python world to want an official, verifiable place to keep most
modules, but it does not work for us for a number of reasons:

* We organize our releases so that it's easy for companies to download builds
  of any version through a web page. PyPI's interface is more geared toward
  showing the latest few versions of a package, and becomes a barrier for the
  users we work with.

* We need to be able to provide different stable, beta, nightly, etc. channels,
  as well as private builds for some customers. PyPI doesn't really allow for
  this if we host our packages there.

* We store other files alongside the builds, such as SHA checksum files and
  PGP signatures. While the new Python Wheel format has a concept of signing,
  eggs and tarballs do not. We'd lose out on this very useful information by
  storing our packages on PyPI.

* We track download stats across operating systems, countries, Python versions,
  installers, time of day, and more. PyPI doesn't allow for the type of stats
  we need.

* Since we have customers using versions of Review Board that depend on
  outdated versions of Django that are no longer officially maintained, we've
  opted to provide builds that contain backports of important security fixes.
  There's no way in the PyPI/pip ecosystem for us to depend on these builds
  and install them when upgrading Review Board.

Furthermore, customers all too frequently run into the problem where they want
to upgrade to the latest patch release for an older major.minor version
(say, 1.7.x), but end up getting the very latest stable release instead, since
they're just doing a `pip install -U` or `easy_install -U`. This can be very
disruptive. A more focused installer can be smart here and do the right thing.


### How safe is rbpkg compared to pip?

pip is very security-conscious. It ensures that, by default, all packages are
coming from PyPI over HTTPS and that any externally-hosted packages will only
be downloaded if you give a series of command line arguments. However, it
doesn't know anything about the contents of the packages.

rbpkg is even more security-conscious since it's a more focused installer:

* It works only with our official, maintained, and signed list of packages.
  This way you always know you're getting our stuff.

* It communicates exclusively over HTTPS.

* It verifies all downloaded builds against our checksums and signatures (if
  GnuPG is installed).

* No risk of typos resulting in downloading or installing the wrong package.

* If we ship security backports for an otherwise unmaintained module, you'll
  get them automatically instead of the stale upstream versions.


Getting Support
---------------

We can help you get going with rbpkg and Review Board, and diagnose any issues
that may come up. There are two levels of support: public community support,
and private premium support.

The public community support is available on our main
[discussion list](https://groups.google.com/group/reviewboard/). We generally
respond to requests within a couple of days. This support works well for
general, non-urgent questions that don't need to expose confidential
information.

We can also provide more
[dedicated, private support](https://www.beanbaginc.com/support/contracts/) for
your organization through a support contract. We offer same-day responses
(generally within a few hours, if not sooner), confidential communications,
installation/upgrade assistance, emergency database repair, phone/chat (by
appointment), priority fixes for urgent bugs, and backports of urgent fixes to
older releases (when possible).


Reporting Bugs
--------------

Hit a bug? Let us know by
[filing a bug report](https://www.reviewboard.org/bugs/new/).

You can also look through the
[existing bug reports](https://www.reviewboard.org/bugs/) to see if anyone else
has already filed the bug.


Contributing
------------

Are you a developer? Want to help improve rbpkg? Great! Let's help you get
started.

First off, read through our
[contributor guide](https://www.reviewboard.org/docs/codebase/dev/).

We accept patches to Review Board, rbpkg, and other related projects on
[reviews.reviewboard.org](https://reviews.reviewboard.org/). (Please note that
we do not accept pull requests.)

Got any questions about anything related to rbpkg and development? Head
on over to our
[development discussion list](https://groups.google.com/group/reviewboard-dev/).
