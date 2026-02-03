import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class UnionFindSeniorSweEasyTest {
    @Test
    void countsComponents() {
        UnionFindSeniorSweEasy solver = new UnionFindSeniorSweEasy();
        int[][] edges = new int[][]{{0, 1}, {1, 2}, {3, 4}};
        assertEquals(2, solver.countComponents(5, edges));
    }
    
    @Test
    void noEdgesAllIsolated() {
        UnionFindSeniorSweEasy solver = new UnionFindSeniorSweEasy();
        assertEquals(3, solver.countComponents(3, new int[0][0]));
    }

}
