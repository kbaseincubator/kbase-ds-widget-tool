# Pull Request

> Replace quoted instructions with the requested information.
> Leave checkboxes in place, check them off as tasks completed
> (And yes, remove this quote block!)
> 
> Also please ~~cross out~~ any requirements which are inapplicable

## Description

> * Summarize the changes.
> * Describe relevant motivation and context.
> * List any dependencies involved in this change.

## Issues Resolved

> * list Jira tickets resolved in this PR
>   e.g.  https://kbase-jira.atlassian.net/browse/PTV-XXX

> * list GitHub issues resolved by this PR
>   e.g. https://github.com/myrepo/issues/xxx

* [ ] Added the Jira Ticket id(s) to the title of the PR
* ~~[ ] Added the Github Issue Ids to the title of the PR~~


## Testing Instructions

One needs to have bash and docker installed.

```
git clone https://github.com/kbase/kbase-service-orcidlink
cd kbase-service-orcidlink
./Taskfile test
```
  
* [ ] Tests pass locally
* [ ] Tests and build pass in GitHub actions
* [ ] Manually verified that changes are available (if applicable)

## Dev Checklist

* [ ] I have performed a self-review of my own code
* [ ] I have commented my code, particularly in hard-to-understand areas
* [ ] I have made corresponding changes to the documentation
* [ ] My changes generate no new warnings
* [ ] I have added tests that prove my fix is effective or that my feature works
* [ ] New and existing unit tests pass locally with my changes
* [ ] I have run the code quality tools against the codebase

## Release Notes - Development

> This section only relevant to a PR against develop

* [ ] Ensure there is an "Unreleased" section located at the top of RELEASE_NOTES.md
* [ ] Add relevant notes to Unreleased

## Release

> This section only relevant if this PR is preparing a release

* ~~[ ] Rename the "Unreleased" section to the appropriate release, and create a new, empty "Ureleased" section at the top~~
