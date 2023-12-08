import tkinter as tk
import calendar
from datetime import datetime, date
# import datetime
from tkinter import messagebox, simpledialog
import requests
from bs4 import BeautifulSoup


# Calendar Module
class CalendarModule(tk.Frame):
    """
    A Calendar Module class for a tkinter application.

    This class creates and manages a calendar UI, allowing users to navigate through months and years,
    and interact with events.

    Attributes:
        parent: The parent widget for this module.
        event_management: An EventManagement instance for event handling.
        current_year: The current year.
        current_month: The current month.
    """
    def __init__(self, parent, event_management):
        """
        Initialize the CalendarModule instance.

        Args:
            parent: The parent widget for this module.
            event_management: An EventManagement instance for event handling.
        """
        super().__init__(parent)
        self.parent = parent
        self.event_management = event_management
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface for the calendar module.
        This method sets up the navigation frame, buttons, label for month and year,
        and the frame for displaying the calendar.
        """
        # Create navigation frame
        self.nav_frame = tk.Frame(self)
        self.nav_frame.pack(side="top", fill="x")

        # Buttons for previous and next month
        self.prev_month_button = tk.Button(self.nav_frame, text="<", command=self.prev_month)
        self.prev_month_button.pack(side="left")

        self.next_month_button = tk.Button(self.nav_frame, text=">", command=self.next_month)
        self.next_month_button.pack(side="right")

        # Adjust the size of the navigation buttons
        self.prev_month_button.config(width=3, height=1)
        self.next_month_button.config(width=3, height=1)

        # Label for displaying the current month and year
        self.month_year_label = tk.Label(self.nav_frame, text="", font=("Helvetica", 16))
        self.month_year_label.pack(side="left", fill="x", expand=True)

        # Calendar frame
        self.calendar_frame = tk.Frame(self)
        self.calendar_frame.pack_propagate(False)
        self.calendar_frame.pack(fill="both", expand=True)

        self.display_month(self.current_year, self.current_month)

    def display_month(self, year, month):
        """
        Display the calendar for a given year and month.

        Args:
            year: The year to display.
            month: The month to display.
        """
        # Clear previous calendar frame
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Update month and year label
        self.month_year_label.config(text=f"{calendar.month_name[month]} {year}")

        # Create the calendar
        month_calendar = calendar.monthcalendar(year, month)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Displaying the days of the week
        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day).grid(row=0, column=i)

        for i, week in enumerate(month_calendar):
            for j, day in enumerate(week):
                if day != 0:
                    day_label = tk.Label(self.calendar_frame, text=day)
                    day_label.grid(row=i+1, column=j)
                    # Bind the click event to the day_selected method
                    day_label.bind('<Button-1>', lambda event, day=day: self.day_selected(day))
        # Assign weights to the rows and columns
        for i in range(7):  # Assuming 7 columns for the days of the week
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(1, 7):  # Assuming 6 possible rows for weeks
            self.calendar_frame.rowconfigure(i, weight=1)

    def prev_month(self):
        """
        Navigate to the previous month in the calendar.

        This method updates the calendar to display the previous month. It automatically
        adjusts the year if the current month is January and decrements the year accordingly.
        """
        # Go to the previous month
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.display_month(self.current_year, self.current_month)

    def next_month(self):
        """
        Navigate to the next month in the calendar.

        This method updates the calendar to display the next month. It automatically
        adjusts the year if the current month is December and increments the year accordingly.
        """

        # Go to the next month
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.display_month(self.current_year, self.current_month)

    def day_selected(self, day):
        """
        Handle the selection of a day on the calendar.

        This method is triggered when a user selects a day on the calendar. It updates
        the event management module with the selected date.

        Args:
            day: The day of the month that was selected.
        """

        selected_date = date(self.current_year, self.current_month, day)

        # Updating events with saved EventManagement references
        self.event_management.set_selected_date(selected_date)


# Event Management Module
class EventManagement(tk.Frame):
    """
    Event Management class for a tkinter application.

    This class handles the creation, display, and management of events within the calendar application.
    It interacts with external sources to scrape and display event data.

    Attributes:
        parent: The parent widget for this module.
    """
    def __init__(self, parent):
        """
        Initialize the EventManagement instance.

        Args:
            parent: The parent widget for this module.
        """
        super().__init__(parent)
        self.parent = parent
        self.events = {}  # Store events as a dict with dates as keys
        self.selected_date = datetime.now().date()  # Default selected date
        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface for the event management module.

        This method sets up the UI elements for displaying and managing events.
        It includes a label to show the selected date, a listbox to display events,
        form fields for adding or editing events, and buttons for event operations 
        like add, edit, delete, and scraping external event data.
        """
        # Display the selected date
        self.date_label = tk.Label(self, text=f"Events for: {self.selected_date.strftime('%Y-%m-%d')}")
        self.date_label.pack(side=tk.TOP, fill=tk.X)

        # Event list area
        self.event_listbox = tk.Listbox(self, height=8)
        self.event_listbox.pack(side=tk.TOP, fill=tk.X, expand=True)

        # Form for adding events
        self.event_time_label = tk.Label(self, text="Event Time (HH:MM):")
        self.event_time_label.pack(side=tk.TOP, fill=tk.X)
        self.event_time_entry = tk.Entry(self)
        self.event_time_entry.pack(side=tk.TOP, fill=tk.X)

        self.event_name_label = tk.Label(self, text="Event Name:")
        self.event_name_label.pack(side=tk.TOP, fill=tk.X)
        self.event_name_entry = tk.Entry(self)
        self.event_name_entry.pack(side=tk.TOP, fill=tk.X)

        self.add_button = tk.Button(self, text="Add Event", command=self.add_event)
        self.add_button.pack(side=tk.TOP, fill=tk.X)

        self.edit_button = tk.Button(self, text="Edit Selected Event", command=self.edit_event)
        self.edit_button.pack(side=tk.TOP, fill=tk.X)

        self.delete_button = tk.Button(self, text="Delete Selected Event", command=self.delete_event)
        self.delete_button.pack(side=tk.TOP, fill=tk.X)

        self.scrape_button = tk.Button(self, text="Scrape F1 Schedule", command=self.scrape_f1_schedule)
        self.scrape_button.pack(side=tk.TOP, fill=tk.X)

        # Load events for selected date
        self.load_events(self.selected_date)

    def load_events(self, date):
        """
        Load and display events for a specified date.

        This method clears the current event list and loads events for the given date. 
        Events are displayed in the event listbox. If no events are available for the 
        specified date, the listbox will be empty.

        Args:
            date: The date for which events are to be loaded, represented as a datetime.date object.
        """
    # Code to load an
        # Clear the listbox
        self.event_listbox.delete(0, tk.END)
        # Load events for the given date
        if date in self.events:
            for event_time, event_name in sorted(self.events[date].items()):
                self.event_listbox.insert(tk.END, f"{event_time} - {event_name}")

    def add_event(self):
        """
        Add a new event to the calendar.

        This method retrieves event time and name from the entry fields, performs basic validation, 
        and adds the event to the events dictionary. It then reloads the event listbox to display 
        the new event and clears the entry fields.
        """
        # Get event time and name from the entries
        event_time = self.event_time_entry.get()
        event_name = self.event_name_entry.get()

        # Basic validation
        if not event_time or not event_name:
            messagebox.showwarning("Warning", "Both time and name are required.")
            return

        # Add the event to the dictionary
        if self.selected_date not in self.events:
            self.events[self.selected_date] = {}
        self.events[self.selected_date][event_time] = event_name

        # Reload the event listbox
        self.load_events(self.selected_date)

        # Clear the entries
        self.event_time_entry.delete(0, tk.END)
        self.event_name_entry.delete(0, tk.END)

    def add_event_from_scrape(self, date, event_name, event_time):
        """
        Add an event obtained from web scraping.
        This method is used to add events that are scraped from external sources. It converts 
        the provided date string to a datetime.date object, and adds the event to the events 
        dictionary. If the event date matches the selected date, it reloads the event listbox.

        Args:
            date: The date of the event, as a string.
            event_name: The name of the event.
            event_time: The time of the event.
        """
        # Convert date strings to datetime.date objects
        # Assuming the format of date is "Friday, March 3, 2023".
        event_date = datetime.strptime(date, "%A, %B %d, %Y").date()

        # Add events to the self.events dictionary
        if event_date not in self.events:
            self.events[event_date] = {}
        self.events[event_date][event_time] = event_name

        # Reload event if the selected date is the currently loaded date
        if event_date == self.selected_date:
            self.load_events(event_date)

    def delete_event(self):
        """
        Delete the selected event from the calendar.

        This method removes the selected event from the events dictionary and reloads
        the event listbox. If no event is selected, it displays an informational message.
        """
        # Get the index of the selected event
        selected_index = self.event_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            event_time = list(self.events[self.selected_date].keys())[selected_index]

            # Delete events from a data structure
            del self.events[self.selected_date][event_time]

            # load event
            self.load_events(self.selected_date)
        else:
            messagebox.showinfo("Info", "Please select an event to delete.")

    def edit_event(self):
        """
        Edit the name of the selected event.

        This method allows the user to edit the name of the selected event. It displays a dialog 
        box for the user to enter the new event name and updates the event in the events dictionary. 
        The event listbox is reloaded to reflect the changes. If no event is selected, it displays 
        an informational message.
        """
        # Get the index of the selected event
        selected_index = self.event_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            event_time = list(self.events[self.selected_date].keys())[selected_index]
            event_name = self.events[self.selected_date][event_time]

            # Pop-up dialog to let the user edit the event name
            new_name = simpledialog.askstring("Edit Event", "Enter new event name:", initialvalue=event_name)
            if new_name:
                # Update event name
                self.events[self.selected_date][event_time] = new_name

                # load event
                self.load_events(self.selected_date)
        else:
            messagebox.showinfo("Info", "Please select an event to edit.")

    def set_selected_date(self, date):
        """
        Set the selected date and refresh the event list.
        This method updates the selected date in the event management module and refreshes 
        the UI to display events for the new date.

        Args:
            date: The new date to be set, represented as a datetime.date object.
        """

        # Set the selected date and refresh the UI
        self.selected_date = date
        self.date_label.config(text=f"Events for: {self.selected_date.strftime('%Y-%m-%d')}")
        self.load_events(self.selected_date)

    def scrape_f1_schedule(self):
        """
        Scrape Formula 1 race schedule from a web page.
        This method retrieves the Formula 1 race schedule from an external website,
        parses the data, and updates the calendar with the events.
        """

        url = 'https://espnpressroom.com/us/formula-1-2018-world-championship-schedule-on-espn-networks/'
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # extract_f1_schedule
            f1_schedule = extract_f1_schedule(soup)
            for event_info in f1_schedule:
                # The date format is 'Friday, March 3, 2023'
                # event_date = datetime.strptime(event_info['date'], '%A, %B %d, %Y').date()
                # Adding events to the calendar
                self.add_event_from_scrape(event_info['date'], event_info['session'], event_info['time'])
        else:
            print("Failed to retrieve the web page. Status code:", response.status_code)


def extract_f1_schedule(soup):
    """
    Extract the Formula 1 schedule from a BeautifulSoup object.

    Args:
        soup: BeautifulSoup object containing parsed HTML from the F1 schedule web page.

    Returns:
        A list of dictionaries, each containing information about a scheduled event.
    """

    # Initialize variables to hold spanning titles
    current_title = None
    schedule = []

    # find all rows
    table_rows = soup.find_all('tr')
    for row in table_rows:
        # find all cells in current row
        cells = row.find_all('td')

        # Check if it's a row with a title (assuming the title row 
        # has the 'rowspan' attribute)
        if cells and 'rowspan' in cells[0].attrs:
            current_title = cells[1].get_text(strip=True)

        if len(cells) == 5:  # Assuming the row has 5 cells
            # extract text
            session = cells[0].get_text(strip=True)
            date = cells[1].get_text(strip=True)
            time = cells[2].get_text(strip=True)

            # Add extracted information to the schedule list
            schedule.append({
                'title': current_title,
                'session': session,
                'date': date,
                'time': time
            })
    return schedule


# Main Application
class MainApplication(tk.Tk):
    """
    Main Application class for a tkinter calendar application.
    This class initializes and manages the main window of the application, 
    including the calendar module and event management module.

    Methods:
        run_scrape: Method to initiate the scraping of event data.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the MainApplication instance.
        """
        super().__init__(*args, **kwargs)
        self.title('Python Calendar Application')

        # Set the size of the window
        self.minsize(500, 400)
        self.geometry("500x500")  # Width x Height

        # Initialize modules
        self.event_management = EventManagement(self)
        self.calendar_module = CalendarModule(self, self.event_management)

        # Layout the modules
        self.calendar_module.pack(side="left", fill="both", expand=True)
        self.event_management.pack(side="right", fill="both", expand=True)

    def run_scrape(self):
        """
        Initiate the scraping of Formula 1 event data.
        """
        self.event_management.scrape_f1_schedule()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
