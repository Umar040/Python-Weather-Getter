import schedule
import smtplib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from datetime import datetime
import math

cService = webdriver.ChromeService(executable_path='C:/Users/Muna2/Downloads/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service = cService)

def WeatherCheck(city):
    url="https://www.bing.com/search?q=weather+"+city #URL being checked
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    weather = soup.find('div',attrs={'class':'wtr_hourly'}).text #Get hourly data (each 3hr period)
    weather = weather[15:] #Get rid of text at the start
    hourlylist = []
    for hourlyweather in weather.split('%'):
        hourlylist.append(hourlyweather+'%')
        
    hours = []
    tempPerp = []
    currentTime = datetime.now()
    oneDay = hourlylist[:9] #Get next 24hr weather data

    for x in oneDay: #For each day
        if len(x) < 7: #For the first data point
            if (len(str(currentTime.minute))<2):#If the minute value is under 10
                hours.append(str(datetime.now().hour) +":0"+ str(datetime.now().minute)) #Add a 0 to the front and add to the first data point
            else:
                hours.append(str(datetime.now().hour) +":"+ str(datetime.now().minute))
            tempPerp.append(x)
            #^This happens as the first data point in bing is the current exact time weather before progressing to every 3 hours
        else:
            if ':' in x[:2]: #If the hour digit is under 10
                hours.append(x[:4]) #First 4 digits is the time
                tempPerp.append(x[4:]) #Everything after is temperature and rain chance
            else:
                hours.append(x[:5]) #Otherwise the next 5 digits is the time
                tempPerp.append(x[5:]) #And everything after is temperature and rain chance
    #Print to console to check results
    print("The next 24 hours:")
    [print("At "+hours[x]+" Temperature and Chance to rain is "+tempPerp[x]) for x in range(len(hours))]
    
    perpList=[] #Rain chance in next 24 hours list
    #Split the perpList element by the degree symbol then take the 2nd element which is the rain chance
    #then remove the percent sign and turn the number into an integer
    badData = []
    for x in tempPerp:
        #Added a try and except as well as removing list comprehension as bing sometimes gave bad data that joined multiple times into one crashing the program
        try:
            perpList.append(int(x.split('°')[1][:-1]))
        except ValueError:
            badData.append(x)
    rainchance = 1
    #Calculating rainchance by calculating the chance that no rain will occur at all for
    #each 3 hour period then times the result to the current result
    for x in perpList:
        rainchance = rainchance * (1-(x/100))

    #1 minus the chance of no rain at all is the chance that rain will occur at least once
    #in the 24 hours then floor division to round down the result always and divide by 100
    #to get it back into normal form ending with a result of rounding down to 2 digits
    rainchance = (1-rainchance)*100 //0.01/100
    print("\nThe Chance for rain in the next 24hrs is "+str(rainchance)+"%")
    secbody=""
    if len(badData) == 0:
        tribody=""
    else:
        tribody="Bad Data:\n"
    driver.close()
    #Using gmail for myself need to change port and email type if you use something else
    smtpLink = smtplib.SMTP('smtp.gmail.com', 587) #("Email Service", Port)
    smtpLink.starttls()
    smtpLink.login("Your_Gmail@gmail.com","Your App Password") #("Email","Password")
    subject = "Weather Reminder"
    #Creating the text body
    body = "The chance to rain is "+str(rainchance)+ "% for the next 24 hours\n"
    for x in range(len(hours)):
       secbody+="At "+hours[x]+" Temperature is "+tempPerp[x].split('°')[0]+"° and Chance to rain is "+tempPerp[x].split('°')[1]+"\n"
    for x in range(len(badData)):
        tribody+=""+badData[x]+"\n"
    body = body + secbody + tribody
    msg = "Subject:"+subject+"\n\n"+body+"\n\n From Sender"
    msg = msg.encode('utf-8')
    smtpLink.sendmail("Recipient", "Sender" , msg)
    smtpLink.quit()
    print("email sent")
    

WeatherCheck('birmingham')
