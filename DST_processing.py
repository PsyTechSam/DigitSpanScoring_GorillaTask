"""
IMPORTS
"""
import csv
import math
import pandas as pd
import numpy as np
from operator import itemgetter


"""
INITIALISE VARIABLES
"""

ID_columnName = "Participant Private ID"
ScreenName_columnName = "Screen Name"
correct_columnName = "Correct"
incorrect_columnName = "Incorrect"
value_columnName = "value"
responseScreenName = "response"

direction = "forward"
startingNBACK = 2

headerList = ["ID", "Max length", "Mean Span", "Two-error Max Length", "Two-Error total trials"]

"""
FUNCTIONS
"""

def readFile(file):
    data = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                headers = row
                line_count += 1
            else:
                data.append(row)
                line_count += 1
    return headers, data

def readIndex(headers, filter):
    filterIndex = float('NaN')
    try:
        filterIndex = headers.index(filter)
    except:
        print("Filter not in headers list - No index.")
        exit()
    return filterIndex


def seperateParticipants(data, headers):
    IDIndex = readIndex(headers, ID_columnName)
    firstRow = data[0]
    currentID = firstRow[IDIndex]
    pp_dataLists = []
    pp_list = []
    currentRow = 0
    for row in data:
        ppID = row[IDIndex]
        if ppID == currentID:
            pp_list.append(row)
        try:
            nextRow = data[currentRow + 1]
            nextID = nextRow[IDIndex]
            if nextID != currentID:
                pp_list.append(row)
                pp_dataLists.append(pp_list)
                pp_list = []
                currentID = nextID
            currentRow += 1
        except:
            pp_dataLists.append(pp_list)
            break
    return pp_dataLists

def calculateMaxLength(data_ppLists, headers):
    maxLengths = []
    IDIndex = readIndex(headers, ID_columnName)
    correctIndex = readIndex(headers, correct_columnName)
    screenIndex = readIndex(headers, ScreenName_columnName)
    valueIndex = readIndex(headers, value_columnName)
    for participant in data_ppLists:
        pp_max = []
        currentMax = 0
        firstRow = participant[0]
        ID = firstRow[IDIndex]
        pp_max.append(ID)
        for row in participant:
            if row[screenIndex] == responseScreenName and row[correctIndex] == "1":
                responseValue = row[valueIndex]
                responseLength = len(responseValue)
                if responseLength > currentMax:
                    currentMax = responseLength
        pp_max.append(currentMax)
        maxLengths.append(pp_max)
    return maxLengths

def calculateMeanSpans(data_ppLists, headers):
    meanSpans = []
    IDIndex = readIndex(headers, ID_columnName)
    correctIndex = readIndex(headers, correct_columnName)
    screenIndex = readIndex(headers, ScreenName_columnName)
    valueIndex = readIndex(headers, value_columnName)
    incorrectIndex = readIndex(headers, incorrect_columnName)
    for participant in data_ppLists:
        pp_meanSpan = []
        firstRow = participant[0]
        ID = firstRow[IDIndex]
        pp_meanSpan.append(ID)
        pp_trials = []
        for row in participant:
            if row[screenIndex] == responseScreenName:
                responseValue = row[valueIndex]
                responseLength = len(responseValue)
                trial = [row[correctIndex], row[incorrectIndex], responseLength]
                pp_trials.append(trial)
        meanSpan_Base = startingNBACK - 0.5
        counter = startingNBACK + 1
        while counter < 16:
            counterCorrect = 0
            counterIncorrect = 0
            counterTotal = 0
            for trial in pp_trials:
                if trial[2] == counter:
                    counterCorrect = counterCorrect + int(trial[0])
                    counterIncorrect = counterIncorrect + int(trial[1])
                    counterTotal = counterTotal + 1
            try:
                addition = (counterCorrect/(counterCorrect + counterIncorrect))
                meanSpan_Base = meanSpan_Base + addition
            except:
                meanSpan_Base = meanSpan_Base
            counter += 1
        pp_meanSpan.append(meanSpan_Base)
        meanSpans.append(pp_meanSpan)
    return meanSpans


def calculateTEmeasures(data_ppLists, headers):
    TEmeasures = []
    IDindex = readIndex(headers, ID_columnName)
    correctIndex = readIndex(headers, correct_columnName)
    incorrectIndex = readIndex(headers, incorrect_columnName)
    screenIndex = readIndex(headers, ScreenName_columnName)
    valueIndex = readIndex(headers, value_columnName)
    for participant in data_ppLists:
        TEm = []
        IncorrectInARow = 0
        lastIncorrectLength = 0
        lastCorrectLength = 0
        TT_Count = 0
        firstRow = participant[0]
        participantID = firstRow[IDindex]
        TEm.append(participantID)
        for row in participant:
            if IncorrectInARow < 2:
                if row[screenIndex] == responseScreenName:
                    TT_Count += 1
                    if row[incorrectIndex] == '1':
                        incorrect_value = row[valueIndex]
                        incorrectLength = len(incorrect_value)
                        if IncorrectInARow == 0:
                            IncorrectInARow = 1
                            lastIncorrectLength = incorrectLength
                        elif IncorrectInARow == 1:
                            if incorrectLength == lastIncorrectLength:
                                IncorrectInARow = 2
                            else:
                                IncorrectInARow = 1
                                lastIncorrectLength = incorrectLength
                    elif row[correctIndex] == '1':
                        IncorrectInARow = 0
                        correct_value = row[valueIndex]
                        CorrectLength = len(correct_value)
                        if CorrectLength > lastCorrectLength:
                            lastCorrectLength = CorrectLength
            else:
                break
        TEm.append(lastCorrectLength)
        TEm.append(TT_Count)
        TEmeasures.append(TEm)
    return TEmeasures


def compileOutputs(maxLengths, meanSpans, TEmeasures):
    output = []
    output.append(headerList)
    for row in maxLengths:
        output.append(row)
    for line in meanSpans:
        ID = line[0]
        for row in output:
            if ID == row[0]:
                row.append(line[1])
    for point in TEmeasures:
        ID = point[0]
        for row in output:
            if ID == row[0]:
                row.append(point[1])
                row.append(point[2])
    np.savetxt("DST_output.txt", output, fmt='%s', delimiter=',')

        


"""
MAIN LOOP
"""


file = 'data_exp_51687-v9_task-fpfx.csv'
headers, data = readFile(file)
data_ppLists = seperateParticipants(data, headers)
maxLengths = calculateMaxLength(data_ppLists, headers)
meanSpans = calculateMeanSpans(data_ppLists, headers)
TEmeasures = calculateTEmeasures(data_ppLists, headers)
compileOutputs(maxLengths, meanSpans, TEmeasures)
