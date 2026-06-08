import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class PriorityQueueSeniorSweEasyTest {
    @Test
    void returnsTopK() {
        PriorityQueueSeniorSweEasy solver = new PriorityQueueSeniorSweEasy();
        int[] result = solver.topKFrequent(new int[]{1, 1, 1, 2, 2, 3}, 2);
        Arrays.sort(result);
        assertArrayEquals(new int[]{1, 2}, result);
    }
    
    @Test
    void singleCode() {
        PriorityQueueSeniorSweEasy solver = new PriorityQueueSeniorSweEasy();
        int[] result = solver.topKFrequent(new int[]{9}, 1);
        assertArrayEquals(new int[]{9}, result);
    }

}
