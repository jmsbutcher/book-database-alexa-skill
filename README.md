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
<p>But sometimes I also wanted to keep track of specific <em>readings</em> of a certain book: the date, the format, where I was, and so on. Trying to keep all this information stuffed into a single row was very clunky. It was easy to lose information this way.</p>


### Before - 1 table:

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
<img src="https://github.com/jmsbutcher/book-database-alexa-skill/blob/main/images/aws_rds_screenshot1.png">
<p>I now had a proper book database running on the cloud. I could access it from any device using MySQL commands.</p>
<p>It was nice just to prove that I could do it, and now I had some valuable experience using AWS and SQL. However, it didn't make my life easier just yet. I still had to manually enter SQL commands whenever I finished a book or wanted to look up something. This was less convenient than simply entering values into a spreadsheet. But, with a little help from Amazon's Alexa Developer, I could make it so I wouldn't need to type in anything at all!</p>


<br>

## Part 3: Making the Alexa Skill

<p>This part was by far the most work. Each step had its own learning curve. But with lots of tinkering, testing, debugging, and amazingly helpful tutorials, I eventually got a hold of each one well enough to make my vision come alive.</p>
<p>The first part was understanding the basics of how an Alexa Skill works.</p>
<p>I first went to the <a href="https://developer.amazon.com/alexa/console/ask">Alexa Developer Console</a> and created a new skill (after creating an Amazon Developer account.)</p>
<p>From there the task was to create a custom <em>interaction model.</em> This is the thing that dictates how you're supposed to say things to Alexa, and how she is supposed to say things back to you.</p>
<p>The things you say (called <em>utterances</em>) activate certain <em>intents</em>. There are built-in intents, such as HelpIntent (activated by saying "Help") or CancelIntent (activated by saying "Never mind."). But you can also create your own custom intents. For example, one of the intents I built for this project was <b>AddReadInstanceIntent</b>, which was activated by saying one of several utterances along the lines of "Add {title} by {author} to my book database."<p>
<img src="https://github.com/jmsbutcher/book-database-alexa-skill/blob/main/images/read_instance_intent_interaction2.png" width="600" height="300">
<p>An intent may require specific information from you in order to do its job. These are called <em>slots</em>, and are indicated in utterances by curly braces. Each slot has a type, which helps Amazon Alexa better understand what you mean to say. For example, I made the {title} slot of type <em>AMAZON.book</em>, so that when I say "Nineteen Eighty-Four" in the place in the sentence denoted by {title}, Alexa has a better chance of knowing I mean the book by George Orwell, and not the two numbers 19 and 84.</p>
<img src="https://github.com/jmsbutcher/book-database-alexa-skill/blob/main/images/read_instance_intent_title_slot.png" width="600" height="800">

<br>

<p>Next, I had to write the code "behind the intents" -- the backend. In the Alexa Development Kit, this is called the lambda function. This is the code that Alexa carries out after eliciting an intent and all the information is provided.</p>
<p>When you create a custom skill, you have the option of having a basic lambda function file set up for you, hosted on the cloud via AWS Lambda, either in Python or in Node.js, or you can provide your own endpoint and backend resources.</p>
<p>I chose the Alexa-provided Python option. This was especially convenient since the Alexa Developer Console has a Code tab where you can edit the backend code and deploy it with one click.</p>

<br>

<p>At this point I needed to learn how to manage an SQL database through Python code. These two YouTube videos were excellent guides for me:<p>
- <a href="https://www.youtube.com/watch?v=3vsC05rxZ8c&list=PLwGZ7X2gMChQbGLrYP57YW2S_lrknkw1_&index=45">Tech With Tim  -  Python MySQL Tutorial - Setup & Basic Queries (w/ MySQL Connector)</a>
- <a href="https://www.youtube.com/watch?v=RerDL93sBdY&list=PLwGZ7X2gMChQbGLrYP57YW2S_lrknkw1_&index=46">KGP Talkie  -  AWS RDS with Python Tutorial | How Connect AWS RDS with Python using PyMySQL</a>
	
<p>I learned the ropes of using   by playing around and testing on Spyder (my favorite Python IDE) before trying it out in the Alexa lambda function.</p>



















