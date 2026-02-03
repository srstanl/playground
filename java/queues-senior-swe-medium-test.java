import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class QueuesSeniorSweMediumTest {
    @Test
    void enqueueDequeueHonorsPriorityAndCapacity() {
        BoundedPriorityTicketQueue queue = new BoundedPriorityTicketQueue(3);

        assertTrue(queue.enqueue("T1", 2));
        assertTrue(queue.enqueue("T2", 5));
        assertTrue(queue.enqueue("T3", 5));
        assertFalse(queue.enqueue("T4", 3));

        assertEquals("T2", queue.dequeue());
        assertEquals("T3", queue.dequeue());
        assertEquals("T1", queue.dequeue());
        assertNull(queue.dequeue());
    }

    @Test
    void fifoForEqualSeverity() {
        BoundedPriorityTicketQueue queue = new BoundedPriorityTicketQueue(4);

        assertTrue(queue.enqueue("A", 4));
        assertTrue(queue.enqueue("B", 4));
        assertTrue(queue.enqueue("C", 4));

        assertEquals("A", queue.dequeue());
        assertEquals("B", queue.dequeue());
        assertEquals("C", queue.dequeue());
        assertNull(queue.dequeue());
    }

    @Test
    void mixedSeveritiesDequeueHighestFirst() {
        BoundedPriorityTicketQueue queue = new BoundedPriorityTicketQueue(5);

        assertTrue(queue.enqueue("X", 1));
        assertTrue(queue.enqueue("Y", 3));
        assertTrue(queue.enqueue("Z", 2));

        assertEquals("Y", queue.dequeue());
        assertEquals("Z", queue.dequeue());
        assertEquals("X", queue.dequeue());
        assertNull(queue.dequeue());
    }
}
