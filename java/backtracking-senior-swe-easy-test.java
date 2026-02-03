import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class BacktrackingSeniorSweEasyTest {
    @Test
    void returnsAllSubsets() {
        BacktrackingSeniorSweEasy solver = new BacktrackingSeniorSweEasy();
        List<List<String>> result = solver.subsets(new String[]{"A", "B"});
        assertEquals(4, result.size());
    }
    
    @Test
    void emptyHasOneSubset() {
        BacktrackingSeniorSweEasy solver = new BacktrackingSeniorSweEasy();
        List<List<String>> result = solver.subsets(new String[]{});
        assertEquals(1, result.size());
    }

}
