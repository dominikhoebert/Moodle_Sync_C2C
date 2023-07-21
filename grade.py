from dataclasses import dataclass
from datetime import datetime


@dataclass
class Grade:
    student_id: int
    from_assignment: int
    grade: float
    comment: str

    def __str__(self):
        return self.__repr__() + f'|"{self.comment}"'

    def __repr__(self):
        return f"id={self.student_id}|assig={self.from_assignment}|grade={self.grade}"

    def __eq__(self, other):
        return self.student_id == other.student_id and float(self.grade) == float(other.grade)

    def to_grade_obj(self):
        return {
            "userid": self.student_id,
            "grade": self.grade,
            "attemptnumber": -1,
            "addattempt": 0,
            "workflowstate": "graded",
            "plugindata": {
                "assignfeedbackcomments_editor": {
                    "text": self.comment,
                    "format": 4,
                }
            }
        }

    def to_user_flag_obj(self):
        return {
            "userid": self.student_id,
            "mailed": 1
        }


def grades_list_from_assign_get_grades_response(response: list, comment: str = ""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    grades = []
    from_assignment = response['assignments'][0]['assignmentid']
    for grade in response['assignments'][0]['grades']:
        build_comment = "automatic grade for UserID: " + str(
            grade['userid']) + " Timestamp: " + timestamp + " " + comment
        grades.append(Grade(student_id=grade['userid'], from_assignment=from_assignment, grade=grade['grade'],
                            comment=build_comment))
    return grades


def grades_list_from_gradereport(response: list, instance_id: int, comment: str = ""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    grades = []
    for student in response['usergrades']:
        for grade_item in student['gradeitems']:
            if grade_item['id'] == instance_id:
                build_comment = "automatic grade for UserID: " + str(
                    student['userid']) + " Timestamp: " + timestamp + " " + comment
                if grade_item['graderaw'] is not None:
                    grades.append(Grade(student_id=student['userid'], from_assignment=instance_id,
                                        grade=grade_item['graderaw'], comment=build_comment))
    return grades


def compare_grades(new_grades: list, old_grades: list):
    """
    :param new_grades: list of grades
    :param old_grades: list of grades
    :return: list of grades that are in new_grades but not in old_grades, or have a different grade
    """
    return [grade for grade in new_grades if grade not in old_grades]
