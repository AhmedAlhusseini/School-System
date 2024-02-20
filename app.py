# Using SQLite3 database .
import sqlite3

# Making a connection with the database .
connection = sqlite3.connect("school.db")
cursor = connection.cursor()


def create_tables():
    """
    Creates students and lessons tables .
    """
    # Creating students' table .
    cursor.execute('''CREATE TABLE IF NOT EXISTS students(
                  student_number INTEGER PRIMARY KEY,
                  name TEXT, 
                  nickname TEXT, 
                  age INTEGER, 
                  grade TEXT, 
                  reg_date TEXT
                  );
                  ''')
    # Creating lessons table .
    cursor.execute('''CREATE TABLE IF NOT EXISTS lessons(
    lesson_number INTEGER PRIMARY KEY, 
    name TEXT,
    subscriber_number INTEGER,
    FOREIGN KEY (subscriber_number) REFERENCES students (student_number)
    );
    ''')
    # Writing changes .
    connection.commit()


def get_number() -> int:
    """
    Takes the student's number from the user .
    :return: The student's number .
    """
    answer = to_int(input("Enter the student's number: "))
    return answer


def find(_number: int) -> tuple:
    """
    Searches for the student in the students' table .
    :param _number: The number of the student .
    :return: A row contains student's information .
    """
    cursor.execute("SELECT * FROM students WHERE student_number=?;", (_number,))
    return cursor.fetchone()


def to_int(string: str) -> int:
    """
    Converts a string into an integer .
        *If the string contains non-numeric characters,
        it calls itself .
    :param string: A string contains numeric characters .
    :return: An integer from the numeric characters .
    """
    try:
        return int(string)
    except ValueError:
        print("This field must be an integer .")
        return to_int(input("Try again: "))


def form_head(header: str):
    """
    Prints the header of the forms .
    :param header: The name of the form .
    """
    print(f"{'-' * 20} {header} {'-' * 20}")


def form_tail():
    """
    Prints the footer of the forms .
    """
    print('-' * 64)


def get_lessons(prompt: str) -> list:
    """
    Takes the lessons subscriptions for the student .
    :param prompt: The prompt of the input .
    :return: A list contains subscribed lessons .
    """
    print(f"{'-' * 20} Lessons subscription {'-' * 20}")
    # Getting the lessons list from the database .
    cursor.execute('''SELECT DISTINCT(name) FROM lessons''')
    records = cursor.fetchall()
    # Initializing the lessons list .
    subjects = [x[0] for x in records]
    lessons = {}
    index = 0
    for key in range(1, len(subjects) + 1):
        lessons[f'{key}'] = subjects[index]
        index += 1
    for k, v in lessons.items():
        print(f'{k}: {v}')
    # Getting the subscriptions from the user .
    codes = input(prompt)
    numbers = codes.split(',')
    processed = []
    subscriptions = []
    for x in numbers:
        if x not in lessons.keys():
            print(f"The invalid input {x} is canceled!")
            continue
        if x in processed:
            print(f"The repeated lesson number {x} is canceled!")
        else:
            processed.append(x)
            subscriptions.append(lessons[x])
    return subscriptions


def add_student():
    """
    Adds a new student to the students' table,
    his lessons to the lessons table .
    """
    # Getting the student's information .
    form_head("Adding a new student")
    student_number = get_number()
    if find(student_number):
        print("This number is already existed!")
        return add_student()
    name = input("Enter the name of the student: ")
    nickname = input("Enter the nickname of the student: ")
    age = to_int(input("Enter the age of the student: "))
    grade = input("Enter the grade of the student: ")
    reg_date = input("Enter the registration date of the student: ")
    # Getting the student's lessons .
    lessons = get_lessons("Enter the lessons numbers for subscription: ")
    form_tail()
    # Inserting the student's information into the students' table .
    cursor.execute('''INSERT INTO students 
        (student_number,name, nickname, age, grade, reg_date)
        VALUES (?, ?, ?, ?, ?, ?);''',
                   (student_number, name, nickname, age, grade, reg_date)
                   )
    # Inserting the student's lessons into the lessons table .
    for name in lessons:
        cursor.execute('''INSERT INTO lessons 
            (name,subscriber_number) VALUES (?, ?);''',
                       (name, student_number)
                       )
    # Writing changes .
    connection.commit()
    print()
    print("Student added successfully!")


def failed():
    """
    Prints the message of failing searching .
    """
    print("Student not found!")


def show_student():
    """
    Prints the student's information .
    """
    # Getting the student's information .
    student_number = get_number()
    student = find(student_number)
    if not student:
        failed()
    else:
        # Getting the student's lessons .
        cursor.execute('''SELECT lessons.name 
            FROM lessons JOIN students ON
            students.student_number = lessons.subscriber_number
            WHERE student_number = ? ;''',
                       (student_number,)
                       )
        result = cursor.fetchall()
        # Initializing the student's lessons .
        lessons = [x[0] for x in result]
        # Printing the student's information .
        print(f'''
            {'-' * 20} Student's Information {'-' * 20}
            number: {student[0]},
            name: {student[1]},
            nickname: {student[2]},
            age: {student[3]},
            grade: {student[4]},
            registration date: {student[5]},
            lessons: {lessons}
            {'-' * 64}
        ''')


def update_student():
    """
    Updates the student's information .
    """
    # Getting the student's number .
    student_number = get_number()
    if not find(student_number):
        failed()
    else:
        modify(student_number)


def modify(student_number: int):
    """
    Modifies the student's information .
    :param student_number: The number of the student .
    """
    # Getting the new information for the student .
    form_head("Updating the student's information")
    new_student_number = to_int(input("Enter the new number of the student: "))
    if new_student_number != student_number:
        if find(new_student_number):
            print("The new number is already existed!")
            return modify(student_number)
    name = input("Enter the new name of the student: ")
    nickname = input("Enter the new nickname of the student: ")
    age = to_int(input("Enter the new age of the student: "))
    grade = input("Enter the new grade of the student: ")
    reg_date = input("Enter the new registration date of the student: ")
    # Getting the new lessons .
    new_lessons = get_lessons("Enter the new lessons numbers to subscribe on: ")
    form_tail()
    # Deleting the old lessons .
    cursor.execute("DELETE FROM lessons WHERE subscriber_number = ?;", (student_number,))
    # Updating the student's information in the students' table .
    cursor.execute('''UPDATE students 
                SET student_number=?, name=?, nickname=?, age=?, grade=?, reg_date=?
                WHERE student_number=?;''',
                   (new_student_number, name, nickname, age, grade, reg_date, student_number)
                   )
    # Inserting the new lessons .
    for lesson in new_lessons:
        cursor.execute('''INSERT INTO lessons 
               (name,subscriber_number) VALUES (?, ?);''',
                       (lesson, new_student_number)
                       )
    # Writing changes .
    connection.commit()
    print()
    print("Student updated successfully!")


def delete_student():
    """
    Deletes the student from the students' table,
    and his lessons from lessons table .
    """
    # Getting the student's number .
    form_head("Deleting the student")
    student_number = get_number()
    form_tail()
    if not find(student_number):
        failed()
    else:
        # Deleting the lessons of the student from lessons table .
        cursor.execute("DELETE FROM lessons WHERE subscriber_number = ?;", (student_number,))
        # Deleting the student's information from the students' table .
        cursor.execute("DELETE FROM students WHERE student_number=?;", (student_number,))
        # Writing changes .
        connection.commit()
        print("Student deleted successfully!")


def connected() -> bool:
    """
    keeps the connection with the database .
    :return: True if continue , else False .
    """
    power = input("Click 'y' to continue or 'n' to terminate the session: ")
    if power == 'y':
        return True
    elif power == 'n':
        connection.close()
        return False
    else:
        print("Invalid choice!")
        return connected()


if __name__ == "__main__":
    create_tables()
    session = True
    while session:
        print('''
        Please choose the operation you want to perform:
        * To add a student, click on the letter a .
        * To delete a student, click on the letter d .
        * To modify a student’s information, click on the letter u .
        * To view student information, click on the letter s .
        ''')
        choice = input("Enter your choice: ")
        if choice == 'a':
            add_student()
        elif choice == 'd':
            delete_student()
        elif choice == 'u':
            update_student()
        elif choice == 's':
            show_student()
        else:
            print("Invalid choice!")
        session = connected()
