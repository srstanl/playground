import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class UnionFindSeniorSweMediumTest {
    @Test
    void findsRedundant() {
        UnionFindSeniorSweMedium solver = new UnionFindSeniorSweMedium();
        int[] result = solver.findRedundantConnection(new int[][]{{1, 2}, {1, 3}, {2, 3}});
        assertArrayEquals(new int[]{2, 3}, result);
    }
    
    @Test
    void findsLaterRedundant() {
        UnionFindSeniorSweMedium solver = new UnionFindSeniorSweMedium();
        int[] result = solver.findRedundantConnection(new int[][]{{1, 2}, {2, 3}, {3, 4}, {1, 4}, {1, 5}});
        assertArrayEquals(new int[]{1, 4}, result);
    }

}
