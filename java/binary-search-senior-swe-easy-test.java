import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class BinarySearchSeniorSweEasyTest {
    @Test
    void findsFirstFailure() {
        BinarySearchSeniorSweEasy solver = new BinarySearchSeniorSweEasy();
        assertEquals(2, solver.firstFailed(new boolean[]{false, false, true, true}));
    }
    
    @Test
    void returnsMinusOneWhenNone() {
        BinarySearchSeniorSweEasy solver = new BinarySearchSeniorSweEasy();
        assertEquals(-1, solver.firstFailed(new boolean[]{false, false}));
    }

}
