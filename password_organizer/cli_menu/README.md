NOTE that this is basically a rip-off of the PyInquirer project.

My main concern with the project is that it's stuck with a very old version of prompt-toolkit that
is not compatible with things like ipython.

Upgrading to prompt-toolkit 3 is not easy (especially the async Application part) but I wanted to
try and spend a bit of time on it. Unfortunately, there does not seem to be a CI, and the few tests
that the PyInquirer have are working neither on my Mac, nor in a linux container. So I just
abandonned for now.
