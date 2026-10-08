**Player Scouting System**

The Player Scouting System is a web application developed using Python and Django. The main purpose of this project is to connect football academies and scouts through a single platform.

Academies can register and manage their players, while scouts can search for players, view their details, check their skills and shortlist players based on their requirements.

**Project Overview**

The system has three main users.

Admin manages the complete system. The admin approves Academy and Scout registrations and can view and manage their information.

Academy can add players, update player information and manage their players. An academy can also add players with only basic details first and complete their evaluation later.

Scout can search for players, view detailed player information and shortlist players that match their requirements.

**Main Features**

**Admin**

Admin login

View registered Scouts and Academies

Approve or reject Scout registrations

Approve or reject Academy registrations

View certificates uploaded during registration

View Academy players

Delete Academy or Scout accounts

**Academy**

Academy registration

Certificate upload during registration

Admin approval system

Academy dashboard

Add fully evaluated players

Add unevaluated players

Update player information

Evaluate previously unevaluated players

Delete players

View and manage academy players

**Scout**

Scout registration

Admin approval system

Scout dashboard

View available academies

View academy players

Search players using different requirements

View detailed player information

Shortlist players

View shortlisted players

Remove players from shortlist

Player Management

There are two ways an Academy can add a player.

The first method is adding a complete player. The academy provides the player's basic information, physical details and skill ratings.

The second method is adding an unevaluated player. In this case, the academy only enters the player's name, age and position.

The player is initially stored as unevaluated. Later, the academy can open the player and complete the remaining information and skill evaluation.

After evaluation, the player becomes an evaluated player and can be viewed by scouts.

**Player Information**

Basic information includes:

Name

Age

Position

Preferred foot

Height

Weight

Phone number

Player photo

Player Skills

The system stores different types of football skills.

Existing performance

Speed

Shooting

Passing

Dribbling

Technical skills

Ball control

Crossing

Finishing

Heading

Physical skills

Acceleration

Agility

Balance

Stamina

Strength

Jumping

Defensive skills

Defending

Tackling

Interceptions

Marking

Mental and tactical skills

Vision

Decision making

Positioning

Composure

**Player Search**

Scouts can search for players based on different requirements.

The search system checks information such as position, preferred foot, age, height, weight and player skills.

A match percentage is calculated based on how closely the player's information matches the scout's requirements.

**Shortlisting**

Scouts can shortlist players they are interested in.

A scout can view all shortlisted players from the shortlist section and remove a player from the shortlist when required.

**Authentication**

The system has separate login access for Admin, Academy and Scout users.

Academy and Scout accounts need to be approved by the Admin before they can use the system.

The project also uses session-based login and role-based access to protect different sections of the application.

**Certificate Verification**

During registration, Scouts and Academies can upload a certificate.

The Admin can view the uploaded certificate before approving the account.

**Database Structure**

The main models used in the project are:

UserProfile
Stores additional information about registered users such as role, current club, certificate and approval status.

Academy
Stores academy information such as academy name, location, user account and approval status.

Player
Stores player information, evaluation status, academy and all player skill details.

ShortlistedPlayer
Stores the relationship between a Scout and a shortlisted player.

Project Workflow
A Scout or Academy first creates an account.

The Admin checks the registration and approves the account.

After approval, the user can log in to the system.

An Academy can add and manage players.

An Academy can either add a complete player or add an unevaluated player with basic information.

Unevaluated players can later be evaluated by the Academy.

Scouts can search for players and view their details.

Scouts can shortlist players they are interested in.

**Technologies Used**

Python

Django

SQLite

HTML

CSS

JavaScript

Bootstrap

Bootstrap Icons

Django Templates

Project Structure

Player Scouting System

manage.py

myproject

settings.py

urls.py

wsgi.py

scouts

models.py

views.py

urls.py

admin.py

migrations

templates

static

media
