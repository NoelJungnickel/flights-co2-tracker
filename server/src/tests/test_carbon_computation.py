import pytest

from carbon_computation import CarbonComputation


class TestCarbonComputation:
    """Class to group tests of the carbon computation."""

    @pytest.fixture
    def computer(self) -> CarbonComputation:
        """Initialize carbon computation for simple mock airspace."""
        return CarbonComputation("test", (-5.0, -10.0, 5.0, 10.0))

    def test_correct_edge_positions(self, computer: CarbonComputation) -> None:
        """Test whether the estimated edge position are correct."""
        assert computer.get_edge_position(true_track=0, position=(0, 0)) == (5.0, 0.0)
        assert computer.get_edge_position(true_track=90, position=(0, 0)) == (0.0, 10.0)
        assert computer.get_edge_position(true_track=180, position=(0, 0)) == (
            -5.0,
            0.0,
        )
        assert computer.get_edge_position(true_track=270, position=(0, 0)) == (
            0.0,
            -10.0,
        )
        assert computer.get_edge_position(true_track=360, position=(0, 0)) == (
            5.0,
            0.0,
        )

        # First quadrant
        assert computer.get_edge_position(true_track=45, position=(2, 3)) == (5.0, 6.0)
        assert computer.get_edge_position(true_track=45, position=(2, 8)) == (4.0, 10.0)

        # Second quadrant
        assert computer.get_edge_position(true_track=135, position=(-2, 8)) == (
            -4.0,
            10.0,
        )
        assert computer.get_edge_position(true_track=135, position=(-4, 8)) == (-5.0, 9.0)

        # Third quadrant
        assert computer.get_edge_position(true_track=225, position=(-3, -4)) == (
            -5.0,
            -6.0,
        )
        assert computer.get_edge_position(true_track=225, position=(-3, -9)) == (
            -4.0,
            -10.0,
        )

        # Fourth quadrant
        assert computer.get_edge_position(true_track=315, position=(2, -8)) == (
            4.0,
            -10.0,
        )
        assert computer.get_edge_position(true_track=315, position=(4, -8)) == (5.0, -9.0)
