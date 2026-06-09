import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class TwoPointerSortingSeniorSweMediumTest {
    @Test
    void mergesOverlaps() {
        TwoPointerSortingSeniorSweMedium solver = new TwoPointerSortingSeniorSweMedium();
        int[][] input = new int[][]{{1, 3}, {2, 6}, {8, 10}};
        int[][] expected = new int[][]{{1, 6}, {8, 10}};
        int[][] actual = solver.mergeIntervals(input);
        assertTrue(Arrays.deepEquals(expected, actual));
    }
    
    @Test
    void keepsDisjoint() {
        TwoPointerSortingSeniorSweMedium solver = new TwoPointerSortingSeniorSweMedium();
        int[][] input = new int[][]{{1, 2}, {4, 5}};
        int[][] expected = new int[][]{{1, 2}, {4, 5}};
        int[][] actual = solver.mergeIntervals(input);
        assertTrue(Arrays.deepEquals(expected, actual));
    }

}
