import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class BfsDfsSeniorSweEasyTest {
    @Test
    void reachableCountsIncludeStart() {
        BfsDfsSeniorSweEasy solver = new BfsDfsSeniorSweEasy();
        Map<String, List<String>> graph = new HashMap<>();
        graph.put("A", List.of("B"));
        graph.put("B", List.of("C"));
        graph.put("C", List.of());
        assertEquals(3, solver.countReachable(graph, "A"));
    }
    
    @Test
    void reachableIgnoresDisconnected() {
        BfsDfsSeniorSweEasy solver = new BfsDfsSeniorSweEasy();
        Map<String, List<String>> graph = new HashMap<>();
        graph.put("A", List.of("B"));
        graph.put("B", List.of());
        graph.put("X", List.of("Y"));
        graph.put("Y", List.of());
        assertEquals(2, solver.countReachable(graph, "A"));
    }

}
