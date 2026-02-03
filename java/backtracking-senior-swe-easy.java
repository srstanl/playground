// Problem: Generate Feature Flag Combinations (Business-Oriented)
// Role: Senior SWE
// Difficulty: Easy
// Context: Default business domain
//
// Description:
// Given an array of feature flags, return all subsets.
//
// Requirements:
// - Implement the method described below
// - Target O(n log n) or better where applicable
//
// Method Signature:
// java.util.List<java.util.List<String>> subsets(String[] flags)

import java.util.*;

class BacktrackingSeniorSweEasy {
    public java.util.List<java.util.List<String>> subsets(String[] flags) {
        if (flags == null || flags.length == 0) {
            java.util.List<java.util.List<String>> empty = new ArrayList<>();
            empty.add(new ArrayList<>());
            return empty;
        }
        int n = flags.length;
        java.util.List<java.util.List<String>> result = new ArrayList<>(1 << Math.min(n, 30));
        result.add(new ArrayList<>());
        for (String flag : flags) {
            int size = result.size();
            for (int i = 0; i < size; i++) {
                java.util.List<String> subset = result.get(i);
                java.util.List<String> next = new ArrayList<>(subset.size() + 1);
                next.addAll(subset);
                next.add(flag);
                result.add(next);
            }
        }
        return result;
    }
}
