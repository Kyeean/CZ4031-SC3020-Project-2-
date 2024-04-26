'''
Contains code for preprocessing user inputs and data used in algorithm
'''

import psycopg2, re
from graphviz import Digraph


class GraphGeneration():
    def __init__(self, qep_plan):
        '''
         Initialize the QEP visualization. This is the place to do it. You have to call __init__ in order to get the graph and node's visualization attributes
         
         Args:
         	 qep_plan: The QEP plan to
        '''
        self.qep = qep_plan
        #Pre-defining the graph and node's visualization attributes
        graph_attribute = {'bgcolor': 'white'}
        node_attribute = {'style': 'filled', 'color': 'black', 'fillcolor': 'lightblue'}
        self.graph = Digraph(graph_attr=graph_attribute, node_attr=node_attribute)
        
    
    def build_dot(self, qep, parent=None, seq=1):
        '''
        Recursive method to build the graph.
        
        Args:
            qep (dict): A dictionary representing the query execution plan.
            parent (str): ID of the parent node. Default is None.
            seq (int): Sequence of the node within the parent. Default is 1.
        '''
        node_id = str(hash(str(qep)))
        label = f"{qep['Node Type']} (Cost: {qep['Total Cost']:.2f})"
        if 'Relation Name' in qep:
            label += f"\nRelation Name: {qep['Relation Name']}"
        shape = 'box' 
        self.graph.node(node_id, label, shape=shape)
        if parent is not None:
            self.graph.edge(parent, node_id)
        if 'Plans' in qep:
            for i, plan in enumerate(qep['Plans']):
                self.build_dot(plan, node_id, i+1)

    def generate_graph(self, query_plan, format='png', view=True):
        '''
        Method to generate the graph.
        
        Args:
            query_plan (str): File path to save the generated graph image.
            format (str): Format of the generated graph image. Default is 'png'.
            view (bool): Whether to display the generated graph image. Default is True.
        
        '''
        self.build_dot(self.qep)
        self.graph.attr('node', shape='box')  # set the shape of the nodes
        self.graph.render(query_plan, format=format, view=False)
    

class Preprocessing:
    def __init__(self,configList):
        '''
        Initializes a new instance of the `Preprocessing` class.
        '''
        self.db = DBConnection(configList)

    def get_query_results(self, sql_query):
        '''
        Executes the given SQL query on the connected database and returns the resulting data and column names.

        Args:
            sql_query: The SQL query to be executed on the connected database.

        Returns:
        	query_res: The resulting data of the executed SQL query.
        	column_names: The column names of the resulting data.
        '''
        output = self.validate_query(sql_query) 
        query_res, column_names = self.db.execute(sql_query)
        return query_res, column_names
    
    
    def get_query_plan(self, sql_query):
        '''
        Generates a Query Execution Plan (QEP) for a given SQL query.

        Args:
            sql_query (str): The SQL query for which to generate a QEP.

        Returns:
            dict: A dictionary representation of the QEP generated by PostgreSQL.
                The dictionary is in JSON format and contains detailed information
                about the steps involved in executing the query.

        Raises:
            ValueError: If the provided SQL query is invalid.
        '''
        is_query_valid = self.validate_query(sql_query) 
        query_plan_res = self.db.execute("EXPLAIN (FORMAT JSON) " + sql_query)
        try:
            query_plan_res = query_plan_res[0][0][0][0]['Plan']
            
        except Exception as e:
            query_plan_res = {}
            pass
        return query_plan_res

    def validate_query(self, query):
        '''
        Checks if the given query string is valid.
        Returns:
            dict: A dictionary with the following keys:
                error (bool): Indicates if an error occurred during validation.
                error_message (str): The error message if an error occurred,
                otherwise an empty string.
        '''
        result = {"error": False, "error_message": ""}
        # checks if there's a query to execute
        if not len(query):
            result["error_message"] = "There is no query to execute."
            result["error"] = True
            return result
        # if query exists check that the query is a valid query
        isValid, error = self.db.is_query_valid(query)
        if not isValid:
            result["error_message"] = f"The query cannot be executed and is invalid. \n Error: {error}"
            result["error"] = True
            return result
            
        return result

class DBConnection:
    def __init__(self, configList):
        '''Initializes a new instance of the 'Database' class
        
        The constructor reads the database connection details from the config.json file and establishes a connection to the PostgreSQL server

        Args:
        db_config_path (str, optional): The path to the configuration file containing
        the database connection details. If not provided,
            the default value is 'config.json'
        
        Raises:
            FileNotFoundException: If the config.json file is not found
            ValueError: If the config.json fi
        
        '''
        self.host = configList[0]
        self.port = configList[1]
        self.database = configList[2]
        self.user = configList[3]
        self.password = configList[4]
        self.conn = psycopg2.connect(host=self.host, port=self.port,database=self.database,user=self.user, password=self.password)
        self.cur = self.conn.cursor()

    def execute(self, query: str):
        '''
        Executes a query on the database and returns the results.
        '''
        try:
            self.cur.execute(query)
            column_names = [description[0] for description in self.cur.description]
            query_results = self.cur.fetchall()
            return query_results, column_names
        except Exception as e:
            pass

    def execute_row_analyse(self, query: str):
        '''
        Executes the query with explain analyze on the database and returns the rows accessed
        '''
        try:
            self.cur.execute(self.cur.mogrify('explain (analyze, FORMAT json)' + query))
            analyze_result = self.cur.fetchall()  
            plan_test = []
            for item in analyze_result:
                for inner_list in item:
                    for dictionary in inner_list:
                        if 'Plans' in dictionary['Plan']:  # Check if there are nested plans
                            for plan in dictionary['Plan']['Plans']:
                                plan_test.append({'Plan Rows': plan['Plan Rows'], 'Actual Rows': plan['Actual Rows']})
                        else:
                # Trivial case with only one plan
                            plan_test.append({'Plan Rows': dictionary['Plan']['Plan Rows'], 'Actual Rows': dictionary['Plan']['Actual Rows']})
            output = ""
            for item in plan_test:
                output += f"The estimated rows to be accessed is {item['Plan Rows']}\n"
                output += f"The actual rows accessed is {item['Actual Rows']}\n"       
            return output
        except Exception as e:
            pass    
    
    def execute_analyse(self, query: str):
        '''
        Executes a query with "explain analyze" on the database and returns the actual time that it will take to execute the query.
        '''
        try:
          self.cur.execute(self.cur.mogrify('explain analyze ' + query))
          analyze_result = self.cur.fetchall()
          return analyze_result
        except Exception as e:
            pass        
    
    def compareRow(self, compareText):
        numbers = re.findall(r'\d+', compareText)
        estimated_row = int(numbers[0])
        actual_rows = int(numbers[1])
        if actual_rows < estimated_row:
            return "As the actual rows accessed is smaller than the actual rows, it can be inferred that the actual cost needed to perform this query is smaller than the estimated cost."
        elif actual_rows == estimated_row:
            return "The number of actual rows accessed is the same as the estimated number of rows. It is likely that the query is either trivial or the query plan takes on the worst case scenario"
        else:
            return "The actual cost can be inferred to be more than the estimated costs, this suggest that the query plan chosen is not the ideal query plan."
        
    
    def is_query_valid(self, query: str):    
        '''
        Fetches a single row from the database to check if the query is valid.

        Args:
            query (str): Query string that was entered by the user.
        Returns:
            boolean: true if query is valid, false otherwise.
        '''
        try:
            self.cur.execute(query)
            self.cur.fetchone()
        except Exception as e:
            print ("Exception: is_query_valid:", e)
            return False, e
        return True, None

class CalculateCost:
    def __init__(self):
        print("Calculating cost------------")

        # Calculate total cost of all nodes in plan
    def calculateCost(self, plan):
        '''
         Calculates the cost of a search. This is used to determine how much the search will take place in order to get an answer to the user
         
         Args:
         	 plan(str): The search plan that we are going to search for
         
         Returns: 
         	 totalCost(float): The total cost of the search plan as a float
        '''
        # Return the total cost of the search plan. This is used to determine the cost of a search
        totalCost = 0
        # Calculate total cost of all plans
        for i in range(len(plan)):     
            initialKey = list(plan.keys())[i]
            initialValue = plan[initialKey]
            # Add initial cost to totalCost.
            if initialKey == 'Total Cost':
                totalCost += initialValue
        return totalCost
            
    # Print cost comparison in readable format
    def printCost(self,plan):
        '''
         Prints the cost of the query.
         
         Args:
         	 Plan(str): The query that is being executed.
               
         Returns: 
         	 A string that is the overall cost of the query in a readable format.
        '''

        total_cost = self.calculateCost(plan)
        total_cost_string = f"\nThe estimated cost of this query plan is {total_cost}.\n"
        return str(total_cost_string)

class SearchNode:
    
    def __init__(self):
        print("Searching for joins------------")

    # Search for all Joins, Relations and Scan type for a plan
    def searchJoin(self,plan):
        '''
        Search for all join types, link them with their respective relations and scan type for selected plan
        
        Args:
            plan(str): plan to be searched
        
        Returns: 
            join_dict(dict): Returns all Join-Relations as a dictionary
            scan_dict(dict): Returns all Scan-Relations as a dictionary
        '''

        joinList, relationList, scanList = [],[], []
        joinOrder = 0

        # find relations to join type and put into a list as a tuple
        def findRelations(plan,joinOrder,joinList, relationList):
            '''
            Find Relations in plan and add them to joinList and relationList.
            
            Args:
                plan(str): Plan to look for relations in. It is assumed that plan ['Node Type'] is Join or NestedLoop with joinOrder
                joinOrder(int): The order which relations would be assigned to any joins
                joinList(list): List of joins 
                relationList(list): List of relations
            
            Returns:
                joinList(list): List of joins
                relationList(list): List of relations
            '''

            # This function iterates through all the plans in the plan and returns a list of nodes and their children
            for i in range(len(plan)):
                initialKey = list(plan.keys())[i]
                initialValue = plan[initialKey]

                # append all Node Type that contains Join/NestedLoop with joinOrder
                if initialKey == 'Node Type':
                
                    # Add join to joinList. append joinOrder initialValue
                    if "Join" in initialValue or "Nested Loop" in initialValue:
                        joinOrder += 1
                        joinList.append((joinOrder, initialValue))

                # append all Relation Name with joinorder and get Scan type of relations
                if initialKey == 'Relation Name':
                    relationList.append((joinOrder,initialValue))
                    scanList.append((initialValue, plan['Node Type']))
                    
                # recursively iterate through all Plans
                if initialKey == 'Plans':
                    # Find relations in initialValue.
                    for j in initialValue:
                        findRelations(j,joinOrder,joinList,relationList)
            
            return joinList, relationList
        
        joinList,relationList = findRelations(plan,joinOrder, joinList, relationList)

        # Make dictionary of Relations to Scan
        scan_dict = {}
        for relations,scan in scanList:
            scan_dict[relations] = scan
    

        # Make a join dictionary that connects Join to Relations based on joinOrder
        join_dict = {}
        joincount=0
        for join in joinList:
            tempList = []
            joincount+=1
            for relations in relationList:
                if join[0] <= relations[0]:
                    tempList.append(relations[1])
            join_dict[join[1]+str(joincount)] = tempList

        
        # Remove duplicate relations in join_dict
        for join in join_dict:

            for join2 in join_dict:
                if join == join2: 
                    continue

                if all(elem in join_dict[join2] for elem in join_dict[join]):
                    elemstring = ""
                    for elem in join_dict[join]:
                        join_dict[join2].remove(elem)
                        elemstring = elemstring + elem + ", "
                    elemstring = "[" + elemstring[:-2] + "]"
                    join_dict[join2].append(elemstring)

        return join_dict,scan_dict
    
    
