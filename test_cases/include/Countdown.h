#ifndef COUNTDOWN_H
#define COUNTDOWN_H

#include <string>
#include <sstream>

// this is provided code for the last part of the README

std::string intToString(const int x) {
    std::ostringstream str;
    str << x;
    return str.str();
}

class CountdownSolution {

private:
    std::string solution;
    int value;

public:

    CountdownSolution() : solution(), value(0) {}

    CountdownSolution(const std::string & solutionIn, const int valueIn)
        : solution(solutionIn), value(valueIn) {
    }

    const std::string & getSolution() const {
        return solution;
    }

    int getValue() const {
        return value;
    }

};

// Do not edit above this line

// TODO: write code here:

using std::string;
#include <utility>
#include <iostream>
using std::cout;
#include <vector>
using std::vector;
using std::to_string;
using std::endl;

double run_operator(double operand1, double operand2, string operator_str) {
    if (operator_str == "+") {
        return operand1 + operand2;
    }
    else if (operator_str == "-") {
        return operand2 - operand1;
    } else if (operator_str == "*") {
        return operand1 * operand2;
    } else if (operator_str == "/") {
        return operand2 / operand1;
    } else {
        return 0.0;
    }
}

bool isOperator (string possible_operator){
    if (possible_operator == "+"){
        return true;
    }
    else if (possible_operator == "-"){
        return true;
    }
    else if (possible_operator == "/"){
        return true;
    }
    else if (possible_operator == "*"){
        return true;
    }
    else{
        return false;
    }
}

void evaluatePushedItems (vector<double> & number_stack, vector<string> & operator_stack){
    double num1 = number_stack.back();
    number_stack.pop_back();

    double num2 = number_stack.back();
    number_stack.pop_back();

    string oper = operator_stack.back();
    operator_stack.pop_back();

    number_stack.push_back(run_operator(num1,num2,oper));
}

double evaluateCountdown(string expression){

    int size_of_expression = expression.size();
    vector<double> number_stack = vector<double>();
    vector<string> operator_stack = vector<string>();

    // Parse string & add to stacks
    unsigned int prev_push_index = 0;
    for(int point_index = 0; point_index<size_of_expression; point_index++){

        if (std::to_string(' ') == std::to_string(expression[point_index])){
            string element_to_push = expression.substr(prev_push_index, (point_index-prev_push_index));

            if(!isOperator(element_to_push)){
                number_stack.push_back(std::stod(element_to_push));
            }
            else{
                operator_stack.push_back(element_to_push);
            }

            prev_push_index = point_index+1;
        }
        else if (point_index == size_of_expression-1){
            string element_to_push = expression.substr(size_of_expression-1,1);
            operator_stack.push_back(element_to_push);
        }

        // Evaluate items once two numbers and an operator appear
        if((number_stack.size() >= 2) && (operator_stack.size() == 1)){
            evaluatePushedItems(number_stack, operator_stack);
        }

    }

    double result = number_stack.back();

    return result;
}


void makePermutationsRecur(const string& expression, vector<string> & all_expressions, vector<int> numbers){
    if(numbers.size()>1) {
        for (int i = 0; i < (int) numbers.size(); i++) {
            int chosen_number = numbers[i];

            vector<int> numbers_copy = numbers;
            numbers_copy.erase(numbers_copy.begin()+i);

            if(all_expressions.size()>1){
                string add = expression + to_string(chosen_number) + " + ";
                makePermutationsRecur(add, all_expressions, numbers_copy);

                string subt = expression + to_string(chosen_number) + " - ";
                makePermutationsRecur(subt, all_expressions, numbers_copy);

                string div = expression + to_string(chosen_number) + " / ";
                makePermutationsRecur(div, all_expressions, numbers_copy);

                string mult = expression + to_string(chosen_number) + " * ";
                makePermutationsRecur(mult, all_expressions, numbers_copy);
            }

            else {
                makePermutationsRecur(to_string(chosen_number) + " ", all_expressions, numbers_copy);
            }


        }
    }
    else{
        all_expressions.push_back(expression + to_string(numbers.back()) + " +");
        all_expressions.push_back(expression + to_string(numbers.back()) + " -");
        all_expressions.push_back(expression + to_string(numbers.back()) + " /");
        all_expressions.push_back(expression + to_string(numbers.back()) + " *");
    }
}


CountdownSolution checkAllCombinations(vector<string> all_expressions, int target){

    int closest_result = 0;
    int closest_perm_index = 0;
    int current = 0;

    for(int i=0; i< (int) all_expressions.size(); i++){
        string combination = all_expressions[i];
        current = (int) evaluateCountdown(combination);
        if(current == target){
            return CountdownSolution(combination, current);
        }
        else if(abs(current-target) < abs(closest_result-target)){
            closest_result = current;
            closest_perm_index = i;
        }
        else {
            continue;
        }
    }

    return CountdownSolution(all_expressions[closest_perm_index], closest_result);
}

#include <cmath>
using std::abs;

CountdownSolution solveCountdownProblem(vector<int> numbers, int target){
    vector<string> combinations = vector<string>();
    makePermutationsRecur("", combinations, numbers);

    return checkAllCombinations(combinations, target);
}


#endif
