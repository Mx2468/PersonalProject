#ifndef STRINGCONSTRUCTION_H
#define STRINGCONSTRUCTION_H

#include <string>
using std::string;


// TODO: your code goes here:

#include <utility>
#include <vector>
#include <iostream>
#include <unordered_set>
#include <stack>
#include <set>

using std::vector;
using std::set;
using std::stack;
using std::unique_ptr;
using std::unordered_set;
using std::pair;
using std::find;
using std::distance;

using std::ostream;
using std::endl;

void update_substrings(unordered_set<string> &set_of_substrings, const string & string_so_far){
    if((int)string_so_far.size()>=2) {
        set_of_substrings.clear();
        int beginning_index = 0;
        for (int n=2; n<=(int)string_so_far.size(); n++) {
            while (beginning_index + n <= (int) string_so_far.size()) {
                set_of_substrings.insert(string_so_far.substr(beginning_index, n));
                ++beginning_index;
            }
            beginning_index = 0;
        }
    }
}

int stringConstruction(const string& target, const int& clone_cost, const int& append_cost){

    // Initialises Variables
    int result = 0;
    int target_index = 0;
    string current;

    // unordered set - uses hash table for quick lookup of when we need to use substring
    unordered_set<string> substrings_in_current = unordered_set<string>();

    // Initial append cost
    current += target[target_index];
    result += append_cost;

    while(current!=target){

        // Check if there are enough characters in front to loop over
        unsigned int chars_left_after_current = target.size()-current.size();

        if(target_index >=1 && chars_left_after_current >= 2){
            // Check substrings of size 2 up to chars_left_after_current
           for(int i=2; i<=(int)chars_left_after_current && i<=(int)current.size(); i++){
               string substring_to_check = target.substr(target_index+1, i);

               // If substring exists already, then clone it
               if((substrings_in_current.find(substring_to_check)) != (substrings_in_current.end())){
                    current += substring_to_check;
                    result += clone_cost;
                    target_index += (int)substring_to_check.size();
                    std::cout<<"Cloned: "<<substring_to_check<<" Cost: "<< clone_cost<<std::endl;
                    update_substrings(substrings_in_current,current.substr(0,target_index+1));
               }
           }
        }

        if(target_index+1 != (int)target.size()) {
            int next_index = target_index + 1;
            current += target[next_index];
            target_index = next_index;
            result += append_cost;
            std::cout<<"Appended: "<<target[target_index-1]<<" Cost: "<< append_cost<<std::endl;

            // Update substrings
            update_substrings(substrings_in_current, current.substr(0, target_index + 1));
        }
    }

    return result;
}

/*

template <typename T>
class GraphNode{
public:
    T data;
    vector<pair<GraphNode<T>*, int>> adj_list;
    vector<pair<GraphNode<T>*, int>> transverse_adj_list;

    GraphNode(T dataIn) : data(dataIn), adj_list(vector<pair<GraphNode<T>*, int>>()), transverse_adj_list(vector<pair<GraphNode<T>*, int>>()){}

    void add_edge(GraphNode<T>* other_node, int weight){
        adj_list.emplace_back(other_node, weight);
    }

    void add_transverse_edge(GraphNode<T>* other_node, int weight){
        transverse_adj_list.emplace_back(other_node, weight);
    }

    void write_adj_edges(ostream & o) const{
        for(auto node_ptr: adj_list){
            o<<data<<"-->"<<node_ptr.first->data<<"\n";
        }
    }

    bool operator==(GraphNode<T> other) const{
        if(data == other.data){
            return true;
        }
    }

    bool operator!=(GraphNode<T>& other) const{
        if(data != other.data){
            return true;
        }
    }
};

struct CompareGraphNodes{
public:
    bool operator()(GraphNode<string> first, GraphNode<string> second) const{
        return first.data < second.data;
    }
};


template <typename T>
class Graph{
public:
    set<GraphNode<T>,CompareGraphNodes> nodes;
    int number_of_nodes;

    Graph() : nodes(set<GraphNode<T>,CompareGraphNodes>()), number_of_nodes(0){}

    GraphNode<T>* addNode(T data){
        GraphNode<T>* node_to_add_ptr = new GraphNode<T>(data);
        nodes.insert(*node_to_add_ptr);
        number_of_nodes += 1;
        return node_to_add_ptr;
    }

    void connect(GraphNode<T>* from, GraphNode<T>* to, int weight){
        from->add_edge(to, weight);
        to->add_transverse_edge(from, weight);
    }

    int size() const{
        return number_of_nodes;
    }

    GraphNode<T>* find(T dataIn) const{
        for(auto node_itr = nodes.begin(); node_itr!=nodes.end(); node_itr++){
            if(node_itr->data == dataIn){
                GraphNode<T> node = *node_itr;
                return &node;
            }
        }
        return nullptr;
    }

    void write(ostream & o) const {
        for(auto node_ptr : nodes) {
            o << "Node: " << node_ptr.data << "\n";
            node_ptr.write_adj_edges(o);
        }
        o<<endl;
    }

    set<GraphNode<T>,CompareGraphNodes> getNodes() const{
        return nodes;
    }
};


int secondTry(const string& target, const int& clone_cost, const int& append_cost) {
// Make graph from string
    int target_index = 0;
    string current;
    string before_append;
    GraphNode<string>* current_ptr;
    GraphNode<string>* before_append_ptr;
    GraphNode<string>* current_clone_ptr;

    unordered_set<string> substrings_in_current = unordered_set<string>();
    Graph<string> traversal_graph = Graph<string>();

    while (current != target) {

        if((int)current.size()!=0){
            before_append = current;
            before_append_ptr = current_ptr;

            current += target[target_index];
            current_ptr = traversal_graph.find(current);
            if(!current_ptr){
                current_ptr = traversal_graph.addNode(current);
            }
        }

        // Case of first character - no before_append
        else{
            current += target[target_index];
            before_append_ptr = traversal_graph.addNode(current);

            target_index += 1;
            current += target[target_index];
            current_ptr = traversal_graph.addNode(current);
        }

        // Record Append
        traversal_graph.connect(before_append_ptr, current_ptr, append_cost);


        int chars_left_after_current = (int)target.size()-(int)current.size();
        if(target_index >=1 && chars_left_after_current >= 2){
            // Check substrings of size 2 up to chars_left_after_current
            for(int i=2; i<=(int)chars_left_after_current && i<=(int)current.size(); i++) {
                string substring_to_check = target.substr(target_index + 1, i);

                // If substring exists already, then clone it
                if ((substrings_in_current.find(substring_to_check)) != (substrings_in_current.end())) {
                    if(!traversal_graph.find(substring_to_check)){
                        string new_clone_string = current+substring_to_check;
                        // Insert new node(if non-existent) and record clone
                        current_clone_ptr = traversal_graph.find(new_clone_string);
                        if(!current_clone_ptr){
                            current_clone_ptr = traversal_graph.addNode(new_clone_string);
                        }

                        //Record Clone
                        traversal_graph.connect(current_ptr, current_clone_ptr, clone_cost);
                    }
                }
            }
        }
        target_index += 1;
    }

    traversal_graph.write(std::cout);
    return -1;

    //vector<GraphNode<string>>

    //return target_index;
}


vector<GraphNode<string>> topologicalSort(const Graph<string> & graph_obj) {
    vector<GraphNode<string>> sorted_list;
    stack<GraphNode<string>> sort_stack = stack<GraphNode<string>>();
    set<GraphNode<string>,CompareGraphNodes> unsorted_list = graph_obj.getNodes();

    // While list is not the same size as all nodes
    while((int)sorted_list.size() != (int)graph_obj.size()) {
        // Select any unsorted vertex & add to stack
        GraphNode<string> selected_vertex = *unsorted_list.begin();
        sort_stack.push(selected_vertex);
        // While stack is not empty
        while(!sort_stack.empty()) {
            // Inspect top element on stack
            GraphNode<string> element_to_inspect = sort_stack.top();
            for(auto neighbour: element_to_inspect.adj_list) {
                // If this element has no neighbours not in list
                // Pop this element from the stack & add to back of list
                // Else
                // Add unsorted neighbours to stack
            }
        }
    }

    return sorted_list;
}

// "Backtrack" up topological sort
int findMinimalCost(vector<GraphNode<string>> sorted_nodes, Graph<string> graph) {
    GraphNode<string> current_node = sorted_nodes.back();
    int total_cost = 0;


    GraphNode<string> current_parent = current_node;
    int index_of_parent = (int)sorted_nodes.size()-1;
    // While not at starting node
    while(current_node != *sorted_nodes.begin() && current_node != *sorted_nodes.end()) {
        // Loop through all parents
        int cost_of_traverse = 0;

        for(auto parent: current_node.transverse_adj_list) {
            auto itr_to_parent_node = find(sorted_nodes.begin(), sorted_nodes.end(), *parent.first);
            int index_of_node = distance(sorted_nodes.begin(), itr_to_parent_node);

            // Find parent earliest in the sort
            if (index_of_node < index_of_parent){
                current_parent = *itr_to_parent_node;
                index_of_node = index_of_parent;
                cost_of_traverse = parent.second;
            }
        }

        // Add cost of operation
        total_cost += cost_of_traverse;
        // Traverse to parent
        current_node = current_parent;

    }
    // Return total cost
    return total_cost;

}

// do not write or edit anything below this line
*/

#endif
