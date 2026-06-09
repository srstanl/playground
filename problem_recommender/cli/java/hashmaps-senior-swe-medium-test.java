import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class HashmapsSeniorSweMediumTest {
    @Test
    void findsFirstToReachK() {
        HashmapsSeniorSweMedium solver = new HashmapsSeniorSweMedium();
        assertEquals("a", solver.firstUserToReachK(new String[]{"a", "b", "a", "c", "a"}, 2));
    }
    
    @Test
    void returnsNullWhenNone() {
        HashmapsSeniorSweMedium solver = new HashmapsSeniorSweMedium();
        assertNull(solver.firstUserToReachK(new String[]{"a", "b", "c"}, 2));
    }

}
