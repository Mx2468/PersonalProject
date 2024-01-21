#ifndef LINKEDLIST_H
#define LINKEDLIST_H

#include "node.h"

#include <utility>

// Do not add any #include statements here.  If you have a convincing need for adding a different `#include` please post in the forum on KEATS.

// TODO your code goes here:
#include<initializer_list>

template<typename T>
class LinkedList{
protected:
    Node<T>* head;
    Node<T>* tail;
    int element_count;

public:
    LinkedList():head(nullptr), tail(nullptr), element_count(0){}

    LinkedList(std::initializer_list<T> listIn)
        : head(nullptr), tail(nullptr), element_count(listIn.size()){

        for(auto element : listIn){
            push_back(element);
        }
    }

    ~LinkedList(){
        for (Node<T>* ptr = head; ptr != nullptr;){
            Node<T>* next_ptr = ptr->next;
            delete ptr;
            ptr = next_ptr;
        }
    };

    NodeIterator<T> insert(NodeIterator<T> where_to_insert, T element){
        Node<T>* element_to_add_ptr = new Node<T>(element);
        Node<T>* node_to_search_for_ptr = head;
        while (NodeIterator<T>(node_to_search_for_ptr) != where_to_insert){
            node_to_search_for_ptr = node_to_search_for_ptr->next;
        }

        Node<T>* prev_element_ptr = node_to_search_for_ptr->previous;

        element_to_add_ptr->next = node_to_search_for_ptr;
        element_to_add_ptr->previous = prev_element_ptr;

        if (node_to_search_for_ptr != nullptr) {
            node_to_search_for_ptr->previous = element_to_add_ptr;
        }
        if (prev_element_ptr != nullptr){
            prev_element_ptr->next = element_to_add_ptr;
        }
        return NodeIterator<T>(element_to_add_ptr);
    }

    NodeIterator<T> erase(NodeIterator<T> where_to_delete){
        Node<T>* node_to_delete_ptr = head;
        while(NodeIterator<T>(node_to_delete_ptr) != where_to_delete) {
            node_to_delete_ptr = node_to_delete_ptr->next;
        }

        Node<T>* element_to_delete_ptr = node_to_delete_ptr;
        Node<T>* next_element_ptr = element_to_delete_ptr->next;
        Node<T>* prev_element_ptr = element_to_delete_ptr->previous;

        if (prev_element_ptr != nullptr) {
            prev_element_ptr->next = next_element_ptr;
            if(element_to_delete_ptr == tail){
                tail = prev_element_ptr;
            }
        }

        if (next_element_ptr != nullptr) {
            next_element_ptr->previous = prev_element_ptr;
            if(element_to_delete_ptr == head){
                head = next_element_ptr;
            }
        }

        element_to_delete_ptr->next = nullptr;
        element_to_delete_ptr->previous = nullptr;
        element_count -= 1;
        delete element_to_delete_ptr;

        return NodeIterator<T>(next_element_ptr);
    }

    void push_front(T element_to_add){
        Node<T>* prev_head = head;
        head = new Node<T>(element_to_add);
        if(prev_head != nullptr) {
            prev_head->previous = head;
            head->next = prev_head;
        }

        if(tail == nullptr){
            tail = head;
        }
        element_count += 1;
    }

    void push_back(T element_to_add){
        Node<T>* prev_tail = tail;
        tail = new Node<T>(element_to_add);
        if (prev_tail != nullptr) {
            prev_tail->next = tail;
            tail->previous = prev_tail;
        }

        if(head == nullptr){
            head = tail;
        }
        element_count += 1;
    }

    const T & front() const{
        return head->data;
    }

    const T & back() const{
        return tail->data;
    }

    const int size() const{
        return element_count;
    }

    NodeIterator<T> end() {
        return NodeIterator<T>(nullptr);
    }

    const ConstNodeIterator<T> end() const{
        return ConstNodeIterator<T>(nullptr);
    }

    NodeIterator<T> begin(){
        return NodeIterator<T>(head);
    }

    const ConstNodeIterator<T> begin() const{
        return ConstNodeIterator<T>(head);
    }

    void reverse(){
        for (Node<T>* ptr = head; ptr != nullptr;){
            Node<T>* next_ptr = ptr->next;
            ptr->next = ptr->previous;
            ptr->previous = next_ptr;
            ptr = next_ptr;
        }
        Node<T>* temp = head;
        head = tail;
        tail = temp;
    }

};



// do not edit below this line

#endif
