# book-database-alexa-skill

### An Amazon Alexa skill that manages a MySQL database of books I've read hosted on AWS RDS

---

#### Technologies/Skills Used: <b>Python, MySQL, AWS RDS, AWS Lambda, Alexa Skill Development</b>

<img src="https://github.com/jmsbutcher/book-database-alexa-skill/blob/main/images/AlexaConversation1.png">

<p>For years now, I've been keeping track of all the books I've read. I like to have a record handy of how many times I've read a book, when was the first time I read it, how many books I've read in a given year, and so on. </p>
<p>And all this time I used a (you guessed it) manually-updated Excel sheet.</p>
<p>Every time I read a new book, I would add a row.</p>
<p>Every time I re-read a book, I would update that row by incrementing the "times read" column by 1, changing the last read date, etc.</p>
<p>This was very time-consuming and messy. There were issues when my Office subscription expired and I had to move everything to the free, cloud version of Excel. Information was constantly getting lost between updates, losing track of different file versions, and simple manual input mistakes.</p>

<p>Here was a perfect opportunity to learn some SQL and Python while building a practical project to make my life a little easier. I would finally turn my disorderly old Excel sheet into a proper database.</p>
<p>And, while I was at it, why not put that database on the cloud? Perhaps using the free tier of Amazon Web Services' Relational Database Service (RDS)?</p>
<p>And - to make it even more fun - how about I get Amazon Alexa to manage that database for me through verbal commands?</p>

<br>

I thus broke down the project into 3 parts:

1. Create a good database schema for my book list
2. Put the database up on AWS RDS
3. Create the Alexa Skill 

<br>

## Part 1: MySQL Database
<p>The first question was how to structure the data. There was a problem with using only one table, as I had been doing with the Excel sheet. It was simplest to have one row per book - it was a summary; sometimes I only wanted to know if I read a specific book at least once or not.</p>
<p>But sometimes I also wanted to keep track of specific <em>readings</em> of a certain book: the date, the format, where I was, and so on. Trying to keep all this information stuffed into a single row was very clunky.</p>

<br>

### Before:

<img src="https://github.com/jmsbutcher/book-database-alexa-skill/blob/main/images/old_excel_example1.png">
<br>

<p>So I decided to make <b>two tables:</b> One to keep track of <b>books</b> and one to keep track of <b>read instances:</b></p>

```

CREATE TABLE books (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    author VARCHAR(100) NOT NULL,
    first_read_year YEAR NOT NULL,
    first_read_month VARCHAR(10) NULL DEFAULT NULL,
    unsure TINYINT NULL DEFAULT NULL,
    last_read_year YEAR NOT NULL,
    last_read_month VARCHAR(10) NULL DEFAULT NULL,
    times_read TINYINT NULL DEFAULT NULL,
    overall_format VARCHAR(20) NULL DEFAULT NULL,
    overall_context TEXT,
    PRIMARY KEY (id)
    );
    
CREATE TABLE read_instances (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    author VARCHAR(100) NOT NULL,
    read_year YEAR NOT NULL,
    read_month VARCHAR(10) NULL DEFAULT NULL,
    unsure TINYINT NULL DEFAULT NULL,
    read_format VARCHAR(20) NULL DEFAULT NULL,
    read_context TEXT,
    PRIMARY KEY (id)
	);
```

<p>Then, after much pre-processing, I converted the old book list Excel sheet into a csv file and loaded it into my test database on my root local instance.</p>
<p>I used MySQL workbench 8.0.22 for everything.</p>
<p>Now I have two different tables perfectly suited for different purposes. One is a summary and one is a detailed account preserving all information.

<br>

### After:

Books table - high level view

<img src="https://github.com/jmsbutcher/book-database-alexa-skill/blob/main/images/sql_example_books1.png">

Read instances table - low level view

<img src="https://github.com/jmsbutcher/book-database-alexa-skill/blob/main/images/sql_example_readinstances1.png">

<br>
<br>

## Part 2: Putting the database in the cloud

<p>The practical reason for putting my book database on the cloud was so that I could access it anywhere. But the main reason was simply to prove that I could do it. I wanted to gain experience using cloud services with a real project.</p>
<p>I decided to use Amazon Web Services' Relational Database Service (RDS) because it was able to work with MySQL.</p>
<p>After much googling and tutorial reading I got my database instance up and running. And after some more searching I was able to connect to it through the MySQL Workbench, create the tables, and insert all the data.</p>






















