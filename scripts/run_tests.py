import sys
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TESTS = {
    "attendance": "tests/test_attendance.py",
    "authentication": "tests/test_authentication.py",
    "courses": "tests/test_courses.py",
    "grades": "tests/test_grades.py",
    "notification": "tests/test_notification.py",
    "students": "tests/test_students.py",
    "dashboard": "tests/test_dashboard.py",
}

def run_tests(selected_tests):
    os.chdir(BASE_DIR)

    if not selected_tests or "all" in selected_tests:
        print("🚀 Running ALL tests...")
        command = ["pytest"]
    else:
        test_files = []
        for test in selected_tests:
            if test not in TESTS:
                print(f"❌ Unknown test: {test}")
                print(f"Available tests: {', '.join(TESTS.keys())}")
                sys.exit(1)
            test_files.append(TESTS[test])

        print(f"🚀 Running tests: {', '.join(selected_tests)}")
        command = ["pytest"] + test_files

    subprocess.run(command)


if __name__ == "__main__":
    """
    Usage:
        python scripts/run_test.py                -> run all tests
        python scripts/run_test.py all            -> run all tests
        python scripts/run_test.py students
        python scripts/run_test.py attendance grades
    """

    args = sys.argv[1:]
    run_tests(args)
