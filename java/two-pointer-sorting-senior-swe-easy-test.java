import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class TwoPointerSortingSeniorSweEasyTest {
    @Test
    void findsPair() {
        TwoPointerSortingSeniorSweEasy solver = new TwoPointerSortingSeniorSweEasy();
        assertTrue(solver.hasPairWithSum(new int[]{1, 4, 7, 2}, 6));
    }
    
    @Test
    void noPair() {
        TwoPointerSortingSeniorSweEasy solver = new TwoPointerSortingSeniorSweEasy();
        assertFalse(solver.hasPairWithSum(new int[]{5, 1, 3}, 10));
    }

}
