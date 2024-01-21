#ifndef COVIDCASEMAP_H
#define COVIDCASEMAP_H

#include "CovidCase.h"

// TODO: your code goes here
#include<vector>
#include<set>
#include<limits>
#include<algorithm>

using std::vector;
using std::set;

class TimeAndCaseData{
private:
    int time = 0;
    int cases = 0;

public:
    TimeAndCaseData(int timeIn, int casesIn)
            : time(timeIn), cases(casesIn){}

    int getTime(){
        return time;
    }
    int getNumberOfCases(){
        return cases;
    }
};

class CovidCaseMap{
private:
    vector<CovidCase> cases = vector<CovidCase>();

    set<int> getUniqueTimes(){
        set<int> times = set<int>();
        for(int i=0; i< (int) cases.size(); i++){
            times.insert(cases[i].getTime());
        }
        return times;
    }

public:
    void addCase(CovidCase case_to_add){
        cases.push_back(case_to_add);
    }

    vector<TimeAndCaseData> getCasesOverTime(int hours_case_active_for){
        // Gets all times within cases
        set<int> times = getUniqueTimes();

        // Pads out times with 0 and times where each case disappears
        times.insert(0);
        for(const auto& one_case: cases){
            times.insert(one_case.getTime()+hours_case_active_for);
        }

        vector<TimeAndCaseData> cases_and_times = vector<TimeAndCaseData>();

        for(auto time : times){
            int cases_per_time = 0;

            for(const auto & j : cases){
                int case_start_time = j.getTime();
                int case_max_time = case_start_time+hours_case_active_for;

                if (case_start_time<=time && case_max_time>time) {
                    cases_per_time += 1;
                }
            }
            cases_and_times.emplace_back(time, cases_per_time);
        }

        return cases_and_times;
    }

    double supportVisitGreedyTSP(double latitude, double longitude, int time, int length_isolation){

        double final_length = 0.0;

        CovidCase starting_point = CovidCase(latitude, longitude, "Starting point", 0, 0);

        vector<CovidCase> not_visited_cases = vector<CovidCase>();

        for(const auto & one_case : cases){
            int case_start_time = one_case.getTime();
            int case_finish_time = case_start_time+length_isolation;
            if(case_start_time<=time && case_finish_time>time){
                not_visited_cases.push_back(one_case);
            }
        }


        CovidCase current_case = starting_point;

        // Until each case is visited
        while(!not_visited_cases.empty()) {

            // Find closest case
            CovidCase closestCase;
            double closest_dist = std::numeric_limits<double>::max();

            for(const auto& covid_case : not_visited_cases){
                if (!(current_case == covid_case) && !(starting_point == covid_case)){
                    double dist_to_case = current_case.distanceTo(covid_case);
                    if(dist_to_case<closest_dist){
                        closestCase = covid_case;
                        closest_dist = dist_to_case;
                    }
                }
            }

            // Select closest case & travel

            // Removes current case from not visited cases list
            auto found_iterator = std::find(not_visited_cases.begin(), not_visited_cases.end(), current_case);
            if(found_iterator != not_visited_cases.end()){
                not_visited_cases.erase(found_iterator);
            }


            if (!(closestCase == current_case) && !(closestCase == CovidCase())) {
                current_case = closestCase;
                final_length += closest_dist;
            }

        }

        final_length += current_case.distanceTo(starting_point);

        // Return length
        return final_length;
    }
};

// don't write any code below this line

#endif

