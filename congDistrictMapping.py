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

startTime = time.asctime(time.localtime(time.time()))
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
    districtPolygonDictionary={}
    with open(districtInput) as json_data:
        originalDistrictFile = json.load(json_data)
        districtCoordinatesDictionary = {}

        for line in originalDistrictFile["features"]:
            state = str(line["properties"]["STATEFP"])
            if state == fipsID:
                district = int(line["properties"]["CD115FP"])
                if line["geometry"]["type"] == "Polygon":
                    coordinates = str(line["geometry"]["coordinates"]).replace("[", "").replace("]", "").replace(" ", "")
                    districtCoordinatesDictionary[district] = coordinates
                else:
                    coordinatesSuperList=[]
                    for poly in line["geometry"]["coordinates"]:
                        coordinates=str(poly).replace("[", "").replace("]", "").replace(" ", "")
                        coordinatesSuperList.append(coordinates)
                    districtCoordinatesDictionary[district] = coordinatesSuperList

        for district, coordinates in districtCoordinatesDictionary.items():
            if isinstance(coordinates,str):
                listOfCoordinates = coordinates.split(",")
                coordinatePointList = []
                n = 0
                while n < len(listOfCoordinates):
                    coordinatePointList.append(Point(float(listOfCoordinates[n+1]), float(listOfCoordinates[n])))
                    n = n + 2
                districtPolygonDictionary[district] = Polygon([[p.x,p.y] for p in coordinatePointList])
            else:
                polygonList=[]
                for subCoordinates in coordinates:
                    listOfCoordinates = subCoordinates.split(",")
                    coordinatePointList = []
                    n = 0
                    while n < len(listOfCoordinates):
                        coordinatePointList.append(Point(float(listOfCoordinates[n + 1]), float(listOfCoordinates[n])))
                        n = n + 2
                    polygonList.append(Polygon([[p.x,p.y] for p in coordinatePointList]))

                districtPolygonDictionary[district]=MultiPolygon(polygonList)
    return districtPolygonDictionary

def createPointDictionary(inputFile):
    inputFileList=inputFile.readlines()
    inputFileListFormatted=[]
    customerIDListFormatted=[]

    for line in inputFileList:
        coordinates = (((line.split(':'))[1]).split('\n'))[0]
        inputFileListFormatted.append(coordinates)
        id = (line.split(':'))[0]
        customerIDListFormatted.append(id)

    customerCoordinatesList=[]

    for line in inputFileListFormatted:
        customerCoordinates = line.split(",")
        customerCoordinatesList.append(customerCoordinates)

    for customer in customerCoordinatesList:
        try:
            customer[0] = float(customer[0])
            customer[1] = float(customer[1])
        except ValueError:
            customer[0] = "null"
            customer[1] = "null"

    customerPointDictionary = {}
    n=0
    for customer in customerCoordinatesList:
        try:
            customerPointDictionary[customerIDListFormatted[n]] = Point(customer[0], customer[1])
        except TypeError:
            customerPointDictionary[customerIDListFormatted[n]] = "Invalid"
        n+=1

    return customerPointDictionary


def countDistricts(districtPolygonDictionary,customerPointDictionary):
    districtCounter={}
    outputDictionary={}
    processingCount = 1
    for district,polygon in districtPolygonDictionary.items():
        print("Processing:" + str(processingCount) + "/" + str(
            len(districtPolygonDictionary)))
        print("Processing District " + str(district))
        counter=0

        for id,point in customerPointDictionary.items():
            try:
                if polygon.contains(point):
                    counter = counter+1
                    outputDictionary[id]=str(point.x)+","+str(point.y)+" : "+str(fipsID) + " : " + str(district)

                elif point.touches(polygon):
                    counter = counter + 1
                    outputDictionary[id] = str(point.x) + "," + str(point.y) + " : " + str(fipsID) + " : " + str(district)

                else:
                    try:
                        if not (isinstance(outputDictionary[id],str)):
                            outputDictionary[id] = str(point.x) + "," + str(point.y) + " : Not Found"
                    except KeyError:
                        outputDictionary[id] = str(point.x) + "," + str(point.y) + " : Not Found"
            except AttributeError:
                outputDictionary[id] = "Invalid"

        districtCounter[district]=counter
        processingCount=processingCount+1

    return districtCounter,outputDictionary

def plotPolygon(x,y,title):
    fig = plt.figure(1, figsize=(5, 5), dpi=90)
    ax = fig.add_subplot(111)
    ax.plot(x, y, color='#6699cc', alpha=0.7,
            linewidth=3, solid_capstyle='round', zorder=2)
    ax.set_title(title)
    plt.show()

districtPolygonDictionary = createDistrictPolygonDictionary(districtsFile)
pointDictionary = createPointDictionary(inputFile)
districtCounter,outputDictionary=countDistricts(districtPolygonDictionary,pointDictionary)
for id,location in outputDictionary.items():
    outputFilePoints.write(id+" : "+location+"\n")
for district,count in districtCounter.items():
    outputFileDistricts.write(str(district)+" : "+str(count)+"\n")

outputFileDistricts.close()
outputFilePoints.close()

endTime = time.asctime( time.localtime(time.time()) )
print ("End Time: " + endTime)




