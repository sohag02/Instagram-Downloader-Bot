FROM python:3.9.5-buster

#Updating pip
RUN python3.9 -m pip install -U pip

COPY . .

#Installing Requirement
RUN python3.9 -m pip install -U -r requirements.txt

CMD python3 bot.py