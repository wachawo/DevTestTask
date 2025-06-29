Test Task:

Using a script, generate a CSV file with data on how company employees handle incoming requests:
python3 ./main.py -n 1000000

The file contains the following fields:

CALLTIME — date and time of the request
AGENT — employee name
CAMPAIGN — project
STATUS — status of the request; SALE and CCSALE are successful sales, all other statuses are considered unsuccessful
AMOUNT — sale amount

You need to develop a script that classifies employees by productivity for each workday.
The script should be able to handle files with around 500 million rows on a server with 8 GB of RAM.
You can choose any programming language and libraries.

Productivity is defined as:
The total amount and number of successful sales per hour worked.

Tasks:

1. Calculate the average productivity for each project per day.
2. Identify the top-performing employees by productivity for each project per day.
3. Determine the bottom 20% of employees by productivity for each day (regardless of project).

Additional Requirements:

* Only consider successful requests (STATUS in ['SALE', 'CREDIT']) when calculating productivity.
* An employee’s working time is the time between their first and last call on a given day.
* The result must be shared as a link to a public Git repository.

Sample CSV format:

CALLTIME            AGENT       CAMPAIGN    STATUS   AMOUNT
2025-05-12 19:25:09 agent0175   3000        DNC
2025-05-12 15:44:55 agent0514   5000        BUSY
2025-05-12 10:14:16 agent0915   2000        BUSY
2025-05-12 20:41:15 agent0591   2000        NI
2025-05-12 18:20:27 agent0931   2000        SALE      20
...
2025-05-16 12:06:43 agent0095   1000        DNC
2025-05-16 16:01:02 agent0941   5000        SALE      60
2025-05-16 10:27:45 agent0735   9000        SALE      50
2025-05-16 19:53:15 agent0545   2000        DNC
2025-05-16 20:50:38 agent0257   2000        DNC

[1000000 rows × 5 columns]
