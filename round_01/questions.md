# Python


# 1. Explain Mutable vs Immutable.

Mutable means user can change the value of the data and Immutable means user is not able to change data into our datatype.

# 2. List vs Tuple.

1. list
list is a mutable architacture and user can change / edit data , remove or add elements.

list={1,2,3,4}
here we can add element via add operation

list.add (5)

-> now we can print our list
print (list)
print updated list


2. tuple
tuple is immutable architacture and user is not able to change /edit data , remove or add data.

tuple=(1,2,3)

-> now we are not able to edit , add , remove data from tuple

-> we can change our data with some things like type conversion

list=list(tuple)
list.append(4)
tuple=tuple(list)
print(tuple)

-> output =(1,2,3,4)


# 3. Decorators
-> we can use decorators to modify class and its take as input a class and connect it to other class and we can use as change our function with aur requirements.

# 4. Generators
-> we can use generators as change or terminate our functions. also we can use yeild as generators.


# 5. Lambda
-> lambda is a fuction that allows you to find power of the value
for an example

Lambda x: x * 2
print((lambda x: x * 2)(5))
-> output is 10

# 6. Context Manager
-> contaxt manager is function that can understand connection with words
-> for example we can use "drinking water" here drinking is a contaxt which is gives us to understand the user can drink water and it is purify water so we can use it as drink.

# 7. GIL
-> GIL is a global interpreted lock which is usefull for lock specific version in full project ti maintain consistancy.

# 8. Multithreading vs Multiprocessing
-> multithreading is useful for perform multiple tasks with indexing and user can process tasks as fifo (first in first out).

-> multiprocessing means user can perform multiple tasks at a time with parelal. Here user can process multiple tasks at single time and can save time for performing tasks.

# 9. Async Programming
-> Async programming can perform tasks at a same time and it can continue all tasks without any interruption.

# 10. Memory Management
-> memory management is a task for manage memory of the program. it cantain details of the memory and perform all tasks with proper memory allocation. it give refer to function , variable to user and it is useful for management of memory and program.



# Flask

# 1. Request Lifecycle
-> request lifecycle means a request is "valid  till" . here user can set request lifecycle into some seconds and can terminate the request automatically after times.

# 2. Blueprints
-> blueprint is a part of development and we can make our software with proper chunks and we can re use it into our production. it is useful for manage large projects to do less coding.

# 3. Flask Context
-> flask contaxt is useful for manage our contaxt and can gives details of our contaxt.

# 4. SQLAlchemy Session
-> SQLAlchemy Session is useful for create , manage and delete sessions.it gives security into our website or software to manage sessions and manage dashboards and other things into sessions.

# 5. Flask Login
-> flask login can give security to authenticate.we can use flask login module to create simple log in with less coding.

# 6. JWT
-> jwt is json web tokens and we can provide security with jwt.when we found token we can give access to user to perform specific tasks.

# 7. CSRF
-> csrf is a technology that can provide security to preventing malicious website.

# 8. Flask-Migrate
-> flask migration is a useful part for website and data management.we can migrate table and add missing column without manually adding it.basically it is usefull for auto ma=igration and it can auto add missing column into our database.

# 9. Alembic
-> alembic is lightweight module and we can use it as migration.

# 10. Middleware
-> middleware is a variable and it can help to pointer to add database.we can use middleware as operator between data and databse.


# Database


# 1. Second Highest Salary
SELECT Salary From employee     /employee table selected and Salary column selected

ORDER BY Salary DESC    //sorting the Salary column with highest to lowest

LIMIT 1 OFFSET 1        // here limitation is going to 1 and offset is 1 because we are finding second highest salary

# 2. Nth Highest Salary
SELECT Salary From employee     /employee table selected and Salary column selected

ORDER BY Salary DESC    //sorting the Salary column with highest to lowest
LIMIT 1 OFFSET n-1        // here limitation is going to 1 and offset is n-1 because we are finding nth highest salary

# 3. Recursive Category Tree
WITH RECURSIVE category_tree AS (
    -- 1. Anchor Member: Get all top-level root categories
    SELECT 
        id, 
        name, 
        parent_id, 
        1 AS level,
        CAST(name AS CHAR(255)) AS path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- 2. Recursive Member: Join the table back to the CTE to get children
    SELECT 
        c.id, 
        c.name, 
        c.parent_id, 
        ct.level + 1 AS level,
        CONCAT(ct.path, ' > ', c.name) AS path
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.id
)
-- 3. Final Execution: Pull the complete hierarchy
SELECT id, name, parent_id, level, path 
FROM category_tree
ORDER BY path;


# 4. Employee Hierarchy
CREATE TABLE Employees (                //creating employee table
    EmployeeID INT PRIMARY KEY,         //adding employee id
    Name VARCHAR(100),                  //adding employee name
    ManagerID INT,                      // adding manager id
    FOREIGN KEY (ManagerID) REFERENCES Employees(EmployeeID)
                                        //refered to manager id to connect employees with manager
);

# 5. Running Total
SELECT
    order_id,                           //selecting order id from 
                                        our orders table
    order_date,                         //selecting order date from 
                                        our orders table
    amount,                             //selecting order amount from 
                                        our orders table
    SUM(amount) OVER (ORDER BY order_date) AS running_total
                                        //creating total of our all orders
FROM
    orders;                             // orders table selected


# 6. Window Functions
SELECT 
    id,
    name,
    department,
    salary,
    -- 1. Row number resets for each department based on highest salary
    ROW_NUMBER() OVER (
        PARTITION BY department 
        ORDER BY salary DESC
    ) AS row_num,

    -- 2. Rank skips numbers if there is a tie in salary
    RANK() OVER (
        PARTITION BY department 
        ORDER BY salary DESC
    ) AS salary_rank,

    -- 3. Running total of salaries inside each department
    SUM(salary) OVER (
        PARTITION BY department 
        ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_department_total

FROM employees;

# 7. Pivot
SELECT 
    year,
    SUM(CASE WHEN quarter = 'Q1' THEN amount ELSE 0 END) AS Q1_Sales,
    SUM(CASE WHEN quarter = 'Q2' THEN amount ELSE 0 END) AS Q2_Sales,
    SUM(CASE WHEN quarter = 'Q3' THEN amount ELSE 0 END) AS Q3_Sales,
    SUM(CASE WHEN quarter = 'Q4' THEN amount ELSE 0 END) AS Q4_Sales
FROM sales
GROUP BY year
ORDER BY year;

# 8. Index Optimization
-> index optimization is useful for creating and managing database with proper indexing and we can access it easily.

SELECT 
    migs.avg_user_impact * (migs.user_seeks + migs.user_scans) AS estimated_score,
    mid.statement AS table_name,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns
FROM sys.dm_db_missing_index_groups mig
INNER JOIN sys.dm_db_missing_index_group_stats migs ON migs.group_handle = mig.index_group_handle
INNER JOIN sys.dm_db_missing_index_details mid ON mid.index_handle = mig.index_handle
ORDER BY estimated_score DESC;



# React
-> it is inbuilt function that allows you to create components and it is also usefull for UI interaction. Basically it is a javascript library.

# Virtual DOM
-> it is a virtual representation of our actual DOM. it is usefull for creating and managing components and it is also usefull for UI interaction.

# useMemo
-> it is a inbuilt function that allows you to memoize the value of a variable and it is also usefull for UI interaction.

# useCallback
-> it is a inbuilt function that allows you to memoize the value of a function and it is also usefull for UI interaction.

# Redux
-> it is a popular state management library for react application. it is also usefull for UI interaction.


# Context API
-> it is a inbuilt feature of react that allows you to connect components without props drilling.

# Performance
-> it is a inbuilt feature of react that allows you to optimize the performance of the application.


# Lazy Loading
-> it is a inbuilt feature of react that allows you to load the components only when they are needed.


# Suspense
->

