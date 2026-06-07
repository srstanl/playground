// Problem: Retry Plans (Business-Oriented)
// Role: Senior SWE
// Difficulty: Easy
// Context: Default business domain
//
// Description:
// A service can retry an operation by waiting 1 or 2 minutes. Return the number of distinct retry plans to wait n minutes.
//
// Requirements:
// - Implement the method described below
// - Target O(n log n) or better where applicable
//
// Method Signature:
// int countRetryPlans(int n)

import java.util.*;

class DynamicProgrammingSeniorSweEasy {
    public int countRetryPlans(int n) {

        int plans = 0;
        // TODO: implement
        if (n <= 0) {
            plans=  0;
        }
        return plans;
    }
}
