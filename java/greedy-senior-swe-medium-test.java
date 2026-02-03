import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class GreedySeniorSweMediumTest {
    @Test
    void minServersBasic() {
        GreedySeniorSweMedium solver = new GreedySeniorSweMedium();
        int[][] intervals = new int[][]{{0, 30}, {5, 10}, {15, 20}};
        assertEquals(2, solver.minServers(intervals));
    }
    
    @Test
    void minServersNested() {
        GreedySeniorSweMedium solver = new GreedySeniorSweMedium();
        int[][] intervals = new int[][]{{1, 4}, {2, 3}};
        assertEquals(2, solver.minServers(intervals));
    }

}
