import API
import sys
import heapq

EAST = 0
NORTH = 1
WEST = 2
SOUTH = 3
LEFT = 1
RIGHT = -1
FWD = 0
BKWD = 2

vis = {(0, 0): 1}  # gives the location of visited places, stored by tuples (,).
posArray = [1, 0, -1, 0]  # weird orientation logic.
orientation = 1  # 0=EAST,1=NORTH,2=WEST,3=SOUTH
current = (0, 0)
Edges = {}


TotalTurns=0
TotalEffectiveDistance=0

def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()

# Allows the code to take advantage of API.move(Forward(X)). Processes and returns instructions as a list
def Simplify(InstructionList):
    returnList = []
    fwdCounter = 0
    for i in range(len(InstructionList)):
        if (InstructionList[i] == 0):
            fwdCounter += 1
        else:
            if (fwdCounter != 0):
                returnList.append(fwdCounter)
                fwdCounter=0
            returnList.append(InstructionList[i])
    if (fwdCounter != 0):
        returnList.append(fwdCounter)
    log(returnList)
    return returnList

# Executes Instructions for the bot
def ExecuteInstructions(Instructions):
    for eachInstruction in Instructions:
        if (eachInstruction >= 0):
            API.moveForward(max(1,eachInstruction))
        elif (eachInstruction == -1):
            API.turnRight()
        elif (eachInstruction == -2):
            API.turnLeft()
        elif (eachInstruction == -3):
            API.turnLeft()
            API.turnLeft()
        elif (eachInstruction == -4):
            API.ackReset()

# Moves to adjacent square to the current one. Last two parameters in case of Mental maze,
# returns Instructions which can be simplified or executed directly.
def moveFromAdjacent(nextLoc, extra=5, extra2=5):
    if (extra == 5):
        global current, orientation
    else:
        current = extra
        orientation = extra2
    x = current[0]
    y = current[1]
    xNew = nextLoc[0] - x
    yNew = nextLoc[1] - y
    Instructions = []
    if ((orientation == 0) and ((xNew, yNew) == (1, 0))) or (
            (orientation == 1) and ((xNew, yNew) == (0, 1))) or (
            (orientation == 2) and ((xNew, yNew) == (-1, 0))) or (
            (orientation == 3) and ((xNew, yNew) == (0, -1))):
        Instructions.append(0)
    elif ((orientation == 0) and ((xNew, yNew) == (0, 1))) or (
            (orientation == 1) and ((xNew, yNew) == (-1, 0))) or (
            (orientation == 2) and ((xNew, yNew) == (0, -1))) or (
            (orientation == 3) and ((xNew, yNew) == (1, 0))):
        Instructions.append(-2)
        Instructions.append(0)
        orientation = (orientation + 1) % 4
    elif ((orientation == 0) and ((xNew, yNew) == (0, -1))) or (
            (orientation == 1) and ((xNew, yNew) == (1, 0))) or (
            (orientation == 2) and ((xNew, yNew) == (0, 1))) or (
            (orientation == 3) and ((xNew, yNew) == (-1, 0))):
        Instructions.append(-1)
        Instructions.append(0)
        orientation = (orientation - 1) % 4
    else:
        Instructions.append(-3)
        Instructions.append(0)
        orientation = (orientation + 2) % 4

    current = (x + xNew, y + yNew)
    vis[current] = 1
    return Instructions

# Arranges possibilities in the order of manhattan distance from the center.
def Arrange(currentCrossroads):
    if (len(currentCrossroads) == 0):
        return currentCrossroads
    elif (len(currentCrossroads) <= 2) and (currentCrossroads[0] == current):
        return currentCrossroads
    elif (len(currentCrossroads) <= 1):
        return currentCrossroads
    else:
        if (currentCrossroads[0] == current):
            nodes = currentCrossroads[1:]
        else:
            nodes = currentCrossroads[:]
        distarr = []
        for i in nodes:
            x = i[0]
            y = i[1]
            distarr.append([(x - 7.5) ** 2 + (y - 7.5) ** 2, i])
            distarr.sort(reverse=True)
        nodes = []
        for i in distarr:
            nodes.append(i[1])
        if (currentCrossroads[0] == current):
            currentCrossroad = [currentCrossroads[0]]
        else:
            currentCrossroad = []
        currentCrossroad.extend(nodes)
        return currentCrossroad

# Detects wall around it and uses this information to create a mental maze and also gives out possibilities of next move
def detectAndAdd(currentCrossroads):
    global orientation, current
    x = current[0]
    y = current[1]
    API.setColor(x, y, "G")
    if (API.wallLeft() == False):
        if ((x + posArray[(orientation + 1) % 4], y + posArray[(orientation) % 4]) not in vis):
            currentCrossroads.append((x + posArray[(orientation + 1) % 4], y + posArray[(orientation) % 4]))
        if (current in Edges):
            Edges[current].append((x + posArray[(orientation + 1) % 4], y + posArray[(orientation) % 4]))
        else:
            Edges[current] = [((x + posArray[(orientation + 1) % 4], y + posArray[(orientation) % 4]))]
        if ((x + posArray[(orientation + 1) % 4], y + posArray[(orientation) % 4]) in Edges):
            Edges[(x + posArray[(orientation + 1) % 4], y + posArray[(orientation) % 4])].append(current)
        else:
            Edges[(x + posArray[(orientation + 1) % 4], y + posArray[(orientation) % 4])] = [current]
    if (API.wallFront() == False):
        if ((x + posArray[(orientation) % 4], y + posArray[(orientation + 3) % 4]) not in vis):
            currentCrossroads.append((x + posArray[(orientation) % 4], y + posArray[(orientation + 3) % 4]))
        if (current in Edges):
            Edges[current].append((x + posArray[(orientation) % 4], y + posArray[(orientation + 3) % 4]))
        else:
            Edges[current] = [((x + posArray[(orientation) % 4], y + posArray[(orientation + 3) % 4]))]
        if ((x + posArray[(orientation) % 4], y + posArray[(orientation + 3) % 4]) in Edges):
            Edges[(x + posArray[(orientation) % 4], y + posArray[(orientation + 3) % 4])].append(current)
        else:
            Edges[(x + posArray[(orientation) % 4], y + posArray[(orientation + 3) % 4])] = [current]
    if (API.wallRight() == False):
        if ((x + posArray[(orientation + 3) % 4], y + posArray[(orientation + 2) % 4]) not in vis):
            currentCrossroads.append((x + posArray[(orientation + 3) % 4], y + posArray[(orientation + 2) % 4]))
        if (current in Edges):
            Edges[current].append((x + posArray[(orientation + 3) % 4], y + posArray[(orientation + 2) % 4]))
        else:
            Edges[current] = [((x + posArray[(orientation + 3) % 4], y + posArray[(orientation + 2) % 4]))]
        if ((x + posArray[(orientation + 3) % 4], y + posArray[(orientation + 2) % 4]) in Edges):
            Edges[(x + posArray[(orientation + 3) % 4], y + posArray[(orientation + 2) % 4])].append(current)
        else:
            Edges[(x + posArray[(orientation + 3) % 4], y + posArray[(orientation + 2) % 4])] = [current]
    return Arrange(currentCrossroads)

# Basic DFS, no optimizations.
def DFS():
    log("Running DFS")
    global current
    mazeSearchStack = []
    while (True):
        log(current)
        if (current in [(7, 7), (7, 8), (8, 7), (8, 8)]):
            log("Success!")
            break
        currentCrossroads = [current]
        currentCrossroads = detectAndAdd(currentCrossroads)

        if (len(currentCrossroads) > 1):
            mazeSearchStack.append(currentCrossroads)
        else:
            while (True):
                log("Backtracking")
                log(current)
                log("")
                currentCrossroads = mazeSearchStack.pop()
                nextLoc = currentCrossroads[0]
                Instructions = moveFromAdjacent(nextLoc)
                ExecuteInstructions(Instructions)
                if (len(currentCrossroads) > 1):
                    mazeSearchStack.append(currentCrossroads)
                    break

        currentCrossroads = mazeSearchStack.pop()
        nextLoc = currentCrossroads.pop()
        if (len(currentCrossroads) > 0):
            mazeSearchStack.append(currentCrossroads)
        Instructions = moveFromAdjacent(nextLoc)
        ExecuteInstructions(Instructions)

#Shitty function but I need it cuz I'm too stupid to debug my code
def orientationFN(instru):
    x=orientation
    for i in instru:
        if(i==-1):
            x-=1
        elif(i==-2):
            x+=1
        elif(i==-3):
            x+=2
    return x%4

# Moves to next location from given one, while finding the best route using the mental map.
def moveTo(nextLoc):
    global current, orientation
    OrientationDummyvar = orientation
    # For the 4th element of the list, we use a list to keep track of the paths used. 0=moveFWD,-1=TurnRight,-2=TurnLEFT,-3 is back,-4 is AckReset
    Nodes = [[0, current, orientation, []], [15, (0, 0), 1, [-4]]]
    heapq.heapify(Nodes)
    d2 = {}
    while (True):
        node = heapq.heappop(Nodes)
        if (node[1] not in d2):
            d2[node[1]] = node[0]
        if (node[1] == nextLoc):
            Instructions = Simplify(node[3])
            orientation = OrientationDummyvar
            ExecuteInstructions(Instructions)
            orientation=orientationFN(node[3])
            current = nextLoc
            return
        if (node[1] not in vis):
            continue
        localOr = node[2]
        d = {}
        for i in Edges[node[1]]:
            if (i not in d2):
                d2[i] = node[0] + 4
            if (i in d):
                continue
            d[i] = 1
            c = [j for j in node[3]]
            Instructions = moveFromAdjacent(i, node[1], localOr)
            c.extend(Instructions)
            if (Instructions[0] == 0):
                if (len(c) > 3) and (c[-1] == 0) and (c[len(c) - 2] == 0) and (c[len(c) - 3] == 0):
                    if (d2[i] + 1 >= node[0] + 0.5):
                        heapq.heappush(Nodes, [node[0] + 0.5, i, localOr, c])
                        d2[i] = min(node[0] + 0.5, d2[i])
                    else:
                        continue
                else:
                    if (d2[i] + 1 >= node[0] + 1):
                        heapq.heappush(Nodes, [node[0] + 1, i, localOr, c])
                        d2[i] = min(d2[i], node[0] + 1)
                    else:
                        continue
            elif (Instructions[0] == -1):
                if (d2[i] + 1 >= node[0] + 2):
                    heapq.heappush(Nodes, [node[0] + 2, i, (localOr + 3) % 4, c])
                    d2[i] = min(d2[i], node[0] + 2)
                else:
                    continue
            elif (Instructions[0] == -2):
                if (d2[i] + 1 >= node[0] + 2):
                    heapq.heappush(Nodes, [node[0] + 2, i, (localOr + 1) % 4, c])
                    d2[i] = min(d2[i], node[0] + 2)
                else:
                    continue
            elif (Instructions[0] == -3):
                if (d2[i] + 1 >= node[0] + 3):
                    heapq.heappush(Nodes, [node[0] + 3, i, (localOr + 2) % 4, c])
                    d2[i] = min(d2[i], node[0] + 3)

# Partially optimized DFS. One more optimization left before submission.
def DFS2():
    log("Running optimized DFS")
    global current, orientation
    mazeSearchStack = []

    while (True):
        log(current)
        if (current in [(7, 7), (7, 8), (8, 7), (8, 8)]):
            log("Success!")
            return current
        currentCrossroads = []
        currentCrossroads = detectAndAdd(currentCrossroads)
        if (len(currentCrossroads) > 0):
            nextLoc = currentCrossroads.pop()
            if (len(currentCrossroads) > 0):
                mazeSearchStack.append(currentCrossroads)
            Instructions = moveFromAdjacent(nextLoc)
            ExecuteInstructions(Instructions)
        else:
            log(orientation)
            log("Backtracking begins")
            currentCrossroads = mazeSearchStack.pop()
            nextLoc = currentCrossroads.pop()
            log("From "+str(current)+" to "+str(nextLoc))
            moveTo(nextLoc)
            log("Exited backtracking")
            log(orientation)
            if (len(currentCrossroads) > 0):
                mazeSearchStack.append(currentCrossroads)

def main():
    global current,orientation
    API.setColor(0, 0, "G")
    for i in range(16):
        for j in range(16):
            API.setText(i, j, str(i)+","+str(j))
    """
    while True:
        if not API.wallLeft():
            API.turnLeft()
        while API.wallFront():
            API.turnRight()
        API.moveForward()
    """
    DFS2()
    log(Edges)


if __name__ == "__main__":
    main()
