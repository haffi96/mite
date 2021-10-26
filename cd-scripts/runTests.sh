#!/bin/sh -x

/home/jenkins/.local/bin/pre-commit run --origin HEAD --source origin/master
PRE_COMMIT_STATUS=$?

if [ $PRE_COMMIT_STATUS -ne 0 ]; then
    git diff
fi

# tox seems to be giving issues, so dropping it for now
# tox -e py39; TOX_EXIT_CODE=$?

# Further ideas for jobs to run:
# - license check
# - make sure test coverage increases
# And, once we're sure that the pipeline is working:
# - integration/performance tests
# Once we have docs:
# - documentation coverage
# - docs build (on master only)

# when we start using tox again, uncomment the line below
# [ "$TOX_EXIT_CODE" -eq 0 -a "$PRE_COMMIT_STATUS" -eq 0 ] || exit 1
