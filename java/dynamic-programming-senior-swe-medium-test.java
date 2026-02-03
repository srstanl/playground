import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class DynamicProgrammingSeniorSweMediumTest {
    @Test
    void findsMaxNonAdjacent() {
        DynamicProgrammingSeniorSweMedium solver = new DynamicProgrammingSeniorSweMedium();
        assertEquals(12, solver.maxNonAdjacentLoad(new int[]{2, 7, 9, 3, 1}));
    }
    
    @Test
    void singleSlot() {
        DynamicProgrammingSeniorSweMedium solver = new DynamicProgrammingSeniorSweMedium();
        assertEquals(5, solver.maxNonAdjacentLoad(new int[]{5}));
    }

}
