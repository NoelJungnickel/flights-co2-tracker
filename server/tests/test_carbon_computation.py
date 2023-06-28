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
        assert computer.get_edge_position(true_track=180, position=(0, 0)) == (-5.0, 0.0)
        assert computer.get_edge_position(true_track=270, position=(0, 0)) == (0.0, -10.0)

        assert computer.get_edge_position(true_track=45, position=(2, 3)) == (5.0, 6.0)
        assert computer.get_edge_position(true_track=45, position=(2, 8)) == (4.0, 10.0)
