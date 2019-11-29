#include <Servo.h>

const double pi = 3.14159265358979;
const int first_bar = 104, second_bar = 97;
const int SERVOS = 5;
const int motor[SERVOS] = {2, 3, 9, 8, 4};
const int value_init[SERVOS] = {90, 180, 96, 0, 0};

int value[SERVOS] = {0};
double x1, x2, y1, y2, h, v, r, p, n, a;
double v1, v2;

bool value3_auto = false;
bool pick_sequence = false;
bool move_confirm = false;

Servo myservo[SERVOS];

void setup() {
    for(int i = 0; i < SERVOS; i++) {
        myservo[i].attach(motor[i]);
        value[i] = value_init[i];
    }
    Serial.begin(115200);

    h = position_x();
    v = position_y();
    r = value_init[0];
    p = value_init[4];
    n = value_init[3];
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

void setValue3(void) {
    value[3] = constrain(90 - value[1] + value[2] - 10, 0, 180);
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
    aim();
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
    if(value[3] < n) {
        valueUp(3);
    } else if(value[3] > n) {
        valueDown(3);
    }
}

void initial() {
    bool init_a = true, init_b = true;
    while(init_a) {
        if(value[4] > 0) valueDown(4);
        else if(value[3] < 180) valueUp(3);
        else if(value[1] < 30) valueUp(1);
        else if(value[2] < 30) valueUp(2);
        else if(value[1] < 60) valueUp(1);
        else if(value[2] < 60) valueUp(2);
        else if(value[1] < 90) valueUp(1);
        else if(value[2] < 90) valueUp(2);
        else init_a = false;
        servo_move(100);
    }
    while(init_b) {
        if(value[2] > 90) valueDown(2);
        else if(value[1] < 180) valueUp(1);
        else if(value[3] > 0) valueDown(3);
        else if(value[0] < 90) valueUp(0);
        else if(value[0] > 90) valueDown(0);
        else init_b = false;
        servo_move(100);
    }
    h = -104;
    v = 97;
    r = 90;
    p = 0;
}

bool isNum(char n) {
    if(n > 47 && n < 58) return true;
    else return false;
}

void serial_read() {
    static String command = "hvrpnmias";
    if(Serial.available() > 0) {
        String inString = Serial.readStringUntil('\n');
        //Serial.println(inString);

        char c;
        String str_num = "";
        for(int i = 0; i < inString.length(); i++) {
            if(command.indexOf(inString[i] != -1)) {
                if(inString[i] == 'q') {
                    move_ready();
                } else if(inString[i] == 'i') {
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
            p = 70;
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
            a = 0; n = 53;
            sequence = 1;
            pick_sequence = false;
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
        case 'a':
            if(num > 0)
                value3_auto = true;
            else
                value3_auto = false;
            break;
    }
}

void serial_print() {
    Serial.print("  value[0] = ");
    Serial.print(value[0]);
    /*Serial.print("  value[1] = ");
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
    Serial.print(n);*/
    Serial.print("  h = ");
    Serial.println(int(position_x()));
}

void move_ready() {
    if(v1 == value[1] && v2 == value[2] && r == value[0]) {
        Serial.println("y");
        move_confirm = false;
    }
}

void loop() {
    if(value3_auto)
        setValue3();
    if(pick_sequence)
        pick_object();
    if(move_confirm)
        move_ready();
        
    value_change(h, v);

    margin();

    if(pick_sequence) {
        servo_move(120);
    } else if(position_x() > 50 && position_y() < 50) {
        servo_move(200);
    } else if(position_x() > 0 && position_y() < 100) {
        servo_move(150);
    } else {
        servo_move(100);
    }
    
    serial_read();
}
