import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class HashmapsSeniorSweEasyTest {
    @Test
    void findsMostFrequent() {
        HashmapsSeniorSweEasy solver = new HashmapsSeniorSweEasy();
        assertEquals("u1", solver.mostFrequentUser(new String[]{"u1", "u2", "u1", "u3"}));
    }
    
    @Test
    void singleUser() {
        HashmapsSeniorSweEasy solver = new HashmapsSeniorSweEasy();
        assertEquals("u9", solver.mostFrequentUser(new String[]{"u9"}));
    }

}
