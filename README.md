Steps to run this project

1.Create a new folder with the name of your project.
2.Click on the URL of the folder and type 'cmd' to open the command prompt of your project location.
3.Once the command prompt opens write 'pip install virtualenv' to make virtual environment. 
4.Then type ' python -m virtualenv env' and hit enter to make environment of django server.
5.After this env folder successfully enabled in your project directory.
6.Go to command prompt and locate the location '/env/scripts' and then type 'activate' to activate the virtual environment.
7.Install rest framework and django by 'pip install djangorestframework' and then 'pip install django'.
8.then 'cd..' and again 'cd..' and then run the server ,first type 'cd filesharingsystem' and then this command 'python manage.py runserver'.
9.After running the server type 'cd filesharingsystem' and type this command 'curl -X POST http://127.0.0.1:8000/api/login/ -H "Content-Type: application/json" -d "{\"username\":\"ops_user\",\"password\":\"StrongPass123\"}"'.
10.After running this command a unique client token will be generated which will be used to download the file.
11.'curl -X GET http://127.0.0.1:8000/api/client/files/ -H "Authorization: Token clienttoken123456789"' type this command to download the file after replacing the client token with the unique client token that was generated.
