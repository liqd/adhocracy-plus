# Fair Vote Module

## Simulations:
### `create-delete` file:
For initialization:
1. Set the following variables as you want: 
    
        ORG = "org-name"
        PROJECT = "project-name"
        MODULE = "module-name"
        superuser_name = "superuser-name"
        superuser_pass = "superuser-password" 
 
2. Run the following functions:
    1. **create_superuser** - create superuser that will be the organisation inventor.
    2. **create_organisation** - create the organisation in order to add project.
    3. **create_project** - create the project in order to add modules. (use can you the returned organisation for 'org' argument)
    4. **create_module** - create the fairvote module which allows users add ideas and support them. (use can you the returned organisation for 'project' argument)
    5. **register** - register all users in the 'user_list'.

For reset:
1. 

### `simulator_sn`/`simulator_sn_bicycle` file:
**Prerequisites:**
firefox browser

**Required libraries:**
1. mechanize
2. selenium

**For initialization:**
1. Set the following variables as you want: 

        URL = "http://localhost:8004"
        ORG = "org-name"
        PROJECT = "project-name"
        MODULE = "module-name"
        superuser_name = "superuser-name"
        superuser_pass = "password"

2. Ensure that `user_list` equals to the one in the previous file.
3. You can edit the `idea_list` if you want to.
4. Run the following functions:
    ### submit ideas (by superuser)
    1. submit_ideas_simulator()

    ### users vote ideas
    1. `users = user_list.copy()`
    2. `random.shuffle(users)`
    3. `link = f"{URL}/{ORG}/projects/module/{MODULE}/?"` - module url
    5. `ideas_p = get_all_ideas(link)` - idea links list
    6. `vote_ideas_simulator(ideas_p)` - the voting simulator

    ### Accepting ideas by superuser
    `accept_ideas_simulator(n)` -
    accept the most n fair ideas