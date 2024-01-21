#ifndef SUDOKU_H
#define SUDOKU_H

#include "Searchable.h"

// TODO: Your Sudoku class goes here:
#include <vector>
using std::vector;
#include <set>
using std::set;
#include <cmath>
using std::ceil;
using std::unique_ptr;

class Sudoku : public Searchable{
private:
    vector<vector<set<int>>> solution;

public:
    Sudoku(int square_size){
        solution = vector<vector<set<int>>>(square_size);
        for(int i=0; i<square_size; i++) {
            vector<set<int>> row(square_size);
            for(int j=0; j<square_size; j++){
                row[j] = set<int>{1,2,3,4,5,6,7,8,9};
            }
            solution[i] = row;
        }
    }

    int getSquare(int row, int col) const {
        set<int> value = solution[row][col];
        if(value.size() == 1){
            return *value.begin();
        }
        else{
            return -1;
        }
    }

    bool setSquare(int row, int col, int value){
        set<int> possible_values = solution[row][col];
        possible_values.erase(possible_values.begin(), possible_values.end());
        possible_values.emplace(value);
        solution[row][col] = possible_values;

        for(int row_index=0; row_index < (int) solution.size(); row_index++){
            for(int column=0; column < (int) solution.size(); column++){
                if (solution[row_index][column].size() == 1) {
                    if (!remove_adjacent_values(row_index, column, *solution[row_index][column].begin())) {
                        return false;
                    }
                }
                else if (solution[row_index][column].empty()) {
                    return false;
                }
                else {
                    continue;
                }
            }
        }
        return true;
    }

    bool remove_adjacent_values(int row_index, int column_index, int value){

        for(int row_num=0; row_num < (int) solution.size(); row_num++){
            if(row_num!=row_index) {
                int size_before = (int) solution[row_num][column_index].size();

                if (!remove_value(row_num, column_index, value)) {
                    return false;
                }

                int size_after = (int) solution[row_num][column_index].size();
                if(size_before!=1 && size_after==1){
                    remove_adjacent_values(row_num, column_index, *solution[row_num][column_index].begin());
                }
            }
        }

        for(int column_num=0; column_num < (int) solution.size(); column_num++){
            if (column_num!=column_index){

                int size_before = (int) solution[row_index][column_num].size();

                if(!remove_value(row_index, column_num, value)){
                    return false;
                }

                int size_after = (int) solution[row_index][column_num].size();
                if(size_before!=1 && size_after==1){
                    remove_adjacent_values(row_index, column_num, *solution[row_index][column_num].begin());
                }
            }
        }

        int square_of_size = (int) std::sqrt(solution.size());
        int y_square_number = (int) std::ceil(row_index / square_of_size)+1;
        int x_square_number = (int) std::ceil(column_index / square_of_size)+1;
        int max_y_value = y_square_number * square_of_size;
        int max_x_value = x_square_number * square_of_size;

        for(int row = max_y_value-square_of_size; row<max_y_value; row++){
            for(int column = max_x_value-square_of_size; column<max_x_value; column++){
                if(!(row == row_index && column == column_index)){

                    int size_before = (int)solution[row][column].size();

                    if(!remove_value(row, column, value)){
                        return false;
                    }

                    int size_after = (int)solution[row][column].size();
                    if(size_before!=1 && size_after==1){
                        remove_adjacent_values(row, column, *solution[row][column].begin());
                    }
                }
            }
        }

        return true;
    }

    bool remove_value(int row, int column, int value){
        solution[row][column].erase(value);
        if(solution[row][column].empty()){
            return false;
        }
        else {
            return true;
        }

    }

    bool isSolution() const override {
        for(auto row: solution){
            for(auto column: row){
                if(column.size() != 1){
                    return false;
                }
            }
        }
        return true;
    }

    void write(ostream & o) const override{
        for(auto row: solution) {
            for (auto column: row){
                if(column.empty()){
                    o<<"X";
                }
                else if (column.size()==1){
                    o<<*column.begin();
                }
                else{
                    o<<"?";
                }
            }

        }
        o<<"\n";
    }

    int heuristicValue() const override{
        return 0;
    }

    vector<unique_ptr<Searchable>> successors() const override{
        vector<unique_ptr<Searchable>> result_vector = vector<unique_ptr<Searchable>>();
        int row_index=0;
        int col_index=0;
        set<int> possible_values;
        bool found = false;

        // Find first square with multiple values
        for(int row=0; row<(int)solution.size() && !found; row++){
            for(int column=0; column<(int)solution.size() && !found; column++){
                if((int) solution[row][column].size() > 1){
                    // Record coordinates & values of that square
                    found = true;
                    row_index = row;
                    col_index = column;
                    possible_values = solution[row][column];
                }
            }
        }


        // Loop over values
        for(auto possible_value: possible_values) {
            // Make copy of current object
            Sudoku* copy_of_current = new Sudoku(*this);
            // SetSquare on current iterated value in coordinate
            if(copy_of_current->setSquare(row_index, col_index, possible_value)) {
                // If this is true, add sudoku object to vector
                result_vector.emplace_back(copy_of_current);
            }
        }

        return result_vector;
    }
};



#endif
