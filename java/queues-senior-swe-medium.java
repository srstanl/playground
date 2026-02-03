// Problem: Prioritized Support Ticket Routing (Business-Oriented)
// Role: Senior SWE
// Difficulty: Medium
// Context: Default business domain
//
// Description:
// You are building the backend for a customer support platform. Incoming tickets must be
// routed to agents based on severity and arrival time. High-severity tickets are handled
// first, and tickets with equal severity must be processed FIFO. The queue has a fixed
// capacity to prevent overload.
//
// Requirements:
// - enqueue(id, severity) returns true if accepted, false if full
// - dequeue() returns next ticket id, or null if empty
// - FIFO order for equal severity
// - Target O(log n) for enqueue/dequeue
//
// Example:
// capacity = 3
// enqueue("T1", 2) -> true
// enqueue("T2", 5) -> true
// enqueue("T3", 5) -> true
// enqueue("T4", 3) -> false
// dequeue() -> "T2"
// dequeue() -> "T3"
// dequeue() -> "T1"

import java.util.PriorityQueue;

class BoundedPriorityTicketQueue {
    private static final class Ticket {
        private final String id;
        private final int severity;
        private final long sequence;

        private Ticket(String id, int severity, long sequence) {
            this.id = id;
            this.severity = severity;
            this.sequence = sequence;
        }
    }

    private final int capacity;
    private final PriorityQueue<Ticket> heap;
    private long sequenceCounter;

    BoundedPriorityTicketQueue(int capacity) {
        // TODO: validate capacity
        this.capacity = capacity;
        this.sequenceCounter = 0;
        this.heap = new PriorityQueue<>((a, b) -> {
            // TODO: order by severity descending, then sequence ascending        return false;
        });
    }

    public boolean enqueue(String id, int severity) {
        // TODO: return false if full
        // TODO: insert ticket with FIFO tie-breaker
        return false;
    }

    public String dequeue() {
        // TODO: return null if empty
        return null;
    }

    public int size() {
        // TODO: return current size
        return 0;
    }
}

public class queues_senior_swe_medium {
    public static void main(String[] args) {
        // TODO: add quick manual checks if desired
    }
}
