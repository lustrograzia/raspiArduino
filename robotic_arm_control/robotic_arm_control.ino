#include <Servo.h>

const double pi = 3.14159265358979;
const int first_bar = 105, second_bar = 100;
const int SERVOS = 5;
const int motor[SERVOS] = {2, 3, 9, 8, 4};
const int value_init[SERVOS] = {90, 180, 100, 0, 0};

int value[SERVOS] = {0};
double x1, x2, y1, y2;
double v1, v2;
double h, v, r, p, n;
double h0, v0;

bool pick_sequence = false;
bool move_confirm = false;

Servo myservo[SERVOS];

void setup() {
    for(int i = 0; i < SERVOS; i++) {
        myservo[i].attach(motor[i]);
        value[i] = value_init[i];
    }
    Serial.begin(115200);

    h0 = h = position_x();
    v0 = v = position_y();
    r = value_init[0];
    p = value_init[4];
    n = 10;
}

void servo_move(int count) {
    for(int n = 0; n < count; n++)
        for(int i = 0; i < SERVOS; i++)
            myservo[i].write(value[i]);
}

void valueUp(int servo) {
    if(servo == 2) {
        if(value[servo] < 150) value[servo]++;
    } else {
        if(value[servo] < 180) value[servo]++;
    }
}

void valueDown(int servo) {
    if(value[servo] > 0) value[servo]--;
}

void setValue3(int set_n=10) {
    value[3] = constrain(90 - value[1] + value[2] - set_n, 0, 180);
}

double position_x(void) {
    x1 = (double)first_bar * cos(pi / 180 * value[1]);
    x2 = (double)second_bar * cos(pi / 180 * (value[1] - value[2]));
    return x1 + x2;
}

double position_y(void) {
    y1 = (double)first_bar * sin(pi / 180 * value[1]);
    y2 = (double)second_bar * sin(pi / 180 * (value[1] - value[2]));
    return y1 + y2;
}

void value_change(int benchmark_x, int benchmark_y) {
    if( abs(benchmark_x - position_x()) + abs(benchmark_y - position_y()) > 2 ) {
        double l = sqrt( (double)benchmark_x/100 * benchmark_x + (double)benchmark_y/100 * benchmark_y ) * 10;
        double first_bar_angle = acos( (first_bar * first_bar + l * l - second_bar * second_bar) / ( 2 * first_bar * l ) ) / pi * 180.0;
        double second_bar_angle = acos( (second_bar * second_bar + l * l - first_bar * first_bar ) / ( 2 * second_bar * l ) ) / pi * 180.0;
        v2 = int(first_bar_angle + second_bar_angle);
        if(benchmark_x < 0) {
            double angle = atan( (double)benchmark_x / benchmark_y ) / pi * 180.0;
            v1 = int(90 + first_bar_angle - angle);
        } else {
            double angle = atan( (double)benchmark_y / benchmark_x ) / pi * 180.0;
            v1 = int(first_bar_angle + angle);
        }
        if (l > 200) {
          v2 = 0;
          if (benchmark_x < 0) {
              v1 = int(90 + atan(abs(benchmark_x) / (double)benchmark_y) / pi * 180);
          } else {
              v1 = int(atan((double)benchmark_y/ benchmark_x) / pi * 180);
          }
        }
    }
}

void aim() {
    if(v1 > value[1]) {
        valueUp(1);
    } else if(v1 < value[1]) {
        valueDown(1);
    }
    if(v2 > value[2]) {
        valueUp(2);
    } else if(v2 < value[2]) {
        valueDown(2);
    }
}

void margin() {
    if(position_x() < h) {
        if(v2 > value[2]) {
            valueUp(2);
        } else if(v2 < value[2]) {
            valueDown(2);
        } else {
            if(v1 > value[1]) {
                valueUp(1);
            } else if(v1 < value[1]) {
                valueDown(1);
            }
        }
    } else if(position_x() > h) {
        if(v1 > value[1]) {
            valueUp(1);
        } else if(v1 < value[1]) {
            valueDown(1);
        } else {
            if(v2 > value[2]) {
                valueUp(2);
            } else if(v2 < value[2]) {
                valueDown(2);
            }
        }
    } else {
        aim();
    }
    if(value[0] < r) {
        valueUp(0);
    } else if(value[0] > r) {
        valueDown(0);
    }
    if(value[4] < p) {
        valueUp(4);
    } else if(value[4] > p) {
        valueDown(4);
    }
}

void initial() {
    while(position_x() > 100) {
        h = 80; n = 10;
        setValue3(n);
        value_change(h, v);
        margin();
        servo_move(100);
    }
    h = h0;
    v = v0;
    r = value_init[0];
    p = value_init[4];
    n = 10;
}

bool isNum(char c) {
    if(c > 47 && c < 58) return true;
    else return false;
}

void serial_read() {
    static String command = "hvrpnmis";
    if(Serial.available() > 0) {
        String inString = Serial.readStringUntil('\n');

        char c;
        String str_num = "";
        for(int i = 0; i < inString.length(); i++) {
            if(command.indexOf(inString[i] != -1)) {
                if(inString[i] == 'i') {
                    initial();
                } else if(inString[i] == 'm') {
                    serial_print();
                } else if(inString[i] == 's') {
                    pick_sequence = true;
                } else {
                    c = inString[i];
                    for(int j = i + 1; j < inString.length(); j++) {
                        if(inString[j] == 45 || isNum(inString[j])) {
                            str_num += inString[j];
                        } else {
                            i = j - 1;
                            break;
                        }
                    }
                    if(str_num != "")
                        input_value(c, str_num.toInt());
                    str_num = "";
                }
            }
        }
    }
}

void pick_object(){
    static int sequence = 1;
    switch(sequence) {
        case 1:
            p = 75;
            if(value[4] == p)
                sequence++;
            break;
        case 2:
            v = 50; h = 100;
            if(abs(position_y() - v) < 5 && abs(position_x() - h) < 5)
                sequence++;
            break;
        case 3:
            r = 170;
            if(value[0] == r)
                sequence++;
            break;
        case 4:
            v = -40;
            if(abs(position_y() - v) < 5)
                sequence++;
            break;
        case 5:
            p = 0;
            if(value[4] == p)
                sequence++;
            break;
        case 6:
            v = 50;
            if(abs(position_y() - v) < 5)
                sequence++;
            break;
        case 7:
            r = 90; v = 53; h = 90;
            if(v1 == value[1] && v2 == value[2])
                sequence++;
            break;
        case 8:
            initial();
            sequence = 1;
            pick_sequence = false;
            break;
    }
}

void input_value(char command, int num) {
    move_confirm = true;
    switch(command) {
        case 'h':
            h = constrain(num, -120, 200);
            break;
        case 'v':
            v = constrain(num, -50, 200);
            break;
        case 'r':
            r = constrain(num, 0, 180);
            break;
        case 'p':
            p = constrain(num, 0, 90);
            break;
        case 'n':
            n = constrain(num, 0, 180);
            break;
    }
}

void serial_print() {
    Serial.print("  value[0] = ");
    Serial.print(value[0]);
    Serial.print("  value[1] = ");
    Serial.print(value[1]);
    Serial.print("  value[2] = ");
    Serial.print(value[2]);
    Serial.print("  value[3] = ");
    Serial.print(value[3]);
    Serial.print("  value[4] = ");
    Serial.print(value[4]);
    Serial.print("  v1 = ");
    Serial.print(v1);
    Serial.print("  v2 = ");
    Serial.print(v2);
    Serial.print("  v3 = ");
    Serial.print(90 - value[1] + value[2]);
    Serial.print("  h = ");
    Serial.print(h);
    Serial.print("  v = ");
    Serial.print(v);
    Serial.print("  r = ");
    Serial.print(r);
    Serial.print("  p = ");
    Serial.print(p);
    Serial.print("  n = ");
    Serial.print(n);
    Serial.print("  h = ");
    Serial.println(int(position_x()));
}

void move_ready() {
    if((abs(position_x() - h) < 2) && (abs(position_y() - v) < 2)
            && r == value[0]) {
    //if(v1 == value[1] && v2 == value[2] && r == value[0]) {
        Serial.println("y");
        move_confirm = false;
    }
}

void loop() {
    if(pick_sequence)
        pick_object();
    if(move_confirm)
        move_ready();
        
    setValue3(n);
    value_change(h, v);

    margin();

    if(pick_sequence) {
        servo_move(80);
    } else if(position_x() > 50 && position_y() < 50) {
        servo_move(100);
    } else if(position_x() > 0 && position_y() < 100) {
        servo_move(80);
    } else {
        servo_move(50);
    }
    
    serial_read();
}
