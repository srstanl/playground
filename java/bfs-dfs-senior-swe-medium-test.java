import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class BfsDfsSeniorSweMediumTest {
    @Test
    void shortestHopsFound() {
        BfsDfsSeniorSweMedium solver = new BfsDfsSeniorSweMedium();
        Map<String, List<String>> graph = new HashMap<>();
        graph.put("A", List.of("B"));
        graph.put("B", List.of("A", "C"));
        graph.put("C", List.of("B"));
        assertEquals(2, solver.shortestHops(graph, "A", "C"));
    }
    
    @Test
    void shortestHopsUnreachable() {
        BfsDfsSeniorSweMedium solver = new BfsDfsSeniorSweMedium();
        Map<String, List<String>> graph = new HashMap<>();
        graph.put("A", List.of("B"));
        graph.put("B", List.of("A"));
        graph.put("X", List.of("Y"));
        graph.put("Y", List.of("X"));
        assertEquals(-1, solver.shortestHops(graph, "A", "Y"));
    }

}
