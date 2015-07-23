# Change Log
All notable changes to this project will be documented in this file.

## [1.2.0] - 2015-07-23
### Added
- Management command to export project data for Jira:
  `generate_jira_migration_json <project_id> { --agile }`

## [1.1.2] - 2015-06-03
### Fixed
- Layout issues on timesheet page

## [1.1.1] - 2015-05-04
### Fixed
- Reverted the previous/next buttons since they broke things
- Some things on the scrum views

## [1.1.0] - 2015-04-27
### Added
- Previous/next buttons on ticket detail page
- Added work summary per day and total hours worked
### Fixed
- Fixed imgurize templatetag so Timesheet view still displayed on http error
  429 (too many requests)

## [1.0.0] - 2015-04-13
### Added
- Everything
