import java.util.Scanner;
import java.util.concurrent.ThreadLocalRandom;




public class MyConnectFour {
	
	/**
	 * Function that processes one move in a connect four game. Changes the state of the board that it is given
	 * @param grid the game grid
	 * @param column the column in which a piece is being dropped in
	 * @param player the player that is placing the piece (1 or 2)
	 */
	public static void move(int[][] grid, int column, int player) {
		int gamePiece = -1;
		boolean changed = false;
		if(player == 1) {
			gamePiece = 1;
		} else if (player == 2) {
			gamePiece = 2;
		} else {
			System.out.println("Invalid player");
		}
		for (int y = 0; y < 8; y++) {
			if (grid[y][column] == 0) {
				grid[y][column] = gamePiece;
				changed = true;
				break;
			}
		}
		if (changed == false) {
			System.out.println("Invalid move");
		}
	}
	
	public static void printGrid(int[][] grid){
		for (int i = grid.length - 1; i >= 0; i--) {
			for (int j = 0; j < grid.length; j ++) {
				System.out.print(grid[i][j] + " ");
			}
			System.out.print("\n");
		}
	}
	
	public static void initGrid(int[][] grid) {
		for (int i = 0; i < grid.length; i ++) {
			for (int j = 0; j < grid.length; j ++) {
				grid[i][j] = 0;
			}
		}
	}
	
	public static int evaluate(int[][] grid) {
		int winner = 0;
		for (int i = 0; i < grid.length ; i++) {
			for (int j = 0; j < grid.length; j++) {
				try {
					if (grid[i][j] * grid[i][j + 1] * grid[i][j + 2] * grid[i][j + 3] == 1) {
						System.out.println("player 1 wins");
						winner = 1;
						break;
					} else if (grid[i][j] * grid[i][j + 1] * grid[i][j + 2] * grid[i][j + 3] == 16) {
						System.out.println("player 2 wins");
						winner = 2;
						break;
					} else if (grid[i][j] * grid[i + 1][j] * grid[i + 2][j] * grid[i + 3][j] == 1) {
						System.out.println("player 1 wins");
						winner = 1;
						break;
					} else if (grid[i][j] * grid[i + 1][j] * grid[i + 2][j] * grid[i + 3][j] == 16) {
						System.out.println("player 2 wins");
						winner = 2;
						break;
					} else if (grid[i][j] * grid[i + 1][j + 1] * grid[i + 2][j + 2] * grid[i + 3][j + 3] == 1) {
						System.out.println("player 1 wins");
						winner = 1;
						break;
					} else if (grid[i][j] * grid[i + 1][j + 1] * grid[i + 2][j + 2] * grid[i + 3][j + 3] == 16) {
						System.out.println("player 2 wins");
						winner = 2;
						break;
					} else if (grid[i][j] * grid[i - 1][j + 1] * grid[i - 2][j + 2] * grid[i - 3][j + 3] == 1) {
						System.out.println("player 1 wins");
						winner = 1;
						break;
					} else if (grid[i][j] * grid[i - 1][j + 1] * grid[i - 2][j + 2] * grid[i - 3][j + 3] == 16) {
						System.out.println("player 2 wins");
						winner = 2;
						break;
					}
				} catch (ArrayIndexOutOfBoundsException e) {
					
				}
			}
		}
		return winner;
	}
	
	
	public static void main(String[] args) {
		int[][] gameGrid = new int[8][8];
		initGrid(gameGrid);
		Scanner scan = new Scanner(System.in);
		int next;
		int player = 1;
		int winner = 0;
//		int randomNum = ThreadLocalRandom.current().nextInt(min, max + 1);
		int numTurns = 0;

		
		printGrid(gameGrid);
		
		while(true) {
			
//			next = scan.nextInt();
			next = ThreadLocalRandom.current().nextInt(0, gameGrid.length);
			
			if (next < gameGrid.length) {
				move(gameGrid, next, player);
				printGrid(gameGrid);
				System.out.println("=====");
				winner = evaluate(gameGrid);
				numTurns++;
			}
			
			if (player == 1) {
				player = 2;
			} else {
				player = 1;
			}
			
			if (winner > 0) {
				System.out.println("number of turns it took to finish: " + numTurns);
				break;
			}
		}
	}
}
