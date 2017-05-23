#include <iostream>
#include <string>
const int GAMEWIDTH = 7;
const int GAMEHEIGHT = 6;

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

    void printGame() {
        int i, j;
        std::cout << "-----------------------------\n";
        for (j = h - 1; j >= 0; j--) {
            std::cout << "| ";
            for (i = 0; i < w; i++) {
                std::cout << gameBoard[i][j] << " | ";
            }
            std::cout << "\n";
            std::cout << "-----------------------------\n";
        }
    }

    void makeMove(int player, int column) {
        if (player < 1 || player > 2) {
            std::cout << "invalid player\n";
            exit(1);
        } else if (column < 0 || column > w) {
            std::cout << "invalid move\n";
            exit(2);
        } else {
            int row;
            for (row = 0; row < h; row++) {
                if (gameBoard[column][row] == 0) {
                    gameBoard[column][row] = player;
                    break;
                }
            }
        }
    }


    // TODO: diagonal function is not quite correct
    int evaluate() {
		int winner = 0;
		for (int i = 0; i < w ; i++) {
			for (int j = 0; j < h; j++) {
				if (gameBoard[i][j] * gameBoard[i][j + 1] * gameBoard[i][j + 2] * gameBoard[i][j + 3] == 1) {
					winner = 1;
					break;
				} else if (gameBoard[i][j] * gameBoard[i][j + 1] * gameBoard[i][j + 2] * gameBoard[i][j + 3] == 16) {
					winner = 2;
					break;
				} else if (gameBoard[i][j] * gameBoard[i + 1][j] * gameBoard[i + 2][j] * gameBoard[i + 3][j] == 1) {
					winner = 1;
					break;
				} else if (gameBoard[i][j] * gameBoard[i + 1][j] * gameBoard[i + 2][j] * gameBoard[i + 3][j] == 16) {
					winner = 2;
					break;
				} else if (gameBoard[i][j] * gameBoard[i + 1][j + 1] * gameBoard[i + 2][j + 2] * gameBoard[i + 3][j + 3] == 1) {
					winner = 1;
					break;
				} else if (gameBoard[i][j] * gameBoard[i + 1][j + 1] * gameBoard[i + 2][j + 2] * gameBoard[i + 3][j + 3] == 16) {
					winner = 2;
					break;
				} else if (gameBoard[i][j] * gameBoard[i - 1][j + 1] * gameBoard[i - 2][j + 2] * gameBoard[i - 3][j + 3] == 1) {
					winner = 1;
					break;
				} else if (gameBoard[i][j] * gameBoard[i - 1][j + 1] * gameBoard[i - 2][j + 2] * gameBoard[i - 3][j + 3] == 16) {
					winner = 2;
					break;
				}
			}
		}
		return winner;
	}
};


int main() {
    Game myGame;
    int curPlayer = 1;
    int winner = 0;
    myGame.init();
    myGame.printGame();
    int a = -1;

    while (winner == 0) {
        std::cin >> a;
        myGame.makeMove(curPlayer, a);
        myGame.printGame();
        winner = myGame.evaluate();
        if (curPlayer == 1) {
            curPlayer = 2;
        } else {
            curPlayer = 1;
        }

    }
    std::cout << "The winner is: " <<  winner << std::endl;
}
