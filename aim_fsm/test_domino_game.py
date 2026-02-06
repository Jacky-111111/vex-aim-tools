import unittest

from domino_game import DominoBlockGameState, Domino


class DominoGameSimulationTests(unittest.TestCase):
    def partial_game(self) -> None:
        player_hand = [
            Domino(6, 6),
            Domino(6, 5),
            Domino(5, 4),
            Domino(4, 4),
            Domino(4, 1),
            Domino(1, 0),
            Domino(2, 0),
        ]
        opponent_hand = [
            Domino(6, 3),
            Domino(3, 3),
            Domino(3, 1),
            Domino(1, 1),
            Domino(2, 1),
            Domino(2, 2),
            Domino(5, 0),
        ]

        state = DominoBlockGameState(
            player_hand=player_hand,
            opponent_hand=opponent_hand,
            current_player="player",
        )

        # check who goes first
        self.assertEqual(state.who_goes_first(), "player")
        state.current_player = state.who_goes_first()

        self.assertEqual(state.format_board(), "(empty)")
        self.assertEqual(len(state.player_hand), 7)
        self.assertEqual(len(state.opponent_hand), 7)

        state.play_domino(Domino(6, 6), "right")
        self.assertEqual(state.format_board(), "[6|6]")
        self.assertEqual(len(state.player_hand), 6)
        self.assertEqual(len(state.opponent_hand), 7)

        state.play_domino(Domino(6, 3), "right")
        self.assertEqual(state.format_board(), "[6|6] - [6|3]")
        self.assertEqual(state.board_ends(), (6, 3))
        self.assertEqual(len(state.player_hand), 6)
        self.assertEqual(len(state.opponent_hand), 6)

        state.play_domino(Domino(6, 5), "left")
        self.assertEqual(state.format_board(), "[5|6] - [6|6] - [6|3]")
        self.assertEqual(state.board_ends(), (5, 3))
        self.assertEqual(len(state.player_hand), 5)
        self.assertEqual(len(state.opponent_hand), 6)

        state.play_domino(Domino(3, 1), "right")
        self.assertEqual(state.format_board(), "[5|6] - [6|6] - [6|3] - [3|1]")
        self.assertEqual(state.board_ends(), (5, 1))
        self.assertEqual(len(state.player_hand), 5)
        self.assertEqual(len(state.opponent_hand), 5)


if __name__ == "__main__":
    unittest.main()
