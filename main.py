import tkinter as tk
import calendar
from datetime import datetime, date
# import datetime
from tkinter import messagebox, simpledialog
import requests
from bs4 import BeautifulSoup

# Calendar Module
class CalendarModule(tk.Frame):
    def __init__(self, parent, event_management):
        super().__init__(parent)
        self.parent = parent
        self.event_management = event_management 
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        self.init_ui()

    def init_ui(self):
        # Create navigation frame
        self.nav_frame = tk.Frame(self)
        self.nav_frame.pack(side="top", fill="x")

        # Buttons for previous and next month
        self.prev_month_button = tk.Button(self.nav_frame, text="<", command=self.prev_month)
        self.prev_month_button.pack(side="left")

        self.next_month_button = tk.Button(self.nav_frame, text=">", command=self.next_month)
        self.next_month_button.pack(side="right")

        #Adjust the size of the navigation buttons
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
        # Go to the previous month
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.display_month(self.current_year, self.current_month)

    def next_month(self):
        # Go to the next month
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.display_month(self.current_year, self.current_month)

    def day_selected(self, day):

        selected_date = date(self.current_year, self.current_month, day)

        # 使用保存的EventManagement引用来更新事件
        self.event_management.set_selected_date(selected_date)


# Event Management Module
class EventManagement(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.events = {}  # Store events as a dict with dates as keys
        self.selected_date = datetime.now().date()  # Default selected date
        self.init_ui()

    def init_ui(self):
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
        # Clear the listbox
        self.event_listbox.delete(0, tk.END)
        # Load events for the given date
        if date in self.events:
            for event_time, event_name in sorted(self.events[date].items()):
                self.event_listbox.insert(tk.END, f"{event_time} - {event_name}")

    def add_event(self):
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
        # 将日期字符串转换为 datetime.date 对象
        # 假设 date 的格式是 "Friday, March 3, 2023"
        event_date = datetime.strptime(date, "%A, %B %d, %Y").date()

        # 添加事件到 self.events 字典
        if event_date not in self.events:
            self.events[event_date] = {}
        self.events[event_date][event_time] = event_name

        # 如果选定的日期是当前加载的日期，则重新加载事件
        if event_date == self.selected_date:
            self.load_events(event_date)

    def delete_event(self):
        # 获取选中的事件索引
        selected_index = self.event_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            event_time = list(self.events[self.selected_date].keys())[selected_index]

            # 从数据结构中删除事件
            del self.events[self.selected_date][event_time]

            # 重新加载事件
            self.load_events(self.selected_date)
        else:
            messagebox.showinfo("Info", "Please select an event to delete.")

    def edit_event(self):
        # 获取选中的事件索引
        selected_index = self.event_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            event_time = list(self.events[self.selected_date].keys())[selected_index]
            event_name = self.events[self.selected_date][event_time]

            # 弹出对话框让用户编辑事件名称
            new_name = simpledialog.askstring("Edit Event", "Enter new event name:", initialvalue=event_name)
            if new_name:
                # 更新事件名称
                self.events[self.selected_date][event_time] = new_name

                # 重新加载事件
                self.load_events(self.selected_date)
        else:
            messagebox.showinfo("Info", "Please select an event to edit.")

    def set_selected_date(self, date):
        # Set the selected date and refresh the UI
        self.selected_date = date
        self.date_label.config(text=f"Events for: {self.selected_date.strftime('%Y-%m-%d')}")
        self.load_events(self.selected_date)

    def scrape_f1_schedule(self):
        url = 'https://espnpressroom.com/us/formula-1-2018-world-championship-schedule-on-espn-networks/'
        headers = {
            'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 在这里调用您之前写的提取日程的函数 extract_f1_schedule
            # print(soup)
            f1_schedule = extract_f1_schedule(soup)
            for event_info in f1_schedule:
                # 假设您的日期格式是 'Friday, March 3, 2023'
                # event_date = datetime.strptime(event_info['date'], '%A, %B %d, %Y').date()
                # 将事件添加到日历中
                self.add_event_from_scrape(event_info['date'], event_info['session'], event_info['time'])
        else:
            print("Failed to retrieve the web page. Status code:", response.status_code)

def extract_f1_schedule(soup):
    # 初始化变量来保存跨行标题
    current_title = None
    schedule = []

    # 找到所有的行
    table_rows = soup.find_all('tr')
    for row in table_rows:
        # 在当前行中找到所有单元格
        cells = row.find_all('td')
            
        # 检查是否是带有标题的行（假设标题行有 'rowspan' 属性）
        if cells and 'rowspan' in cells[0].attrs:
            current_title = cells[1].get_text(strip=True)
            
        # 根据单元格数量来判断是否是详细信息的行
        if len(cells) == 5:  # 假设详细信息行有5个单元格
            # 提取文本
            session = cells[0].get_text(strip=True)
            date = cells[1].get_text(strip=True)
            time = cells[2].get_text(strip=True)
                
            # 将提取的信息添加到日程列表中
            schedule.append({
                'title': current_title,
                'session': session,
                'date': date,
                'time': time
            })

    return schedule    

# Main Application
class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
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
        self.event_management.scrape_f1_schedule()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()