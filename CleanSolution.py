from graphics import *
from PartialOrderings import *
import random
import copy
import math
import time

class Pt:
    '''Class for points in the plane'''

    def __init__(self, x, y):
        '''Create a point at (x,y)'''

        self.x = float(x)
        self.y = float(y)

    def display(self, win, color="black", size=3):
        '''Display the point on a window'''

        #Y coordinate flipped as graphics origin is top left corner
        point = Point(self.x, win.height - self.y)
        cir = Circle(point)
        cir.setFill(color)
        cir.draw(win)
        return cir

    def clone(self):
        '''Returns a copy of the point'''

        return Pt(self.x, self.y)

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class LineSegment:
    '''Class for directed line segments in the plane'''

    epsilon = 1e-2

    def __init__(self, pt1, pt2):
        '''Create a directed line segement from pt1 to pt2'''

        self.pt1 = pt1;
        self.pt2 = pt2;

    def signedArea(self, pt):
        '''Returns signed area of pt1, pt2, pt'''

        pt1 = self.pt1
        pt2 = self.pt2
        return (pt2.x - pt1.x) * (pt.y - pt1.y) - (pt2.y - pt1.y) * (pt.x - pt1.x)

    def contains(self, pt):
        '''Returns whether a pt lies on the segment'''

        minx = min(self.pt1.x, self.pt2.x)
        maxx = max(self.pt1.x, self.pt2.x)
        if (pt.x >= minx and pt.x <= maxx):
            return abs(self.signedArea(pt)) <= self.epsilon
        return False;

    def orientation(self, pt):
        '''Returns an int indicating whether pt is above or below the segment'''

        value = self.signedArea(pt)
        if (abs(value) <= self.epsilon):
            return 0
        elif (value < 0):
            return -1
        else:
            return 1

    def display(self, win, width=2):
        '''Display the directed segment on a window'''

        #Y coordinate flipped as graphics origin is top left corner
        p1 = Point(self.pt1.x, win.height - self.pt1.y)
        p2 = Point(self.pt2.x, win.height - self.pt2.y)
        line = Line(p1, p2)
        line.setWidth(width)
        line.setArrow("last")
        line.draw(win)
        return line

    def intersect(self, otherLine):
        '''Returns whether or not two directed segments intersect'''

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
        return self.pt1.__repr__() + " to " + self.pt2.__repr__()



def generatePoints(x,y,n):
    '''generates and returns n random non-degenerate points in [0,x) x [0,y)'''

    points = []
    lines = []
    while (len(points) < n):
        point = Pt(random.uniform(0,x), random.uniform(0,y))
        valid = True;

        #Check it has a unique y coordinate
        if point.y in [p.y for p in points]:
            valid = False
        else:
            #Check that the points are not colinear
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
    '''displays a set of points and directed segments'''

    for point in points:
        point.display(win)
    for line in lines:
        line.display(win)


def pathStringDP(points, string, solved={}):
    '''Dynamic Programming Solver for path string problem

        Takes cases on where the top point can be in the sequence

        NOTE: Can be made to generate all possible path strings by including
        a blacklist of edges for case III but this would significantly hinder
        performance as we may have to solve an previous subcase as many as
        2^n times as we'd need to recalculate each path for the various blacklists

        Arguments:
            points: a non degenerate set of n > 1 points, sorted by height
            string: a string of length n-1 from {U,D}*

        Returns:
            Many paths satisfying the path string on the point set

    '''

    solved[string] = []

    if len(string) == 1:
        if string[0] == "U":
            solved[string].append([LineSegment(points[0], points[1])])
        else:
            solved[string].append([LineSegment(points[1], points[0])])
        return

    #Case I: Paths that start at the top point
    if string[0] == "D":

        #Find all paths for n - 1 points (all but the top pt) satsifying string[1:]
        partial = string[1:]
        if (partial not in solved):
            pathStringDP(points[:len(points) - 1], partial, solved)
        partialsolutions = solved[partial]

        #Try appending the top point to all subsolutions
        for partialsol in partialsolutions:
            partialsolution = copy.copy(partialsol)
            startingpoint = partialsolution[0].pt1

            #Ensure that the path starting at top point doesn't intersect itself
            newLine = LineSegment(points[len(points) - 1], startingpoint)
            valid = True
            for i in range(1, len(partialsolution)):
                if (partialsolution[i].intersect(newLine)):
                    valid = False
                    break;

            #If no intersections add to solution dictionary
            if (valid):
                partialsolution.insert(0, newLine)
                solved[string].append(partialsolution)

    #Case II: Paths that end at the top point
    if string[len(string) - 1] == "U":

        #Find all paths for n - 1 points (all but the top pt) satsifying string[:len(string)-1]
        partial = string[:len(string) - 1]
        if (partial not in solved):
            pathStringDP(points[:len(points) - 1], partial, solved)
        partialsolutions = solved[partial]

        #Try appending the top point to all subsolutions
        for partialsol in partialsolutions:
            partialsolution = copy.copy(partialsol)

            #Ensure that the path starting at top point doesn't intersect itself
            endpoint = partialsolution[len(partialsolution) - 1].pt2
            newLine = LineSegment(endpoint, points[len(points) - 1])
            valid = True
            for i in range(len(partialsolution) - 1):
                if (partialsolution[i].intersect(newLine)):
                    valid = False
                    break;

            #If no intersections add to solution dictionary
            if (valid):
                partialsolution.append(newLine)
                solved[string].append(partialsolution)

    #Case III: Paths where the top point is not an end point
    #NOTE: Must be at an "UD" in the string
    for i in range(0, len(string) - 1):

        #Find all occurences of "UD"
        if string[i] == "U":
            if string[i + 1] == "D":

                #Have to consider appending top point to solutions to two path strings
                partial1 = string[:i] + "U" + string[i + 2:]
                partial2 = string[:i] + "D" + string[i + 2:]

                #Find all paths for n - 1 points (all but the top pt) satsifying partial1
                if partial1 not in solved:
                    pathStringDP(points[:len(points) - 1], partial1, solved)
                partialSolutions = solved[partial1]

                #Try adding the top point
                for partialsol in partialSolutions:
                    partialSolution = copy.copy(partialsol)
                    #Remove edge corresponding to partial1[i]
                    oldLine = partialSolution.pop(i);

                    #Check if adding top point causes path to intersect itself
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

                    #If no intersections add to solution dictionary
                    if valid:
                        partialSolution.insert(i, newLine1)
                        partialSolution.insert(i + 1, newLine2)
                        solved[string].append(partialSolution)

                #Find all paths for n - 1 points (all but the top pt) satsifying partial2
                if partial2 not in solved:
                    pathStringDP(points[:len(points) - 1], partial2, solved)
                partialSolutions = solved[partial2]

                #Try adding the top point
                for partialsol in partialSolutions:
                    partialSolution = copy.copy(partialsol)

                    #Remove edge corresponding to partial2[i]
                    oldLine = partialSolution.pop(i);

                    #Check if adding top point causes path to intersect itself
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

                    #If no intersections add to solution dictionary
                    if valid:
                        partialSolution.insert(i, newLine1)
                        partialSolution.insert(i + 1, newLine2)
                        solved[string].append(partialSolution)
                i += 1
                return solved

def pathStringDPWrapper(points, string, solved={}, inOrder=False):
    '''A wrapper for the pathStringDP method'''
    if not inOrder:
        points.sort(key=lambda p: p.y)
    sols = pathStringDP(points, string, solved)
    return sols

def randomPathString(n):
    '''Randomly generate a path string of length n'''

    string = ""
    for i in range(n):
        if random.uniform(0,1) > .5:
            string += "U"
        else:
            string += "D"
    return string

def generateAllPathStrings(n, filename, points=None):
    '''Generates n points and then solves all path strings and writes to the
    results to a file'''

    f = open(filename, 'a')

    if points == None:
        points = generatePoints(1000, 1000, n)

    points.sort(key=lambda p: p.y)
    solved = {}
    for i in range(int(math.pow(2, n - 1))):
        if (i % 20 == 0):
            print(i)
        string = "{0:b}".format(i)
        string = "0" * (n - 1 - len(string)) + string
        string = string.replace("0", "U")
        string = string.replace("1", "D")
        f.write(string + ", " + str(len(pathStringDPWrapper(points, string, \
            solved, True)[string])) + "\n")
    f.close()

def bunchOfTrials(n, numPoints, filename):
    '''Initializes n points sets and solves them for all path strings and
    writes the results to a file'''

    f = open(filename, 'a')
    pointSets = []
    solvedSets = []
    output, successful = hullJumpingRecursive(tempPoints, p, tempString)

    #Initialize point sets and solved dictionaries
    for i in range(n):
        points = generatePoints(1000, 1000, numPoints)
        points.sort(key=lambda p: p.y)
        pointSets.append(points)
        solvedSets.append({})

    #Solve all path strings for each points set
    for i in range(int(math.pow(2, numPoints - 1))):
        print(i)
        string = "{0:b}".format(i)
        string = "0" * (numPoints - 1 - len(string)) + string
        string = string.replace("0", "U")
        string = string.replace("1", "D")
        arr = []
        for i in range(len(pointSets)):
            solved = pathStringDPWrapper(pointSets[i], string, solvedSets[i], True)
            arr.append(len(solved[string]))

            #If there is no solution display the point set
            if (len(solved[string]) == 0):
                win = GraphWin("Path String", 1000,1000)
                print(string)
                display(pointSet[i], [], win)
                input()

        f.write(string + ", " + str(max(arr)) + ", " + str(partialOrderings(string, {})) + "\n")
    f.close()

def nonIntersectingPaths(n):
    '''Gives lower bound for the number of non intersecting paths on n points'''

    total = 0
    points = generatePoints(1000, 1000, n)
    points.sort(key=lambda p: p.y)
    solved = {}
    for i in range(int(math.pow(2, n - 1))):
        string = "{0:b}".format(i)
        string = "0" * (n - 1 - len(string)) + string
        string = string.replace("0", "U")
        string = string.replace("1", "D")
        total += len(pathStringDPWrapper(points, string, solved,True)[string])
    return total

def generateConvexPoints(n, r=100):
    '''Generates points in convex position (more specifically on a circle)'''

    thetas = []
    points = []
    while len(points) < n:

        #Make sure that two points don't have the same y coordinate
        theta = random.uniform(-math.pi, math.pi)
        if theta not in thetas and -theta not in thetas:
            points.append(Pt(r*math.cos(theta), r*math.sin(theta)))
            thetas.append(theta)
    return points

def convexHull(points,sortedByY=False):
    '''Grahm Scan convex hull algorithm'''

    if (len(points) < 4):
        return points
    bottom = points[0]
    if not sortedByY:
        for i in range(1,len(points)):
            if points[i].y < bottom.y:
                bottom = points[i]
    points.remove(bottom)
    points.sort(key=lambda p: -1 * (p.x - bottom.x)/(p.y - bottom.y))
    points.append(bottom)
    stack = [bottom, points[0]]
    for cur in range(1, len(points)):
        stack.append(points[cur])
        p3 = stack.pop()
        p2 = stack.pop()
        p1 = stack.pop()
        signedArea = (p2.x - p1.x)*(p3.y - p1.y) - (p2.y - p1.y)*(p3.x - p1.x)
        while signedArea <= 0:
            p2 = p1
            p1 = stack.pop()
            signedArea = (p2.x - p1.x)*(p3.y - p1.y) - (p2.y - p1.y)*(p3.x - p1.x)
        stack.append(p1)
        stack.append(p2)
        stack.append(p3)
    stack.pop()
    return stack

def jarvisMarchSinglePass(points, point):
    '''A single iteration of Jarvis march'''

    nextPoint = point
    nextSegment = LineSegment(point, point)
    prevPoint = point
    prevSegment = LineSegment(point, point)
    for p in points:
        if (nextPoint == point or nextSegment.signedArea(p) > 0):
            nextPoint = p
            nextSegment.pt2 = p
        if (prevPoint == point or prevSegment.signedArea(p) < 0):
            prevPoint = p
            prevSegment.pt2 = p
    return [nextPoint, prevPoint]

def hullJumping(points, string, hull=None):
    '''A wrapper for the hull jumping algorithm'''

    if hull == None:
        hull = convexHull(points)
    found = False
    output = []

    #Start the recursive hull jumping algorithm from each point in the hull
    for point in hull:
        out, success = hullJumpingRecursive(copy.copy(points),point,string)
        if success:
            found = True
            for o in out:
                o.append(point)
                output.append(o)

    return output

def hullJumpingRecursive(points, point, string):
    '''A recursive implementation for the hull jumping algorithm'''

    if (len(string) == 1):
        points.remove(point)
        if string[0] == "U" and points[0].y < point.y:
            return [[points[0]]], True
        if string[0] == "D" and points[0].y > point.y:
            return [[points[0]]], True
        return [[]], False

    #Find previous point and next point on the convex hull
    p1, p2 = jarvisMarchSinglePass(points, point)

    #Determine what new points will be on the convex hull after removing the current point
    p3, p4 = jarvisMarchSinglePass(points, p1)
    if p3.x == point.x and p3.y == point.y:
        p3 = p4
    p4 = p1
    points.remove(point)
    nextPoints = [p1]
    while p4.x != p2.x and p4.y != p2.y:
        p5, p6 = jarvisMarchSinglePass(points, p4)
        if p5.x == p3.x and p5.y == p3.y:
            p5 = p6
        p3 = p4
        p4 = p5
        nextPoints.append(p4)

    out = []
    success = False

    #Try jumping to a point in the next hull
    if (string[0] == "U"):
        for p in nextPoints:
            if p.y > point.y:
                tempPoints = copy.copy(points)
                tempString = string[1:]
                output, successful = hullJumpingRecursive(tempPoints, p, tempString)
                if successful:
                    for arr in output:
                        arr.append(p)
                        out.append(arr)
                    success = True
    else:
        for p in nextPoints:
            if p.y < point.y:
                tempPoints = copy.copy(points)
                tempString = string[1:]
                output, successful = hullJumpingRecursive(tempPoints, p, tempString)
                if successful:
                    for arr in output:
                        arr.append(p)
                        out.append(arr)
                    success = True
    return out, success

print(hullJumping(generatePoints(1000,1000,5), "UDUU"))
print(pathStringDPWrapper(generatePoints(1000,1000,5), "UDUU"))
