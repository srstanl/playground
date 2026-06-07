import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class BacktrackingSeniorSweMediumTest {
    @Test
    void returnsAllPermutations() {
        BacktrackingSeniorSweMedium solver = new BacktrackingSeniorSweMedium();
        List<List<String>> result = solver.permutations(new String[]{"A", "B", "C"});
        assertEquals(6, result.size());
    }
    
    @Test
    void singlePermutation() {
        BacktrackingSeniorSweMedium solver = new BacktrackingSeniorSweMedium();
        List<List<String>> result = solver.permutations(new String[]{"X"});
        assertEquals(1, result.size());
    }

}
