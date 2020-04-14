import sys
import time

from mpi4py import MPI

comm = MPI.COMM_WORLD

size = comm.size
rank = comm.rank



class Board:

    def __init__(self):
        self.field = [[0 for x in range(6)] for y in range(7)]
        self.finished = False

    def isLegal(self,col):
        return self.field[col][5]==0 and not self.finished

    def isFinished(self):
        return self.finished

    def move(self, player, col):
        if not self.isLegal(col):
            raise Exception("Stupac je pun ili je igra zavrsila!")
        for i in range(0,6):
            if (self.field[col][i]==0):
                self.field[col][i]=player
                if (self.isWon(player,col,i)):
                    return player
                else:
                    return 0

    def undoMove(self,col):
        for i in range(5,-1,-1):
            if (self.field[col][i]!=0):
                self.field[col][i]=0
                self.finished = False
                break

    def isWon(self,player,col,row):

        #ovo je horizontalno
        temp = 1
        for i in range(col-1,-1,-1):
            if (self.field[i][row]==player):
                temp = temp + 1
            else:
                break
        for i in range(col+1, 7, 1):
            if (self.field[i][row] == player):
                temp = temp + 1
            else:
                break
        if (temp>=4):
            self.finished = True
            return True

        #ovo je vertikalno
        temp = 1
        for i in range(row - 1, -1, -1):
            if (self.field[col][i] == player):
                temp = temp + 1
            else:
                break
        for i in range(row + 1, 6, 1):
            if (self.field[col][i] == player):
                temp = temp + 1
            else:
                break
        if (temp >= 4):
            self.finished = True
            return True

        #ovo je dijagonalno u pravo
        temp = 1
        tempcol=col - 1
        temprow=row - 1

        while (tempcol>=0 and tempcol <7 and temprow>=0 and temprow<6):
            if (self.field[tempcol][temprow]==player):
                temp = temp + 1
            else:
                break
            tempcol = tempcol - 1
            temprow = temprow - 1

        tempcol = col + 1
        temprow = row + 1
        while (tempcol >= 0 and tempcol < 7 and temprow >= 0 and temprow < 6):
            if (self.field[tempcol][temprow] == player):
                temp = temp + 1
            else:
                break
            tempcol = tempcol + 1
            temprow = temprow + 1
        if (temp >= 4):
            self.finished = True
            return True

        # ovo je dijagonalno u krivo
        temp = 1
        tempcol = col - 1
        temprow = row + 1

        while (tempcol >= 0 and tempcol < 7 and temprow >= 0 and temprow < 6):
            if (self.field[tempcol][temprow] == player):
                temp = temp + 1
            else:
                break
            tempcol = tempcol - 1
            temprow = temprow + 1

        tempcol = col + 1
        temprow = row - 1
        while (tempcol >= 0 and tempcol < 7 and temprow >= 0 and temprow < 6):
            if (self.field[tempcol][temprow] == player):
                temp = temp + 1
            else:
                break
            tempcol = tempcol + 1
            temprow = temprow - 1
        if (temp >= 4):
            self.finished = True
            return True

        return False

    def print(self):
        print("-----------------------")
        for i in range(5,-1,-1):
            for j in range(7):
                print(str(self.field[j][i])+" ",end="")
            print("\n")
        print("-----------------------")


    def __str__(self):
        return self.print()


def evaluate(board, lastPlayer, depth):
    allLose = True
    allWin = True

    if (board.isFinished()):
        if (lastPlayer==1):
            return 1
        else:
            return -1

    if (depth==0):
        return 0
    depth = depth-1
    newPlayer = 0
    if (lastPlayer==1):
        newPlayer=2
    else:
        newPlayer=1

    total = 0
    moves = 0

    for col in range(7):
        if (board.isLegal(col)):
            moves = moves + 1
            board.move(newPlayer,col)
            result = evaluate(board,newPlayer,depth)
            board.undoMove(col)
            if result > -1:
                allLose = False
            if result!=1:
                allWin = False
            if (result == 1 and newPlayer == 1):
                return 1
            if (result == 1 and newPlayer == 2):
                return -1
            total = total + result

    if (allWin):
        return 1
    if (allLose):
        return -1
    return total/moves


if __name__ == '__main__':

    if (rank==0):
        b = Board()
        while True:
            inp = int(input("Unesi potez: "))
            b.move(2,inp)
            b.print()

            if (b.isFinished()):
                print("ČESTITAMO DOBILI STE")
                break

            sys.stdout.flush()

            start = time.time()

            best = -1
            bestCol = -1
            depth = 6

            lastSentWorker=1
            jobsSent=0

            while (depth>0 and best==-1):
                for col in range(7):
                    if (b.isLegal(col)):
                        if bestCol == -1:
                            bestCol = col
                        b.move(1,col)
                        for col2 in range(7):
                            if (b.isLegal(col2)):
                                b.move(2,col2)
                                comm.send((b,1,depth-1,col),dest=(lastSentWorker)%size,tag=99)
                                jobsSent = jobsSent+1
                                lastSentWorker = lastSentWorker+1
                                if (lastSentWorker%size==0):
                                    lastSentWorker = lastSentWorker+1
                                b.undoMove(col2)
                        b.undoMove(col)

                for i in range(jobsSent):
                    result, col = comm.recv(source=MPI.ANY_SOURCE, tag=99)
                    if (result>best):
                        best = result
                        bestCol = col
                depth = depth/2

            b.move(1,bestCol)
            b.print()

            end = time.time()

            print("VRIME :" + str(end-start))
            sys.stdout.flush()

            if (b.isFinished()):
                print("NAŽALOST IZGUBILI STE")
                break
    else:
        while True:
            b,player,depth,col = comm.recv(source=0,tag=99)
            result = evaluate(b,player,depth)
            comm.send((result,col),dest=0,tag=99)