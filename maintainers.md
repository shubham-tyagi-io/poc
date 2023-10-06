# Guide for Maintainers
This repository is is primarily based on github actions and python scripting. With the help of Personal Access Toekn with right privledges, one can maintain github team users.

## Prerequisites
The workflow comprises of mentioned below pre-requisites:
 
  - Team structure is dependent on parent team yaml files and should be placed under "users" folder.
  - Yaml files name should be of same name as that of parent team name.
  - Yaml file must conatin "githubid" and "role" key
  - There should be atleast one "githubid". Blank file wont be accepted by the script and workflow will fail.
   

## Workflows
[Workflow Batch]()

This repository is having one workflow with on push to main branch. The workflows is dynamic and can be leveredge for any organisation with appropriate github access token.

```yml
env:
  organisation_name: cto-devops 
```
## Script
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Script works on the package for response. From api.github.com, script is altering the data for adding/removing users. Script has mnetioned below functionality
  - Function to add user to team
  - Function to remove a user from a team
  - Display list of pending and active users

## Users Folder
Teams and yaml structure should be created as mentioned below
```yml
####################
# Team Name PJPROS #
####################

//pjpros.yml

users:
  githubid: user1
  role: dev
  
###############
# GitHub Team #
###############
Parent Team name  --> pjpros
Child Team name   --> pjpros-dev

 ```
## Limitations
- Workflow won`t create team automatically based on yaml file name. It will be a manual activity.


