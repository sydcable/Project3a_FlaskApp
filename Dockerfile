#use an offical python image as the base image
FROM python:3.8-slim-buster
 
#set the working directory in the container to /app
#compy contents of the current directory into the container /app directory
#upgrade pip 
#install any needed packages
#set default commands to run when starting the container