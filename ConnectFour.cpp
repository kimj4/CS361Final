#include <iostream>
#include <string>
#include <stdlib.h>
#include <cstdlib>
#include <ctime>
const int GAMEWIDTH = 7;
const int GAMEHEIGHT = 6;

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
    int gameBoard[GAMEWIDTH][GAMEHEIGHT];
    void init() {
        w = GAMEWIDTH;
        h = GAMEHEIGHT;
        int i, j;
        for (i = 0; i < w; i++) {
            for (j = 0; j < h; j++) {
                gameBoard[i][j] = 0;
            }
        }
    }

    /*
     * Utility to print the state of the board. Player 1's pieces are Os and
     * Player 2's pieces are Xs. The columns are numbered for ease of use for
     * people.
     * TODO: take flags to specify printing Os and Xs vs 0, 1, 2s.
     */
    void printGame() {
        int i, j;
        std::string thingToWrite = " ";
        std::cout << "-----------------------------" << std::endl;
        for (j = h - 1; j >= 0; j--) {
            std::cout << "| ";
            for (i = 0; i < w; i++) {
                if (gameBoard[i][j] == 1) {
                    thingToWrite = "O";
                } else if (gameBoard[i][j] == 2) {
                    thingToWrite = "X";
                }
                std::cout << thingToWrite << " | ";
                thingToWrite = " ";
            }
            std::cout << std::endl;
            std::cout << "-----------------------------" << std::endl;
        }
        std::cout << "-----------------------------" << std::endl;
        std::cout << "| 0 | 1 | 2 | 3 | 4 | 5 | 6 |" << std::endl;
    }


    /*
     * Checks if the board is full (does not check win condition). Does this
     * by checking if there are any 0s in the top row. Therefore dependent on
     * makeMove(...) being correct.
     */
    bool isFull() {
        int i;
        for (i = 0; i < w; i++) {
            if (gameBoard[i][h - 1] == 0) {
                return false;
            }
        }
        return true;
    }

    /*
     * Changes the board state. Specify which player is dropping pieces into
     * which column.
     * Returns true if the move was made successfully.
     * Returns false if the move was invalid for whatever reason.
     */
    bool makeMove(int player, int column) {
        bool moved = false;

        if (player < 1 || player > 2) {
            std::cout << "invalid player" << std::endl;
        } else if (column < 0 || column >= w) {
            std::cout << "invalid move: wrong column chosen" << std::endl;
        } else {
            int row;
            for (row = 0; row < h; row++) {
                if (gameBoard[column][row] == 0) {
                    gameBoard[column][row] = player;
                    moved = true;
                    break;
                }
            }
            if (!moved) {
                std::cout << "invalid move: column is full" << std::endl;
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
    				if (gameBoard[i][j] * gameBoard[i][j + 1] * gameBoard[i][j + 2] * gameBoard[i][j + 3] == 1) {
    					winner = 1;
    					break;
    				} else if (gameBoard[i][j] * gameBoard[i][j + 1] * gameBoard[i][j + 2] * gameBoard[i][j + 3] == 16) {
    					winner = 2;
    					break;
                    }
                }

                if (i + 3 < w) {
    				if (gameBoard[i][j] * gameBoard[i + 1][j] * gameBoard[i + 2][j] * gameBoard[i + 3][j] == 1) {
    					winner = 1;
    					break;
    				} else if (gameBoard[i][j] * gameBoard[i + 1][j] * gameBoard[i + 2][j] * gameBoard[i + 3][j] == 16) {
    					winner = 2;
    					break;
                    }
                }

                if (i + 3 < w && j + 3 < h) {
    				if (gameBoard[i][j] * gameBoard[i + 1][j + 1] * gameBoard[i + 2][j + 2] * gameBoard[i + 3][j + 3] == 1) {
    					winner = 1;
    					break;
    				} else if (gameBoard[i][j] * gameBoard[i + 1][j + 1] * gameBoard[i + 2][j + 2] * gameBoard[i + 3][j + 3] == 16) {
    					winner = 2;
    					break;
                    }
                }

                if (i - 3 >= 0 && j + 3 < h) {
    				if (gameBoard[i][j] * gameBoard[i - 1][j + 1] * gameBoard[i - 2][j + 2] * gameBoard[i - 3][j + 3] == 1) {
    					winner = 1;
    					break;
    				} else if (gameBoard[i][j] * gameBoard[i - 1][j + 1] * gameBoard[i - 2][j + 2] * gameBoard[i - 3][j + 3] == 16) {
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
 * Matches two randomly behaving players against each other, and plays numRounds
 * number of games. A player is forced to make valid moves.
 */
void RandomCompete(int numRounds) {
    Game game;
    int curPlayer = 1;
    int winner = 0;
    std::srand(std::time(0)); // use current time as seed for random generator
    int moveColumn;
    bool validMove = false;

    int p1Wins = 0;
    int p2Wins = 0;
    int ties = 0;

    int i;
    for (i = 0; i < numRounds; i++) {
        game.init();
        while (winner == 0) {
            while(!validMove) {
                if (!game.isFull()) {
                    moveColumn = std::rand() % 7;
                    validMove = game.makeMove(curPlayer, moveColumn);
                } else {
                    break;
                }
            }
            validMove = false;
            winner = game.evaluate();
            curPlayer = curPlayer % 2 + 1; // if p1, make p2, if p2, make p1
        }

        if (winner == 1) {
            p1Wins++;
        } else if (winner == 2) {
            p2Wins++;
        } else if (winner == 3) {
            ties++;
        } else {
            std::cout << "error: invalid winner number is returned." << std::endl;
        }
        game.printGame();
        std::cout << "\n\n\n" << std::endl;

        winner = 0;
        curPlayer = 1;
    }
    std::cout << "p1 wins: " << p1Wins << std::endl;
    std::cout << "p2 wins: " << p2Wins << std::endl;
    std::cout << "ties: " << ties << std::endl;
}

int main() {
    RandomCompete(100);
}
