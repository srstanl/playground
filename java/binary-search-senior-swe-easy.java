// Problem: First Failed Deployment (Business-Oriented)
// Role: Senior SWE
// Difficulty: Easy
// Context: Default business domain
//
// Description:
// Given a boolean array where false means success and true means failed, find the index of the first failure. Return -1 if none.
//
// Requirements:
// - Implement the method described below
// - Target O(n log n) or better where applicable
//
// Method Signature:
// int firstFailed(boolean[] results)

import java.util.*;

class BinarySearchSeniorSweEasy {
    public int firstFailed(boolean[] results) {
        if (results == null || results.length == 0) {
            return -1;
        }
        for (int i = 0; i <results.length; i++){
            if(results[i] == true){
                System.out.println(i);
            }
        }
    }
}
