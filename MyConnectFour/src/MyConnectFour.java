import java.util.Scanner;
import java.util.concurrent.ThreadLocalRandom;




public class MyConnectFour {

	/**
	 * Function that processes one move in a connect four game. Changes the state of the board that it is given
	 * @param grid the game grid
	 * @param column the column in which a piece is being dropped in
	 * @param player the player that is placing the piece (1 or 2)
	 */
	public static boolean move(int[][] grid, int column, int player) {
		int gamePiece = -1;
		boolean changed = false;
		if (player == 1) {
			gamePiece = 1;
		} else if (player == 2) {
			gamePiece = 2;
		} else {
			System.out.println("Invalid player");
		}
		for (int y = 0; y < grid.length; y++) {
			if (grid[y][column] == 0) {
				grid[y][column] = gamePiece;
				changed = true;
				break;
			}
		}
		return changed;
	}

	/**
	 * Prints the game board. 0 is empty, 1 is player one's pieces, 2 is player two's pieces.
	 * @param grid game board
	 */
	public static void printGrid(int[][] grid){
		for (int i = grid.length - 1; i >= 0; i--) {
			for (int j = 0; j < grid[0].length; j ++) {
				System.out.print(grid[i][j] + " ");
			}
			System.out.print("\n");
		}
	}

	/**
	 * initializes the game grid to have 0s for all of its slots
	 * @param grid game board
	 */
	public static void initGrid(int[][] grid) {
		for (int i = 0; i < grid.length; i ++) {
			for (int j = 0; j < grid[0].length; j ++) {
				grid[i][j] = 0;
			}
		}
	}

	/**
	 * Examines a game grid and determines if either player won.
	 * Looks at rows of four in horizontal, vertical, and diagonal directions
	 * Not sure if algorithm is completely right, but it has worked so far.
	 * @param grid game board
	 * @return 0 if no winners, 1 if player 1 wins, 2 if player 2
	 */
	public static int evaluate(int[][] grid) {
		int winner = 0;
		for (int i = 0; i < grid.length ; i++) {
			for (int j = 0; j < grid[0].length; j++) {
				try {
					if (grid[i][j] * grid[i][j + 1] * grid[i][j + 2] * grid[i][j + 3] == 1) {
						winner = 1;
						break;
					} else if (grid[i][j] * grid[i][j + 1] * grid[i][j + 2] * grid[i][j + 3] == 16) {
						winner = 2;
						break;
					} else if (grid[i][j] * grid[i + 1][j] * grid[i + 2][j] * grid[i + 3][j] == 1) {
						winner = 1;
						break;
					} else if (grid[i][j] * grid[i + 1][j] * grid[i + 2][j] * grid[i + 3][j] == 16) {
						winner = 2;
						break;
					} else if (grid[i][j] * grid[i + 1][j + 1] * grid[i + 2][j + 2] * grid[i + 3][j + 3] == 1) {
						winner = 1;
						break;
					} else if (grid[i][j] * grid[i + 1][j + 1] * grid[i + 2][j + 2] * grid[i + 3][j + 3] == 16) {
						winner = 2;
						break;
					} else if (grid[i][j] * grid[i - 1][j + 1] * grid[i - 2][j + 2] * grid[i - 3][j + 3] == 1) {
						winner = 1;
						break;
					} else if (grid[i][j] * grid[i - 1][j + 1] * grid[i - 2][j + 2] * grid[i - 3][j + 3] == 16) {
						winner = 2;
						break;
					}
				} catch (ArrayIndexOutOfBoundsException e) {

				}
			}
		}
		return winner;
	}

	/**
	 * Runs a match where two randomly behaving players play each other
	 * @return an array
	 * index 0 is the winner
	 * index 1 is the number of turns it took
	 */
	public static int[] runRandom() {
		int[][] gameGrid = new int[7][6];
		initGrid(gameGrid);
		Scanner scan = new Scanner(System.in);
		int next = 0;
		int player = 1;
		int winner = 0;
		int numTurns = 0;
		boolean validMove = false;
		while(true) {

			if (next < gameGrid.length) {
				while (!validMove) {
					next = ThreadLocalRandom.current().nextInt(0, gameGrid.length);
					validMove = move(gameGrid, next, player);
				}
				validMove = false;
				winner = evaluate(gameGrid);
				numTurns++;
			}

			if (player == 1) {
				player = 2;
			} else {
				player = 1;
			}

			if (winner > 0) {
				printGrid(gameGrid);
				System.out.println("=====");
				break;
			}
		}
		int returnArray[] = {winner, numTurns};
		return returnArray;
	}


	public static void main(String[] args) {
		int[] result;
		int numP1Wins = 0;
		int numP2Wins = 0;
		double avgNumTurns = 0;
		int numTests = 100;
		for (int i = 0; i < numTests; i++) {
			result = runRandom();
			if (result[0] == 1) {
				numP1Wins++;
			} else if (result[0] == 2) {
				numP2Wins++;
			}
			avgNumTurns += result[1];
		}
		avgNumTurns = avgNumTurns / numTests;
		System.out.println("Player 1 wins: " + numP1Wins);
		System.out.println("Player 2 wins: " + numP2Wins);
		System.out.println("Average number of turns to finish a game: " + avgNumTurns);
	}
}
