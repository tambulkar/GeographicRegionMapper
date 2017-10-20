from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from matplotlib import pyplot as plt
import time
import json

StateName="California" #State to be used for processing
districtsFile = "./input/districts115.geojson" #Coordinates for the districts
inputFile = open("./input/inputList.txt","r") #Coordinates of points to be sorted
outputFilePoints = open("./output/pointOutput_" + StateName + ".txt","w+") #Output file with each point and the assigned district
outputFileDistricts = open("./output/districtOuput_" + StateName + ".txt","w+") #Output file with districts and number of points within the district

startTime = time.asctime(time.localtime(time.time())) #To track how long code runs
print ("Start Time: " + startTime)

def stateToFIPS(state):
    switcher = {
        "Alabama":"01",
        "Alaska":"02",
        "Arizona":"04",
        "Arkansas":"05",
        "California":"06",
        "Colorado":"08",
        "Connecticut":"09",
        "Delaware":"10",
        "District of Columbia":"11",
        "Florida":"12",
        "Georgia":"13",
        "Hawaii":"15",
        "Idaho":"16",
        "Illinois":"17",
        "Indiana":"18",
        "Iowa":"19",
        "Kansas":"20",
        "Kentucky":"21",
        "Louisiana":"22",
        "Maine":"23",
        "Maryland":"24",
        "Massachusetts":"25",
        "Michigan":"26",
        "Minnesota":"27",
        "Mississippi":"28",
        "Missouri":"29",
        "Montana":"30",
        "Nebraska":"31",
        "Nevada":"32",
        "New Hampshire":"33",
        "New Jersey":"34",
        "New Mexico":"35",
        "New York":"36",
        "North Carolina":"37",
        "North Dakota":"38",
        "Ohio":"39",
        "Oklahoma":"40",
        "Oregon":"41",
        "Pennsylvania":"42",
        "Puerto Rico":"43",
        "Rhode Island":"44",
        "South Carolina":"45",
        "South Dakota":"46",
        "Tennessee":"47",
        "Texas":"48",
        "Utah":"49",
        "Vermont":"50",
        "Virgina":"51",
        "Washington":"53",
        "West Virginia":"54",
        "Wisconsin":"55",
        "Wyoming":"56"
    }
    return switcher[state]

fipsID = stateToFIPS(StateName)

def createDistrictPolygonDictionary(districtInput):

    districtPolygonDictionary={} #Initialize polygon dictionary
    with open(districtInput) as json_data: #Load district file as JSON
        originalDistrictFile = json.load(json_data)
        districtCoordinatesDictionary = {} #Initialize dictioanry to store coordinates which will later be put in polygon constructor

        for line in originalDistrictFile["features"]: #Cycle through each line in the district shapefile...each line is different district

            state = str(line["properties"]["STATEFP"]) #Store the state in each line

            if state == fipsID: #Compare the state of the line to the state we are sorting in
                district = int(line["properties"]["CD115FP"]) #Store the district of the current line

                if line["geometry"]["type"] == "Polygon": #If the coordinates represent a polygon
                    coordinates = str(line["geometry"]["coordinates"]).replace("[", "").replace("]", "").replace(" ", "")
                    districtCoordinatesDictionary[district] = coordinates #Store coordinates as a key,value pair with their respective district number

                else: #If the coordinates represent a multiPolygon
                    coordinatesSuperList=[] #Initialize list to store lists of coordinates

                    for poly in line["geometry"]["coordinates"]: #Cycle through each set of coordinates in the multipolygon
                        coordinates=str(poly).replace("[", "").replace("]", "").replace(" ", "") #Convert coordinates into form "x1,y1,x2,y2,...,xn,yn"
                        coordinatesSuperList.append(coordinates) #Store coordinates in form ["x1,y1,x2,y2,..,xn,yn","x1,y1,x2,y2,..,xn,yn",.....,"x1,y1,x2,y2,..,xn,yn"]

                    districtCoordinatesDictionary[district] = coordinatesSuperList #Store coordinates as a key,value pair with their respective district number

        for district, coordinates in districtCoordinatesDictionary.items(): #Iterate through districtCoordinatesDictionary

            if isinstance(coordinates,str): #Check for polygon case
                listOfCoordinates = coordinates.split(",") #Split coordinates from string into list of coordinates [x1,y1,x2,y2,...,xn,yn]
                coordinatePointList = [] #Initialize list to hold points instead of individual coordinates

                n = 0
                while n < len(listOfCoordinates): #Iterate through 2 elements of list at time
                    coordinatePointList.append(Point(float(listOfCoordinates[n+1]), float(listOfCoordinates[n]))) #Create point objects with every lat&long
                    n = n + 2

                districtPolygonDictionary[district] = Polygon([[p.x,p.y] for p in coordinatePointList]) #Create Polygon object using every point object in coordinatePointList

            else: #Check for multiPolygon Case
                polygonList=[] #Initialize list to store all polygons in multipolygon

                for subCoordinates in coordinates: #Iterate through each list of coordinates...each list represents one polygon in the overall multipolygon
                    listOfCoordinates = subCoordinates.split(",") #Split coordinates from string into list of coordinates [x1,y1,x2,y2,...,xn,yn]
                    coordinatePointList = [] #Initialize list to hold points instead of individual coordinates

                    n = 0
                    while n < len(listOfCoordinates): #Iterate through 2 elements of list at time
                        coordinatePointList.append(Point(float(listOfCoordinates[n + 1]), float(listOfCoordinates[n]))) #Create point objects with every lat&long
                        n = n + 2

                    polygonList.append(Polygon([[p.x,p.y] for p in coordinatePointList])) #Create Polygon object using every point object in coordinatePointList and add to the list of polygons in the multiPolygon

                districtPolygonDictionary[district]=MultiPolygon(polygonList) #Create multipolygon from list of polygons
    return districtPolygonDictionary

def createPointDictionary(inputFile):

    inputFileList=inputFile.readlines() #Convert file to list of strings
    IDListFormatted=[]
    coordinatesList = []  #Initialize list to store just the coordinates

    for line in inputFileList: #Iterate through each line in the inputFile
        coordinates = (((line.split(':'))[1]).split('\n'))[0].split(",") #Split on comma to get a string "lat,long" then split on new line to get only the numbers
        coordinatesList.append(coordinates) #append strings in the format [[lat,long],[lat,long],...,[lat,long]
        id = (line.split(':'))[0] #Store id
        IDListFormatted.append(id) #Store id's in a list

    for coordinate in coordinatesList: #Iterate through each coordinate in coordinatesList
        try: #Make sure values are numbers
            coordinate[0] = float(coordinate[0])
            coordinate[1] = float(coordinate[1])
        except ValueError:
            coordinate[0] = "null"
            coordinate[1] = "null"

    pointDictionary = {} #Initialize Dictionary to store points

    n=0
    for coordinate in coordinatesList: #Iterate through coordinatesList
        try:
            pointDictionary[IDListFormatted[n]] = Point(coordinate[0], coordinate[1]) #Store points in dictionary with respective id as key,value pair
        except TypeError: #In case values were stored as null in step above
            pointDictionary[IDListFormatted[n]] = "Invalid"
        n+=1

    return pointDictionary


def countDistricts(districtPolygonDictionary,customerPointDictionary):

    districtCounter={} #Initialize district counter dictionary
    outputDictionary={} #Initialize outputDictionary
    processingCount = 1 #To track progress of program while running

    for district,polygon in districtPolygonDictionary.items(): #Iterate through districts
        print("Processing:" + str(processingCount) + "/" + str(len(districtPolygonDictionary))) #Track progress
        print("Processing District " + str(district)) #Track progress
        counter=0

        for id,point in customerPointDictionary.items(): #Iterate through customer dictionary
            try:
                if polygon.contains(point): #if point is in district
                    counter = counter+1 #Increment count of points in current district
                    outputDictionary[id] = str(point.x) + "," + str(point.y) + " : " + str(fipsID) + " : " + str(district) #Store point in dictionary with district it is in

                elif point.touches(polygon): #if point is on district border
                    counter = counter + 1 #Increment count of points in current district
                    outputDictionary[id] = str(point.x) + "," + str(point.y) + " : " + str(fipsID) + " : " + str(district) #Store point in dictionary with district it is in

                else: #Point not in district
                    try:
                        if not (isinstance(outputDictionary[id],str)):
                            outputDictionary[id] = str(point.x) + "," + str(point.y) + " : Not Found"
                    except KeyError:
                        outputDictionary[id] = str(point.x) + "," + str(point.y) + " : Not Found"
            except AttributeError: #In case value was stored as null
                outputDictionary[id] = "Invalid"

        districtCounter[district]=counter #Save counter with key of district number
        processingCount=processingCount+1 #Track program progress

    return districtCounter,outputDictionary

def plotPolygon(x,y,title): #Plot district polygon with list of x and y coordinates
    fig = plt.figure(1, figsize=(5, 5), dpi=90)
    ax = fig.add_subplot(111)
    ax.plot(x, y, color='#6699cc', alpha=0.7,
            linewidth=3, solid_capstyle='round', zorder=2)
    ax.set_title(title)
    plt.show()

districtPolygonDictionary = createDistrictPolygonDictionary(districtsFile) #Create districtPolygonDictionary
pointDictionary = createPointDictionary(inputFile) #Create pointDictionary
districtCounter,outputDictionary=countDistricts(districtPolygonDictionary,pointDictionary) #Count number of points in each district and sort each point to a district

for id,location in outputDictionary.items(): #Iterate through outputDictionary
    outputFilePoints.write(id+" : "+location+"\n") #Write output to file

for district,count in districtCounter.items(): #Iterate through districtCounter
    outputFileDistricts.write(str(district)+" : "+str(count)+"\n") #Write output to file

outputFileDistricts.close()
outputFilePoints.close()

endTime = time.asctime( time.localtime(time.time()) ) #To track how long code runs
print ("End Time: " + endTime)




