import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class TopologicalSortSeniorSweEasyTest {
    @Test
    void returnsValidOrder() {
        TopologicalSortSeniorSweEasy solver = new TopologicalSortSeniorSweEasy();
        int[][] prereqs = new int[][]{{1, 0}, {2, 0}, {3, 1}, {3, 2}};
        int[] order = solver.buildOrder(4, prereqs);
        assertTrue(isValidOrder(4, prereqs, order));
    }
    
    @Test
    void returnsEmptyOnCycle() {
        TopologicalSortSeniorSweEasy solver = new TopologicalSortSeniorSweEasy();
        int[][] prereqs = new int[][]{{0, 1}, {1, 0}};
        int[] order = solver.buildOrder(2, prereqs);
        assertEquals(0, order.length);
    }

    private boolean isValidOrder(int n, int[][] prereqs, int[] order) {
        if (order.length != n) {
            return false;
        }
        int[] pos = new int[n];
        for (int i = 0; i < n; i++) {
            pos[order[i]] = i;
        }
        for (int[] edge : prereqs) {
            if (pos[edge[1]] > pos[edge[0]]) {
                return false;
            }
        }
        return true;
    }

}
