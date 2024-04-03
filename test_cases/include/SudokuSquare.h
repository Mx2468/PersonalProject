#ifndef SUDOKUSQUARE_H
#define SUDOKUSQUARE_H

// Do not add any #include statements to this file


class SudokuSquareSet {

    // TODO: write your code here
private:
    unsigned int values;
    int number_of_bits;

public:
    SudokuSquareSet() : values(0x00u), number_of_bits(0){}

    int size() const{
        return number_of_bits;
    }

    bool empty() const{
        unsigned int empty_result = values ^ 0x00u;
        if(empty_result == 0){
            return true;
        }
        else{
            return false;
        }
    }

    void clear(){
        values &= 0x00u;
    }

    bool operator==(const SudokuSquareSet & other) const{
        if(number_of_bits == other.number_of_bits && values == other.values){
            return true;
        }
        else{
            return false;
        }
    }

    bool operator!=(const SudokuSquareSet & other) const{
        return !operator==(other);
    }

    class iterator{
    public:
        SudokuSquareSet* set;
        unsigned int mask;

        iterator(SudokuSquareSet* a_set, int bit_to_get) : set(a_set){
            mask = 0x01u;
            for(int i=1; i<bit_to_get; i++){
                mask = mask<<1;
            }
        }

        unsigned int operator*(){
            unsigned int values_to_get = set->values;
            unsigned int result = mask & values_to_get;
            return result;
        }

        void operator++(){
            mask = mask<<1;
        }

    };

    iterator begin(){
        return iterator(this, 1);
    }

    iterator end(){
        return iterator(nullptr, 10);
    }

    iterator insert(int value){
        iterator place = begin();
        for(int i=0; i<value;i++){
            ++place;
        }

    }

};


// Do not write any code below this line
static_assert(sizeof(SudokuSquareSet) == sizeof(unsigned int) + sizeof(int), "The SudokuSquareSet class needs to have exactly two 'int' member variables, and no others");


#endif
