# Bookmarks
A Django app which lets user create account, Book images, follow other users and check activity feed from those users

#### User 
User can visit this website, create account, update their profile pictures, change password and login using their email IDs for username (using custom authentication)

User can add a bookmark button in the browser and bookmark the images that they like by clicking that button.

User can track other users by clicking People from the navigation tab and follow other uses to check their action feed.

By default feed from all users is visible to a user, when they start following people then feed fetches from the activity of those users.

##### Social Login
User can login from Social media account (social-auth-app-django) for now only `Google` is supported, will add `twitter` soon.


#### SSL/TLS on Localhost 
`Note` in order to allow social login you need to have `https` connection, to make it possible on local host the project installs `certifi` which creates a dummy certificate for you to run the local server on `https`.
For this we need to install `django-extension, myOpenSSL and werkzeug` packages and add django-extension in installed apps list.

Now we can run use `RunServerPlus` which will generate `ssl/tls`certificate for us.

`./manage.py runserver_plus --cert-file cert.crt`


#### Concepts

`add_to_class`is used inside the app to dynamically add attributes to existing models.

`ContentType` and `GenericForeignKey`used to form dynamic type relations between models