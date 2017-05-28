import ConnectFour
from ConnectFour import Game, GameTree, PossibleMove


# ConnectFour.RandomCompete(10000)
myGame = Game()
# myGame.printGame()
myGame.makeMove(1, 0)
myGT = GameTree(1, myGame, 2)
# myGT.tree
print(len(myGT.tree))
for thing in myGT.tree:
    # ConnectFour.gameGridPrint(thing.gameState)
    a = thing.getInputFormatVec(1)
    # print(a)
    cc = ""
    for aa in a:
        cc = cc + str(aa) + ","
    print(cc)
    #     print(aa)
# ConnectFour.gameGridPrint(myGT.tree[0].gameState)
# myGame.printGame()
# myGame.makeMove(1, 1)
# myGame.printGame()
# main()
