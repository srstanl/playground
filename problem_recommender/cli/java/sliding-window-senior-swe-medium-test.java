import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class SlidingWindowSeniorSweMediumTest {
    @Test
    void findsMinWindow() {
        SlidingWindowSeniorSweMedium solver = new SlidingWindowSeniorSweMedium();
        assertEquals("BANC", solver.minWindow("ADOBECODEBANC", "ABC"));
    }
    
    @Test
    void returnsEmptyWhenNotFound() {
        SlidingWindowSeniorSweMedium solver = new SlidingWindowSeniorSweMedium();
        assertEquals("", solver.minWindow("abc", "zzz"));
    }

}
