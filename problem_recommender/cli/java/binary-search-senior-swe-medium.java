// Problem: Minimum Processing Capacity (Business-Oriented)
// Role: Senior SWE
// Difficulty: Medium
// Context: Default business domain
//
// Description:
// Given job sizes and days D, find the minimum capacity per day to process jobs in order within D days.
//
// Requirements:
// - Implement the method described below
// - Target O(n log n) or better where applicable
//
// Method Signature:
// int minCapacity(int[] jobs, int days)

import java.util.*;

class BinarySearchSeniorSweMedium {
    public int minCapacity(int[] jobs, int days) {
        if (jobs == null || jobs.length == 0 || days <= 0) {
            return 0;
        }
        int maxJob = 0;
        int sum = 0;
        for (int job : jobs) {
            if (job > maxJob) {
                maxJob = job;
            }
            sum += job;
        }
        int left = maxJob;
        int right = sum;
        while (left < right) {
            int mid = left + ((right - left) >>> 1);
            int neededDays = 1;
            int current = 0;
            for (int job : jobs) {
                int next = current + job;
                if (next > mid) {
                    neededDays++;
                    current = job;
                    if (neededDays > days) {
                        break;
                    }
                } else {
                    current = next;
                }
            }
            if (neededDays <= days) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }
}
