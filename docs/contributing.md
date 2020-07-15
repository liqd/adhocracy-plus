# Contributing to adhocracy+

We're happy that you are reading this document! We can make a bigger impact together!

## Found a bug?
-   If it is a security concern, please describe it in an email to info [at] liqd [dot] net.
-   Search through our [issues](https://github.com/liqd/adhocracy-plus/issues), if the bug was already reported. If you find it and have clarifications or anything more to add, please do so in a comment.
-   If it's a new issue, please add it to the [issues](https://github.com/liqd/adhocracy-plus/issues) with as much information as you can possibly provide. There is an issue template, which should help you with that.

## Want a feature?
Are you missing a feature or have a great idea? Please add and/or discuss it on [adhocracy.plus](https://adhocracy.plus/feedback/projects/deine-ideen-fur-a/).

## Fixed a bug?
Open a [pull request on github](https://github.com/liqd/adhocracy-plus/pulls). Make sure to include the issue number and a good explanation.

## Want to implement a new feature?
If you want to implement something you found on the [list](https://adhocracy.plus/feedback/projects/deine-ideen-fur-a/) or already implemented a feature in your fork that seems to work great, please get in touch with us! info [at] liqd [dot] net

## Want to contribute, but don't know where to start?
-   Find an issue you want to fix on [issues](https://github.com/liqd/adhocracy-plus/issues).
-   Fork adhocracy-plus and install it locally. A guide to forking can be found [here](https://guides.github.com/activities/forking/).
-   Fix the bug and open a a [pull request on github](https://github.com/liqd/adhocracy-plus/pulls). Make sure to include the issue number and a good explanation.

## Want to develop features in your own version of adhocracy+?
-   Fork adhocracy-plus and install it locally. A guide to forking can be found [here](https://guides.github.com/activities/forking/).
-   Commit your changes, languages, whatever to your own fork. Be careful about migrations when you want to keep your fork up to date with the upstream. (See below for more info.)
-   If you want to get the changes from adhocracy+ into your fork, you need to rebase onto the original repo (called upstream).
    -   cd into you cloned repo and add adhocracy+ as upstream:
        `git remote add upstream git://github.com/liqd/adhocracy-plus.git`
    -   Fetch the changes from upstream:
        `git fetch upstream`
    -   And rebase: `git rebase upstream/master` or `git rebase upstream/release` or whatever branch of upstream you would like to update to.
    -   If you run into conflicts, you may have to run `git rebase --skip` or `git reset --hard upstream/master` to get a clean branch
    -   A longer explanation can be found [here](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/working-with-forks). Even though, contrary to what we said above, this says to merge instead of rebase. A nice discussion about the pros and cons can be found [here](https://strongbox.github.io/developer-guide/git/rebase-vs-merge.html).

### Migrations
-   Migrations are Django's way to tell the database what the data model looks like and what the iterations of the data model are.
-   The migrations for every app (found in apps/app_name/migrations) are run in the specific order they are given in and depend on the ones before them.
-   If there are changes to the same model in two different branches, the migrations will be conflicting and can't be rebased, but have to be redone.
-   So, every model in every app that needs to be kept updated with the current version of adhocracy+ shouldn't be changed. Otherwise rebasing will get much harder.
-   If there are help tests or names to be changed, it might be a better idea to chenge them in the form.
-   If there are things to be changed in a module, it might be good to add your own app with a new module.

## Anything missing?
-   If you have questions or other ideas, get in touch: info [at] liqd [dot] net
