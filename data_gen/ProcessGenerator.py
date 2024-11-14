import random
from typing import Dict, List, Set, Tuple
import networkx as nx
import matplotlib.pyplot as plt

class ProcessGenerator:
    def __init__(self, min_nodes: int = 5, max_nodes: int = 10, min_connections: int = 1, max_connections: int = 3, process_name: str = 'Process', lmstudio_connector = None):
        self.min_nodes = max(3, min_nodes)  # Minimum 3 nodes (START, 1 activity, END)
        self.max_nodes = max_nodes
        self.min_connections = max(1, min_connections)
        self.max_connections = max(self.min_connections, max_connections)
        self.graph: Dict[str, List[str]] = {}
        self.nodes: List[str] = []
        self.process_name = process_name
        self.lmstudio_connector = lmstudio_connector
        self.node_descriptions: Dict[str, str] = {}
        self.used_names: Set[str] = {'START', 'END'}  # Track used names

    def _generate_connections(self):
        """Generate random connections between nodes."""
        for i, node in enumerate(self.nodes):
            if node == 'END':
                continue

            # Calculate remaining possible nodes for connections
            remaining_nodes = self.nodes[i+1:]
            if not remaining_nodes:
                continue

            # Determine number of outgoing connections
            max_possible_connections = len(remaining_nodes)
            actual_max_connections = min(self.max_connections, max_possible_connections)
            actual_min_connections = min(self.min_connections, max_possible_connections)

            if actual_min_connections > actual_max_connections:
                actual_min_connections = actual_max_connections

            # Generate connections
            num_connections = random.randint(actual_min_connections, actual_max_connections)
            targets = random.sample(remaining_nodes, num_connections)
            self.graph[node] = targets

    def _ensure_valid_process(self):
        """Ensure the process follows basic modeling rules:
        - START: only outgoing connections (not to END)
        - END: only incoming connections
        - Other nodes: at least one incoming and one outgoing connection
        """
        # Clear any incoming connections to START and direct connections to END from START
        for node, targets in self.graph.items():
            if 'START' in targets:
                targets.remove('START')
            if node == 'START' and 'END' in targets:
                targets.remove('END')

        # Clear any outgoing connections from END
        if 'END' in self.graph:
            self.graph['END'] = []

        # Ensure START has at least one outgoing connection
        if not self.graph['START']:
            possible_targets = [n for n in self.nodes if n not in ['START', 'END']]
            if possible_targets:
                self.graph['START'] = [random.choice(possible_targets)]
            else:
                # If there are no middle nodes, we need to add one
                new_node = 'Activity_1'
                self.nodes.insert(-1, new_node)  # Insert before END
                self.graph[new_node] = ['END']
                self.graph['START'] = [new_node]

        # Check each activity node (excluding START and END)
        for node in self.nodes:
            if node in ['START', 'END']:
                continue

            # Ensure at least one outgoing connection
            if not self.graph[node]:
                possible_targets = [n for n in self.nodes if n not in ['START', node] and self.nodes.index(n) > self.nodes.index(node)]
                if 'END' in possible_targets and len(possible_targets) > 1:
                    possible_targets.remove('END')  # Prefer connecting to intermediate nodes if available
                if possible_targets:
                    self.graph[node] = [random.choice(possible_targets)]
                else:
                    self.graph[node] = ['END']

            # Ensure at least one incoming connection
            has_incoming = False
            for source, targets in self.graph.items():
                if node in targets:
                    has_incoming = True
                    break

            if not has_incoming:
                possible_sources = [n for n in self.nodes if n not in ['END', node] and self.nodes.index(n) < self.nodes.index(node)]
                if possible_sources:
                    source = random.choice(possible_sources)
                    if node not in self.graph[source]:
                        self.graph[source].append(node)
                else:
                    self.graph['START'].append(node)

        # Ensure there is at least one path to END
        has_path_to_end = False
        for node, targets in self.graph.items():
            if node != 'START' and 'END' in targets:
                has_path_to_end = True
                break

        if not has_path_to_end:
            # Find nodes without outgoing connections or with the highest index
            last_nodes = [n for n in self.nodes[1:-1] if not self.graph[n]]  # Exclude START and END
            if last_nodes:
                self.graph[last_nodes[-1]].append('END')
            else:
                # Find any middle node to connect to END
                middle_nodes = [n for n in self.nodes if n not in ['START', 'END']]
                if middle_nodes:
                    self.graph[middle_nodes[-1]].append('END')
                else:
                    # Create a new middle node if necessary
                    new_node = 'Activity_1'
                    self.nodes.insert(-1, new_node)
                    self.graph[new_node] = ['END']
                    self.graph['START'] = [new_node]

    def _get_activity_name(self, node: str, incoming_nodes: List[str], outgoing_nodes: List[str], attempt: int = 1) -> str:
        """Generate a unique descriptive name for an activity using LMStudio."""
        if not self.lmstudio_connector or node in ['START', 'END']:
            return node

        # Adjust prompt based on attempt number to encourage variety
        if attempt == 1:
            uniqueness_instruction = ""
        else:
            uniqueness_instruction = f"\nThe name must be different from: {', '.join(self.used_names - {'START', 'END'})}"

        prompt = f"""In the process '{self.process_name}', name an activity that:
            - Comes after activities: {', '.join(incoming_nodes) if incoming_nodes else 'START'}
            - Leads to activities: {', '.join(outgoing_nodes) if outgoing_nodes else 'END'}{uniqueness_instruction}

            Return only the activity name (2-4 words maximum), no additional text or punctuation."""

        try:
            activity_name = self.lmstudio_connector.get_answer(prompt)
            # Clean up the response
            activity_name = activity_name.strip().replace('\n', ' ').replace('"', '').replace("'", "")

            # Check if name is already used
            if activity_name in self.used_names:
                if attempt < 3:  # Try up to 3 times to get a unique name
                    return self._get_activity_name(node, incoming_nodes, outgoing_nodes, attempt + 1)
                else:
                    # If still not unique, append a number
                    base_name = activity_name
                    counter = 1
                    while activity_name in self.used_names:
                        activity_name = f"{base_name} {counter}"
                        counter += 1

            self.used_names.add(activity_name)
            return activity_name

        except Exception as e:
            print(f"Error generating name for {node}: {e}")
            # Generate a fallback unique name
            counter = 1
            while f"Activity_{counter}" in self.used_names:
                counter += 1
            fallback_name = f"Activity_{counter}"
            self.used_names.add(fallback_name)
            return fallback_name

    def _get_incoming_nodes(self, target_node: str) -> List[str]:
        """Get all nodes that have edges pointing to the target node."""
        return [node for node, targets in self.graph.items() if target_node in targets]

    def generate_process(self) -> Dict[str, List[str]]:
        """Generate a random process with start and end activities."""
        # Reset graph
        self.graph = {}
        self.node_descriptions = {}

        # Generate random number of nodes
        num_nodes = random.randint(self.min_nodes, self.max_nodes)

        # Create nodes (activities) - initially with generic names
        self.nodes = ['START', 'END']
        for i in range(num_nodes - 2):  # -2 for START and END
            self.nodes.append(f'Activity_{i+1}')

        # Initialize graph with empty adjacency lists
        for node in self.nodes:
            self.graph[node] = []

        # Generate random connections ensuring connectivity
        self._generate_connections()

        # Validate and fix the graph if necessary
        self._ensure_valid_process()

        # Now that we have the complete graph structure, generate meaningful names
        if self.lmstudio_connector:
            new_graph = {}
            new_nodes = []
            node_mapping = {}  # Maps old node names to new names

            # First, process START and END
            new_nodes.extend(['START', 'END'])
            node_mapping['START'] = 'START'
            node_mapping['END'] = 'END'

            # Process middle nodes
            for node in self.nodes:
                if node in ['START', 'END']:
                    continue

                incoming_nodes = self._get_incoming_nodes(node)
                outgoing_nodes = self.graph[node]

                # Get new name for the activity
                new_name = self._get_activity_name(
                    node,
                    [node_mapping.get(n, n) for n in incoming_nodes],
                    [node_mapping.get(n, n) for n in outgoing_nodes]
                )

                node_mapping[node] = new_name
                new_nodes.append(new_name)

            # Update graph with new names
            for old_node, targets in self.graph.items():
                new_node = node_mapping[old_node]
                new_graph[new_node] = [node_mapping[t] for t in targets]

            self.graph = new_graph
            self.nodes = new_nodes

        return self.graph

    def visualize_with_graphviz(self):
        """Alternative visualization using Graphviz for better directed graph layout.
        Saves the generated graph to a file named after the process name."""
        try:
            import graphviz

            # Create a new directed graph
            dot = graphviz.Digraph(comment='Process Flow')
            dot.attr(rankdir='LR')  # Left to right layout

            # Add nodes with different shapes and colors
            dot.node('START', 'START', shape='oval', style='filled', fillcolor='lightgreen')
            dot.node('END', 'END', shape='oval', style='filled', fillcolor='lightcoral')

            # Add activity nodes
            for node in self.nodes:
                if node not in ['START', 'END']:
                    dot.node(node, node, shape='box', style='filled', fillcolor='lightblue')

            # Add edges
            for source, targets in self.graph.items():
                for target in targets:
                    dot.edge(source, target)

            # Save the graph to a file
            # Using the process name as the filename, replacing spaces with underscores
            filename = "images/" + self.process_name.replace(' ', '_').lower().replace('"', '')
            dot.render(filename, format='png', cleanup=True)  # cleanup=True removes the .gv file
            print(f"Graph saved as {filename}.png")

            return dot
        except ImportError:
            print("Graphviz is not installed. Please install it with: pip install graphviz")
            return None