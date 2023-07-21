import json

import pandas as pd
from requests import post
from loguru import logger
from grade import Grade, grades_list_from_assign_get_grades_response, compare_grades

"""
[SSL: CERTIFICATE_VERIFY_FAILED] Error: https://stackoverflow.com/questions/51925384/unable-to-get-local-issuer-certificate-when-using-requests-in-python
Install certifi; copy cacert.pem aus certifi folder
"""

ENDPOINT = "/webservice/rest/server.php"


def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.

    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict is None:
        out_dict = {}
    if not type(in_args) in (list, dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args) == list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args) == dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict


def moodlesync_from_credentials(credentials_file_path: str = "data/credentials.json"):
    with open(credentials_file_path, "r") as f:
        credentials = json.load(f)
    return MoodleSync(credentials["url"], credentials["user"], credentials["password"], credentials["service"])


class MoodleSync:
    def __init__(self, url: str, username: str, password: str, service: str):
        self.url = url
        self.key = self.get_token(url, username, password, service)

    def call(self, function_name, **kwargs):
        """Calls moodle API function with function name fname and keyword arguments.

        Example:
        call_mdl_function('core_course_update_courses',
                               courses = [{'id': 1, 'fullname': 'My favorite course'}])
        """
        parameters = rest_api_parameters(kwargs)
        parameters.update({"wstoken": self.key, 'moodlewsrestformat': 'json', "wsfunction": function_name})
        response = post(self.url + ENDPOINT, parameters)
        response = response.json()
        if type(response) == dict and response.get('exception'):
            raise SystemError("Error calling Moodle API\n", response)
        return response

    def get_token(self, url, username, password, service):
        obj = {"username": username, "password": password, "service": service}
        response = post(url + "/login/token.php", data=obj)
        response = response.json()
        return response['token']

    def get_recent_courses(self):
        response = self.call('core_course_get_recent_courses')
        return {c['fullname']: {'id': c['id']} for c in response}

    def get_course_modules(self, course_id):
        response = self.call('core_course_get_contents', courseid=course_id)
        modules = {}
        for section in response:
            for module in section['modules']:
                if 'modname' in module:
                    if module['modname'] == 'assign':
                        modules[module['name']] = {'id': module['id'], 'instance': module['instance']}
        return modules

    def gradereport_user_get_grade_items(self, course_id: int):
        return self.call('gradereport_user_get_grade_items', courseid=course_id)

    def get_gradereport_of_course(self, course_id: int):
        response = self.gradereport_user_get_grade_items(course_id)
        gradeitems = {}
        for gradeitem in response['usergrades'][0]['gradeitems']:
            gradeitems[gradeitem['itemname']] = gradeitem['id']

        pd.MultiIndex.from_product([list(gradeitems.keys()), ["grade", "feedback"]], names=["first", "second"])

        df = pd.DataFrame(columns=['userfullname', 'userid'] + list(gradeitems.keys()))

        for student in response['usergrades']:
            grades = {'userfullname': student['userfullname'], "userid": student['userid']}
            for gradeitem in student['gradeitems']:
                grades[gradeitem['itemname']] = gradeitem['gradeformatted']
            df = df.append(grades, ignore_index=True)

        df = df.rename(columns={None: 'Kurs', 'userfullname': 'Schüler'})
        return df

    def get_student_info(self, userlist):
        """
        Takes an array of dict with key userid=int, courseid=int
        Returns a DataFrame with user info id, fullname, email, groups (all groups as joined str)

        :param userlist:
        :return DataFrame:
        """
        response = self.call('core_user_get_course_user_profiles', userlist=userlist)
        user_df = pd.DataFrame(columns=['id', 'fullname', 'email', 'groups'])
        for student in response:
            groups_list = []
            for group in student["groups"]:
                groups_list.append(group["name"])
            groups = ""
            if len(groups_list) > 0:
                groups = ",".join(groups_list)
            user_df = user_df.append(
                {"id": student["id"], "fullname": student["fullname"], "email": student["email"], "groups": groups},
                ignore_index=True)
        return user_df

    def get_enrolled_students(self, course_id):
        """
        Returns a DataFrame with user info id, fullname, email, groups (all groups as joined str)"""
        response = self.call('core_enrol_get_enrolled_users', courseid=course_id)
        user_df = pd.DataFrame(columns=['id', 'firstname', 'lastname', 'email'])
        for student in response:
            new_user = pd.DataFrame(
                {"id": student["id"], "firstname": student["firstname"], "lastname": student["lastname"],
                 "email": student["email"]}, index=[0])
            user_df = pd.concat([user_df, new_user])
        return user_df

    def save_grades(self, assignmet_id: int, grades: list):
        return self.call('mod_assign_save_grades', assignmentid=assignmet_id, applytoall=0, grades=grades)

    def get_user_flags(self, assignment_ids: list):
        return self.call('mod_assign_get_user_flags', assignmentids=assignment_ids)

    def set_user_flags(self, assignment_id: int, userflags: list):
        return self.call('mod_assign_set_user_flags', assignmentid=assignment_id, userflags=userflags)

    def mod_assign_get_grades(self, assignmentids):
        return self.call('mod_assign_get_grades', assignmentids=assignmentids)

    def grade_upload(self, assignment_id: int, grades: list, notifications: str):
        """
        :param assignment_id: int
        :param grades: list of dicts containing student_id, grade, comment
        :param notifications: str can be all, changed, none
        :return mumber of updated grades:
        """
        if notifications == "changed":
            old_grades = grades_list_from_assign_get_grades_response(ms.mod_assign_get_grades([assignment_id]))
            grades = compare_grades(grades, old_grades)

        if len(grades) == 0:
            return 0

        grades_object = []
        user_flag_object = []
        for grade in grades:
            grades_object.append(grade.to_grade_obj())
            user_flag_object.append(grade.to_user_flag_obj())
        self.save_grades(assignment_id, grades_object)

        if notifications == "none":
            self.set_user_flags(assignment_id, user_flag_object)
        return len(grades)


if __name__ == '__main__':
    ms = moodlesync_from_credentials()
    # assignment_id = 9430
    # new_grades = [Grade(student_id=82, from_assignment=None, grade=2, comment="test5")]
    # updated_grades = ms.grade_upload(assignment_id=assignment_id, grades=new_grades, notifications="none")
    # print("Grades updated: ", updated_grades)

    # print(ms.get_gradereport_of_course(1309))
    # print(ms.mod_assign_get_grades([2039]))
    print(ms.get_gradereport_of_course(1309))
