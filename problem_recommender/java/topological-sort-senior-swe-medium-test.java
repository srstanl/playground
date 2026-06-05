import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class TopologicalSortSeniorSweMediumTest {
    @Test
    void canDeployAll() {
        TopologicalSortSeniorSweMedium solver = new TopologicalSortSeniorSweMedium();
        int[][] deps = new int[][]{{1, 0}, {2, 1}};
        assertTrue(solver.canDeployAll(3, deps));
    }
    
    @Test
    void detectsCycle() {
        TopologicalSortSeniorSweMedium solver = new TopologicalSortSeniorSweMedium();
        int[][] deps = new int[][]{{1, 0}, {0, 1}};
        assertFalse(solver.canDeployAll(3, deps));
    }

}
