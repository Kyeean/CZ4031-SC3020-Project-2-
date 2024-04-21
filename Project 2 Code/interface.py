import os
from tkinter import *
from tkinter import font, messagebox
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import explain
from PIL import ImageTk, Image
from ttkbootstrap.tableview import Tableview
import traceback

# Fonts
FONT_TITLE = ("Helvetica", 18)
FONT_NORMAL = ("Helvetica", 12)
FONT_BOLD = ("Helvetica BOLD", 14)
FONT_UNDERLINE = ("Helvetica UNDERLINE", 12)

class Application(ttk.Window):
    def __init__(self, master=None):
        '''
         Initialize the Tkinter Application.
        '''
        super().__init__(self)

        # Set the title and dimensions of the window
        self.title("Database System Principles Project 2")
        self.geometry("1920x1080")
        self.generate_UI()
        self.configure(bg='#2C3143')

    def generate_UI(self):
        '''
        Generate the UI
        '''
        
        #Title
        s = ttk.Style()
        s.configure('TFrame', background='#2C3143')
        self.window_container = ttk.Frame(self, style='TFrame')
        self.window_container.pack(fill=tk.BOTH)
        self.app_label = ttk.Label(self.window_container, text="CZ4031/SC3020 Project 2", font=FONT_TITLE, anchor=CENTER, background="#2C3143", foreground='white')
        self.app_label.pack(fill=tk.X, pady=[30, 30])

        # Horizontal line below title
        s.configure("Line.TSeparator", background="black")
        separator = ttk.Separator(self.window_container, orient='horizontal', style="Line.TSeparator")
        separator.pack(fill='x')

        # Create Panedwindow
        panedwindow = PanedWindow(self, orient=HORIZONTAL, bd=4, bg="#1C1C1E")
        panedwindow.pack(fill=BOTH, expand=True)

        # Frame for left
        self.window_container_left = ttk.Frame(panedwindow, width=250, height=400)
        self.window_container_left.pack(fill=tk.BOTH, side=LEFT)

        # Frame for right
        self.window_container_right = ttk.Frame(panedwindow, width=250, height=400)
        self.window_container_right.pack(fill=tk.BOTH, side=RIGHT)

        panedwindow.add(self.window_container_left)
        panedwindow.add(self.window_container_right)

        # Left window

        # Query input

        self.query_input_container = ttk.Frame(self.window_container_left,borderwidth=0)
        self.query_input_container.pack(pady=10,fill=tk.BOTH)

        my_label = Label(self.query_input_container, text="Query Input:", font=FONT_NORMAL)
        my_label.configure(background='#2C3143', foreground='white')
        my_label.pack(padx=10, pady=10, anchor=NW, side=LEFT)

        self.text_container = ttk.Frame(self.window_container_left, borderwidth=0)
        self.text_container.pack(fill=X)
        self.queryInput_textbox = Text(self.text_container, width=70,height=30, wrap="word")
        self.queryInput_textbox.pack(pady=10, padx=10, fill=X)

        #Submit button

        self.submit_button = ttk.Button(self.window_container_left, text="Submit", command=self.submit_queries, bootstyle="success", padding=(100,15))
        self.submit_button.pack(pady=20)

        # Right Window

        s.configure("Custom.TNotebook", tabposition="n", background="#2C3143", bordercolor="#2C3143")
        s.configure("Custom.TNotebook.Tab", background="#6C788B", foreground='white')
        s.map("Custom.TNotebook.Tab", background=[("selected", "#2C3143")], foreground=[("selected", "white")])

        self.tabs_holders = ttk.Notebook(self.window_container_right, style="Custom.TNotebook")
        self.tabs_holders.pack(fill=tk.BOTH, padx=40, pady=20)

        # Query Plan Tab
        
        self.query_container = ttk.Frame(self.tabs_holders, borderwidth=0)
        self.query_container.pack(fill=tk.BOTH)
        self.tabs_holders.add(self.query_container, text="Query Plan")
        self.postgresql_subframe = ttk.Frame(self.query_container, borderwidth=0)
        self.postgresql_query_plan_label = Label(self.postgresql_subframe, text="Query Execution Plan", font=FONT_UNDERLINE)
        self.postgresql_query_plan_label.configure(background='#2C3143', foreground='white')
        self.postgresql_query_plan_label.pack(padx=0, pady=(10,0), expand=True, fill=BOTH)
        self.postgresql_query_plan_text = Text(self.postgresql_subframe, width=40, height=80, wrap="word")
        self.postgresql_query_plan_text.pack(padx = 10, pady= 10, expand=True, fill=BOTH)
        self.postgresql_subframe.pack(expand=True, fill=BOTH, side=LEFT)

        # Analysis Tab

        self.analysis_container = ttk.Frame(self.tabs_holders, borderwidth=0)
        self.analysis_container.pack(fill=tk.BOTH)
        self.tabs_holders.add(self.analysis_container, text="Analysis")

        self.analysis_label = Label(self.analysis_container, text="What has changed and why:", font=FONT_NORMAL)
        self.analysis_label.configure(background='#2C3143', foreground='white')
        self.analysis_label.pack(pady=20)
        self.analysis_text = Text(self.analysis_container, width=70, height=50, wrap="word")
        self.analysis_text.pack(pady=10, padx=10, expand=True, fill=BOTH)

        # Output Tab

        self.sql_output_container = ttk.Frame(self.tabs_holders, borderwidth=0)
        self.sql_output_container.pack(fill=tk.BOTH)
        self.tabs_holders.add(self.sql_output_container, text="Output")

        # Login ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        self.login_window = Toplevel(self.window_container)
        self.login_window.title("Login")
        self.login_window.grab_set()
        width = 270
        height = 270
        screen_width = self.window_container.winfo_screenwidth()
        screen_height = self.window_container.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width / 2)
        y_coordinate = (screen_height / 2) - (height / 2)
        self.login_window.geometry("%dx%d+%d+%d" % (width, height, x_coordinate, y_coordinate))

        # Create the login form
        self.host_label = ttk.Label(self.login_window, text="Host:")
        self.host_entry = ttk.Entry(self.login_window)
        self.host_entry.insert(0, "localhost")

        self.port_label = ttk.Label(self.login_window, text="Port:")
        self.port_entry = ttk.Entry(self.login_window)
        self.port_entry.insert(0, '5432')

        self.database_label = ttk.Label(self.login_window, text="Database:")
        self.database_entry = ttk.Entry(self.login_window)
        self.database_entry.insert(0,'TPC-H')

        self.user_label = ttk.Label(self.login_window, text="User:")
        self.user_entry = ttk.Entry(self.login_window)
        self.user_entry.insert(0, 'postgres')

        self.password_label = ttk.Label(self.login_window, text="Password:")
        self.password_entry = ttk.Entry(self.login_window, show="*")
        self.password_entry.insert(0,'12345')

        self.login_button = ttk.Button(self.login_window, text="Login", command=self.login)

        # Lay out the login form using grid
        self.host_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        self.port_label.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.port_entry.grid(row=1, column=1, padx=5, pady=5, sticky=W)

        self.database_label.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.database_entry.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        self.user_label.grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.user_entry.grid(row=3, column=1, padx=5, pady=5, sticky=W)

        self.password_label.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.password_entry.grid(row=4, column=1, padx=5, pady=5, sticky=W)

        self.login_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Focus the username entry widget
        self.host_entry.focus_set()

        # Bind the <Return> key to the login method
        self.login_window.bind("<Return>", self.login)
        self.login_window.protocol("WM_DELETE_WINDOW", lambda: self.destroy())

    def login(self, event=None):
        '''
         Connects to the database. This is called when the user clicks the login button.
        '''
        self.configList = [self.host_entry.get(),
                           self.port_entry.get(),
                           self.database_entry.get(),
                           self.user_entry.get(),
                           self.password_entry.get()]
        try:
            preprocessor = explain.Preprocessing(self.configList)
            messagebox.showinfo("Login", "You are now logged in!")
            self.login_window.destroy()
        except Exception as e:
            messagebox.showinfo("Failed", "Login failed")

    def submit_queries(self):
        '''
        Submit query
        '''
        self.submit_button.configure(state=DISABLED)

        # Get the SQL queries from user input and clean queries
        self.query_input = self.queryInput_textbox.get('1.0', 'end-1c')
        self.query_input = self.query_input.strip()
        self.query_input = self.query_input.replace('\n', ' ')
        
        self.illustrating_changes(self.query_input)

        self.submit_button.config(state="normal")

    def illustrating_changes(self, query):
        '''
        Display the query plans and analysis
        '''
        
        preprocessor = explain.Preprocessing(self.configList)
        isValid = self.query_validation(query, preprocessor)
        title_font = font.Font(family="Helvetica", size=18, weight="bold")
        body_font = font.Font(family="Helvetica", size=14)

        # If input query is valid
        if isValid:
            self.analysis_text.config(state="normal")
            self.analysis_text.delete('1.0', END)
            try:
                QueryPlan = preprocessor.get_query_plan(self.query_input)
            except Exception as e:
                messagebox.showerror("showwarning", "Please input a working SQL Query!")
                return
            
            for widget in self.sql_output_container.winfo_children():
                widget.destroy()

            self.table_button = ttk.Button(self.sql_output_container, text="Generate Table", command=lambda: self.tableTab(self.query_input, self.sql_output_container), bootstyle="secondary")
            self.table_button.pack(pady=20, expand=True)

            try:
                if os.path.isdir("img"):
                    graph_path = "img/QueryPlan"
                    image_path = "img/QueryPlan.png"
                else:
                    graph_path = "QueryPlan"
                    image_path = "QueryPlan.png"

                graphGenerator = explain.GraphGeneration(QueryPlan)
                graphGenerator.generate_graph(graph_path)

                self.postgresql_query_plan_text.config(state="normal")
                self.postgresql_query_plan_text.delete('1.0', END)

                imgQuery = Image.open(image_path)

                gui_width = self.postgresql_query_plan_text.winfo_width() - 50
                gui_height = self.postgresql_query_plan_text.winfo_height() - 50

               

                w, h = imgQuery.size
                x_offset = max((gui_width - w) // 2,0)
                y_offset = max((gui_height - h) // 2,0)
                if w > gui_width or h > gui_height:
                    ratio = min(gui_width/w, gui_height/h)
                    new_size = (int(w * ratio), int(h * ratio))
                    imgQuery = imgQuery.resize(new_size)

                # Insert image for the query plan
                self.query_img = ImageTk.PhotoImage(imgQuery)
                self.postgresql_query_plan_text.image_create(END, image=self.query_img,padx=x_offset, pady=y_offset)
                self.postgresql_query_plan_text.config(state=DISABLED)

                self.analysis_text.config(state="normal")
                self.analysis_text.insert(END, "Query Plan Analysis:\n", ("title",))

                searchFunction = explain.SearchNode()
                joinResults, scanResults = searchFunction.searchJoin(QueryPlan)
                self.printJoin(joinResults, scanResults, self.analysis_text)

                cost = explain.CalculateCost().printCost(QueryPlan)
                self.analysis_text.insert(END, cost, ("body",))

                analysisList = self.printAnalysis(query)
                for timeTaken in analysisList:
                    self.analysis_text.insert(END, "\n Actual " + timeTaken + "\n", ("body",))

                self.analysis_text.tag_configure("title", font=title_font, underline=True)
                self.analysis_text.tag_configure("body", font=body_font)
                self.analysis_text.config(state=DISABLED)

            except Exception as e:
                messagebox.showinfo("Warning")
                print(traceback.format_exc())

    def printAnalysis(self, query):

        db = explain.DBConnection(self.configList)
        analysis = db.execute_analyse(query)
        timeTakenstr = []
        for i in analysis:
            for j in i:
                k = str(j)
                if k.__contains__("Planning Time") == True or k.__contains__("Execution Time") == True:
                    timeTakenstr.append(k)
        return timeTakenstr
                 
    def printJoin(self, join_dict, scan_dict, container):
        '''
         Prints out the joins in a query.
         
         Args:
         	 join_dict: Dictionary with the joins as keys and the relation as values
         	 scan_dict: Dictionary with the relations as keys and the relation as values
         	 container: Container to insert the relations into.
         
         Returns: 
         	 The string that is displayed in the Analysis tab
        '''

        body_font = font.Font(family="Helvetica", size=12)
        container.config(state="normal")
        joinString = ""
        # Concatenating the strings together
        for join in join_dict:
            try:
                joinString = f"\n{join[:-1]} was used between '{join_dict[join][0]}'({scan_dict[join_dict[join][0]]}) and '{join_dict[join][1]}'({scan_dict[join_dict[join][1]]})\n"
                container.insert(END, joinString, ("body",))
            except Exception as e:
                try:
                    joinString = f"\n{join[:-1]} was used between '{join_dict[join][0]}'({scan_dict[join_dict[join][0]]}) and '{join_dict[join][1]}'\n"
                    container.insert(END, joinString, ("body",))

                except Exception as e:
                    joinString = f"\n{join[:-1]} was used between '{join_dict[join][0]}' and '{join_dict[join][1]}'\n"
                    container.insert(END, joinString, ("body",))

        if(joinString == ""):
            joinString = "\nNo joins are present in this query\n"
            container.insert(END, joinString, ("body",))

        self.analysis_text.tag_configure("body", font=body_font)

    def query_validation(self, query, preprocessor):
        '''
        Validates the queries.
        '''

        validation = preprocessor.validate_query(query)

        if validation["error"] == True:
            messagebox.showerror("Warning", validation["error_message"])
            return False
        return True
    

    def tableTab(self, query, container):
        '''
        Create table based on query. 
        
        Args:
            query: The query to use for the execution. It can be a string or a list of strings.
            container: The container that will contain the table. This container must be a tab
        '''

        # Clear SQL queries in container
        for child in container.winfo_children():
            child.destroy()  # Clean up sql output
        preprocessor = explain.Preprocessing(self.configList)

        output, columns = preprocessor.get_query_results(query)

        # Create table in container
        if (output is None or (len(output) == 0)):
            ttk.Label(container, text="No results matching the query provided.", font=FONT_BOLD, anchor=CENTER, background="#2C3143", foreground='white').pack(pady=20, fill=tk.X)

        else:
            self.createTableOutput(output, columns, container)
            


    def createTableOutput(self, output, columns, container):
        '''
         Create table with output from get_query_results. 
         
         Args:
         	 output: List of rows of data
         	 columns: List of column headers to be displayed in table
         	 container: Container to insert the created table into
        '''

        column_data, row_data = [], []

        # Add a header column to the columnData
        for header in columns:
            header_column = {"text": f"{header}", "stretch": True}
            column_data.append(header_column)

        # Append the output to rowData
        for row in output:
            row_data.append(row)

        # Create table view
        table = Tableview(
            master=container,
            coldata=column_data,
            rowdata=row_data,
            autoalign=True,
            autofit=True,
            paginated=True,
            pagesize=40,
            searchable=True,
            stripecolor=(None, None)
        )

        table.pack(padx=10, pady=10, expand=True, fill=BOTH)














