import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class PriorityQueueSeniorSweMediumTest {
    @Test
    void mergesLists() {
        PriorityQueueSeniorSweMedium solver = new PriorityQueueSeniorSweMedium();
        List<List<Integer>> lists = new ArrayList<>();
        lists.add(Arrays.asList(1, 4));
        lists.add(Arrays.asList(2, 3));
        assertEquals(Arrays.asList(1, 2, 3, 4), solver.mergeSortedLists(lists));
    }
    
    @Test
    void handlesEmpty() {
        PriorityQueueSeniorSweMedium solver = new PriorityQueueSeniorSweMedium();
        assertEquals(Collections.emptyList(), solver.mergeSortedLists(new ArrayList<>()));
    }

}
