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
};


int main() {
    Game myGame;
    myGame.init();
    myGame.printGame();
    int a;
    std::cin >> a;
    myGame.makeMove(1, a);
    myGame.printGame();
}
