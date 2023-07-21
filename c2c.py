from moodle_sync import MoodleSync, moodlesync_from_credentials
import argparse
from loguru import logger
from grade import Grade, grades_list_from_assign_get_grades_response, compare_grades, grades_list_from_gradereport

logger.add("logs/c2c.log", rotation="50 MB", level="INFO")


def parse_args():
    parser = argparse.ArgumentParser(description='Copy grades from one assignment to another')
    parser.add_argument("credentials",
                        help="MANDATORIY JSON file including url, user, password and service",
                        type=str,
                        )
    parser.add_argument('from_assignment_id', type=int, help='MANDATORIY source assignment ID')
    parser.add_argument('to_assignment_id', type=int, help='MANDATORIY target assignment ID')
    parser.add_argument('-i', '--course-id', type=int,
                        help='If grade is from calculation (and not from an assignment) course id is needed',
                        dest='course_id', default=None)
    parser.add_argument('-c', '--comment', type=str, help='Comment to add to the grade', dest='comment', default=None)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    logger.info(f"{args.credentials} {args.from_assignment_id}({args.course_id}) --> "
                f"{args.to_assignment_id}, comment: {args.comment}")
    ms = moodlesync_from_credentials(args.credentials)

    from_assignment_id = args.from_assignment_id
    to_assignment_id = args.to_assignment_id
    comment = args.comment
    course_id = args.course_id
    if course_id is None:
        grades = grades_list_from_assign_get_grades_response(ms.mod_assign_get_grades([from_assignment_id]), comment)
    else:
        grades = grades_list_from_gradereport(ms.gradereport_user_get_grade_items(course_id), from_assignment_id,
                                              comment)

    updated_grades = ms.grade_upload(assignment_id=to_assignment_id, grades=grades, notifications="none")
    logger.info(f"Grades updated: {updated_grades}")


if __name__ == "__main__":
    main()
