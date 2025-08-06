

import tkinter as tk
from tkinter import ttk, messagebox
import heapq
from collections import deque

# --------- Graph Data ---------
graph = {
    'A': {'B': 1, 'C': 4},
    'B': {'C': 2, 'D': 5},
    'C': {'D': 1},
    'D': {'E': 3},
    'E': {}
}

heuristics = {
    'A': 7, 'B': 6, 'C': 2, 'D': 1, 'E': 0
}

# --------- Algorithms ---------
def bfs(start, goal):
    visited = set()
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in graph[node]:
                queue.append(path + [neighbor])
    return None

def dfs(start, goal, visited=None, path=None):
    visited = visited or set()
    path = path or []
    visited.add(start)
    path.append(start)
    if start == goal:
        return path
    for neighbor in graph[start]:
        if neighbor not in visited:
            result = dfs(neighbor, goal, visited.copy(), path.copy())
            if result:
                return result
    return None

def ucs(start, goal):
    pq = [(0, [start])]
    while pq:
        cost, path = heapq.heappop(pq)
        node = path[-1]
        if node == goal:
            return path, cost
        for neighbor, edge_cost in graph[node].items():
            heapq.heappush(pq, (cost + edge_cost, path + [neighbor]))
    return None, float('inf')

def a_star(start, goal):
    open_set = [(heuristics[start], 0, start, [start])]
    while open_set:
        est_total, cost_so_far, current, path = heapq.heappop(open_set)
        if current == goal:
            return path, cost_so_far
        for neighbor, cost in graph[current].items():
            new_cost = cost_so_far + cost
            est = new_cost + heuristics[neighbor]
            heapq.heappush(open_set, (est, new_cost, neighbor, path + [neighbor]))
    return None, float('inf')

def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            new_paths = find_all_paths(graph, node, end, path)
            for p in new_paths:
                paths.append(p)
    return paths

def calculate_cost(path):
    return sum(graph[path[i]].get(path[i+1], 1000) for i in range(len(path)-1))

def csp_path_finder(start, goal, required_stops=None, banned_stops=None, max_stops=None):
    all_paths = find_all_paths(graph, start, goal)
    valid_paths = []
    for path in all_paths:
        if required_stops and not all(stop in path for stop in required_stops):
            continue
        if banned_stops and any(stop in path for stop in banned_stops):
            continue
        if max_stops is not None and len(path) - 1 > max_stops:
            continue
        valid_paths.append(path)
    if not valid_paths:
        return None, None
    best_path = min(valid_paths, key=calculate_cost)
    return best_path, calculate_cost(best_path)

# --------- GUI Class ---------
class AirlineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Airline Route Optimization System")
        self.root.geometry("640x550")
        self.root.resizable(False, False)

        self.airports = list(graph.keys())

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Airline Route Optimization System", font=("Arial", 16, "bold")).pack(pady=10)

        frame = ttk.Frame(self.root, padding=10)
        frame.pack(pady=10)

        ttk.Label(frame, text="Start Airport").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_combo = ttk.Combobox(frame, values=self.airports, state="readonly")
        self.start_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Destination Airport").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.end_combo = ttk.Combobox(frame, values=self.airports, state="readonly")
        self.end_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Select Algorithm").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.algorithm_combo = ttk.Combobox(frame, values=["BFS", "DFS", "UCS", "A*", "CSP"], state="readonly")
        self.algorithm_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Required Stops (CSP)").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.required_entry = ttk.Entry(frame)
        self.required_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Banned Stops (CSP)").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.banned_entry = ttk.Entry(frame)
        self.banned_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Max Stops (CSP)").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.max_stops_entry = ttk.Entry(frame)
        self.max_stops_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Button(self.root, text="Find Route", command=self.run_algorithm).pack(pady=15)

        self.output_text = tk.Text(self.root, height=10, wrap="word", font=("Arial", 11))
        self.output_text.pack(padx=10, pady=10, fill="both")

    def run_algorithm(self):
        start = self.start_combo.get()
        end = self.end_combo.get()
        algo = self.algorithm_combo.get()

        if not (start and end and algo):
            messagebox.showerror("Input Error", "Please select all fields.")
            return

        result = ""
        if algo == "BFS":
            path = bfs(start, end)
            result = f"BFS Path: {' → '.join(path)}" if path else "No path found."

        elif algo == "DFS":
            path = dfs(start, end)
            result = f"DFS Path: {' → '.join(path)}" if path else "No path found."

        elif algo == "UCS":
            path, cost = ucs(start, end)
            result = f"UCS Path: {' → '.join(path)}\nTotal Cost: {cost}" if path else "No path found."

        elif algo == "A*":
            path, cost = a_star(start, end)
            result = f"A* Path: {' → '.join(path)}\nTotal Cost: {cost}" if path else "No path found."

        elif algo == "CSP":
            required = [x.strip().upper() for x in self.required_entry.get().split(',') if x.strip()]
            banned = [x.strip().upper() for x in self.banned_entry.get().split(',') if x.strip()]
            max_stops = self.max_stops_entry.get().strip()
            max_stops = int(max_stops) if max_stops.isdigit() else None

            path, cost = csp_path_finder(start, end, required, banned, max_stops)
            result = f"CSP Path: {' → '.join(path)}\nTotal Cost: {cost}" if path else "No valid path found."

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, result)

# --------- Main Program ---------
if __name__ == "__main__":
    root = tk.Tk()
    app = AirlineGUI(root)
    root.mainloop()
