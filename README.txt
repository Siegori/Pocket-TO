This is a simple website, a docker image shuold be created with no trouble as long as you install
what's in requirements.txt and use the CMD to do
py manage runserver
Afterwards, all you need to do is create an admin and some users to use the web page
as it requires login access

One thing to note is that the Users object that are run in tournaments are not Users
that can log in and vice versa, the app is meant to be managed by a single person to do book keeping
so we only need a handful of accounts that can access it and the "players" generated do not need access
rights.
