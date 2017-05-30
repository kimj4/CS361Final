#include <iostream>
#include <string>
#include <stdlib.h>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <tgmath.h>
#include <boost/python.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/implicit.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

const int GAMEWIDTH = 7;
const int GAMEHEIGHT = 6;
/*
 * Utility function for printing a grid of some size
 */
void printGame(std::vector<std::vector<int> > gameGrid) {
    int i, j;
    std::string thingToWrite = " ";
    std::cout << "-----------------------------" << std::endl;
    for (j = GAMEHEIGHT - 1; j >= 0; j--) {
        std::cout << "| ";
        for (i = 0; i < GAMEWIDTH; i++) {
            if (gameGrid[i][j] == 1) {
                thingToWrite = "O";
            } else if (gameGrid[i][j] == 2) {
                thingToWrite = "X";
            }
            std::cout << thingToWrite << " | ";
            thingToWrite = " ";
        }
        std::cout << std::endl;
        std::cout << "-----------------------------" << std::endl;
    }
    std::cout << "-----------------------------" << std::endl;
    std::cout << "| 1 | 2 | 3 | 4 | 5 | 6 | 7 |" << std::endl;
}

void printInputMatrix(std::vector<std::vector<int> > gameGrid) {
    int i, j;
    std::string thingToWrite = " ";
    std::cout << "----------------------------------------------------------" << std::endl;
    for (j = GAMEHEIGHT - 1; j >= 0; j--) {
        std::cout << "| ";
        for (i = 0; i < 2 * GAMEWIDTH; i++) {
            if (gameGrid[i][j] == 1) {
                thingToWrite = "O";
            } else if (gameGrid[i][j] == 2) {
                thingToWrite = "X";
            }
            std::cout << thingToWrite << " | ";
            thingToWrite = " ";
        }
        std::cout << std::endl;
        std::cout << "----------------------------------------------------------" << std::endl;
    }
}



/*
 * Class that contains information about connect an instance of connect four.
 * To change the size of the board, the global constants must be changed.
 * gameBoard contains the state of the game, where 0 is empty, 1 is player 1,
 * and 2 is player 2.
 */
class Game {
public:
    int w;
    int h;
    std::vector<std::vector<int> > gameGrid;

    Game() {
        w = GAMEWIDTH;
        h = GAMEHEIGHT;
        int i, j;
        gameGrid = std::vector<std::vector<int> >(w, std::vector<int>(h, 0));
    }

    /*
     * Checks if a column is full [0, 6]
     */
    bool isColumnFull(int index) {
        if (gameGrid[index][h - 1] != 0) {
            return true;
        }
        return false;
    }


    /*
     * Checks if the board is full (does not check win condition). Does this
     * by checking if there are any 0s in the top row. Therefore dependent on
     * makeMove(...) being correct.
     */
    bool isFull() {
        int i;
        bool full = true;
        for (i = 0; i < w; i++) {
            if (!isColumnFull(i)) {
                full = false;
                break;
            }
        }
        return full;
    }

    /*
     * Changes the board state. Specify which player is dropping pieces into
     * which column.
     * Returns true if the move was made successfully.
     * Returns false if the move was invalid for whatever reason.
     */
    bool makeMove(int player, int column) {
        return makeMoveOnSeparateBoard(player, column, &gameGrid, &gameGrid);
    }


    bool makeMoveOnSeparateBoard(int player, int column, std::vector<std::vector<int> > *startBoard, std::vector<std::vector<int> > *separateBoard) {
        // copy array
        *separateBoard = *startBoard;

        bool moved = false;
        if (player < 1 || player > 2) {
            // invalid player
        } else if (column < 0 || column >= w) {
            // invalid column
        } else {
            int row;
            for (row = 0; row < h; row++) {
                if (separateBoard->at(column).at(row) == 0) {
                    separateBoard->at(column).at(row) = player;
                    moved = true;
                    break;
                }
            }
            if (!moved) {
                // column is full
            }
        }
        return moved;
    }

    /*
     * Checks the board to see if there is a winner or if there is a tie.
     * The checks are dependent on the fact that 1 * 1 * 1 * 1 = 1 and
     * 2 * 2 * 2 * 2 = 16, and no other length-four combination of 0s, 1s, and
     * 2s allow for these products.
     * Returns the player that wins or 3 if it is a tie.
     */
    int evaluate() {
		int winner = 0;
		for (int i = 0; i < w ; i++) {
			for (int j = 0; j < h; j++) {
                if (j + 3 < h) {
    				if (gameGrid[i][j] * gameGrid[i][j + 1] * gameGrid[i][j + 2] * gameGrid[i][j + 3] == 1) {
    					winner = 1;
    					break;
    				} else if (gameGrid[i][j] * gameGrid[i][j + 1] * gameGrid[i][j + 2] * gameGrid[i][j + 3] == 16) {
    					winner = 2;
    					break;
                    }
                }

                if (i + 3 < w) {
    				if (gameGrid[i][j] * gameGrid[i + 1][j] * gameGrid[i + 2][j] * gameGrid[i + 3][j] == 1) {
    					winner = 1;
    					break;
    				} else if (gameGrid[i][j] * gameGrid[i + 1][j] * gameGrid[i + 2][j] * gameGrid[i + 3][j] == 16) {
    					winner = 2;
    					break;
                    }
                }

                if (i + 3 < w && j + 3 < h) {
    				if (gameGrid[i][j] * gameGrid[i + 1][j + 1] * gameGrid[i + 2][j + 2] * gameGrid[i + 3][j + 3] == 1) {
    					winner = 1;
    					break;
    				} else if (gameGrid[i][j] * gameGrid[i + 1][j + 1] * gameGrid[i + 2][j + 2] * gameGrid[i + 3][j + 3] == 16) {
    					winner = 2;
    					break;
                    }
                }

                if (i - 3 >= 0 && j + 3 < h) {
    				if (gameGrid[i][j] * gameGrid[i - 1][j + 1] * gameGrid[i - 2][j + 2] * gameGrid[i - 3][j + 3] == 1) {
    					winner = 1;
    					break;
    				} else if (gameGrid[i][j] * gameGrid[i - 1][j + 1] * gameGrid[i - 2][j + 2] * gameGrid[i - 3][j + 3] == 16) {
    					winner = 2;
    					break;
    				}
                }
			}
		}
        if (this->isFull() && winner == 0) {
            winner = 3; //tie
        }
		return winner;
	}
};

/*
 * An object that contains:
 *  - moves as a vector of ints
 *  - the resulting game state after the move
 */
class PossibleMove {
public:
    std::vector<int> moves;
    // int gameState[GAMEWIDTH][GAMEHEIGHT];
    std::vector<std::vector<int> > gameState;
    PossibleMove() {}

    PossibleMove(std::vector<int> movesVec, std::vector<std::vector<int> > state) {
        moves = movesVec;
        gameState = std::vector<std::vector<int> >(GAMEWIDTH, std::vector<int>(GAMEHEIGHT, 0));
        gameState = state;
    }

    /*
     * convert the gamestate into a list of length 2 * GAMEWIDTH * GAMEHEIGHT
     */
    std::vector<int> getInputFormatVec(int player) {
        std::vector<std::vector<int> > inputMatrix = std::vector<std::vector<int> >( 2 * GAMEWIDTH, std::vector<int>(GAMEHEIGHT, 0));
        int i, j;
        for (i = 0; i < GAMEWIDTH; i++) {
            for (j = 0; j < GAMEHEIGHT; j++) {
                if (gameState[i][j] == player) {
                    inputMatrix[i][j] = 1;
                } else if (gameState[i][j] == (3 - player)) {
                    inputMatrix[i + 7][j] = 1;
                }
            }
        }


        std::vector<int> returnList = std::vector<int>(2 * GAMEWIDTH * GAMEHEIGHT);
        int curIdx = 0;
        for (i = 0; i < 2 * GAMEWIDTH; i++) {
            for (j = 0; j < GAMEHEIGHT; j++) {
                returnList[curIdx] = inputMatrix[i][j];
                curIdx++;
            }
        }
        return returnList;
    }

    /*
     * convert the gamestate into a list of length 2 * GAMEWIDTH * GAMEHEIGHT
     * This time, makes the list from the game state, but flipped about the
     * vertical axis
     */
    std::vector<int> getInputFormatVecMirrored(int player) {
        std::vector<std::vector<int> > inputMatrix = std::vector<std::vector<int> >( 2 * GAMEWIDTH, std::vector<int>(GAMEHEIGHT, 0));
        int i, j;
        for (i = 0; i < GAMEWIDTH; i++) {
            for (j = 0; j < GAMEHEIGHT; j++) {
                if (gameState[i][j] == player) {
                    inputMatrix[6 - i][j] = 1;
                } else if (gameState[i][j] == (3 - player)) {
                    inputMatrix[13 - i][j] = 1;
                }
            }
        }


        std::vector<int> returnList = std::vector<int>(2 * GAMEWIDTH * GAMEHEIGHT);
        int curIdx = 0;
        for (i = 2 * GAMEWIDTH - 1; i >= 0; i--) {
            for (j = 0; j < GAMEHEIGHT; j++) {
                returnList[curIdx] = inputMatrix[i][j];
                curIdx++;
            }
        }
        return returnList;
    }


};

bool operator==(const PossibleMove &lhs, const PossibleMove &rhs) {
    bool truthVal = false;
    if (lhs.moves == rhs.moves) {
        truthVal = true;
    }
    return truthVal;
}

/*
 * A list of list of ints
 * the lower level list contains list of moves
 * sample:
 * for depth 1
 * [
 *   [1,1], [1,2], [1,3], [1,4], [1,5], [1,6], [1,7],
 *   [2,1], [2,2]
 *  ...
 * ]
 * should save on space
 * can integrate a separate storage later
 * if depth is 1, 49 PossibleMove objects
 * if depth is 2, 7 * 7 * 7 * 7 PossibleMove objects
 */
class GameTree {
public:
    std::vector<PossibleMove*> tree;

    GameTree(int depth, Game game, int player) {
        if (depth == 0) {
            std::vector<int> null_moves;
            // PossibleMove null_pm = PossibleMove(null_moves, game.gameGrid);
            tree.push_back(new PossibleMove(null_moves, game.gameGrid));
        } else {
            // build the vector that hold the sequence of moves to perform
            std::vector<std::vector<int> > movesVecVec;
            std::vector<int> emptyMove;
            movesVecVec.push_back(emptyMove);
            movesVecVec = recursivelyBuildMoves(movesVecVec, depth);
            buildTree(game, movesVecVec, player);
        }
    }

    void buildTree(Game initialGame, std::vector<std::vector<int> > movesVecVec, int player) {
        int curIdx = 0;
        while (curIdx != movesVecVec.size()) {
            std::vector<std::vector<int> > newGameState = std::vector<std::vector<int> >(GAMEWIDTH, std::vector<int>(GAMEHEIGHT, 0));
            std::vector<int> badMoves;

            if (std::find(badMoves.begin(), badMoves.end(), movesVecVec.at(curIdx).at(0)) == badMoves.end()) {
                // if the move is not marked as bad
                int curPlayer = player;
                bool validMove = true;
                int i;
                for (i = 0; i < movesVecVec.at(curIdx).size(); i++) {
                    if (i == 0) {
                        validMove = initialGame.makeMoveOnSeparateBoard(curPlayer, movesVecVec.at(curIdx).at(i), &initialGame.gameGrid ,&newGameState);
                    } else {
                        validMove = initialGame.makeMoveOnSeparateBoard(curPlayer, movesVecVec.at(curIdx).at(i), &newGameState, &newGameState);
                    }
                    if (!validMove) {
                        if (i == 0) {
                            badMoves.push_back(movesVecVec.at(curIdx).at(i));
                            break;
                        } else {
                            validMove = true;
                            break;
                        }
                    }
                    curPlayer = curPlayer % 2 + 1;
                }
                if (validMove) {
                    // PossibleMove newPM = PossibleMove(movesVecVec.at(curIdx), newGameState);
                    // tree.push_back(&newPM);
                    tree.push_back(new PossibleMove(movesVecVec.at(curIdx), newGameState));
                }
            }
            curIdx++;
        }
    }

    std::vector<std::vector<int> > recursivelyBuildMoves(std::vector<std::vector<int> > workingMoves, int depth) {
        if (depth == 0) {
            return workingMoves;
        } else {
            std::vector<std::vector<int> > newMoves;
            int curIdx = 0;
            while (curIdx != workingMoves.size()) {
                int i, j;
                for (i = 0; i < GAMEWIDTH; i++) {
                    for (j = 0; j < GAMEWIDTH; j++) {
                        std::vector<int> copy = workingMoves.at(curIdx);
                        copy.push_back(i);
                        copy.push_back(j);
                        newMoves.push_back(copy);
                    }
                }
                curIdx++;
            }
            return recursivelyBuildMoves(newMoves, depth - 1);
        }
    }

    PossibleMove getPMAt(int idx) {
        return *(tree.at(idx));
    }

    int length() {
        return tree.size();
    }
};

void vectorPrint(std::vector<int> vec) {
    for (int i = 0; i < vec.size(); i++) {
        if (i == vec.size() - 1) {
            std::cout << vec[i] << std::endl;
        } else {
            std::cout << vec[i] << ", ";
        }
        if (i + 1 % 6 == 0) {
            std::cout << '\n';
        }

    }
}

// int main() {
//     std::cout << "aaa" << '\n';
//     Game game = Game();
//     std::cout << "bbb" << '\n';
//     game.makeMove(1, 0);
//     printGame(game.gameGrid);
//
//
//     GameTree tree = GameTree(1, game, 2);
//     vectorPrint(tree.getPMAt(0).getInputFormatVec(2));
//     vectorPrint(tree.getPMAt(0).getInputFormatVecMirrored(2));
// }


BOOST_PYTHON_MODULE(ConnectFour2) {
    using namespace boost::python;

    def("printGame", printGame);
    def("vectorPrint", vectorPrint);
    def("printInputMatrix", printInputMatrix);

    class_<PossibleMove>("PossibleMove")
        .def("getInputFormatVec", &PossibleMove::getInputFormatVec)
        .def("getInputFormatVecMirrored", &PossibleMove::getInputFormatVecMirrored)
        .add_property("moves", &PossibleMove::moves)
        .add_property("gameState", &PossibleMove::gameState)
    ;

    class_<std::vector<PossibleMove> >("PMList")
        .def(vector_indexing_suite<std::vector<PossibleMove> >());

    class_<GameTree>("GameTree", init<int, Game, int>())
        .def("getPMAt", &GameTree::getPMAt)
        .def("length", &GameTree::length)
        .add_property("tree", &GameTree::tree)
    ;

    class_<Game>("Game")
        .def("evaluate", &Game::evaluate)
        .def("makeMove", &Game::makeMove)
        .def("isColumnFull", &Game::isColumnFull)
        .def("isFull", &Game::isFull)
        .add_property("w", &Game::w)
        .add_property("h", &Game::h)
        .add_property("gameGrid", &Game::gameGrid)
    ;
}
