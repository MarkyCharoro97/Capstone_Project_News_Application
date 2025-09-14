 News Platform

A Django-based news platform with role-based user management, article publishing workflow, and newsletter functionality.

Features

User Roles & Permissions

•
Readers: View articles and newsletters, subscribe to newsletters

•
Journalists: Create articles (pending editor approval), manage own articles, all reader features

•
Editors: Approve articles, create and send newsletters, all journalist and reader features

Core Functionality

•
Article Management: Create, approve, and publish articles with proper workflow

•
Newsletter System: Create targeted newsletters with audience segmentation

•
User Registration: Role-based registration with proper validation

•
Permission System: Comprehensive role-based access control

•
Responsive Design: Bootstrap-based UI that works on all devices

Installation

1.
Extract the project:

2.
Create virtual environment:

3.
Install dependencies:

4.
Run migrations:

5.
Create superuser (optional):

6.
Start development server:

7.
Access the application:
Open http://127.0.0.1:8000 in your browser

Usage

Getting Started

1.
Visit the home page and click "Register Now"

2.
Choose your role: Reader, Journalist, or Editor

3.
Complete the registration form

4.
Start using the platform based on your role

###For Journalists###

Create articles via "Create Article" button
View your articles in "My Articles" section
Articles require editor approval before publication
###For Editors###

Review pending articles in "Pending Articles"
Approve articles to make them public
Create newsletters via "Create Newsletter"
Send newsletters to targeted audiences

##For Readers##

Browse published articles
Subscribe to newsletters
Stay updated with latest content

