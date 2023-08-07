FROM python3.9
#Naming this /app as a default
WORKDIR /app
copy . /app

#Install all the needed packages from requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

#Selecting port 8001
EXPOSE port 8001

#Giving out lines to the command line to make the project run
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
