from graphics import *
import random
import copy
import math
import time


f = open("bunchOfEights2.csv", 'a')

class Pt:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def display(self, win):
        point = Point(self.x, self.y)
        cir = Circle(point, 3)
        cir.setFill("black")
        cir.draw(win)

    def clone(self):
        other = Pt(self.x, self.y)
        return other

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

class LineSegment:

    epsilon=1e-2

    def __init__(self, pt1, pt2):
        self.pt1 = pt1;
        self.pt2 = pt2;

    def signedArea(self, pt):
        pt1 = self.pt1
        pt2 = self.pt2
        return (pt2.x - pt1.x) * (pt.y - pt1.y) - (pt2.y - pt1.y) * (pt.x - pt1.x)

    def contains(self, pt):
        minx = min(self.pt1.x, self.pt2.x)
        maxx = max(self.pt1.x, self.pt2.x)
        if (pt.x >= minx and pt.x <= maxx):
            return abs(self.signedArea(pt)) <= self.epsilon
        return False;

    def orientation(self, pt):
        value = self.signedArea(pt)
        if (abs(value) <= self.epsilon):
            return 0
        elif (value < 0):
            return -1
        else:
            return 1

    def display(self, win):
        line = Line(self.pt1, self.pt2)
        line.setWidth(2)
        line.setArrow("last")
        line.draw(win)

    def intersect(self, otherLine):
        selfminx = min(self.pt1.x, self.pt2.x)
        selfmaxx = max(self.pt1.x, self.pt2.x)
        otherminx = min(otherLine.pt1.x, otherLine.pt2.x)
        othermaxx = max(otherLine.pt1.x, otherLine.pt2.x)
        selfOrient1 = self.orientation(otherLine.pt1)
        selfOrient2 = self.orientation(otherLine.pt2)
        otherOrient1 = otherLine.orientation(self.pt1)
        otherOrient2 = otherLine.orientation(self.pt2)
        if selfOrient1 != selfOrient2 and otherOrient1 != otherOrient2:
            return True;
        if (selfOrient1 == 0 and otherLine.pt1.x >= selfminx and otherLine.pt1.x <= selfmaxx):
            return True
        if (selfOrient2 == 0 and otherLine.pt2.x >= selfminx and otherLine.pt2.x <= selfmaxx):
            return True
        if (otherOrient1 == 0 and self.pt1.x >= otherminx and self.pt1.x <= othermaxx):
            return True
        if (otherOrient2 == 0 and self.pt2.x >= otherminx and self.pt2.x <= othermaxx):
            return True
        return False;

    def __repr__(self):
        return p1.__repr__() + " to " + pt2.__repr__()


def generatePoints(x,y,n):
    points = []
    lines = []
    while (len(points) < n):
        point = Pt(random.uniform(0,x), random.uniform(0,y))
        valid = True;
        for line in lines:
            if line.contains(point):
                valid = False;
                break;
        if (valid):
            for pt in points:
                lines.append(LineSegment(pt, point))
            points.append(point)
    return points

def display(points, lines, win):
    for point in points:
        point.display(win)
    for line in lines:
        line.display(win)

#Upperbound on number of recursive calls: 2^n * Binomial(n+k,k)
def pathString(points, string, solved):
    solved[string] = []
    if len(string) == 1:
        if string[0] == "U":
            solved[string].append([LineSegment(points[0], points[1])])
        else:
            solved[string].append([LineSegment(points[1], points[0])])
        return
    if string[0] == "D":
        partial = string[1:]
        if (partial not in solved):
            pathString(points[:len(points) - 1], partial, solved)
        partialsolutions = solved[partial]
        for partialsol in partialsolutions:
            partialsolution = copy.copy(partialsol)
            startingpoint = partialsolution[0].pt1
            newLine = LineSegment(points[len(points) - 1], startingpoint)
            valid = True
            for i in range(1, len(partialsolution)):
                if (partialsolution[i].intersect(newLine)):
                    valid = False
                    break;
            if (valid):
                partialsolution.insert(0, newLine)
                solved[string].append(partialsolution)
    if string[len(string) - 1] == "U":
        partial = string[:len(string) - 1]
        if (partial not in solved):
            pathString(points[:len(points) - 1], partial, solved)
        partialsolutions = solved[partial]
        for partialsol in partialsolutions:
            partialsolution = copy.copy(partialsol)
            endpoint = partialsolution[len(partialsolution) - 1].pt2
            newLine = LineSegment(endpoint, points[len(points) - 1])
            valid = True
            for i in range(len(partialsolution) - 1):
                if (partialsolution[i].intersect(newLine)):
                    valid = False
                    break;
            if (valid):
                partialsolution.append(newLine)
                solved[string].append(partialsolution)
    for i in range(0, len(string) - 1):
        if string[i] == "U":
            if string[i + 1] == "D":
                partial1 = string[:i] + "U" + string[i + 2:]
                partial2 = string[:i] + "D" + string[i + 2:]
                if partial1 not in solved:
                    pathString(points[:len(points) - 1], partial1, solved)
                partialSolutions = solved[partial1]
                for partialsol in partialSolutions:
                    partialSolution = copy.copy(partialsol)
                    oldLine = partialSolution.pop(i);
                    newLine1 = LineSegment(oldLine.pt1, points[-1])
                    newLine2 = LineSegment(points[-1], oldLine.pt2)
                    valid = True;
                    for j in range(i - 1):
                        if (newLine1.intersect(partialSolution[j]) or
                            newLine2.intersect(partialSolution[j])):
                            valid = False;
                            break;
                    if valid and i > 0 and partialSolution[i-1].intersect(newLine2):
                        valid = False
                    if valid and i < len(partialSolution) and partialSolution[i].intersect(newLine1):
                        valid = False
                    if valid:
                        for j in range(i + 1, len(partialSolution)):
                            if (newLine1.intersect(partialSolution[j]) or
                                newLine2.intersect(partialSolution[j])):
                                valid = False;
                                break;
                    if valid:
                        partialSolution.insert(i, newLine1)
                        partialSolution.insert(i + 1, newLine2)
                        solved[string].append(partialSolution)
                if partial2 not in solved:
                    pathString(points[:len(points) - 1], partial2, solved)
                partialSolutions = solved[partial2]
                for partialsol in partialSolutions:
                    partialSolution = copy.copy(partialsol)
                    oldLine = partialSolution.pop(i);
                    newLine1 = LineSegment(oldLine.pt1, points[-1])
                    newLine2 = LineSegment(points[-1], oldLine.pt2)
                    valid = True;
                    for j in range(i - 1):
                        if (newLine1.intersect(partialSolution[j]) or
                            newLine2.intersect(partialSolution[j])):
                            valid = False;
                            break;
                    if valid and i > 0 and partialSolution[i-1].intersect(newLine2):
                        valid = False
                    if valid and i < len(partialSolution) and partialSolution[i].intersect(newLine1):
                        valid = False
                    if valid:
                        for j in range(i + 1, len(partialSolution)):
                            if (newLine1.intersect(partialSolution[j]) or
                                newLine2.intersect(partialSolution[j])):
                                valid = False;
                                break;
                    if valid:
                        partialSolution.insert(i, newLine1)
                        partialSolution.insert(i + 1, newLine2)
                        solved[string].append(partialSolution)
                i += 1
def pathStringWrapper(points, string):
    points.sort(key=lambda p: -1*p.y)
    string = string.upper()
    solved = {}
    pathString(points, string, solved)
    f.write(string + ", " + str(len(solved[string])) + "\n")
    return solved[string][0]

def pathStringBulk(points, string, solved):
    pathString(points, string, solved)
    f.write(string + ", " + str(len(solved[string])) + "\n")

def pathStringBulkNoWrite(points, string, solved):
    pathString(points, string, solved)
    return solved

def randomPathString(n):
    string = ""
    for i in range(n - 1):
        if random.uniform(0,1) > .5:
            string += "U"
        else:
            string += "D"
    return string

def randomRun(winX, winY, n):
    s = randomPathString(n - 1)
    #print(s)
    points = generatePoints(winX, winY, n)
    lines = pathStringWrapper(points, s)
    #win = GraphWin("Path Strings", winX, winY)
    #display(points, lines, win);
    #input()

def generateAllPathStrings(start, stop):
    win = GraphWin("Path Strings", 1000, 1000)
    display(points, [], win)
    for j in range(start, stop + 1):
        points = generatePoints(1000, 1000, j)
        points.sort(key=lambda p: -1*p.y)
        solved = {}
        for i in range(int(math.pow(2, j - 1))):
            if (i % 20 == 0):
                print(i)
            string = "{0:b}".format(i)
            string = "0" * (j - 1 - len(string)) + string
            string = string.replace("0", "U")
            string = string.replace("1", "D")
            pathStringBulk(points, string, solved)
    f.close()

def bunchOfTrials(n, numPoints):
    pointSets = []
    solvedSets = []
    for i in range(n):
        points = generatePoints(1000, 1000, numPoints)
        points.sort(key=lambda p: -1*p.y)
        pointSets.append(points)
        solvedSets.append({})
    for i in range(int(math.pow(2, numPoints - 1))):
        print(i)
        string = "{0:b}".format(i)
        string = "0" * (numPoints - 1 - len(string)) + string
        string = string.replace("0", "U")
        string = string.replace("1", "D")
        arr = []
        for i in range(len(pointSets)):
            solved = pathStringBulkNoWrite(pointSets[i], string, solvedSets[i])
            arr.append(len(solved[string]))
            if (len(solved[string]) == 0):
                win = GraphWin("Path String", 1000,1000)
                print(string)
                display(pointSet[i], [], win)
                input()
        f.write(string + ", " + str(min(arr)) + "\n")
    f.close()

def screenSaver():
    win = GraphWin("Path String", 1920,1080)
    win.setBackground("Black")
    graphPoints = []
    graphLines = []
    text = Text(Point(0,0), "")
    for i in range(100000):
        points = generatePoints(1770,950, 10)
        points.sort(key=lambda p: -1*p.y)
        string = randomPathString(10)
        x = pathStringBulkNoWrite(points, string, {})
        try:
            linesSet = x[string]
            if i != 0:
                time.sleep(1)
            for point in graphPoints:
                point.undraw()
            for line in graphLines:
                line.undraw()
            text.undraw()
            graphPoints = [Circle(Point(p.x,p.y), 7) for p in points]
            graphLines = []
            for lines in linesSet:
                for l in lines:
                    graphLines.append(Line(l.pt1, l.pt2))
            text = Text(Point(1770,20), string)
            text.setTextColor("orange")
            text.setFace("arial")
            text.setSize(20)
            text.draw(win)
            for point in graphPoints:
                point.setFill("red")
                point.draw(win)
            for line in graphLines:
                line.setArrow("last")
                line.setWidth(2)
                line.setFill("blue")
                line.draw(win)
        except IndexError:
            win = GraphWin("Path String", 1770,950)
            display(points, [], win)
            input()

screenSaver()
