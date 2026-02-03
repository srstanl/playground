import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class SlidingWindowSeniorSweEasyTest {
    @Test
    void findsMaxWindowSum() {
        SlidingWindowSeniorSweEasy solver = new SlidingWindowSeniorSweEasy();
        assertEquals(7, solver.maxRequestsInWindow(new int[]{1, 2, 3, 4}, 2));
    }
    
    @Test
    void singleWindow() {
        SlidingWindowSeniorSweEasy solver = new SlidingWindowSeniorSweEasy();
        assertEquals(5, solver.maxRequestsInWindow(new int[]{5}, 1));
    }

}
