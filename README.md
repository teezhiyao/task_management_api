# task_management_api

# Fastapi
index.py - contains the various api definition + authentication 
models.py - definition of the tables and relationship between the tables
schemas.py - definition of the json schemas that are used to organize the parameters and output of the apis
crud.py - functions to interact with the database / sql queries

# Docker
- 'docker-compose up --build' to build and run the app / db container.

# To start the docker
docker-compose up

# API info
- http://localhost:8000/docs#/

| Request Type | Resource        | Note                                                                                               | Corresponding user story point                                         |
| ------------ | --------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| POST         | /user           | Create new user                                                                                    |                                                                        |
| POST         | /task           | Create new task                                                                                    | Employer - Create Task                                                 |
| GET          | /task           | - filter and sort as parameters for view all task<br>- Employee can only read their own task       | Employee - View Assigned Tasks<br><br>Employer - Filter/Sort all tasks |
| GET          | /user/summary   | EmployeeTask summary                                                                               | Employer - View Employee Task Summary                                  |
| PUT          | /task/{task_id} | Assign Task and update status (Employee can only update status)                                    | Employee - Task Status update<br>Employer - Assign Task                |
| POST         | /user/login     | Validate credentials with formdata with username and password. Returns access_token and token_type |                                                                        |


## Other Note
- The password for users created from init.sql are not hashed
- Assumption for role_id is that 
  - employer's role_id = 1
  - employee's role_id = 2