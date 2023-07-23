from moodle_sync import MoodleSync, moodlesync_from_credentials
import argparse

parser = argparse.ArgumentParser(description='Show module instances in a course')
parser.add_argument("credentials",
                        help="MANDATORIY JSON file including url, user, password and service",
                        type=str,
                        )
args = parser.parse_args()

ms = moodlesync_from_credentials(args.credentials)
courses = ms.get_recent_courses()

for i, course in enumerate(courses.keys()):
    print(f"{i + 1}\t{course} (ID: {courses[course]['id']})")

course_choice = int(input(f"Choose a course (1-{len(courses)}): ")) - 1
course_id = list(courses.values())[course_choice]['id']
print(f"Course ID: {course_id}")

# modules = ms.get_course_modules(course_id)
# for module in modules:
#     print(f"{module}\tID:{modules[module]['id']}\tInstance:{modules[module]['instance']}")
grade_items = ms.core_grades_get_gradeitems(course_id)
for grade_item in grade_items['gradeItems']:
    print(f"{grade_item['itemname']}\tID:{grade_item['id']}")
