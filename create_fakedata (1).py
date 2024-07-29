import csv
import random

'''Time Stamp	Heart Rate	Respiration Rate	Location
      0	         60-120bpm	    10-20 bpm	    (x,y)'''

#Define duration of recording (seconds) by length of Time

time = 86400 #one day seconds

time_stamps = [i for i in range(time)]

heart_rates = []
respiration_rates = []

#location xy by room? - coords for each room
for t in time_stamps:
    if 0 <= t < 25200: #12am - 7am
        heart_rates.append(random.randint(50,65))
        respiration_rates.append(random.randint(10,12))
    elif 25200 <= t < 36000: #7am - 10 am
        heart_rates.append(random.randint(65,90))
        respiration_rates.append(random.randint(12,16))
    elif 36000 <= t < 39600: #10am - 11am exercise
        heart_rates.append(random.randint(90,120))
        respiration_rates.append(random.randint(16,20))
    else: #11am - 12am
        heart_rates.append(random.randint(65,90))
        respiration_rates.append(random.randint(13,16))

locations = []
for i in range(time):
    templist = []
    templist.append(random.randint(-100,100))
    templist.append(random.randint(-100,100))
    locations.append(templist)



with open('Vital Signs Data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time','Heart Rate','Respiration Rate','Location'])
    for i in range(time):
        row = [time_stamps[i],heart_rates[i],respiration_rates[i],locations[i]]
        writer.writerow(row)
print("Done")