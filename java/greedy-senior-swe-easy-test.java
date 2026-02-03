import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class GreedySeniorSweEasyTest {
    @Test
    void maxNonOverlappingCount() {
        GreedySeniorSweEasy solver = new GreedySeniorSweEasy();
        int[][] intervals = new int[][]{{1, 2}, {2, 3}, {3, 4}, {1, 3}};
        assertEquals(3, solver.maxNonOverlapping(intervals));
    }
    
    @Test
    void singleInterval() {
        GreedySeniorSweEasy solver = new GreedySeniorSweEasy();
        int[][] intervals = new int[][]{{1, 10}};
        assertEquals(1, solver.maxNonOverlapping(intervals));
    }

}
