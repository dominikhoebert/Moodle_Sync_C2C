# Moodle_Sync_C2C

## C2C Course to Course

Python script for coping grades from one course to another.

### [Docker](https://hub.docker.com/repository/docker/dominik1220/moodle_sync_c2c)

``` bash
docker pull dominik1220/moodle_sync_c2c
docker run --rm -v ${pwd}/data:/c2c/data -v ${pwd}/logs:/c2c/logs dominik1220/moodle_sync_c2c data/credentials.json 1234 5678 --save-grade --comment "copied from [course name assignment name](https://elearning.school.com/mod/assign/view.php?id=123456)"
```

### CLI interface:

``` bash
python c2c.py -h
python c2c.py credentials.json file from_course_instance_id to_course_instance_id --save-grade --comment "comment"
python c2c.py credentials.json 1234 5678 --save-grade --comment "copied from [course name assignment name](https://elearning.school.com/mod/assign/view.php?id=123456)"
```

If grades from a calculation are needed, the course id has to be specified with the --course-id parameter.
IDs can be found in the URL of the calculation.

``` bash
python c2c.py credentials.json file from_course_instance_id to_course_instance_id --course-id course_id --save-grade --comment "comment"
python c2c.py credentials.json 1234 5678 --course-id 9876 --save-grade --comment "copied from [course name assignment name](https://elearning.school.com/mod/assign/view.php?id=123456)"
```

### credentials.json structure

``` json
{
  "url": "https://elearning.school.com",
  "user": "username",
  "password": "password",
  "service": "servicename"
}
```

contact your moodle administrator for the service name

## Module Instance

Script to get the id from a course and grade item

``` bash
python show_module_instance.py credentials.json
```

### Docker:

``` bash
docker run --rm -it --entrypoint python dominik1220/moodle_sync_c2c show_module_instances.py credentials.json
```

## TODO

* ~~notifications~~
    * ~~all/changed/none~~
* ~~function grade_upload(assigment_id, grades=[{"student_id": "123", "grade": "1", "comment": "comment"}],
  notification="
  all/changed/none")~~
* ~~function for grade comment standart text "Grade for Studentname from Course[link]/Bewertung[link] updated
  timestamp"~~
* ~~get grade from different course~~
* ~~cli interface~~
* ~~get grade from calculations (gradeitem)~~
* ~~docker container~~
* ~~show also calculation instance id~~
* ~~save history of copied grades in file~~
* ~~logging~~
