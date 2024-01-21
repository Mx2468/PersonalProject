#ifndef COVIDCASE_H
#define COVIDCASE_H

#include <iostream>
using std::ostream;

// TODO: your code  goes here
#include <string>
#include <sstream>
#include <cmath>

using std::string;
using std::to_string;
using std::ostream;
using std::stod;
using std::stoi;
using std::getline;
using std::istringstream;
using std::atan2;


class CovidCase{
private:
    double latitude = 0.0;
    double longitude = 0.0;
    string name = "";
    int age = 0;
    // When the user tested positive in hours since 1/1/2020
    int test_positive_time = 0;


public:
    CovidCase(double latitudeIn, double longitudeIn, string nameIn, int ageIn, int hours)
    : latitude(latitudeIn), longitude(longitudeIn), name(nameIn), age(ageIn),
    test_positive_time(hours){}

    CovidCase() = default;


    CovidCase(const string & stringDescription){

        istringstream input_values;
        input_values.str(stringDescription);

        string lat_str;
        getline(input_values, lat_str,',');
        latitude = stod(lat_str.substr(0, (lat_str.size())));

        string long_str;
        getline(input_values, long_str, ',');
        longitude = stod(long_str.substr(1, (long_str.size()-1)));

        string name_str;
        getline(input_values, name_str, ',');
        name = name_str.substr(2,(name_str.size()-3));

        string age_str;
        getline(input_values, age_str,',');
        age = stoi(age_str.substr(1,(age_str.size()-1)));

        string test_str;
        getline(input_values, test_str,',');
        test_positive_time = stoi(test_str.substr(1,(test_str.size()-1)));

    }

    // Using write method approach from lecture 1
    void write(ostream & o) const{
        o << "{" << latitude << ", " << longitude << ", " << "\"" << name << "\"" << ", " << age <<
        ", " << test_positive_time << "}";
    }

    double distanceTo(const CovidCase& other_case) const{
        const double PI = 3.14159265358979323846;
        double lat1 = (latitude*PI)/180;
        double lat2 = (other_case.latitude*PI)/180;
        double long1 = (longitude*PI)/180;
        double long2 = (other_case.longitude*PI)/180;

        double delta_long = long2-long1;
        double delta_lat = lat2-lat1;

        double a = pow((sin(delta_lat/2)), 2) + cos(lat1) * cos(lat2) * pow((sin(delta_long/2)), 2);
        double c = 2 * atan2( sqrt(a), sqrt(1-a));

        double result = 3960*c;
        return result;
    }

    // Getter functions for object

    const double & getLatitude() const {
        return latitude;
    }

    const double & getLongitude() const{
        return longitude;
    }

    const string & getName() const{
        return name;
    }

    const int & getAge() const{
        return age;
    }

    const int & getTime() const{
        return test_positive_time;
    }

    bool operator==(const CovidCase & other_case){
        bool same_name = (name == other_case.getName());
        bool same_age = (age == other_case.getAge());
        bool same_longitude = (longitude == other_case.getLongitude());
        bool same_latitude = (latitude == other_case.getLatitude());
        bool same_time = (test_positive_time == other_case.getTime());
        return same_name && same_age && same_longitude && same_latitude && same_time;
    }

    CovidCase & operator= (const CovidCase & other_case){
        name = other_case.getName();
        age = other_case.getAge();
        longitude = other_case.getLongitude();
        latitude = other_case.getLatitude();
        test_positive_time = other_case.getTime();
        return *this;
    }
};

ostream & operator<<(ostream & o, const CovidCase & a_case){
    a_case.write(o);
    return o;
}


// don't write any code below this line

#endif

