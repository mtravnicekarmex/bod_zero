# Template origins

git remote URLs that are point-zero templates, not a real project's
repository. `commit_and_push()` (`agents/git_ops.py`) checks `origin`
against this list before every push and refuses if it still matches one
of these — see ADR-025. One URL per line; `#` starts a comment; blank
lines are ignored. Matching ignores a trailing `.git`, a trailing slash,
and case.

After cloning this repository to start a new project, create a fresh,
dedicated repository for it and run:

```
git remote set-url origin <new-repo-url>
```

before running the pipeline for the first time.

https://github.com/mtravnicekarmex/bod_zero.git
https://github.com/mtravnicekarmex/bod-nula.git
