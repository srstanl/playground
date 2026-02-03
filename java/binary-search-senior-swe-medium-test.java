import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class BinarySearchSeniorSweMediumTest {
    @Test
    void findsMinCapacity() {
        BinarySearchSeniorSweMedium solver = new BinarySearchSeniorSweMedium();
        assertEquals(6, solver.minCapacity(new int[]{3, 2, 2, 4, 1, 4}, 3));
    }
    
    @Test
    void singleDayCapacityIsSum() {
        BinarySearchSeniorSweMedium solver = new BinarySearchSeniorSweMedium();
        assertEquals(14, solver.minCapacity(new int[]{7, 2, 5}, 1));
    }

}
