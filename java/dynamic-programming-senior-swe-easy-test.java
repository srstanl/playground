import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class DynamicProgrammingSeniorSweEasyTest {
    @Test
    void countsRetryPlans() {
        DynamicProgrammingSeniorSweEasy solver = new DynamicProgrammingSeniorSweEasy();
        assertEquals(3, solver.countRetryPlans(3));
    }
    
    @Test
    void singleMinute() {
        DynamicProgrammingSeniorSweEasy solver = new DynamicProgrammingSeniorSweEasy();
        assertEquals(1, solver.countRetryPlans(1));
    }

}
