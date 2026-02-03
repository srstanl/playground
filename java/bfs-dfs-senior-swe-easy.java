// Problem: Service Dependency Reachability (Business-Oriented)
// Role: Senior SWE
// Difficulty: Easy
// Context: Default business domain
//
// Description:
// Given a directed adjacency list of services and a starting service, return how many services are reachable (including the start).
//
// Requirements:
// - Implement the method described below
// - Target O(n log n) or better where applicable
//
// Method Signature:
// int countReachable(java.util.Map<String, java.util.List<String>> graph, String start)

import java.util.*;

class BfsDfsSeniorSweEasy {
    public int countReachable(java.util.Map<String, java.util.List<String>> graph, String start) {
        // TODO: implement
        if (graph == null || start == null || !graph.containsKey(start)) {
        return 0;
    }
    
}
