from collections import OrderedDict
from datetime import datetime

import os
import sys

from entry import Entry, initialise


def clear_screen():
    """Clear the screen in the command prompt"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_employee_name():
    """Get employee name from user"""
    while True:
        employee_name = input("Enter employee name: ")
        try:
            if not employee_name:
                raise ValueError('Cannot be blank')
        except ValueError as e:
            print(e)
            continue
        else:
            return employee_name


def get_task_name():
    """Get task from user"""
    while True:
        title_task = input("Title of task: ")
        try:
            if not title_task:
                raise ValueError('Cannot be blank')
        except ValueError as e:
            print(e)
            continue
        else:
            return title_task


def get_time_spent():
    """Get time spent in minutes from user"""
    while True:
        time_spent = input("Time spent (rounded minutes): ")
        try:
            int(time_spent)
        except ValueError:
            print("""
Please input a rounded minute. i.e if 1.5, input 2; if 1.1 input 1""")
            continue
        else:
            return time_spent


def get_notes():
    """Get notes from user"""
    notes = input("Notes (Optional, you can leave this empty): ")
    return notes


def get_date():
    """Get date in the format of YYYY-MM-DD from user"""
    while True:
        """Get date from user"""
        while True:
            date_entry = input("Date of task (Please use YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date_entry, '%Y-%m-%d')
            except ValueError:
                print("""
{} is an invalid date. Please enter a correct date.""".format(date_entry))
                continue
            else:
                return date_entry


def display_temp_entry(entry):
    """Display entry to user before writing to database"""
    clear_screen()
    print("""
Date: {date}
Employee Name: {employee_name}
Task Name: {task_name}
Minutes: {minutes}
Notes: {notes}
""".format(**entry))


def create_entry(entry):
    """Create entry in database"""
    Entry.create(**entry)
    return entry


def get_user_entry():
    """Get user input for the data fields in the Entry model"""
    clear_screen()
    date = convert_string_to_datetime(get_date())
    employee_name = get_employee_name()
    task_name = get_task_name()
    minutes = get_time_spent()
    notes = get_notes()

    entry = {
        "employee_name": employee_name,
        "date": date,
        "task_name": task_name,
        "minutes": minutes,
        "notes": notes
    }

    display_temp_entry(entry)

    while True:
        save = input("\nSave entry? [Y/n] ").lower().strip()
        if save != 'n':
            input("\nEntry saved successfully! Press ENTER to continue.")
            return entry
        else:
            input("\nEntry not saved! Press ENTER to continue.")
            return None


def add_entry():
    """Add a work entry to the database"""
    entry = get_user_entry()
    if entry:
        return create_entry(entry)


def select_all_entries():
    """Gets all entries in database sorted by date"""
    entries = Entry.select().order_by(Entry.date.desc())
    return entries


def find_by_employee():
    """Search by Employee Name"""
    clear_screen()
    print("Search by Employee Name\n")
    user_input = get_employee_name()
    entries = select_all_entries()
    entries = entries.where(Entry.employee_name.contains(user_input))
    entries = check_employee_name_match(entries)
    list_entries(entries, user_input)
    return entries


def check_employee_name_match(entries):
    """
    Check to see if there are multiple employee name matches. If so, provide
    the matches and allow the user to select the name.
    """
    names = []
    for entry in entries:
        name = entry.employee_name.strip()
        if name not in names:
            names.append(name)
    if len(names) > 1:
        while True:
            clear_screen()
            print("Here are the employee names that match your search: \n")
            for name in names:
                print(name)
            employee_name = input(
                "\nWhich employee would you like to search? ").strip()
            if employee_name in names:
                entries = Entry.select().order_by(Entry.date.desc()).where(
                    Entry.employee_name == employee_name)
                return entries
            else:
                print("\n{} is not an employee's name listed above!\n".format(employee_name))
                input("Press ENTER to try again...")
    return entries


def find_by_date():
    """Search by Date"""
    clear_screen()
    # Select distinct dates from all entries
    dates = get_all_distinct_dates_list()
    print("Search by Date\n")
    print("Here are the dates we have entries for: \n")
    for date in dates:
        print(convert_datetime_to_string(date))
    print("\n")
    user_input = get_date()

    # Find and display all entries.
    entries = select_all_entries()
    entries = entries.where(Entry.date == user_input)
    list_entries(entries, user_input)
    return entries


def get_all_distinct_dates_list():
    """Find a distinct dates in the databse. Returns a list of strings."""
    dates = []
    entries = select_all_entries()
    entries = entries.order_by(Entry.date.desc())
    for entry in entries:
        date = entry.date
        if date not in dates:
            dates.append(date)
    return dates


def convert_string_to_datetime(date):
    """Converts a string to a datetime object."""
    date_datetime = datetime.strptime(date, "%Y-%m-%d").date()
    return date_datetime


def convert_datetime_to_string(date):
    """Converts datetime object to a string."""
    date = date.strftime("%Y-%m-%d")
    return date


def find_by_term():
    """Search by Task name or Notes"""
    clear_screen()
    print("Search by Task name or Notes\n")
    user_input = input("Enter a search term: ")
    entries = select_all_entries()
    entries = entries.where(
        Entry.task_name.contains(user_input)|Entry.notes.contains(user_input))
    list_entries(entries, user_input)
    return entries


def get_all_minutes():
    """Find numbers in database"""
    minutes = []
    entries = select_all_entries()
    entries = entries.order_by(Entry.date.desc())
    for entry in entries:
        minute = entry.minutes
        if minute not in minutes:
            minutes.append(minute)
    return minutes


def find_by_time_spent():
    """Search by Time Spent"""
    clear_screen()
    minutes = get_all_minutes()
    print("Search by time spent\n")
    print("Here are the minutes we have entries for: \n")
    for i in minutes:
        print(i)
    print("\n")
    user_input = get_time_spent()

    entries = select_all_entries()
    entries = entries.where(Entry.minutes == user_input)
    list_entries(entries, user_input)
    return entries


def search_entries():
    """Lookup previous work entry/entries"""
    choice = None

    while True:
        clear_screen()
        print("Search Menu\n")
        for key, value in search_menu.items():
            print("{}) {}".format(key, value.__doc__))
        choice = input("\nEnter a choice: ").lower().strip()

        if choice in search_menu:
            clear_screen()
            search = search_menu[choice]()
            return search


def quit_program():
    """Exit the Work Log DB app"""
    print("Thanks for using the Work Log DB app. \nSee you soon!")
    sys.exit()


def display_entry(entry):
    """Display a single entry"""
    print("Date: {}\nEmployee Name: {}\nTask Name: {}\nMinutes: {}\nNotes: {}".format(
            entry.date,
            entry.employee_name,
            entry.task_name,
            entry.minutes,
            entry.notes))


def list_entries(entries, user_input):
    """Shows list of entries"""
    clear_screen()
    if entries:
        return display_entries(entries)
    else:
        print("No matches found for {}!".format(user_input))
        response = input("\nDo you want to search something else? Y/[n] ")
        if response.lower().strip() != 'y':
            return menu_loop()
        else:
            clear_screen()
            return search_entries()


def display_entries(entries):
    """Displays entries to the screen"""
    index = 0

    while True:
        clear_screen()
        print_entries(index, entries)

        display_nav_options(index, entries)

        user_input = input("\nSelect option from above: ").lower().strip()

        if len(entries) > 1 and user_input == 'n':
            index += 1
            clear_screen()
        elif len(entries) > 1 and index < len(entries) - 1 and user_input == 'n':
            index += 1
            clear_screen()
        elif len(entries) > 1 and index < len(entries) - 1 and user_input == 'p':
            index -= 1
            clear_screen()
        elif len(entries) > 1 and index == len(entries) - 1 and user_input == 'p':
            index -= 1
            clear_screen()
        elif user_input == 'q':
            return menu_loop()
        else:
            input("\n{} is not a valid command! Please try again.".format(user_input))


def display_nav_options(index, entries):
    """Displays a menu that let's the user page through the entries."""
    p = "[P] - Previous entry"
    n = "[N] - Next entry"
    q = "[Q] - Return to Main Menu"
    menu = [p, n, q]

    if len(entries) == 1:
        menu.remove(p)
        menu.remove(n)
    elif len(entries) > 1 and index == 0:
        menu.remove(p)
    elif len(entries) > 1 and index == len(entries) - 1:
        menu.remove(n)

    print("\n")
    for option in menu:
        print(option)
    return menu


def print_entries(index, entries, display=True):
    """Print entries to screen"""
    if display:
        print("Showing {} of {} entry(ies)".format(index + 1, len(entries)))

    print("\n")
    print("Date: {}\nEmployee Name: {}\nTask Name: {}\nMinutes: {}\nNotes: {}".format(
            convert_datetime_to_string(entries[index].date),
            entries[index].employee_name,
            entries[index].task_name,
            entries[index].minutes,
            entries[index].notes))


def menu_loop():
    """Return to Main Menu"""
    choice = None

    while True:
        clear_screen()
        print("Work Log DB\nWhat would you like to do?\n")
        for key, value in main_menu.items():
            print("{}) {}".format(key, value.__doc__))
        choice = input("\nEnter a choice: ").lower().strip()

        if choice in main_menu:
            clear_screen()
            main_menu[choice]()


main_menu = OrderedDict([
    ('a', add_entry),
    ('b', search_entries),
    ('c', quit_program),
])


search_menu = OrderedDict([
    ('a', find_by_employee),
    ('b', find_by_date),
    ('c', find_by_time_spent),
    ('d', find_by_term),
    ('e', menu_loop)
])


if __name__ == '__main__':
    initialise()
    clear_screen()
    menu_loop()