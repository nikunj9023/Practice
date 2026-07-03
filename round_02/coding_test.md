# Coding Test - Round 02


# Problem 1
a = [4, 6, 1, 3, 8, 5, 7]  # sort it with loop

for i in range(len(a)):
    for j in range(i + 1, len(a)):
        if a[i] > a[j]:
            a[i], a[j] = a[j], a[i]

n = len(a)
print("Sorted list:", a)
print("Second largest number is:", a[n - 2])
print("Second smallest number is:", a[1])
median = (a[n // 2] + a[(n - 1) // 2]) / 2
print("Median is:", median)
mode = a[0]
for i in range(1, n):
    if a[i] == a[i - 1]:
        mode = a[i]
print("Mode is:", mode)


# Problem 2
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        
        # Dummy head and tail to avoid edge cases
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_node(self, node: Node):
        """Always add the new node right after head."""
        node.prev = self.head
        node.next = self.head.next

        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: Node):
        """Remove an existing node from the linked list."""
        prev = node.prev
        nxt = node.next

        prev.next = nxt
        nxt.prev = prev

    def _move_to_head(self, node: Node):
        """Move certain node in between to the head."""
        self._remove_node(node)
        self._add_node(node)

    def _pop_tail(self) -> Node:
        """Pop the current tail."""
        res = self.tail.prev
        self._remove_node(res)
        return res

    def get(self, key: int) -> int:
        node = self.cache.get(key)
        if not node:
            return -1
        
        # Move the accessed node to the head
        self._move_to_head(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self.cache.get(key)

        if not node:
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            
            if len(self.cache) > self.capacity:
                # Pop the tail
                tail = self._pop_tail()
                del self.cache[tail.key]
        else:
            # Update the value
            node.value = value
            self._move_to_head(node)


# Problem 3
r = redis.Redis(host='localhost', port=6379, db=0)
r.rate_limit('my_key', 5, 60)  # Allow 5 requests in 60 seconds

# Problem 4
flatten={a:1,b:{c:2,d:{e:3}}}

for key, value in flatten.items():
    if isinstance(value, dict):
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, dict):
                for sub_sub_key, sub_sub_value in sub_value.items():
                    print(f"{key}.{sub_key}.{sub_sub_key}={sub_sub_value}")
            else:
                print(f"{key}.{sub_key}={sub_value}")
    else:
        print(f"{key}={value}")


# Problem 5
# palindrome ignore case and spaces and symbols
def is_palindrome(s):
    # Removing symbols and case , spaces
    cleaned = ''.join(char.lower() for char in s if char.isalnum())
    # Check if the cleaned string is equal to its reverse
    return cleaned == cleaned[::-1]
s=input("Enter a string to check if it's a palindrome: ")
<!-- input string to check pelindrome -->
if is_palindrome(s):
    print(f'"{s}" is a palindrome.')
    <!-- if found pelindrome -->
else:
    print(f'"{s}" is not a palindrome.')
    <!-- if not found pelindrome -->

# Problem 6

from collections import Counter

def top_k_frequent(nums, k):
    count = Counter(nums)
    return [num for num, freq in count.most_common(k)]
nums = [1, 1, 1, 2, 2, 3]
k = 2
print(top_k_frequent(nums, k))  # Output: [1, 2]

# Problem 7

import threading
import time
import random

class ProducerConsumerQueue:
    def __init__(self, max_size=5):
        self.queue = []
        self.max_size = max_size
        # Condition variable for synchronization
        self.condition = threading.Condition()

    def put(self, item):
        with self.condition:
            # Wait if the queue is full
            while len(self.queue) >= self.max_size:
                print("Producer: Queue is full, waiting...")
                self.condition.wait()
            
            # Add item to the queue
            self.queue.append(item)
            print(f"Producer: Added {item} to queue. Queue size: {len(self.queue)}")
            
            # Notify the consumer that an item is available
            self.condition.notify()

    def get(self):
        with self.condition:
            # Wait if the queue is empty
            while len(self.queue) == 0:
                print("Consumer: Queue is empty, waiting...")
                self.condition.wait()
            
            # Remove item from the queue
            item = self.queue.pop(0)
            print(f"Consumer: Processed {item}. Queue size: {len(self.queue)}")
            
            # Notify the producer that space is available
            self.condition.notify()
            return item

def producer_task(q, num_items):
    for i in range(1, num_items + 1):
        item = f"Item-{i}"
        time.sleep(random.uniform(0.1, 0.5))  # Simulate variable production time
        q.put(item)
    
    # Send a sentinel value to signal completion
    q.put(None)
    print("Producer: Finished producing.")

def consumer_task(q):
    while True:
        time.sleep(random.uniform(0.2, 0.8))  # Simulate variable consumption time
        item = q.get()
        
        if item is None:
            print("Consumer: Received sentinel value, exiting.")
            break

if __name__ == "__main__":
    print("Main: Starting threads...")
    
    # Create the shared queue
    shared_queue = ProducerConsumerQueue(max_size=5)
    
    # Create producer and consumer threads
    producer_thread = threading.Thread(target=producer_task, args=(shared_queue, 10))
    consumer_thread = threading.Thread(target=consumer_task, args=(shared_queue,))

    # Start the threads
    producer_thread.start()
    consumer_thread.start()

    # Wait for the threads to finish
    producer_thread.join()
    consumer_thread.join()

    print("Main: All tasks completed.")


# Problem 8
# Creating Mini URL Shortener in python using Flask
url=input("Enter your URL :")
#creating dictionary to store the shortened URLs
url_dict={}
#creating short url
def shorten_url(url):
    #generating a random string of 6 characters
    import random
    import string
    short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    #storing the original URL and the shortened URL in the dictionary
    url_dict[short_url] = url
    return short_url
#printing short url
print("Shortened URL:", shorten_url(url))


